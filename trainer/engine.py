"""
Knowledge Trainer Engine — Pure functions for Elo rating, SM-2 spaced repetition, and prerequisite-aware card scheduling.

No I/O or network dependencies. Everything here takes inputs and returns outputs deterministically.
"""
from __future__ import annotations

import math
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


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


def filter_selectable_cards(
    cards: List[Dict[str, Any]],
    progress: Dict[str, Any],
    now: datetime,
    cram_mode: bool = False,
) -> List[Dict[str, Any]]:
    """
    Filter cards that are unlocked (prerequisites met) and due (if not in cram mode).
    """
    selectable = []
    cards_progress = progress.get("cards", {})
    
    for card in cards:
        card_id = card["id"]
        reqs = card.get("requires", [])
        if not is_card_unlocked(reqs, progress):
            continue
        
        card_prog = cards_progress.get(card_id)
        if cram_mode or is_card_due(card_prog, now):
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
    Select the next card for the user using Elo windowing (|Rc - Ru| <= window, starting at 150).
    """
    if ladder_filter:
        cards = [c for c in cards if c.get("ladder") == ladder_filter]
        
    candidates = filter_selectable_cards(cards, progress, now, cram_mode=cram_mode)
    if not candidates:
        return None
    
    user_rating = progress.get("user_rating", 1200.0)
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
        matched = [c for c in candidates if abs(get_card_rating(c) - user_rating) <= window]
        if len(matched) >= 3 or len(matched) == len(candidates):
            break
        window += 50.0
        
    if not matched:
        matched = candidates
        
    rng = random.Random(random_seed)
    return rng.choice(matched)
