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
    get_ladder_rating,
    get_default_ladder_rating,
    migrate_progress,
    DEFAULT_LADDER_RATINGS,
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
    selectable = filter_selectable_cards(cards, progress, now, cram_mode=False)
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
    selectable = filter_selectable_cards(cards, progress, now, cram_mode=False)
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
    selectable = filter_selectable_cards(cards, progress, now, cram_mode=False)
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
        {"id": f"c{i}", "level": 0, "difficulty": 1200, "requires": []} for i in range(5)
    ]
    cards.append({"id": "c_far", "level": 0, "difficulty": 1900, "requires": []})
    
    selected = select_next_card(cards, progress, now, cram_mode=False, random_seed=42)
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


# =====================================================================
# 6. Per-Ladder Rating Tests (Part A)
# =====================================================================

def test_ladder_ratings_are_independent():
    """Answering a PyTorch card increases PyTorch rating while keeping de-grammatik rating unchanged."""
    progress = {
        "ladder_ratings": {
            "pytorch": 820.0,
            "de-grammatik": 1200.0,
        },
        "cards": {}
    }
    
    pytorch_ru = get_ladder_rating(progress, "pytorch")
    german_ru = get_ladder_rating(progress, "de-grammatik")
    assert pytorch_ru == 820.0
    assert german_ru == 1200.0
    
    # User answers a PyTorch card (Rc=800.0) with score 1.0
    new_pyt_ru, new_card_rc = calculate_elo(pytorch_ru, 800.0, 1.0)
    progress["ladder_ratings"]["pytorch"] = new_pyt_ru
    
    assert progress["ladder_ratings"]["pytorch"] > 820.0
    assert progress["ladder_ratings"]["de-grammatik"] == 1200.0  # Strictly unchanged!


def test_migration_seeds_all_ladders_from_legacy_rating():
    """
    The legacy global rating described progress in the ladders that existed while it was the only
    rating -- the ML ones. Ladders introduced afterwards (German) must start at their CONFIGURED
    DEFAULT, not at the legacy value: seeding German at an ML rating puts every German card outside
    the selection window, and 400 draws returned zero German cards before this was fixed.
    Card history must survive either way.
    """
    legacy_progress = {
        "user_rating": 911.48,
        "cards": {
            "card-001": {
                "rating": 1050.0,
                "reps": 3,
                "mastered": True,
                "history": [{"timestamp": "2026-08-20T00:00:00Z", "score": 1.0}]
            }
        }
    }
    
    migrated = migrate_progress(legacy_progress)
    assert "ladder_ratings" in migrated
    # ladders that existed under the legacy global rating keep it
    assert migrated["ladder_ratings"]["pytorch"] == 911.48
    assert migrated["ladder_ratings"]["uncertainty"] == 911.48
    # ladders introduced later take their configured default, NOT the legacy value
    assert migrated["ladder_ratings"]["de-konnektoren"] == 1200.0
    assert migrated["ladder_ratings"]["de-grammatik"] == 1200.0
    assert migrated["ladder_ratings"]["de-wortschatz"] == 1200.0
    assert migrated["ladder_ratings"]["air-quality"] == 911.48
    
    # Assert card history is completely intact
    assert "card-001" in migrated["cards"]
    assert migrated["cards"]["card-001"]["reps"] == 3
    assert migrated["cards"]["card-001"]["mastered"] is True
    assert len(migrated["cards"]["card-001"]["history"]) == 1


