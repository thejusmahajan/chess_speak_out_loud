"""Puzzle sets and Puzzle Streak sessions.

Persists custom puzzle sets and tracks streak sessions where puzzles climb
in difficulty across 50-point rating bins and are reshuffled each session.
"""

from __future__ import annotations

import datetime
import json
import os
import random
import re
import uuid
from typing import Optional

import chess

from backend.training import puzzle_regime, store
from backend.training.puzzle_db import DB_PATH

REGIME_DIR = os.getenv("CSZERO_REGIME_DIR", os.path.join(os.path.dirname(DB_PATH), "regime"))
SETS_DIR = os.path.join(REGIME_DIR, "sets")
SESSIONS_DIR = os.path.join(REGIME_DIR, "sessions")


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or f"set-{uuid.uuid4().hex[:8]}"


def _rows_for(ids: list[str]) -> list[dict]:
    """Fetch puzzle rows from the database in the exact order of `ids`."""
    if not ids:
        return []
    with puzzle_regime._connect() as conn:
        qs = ",".join("?" * len(ids))
        rows = [
            dict(r)
            for r in conn.execute(
                f"SELECT id, fen, moves, rating, popularity, themes "
                f"FROM puzzles WHERE id IN ({qs})",
                ids,
            ).fetchall()
        ]
    by_id = {r["id"]: r for r in rows}
    return [by_id[pid] for pid in ids if pid in by_id]


def create_set(
    name: str,
    min_rating: int = 1500,
    max_rating: int = 2000,
    themes: list[str] | None = None,
    size: int = 200,
    min_popularity: int = 80,
) -> dict:
    """Sample puzzles matching criteria and write set to data/puzzles/regime/sets/<slug>.json."""
    where = ["p.rating BETWEEN ? AND ?", "p.popularity >= ?"]
    params: list = [min_rating, max_rating, min_popularity]

    if themes:
        themes = list(themes)
        where.append("(" + " OR ".join("p.themes LIKE ?" for _ in themes) + ")")
        params += [f"%{t}%" for t in themes]

    puzzles = puzzle_regime._sample(" AND ".join(where), params, size, seed=None)

    set_id = _slugify(name)
    now = datetime.datetime.now().isoformat(timespec="seconds")
    deck = {
        "id": set_id,
        "name": name,
        "min_rating": min_rating,
        "max_rating": max_rating,
        "themes": list(themes) if themes else [],
        "size": len(puzzles),
        "created": now,
        "puzzles": puzzles,
    }

    os.makedirs(SETS_DIR, exist_ok=True)
    store._write_json_atomic(os.path.join(SETS_DIR, f"{set_id}.json"), deck)

    return {
        "id": set_id,
        "name": name,
        "min_rating": min_rating,
        "max_rating": max_rating,
        "themes": list(themes) if themes else [],
        "size": len(puzzles),
        "created": now,
    }


def list_sets() -> list[dict]:
    """List metadata for all saved puzzle sets."""
    if not os.path.isdir(SETS_DIR):
        return []
    out = []
    for f in sorted(os.listdir(SETS_DIR)):
        if f.endswith(".json"):
            path = os.path.join(SETS_DIR, f)
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    d = json.load(fp)
                out.append(
                    {
                        "id": d.get("id", f[:-5]),
                        "name": d.get("name", f[:-5]),
                        "min_rating": d.get("min_rating", 1500),
                        "max_rating": d.get("max_rating", 2000),
                        "themes": d.get("themes", []),
                        "size": d.get("size", len(d.get("puzzles", []))),
                        "created": d.get("created", ""),
                    }
                )
            except Exception:
                pass
    return out


