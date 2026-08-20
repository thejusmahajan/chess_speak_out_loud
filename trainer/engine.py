"""
Knowledge Trainer Engine — Pure functions for Elo rating, SM-2 spaced repetition, and prerequisite-aware card scheduling.

No I/O or network dependencies. Everything here takes inputs and returns outputs deterministically.
"""
from __future__ import annotations

import math
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_LADDER_RATINGS: Dict[str, float] = {
    # German B2 ladders (advanced learner baseline)
    "de-konnektoren": 1200.0,
    "de-grammatik": 1200.0,
    "de-wortschatz": 1200.0,
    # Machine Learning ladders (foundational baseline)
    "air-quality": 820.0,
    "neural-processes": 820.0,
    "own-work": 820.0,
    "pytorch": 820.0,
    "uncertainty": 820.0,
}


def get_default_ladder_rating(ladder: str) -> float:
    """Get the configured default starting rating for a ladder."""
    if ladder in DEFAULT_LADDER_RATINGS:
        return DEFAULT_LADDER_RATINGS[ladder]
    norm = ladder.replace("_", "-")
    if norm in DEFAULT_LADDER_RATINGS:
        return DEFAULT_LADDER_RATINGS[norm]
    if ladder.startswith("de-") or ladder.startswith("de_"):
        return 1200.0
    return 820.0


def get_ladder_rating(progress: Dict[str, Any], ladder: str) -> float:
    """
    Get user rating for a specific ladder.
    If ladder_ratings dict exists, look up ladder (falling back to configured default).
    If legacy user_rating exists without ladder_ratings, return legacy rating.
    """
    ladder_ratings = progress.get("ladder_ratings")
    if isinstance(ladder_ratings, dict):
        if ladder in ladder_ratings:
            return float(ladder_ratings[ladder])
        norm = ladder.replace("_", "-")
        if norm in ladder_ratings:
            return float(ladder_ratings[norm])
        return get_default_ladder_rating(ladder)
    
    # Fallback to legacy user_rating if present
    if "user_rating" in progress:
        return float(progress["user_rating"])
        
    return get_default_ladder_rating(ladder)


LEGACY_GLOBAL_RATING_LADDERS = frozenset({
    "pytorch", "uncertainty", "neural-processes", "air-quality", "own-work",
})


