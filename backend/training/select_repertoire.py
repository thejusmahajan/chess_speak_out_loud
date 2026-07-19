"""Repertoire Architect (Engine 2) — backwards opening selection.

Instead of picking openings by taste, pick the openings whose master-game
structures most often produce the tactical patterns the user currently
misses (from the diagnosis profile), then keep only lines LC0 considers
sound and sharp enough to actually force those patterns.

Pure orchestration: metric math from `backend.training.metrics`, frequency
data from `puzzle_db`, lines from `openings`, evals from the app's engine
singleton. Deterministic rationale template — no LLM.

Color ownership rule: the ECO databases give every line from move 1, so the
spec's "first-move color" filter is interpreted as line ownership — a line
belongs to the side that made its LAST move (odd-length UCI sequence =
white's line, even = black's). Deviation from the spec's literal wording
logged in WORKLOG_TRAINING.md.

OWNERSHIP: Claude worker (C2). See CLAUDE_TRAINING_TASKS.md.
"""

from __future__ import annotations

import datetime

import chess

from backend.training import metrics, openings, puzzle_db
from backend.training.metrics import DEFAULT_CONFIG, TrainingConfig

MAX_ENGINE_CALLS = 15

RATIONALE_TEMPLATE = (
    "Play the {name} ({line_pgn}). Structures from this opening produce "
    "{motif} in {pct:.1f}% of tagged master-game puzzles; LC0 holds the "
    "tabiya at {cp}cp with a {draw_pct} draw share — sharp enough to force "
    "the patterns you miss."
)


def _target_motifs(profile: dict, top_k: int = 3) -> list[tuple[str, int]]:
    """Top motifs ranked by 2*blind + missed (these weights, per spec)."""
    by_motif = (profile or {}).get("aggregates", {}).get("by_motif", {})
    weighted = [
        (motif, 2 * stats.get("blind", 0) + stats.get("missed", 0))
        for motif, stats in by_motif.items()
    ]
    weighted = [(m, w) for m, w in weighted if w > 0]
    weighted.sort(key=lambda x: (-x[1], x[0]))
    return weighted[:top_k]


def _line_color(uci_moves: list[str]) -> str:
    """The side that made the line's last move owns the line."""
    return "white" if len(uci_moves) % 2 == 1 else "black"


async def build_repertoire(
    profile: dict,
    color: str,
    engine,
    top_n: int = 5,
    cfg: TrainingConfig = DEFAULT_CONFIG,
) -> dict:
    if color not in ("white", "black"):
        raise ValueError(f"color must be 'white' or 'black', got {color!r}")

    targets = _target_motifs(profile)
    lines = openings.lines_by_tag()

    # Candidate tags: union over targets of tags where the motif is frequent,
    # kept only when mappable to an ECO line of the right color.
    candidate_tags: set[str] = set()
    for motif, _weight in targets:
        for tag, _freq, _n in puzzle_db.opening_tags_ranked(motif):
            line = lines.get(tag)
            if line and line["fen"] and _line_color(line["uci_moves"]) == color:
                candidate_tags.add(tag)

    # Score = sum over targets of weight_t * motif_profile(tag)[t]
    scored: list[tuple[float, str, dict]] = []
    for tag in candidate_tags:
        freqs = puzzle_db.motif_profile(tag)
        score = sum(w * freqs.get(m, 0.0) for m, w in targets)
        if score > 0:
            scored.append((score, tag, freqs))
    scored.sort(key=lambda x: (-x[0], x[1]))

    # Soundness + sharpness gate on the best candidates only (engine budget).
    recommendations = []
    for score, tag, freqs in scored[:MAX_ENGINE_CALLS]:
        line = lines[tag]
        analysis = await engine.analyze(
            line["fen"], depth=None, multipv=1, time_limit=2.0)

        cp = metrics.eval_cp_number(analysis["evaluation"])
        if cp is None:
            continue
        pov_cp = cp if color == "white" else -cp
        if pov_cp < -cfg.sound_eval_cp:
            continue  # the line is already worse than -sound_eval_cp for us

        sharpness = metrics.sharpness_from_wdl(analysis.get("wdl"), cfg)
        if sharpness is not None and not sharpness["sharp"]:
            continue
        draw_pct = sharpness["draw_pct"] if sharpness else None

        # Rationale anchors on the target motif this tag serves best.
        primary_motif = max(
            targets, key=lambda t: t[1] * freqs.get(t[0], 0.0))[0]
        board = chess.Board()
        line_pgn = board.variation_san(
            [chess.Move.from_uci(u) for u in line["uci_moves"]])

        recommendations.append({
            "tag": tag,
            "eco": line["eco"],
            "name": line["name"],
            "line_pgn": line_pgn,
            "score": round(score, 4),
            "eval_cp": cp,
            "draw_pct": round(draw_pct, 1) if draw_pct is not None else None,
            "primary_motif": primary_motif,
            "rationale": RATIONALE_TEMPLATE.format(
                name=line["name"],
                line_pgn=line_pgn,
                motif=primary_motif,
                pct=freqs.get(primary_motif, 0.0) * 100,
                cp=cp,
                draw_pct=(f"{draw_pct:.0f}%" if draw_pct is not None
                          else "unmeasured"),
            ),
        })
        if len(recommendations) >= top_n:
            break

    return {
        "version": 1,
        "color": color,
        "created": datetime.datetime.utcnow().isoformat(),
        "targets": [{"motif": m, "weight": w} for m, w in targets],
        "recommendations": recommendations,
    }
