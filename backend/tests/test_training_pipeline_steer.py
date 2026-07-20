import pytest
import chess.pgn
from backend.training.pipeline import run_diagnosis
from backend.training import store, metrics
import dataclasses

class MockEngine:
    def __init__(self, evaluate_val=50, evaluate_played=50):
        self.analyze_calls = 0
        self.evaluate_val = evaluate_val
        self.evaluate_played = evaluate_played

    async def get_policy_distribution(self, fen, nodes=None):
        return [
            {"uci": "e2e4", "san": "e4", "p": 0.5},
            {"uci": "d2d4", "san": "d4", "p": 0.3},
        ]

    async def analyze(self, fen, depth=None, multipv=1, time_limit=None):
        self.analyze_calls += 1
        return {
            "evaluation": {"type": "cp", "value": self.evaluate_val},
            "wdl": [333, 333, 334],
            "best_moves": [{"move": "e2e4", "score": self.evaluate_val}, {"move": "d2d4", "score": self.evaluate_val - 10}],
            "pv_lines": ["e2e4"]
        }

class MockVision:
    def saliency_absolute(self, fen):
        return {"e4": 1.0}

@pytest.mark.anyio
async def test_steer_budget_exhausted(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "TRAINING_DIR", str(tmp_path))
    monkeypatch.setattr(store, "DATA_DIR", str(tmp_path))

    pgn_text = '[White "TestPlayer"]\n[Black "Opponent"]\n\n1. e4 e5 *'
    engine = MockEngine()
    vision = MockVision()
    orig_budget = metrics.DEFAULT_CONFIG.steer_search_budget
    object.__setattr__(metrics.DEFAULT_CONFIG, "steer_search_budget", 1)

    try:
        await run_diagnosis("test_job_1", pgn_text, "TestPlayer", engine, vision)

        profile = store.load_profile()
        assert profile is not None
        assert profile["steer_budget_exhausted"] is True
        assert engine.analyze_calls == 1
    finally:
        object.__setattr__(metrics.DEFAULT_CONFIG, "steer_search_budget", orig_budget)

@pytest.mark.anyio
async def test_opening_sidelines_excluded(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "TRAINING_DIR", str(tmp_path))
    monkeypatch.setattr(store, "DATA_DIR", str(tmp_path))

    pgn_text = '[White "TestPlayer"]\n[Black "Opponent"]\n\n1. e4 e5 *'
    
    class DivergenceEngine(MockEngine):
        async def get_policy_distribution(self, fen, nodes=None):
            # Best is d4, played is e4. Divergence severity is blind.
            return [
                {"uci": "d2d4", "san": "d4", "p": 0.99},
                {"uci": "e2e4", "san": "e4", "p": 0.00},
            ]

    # Use small eval swing so it's not confirmed.
    engine = DivergenceEngine(evaluate_val=10)
    vision = MockVision()
    orig_budget = metrics.DEFAULT_CONFIG.steer_search_budget
    orig_ply = metrics.DEFAULT_CONFIG.opening_max_ply
    
    object.__setattr__(metrics.DEFAULT_CONFIG, "steer_search_budget", 100)
    try:
        await run_diagnosis("test_job_2", pgn_text, "TestPlayer", engine, vision)

        profile = store.load_profile()
        assert profile is not None
        assert profile["opening_sidelines_excluded"] == 1
        assert len(profile["findings"]) == 0

        object.__setattr__(metrics.DEFAULT_CONFIG, "opening_max_ply", 0)
        
        await run_diagnosis("test_job_3", pgn_text, "TestPlayer", engine, vision)
        profile = store.load_profile()
        assert profile["opening_sidelines_excluded"] == 0
        assert len(profile["findings"]) == 1
    finally:
        object.__setattr__(metrics.DEFAULT_CONFIG, "steer_search_budget", orig_budget)
        object.__setattr__(metrics.DEFAULT_CONFIG, "opening_max_ply", orig_ply)
