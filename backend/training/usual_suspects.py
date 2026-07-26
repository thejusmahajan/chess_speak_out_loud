"""
Usual Suspects — Recurring Weakness Detection & Deck Builder.

Clusters findings by tactical motif across distinct games, evaluating frequency x severity,
and builds severity-weighted blended drill decks from user-approved suspect themes.
"""

import datetime
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

import chess
from backend.training import store, drills

# Leader-tunable module constants
GENERIC_MOTIFS: Set[str] = {"advantage", "veryLong", "quietMove"}
SEVERITY_CAP: float = 800.0
UNCONFIRMED_WEIGHT: float = 0.5
MIN_GAMES_FLOOR: int = 2
HIGH_SEVERITY_THRESHOLD: float = 400.0
MEDIUM_SEVERITY_THRESHOLD: float = 150.0


def game_key(f: Dict[str, Any]) -> str:
    """Extract game key prefix (e.g. 'g014' from 'g014-p026')."""
    f_id = f.get("id", "")
    if "-" in f_id:
        return f_id.split("-")[0]
    return f_id


def finding_severity(f: Dict[str, Any]) -> float:
    """Per-finding severity = min(swing_cp, 800) * (1.0 if confirmed else 0.5)."""
    confirmation = f.get("confirmation", {})
    swing_cp = float(confirmation.get("swing_cp", 0))
    confirmed = bool(confirmation.get("confirmed", False))
    weight = 1.0 if confirmed else UNCONFIRMED_WEIGHT
    return min(swing_cp, SEVERITY_CAP) * weight


def severity_label(mean_sev: float) -> str:
    """Map mean severity to high|medium|low."""
    if mean_sev >= HIGH_SEVERITY_THRESHOLD:
        return "high"
    if mean_sev >= MEDIUM_SEVERITY_THRESHOLD:
        return "medium"
    return "low"


