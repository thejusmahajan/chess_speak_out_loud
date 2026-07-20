"""C2 gate: repertoire target ranking, color filtering, soundness sign
handling, engine budget cap — all against stubbed puzzle_db/openings/engine."""

import anyio
import chess

from backend.training import select_repertoire as sr

START_FEN = chess.Board().fen()


def run(coro):
    return anyio.run(lambda: coro)


def make_profile(by_motif):
    return {"aggregates": {"by_motif": by_motif}}


PROFILE = make_profile({
    "sacrifice": {"blind": 2, "missed": 4},   # 2*2+4 = 8
    "pin":       {"blind": 1, "missed": 5},   # 2*1+5 = 7
    "fork":      {"blind": 3, "missed": 0},   # 2*3+0 = 6
    "skewer":    {"blind": 0, "missed": 2},   # 2*0+2 = 2 (cut by top-3)
})


class FakeEngine:
    def __init__(self, evals_by_fen, wdl=(400, 300, 300)):
        self.evals = evals_by_fen
        self.wdl = list(wdl)
        self.calls = []

    async def analyze(self, fen, depth=None, multipv=1, time_limit=None):
        self.calls.append(fen)
        return {"evaluation": self.evals.get(fen, 0),
                "pv_lines": [], "wdl": self.wdl}


def stub_data(monkeypatch, tags):
    """tags: dict tag -> {"uci_moves": [...], "fen": str}"""
    lines = {t: {"eco": "B00", "name": t.replace("_", " "),
                 "uci_moves": spec["uci_moves"], "fen": spec["fen"]}
             for t, spec in tags.items()}
    monkeypatch.setattr(sr.openings, "lines_by_tag", lambda: lines)
    monkeypatch.setattr(sr.puzzle_db, "opening_tags_ranked",
                        lambda motif, **kw: [(t, 0.2, 500) for t in tags])
    monkeypatch.setattr(sr.puzzle_db, "motif_profile",
                        lambda tag: {"sacrifice": 0.30, "pin": 0.20,
                                     "fork": 0.10, "skewer": 0.05})


def test_target_ranking_weights():
    targets = sr._target_motifs(PROFILE)
    assert targets == [("sacrifice", 8), ("pin", 7), ("fork", 6)]


def test_zero_weight_motifs_excluded():
    profile = make_profile({"fork": {"blind": 0, "missed": 0}})
    assert sr._target_motifs(profile) == []


def test_color_filtering(monkeypatch):
    tags = {
        "White_Line": {"uci_moves": ["e2e4"], "fen": START_FEN},          # white owns
        "Black_Line": {"uci_moves": ["e2e4", "c7c5"], "fen": START_FEN},  # black owns
    }
    stub_data(monkeypatch, tags)
    engine = FakeEngine({START_FEN: 0})

    rep = run(sr.build_repertoire(PROFILE, "black", engine))
    assert [r["tag"] for r in rep["recommendations"]] == ["Black_Line"]

    rep = run(sr.build_repertoire(PROFILE, "white", FakeEngine({START_FEN: 0})))
    assert [r["tag"] for r in rep["recommendations"]] == ["White_Line"]


def test_soundness_sign_for_black(monkeypatch):
    """White-POV +200 is UNSOUND for a black repertoire; -20 is fine."""
    fen_bad = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    fen_ok = "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1"
    tags = {
        "Bad_For_Black": {"uci_moves": ["e2e4", "c7c5"], "fen": fen_bad},
        "Ok_For_Black":  {"uci_moves": ["d2d4", "d7d5"], "fen": fen_ok},
    }
    stub_data(monkeypatch, tags)
    engine = FakeEngine({fen_bad: 200, fen_ok: -20})

    rep = run(sr.build_repertoire(PROFILE, "black", engine))
    assert [r["tag"] for r in rep["recommendations"]] == ["Ok_For_Black"]
    assert rep["recommendations"][0]["eval_cp"] == -20


def test_soundness_sign_for_white(monkeypatch):
    tags = {"Bad_For_White": {"uci_moves": ["e2e4"], "fen": START_FEN}}
    stub_data(monkeypatch, tags)
    engine = FakeEngine({START_FEN: -200})

    rep = run(sr.build_repertoire(PROFILE, "white", engine))
    assert rep["recommendations"] == []


def test_sharpness_gate(monkeypatch):
    """Draw share above max_draw_pct (45%) rejects the line."""
    tags = {"Drawish": {"uci_moves": ["e2e4"], "fen": START_FEN}}
    stub_data(monkeypatch, tags)
    engine = FakeEngine({START_FEN: 0}, wdl=(200, 600, 200))  # 60% draws

    rep = run(sr.build_repertoire(PROFILE, "white", engine))
    assert rep["recommendations"] == []


