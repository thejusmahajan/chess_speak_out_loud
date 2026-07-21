import os
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.training import store, explanations
from backend import llm_client

@pytest.fixture(autouse=True)
def mock_data_dir(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    training_dir = data_dir / "training"
    monkeypatch.setattr(store, "DATA_DIR", str(data_dir))
    monkeypatch.setattr(store, "TRAINING_DIR", str(training_dir))
    return data_dir

FEN_1 = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
FEN_2 = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
FEN_3 = "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1"
FEN_4 = "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq c3 0 1"
FEN_5 = "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1"

@pytest.mark.anyio
async def test_only_critical_nodes_get_explanations(monkeypatch):
    gen_mock = AsyncMock(return_value="Coach explanation for critical move.")
    monkeypatch.setattr(llm_client, "generate_move_explanation", gen_mock)

    tree = {
        "eco": "C20",
        "color": "white",
        "nodes": [
            {"id": "n1", "fen_before": FEN_1, "critical": True, "user_move": {"uci": "e2e4", "san": "e4"}, "critical_reason": "blind_rate"},
            {"id": "n2", "fen_before": FEN_2, "critical": False, "user_move": {"uci": "e7e5", "san": "e5"}},
            {"id": "n3", "fen_before": FEN_3, "critical": True, "user_move": {"uci": "d2d4", "san": "d4"}, "critical_reason": "complexity"},
            {"id": "n4", "fen_before": FEN_4, "critical": False, "user_move": {"uci": "c2c4", "san": "c4"}},
        ]
    }

    enriched = await explanations.enrich_tree_explanations(tree)

    assert enriched["nodes"][0]["explanation"] == "Coach explanation for critical move."
    assert "explanation" not in enriched["nodes"][1]
    assert enriched["nodes"][2]["explanation"] == "Coach explanation for critical move."
    assert "explanation" not in enriched["nodes"][3]
    assert gen_mock.call_count == 2

@pytest.mark.anyio
async def test_generation_happens_once_per_position(monkeypatch):
    gen_mock = AsyncMock(return_value="Single generated explanation.")
    monkeypatch.setattr(llm_client, "generate_move_explanation", gen_mock)

    tree1 = {
        "nodes": [
            {"id": "n1", "fen_before": FEN_1, "critical": True, "user_move": {"uci": "e2e4", "san": "e4"}}
        ]
    }

    res1 = await explanations.enrich_tree_explanations(tree1)
    assert res1["nodes"][0]["explanation"] == "Single generated explanation."
    assert gen_mock.call_count == 1

    tree2 = {
        "nodes": [
            {"id": "n1_fresh", "fen_before": FEN_1, "critical": True, "user_move": {"uci": "e2e4", "san": "e4"}}
        ]
    }

    res2 = await explanations.enrich_tree_explanations(tree2)
    assert res2["nodes"][0]["explanation"] == "Single generated explanation."
    assert gen_mock.call_count == 1

@pytest.mark.anyio
async def test_cache_persists_across_instances(monkeypatch):
    gen_mock = AsyncMock(return_value="Persisted explanation.")
    monkeypatch.setattr(llm_client, "generate_move_explanation", gen_mock)

    tree1 = {
        "nodes": [
            {"id": "n1", "fen_before": FEN_1, "critical": True, "user_move": {"uci": "e2e4", "san": "e4"}}
        ]
    }

    await explanations.enrich_tree_explanations(tree1)
    assert gen_mock.call_count == 1

    # Simulate fresh run reading from disk cache
    gen_mock_new = AsyncMock(return_value="Should not be called.")
    monkeypatch.setattr(llm_client, "generate_move_explanation", gen_mock_new)

    tree2 = {
        "nodes": [
            {"id": "n1_new", "fen_before": FEN_1, "critical": True, "user_move": {"uci": "e2e4", "san": "e4"}}
        ]
    }

    res2 = await explanations.enrich_tree_explanations(tree2)
    assert res2["nodes"][0]["explanation"] == "Persisted explanation."
    assert gen_mock_new.call_count == 0

@pytest.mark.anyio
async def test_max_new_caps_new_generations(monkeypatch):
    gen_mock = AsyncMock(side_effect=lambda ctx, model="gemini-3.5-flash": f"Explanation for {ctx['move_san']}")
    monkeypatch.setattr(llm_client, "generate_move_explanation", gen_mock)

    fens = [FEN_1, FEN_2, FEN_3, FEN_4, FEN_5]
    tree = {
        "nodes": [
            {"id": f"n{i}", "fen_before": fens[i], "critical": True, "user_move": {"uci": f"m{i}", "san": f"M{i}"}}
            for i in range(5)
        ]
    }

    res1 = await explanations.enrich_tree_explanations(tree, max_new=2)
    assert gen_mock.call_count == 2
    assert "explanation" in res1["nodes"][0]
    assert "explanation" in res1["nodes"][1]
    assert "explanation" not in res1["nodes"][2]
    assert "explanation" not in res1["nodes"][3]
    assert "explanation" not in res1["nodes"][4]

    # Follow-up enrich with max_new=8 fills the remaining 3
    res2 = await explanations.enrich_tree_explanations(tree, max_new=8)
    assert gen_mock.call_count == 5  # 2 + 3 = 5
    for i in range(5):
        assert "explanation" in res2["nodes"][i]

@pytest.mark.anyio
async def test_no_critical_nodes_no_calls(monkeypatch):
    gen_mock = AsyncMock()
    monkeypatch.setattr(llm_client, "generate_move_explanation", gen_mock)

    tree = {
        "nodes": [
            {"id": "n1", "fen_before": FEN_1, "critical": False, "user_move": {"uci": "e2e4", "san": "e4"}},
            {"id": "n2", "fen_before": FEN_2, "critical": False}
        ]
    }

    res = await explanations.enrich_tree_explanations(tree)
    assert gen_mock.call_count == 0
    assert "explanation" not in res["nodes"][0]
    assert "explanation" not in res["nodes"][1]

@pytest.mark.anyio
async def test_malformed_node_skipped(monkeypatch):
    gen_mock = AsyncMock(return_value="Valid node explanation.")
    monkeypatch.setattr(llm_client, "generate_move_explanation", gen_mock)

    tree = {
        "nodes": [
            {"id": "bad1", "fen_before": "NOT_A_VALID_FEN", "critical": True, "user_move": {"uci": "e2e4", "san": "e4"}},
            {"id": "bad2", "fen_before": FEN_1, "critical": True, "user_move": None},
            {"id": "good", "fen_before": FEN_2, "critical": True, "user_move": {"uci": "e7e5", "san": "e5"}}
        ]
    }

    res = await explanations.enrich_tree_explanations(tree)
    assert gen_mock.call_count == 1
    assert "explanation" not in res["nodes"][0]
    assert "explanation" not in res["nodes"][1]
    assert res["nodes"][2]["explanation"] == "Valid node explanation."

@pytest.mark.anyio
async def test_explanation_attached_where_ui_reads_it(monkeypatch):
    gen_mock = AsyncMock(return_value="Play Nf3 to control d4.")
    monkeypatch.setattr(llm_client, "generate_move_explanation", gen_mock)

    tree = {
        "nodes": [
            {"id": "n1", "fen_before": FEN_1, "critical": True, "user_move": {"uci": "g1f3", "san": "Nf3"}}
        ]
    }

    res = await explanations.enrich_tree_explanations(tree)
    explanation = res["nodes"][0].get("explanation")
    assert isinstance(explanation, str)
    assert len(explanation) > 0
    assert explanation == "Play Nf3 to control d4."

@pytest.mark.anyio
async def test_generate_move_explanation_no_key_fallback(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    mock_genai_model = MagicMock()
    monkeypatch.setattr(llm_client.genai, "GenerativeModel", mock_genai_model)

    context = {
        "fen": FEN_1,
        "move_san": "e4",
        "move_uci": "e2e4",
        "critical_reason": "blind_rate",
        "user_blind_rate": 0.6,
        "color": "white",
        "opening_name": "King's Pawn"
    }

    result = await llm_client.generate_move_explanation(context)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "e4" in result
    assert mock_genai_model.call_count == 0

@pytest.mark.anyio
async def test_generate_move_explanation_exception_fallback(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-fake-key")

    mock_model_instance = MagicMock()
    mock_model_instance.generate_content_async = AsyncMock(side_effect=RuntimeError("API quota exceeded"))
    monkeypatch.setattr(llm_client.genai, "GenerativeModel", MagicMock(return_value=mock_model_instance))

    context = {
        "fen": FEN_1,
        "move_san": "d4",
        "move_uci": "d2d4",
        "critical_reason": "eval_swing",
        "color": "white",
        "opening_name": "Queen's Pawn"
    }

    result = await llm_client.generate_move_explanation(context)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "d4" in result

@pytest.mark.anyio
async def test_prompt_carries_context(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-fake-key")

    captured_prompt = {}

    mock_response = MagicMock()
    mock_response.text = "Mock LLM output prose."

    async def mock_generate_content_async(prompt, generation_config=None):
        captured_prompt["prompt"] = prompt
        return mock_response

    mock_model_instance = MagicMock()
    mock_model_instance.generate_content_async = mock_generate_content_async
    monkeypatch.setattr(llm_client.genai, "GenerativeModel", MagicMock(return_value=mock_model_instance))

    context = {
        "fen": FEN_1,
        "move_san": "c4",
        "move_uci": "c2c4",
        "critical_reason": "blind_rate",
        "user_blind_rate": 0.75,
        "color": "white",
        "opening_name": "English Opening",
        "opponent_replies": [{"san": "e5", "pct": 45}, {"san": "c5", "pct": 30}]
    }

    result = await llm_client.generate_move_explanation(context)
    assert result == "Mock LLM output prose."
    assert "prompt" in captured_prompt
    p = captured_prompt["prompt"]
    assert FEN_1 in p
    assert "c4" in p
    assert "blind" in p.lower()

@pytest.mark.anyio
async def test_plain_text_contract(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-fake-key")

    mock_response = MagicMock()
    mock_response.text = "<b>c4</b> is great! *Watch out* for e5."

    mock_model_instance = MagicMock()
    mock_model_instance.generate_content_async = AsyncMock(return_value=mock_response)
    monkeypatch.setattr(llm_client.genai, "GenerativeModel", MagicMock(return_value=mock_model_instance))

    context = {
        "fen": FEN_1,
        "move_san": "c4",
        "move_uci": "c2c4",
        "critical_reason": "complexity",
        "color": "white",
        "opening_name": "English Opening"
    }

    # Test real path output cleaned
    result_real = await llm_client.generate_move_explanation(context)
    assert "<" not in result_real
    assert ">" not in result_real
    assert "*" not in result_real

    # Test fallback output clean
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result_fallback = await llm_client.generate_move_explanation(context)
    assert "<" not in result_fallback
    assert ">" not in result_fallback
    assert "`" not in result_fallback


@pytest.mark.anyio
async def test_enrich_calls_real_generate_with_correct_signature(monkeypatch):
    """Regression guard: run enrich WITHOUT mocking the generator and with no
    API key, so the REAL generate_move_explanation executes (its deterministic
    fallback). Catches call-signature drift (the model=/llm_model= mismatch)
    that the mocked tests hid — a TypeError here would fail the test."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    import chess
    tree = {
        "eco": "A40", "color": "white",
        "nodes": [{
            "id": "n1", "fen_before": chess.Board().fen(), "is_user_node": True,
            "user_move": {"uci": "d2d4", "san": "d4"}, "critical": True,
            "critical_reason": "blind_rate", "eval_cp": 26,
            "user_blind_rate": 0.6, "opponent_replies": [],
        }],
    }
    out = await explanations.enrich_tree_explanations(tree)
    exp = out["nodes"][0].get("explanation")
    assert isinstance(exp, str) and exp            # non-empty fallback string
    assert "<" not in exp and ">" not in exp       # plain-text contract
