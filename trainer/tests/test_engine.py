"""
Unit Tests for Knowledge Trainer Engine & Verification Gate.

Tests Elo dynamics, SM-2 scheduling, prerequisite gating (including Level 0),
candidate selection, and verify_cards validation fixtures.
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


def test_level_zero_prerequisite_gating():
    """A level-1 card requiring level-0 is locked until level-0 is answered at 1.0."""
    now = datetime.now(timezone.utc)
    card_l0 = {
        "id": "pyt-l0-001",
        "ladder": "pytorch",
        "level": 0,
        "difficulty": 780,
        "requires": [],
    }
    card_l1 = {
        "id": "pyt-l1-001",
        "ladder": "pytorch",
        "level": 1,
        "difficulty": 980,
        "requires": ["pyt-l0-001"],
    }
    cards = [card_l0, card_l1]
    
    # Initial state: no cards answered
    progress = {"user_rating": 800.0, "cards": {}}
    
    # Level-1 is locked; only Level-0 is selectable
    selectable = filter_selectable_cards(cards, progress, now, cram_mode=True)
    assert len(selectable) == 1
    assert selectable[0]["id"] == "pyt-l0-001"
    
    # Answer Level-0 with partial 0.5: Level-1 remains locked
    progress["cards"]["pyt-l0-001"] = {
        "rating": 780.0,
        "ease": 2.35,
        "interval_days": 1,
        "reps": 0,
        "mastered": False,
        "history": [{"score": 0.5}],
    }
    selectable = filter_selectable_cards(cards, progress, now, cram_mode=True)
    assert len(selectable) == 1
    assert selectable[0]["id"] == "pyt-l0-001"
    
    # Answer Level-0 with 1.0: Level-1 unlocks immediately
    progress["cards"]["pyt-l0-001"] = {
        "rating": 770.0,
        "ease": 2.6,
        "interval_days": 1,
        "reps": 1,
        "mastered": True,
        "history": [{"score": 1.0}],
    }
    selectable = filter_selectable_cards(cards, progress, now, cram_mode=True)
    assert len(selectable) == 2
    assert any(c["id"] == "pyt-l1-001" for c in selectable)


def test_new_user_is_served_level_zero():
    """Empty progress (and inherited ratings), 200 draws, every card served is level 0."""
    now = datetime.now(timezone.utc)
    ladders_dir = Path("trainer/content/ladders")
    all_cards = []
    for jf in ladders_dir.glob("*.json"):
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)
            all_cards.extend(data if isinstance(data, list) else data.get("cards", []))
            
    # Test completely empty progress (defaults to 1200 rating)
    progress_empty = {"cards": {}}
    levels_served_empty = set()
    for i in range(200):
        card = select_next_card(all_cards, progress_empty, now, cram_mode=False, random_seed=i)
        assert card is not None
        levels_served_empty.add(card.get("level"))
    assert levels_served_empty == {0}

    # Test inherited user rating 1055.6
    progress_inherited = {"user_rating": 1055.6, "cards": {}}
    levels_served_inherited = set()
    for i in range(200):
        card = select_next_card(all_cards, progress_inherited, now, cram_mode=False, random_seed=i)
        assert card is not None
        levels_served_inherited.add(card.get("level"))
    assert levels_served_inherited == {0}


def test_level_one_unreachable_until_level_zero_mastered():
    """Master 50% of a ladder's level-0 cards; assert no level-1 card from that ladder is served. Then master 80%; assert level-1 cards appear."""
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=1)
    # 10 Level 0 cards and 5 Level 1 cards
    cards = [
        {"id": f"l0-{i}", "ladder": "test_ladder", "level": 0, "difficulty": 800, "requires": []}
        for i in range(10)
    ] + [
        {"id": f"l1-{i}", "ladder": "test_ladder", "level": 1, "difficulty": 1000, "requires": []}
        for i in range(5)
    ]
    
    progress = {"user_rating": 800.0, "cards": {}}
    # Master 50% of Level 0 cards (5 / 10)
    for i in range(5):
        progress["cards"][f"l0-{i}"] = {
            "mastered": True,
            "reps": 1,
            "interval_days": 1,
            "last_seen": now.isoformat(),
            "due_date": future.isoformat(),
            "history": [{"score": 1.0}],
        }
        
    for i in range(50):
        card = select_next_card(cards, progress, now, cram_mode=False, random_seed=i)
        assert card is not None
        assert card["level"] == 0
        
    # Master 80% of Level 0 cards (8 / 10)
    for i in range(5, 8):
        progress["cards"][f"l0-{i}"] = {
            "mastered": True,
            "reps": 1,
            "interval_days": 1,
            "last_seen": now.isoformat(),
            "due_date": future.isoformat(),
            "history": [{"score": 1.0}],
        }
        
    level_1_served = False
    for i in range(50):
        card = select_next_card(cards, progress, now, cram_mode=False, random_seed=i)
        if card and card["level"] == 1:
            level_1_served = True
            break
    assert level_1_served