def test_engine_budget_cap(monkeypatch):
    """20 sound-looking candidates, all rejected: never more than 15 calls."""
    tags = {}
    evals = {}
    for i in range(20):
        fen = chess.Board().fen().replace(" 0 1", f" 0 {i + 2}")
        # distinct fen strings; ownership white (1 move)
        tags[f"Tag_{i:02d}"] = {"uci_moves": ["e2e4"], "fen": fen}
        evals[fen] = -200  # unsound for white -> no early top_n break
    stub_data(monkeypatch, tags)
    engine = FakeEngine(evals)

    rep = run(sr.build_repertoire(PROFILE, "white", engine, top_n=20))
    assert rep["recommendations"] == []
    assert len(engine.calls) == 15


def test_sacrificial_style_targets_fixed(monkeypatch):
    """Sacrificial style ignores the weakness profile's motifs entirely."""
    tags = {"White_Line": {"uci_moves": ["e2e4"], "fen": START_FEN}}
    stub_data(monkeypatch, tags)
    monkeypatch.setattr(sr.puzzle_db, "motif_profile",
                        lambda tag: {"sacrifice": 0.2, "attraction": 0.1})
    engine = FakeEngine({START_FEN: 0})

    rep = run(sr.build_repertoire(PROFILE, "white", engine, style="sacrificial"))
    assert rep["style"] == "sacrificial"
    assert rep["targets"][0] == {"motif": "sacrifice", "weight": 3}
    assert all(t["motif"] != "pin" for t in rep["targets"])
    rec = rep["recommendations"][0]
    assert rec["primary_motif"] == "sacrifice"


def test_sacrificial_familiarity_boost(monkeypatch):
    """Equal motif scores: the ECO the user already plays ranks first."""
    fen_a = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    fen_b = "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1"
    tags = {
        "Familiar": {"uci_moves": ["e2e4"], "fen": fen_a},
        "Stranger": {"uci_moves": ["d2d4"], "fen": fen_b},
    }
    lines = {t: {"eco": ("C33" if t == "Familiar" else "Z99"),
                 "name": t, "uci_moves": s["uci_moves"], "fen": s["fen"]}
             for t, s in tags.items()}
    monkeypatch.setattr(sr.openings, "lines_by_tag", lambda: lines)
    monkeypatch.setattr(sr.puzzle_db, "opening_tags_ranked",
                        lambda motif, **kw: [(t, 0.2, 500) for t in tags])
    monkeypatch.setattr(sr.puzzle_db, "motif_profile",
                        lambda tag: {"sacrifice": 0.2})
    profile = dict(PROFILE)
    profile["aggregates"] = dict(PROFILE["aggregates"],
                                 by_opening={"C33": {"moves": 50}})
    engine = FakeEngine({fen_a: 0, fen_b: 0})

    rep = run(sr.build_repertoire(profile, "white", engine, style="sacrificial"))
    recs = [r["tag"] for r in rep["recommendations"]]
    assert recs == ["Familiar", "Stranger"]
    scores = {r["tag"]: r["score"] for r in rep["recommendations"]}
    assert scores["Familiar"] == 2 * scores["Stranger"]  # 2x familiarity cap


def test_weakness_style_unchanged_by_familiarity(monkeypatch):
    tags = {"White_Line": {"uci_moves": ["e2e4"], "fen": START_FEN}}
    stub_data(monkeypatch, tags)
    profile = dict(PROFILE)
    profile["aggregates"] = dict(PROFILE["aggregates"],
                                 by_opening={"B00": {"moves": 50}})
    engine = FakeEngine({START_FEN: 0})

    rep = run(sr.build_repertoire(profile, "white", engine))
    assert rep["style"] == "weakness"
    # base score only: 8*0.30 + 7*0.20 + 6*0.10 = 4.4, no familiarity boost
    assert rep["recommendations"][0]["score"] == 4.4


def test_recommendation_output(monkeypatch):
    tags = {"Kings_Gambit": {"uci_moves": ["e2e4", "e7e5", "f2f4"],
                             "fen": START_FEN}}
    stub_data(monkeypatch, tags)
    engine = FakeEngine({START_FEN: 25})

    rep = run(sr.build_repertoire(PROFILE, "white", engine))
    assert rep["color"] == "white"
    assert rep["targets"][0] == {"motif": "sacrifice", "weight": 8}
    rec = rep["recommendations"][0]
    assert rec["line_pgn"] == "1. e4 e5 2. f4"
    assert rec["primary_motif"] == "sacrifice"
    assert rec["draw_pct"] == 30.0
    assert "Kings Gambit" in rec["rationale"]
    assert "30.0%" in rec["rationale"]
    assert "25cp" in rec["rationale"]
