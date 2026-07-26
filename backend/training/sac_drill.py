import os
import json
import time
import random
import chess
from typing import List, Dict, Any, Optional
from backend.training import store


def _get_tal_findings() -> List[Dict[str, Any]]:
    profile = store.load_profile()
    if not profile or "steer_findings" not in profile:
        return []

    steer_findings = profile["steer_findings"]
    tal_findings = [sf for sf in steer_findings if sf.get("had_tal_move") is True]

    # Rank by steer.complexity DESC
    tal_findings.sort(
        key=lambda sf: sf.get("steer", {}).get("complexity", 0.0),
        reverse=True
    )

    # Deduplicate by board EPD
    seen_epds = set()
    deduped = []
    for sf in tal_findings:
        fen = sf.get("fen_before")
        if not fen:
            continue
        try:
            epd = chess.Board(fen).epd()
        except Exception:
            epd = fen.split(" ")[0]

        if epd not in seen_epds:
            seen_epds.add(epd)
            deduped.append(sf)

    return deduped


def build_sac_session(count: int = 10) -> List[Dict[str, str]]:
    """Select eligible sacrifice/landmine positions from profile steer_findings.
    
    Filters had_tal_move=True, ranks by complexity DESC, dedupes by board EPD,
    and returns [{"id": finding_id, "fen": fen_before}] ONLY.
    Answers and evaluations stay server-side.
    """
    eligible = _get_tal_findings()
    if not eligible:
        return []

    if len(eligible) <= count:
        sampled = eligible
    else:
        sampled = random.sample(eligible, count)

    session = []
    for sf in sampled:
        session.append({
            "id": sf["id"],
            "fen": sf["fen_before"],
        })

    return session


def _record_attempt(finding_id: str, uci: str, correct: bool, acceptable: bool):
    store._ensure_dirs()
    attempts_path = os.path.join(store.TRAINING_DIR, "sac_attempts.jsonl")
    record = {
        "finding_id": finding_id,
        "uci": uci,
        "correct": correct,
        "acceptable": acceptable,
        "ts": time.time(),
    }
    with open(attempts_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def score_sac_guess(finding_id: str, uci: str) -> Dict[str, Any]:
    """Score guess against a sacrifice steer_finding by id.
    
    Computes correct (found sac_uci), acceptable (in playable_candidates and not sac),
    soundness comparison (sac vs safe move evals & complexity), and playable candidates.
    Logs attempt to sac_attempts.jsonl.
    """
    profile = store.load_profile()
    if not profile or "steer_findings" not in profile:
        return {}

    sf = next((f for f in profile["steer_findings"] if f.get("id") == finding_id), None)
    if not sf or "steer" not in sf or "best" not in sf:
        return {}

    sac_move = sf["steer"]
    safe_move = sf["best"]
    sac_uci = sac_move.get("uci")

    playable = sf.get("playable_candidates", [])
    alt_ucis = {c["uci"] for c in playable if c.get("uci")}

    correct = (uci == sac_uci)
    acceptable = (uci in alt_ucis and not correct)

    eval_loss_cp = sf.get("eval_loss_cp", 0)

    res = {
        "correct": correct,
        "acceptable": acceptable,
        "sac_move": {
            "uci": sac_move.get("uci", ""),
            "san": sac_move.get("san", ""),
            "eval_cp": sac_move.get("eval_cp", 0),
            "complexity": sac_move.get("complexity", 0.0),
        },
        "safe_move": {
            "san": safe_move.get("san", ""),
            "eval_cp": safe_move.get("eval_cp", 0),
        },
        "eval_loss_cp": eval_loss_cp,
        "playable_candidates": playable,
    }

    _record_attempt(finding_id, uci, correct, acceptable)

    return res


def get_stats() -> Dict[str, Any]:
    """Calculate overall and recent (last 50) sacrifice drill stats."""
    store._ensure_dirs()
    attempts_path = os.path.join(store.TRAINING_DIR, "sac_attempts.jsonl")
    attempts = []
    if os.path.exists(attempts_path):
        with open(attempts_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    attempts.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    total = len(attempts)
    correct_count = sum(1 for a in attempts if a.get("correct"))
    acceptable_count = sum(1 for a in attempts if a.get("acceptable"))
    accuracy = round(correct_count / total, 4) if total > 0 else 0.0

    recent = attempts[-50:]
    recent_correct = sum(1 for a in recent if a.get("correct"))
    recent_accuracy = round(recent_correct / len(recent), 4) if len(recent) > 0 else 0.0

    return {
        "total": total,
        "correct": correct_count,
        "acceptable": acceptable_count,
        "accuracy": accuracy,
        "recent_accuracy": recent_accuracy,
    }