def test_selection_uses_the_ladder_rating():
    """With pytorch at 820 and de-grammatik at 1400, selections match each ladder's own rating."""
    now = datetime.now(timezone.utc)
    cards = [
        # PyTorch cards (Level 0)
        {"id": "pyt-01", "ladder": "pytorch", "level": 0, "difficulty": 800, "requires": []},
        {"id": "pyt-02", "ladder": "pytorch", "level": 0, "difficulty": 820, "requires": []},
        {"id": "pyt-03", "ladder": "pytorch", "level": 0, "difficulty": 840, "requires": []},
        {"id": "pyt-far", "ladder": "pytorch", "level": 0, "difficulty": 1400, "requires": []},
        # German cards (Level 0)
        {"id": "de-far", "ladder": "de-grammatik", "level": 0, "difficulty": 800, "requires": []},
        {"id": "de-01", "ladder": "de-grammatik", "level": 0, "difficulty": 1380, "requires": []},
        {"id": "de-02", "ladder": "de-grammatik", "level": 0, "difficulty": 1400, "requires": []},
        {"id": "de-03", "ladder": "de-grammatik", "level": 0, "difficulty": 1420, "requires": []},
    ]
    progress = {
        "ladder_ratings": {
            "pytorch": 820.0,
            "de-grammatik": 1400.0,
        },
        "cards": {}
    }
    
    # 30 draws from PyTorch: should only draw near 820 (never pyt-far at 1400)
    for i in range(30):
        pyt_card = select_next_card(cards, progress, now, cram_mode=False, ladder_filter="pytorch", random_seed=i)
        assert pyt_card is not None
        assert pyt_card["ladder"] == "pytorch"
        assert pyt_card["difficulty"] in (800, 820, 840)
        assert pyt_card["id"] != "pyt-far"
    
    # 30 draws from German: should only draw near 1400 (never de-far at 800)
    for i in range(30):
        de_card = select_next_card(cards, progress, now, cram_mode=False, ladder_filter="de-grammatik", random_seed=i)
        assert de_card is not None
        assert de_card["ladder"] == "de-grammatik"
        assert de_card["difficulty"] in (1380, 1400, 1420)
        assert de_card["id"] != "de-far"


def test_new_ladder_uses_its_configured_default():
    """An unseeded German ladder defaults to 1200, while an unseeded ML ladder defaults to 820."""
    empty_progress = {"ladder_ratings": {}}
    
    assert get_ladder_rating(empty_progress, "de-konnektoren") == 1200.0
    assert get_ladder_rating(empty_progress, "de-grammatik") == 1200.0
    assert get_ladder_rating(empty_progress, "de-wortschatz") == 1200.0
    assert get_ladder_rating(empty_progress, "pytorch") == 820.0
    assert get_ladder_rating(empty_progress, "neural-processes") == 820.0
    assert get_ladder_rating(empty_progress, "uncertainty") == 820.0


def test_verify_cards_fails_on_german_transliteration(tmp_path: Path):
    """verify_all_cards fails on German cards containing unallowed transliterations like 'fuer'."""
    ladder_file = tmp_path / "de-test.json"
    card = {
        "id": "de-test-01",
        "ladder": "de-test",
        "level": 1,
        "topic": "test",
        "question": "Was ist das Wort fuer dieses Phaenomen?",  # Contains 'fuer' instead of 'für'
        "answer": "Die Erklaerung ist einfach.",
        "sources": ["https://www.dwds.de/wb/Wort"],
        "difficulty": 1200,
        "requires": [],
    }
    ladder_file.write_text(json.dumps([card]), encoding="utf-8")
    
    success, errors, _ = verify_all_cards(ladders_dir=tmp_path)
    assert not success
    assert any("contains unallowed transliteration" in e for e in errors)


# =====================================================================
# 7. Atomic Card Selection & Anti-Repetition Tests (Part A)
# =====================================================================

def test_no_card_repeats_within_recency_window():
    """Serve 20 cards from a pool of 30; assert no id appears twice within any window of 8."""
    now = datetime.now(timezone.utc)
    cards = [
        {"id": f"card-{i:02d}", "ladder": "test", "level": 0, "difficulty": 800 + i * 5, "requires": []}
        for i in range(30)
    ]
    progress = {"ladder_ratings": {"test": 850.0}, "cards": {}, "recent": []}
    
    served_ids = []
    for i in range(20):
        selected = select_next_card(cards, progress, now, cram_mode=False, random_seed=i)
        assert selected is not None
        served_ids.append(selected["id"])
        
    # Check that in every window of 8 cards, all 8 IDs are unique
    for start in range(len(served_ids) - 8 + 1):
        window_ids = served_ids[start:start + 8]
        assert len(window_ids) == len(set(window_ids)), f"Duplicate found in window: {window_ids}"