def usual_suspects(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Cluster profile findings by tactical theme, calculating rank_score = games(T) * mean_severity(T).
    Filters out clusters with games(T) < 2 (MIN_GAMES_FLOOR) and generic motifs.
    
    TODO: Opening grouping is DEFERRED until the ECO fix ships (ECO is '???').
    """
    if not profile or not isinstance(profile, dict):
        return []

    findings = profile.get("findings", [])
    if not findings:
        return []

    # Map each theme T to list of findings F_T
    clusters: Dict[str, List[Dict[str, Any]]] = {}
    for f in findings:
        motifs = f.get("motifs", [])
        themes = set(motifs) - GENERIC_MOTIFS
        for theme in themes:
            if theme not in clusters:
                clusters[theme] = []
            clusters[theme].append(f)

    result = []
    for theme, F_T in clusters.items():
        distinct_games = len({game_key(f) for f in F_T})
        if distinct_games < MIN_GAMES_FLOOR:
            continue

        occurrences = len(F_T)
        severities = [finding_severity(f) for f in F_T]
        mean_sev = sum(severities) / occurrences if occurrences > 0 else 0.0
        rank_score = distinct_games * mean_sev
        label = severity_label(mean_sev)
        finding_ids = [f["id"] for f in F_T if "id" in f]

        result.append({
            "theme": theme,
            "games": distinct_games,
            "occurrences": occurrences,
            "mean_severity": round(mean_sev, 2),
            "rank_score": round(rank_score, 2),
            "severity_label": label,
            "finding_ids": finding_ids,
        })

    # Sort descending by rank_score, then theme asc for deterministic output
    result.sort(key=lambda item: (-item["rank_score"], item["theme"]))
    return result


def get_broad_aggregates(profile: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Surface by_phase and by_concept from profile aggregates for the dashboard broad view.
    """
    if not profile or not isinstance(profile, dict):
        return [], []

    agg = profile.get("aggregates", {})
    raw_phase = agg.get("by_phase", {})
    raw_concept = agg.get("by_concept", {})

    if isinstance(raw_phase, dict):
        by_phase = [{"phase": k, **v} if isinstance(v, dict) else {"phase": k, "value": v} for k, v in raw_phase.items()]
    elif isinstance(raw_phase, list):
        by_phase = raw_phase
    else:
        by_phase = []

    if isinstance(raw_concept, dict):
        concept_list = [{"concept": k, **v} if isinstance(v, dict) else {"concept": k, "value": v} for k, v in raw_concept.items()]
        concept_list.sort(key=lambda x: x.get("missed", 0) if isinstance(x.get("missed"), (int, float)) else 0, reverse=True)
        by_concept = concept_list
    elif isinstance(raw_concept, list):
        by_concept = raw_concept
    else:
        by_concept = []

    return by_phase, by_concept


def allocate_slots(kept_suspects: List[Dict[str, Any]], count: int) -> Dict[str, int]:
    """
    LEADER-PINNED severity-weighted slot allocation:
    slots(T) = max(1, round(count * rank_score(T) / total))
    Adjust rounding drift: if sum(slots) != count, add/remove single slots
    from the HIGHEST-rank_score themes until sum equals count.
    """
    if not kept_suspects or count <= 0:
        return {}

    total_rank_score = sum(s["rank_score"] for s in kept_suspects)
    if total_rank_score <= 0:
        base = max(1, count // len(kept_suspects))
        slots = {s["theme"]: base for s in kept_suspects}
    else:
        slots = {
            s["theme"]: max(1, int(round(count * s["rank_score"] / total_rank_score)))
            for s in kept_suspects
        }

    sum_slots = sum(slots.values())
    if sum_slots != count:
        diff = count - sum_slots
        if diff > 0:
            idx = 0
            for _ in range(diff):
                t_theme = kept_suspects[idx % len(kept_suspects)]["theme"]
                slots[t_theme] += 1
                idx += 1
        elif diff < 0:
            idx = 0
            for _ in range(abs(diff)):
                t_theme = kept_suspects[idx % len(kept_suspects)]["theme"]
                if slots[t_theme] > 1:
                    slots[t_theme] -= 1
                else:
                    found = False
                    for s in kept_suspects:
                        if slots[s["theme"]] > 1:
                            slots[s["theme"]] -= 1
                            found = True
                            break
                    if not found:
                        slots[t_theme] -= 1
                idx += 1
    return slots


def build_suspects_deck(
    profile: Optional[Dict[str, Any]],
    approved_themes: List[str],
    count: int = 20
) -> Dict[str, Any]:
    """
    Build a severity-weighted blended drill deck from approved suspect themes,
    deduping by board EPD across the whole deck.
    """
    set_id = f"suspects-{uuid.uuid4().hex[:8]}"
    created_iso = datetime.datetime.utcnow().isoformat()
    empty_result = {
        "id": set_id,
        "label": "Usual Suspects",
        "source": "usual_suspects",
        "created": created_iso,
        "themes": list(approved_themes) if approved_themes else [],
        "drills": []
    }

    if not profile or not approved_themes:
        return empty_result

    all_suspects = usual_suspects(profile)
    approved_set = set(approved_themes)
    kept_suspects = [s for s in all_suspects if s["theme"] in approved_set]
    if not kept_suspects:
        return empty_result

    kept_suspects.sort(key=lambda s: (-s["rank_score"], s["theme"]))
    slots_map = allocate_slots(kept_suspects, count)

    findings = profile.get("findings", [])
    finding_map = {f["id"]: f for f in findings if "id" in f}

    seen_epds: Set[str] = set()
    deck_drills: List[Dict[str, Any]] = []
    leftover_slots = 0

    for s in kept_suspects:
        theme = s["theme"]
        target_slots = slots_map.get(theme, 1) + leftover_slots
        leftover_slots = 0

        t_finding_ids = s.get("finding_ids", [])
        t_findings = [finding_map[fid] for fid in t_finding_ids if fid in finding_map]
        t_findings.sort(key=lambda f: finding_severity(f), reverse=True)

        added_for_theme = 0
        for f in t_findings:
            if added_for_theme >= target_slots:
                break
            try:
                board_before = chess.Board(f["fen_before"])
                epd = board_before.epd()
            except Exception:
                continue

            if epd in seen_epds:
                continue

            seen_epds.add(epd)
            drill = drills.build_drill_from_finding(f, source="usual_suspects", suspect_theme=theme)
            deck_drills.append(drill)
            added_for_theme += 1

        if added_for_theme < target_slots:
            leftover_slots += (target_slots - added_for_theme)

    if leftover_slots > 0 and len(deck_drills) < count:
        for s in kept_suspects:
            if len(deck_drills) >= count:
                break
            theme = s["theme"]
            t_finding_ids = s.get("finding_ids", [])
            t_findings = [finding_map[fid] for fid in t_finding_ids if fid in finding_map]
            t_findings.sort(key=lambda f: finding_severity(f), reverse=True)
            for f in t_findings:
                if len(deck_drills) >= count:
                    break
                try:
                    board_before = chess.Board(f["fen_before"])
                    epd = board_before.epd()
                except Exception:
                    continue
                if epd in seen_epds:
                    continue
                seen_epds.add(epd)
                drill = drills.build_drill_from_finding(f, source="usual_suspects", suspect_theme=theme)
                deck_drills.append(drill)

    return {
        "id": set_id,
        "label": "Usual Suspects",
        "source": "usual_suspects",
        "created": created_iso,
        "themes": [s["theme"] for s in kept_suspects],
        "drills": deck_drills
    }