def test_ladders_advance_independently():
    """Master all of pytorch level 0 and none of air_quality level 0; assert pytorch level-1 cards are served and air_quality level-1 cards are not."""
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=1)
    pyt_cards = [
        {"id": f"pyt-0-{i}", "ladder": "pytorch", "level": 0, "difficulty": 800, "requires": []} for i in range(5)
    ] + [
        {"id": f"pyt-1-{i}", "ladder": "pytorch", "level": 1, "difficulty": 1000, "requires": []} for i in range(5)
    ]
    aq_cards = [
        {"id": f"aq-0-{i}", "ladder": "air_quality", "level": 0, "difficulty": 800, "requires": []} for i in range(5)
    ] + [
        {"id": f"aq-1-{i}", "ladder": "air_quality", "level": 1, "difficulty": 1000, "requires": []} for i in range(5)
    ]
    all_cards = pyt_cards + aq_cards
    
    # Rating has climbed to 950 after answering PyTorch cards
    progress = {"user_rating": 950.0, "cards": {}}
    # Master all pytorch level 0 cards
    for i in range(5):
        progress["cards"][f"pyt-0-{i}"] = {
            "mastered": True,
            "reps": 1,
            "interval_days": 1,
            "last_seen": now.isoformat(),
            "due_date": future.isoformat(),
            "history": [{"score": 1.0}],
        }
        
    # Sample 100 draws
    served_cards = [select_next_card(all_cards, progress, now, cram_mode=False, random_seed=i) for i in range(100)]
    assert any(c["ladder"] == "pytorch" and c["level"] == 1 for c in served_cards if c)
    assert not any(c["ladder"] == "air_quality" and c["level"] == 1 for c in served_cards if c)


def test_elo_still_orders_within_a_level():
    """With several level-0 cards of differing difficulty and a fixed user rating, the selector prefers those nearest the rating."""
    now = datetime.now(timezone.utc)
    cards = [
        {"id": "c_close_1", "ladder": "test", "level": 0, "difficulty": 800, "requires": []},
        {"id": "c_close_2", "ladder": "test", "level": 0, "difficulty": 820, "requires": []},
        {"id": "c_close_3", "ladder": "test", "level": 0, "difficulty": 840, "requires": []},
        {"id": "c_far", "ladder": "test", "level": 0, "difficulty": 1200, "requires": []},
    ]
    progress = {"user_rating": 800.0, "cards": {}}
    
    # 50 draws: c_far (difficulty 1200, delta 400 > window 150) should never be chosen because 3 candidates exist within window
    for i in range(50):
        selected = select_next_card(cards, progress, now, cram_mode=False, random_seed=i)
        assert selected is not None
        assert selected["id"] != "c_far"


def test_cram_mode_ignores_level_gating():
    """Cram mode still reaches any unlocked card regardless of ladder active level."""
    now = datetime.now(timezone.utc)
    cards = [
        {"id": "c_l0", "ladder": "test", "level": 0, "difficulty": 800, "requires": []},
        {"id": "c_l5", "ladder": "test", "level": 5, "difficulty": 1950, "requires": []},
    ]
    progress = {"user_rating": 800.0, "cards": {}}
    
    # Non-cram mode only serves level 0
    selected_normal = select_next_card(cards, progress, now, cram_mode=False, random_seed=42)
    assert selected_normal is not None
    assert selected_normal["id"] == "c_l0"
    
    # Cram mode can select level 5
    selectable_cram = filter_selectable_cards(cards, progress, now, cram_mode=True)
    assert any(c["id"] == "c_l5" for c in selectable_cram)


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


def test_verify_cards_fails_on_unbalanced_math_delimiters(tmp_path: Path):
    """verify_all_cards fails on a card containing unbalanced math delimiters."""
    ladder_file = tmp_path / "bad_delim.json"
    card = {
        "id": "bad-delim-01",
        "ladder": "bad",
        "level": 5,
        "topic": "test",
        "question": "What is $x + y for this model?",  # Unbalanced single dollar sign!
        "answer": "The answer is 42.",
        "sources": ["https://example.com"],
        "difficulty": 1950,
        "requires": [],
    }
    ladder_file.write_text(json.dumps([card]), encoding="utf-8")
    
    success, errors, _ = verify_all_cards(ladders_dir=tmp_path)
    assert not success
    assert any("unbalanced inline math delimiters" in e for e in errors)


def test_verify_cards_fails_on_unsupported_latex_macro(tmp_path: Path):
    """verify_all_cards fails on a card containing unsupported macros like \\ref."""
    ladder_file = tmp_path / "bad_macro.json"
    card = {
        "id": "bad-macro-01",
        "ladder": "bad",
        "level": 5,
        "topic": "test",
        "question": "What is the variance $\\sigma^2$ as defined in Equation~\\ref{eq1}?",
        "answer": "The answer is given by $\\text{Var}(y)$.",
        "sources": ["https://example.com"],
        "difficulty": 1950,
        "requires": [],
    }
    ladder_file.write_text(json.dumps([card]), encoding="utf-8")
    
    success, errors, _ = verify_all_cards(ladders_dir=tmp_path)
    assert not success
    assert any("unsupported KaTeX macro '\\ref'" in e for e in errors)