def test_unseen_cards_are_preferred():
    """A pool with 5 unseen and 5 reviewed; the next 5 served are all unseen."""
    now = datetime.now(timezone.utc)
    unseen_cards = [
        {"id": f"unseen-{i}", "ladder": "test", "level": 0, "difficulty": 820, "requires": []}
        for i in range(5)
    ]
    reviewed_cards = [
        {"id": f"reviewed-{i}", "ladder": "test", "level": 0, "difficulty": 820, "requires": []}
        for i in range(5)
    ]
    cards = unseen_cards + reviewed_cards
    
    progress = {
        "ladder_ratings": {"test": 820.0},
        "cards": {
            f"reviewed-{i}": {
                "rating": 820.0,
                "reps": 1,
                "interval_days": 0,  # due immediately
                "last_seen": now.isoformat(),
                "history": [{"score": 1.0}]
            }
            for i in range(5)
        },
        "recent": []
    }
    
    served_unseen = []
    for i in range(5):
        selected = select_next_card(cards, progress, now, cram_mode=False, random_seed=i)
        assert selected is not None
        assert selected["id"].startswith("unseen-")
        served_unseen.append(selected["id"])
        
    assert len(set(served_unseen)) == 5


def test_failed_card_returns_after_five_others():
    """Score a card 0.0; assert it is not among the next 5 served, and does reappear afterwards."""
    now = datetime.now(timezone.utc)
    failed_card = {"id": "failed-card", "ladder": "test", "level": 0, "difficulty": 820, "requires": []}
    other_cards = [
        {"id": f"other-{i}", "ladder": "test", "level": 0, "difficulty": 820, "requires": []}
        for i in range(10)
    ]
    cards = [failed_card] + other_cards
    
    # Progress where 'failed-card' just failed (score 0.0, interval 0 -> due immediately)
    progress = {
        "ladder_ratings": {"test": 820.0},
        "cards": {
            "failed-card": {
                "rating": 820.0,
                "reps": 0,
                "interval_days": 0,
                "last_seen": now.isoformat(),
                "history": [{"score": 0.0}]
            },
            **{
                f"other-{i}": {
                    "rating": 820.0,
                    "reps": 1,
                    "interval_days": 0,
                    "last_seen": now.isoformat(),
                    "history": [{"score": 1.0}]
                }
                for i in range(10)
            }
        },
        "recent": ["failed-card"]
    }
    
    # Next 5 draws must NOT be 'failed-card'
    for i in range(5):
        selected = select_next_card(cards, progress, now, cram_mode=False, random_seed=i)
        assert selected is not None
        assert selected["id"] != "failed-card", f"Failed card served prematurely at draw {i+1}"
        
    # After 5 other cards are served, failed-card is eligible to reappear
    found_failed = False
    for i in range(5, 20):
        selected = select_next_card(cards, progress, now, cram_mode=False, random_seed=i)
        if selected and selected["id"] == "failed-card":
            found_failed = True
            break
            
    assert found_failed, "Failed card never returned after 5 other cards were served"


def test_selector_never_starves():
    """With only 2 selectable cards and a recency window of 8, the selector still returns a card rather than None."""
    now = datetime.now(timezone.utc)
    cards = [
        {"id": "card-A", "ladder": "test", "level": 0, "difficulty": 800, "requires": []},
        {"id": "card-B", "ladder": "test", "level": 0, "difficulty": 820, "requires": []},
    ]
    progress = {
        "ladder_ratings": {"test": 800.0},
        "cards": {},
        "recent": ["card-A", "card-B", "card-A", "card-B", "card-A", "card-B", "card-A", "card-B"]
    }
    
    # Even though recent contains both cards in the last 8 entries, selector relaxes and returns a card
    for i in range(10):
        selected = select_next_card(cards, progress, now, cram_mode=False, random_seed=i)
        assert selected is not None
        assert selected["id"] in ("card-A", "card-B")