def get_set(set_id: str) -> dict:
    """Load a full puzzle set by id."""
    path = os.path.join(SETS_DIR, f"{set_id}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"no set {set_id!r}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def delete_set(set_id: str) -> bool:
    """Delete a puzzle set by id."""
    path = os.path.join(SETS_DIR, f"{set_id}.json")
    if os.path.exists(path):
        try:
            os.remove(path)
            return True
        except OSError:
            return False
    return False


def streak_order(puzzles: list[dict], seed: int | None = None) -> list[dict]:
    """Bucket puzzles into 50-point rating bins, shuffle within buckets, and concatenate ascending."""
    rng = random.Random(seed)
    buckets: dict[int, list[dict]] = {}
    for p in puzzles:
        b = p["rating"] // 50
        buckets.setdefault(b, []).append(p)

    ordered: list[dict] = []
    for b in sorted(buckets.keys()):
        items = list(buckets[b])
        rng.shuffle(items)
        ordered.extend(items)
    return ordered


def _orientation(row: dict, board: chess.Board) -> str:
    """Side the solver plays, fixed for the whole puzzle.

    Falls back to the live board only for the empty placeholder row used by the
    session-completed payload, which carries no fen/moves.
    """
    if row.get("fen") and row.get("moves"):
        try:
            start_board, _ = puzzle_regime.puzzle_position(row)
            return "white" if start_board.turn == chess.WHITE else "black"
        except (ValueError, IndexError, AssertionError):
            pass
    return "white" if board.turn == chess.WHITE else "black"


def _format_payload(session: dict, row: dict, board: chess.Board, **kwargs) -> dict:
    themes = row.get("themes", "")
    if isinstance(themes, str):
        themes_list = themes.split()
    elif isinstance(themes, list):
        themes_list = themes
    else:
        themes_list = []

    payload = {
        "id": session["id"],
        "session_id": session["id"],
        "set_id": session["set_id"],
        "seed": session.get("seed"),
        "index": session["index"],
        "ply": session["ply"],
        "streak": session["streak"],
        "best_streak": session["best_streak"],
        "alive": session["alive"],
        "order": session["order"],
        "history": session.get("history", []),
        "total": len(session["order"]),
        "fen": board.fen(),
        # Orientation is a property of the PUZZLE, not of the live board, so it
        # must stay fixed while the solution plays out. Deriving it from
        # board.turn flipped the board at the instant a puzzle was solved: the
        # final solver move hands the turn to the opponent.
        "orientation": _orientation(row, board),
        "rating": row.get("rating", 0),
        "themes": themes_list,
        "puzzle_url": f"https://lichess.org/training/{row.get('id', '')}",
    }
    payload.update(kwargs)
    return payload


def _session_path(session_id: str) -> str:
    return os.path.join(SESSIONS_DIR, f"{session_id}.json")


def _load_session_data(session_id: str) -> dict:
    path = _session_path(session_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"no session {session_id!r}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_session_data(session: dict) -> None:
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    store._write_json_atomic(_session_path(session["id"]), session)


def start_session(set_id: str, seed: int | None = None) -> dict:
    """Create a new streak session for a set, ordering puzzles in ascending difficulty."""
    set_data = get_set(set_id)
    puzzles = set_data.get("puzzles", [])
    ordered = streak_order(puzzles, seed=seed)

    session_id = uuid.uuid4().hex[:12]
    session = {
        "id": session_id,
        "set_id": set_id,
        "seed": seed if seed is not None else random.randint(0, 2**31 - 1),
        "index": 0,
        "ply": 0,
        "streak": 0,
        "best_streak": 0,
        "alive": True,
        "started": datetime.datetime.now().isoformat(timespec="seconds"),
        "order": [p["id"] for p in ordered],
        "history": [],
    }

    _save_session_data(session)

    if session["order"]:
        first_row = _rows_for([session["order"][0]])[0]
        board, _ = puzzle_regime.puzzle_position(first_row)
        return _format_payload(session, first_row, board)
    else:
        return _format_payload(session, {"id": "", "rating": 0, "themes": ""}, chess.Board())


def get_session(session_id: str) -> dict:
    """Get current puzzle state and streak metrics for a session."""
    session = _load_session_data(session_id)
    if session["index"] < len(session["order"]):
        puzzle_id = session["order"][session["index"]]
        rows = _rows_for([puzzle_id])
        if not rows:
            raise FileNotFoundError(f"puzzle row {puzzle_id!r} not found in database")
        row = rows[0]
        board, solution = puzzle_regime.puzzle_position(row)
        for m in solution[: session["ply"]]:
            board.push_uci(m)
        return _format_payload(session, row, board)
    else:
        return _format_payload(
            session,
            {"id": "", "rating": 0, "themes": ""},
            chess.Board(),
            completed=True,
        )


def submit_move(session_id: str, uci: str) -> dict:
    """Submit a solver move in UCI format, evaluating correctness, mate exception, and replies."""
    session = _load_session_data(session_id)
    if not session["alive"]:
        return get_session(session_id)

    if session["index"] >= len(session["order"]):
        return get_session(session_id)

    puzzle_id = session["order"][session["index"]]
    rows = _rows_for([puzzle_id])
    if not rows:
        raise FileNotFoundError(f"puzzle row {puzzle_id!r} not found")
    row = rows[0]

    board, solution = puzzle_regime.puzzle_position(row)
    for m in solution[: session["ply"]]:
        board.push_uci(m)

    expected_uci = solution[session["ply"]]
    expected_move = chess.Move.from_uci(expected_uci)

    try:
        user_move = chess.Move.from_uci(uci)
    except (ValueError, chess.InvalidMoveError):
        user_move = None

    is_correct = False
    if user_move and user_move in board.legal_moves:
        if uci == expected_uci:
            is_correct = True
        elif session["ply"] == len(solution) - 1:
            probe = board.copy()
            probe.push(user_move)
            if probe.is_checkmate():
                is_correct = True

    if is_correct:
        if session["ply"] + 1 < len(solution):
            # Mid-solution: play solver's move and auto-play forced reply
            board.push(expected_move if uci == expected_uci else user_move)
            opponent_uci = solution[session["ply"] + 1]
            board.push_uci(opponent_uci)
            session["ply"] += 2
            _save_session_data(session)
            return _format_payload(
                session,
                row,
                board,
                correct=True,
                solved=False,
                opponent_uci=opponent_uci,
                ply=session["ply"],
            )
        else:
            # Solved puzzle
            board.push(expected_move if uci == expected_uci else user_move)
            session["streak"] += 1
            session["best_streak"] = max(session["best_streak"], session["streak"])
            session["history"].append(
                {
                    "puzzle_id": row["id"],
                    "rating": row["rating"],
                    "solved": True,
                    "streak": session["streak"],
                }
            )
            puzzle_regime.record("streak", row, correct=True, elapsed=0.0, timed_out=False)
            _save_session_data(session)
            return _format_payload(session, row, board, correct=True, solved=True)
    else:
        # Wrong move -> Run ends immediately
        session["alive"] = False
        streak_ended_at = session["streak"]
        session["history"].append(
            {
                "puzzle_id": row["id"],
                "rating": row["rating"],
                "solved": False,
                "streak_ended_at": streak_ended_at,
            }
        )

        line = chess.Board(row["fen"])
        line.push_uci(row["moves"].split()[0])
        san = line.variation_san([chess.Move.from_uci(m) for m in solution])

        puzzle_regime.record("streak", row, correct=False, elapsed=0.0, timed_out=False)
        _save_session_data(session)

        return _format_payload(
            session,
            row,
            board,
            correct=False,
            solved=False,
            alive=False,
            solution=solution,
            solution_san=san,
            streak_ended_at=streak_ended_at,
        )


def next_puzzle(session_id: str) -> dict:
    """Advance to the next puzzle in the streak session."""
    session = _load_session_data(session_id)
    if not session["alive"]:
        return get_session(session_id)

    session["index"] += 1
    session["ply"] = 0
    _save_session_data(session)

    if session["index"] >= len(session["order"]):
        return _format_payload(
            session,
            {"id": "", "rating": 0, "themes": ""},
            chess.Board(),
            completed=True,
        )

    puzzle_id = session["order"][session["index"]]
    rows = _rows_for([puzzle_id])
    if not rows:
        raise FileNotFoundError(f"puzzle row {puzzle_id!r} not found")
    row = rows[0]
    board, _ = puzzle_regime.puzzle_position(row)
    return _format_payload(session, row, board)
