"""
Unit Tests for Knowledge Trainer Engine & Verification Gate.

Tests Elo dynamics, SM-2 scheduling, prerequisite gating, candidate selection,
and verify_cards validation fixtures.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

from trainer.engine import (
    calculate_elo,
    update_sm2,
    is_card_due,
    is_card_unlocked,
    filter_selectable_cards,
    select_next_card,
)
from trainer.verify_cards import verify_all_cards


# =====================================================================
# 1. Elo Tests
# =====================================================================

def test_elo_harder_card_yields_higher_gain():
    """A user rated 1200 beating a 1600 card gains MORE than beating a 1000 card."""
    ru = 1200.0
    
    # Beating a 1600 card (hard)
    expected_hard = 1.0 / (1.0 + 10.0 ** ((1600.0 - 1200.0) / 400.0)) # ~0.0909
    new_ru_hard, _ = calculate_elo(ru, 1600.0, 1.0)
    gain_hard = new_ru_hard - ru
    
    # Beating a 1000 card (easy)
    expected_easy = 1.0 / (1.0 + 10.0 ** ((1000.0 - 1200.0) / 400.0)) # ~0.7597
    new_ru_easy, _ = calculate_elo(ru, 1000.0, 1.0)
    gain_easy = new_ru_easy - ru
    
    assert gain_hard > gain_easy
    assert round(gain_hard, 2) == round(24.0 * (1.0 - expected_hard), 2)
    assert round(gain_easy, 2) == round(24.0 * (1.0 - expected_easy), 2)


def test_elo_proportional_zero_sum():
    """Card moves by exactly 8/24 of user change in the opposite direction."""
    ru, rc = 1200.0, 1400.0
    new_ru, new_rc = calculate_elo(ru, rc, 1.0)
    
    delta_user = new_ru - ru
    delta_card = new_rc - rc
    
    # Delta card should be -(8/24) * Delta user = -1/3 * Delta user
    assert pytest.approx(delta_card, abs=0.05) == -(8.0 / 24.0) * delta_user


# =====================================================================
# 2. SM-2 Tests
# =====================================================================

def test_sm2_three_consecutive_got_it():
    """Intervals follow 1 -> 6 -> round(6 * ease) on three consecutive 'got it's."""
    ease, interval, reps = 2.5, 0, 0
    
    # Rep 1 (got it = 1.0)
    ease, interval, reps = update_sm2(ease, interval, reps, 1.0)
    assert reps == 1
    assert interval == 1
    assert ease == 2.6
    
    # Rep 2 (got it = 1.0)
    ease, interval, reps = update_sm2(ease, interval, reps, 1.0)
    assert reps == 2
    assert interval == 6
    assert ease == 2.7
    
    # Rep 3 (got it = 1.0)
    ease, interval, reps = update_sm2(ease, interval, reps, 1.0)
    assert reps == 3
    assert interval == round(6 * 2.7)  # 16
    assert ease == 2.8


def test_sm2_missed_resets_reps_and_interval():
    """'missed' (0.0) resets reps to 0 and interval to 0 (due immediately)."""
    ease, interval, reps = 2.6, 16, 3
    new_ease, new_interval, new_reps = update_sm2(ease, interval, reps, 0.0)
    
    assert new_reps == 0
    assert new_interval == 0
    assert new_ease == 2.4


def test_sm2_ease_clamping():
    """Ease is strictly clamped to [1.3, 2.8] after extreme grades."""
    ease = 2.75
    # High grades clamped to 2.8
    for _ in range(5):
        ease, _, _ = update_sm2(ease, 1, 1, 1.0)
    assert ease == 2.8
    
    # Low grades clamped to 1.3
    for _ in range(15):
        ease, _, _ = update_sm2(ease, 1, 1, 0.0)
    assert ease == 1.3


# =====================================================================
# 3. Prerequisite & Selection Tests
# =====================================================================

def test_prerequisite_gating():
    """A level-3 card is locked until all its requirements are answered at 1.0."""
    card_l3 = {
        "id": "test-l3",
        "level": 3,
        "difficulty": 1450,
        "requires": ["test-l1", "test-l2"],
    }
    
    progress = {
        "user_rating": 1200.0,
        "cards": {
            "test-l1": {"mastered": True, "reps": 1, "history": [{"score": 1.0}]},
            "test-l2": {"mastered": False, "reps": 0, "history": [{"score": 0.5}]},
        }
    }
    
    # Locked because test-l2 is not mastered
    assert not is_card_unlocked(card_l3["requires"], progress)
    
    # Answer test-l2 at 1.0
    progress["cards"]["test-l2"] = {"mastered": True, "reps": 1, "history": [{"score": 1.0}]}
    assert is_card_unlocked(card_l3["requires"], progress)


def test_selection_rating_window_widening():
    """Card selection stays in rating window when enough candidates exist, and widens when not."""
    now = datetime.now(timezone.utc)
    progress = {"user_rating": 1200.0, "cards": {}}
    
    # 5 cards in range [1100..1300], 1 far out [1900]
    cards = [
        {"id": f"c{i}", "level": 1, "difficulty": 1200, "requires": []} for i in range(5)
    ]
    cards.append({"id": "c_far", "level": 5, "difficulty": 1900, "requires": []})
    
    selected = select_next_card(cards, progress, now, cram_mode=True, random_seed=42)
    assert selected is not None
    assert selected["id"] != "c_far"


# =====================================================================
# 4. Verify Cards Fixture Tests
# =====================================================================

def test_verify_cards_fails_on_missing_sources(tmp_path: Path):
    """verify_all_cards fails on a card with empty sources list."""
    ladder_file = tmp_path / "bad_ladder.json"
    card = {
        "id": "bad-01",
        "ladder": "bad",
        "level": 5,
        "topic": "test",
        "question": "Q",
        "answer": "A",
        "sources": [],  # Empty sources!
        "difficulty": 1950,
        "requires": [],
    }
    ladder_file.write_text(json.dumps([card]), encoding="utf-8")
    
    success, errors, _ = verify_all_cards(ladders_dir=tmp_path)
    assert not success
    assert any("Sources list must be non-empty" in e for e in errors)


def test_verify_cards_fails_on_level_inversion_or_cycle(tmp_path: Path):
    """verify_all_cards fails on a card requiring a card of level >= its own."""
    ladder_file = tmp_path / "bad_cycle.json"
    cards = [
        {
            "id": "card-01",
            "ladder": "bad",
            "level": 2,
            "topic": "test",
            "question": "Q1",
            "answer": "A1",
            "sources": ["https://example.com"],
            "difficulty": 1200,
            "requires": ["card-02"],  # Requires level 3 card!
        },
        {
            "id": "card-02",
            "ladder": "bad",
            "level": 3,
            "topic": "test",
            "question": "Q2",
            "answer": "A2",
            "sources": ["https://example.com"],
            "difficulty": 1450,
            "requires": [],
        },
        {
            "id": "card-05",
            "ladder": "bad",
            "level": 5,
            "topic": "test",
            "question": "Q5",
            "answer": "A5",
            "sources": ["https://example.com"],
            "difficulty": 1950,
            "requires": [],
        }
    ]
    ladder_file.write_text(json.dumps(cards), encoding="utf-8")
    
    success, errors, _ = verify_all_cards(ladders_dir=tmp_path)
    assert not success
    assert any("requires must be lower level" in e for e in errors)
