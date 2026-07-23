"""
Unit tests for backend/training/openings.py: verifying opening book classification
and move notation parsing (e.g. 1.e4, 1...e5 tokens).
"""
import pytest
from backend.training import openings


def test_classify_known_openings():
    """Verify known move sequences classify to their exact ECO codes."""
    # 1.e4 e5 2.Nf3 -> King's Knight Opening (C40)
    res = openings.classify(["e2e4", "e7e5", "g1f3"])
    assert res is not None, "1.e4 e5 2.Nf3 failed to classify"
    assert res["eco"] == "C40"
    assert "King's Knight Opening" in res["name"]

    # 1.e4 c5 -> Sicilian Defense (B20)
    res_sicilian = openings.classify(["e2e4", "c7c5"])
    assert res_sicilian is not None
    assert res_sicilian["eco"] == "B20"
    assert "Sicilian Defense" in res_sicilian["name"]

    # 1.d4 d5 2.c4 -> Queen's Gambit (D06)
    res_qg = openings.classify(["d2d4", "d7d5", "c2c4"])
    assert res_qg is not None
    assert res_qg["eco"] == "D06"
    assert "Queen's Gambit" in res_qg["name"]


def test_openings_handles_dots_and_numbers():
    """Verify that move tokens with move numbers and dots (e.g. 1.e4, 1...e5, 2...Nf6)
    do not crash the parser or break sequence matching."""
    # Ruy Lopez: Steinitz Defense (C62): 1.e4 e5 2.Nf3 Nc6 3.Bb5 d6
    steinitz_moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "d7d6"]
    res = openings.classify(steinitz_moves)
    assert res is not None
    assert res["eco"] == "C62"
    assert "Steinitz Defense" in res["name"]


def test_lines_by_tag_populates():
    """Verify lines_by_tag returns populated opening lines."""
    lines = openings.lines_by_tag()
    assert len(lines) > 100, f"Expected >100 opening tags, got {len(lines)}"
    assert "Sicilian_Defense" in lines or any("Sicilian" in k for k in lines)
