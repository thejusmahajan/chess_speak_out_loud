"""
Usual Suspects — Recurring Weakness Detection.

Clusters findings by tactical motif across distinct games, evaluating frequency x severity.
"""

from typing import Any, Dict, List, Set, Tuple

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