def migrate_progress(progress: Dict[str, Any], known_ladders: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Migrate progress dict from legacy global user_rating to per-ladder ladder_ratings.
    Seeds every existing ladder with the legacy user_rating if ladder_ratings is absent.
    Preserves all card histories and attributes.
    """
    if "ladder_ratings" not in progress or not isinstance(progress["ladder_ratings"], dict):
        legacy_rating = float(progress.get("user_rating", 820.0))
        ladders_to_seed = set(DEFAULT_LADDER_RATINGS.keys())
        if known_ladders:
            ladders_to_seed.update(known_ladders)
        # The legacy global rating described progress in the ladders that existed when it was
        # the only rating -- the ML ones. Ladders introduced later (German) must start at their
        # configured default, or their cards fall outside the selection window and are never
        # served. A migration is a historical fact, so the list is explicit rather than inferred.
        progress["ladder_ratings"] = {
            l: (legacy_rating if l in LEGACY_GLOBAL_RATING_LADDERS
                else get_default_ladder_rating(l))
            for l in ladders_to_seed
        }
    return progress


def calculate_elo(ru: float, rc: float, score: float) -> Tuple[float, float]:
    """
    Calculate updated Elo ratings for the user (Ru) and the card (Rc).
    
    score: 1.0 ('got it'), 0.5 ('partial'), 0.0 ('missed')
    Returns: (new_ru, new_rc)
    """
    if score not in (1.0, 0.5, 0.0):
        raise ValueError(f"Invalid score {score}. Must be 1.0, 0.5, or 0.0.")
    
    expected = 1.0 / (1.0 + 10.0 ** ((rc - ru) / 400.0))
    new_ru = ru + 24.0 * (score - expected)
    new_rc = rc + 8.0 * (expected - score)
    return round(new_ru, 2), round(new_rc, 2)


def update_sm2(ease: float, interval_days: int, reps: int, score: float) -> Tuple[float, int, int]:
    """
    Update SM-2 spaced-repetition parameters.
    
    Returns: (new_ease, new_interval_days, new_reps)
    """
    if score == 1.0:
        reps += 1
        if reps == 1:
            interval = 1
        elif reps == 2:
            interval = 6
        else:
            interval = round(interval_days * ease)
        ease += 0.10
    elif score == 0.5:
        # reps stay same on partial
        interval = max(1, round(interval_days * 0.6))
        ease -= 0.15
    elif score == 0.0:
        reps = 0
        interval = 0
        ease -= 0.20
    else:
        raise ValueError(f"Invalid score {score}. Must be 1.0, 0.5, or 0.0.")
    
    # Clamp ease to [1.3, 2.8]
    ease = max(1.3, min(2.8, ease))
    return round(ease, 2), interval, reps


def is_card_due(card_progress: Optional[Dict[str, Any]], now: datetime) -> bool:
    """
    A card is due if it has never been seen or if now >= due_date.
    """
    if not card_progress:
        return True
    
    last_seen_str = card_progress.get("last_seen")
    if not last_seen_str:
        return True
    
    interval_days = card_progress.get("interval_days", 0)
    if interval_days == 0:
        return True
    
    due_date_str = card_progress.get("due_date")
    if not due_date_str:
        return True
    
    try:
        due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        return now >= due_date
    except Exception:
        return True


def is_card_unlocked(card_requires: List[str], progress: Dict[str, Any]) -> bool:
    """
    A card is unlocked if all card IDs in its `requires` list have been answered at 1.0 at least once.
    """
    if not card_requires:
        return True
    
    cards_progress = progress.get("cards", {})
    for req_id in card_requires:
        req_prog = cards_progress.get(req_id)
        if not req_prog:
            return False
        # Must have scored 1.0 at least once (recorded in mastered flag or reps >= 1 or score 1.0 in history)
        if not req_prog.get("mastered", False) and req_prog.get("reps", 0) < 1:
            has_1 = any(entry.get("score") == 1.0 for entry in req_prog.get("history", []))
            if not has_1:
                return False
    return True


def _is_card_mastered(card_id: str, progress: Dict[str, Any]) -> bool:
    """
    A card is mastered if it has been answered with score 1.0 at least once.
    """
    cards_progress = progress.get("cards", {})
    req_prog = cards_progress.get(card_id)
    if not req_prog:
        return False
    if req_prog.get("mastered", False) or req_prog.get("reps", 0) >= 1:
        return True
    return any(entry.get("score") == 1.0 for entry in req_prog.get("history", []))


def get_ladder_active_level(ladder_cards: List[Dict[str, Any]], progress: Dict[str, Any]) -> int:
    """
    Compute the active eligible level for a ladder.
    Returns the lowest level L where < 80% of cards are mastered.
    If all levels are >= 80% mastered, returns the highest level in the ladder.
    """
    levels = sorted({c.get("level", 0) for c in ladder_cards})
    if not levels:
        return 0
    
    for lvl in levels:
        lvl_cards = [c for c in ladder_cards if c.get("level", 0) == lvl]
        if not lvl_cards:
            continue
        n_mastered = sum(1 for c in lvl_cards if _is_card_mastered(c["id"], progress))
        mastery_rate = n_mastered / len(lvl_cards)
        if mastery_rate < 0.80:
            return lvl
            
    return levels[-1]


def filter_selectable_cards(
    cards: List[Dict[str, Any]],
    progress: Dict[str, Any],
    now: datetime,
    cram_mode: bool = False,
) -> List[Dict[str, Any]]:
    """
    Filter cards that are unlocked (prerequisites met), level-eligible, and due (if not in cram mode).
    """
    selectable = []
    cards_progress = progress.get("cards", {})
    
    if cram_mode:
        for card in cards:
            card_id = card["id"]
            reqs = card.get("requires", [])
            if is_card_unlocked(reqs, progress):
                selectable.append(card)
        return selectable

    # Level gating: compute active level per ladder
    ladder_groups: Dict[str, List[Dict[str, Any]]] = {}
    for card in cards:
        ladder = card.get("ladder", "default")
        ladder_groups.setdefault(ladder, []).append(card)
        
    active_levels: Dict[str, int] = {
        ladder: get_ladder_active_level(l_cards, progress)
        for ladder, l_cards in ladder_groups.items()
    }
    
    for card in cards:
        card_id = card["id"]
        ladder = card.get("ladder", "default")
        card_level = card.get("level", 0)
        
        # A ladder is eligible at level L only. Cards above L are not served.
        if card_level > active_levels.get(ladder, 0):
            continue
            
        reqs = card.get("requires", [])
        if not is_card_unlocked(reqs, progress):
            continue
        
        card_prog = cards_progress.get(card_id)
        if is_card_due(card_prog, now):
            selectable.append(card)
            
    return selectable


def select_next_card(
    cards: List[Dict[str, Any]],
    progress: Dict[str, Any],
    now: datetime,
    cram_mode: bool = False,
    ladder_filter: Optional[str] = None,
    random_seed: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """
    Select the next card for the user using Elo windowing (|Rc - Ru_ladder| <= window, starting at 150).
    Uses the user's rating for the specific ladder of each candidate card.
    """
    if ladder_filter:
        norm_filter = ladder_filter.replace("_", "-")
        cards = [
            c for c in cards
            if c.get("ladder") == ladder_filter or c.get("ladder", "").replace("_", "-") == norm_filter
        ]
        
    candidates = filter_selectable_cards(cards, progress, now, cram_mode=cram_mode)
    if not candidates:
        return None
    
    cards_progress = progress.get("cards", {})
    
    # Helper to get effective card rating
    def get_card_rating(c: Dict[str, Any]) -> float:
        c_id = c["id"]
        if c_id in cards_progress and "rating" in cards_progress[c_id]:
            return float(cards_progress[c_id]["rating"])
        return float(c.get("difficulty", 1200))
    
    window = 150.0
    matched = []
    while window <= 2000.0:
        matched = [
            c for c in candidates
            if abs(get_card_rating(c) - get_ladder_rating(progress, c.get("ladder", "default"))) <= window
        ]
        if len(matched) >= 3 or len(matched) == len(candidates):
            break
        window += 50.0
        
    if not matched:
        matched = candidates
        
    rng = random.Random(random_seed)
    return rng.choice(matched)
