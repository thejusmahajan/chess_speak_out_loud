"""
Knowledge Trainer — FastAPI Server.

Serves the SRS training engine and Web UI for spaced-repetition interview preparation.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from trainer import schedule as schedule_engine
from trainer.engine import (
    calculate_elo,
    update_sm2,
    is_card_due,
    is_card_unlocked,
    filter_selectable_cards,
    select_next_card,
    get_ladder_rating,
    get_ladder_active_level,
    migrate_progress,
    DEFAULT_LADDER_RATINGS,
)

BASE_DIR = Path(__file__).resolve().parent
LADDERS_DIR = BASE_DIR / "content" / "ladders"
STATE_DIR = BASE_DIR / "state"
STATIC_DIR = BASE_DIR / "static"
TIMETABLE_FILE = BASE_DIR / "content" / "timetable.json"
PROGRESS_FILE = STATE_DIR / "progress.json"
ANSWERS_FILE = STATE_DIR / "answers.jsonl"
COMMENTS_FILE = STATE_DIR / "comments.jsonl"

app = FastAPI(title="Knowledge Trainer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_all_cards() -> List[Dict[str, Any]]:
    """Load all authored cards from content/ladders/*.json."""
    cards = []
    for jf in sorted(LADDERS_DIR.glob("*.json")):
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
                c_list = data if isinstance(data, list) else data.get("cards", [])
                cards.extend(c_list)
        except Exception as e:
            print(f"Error loading {jf}: {e}")
    return cards


def load_progress() -> Dict[str, Any]:
    """Load persistent progress state, migrating legacy ratings on load."""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return migrate_progress(data)
        except Exception:
            pass
    return {"ladder_ratings": dict(DEFAULT_LADDER_RATINGS), "user_rating": 820.0, "cards": {}}


def save_progress(progress: Dict[str, Any]) -> None:
    """Save persistent progress state to disk atomically."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp_file = PROGRESS_FILE.with_suffix(".tmp")
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)
    tmp_file.replace(PROGRESS_FILE)


class GradeRequest(BaseModel):
    card_id: str
    score: float = Field(..., description="1.0 (got it), 0.5 (partial), 0.0 (missed)")


class CommentRequest(BaseModel):
    card_id: str
    ladder: str
    level: int
    category: str
    comment: str
    user_rating: float
    revealed: bool = True


@app.get("/")
def get_index():
    index_html = STATIC_DIR / "index.html"
    if not index_html.exists():
        raise HTTPException(status_code=404, detail="static/index.html not found")
    return FileResponse(index_html)


@app.get("/api/state")
def get_state():
    cards = load_all_cards()
    progress = load_progress()
    now = datetime.now(timezone.utc)
    
    cards_progress = progress.get("cards", {})
    ladder_ratings = progress.get("ladder_ratings", {})
    user_rating = progress.get("user_rating", 820.0)
    
    due_count = 0
    mastered_count = 0
    ladder_groups: Dict[str, List[Dict[str, Any]]] = {}
    
    for c in cards:
        c_id = c["id"]
        c_ladder = c.get("ladder", "unknown")
        ladder_groups.setdefault(c_ladder, []).append(c)
        c_prog = cards_progress.get(c_id)
        if is_card_unlocked(c.get("requires", []), progress):
            if is_card_due(c_prog, now):
                due_count += 1
        if c_prog and (c_prog.get("mastered", False) or c_prog.get("reps", 0) >= 1):
            mastered_count += 1
            
    # Count total answer logs
    answer_count = 0
    if ANSWERS_FILE.exists():
        with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
            answer_count = sum(1 for line in f if line.strip())
            
    ladders = sorted(list(ladder_groups.keys()))
    active_levels = {
        ladder: get_ladder_active_level(l_cards, progress)
        for ladder, l_cards in ladder_groups.items()
    }
    
    return {
        "user_rating": user_rating,
        "ladder_ratings": ladder_ratings,
        "due_count": due_count,
        "total_cards": len(cards),
        "mastered_count": mastered_count,
        "answers_count": answer_count,
        "ladders": ladders,
        "active_levels": active_levels,
    }


@app.get("/api/next-card")
def get_next_card(cram: bool = False, ladder: Optional[str] = None):
    cards = load_all_cards()
    progress = load_progress()
    now = datetime.now(timezone.utc)
    
    card = select_next_card(cards, progress, now, cram_mode=cram, ladder_filter=ladder)
    if not card:
        return {"card": None, "message": "No cards currently due. Switch to Cram Mode to keep drilling!"}
    
    save_progress(progress)
    
    card_id = card["id"]
    card_ladder = card.get("ladder", "default")
    card_prog = progress.get("cards", {}).get(card_id, {})
    current_rc = card_prog.get("rating", card.get("difficulty", 1200.0))
    reps = card_prog.get("reps", 0)
    user_ladder_rating = get_ladder_rating(progress, card_ladder)
    
    return {
        "card": card,
        "current_rating": current_rc,
        "reps": reps,
        "user_rating": user_ladder_rating,
        "ladder_rating": user_ladder_rating,
        "ladder_ratings": progress.get("ladder_ratings", {}),
    }


@app.post("/api/grade")
def post_grade(req: GradeRequest):
    if req.score not in (1.0, 0.5, 0.0):
        raise HTTPException(status_code=400, detail="Score must be 1.0, 0.5, or 0.0")
        
    cards = {c["id"]: c for c in load_all_cards()}
    if req.card_id not in cards:
        raise HTTPException(status_code=404, detail=f"Card '{req.card_id}' not found")
        
    card = cards[req.card_id]
    card_ladder = card.get("ladder", "default")
    progress = load_progress()
    now = datetime.now(timezone.utc)
    
    old_ru = get_ladder_rating(progress, card_ladder)
    card_prog = progress.get("cards", {}).get(req.card_id, {
        "rating": float(card.get("difficulty", 1200)),
        "ease": 2.5,
        "interval_days": 0,
        "reps": 0,
        "last_seen": None,
        "due_date": None,
        "mastered": False,
        "history": [],
    })
    
    old_rc = float(card_prog.get("rating", card.get("difficulty", 1200)))
    ease = float(card_prog.get("ease", 2.5))
    interval_days = int(card_prog.get("interval_days", 0))
    reps = int(card_prog.get("reps", 0))
    
    # 1. Elo update for this specific ladder
    new_ru, new_rc = calculate_elo(old_ru, old_rc, req.score)
    
    # 2. SM-2 update
    new_ease, new_interval_days, new_reps = update_sm2(ease, interval_days, reps, req.score)
    
    due_date = now + timedelta(days=new_interval_days) if new_interval_days > 0 else now
    
    # 3. Update in progress
    card_prog["rating"] = new_rc
    card_prog["ease"] = new_ease
    card_prog["interval_days"] = new_interval_days
    card_prog["reps"] = new_reps
    card_prog["last_seen"] = now.isoformat()
    card_prog["due_date"] = due_date.isoformat()
    if req.score == 1.0:
        card_prog["mastered"] = True
        
    card_prog.setdefault("history", []).append({
        "timestamp": now.isoformat(),
        "score": req.score,
        "user_rating": new_ru,
        "card_rating": new_rc,
    })
    
    # Update ladder_ratings dict and legacy user_rating
    progress.setdefault("ladder_ratings", {})[card_ladder] = new_ru
    progress["user_rating"] = new_ru
    progress.setdefault("cards", {})[req.card_id] = card_prog
    save_progress(progress)
    
    # 4. Append to answers.jsonl
    log_entry = {
        "timestamp": now.isoformat(),
        "card_id": req.card_id,
        "ladder": card_ladder,
        "score": req.score,
        "old_user_rating": old_ru,
        "new_user_rating": new_ru,
        "old_card_rating": old_rc,
        "new_card_rating": new_rc,
        "ease": new_ease,
        "interval_days": new_interval_days,
        "reps": new_reps,
    }
    with open(ANSWERS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
        
    return {
        "success": True,
        "ladder": card_ladder,
        "new_user_rating": new_ru,
        "new_card_rating": new_rc,
        "new_interval_days": new_interval_days,
        "new_ease": new_ease,
        "new_reps": new_reps,
    }


# =====================================================================
# Timetable — the 24/7 day schedule that runs alongside the card drilling
# =====================================================================

def _load_timetable():
    """Read the timetable fresh on every request so editing the JSON takes
    effect without restarting the server."""
    try:
        return schedule_engine.load_timetable(TIMETABLE_FILE)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"timetable not found: {TIMETABLE_FILE}")
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"timetable is invalid: {exc}")


@app.get("/api/schedule")
def get_schedule():
    """The whole day plan. The UI fetches this once and ticks locally, so the
    countdown keeps running even if the server is briefly unreachable."""
    timetable = _load_timetable()
    payload = timetable.to_dict()
    payload["server_now"] = datetime.now().isoformat()
    return payload


@app.get("/api/schedule/now")
def get_schedule_now():
    """Live state: what is running, how long is left, what fires next."""
    return schedule_engine.day_state(_load_timetable(), datetime.now())


@app.get("/api/schedule/daemon")
def get_schedule_daemon(stale_seconds: int = 30):
    """Is the desktop timetable daemon running?

    The daemon rewrites its cursor file every few seconds, so the file's
    freshness is the heartbeat. The browser asks this so it can stay SILENT
    while the desktop alarm has him covered — otherwise an open tab and the
    daemon both sound at the same instant and every alert arrives doubled.
    """
    cursor_file = STATE_DIR / "schedule_daemon.json"
    try:
        with open(cursor_file, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        last_seen = datetime.fromisoformat(payload["cursor"])
    except (OSError, ValueError, KeyError):
        return {"alive": False, "last_seen": None, "age_seconds": None, "pid": None}

    age = (datetime.now() - last_seen).total_seconds()
    return {
        "alive": 0 <= age <= stale_seconds,
        "last_seen": last_seen.isoformat(),
        "age_seconds": round(age, 1),
        "pid": payload.get("pid"),
    }


@app.get("/api/schedule/reminders")
def get_schedule_reminders(hours: float = 24.0):
    """Every reminder due in the next `hours`, with its sound decision."""
    timetable = _load_timetable()
    now = datetime.now()
    window = schedule_engine.reminders_between(timetable, now, now + timedelta(hours=hours))
    return {"now": now.isoformat(), "hours": hours, "reminders": [r.to_dict() for r in window]}


@app.post("/api/comment")
def post_comment(req: CommentRequest):
    now = datetime.now(timezone.utc)
    comment_entry = {
        "timestamp": now.isoformat(),
        "card_id": req.card_id,
        "ladder": req.ladder,
        "level": req.level,
        "category": req.category,
        "comment": req.comment.strip(),
        "user_rating": req.user_rating,
        "revealed": req.revealed,
    }
    
    with open(COMMENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(comment_entry) + "\n")
        
    return {"status": "ok", "message": "Feedback submitted directly to the leader's audit queue."}


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