# =====================================================================
# 8. Cram Mode & Prerequisite Selection Tests
# =====================================================================

def test_cram_mode_ignores_prerequisites():
    """Card B requiring A is absent in normal mode (empty progress) and present in cram mode."""
    now = datetime.now(timezone.utc)
    card_a = {"id": "card-a", "ladder": "test", "level": 0, "difficulty": 800, "requires": []}
    card_b = {"id": "card-b", "ladder": "test", "level": 0, "difficulty": 800, "requires": ["card-a"]}
    cards = [card_a, card_b]
    progress = {"cards": {}}

    selectable_normal = filter_selectable_cards(cards, progress, now, cram_mode=False)
    assert not any(c["id"] == "card-b" for c in selectable_normal)
    assert any(c["id"] == "card-a" for c in selectable_normal)

    selectable_cram = filter_selectable_cards(cards, progress, now, cram_mode=True)
    assert any(c["id"] == "card-b" for c in selectable_cram)
    assert any(c["id"] == "card-a" for c in selectable_cram)


def test_cram_mode_ignores_level_gate():
    """A card at level 4 in a ladder whose level 0 is unmastered is absent in normal mode and present in cram mode."""
    now = datetime.now(timezone.utc)
    card_l0 = {"id": "card-l0", "ladder": "test-ladder", "level": 0, "difficulty": 800, "requires": []}
    card_l4 = {"id": "card-l4", "ladder": "test-ladder", "level": 4, "difficulty": 1600, "requires": []}
    cards = [card_l0, card_l4]
    progress = {"cards": {}}

    selectable_normal = filter_selectable_cards(cards, progress, now, cram_mode=False)
    assert not any(c["id"] == "card-l4" for c in selectable_normal)
    assert any(c["id"] == "card-l0" for c in selectable_normal)

    selectable_cram = filter_selectable_cards(cards, progress, now, cram_mode=True)
    assert any(c["id"] == "card-l4" for c in selectable_cram)
    assert any(c["id"] == "card-l0" for c in selectable_cram)


def test_normal_mode_still_enforces_prerequisites():
    """Regression guard: with cram_mode=False, a locked card stays locked."""
    now = datetime.now(timezone.utc)
    card_base = {"id": "card-base", "ladder": "ladder-x", "level": 0, "difficulty": 800, "requires": []}
    card_locked = {"id": "card-locked", "ladder": "ladder-x", "level": 0, "difficulty": 800, "requires": ["card-base"]}
    cards = [card_base, card_locked]
    progress = {"cards": {}}

    selectable = filter_selectable_cards(cards, progress, now, cram_mode=False)
    assert any(c["id"] == "card-base" for c in selectable)
    assert not any(c["id"] == "card-locked" for c in selectable)


def test_cram_mode_ignores_elo_window():
    """A ladder whose user rating is far below its high-level cards must still be able to return one in cram mode."""
    now = datetime.now(timezone.utc)
    cards = [
        {"id": f"c_low_{i}", "ladder": "test", "level": 0, "difficulty": 800, "requires": []}
        for i in range(5)
    ]
    cards.append({"id": "c_high", "ladder": "test", "level": 5, "difficulty": 1950, "requires": []})
    progress = {"ladder_ratings": {"test": 800.0}, "cards": {}}

    # In normal mode, c_high is never selected
    for i in range(20):
        normal_sel = select_next_card(cards, progress, now, cram_mode=False, random_seed=i)
        assert normal_sel is not None
        assert normal_sel["id"] != "c_high"

    # In cram mode, c_high is in the pool and can be selected
    cram_selected = [select_next_card(cards, progress, now, cram_mode=True, random_seed=i)["id"] for i in range(50)]
    assert "c_high" in cram_selected




