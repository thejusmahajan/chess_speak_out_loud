"""
NORMATIVE metric definitions for the Elite Training System.

This file is the single mathematical source of truth for:
  - Policy Divergence          (intuitive blindness)
  - Attention Engagement       (structural blindness)
  - Saliency Concentration     (hidden-gem detection)
  - Quietness / Sharpness      (repertoire + gem gating)

All functions are PURE: no engine calls, no I/O, no torch. Inputs are the
already-extracted data structures produced by the existing oracles:

  policy   : list[dict] from LC0Engine.get_policy_distribution(fen, nodes=1)
             each entry {"uci","san","from","to","p", ...}, sorted desc by p,
             p is a fraction in [0, 1]. Empty list in mock mode.
  saliency : dict[str, float] square-name -> [0,1] from
             NeuralVision.saliency_absolute(fen)  (ABSOLUTE frame — never use
             NeuralVision.saliency() for game analysis; it is only
             frame-correct for white-to-move positions).
  eval_cp  : LC0Engine.analyze()["evaluation"] — int centipawns from WHITE's
             point of view, or a mate string like "M5" / "M-3".

OWNERSHIP: leader-owned. Workers must NOT edit this file. If a threshold
needs tuning, change only TrainingConfig defaults and record why in
WORKLOG_TRAINING.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import chess


@dataclass(frozen=True)
class TrainingConfig:
    """Calibration constants. Initial values are reasoned defaults, not
    gospel — tune only with evidence, and log the change."""

    # --- Policy Divergence (Engine 1) ---
    # D = p_best - p_played. "missed": intuition preferred something much
    # stronger. "blind": the played move was essentially never considered.
    divergence_min: float = 0.15
    blind_prior_max: float = 0.05

    # --- Attention Blindness (Engine 1) ---
    # engagement = max saliency over the squares a move interacts with.
    attention_hot: float = 0.60   # best move engages at least this...
    attention_cold: float = 0.25  # ...while played move engages at most this

    # --- Stage-B confirmation (Engine 1) ---
    # A finding is "confirmed" when playing the best move instead is worth at
    # least this many centipawns (from the mover's point of view).
    confirm_swing_cp: int = 90

    # --- Quiet positions / hidden gems (Engine 3) ---
    quiet_eval_cp: int = 30       # |white-POV eval| <= this => "quiet"
    gem_top_prior: float = 0.35   # network strongly "feels" one move
    gem_top4_mass: float = 0.45   # attention concentrated on few squares

    # --- Drills / repertoire soundness (Engines 2 & 3) ---
    forced_swing_cp: int = 150    # corpus drill solutions must swing >= this
    sound_eval_cp: int = 50       # repertoire lines must stay within +/- this
    alt_solution_margin: float = 0.05  # priors within this of best = accepted

    # --- Repertoire sharpness (Engine 2) ---
    max_draw_pct: float = 45.0    # WDL draw% above this = too drawish to train

    # --- Engine time budgets, seconds (user-tuned 2026-07-20: doubled
    # from 3.0/1.5/0.8/3.0/2.0 — "2 or 3 seconds won't be enough") ---
    confirm_best_seconds: float = 6.0      # stage B best-move eval (multipv=2)
    confirm_played_seconds: float = 3.0    # stage B played-move eval
    gem_screen_seconds: float = 1.6        # gems quick quietness screen
    gem_confirm_seconds: float = 6.0       # gems confirmation eval
    repertoire_eval_seconds: float = 4.0   # repertoire soundness gate

    # --- Time-scramble filter (diagnosis) ---
    # Moves played with less than this many seconds on the mover's clock
    # are excluded from diagnosis: they measure flag-fall panic, not chess
    # understanding. Applies only when the PGN carries [%clk] annotations;
    # games without clocks are analyzed in full.
    min_clock_seconds: float = 20.0


DEFAULT_CONFIG = TrainingConfig()


# ----------------------------------------------------------------------
# Shared helpers
# ----------------------------------------------------------------------

def policy_prior(policy: list[dict], uci: str) -> float:
    """Prior P(s, a) for a move, 0.0 if it does not appear in the list."""
    for entry in policy:
        if entry.get("uci") == uci:
            return float(entry.get("p", 0.0))
    return 0.0


def policy_rank(policy: list[dict], uci: str) -> Optional[int]:
    """1-based rank of a move in the (desc-sorted) policy list, None if absent."""
    for i, entry in enumerate(policy):
        if entry.get("uci") == uci:
            return i + 1
    return None


def policy_uci(board_before: chess.Board, move: chess.Move) -> str:
    """A move's UCI in the LC0 policy frame.

    LC0 encodes castling as king-takes-rook ("e1h1"); python-chess's
    Move.uci() gives the standard frame ("e1g1"). Policy lookups MUST go
    through this helper or castling moves get prior 0.0 and produce false
    "blind" findings. Idempotent for non-castling moves.
    """
    return board_before.uci(move, chess960=True)


def accepted_ucis(board_before: chess.Board, uci: str) -> list[str]:
    """Every UCI spelling of the same legal move — castling has two
    (standard "e1g1" and LC0/chess960 "e1h1"), everything else one.
    Drill answer checks must accept all spellings, because chessground
    reports whichever square the user dropped the king on. Returns the
    input unchanged (as a single-item list) if it is not legal here."""
    try:
        move = board_before.parse_uci(uci)
    except ValueError:
        return [uci]
    return sorted({
        board_before.uci(move, chess960=False),
        board_before.uci(move, chess960=True),
    })


def eval_cp_number(evaluation) -> Optional[int]:
    """Normalize an LC0 evaluation to white-POV centipawns.

    Mate scores ("M5" / "M-3") map to +/-10000 so magnitude comparisons
    still work; returns None for unparseable input.
    """
    if isinstance(evaluation, (int, float)):
        return int(evaluation)
    if isinstance(evaluation, str) and evaluation.lstrip("-").startswith("M"):
        # engine_manager formats mate as "M<n>" with n signed for the side
        try:
            n = int(evaluation.replace("M", ""))
            return 10000 if n > 0 else -10000
        except ValueError:
            return None
    return None


def move_interaction_squares(board_before: chess.Board, move: chess.Move) -> set[str]:
    """The squares a move 'interacts with': from-square, to-square, the
    captured pawn's square for en passant, and every square the moved piece
    attacks AFTER the move is made."""
    squares: set[int] = {move.from_square, move.to_square}
    if board_before.is_en_passant(move):
        # captured pawn sits behind the to-square
        offset = -8 if board_before.turn == chess.WHITE else 8
        squares.add(move.to_square + offset)
    after = board_before.copy(stack=False)
    after.push(move)
    squares |= set(after.attacks(move.to_square))
    return {chess.square_name(sq) for sq in squares}


# ----------------------------------------------------------------------
# Engine 1 — Policy Divergence (intuitive blindness)
# ----------------------------------------------------------------------

def policy_divergence(
    policy: list[dict],
    played_uci: str,
    cfg: TrainingConfig = DEFAULT_CONFIG,
) -> Optional[dict]:
    """Compare the player's move against LC0's raw policy prior.

    Returns None when the policy list is empty (mock mode) — callers must
    skip the move, never treat it as a finding. Otherwise:
      {"p_played","p_best","best_uci","best_san","divergence",
       "rank_played","severity"}  where severity is:
        "blind"  — divergence >= divergence_min AND p_played <= blind_prior_max
                    (pattern recognition never surfaced the idea)
        "missed" — divergence >= divergence_min (considered, undervalued)
        None     — no significant divergence
    """
    if not policy:
        return None
    best = policy[0]
    p_best = float(best.get("p", 0.0))
    p_played = policy_prior(policy, played_uci)
    divergence = p_best - p_played

    severity: Optional[str] = None
    if played_uci != best.get("uci") and divergence >= cfg.divergence_min:
        severity = "blind" if p_played <= cfg.blind_prior_max else "missed"

    return {
        "p_played": p_played,
        "p_best": p_best,
        "best_uci": best.get("uci"),
        "best_san": best.get("san"),
        "divergence": divergence,
        "rank_played": policy_rank(policy, played_uci),
        "severity": severity,
    }


# ----------------------------------------------------------------------
# Engine 1 — Attention Blindness (structural blindness)
# ----------------------------------------------------------------------

def attention_engagement(saliency: dict[str, float], squares: set[str]) -> float:
    """Max saliency over a set of squares (0.0 for an empty set)."""
    return max((saliency.get(sq, 0.0) for sq in squares), default=0.0)


def attention_blindness(
    saliency: dict[str, float],
    board_before: chess.Board,
    played: chess.Move,
    best: chess.Move,
    cfg: TrainingConfig = DEFAULT_CONFIG,
) -> dict:
    """Structural blindness: the network's attention is concentrated where
    the best move operates, and the played move ignores that region.

      {"engagement_played","engagement_best","hot_squares","blind"}
    hot_squares = squares with saliency >= attention_hot, for display.
    """
    e_played = attention_engagement(
        saliency, move_interaction_squares(board_before, played))
    e_best = attention_engagement(
        saliency, move_interaction_squares(board_before, best))
    return {
        "engagement_played": e_played,
        "engagement_best": e_best,
        "hot_squares": sorted(
            sq for sq, v in saliency.items() if v >= cfg.attention_hot),
        "blind": e_best >= cfg.attention_hot and e_played <= cfg.attention_cold,
    }


# ----------------------------------------------------------------------
# Engine 1 — Stage-B confirmation
# ----------------------------------------------------------------------

def confirmation_swing(
    eval_best_cp,
    eval_played_cp,
    mover_is_white: bool,
    cfg: TrainingConfig = DEFAULT_CONFIG,
) -> Optional[dict]:
    """Eval swing (mover's POV, centipawns) between best-move and played-move
    continuations. Both inputs are white-POV evals of the position AFTER the
    respective move. Returns None if either eval is unparseable."""
    b = eval_cp_number(eval_best_cp)
    p = eval_cp_number(eval_played_cp)
    if b is None or p is None:
        return None
    swing = (b - p) if mover_is_white else (p - b)
    return {"swing_cp": swing, "confirmed": swing >= cfg.confirm_swing_cp}


# ----------------------------------------------------------------------
# Engine 3 — quietness, concentration, hidden gems
# ----------------------------------------------------------------------

def is_quiet(evaluation, cfg: TrainingConfig = DEFAULT_CONFIG) -> bool:
    """Near-0.00 position; mate scores are never quiet."""
    cp = eval_cp_number(evaluation)
    return cp is not None and abs(cp) <= cfg.quiet_eval_cp


def saliency_concentration(saliency: dict[str, float]) -> dict:
    """How concentrated the attention mass is.

      top4_mass — fraction of total saliency mass held by the 4 hottest
                  squares (0.0 when the map is empty/all-zero)
      top_squares — those squares, hottest first
    """
    vals = sorted(saliency.values(), reverse=True)
    total = sum(vals)
    if total <= 0:
        return {"top4_mass": 0.0, "top_squares": []}
    top_squares = sorted(saliency, key=saliency.get, reverse=True)[:4]
    return {"top4_mass": sum(vals[:4]) / total, "top_squares": top_squares}


def is_hidden_gem(
    evaluation,
    policy: list[dict],
    saliency: dict[str, float],
    cfg: TrainingConfig = DEFAULT_CONFIG,
) -> dict:
    """A quiet position with latent tension: eval ~0.00, but attention is
    concentrated AND the network strongly prefers one move.

      {"gem": bool, "quiet": bool, "top_prior": float, "top4_mass": float,
       "top_squares": [...]}
    """
    quiet = is_quiet(evaluation, cfg)
    top_prior = float(policy[0]["p"]) if policy else 0.0
    conc = saliency_concentration(saliency)
    return {
        "gem": (quiet
                and top_prior >= cfg.gem_top_prior
                and conc["top4_mass"] >= cfg.gem_top4_mass),
        "quiet": quiet,
        "top_prior": top_prior,
        "top4_mass": conc["top4_mass"],
        "top_squares": conc["top_squares"],
    }


# ----------------------------------------------------------------------
# Engine 2 — sharpness
# ----------------------------------------------------------------------

def sharpness_from_wdl(wdl, cfg: TrainingConfig = DEFAULT_CONFIG) -> Optional[dict]:
    """wdl = [wins, draws, losses] per-mille (LC0 UCI_ShowWDL, white POV).

      {"draw_pct": float, "sharp": bool}  — sharp when the draw share is
    below max_draw_pct. Returns None when wdl is missing."""
    if not wdl or len(wdl) != 3:
        return None
    total = sum(wdl)
    if total <= 0:
        return None
    draw_pct = 100.0 * wdl[1] / total
    return {"draw_pct": draw_pct, "sharp": draw_pct < cfg.max_draw_pct}


def alt_solutions(policy: list[dict], cfg: TrainingConfig = DEFAULT_CONFIG) -> list[str]:
    """UCIs of moves whose prior is within alt_solution_margin of the best —
    all accepted as correct answers in drills (the best move is included)."""
    if not policy:
        return []
    p_best = float(policy[0].get("p", 0.0))
    return [e["uci"] for e in policy
            if p_best - float(e.get("p", 0.0)) <= cfg.alt_solution_margin]
