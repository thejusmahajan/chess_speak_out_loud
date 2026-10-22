"""
Goethe-Zertifikat B2 Exam Simulator — FastAPI Application.
Port: 8020
"""

import sys
import os
import json
import base64
import math
import struct
import wave
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from exam_data import EXAM_CONFIG, MODULE_CONTENT
from gemini_evaluator import (
    evaluate_speaking,
    evaluate_writing,
    evaluate_practice_difficult,
    evaluate_sakha,
)
import panini_data
from practice_data import (
    PRACTICE_TIERS,
    PRACTICE_QUESTIONS,
    sanitize_for_client,
    evaluate_objective_question,
)
STATIC_DIR = BASE_DIR / "static"
CONTENT_DIR = BASE_DIR / "content"
AUDIO_DIR = CONTENT_DIR / "audio"
STATE_DIR = BASE_DIR / "state"
SUBMISSIONS_DIR = STATE_DIR / "submissions"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)

# Generate fallback WAV if not exists
def ensure_sample_audio():
    wav_path = AUDIO_DIR / "hoeren_sample.wav"
    if not wav_path.exists():
        sample_rate = 22050
        duration = 10.0
        num_samples = int(sample_rate * duration)
        with wave.open(str(wav_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            frames = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                envelope = 0.5 * (1.0 + math.sin(2 * math.pi * 1.5 * t))
                f0 = 140 + 20 * math.sin(2 * math.pi * 0.9 * t)
                s = 0.6 * math.sin(2 * math.pi * f0 * t) + 0.3 * math.sin(4 * math.pi * f0 * t)
                val = int(envelope * s * 16000)
                frames.extend(struct.pack("<h", max(-32768, min(32767, val))))
            wav_file.writeframes(frames)

ensure_sample_audio()

app = FastAPI(title="Goethe B2 Exam Simulator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/api/exam/config")
def get_config():
    """Returns general exam configuration and module descriptors."""
    return EXAM_CONFIG


@app.get("/api/exam/module/{module_id}")
def get_module(module_id: str):
    """Returns question and instructions for a specific module."""
    module_id = module_id.lower()
    if module_id not in MODULE_CONTENT:
        raise HTTPException(status_code=404, detail=f"Module '{module_id}' not found.")
    
    data = MODULE_CONTENT[module_id]
    # For client safety, we don't expose correct_option directly to the question view
    sanitized = json.loads(json.dumps(data))
    if "question" in sanitized and "correct_option" in sanitized["question"]:
        # Keep options, but don't leak answer key
        pass
    return sanitized
    

# ==============================================================================
# PRACTICE TRAINER (Grammar, Vocabulary & Sentences) API ENDPOINTS
# ==============================================================================

class PracticeSubmission(BaseModel):
    question_id: str
    submission: Any


@app.get("/api/practice/categories")
def get_practice_categories():
    """Returns available practice tiers and overview metadata."""
    return {
        "tiers": PRACTICE_TIERS,
        "total_questions": len(PRACTICE_QUESTIONS),
    }


@app.get("/api/practice/questions")
def get_practice_questions():
    """Returns all 10 practice questions with client-sanitized options."""
    questions = []
    for q_id, q_data in PRACTICE_QUESTIONS.items():
        questions.append(sanitize_for_client(q_data))
    return {
        "total": len(questions),
        "questions": questions,
    }


@app.post("/api/practice/evaluate")
def api_evaluate_practice(sub: PracticeSubmission):
    """
    Evaluates a practice question.
    Objective questions (q1-q8) use deterministic validation with grammar explanations.
    Difficult questions (q9, q10) use Gemini B2 criteria with intelligent fallback.
    """
    q_id = sub.question_id
    if q_id not in PRACTICE_QUESTIONS:
        raise HTTPException(status_code=404, detail=f"Question '{q_id}' not found.")

    q_data = PRACTICE_QUESTIONS[q_id]
    tier = q_data.get("tier")

    if tier in ["simple", "intermediate"]:
        result = evaluate_objective_question(q_id, sub.submission)
    elif tier == "difficult":
        user_text = str(sub.submission or "")
        result = evaluate_practice_difficult(
            question_id=q_id,
            question_data=q_data,
            user_text=user_text,
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unknown tier '{tier}'.")

    # Persist attempt to disk for analytics and diagnostic review
    try:
        log_file = STATE_DIR / "practice_submissions.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "question_id": q_id,
                "tier": tier,
                "submission": sub.submission,
                "is_correct": result.get("is_correct", False),
                "score": result.get("score", 0),
                "feedback": result.get("feedback", ""),
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Error logging practice submission: {e}")

    return result


@app.get("/api/practice/history")
def get_practice_history():
    """Returns past practice attempts logged on the server."""
    log_file = STATE_DIR / "practice_submissions.jsonl"
    if not log_file.exists():
        return {"total_attempts": 0, "history": []}
    
    entries = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    pass
    return {"total_attempts": len(entries), "history": entries}




class WritingSubmission(BaseModel):
    essay_text: str
    task_prompt: Optional[str] = None


@app.post("/api/exam/evaluate-writing")
def api_evaluate_writing(sub: WritingSubmission):
    """Evaluates written essay using Gemini."""
    prompt = sub.task_prompt or MODULE_CONTENT["schreiben"]["prompt"]
    result = evaluate_writing(essay_text=sub.essay_text, task_prompt=prompt)
    return result


class SpeakingSubmission(BaseModel):
    audio_base64: str
    mime_type: Optional[str] = "audio/webm"
    task_prompt: Optional[str] = None


@app.post("/api/exam/evaluate-speaking")
def api_evaluate_speaking(sub: SpeakingSubmission):
    """Evaluates base64 voice recording using Gemini multimodal audio model."""
    try:
        audio_bytes = base64.b64decode(sub.audio_base64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 audio: {e}")
    prompt = sub.task_prompt or MODULE_CONTENT["sprechen"]["prompt"]
    result = evaluate_speaking(
        audio_bytes=audio_bytes,
        mime_type=sub.mime_type or "audio/webm",
        task_prompt=prompt,
    )
    return result


class CompleteExamSubmission(BaseModel):
    timer_mode: str  # "official" or "sprint"
    lesen_answer: Optional[str] = None
    hoeren_answer: Optional[str] = None
    schreiben_text: Optional[str] = None
    sprechen_audio_base64: Optional[str] = None
    sprechen_mime_type: Optional[str] = "audio/webm"


@app.post("/api/exam/submit-complete")
def submit_complete_exam(sub: CompleteExamSubmission):
    """
    Grades all 4 modules and produces the official Goethe B2 Scorecard.
    """
    # 1. Grade Lesen
    correct_lesen = MODULE_CONTENT["lesen"]["question"]["correct_option"]
    user_lesen = (sub.lesen_answer or "").strip().upper()
    lesen_is_correct = (user_lesen == correct_lesen)
    lesen_points = 30 if lesen_is_correct else 0
    lesen_percentage = (lesen_points / 30.0) * 100.0

    # 2. Grade Hören
    correct_hoeren = MODULE_CONTENT["hoeren"]["question"]["correct_option"]
    user_hoeren = (sub.hoeren_answer or "").strip().upper()
    hoeren_is_correct = (user_hoeren == correct_hoeren)
    hoeren_points = 30 if hoeren_is_correct else 0
    hoeren_percentage = (hoeren_points / 30.0) * 100.0

    # 3. Grade Schreiben via Gemini
    schreiben_text = sub.schreiben_text or ""
    if len(schreiben_text.strip()) > 10:
        schreiben_eval = evaluate_writing(
            essay_text=schreiben_text,
            task_prompt=MODULE_CONTENT["schreiben"]["prompt"],
        )
    else:
        schreiben_eval = {
            "total_score": 0,
            "max_score": 100,
            "percentage": 0,
            "passed": False,
            "word_count": len(schreiben_text.split()),
            "scores": {"aufgabenerfuellung": 0, "koharenz": 0, "wortschatz": 0, "korrektheit": 0},
            "examiner_feedback": "Kein Text eingereicht oder Text zu kurz.",
            "corrections": [],
        }
    schreiben_percentage = float(schreiben_eval.get("percentage", 0))

    # 4. Grade Sprechen via Gemini
    if sub.sprechen_audio_base64:
        try:
            audio_bytes = base64.b64decode(sub.sprechen_audio_base64)
            # Save audio to disk for playback & agent evaluation
            latest_audio_path = STATE_DIR / "audio_latest.webm"
            with open(latest_audio_path, "wb") as af:
                af.write(audio_bytes)

            sprechen_eval = evaluate_speaking(
                audio_bytes=audio_bytes,
                mime_type=sub.sprechen_mime_type or "audio/webm",
                task_prompt=MODULE_CONTENT["sprechen"]["prompt"],
            )
        except Exception as e:
            sprechen_eval = {
                "total_score": 0,
                "max_score": 30,
                "percentage": 0,
                "passed": False,
                "transcript": f"Error decoding audio: {e}",
                "scores": {"aufgabenerfuellung": 0, "koherenz_fluessigkeit": 0, "wortschatz_ausdruck": 0, "korrektheit_grammatik": 0, "aussprache_intonation": 0},
                "examiner_summary": f"Audio processing error: {e}",
            }
    else:
        sprechen_eval = {
            "total_score": 0,
            "max_score": 30,
            "percentage": 0,
            "passed": False,
            "transcript": "Keine Audioaufnahme eingereicht.",
            "scores": {"aufgabenerfuellung": 0, "koherenz_fluessigkeit": 0, "wortschatz_ausdruck": 0, "korrektheit_grammatik": 0, "aussprache_intonation": 0},
            "examiner_summary": "Es wurde keine Audioaufnahme für das Modul Sprechen übermittelt.",
        }
    sprechen_percentage = float(sprechen_eval.get("percentage", 0))

    # Summary calculations (Goethe B2 requires 60% in EACH module to pass)
    pass_mark = EXAM_CONFIG["official_pass_percentage"]
    modules_report = {
        "lesen": {
            "title": "Lesen (Reading)",
            "score": lesen_points,
            "max_score": 30,
            "percentage": round(lesen_percentage, 1),
            "passed": lesen_percentage >= pass_mark,
            "user_answer": user_lesen,
            "correct_answer": correct_lesen,
            "explanation": MODULE_CONTENT["lesen"]["question"]["explanation"],
        },
        "hoeren": {
            "title": "Hören (Listening)",
            "score": hoeren_points,
            "max_score": 30,
            "percentage": round(hoeren_percentage, 1),
            "passed": hoeren_percentage >= pass_mark,
            "user_answer": user_hoeren,
            "correct_answer": correct_hoeren,
            "explanation": MODULE_CONTENT["hoeren"]["question"]["explanation"],
        },
        "schreiben": {
            "title": "Schreiben (Writing)",
            "score": schreiben_eval.get("total_score", 0),
            "max_score": schreiben_eval.get("max_score", 100),
            "percentage": round(schreiben_percentage, 1),
            "passed": schreiben_percentage >= pass_mark,
            "evaluation": schreiben_eval,
        },
        "sprechen": {
            "title": "Sprechen (Speaking)",
            "score": sprechen_eval.get("total_score", 0),
            "max_score": sprechen_eval.get("max_score", 30),
            "percentage": round(sprechen_percentage, 1),
            "passed": sprechen_percentage >= pass_mark,
            "evaluation": sprechen_eval,
        },
    }

    all_passed = (
        modules_report["lesen"]["passed"]
        and modules_report["hoeren"]["passed"]
        and modules_report["schreiben"]["passed"]
        and modules_report["sprechen"]["passed"]
    )

    average_percentage = round(
        (lesen_percentage + hoeren_percentage + schreiben_percentage + sprechen_percentage) / 4.0,
        1,
    )

    now_iso = datetime.now(timezone.utc).isoformat()
    submission_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    final_report = {
        "submission_id": submission_id,
        "timestamp": now_iso,
        "timer_mode": sub.timer_mode,
        "overall_result": "BESTANDEN" if all_passed else "NICHT BESTANDEN",
        "all_modules_passed": all_passed,
        "average_percentage": average_percentage,
        "pass_mark": pass_mark,
        "modules": modules_report,
    }

    # Save to disk
    try:
        out_file = SUBMISSIONS_DIR / f"exam_{submission_id}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving submission: {e}")

    return final_report


@app.get("/api/exam/latest-result")
def get_latest_result():
    """Returns the most recent exam submission scorecard."""
    files = sorted(SUBMISSIONS_DIR.glob("exam_*.json"))
    if not files:
        raise HTTPException(status_code=404, detail="No submissions found.")
    with open(files[-1], "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/api/exam/update-eval")
def update_latest_evaluation(updated_data: Dict[str, Any]):
    """Allows updating the latest submission with AI/Agent evaluation results."""
    files = sorted(SUBMISSIONS_DIR.glob("exam_*.json"))
    if not files:
        raise HTTPException(status_code=404, detail="No submissions found.")
    latest_file = files[-1]
    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "schreiben" in updated_data:
        data["modules"]["schreiben"]["evaluation"] = updated_data["schreiben"]
        data["modules"]["schreiben"]["score"] = updated_data["schreiben"].get("total_score", 0)
        data["modules"]["schreiben"]["percentage"] = updated_data["schreiben"].get("percentage", 0)
        data["modules"]["schreiben"]["passed"] = data["modules"]["schreiben"]["percentage"] >= data["pass_mark"]

    if "sprechen" in updated_data:
        data["modules"]["sprechen"]["evaluation"] = updated_data["sprechen"]
        data["modules"]["sprechen"]["score"] = updated_data["sprechen"].get("total_score", 0)
        data["modules"]["sprechen"]["percentage"] = updated_data["sprechen"].get("percentage", 0)
        data["modules"]["sprechen"]["passed"] = data["modules"]["sprechen"]["percentage"] >= data["pass_mark"]

    m = data["modules"]
    all_passed = (
        m["lesen"]["passed"]
        and m["hoeren"]["passed"]
        and m["schreiben"]["passed"]
        and m["sprechen"]["passed"]
    )
    avg = round(
        (m["lesen"]["percentage"] + m["hoeren"]["percentage"] + m["schreiben"]["percentage"] + m["sprechen"]["percentage"]) / 4.0,
        1,
    )
    data["all_modules_passed"] = all_passed
    data["overall_result"] = "BESTANDEN" if all_passed else "NICHT BESTANDEN"
    data["average_percentage"] = avg

    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


# ==============================================================================
# PĀṆINI-KANON B1 → B2 API ENDPOINTS & PROGRESS STATE
# ==============================================================================

PANINI_PROGRESS_FILE = STATE_DIR / "panini_progress.json"

def get_panini_progress() -> Dict[str, Any]:
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    default_progress = {
        "start_date": "2026-09-29",
        "current_week": 1,
        "current_day": 1,
        "streak_days": 1,
        "last_active_date": today_str,
        "sutras_mastered": [],
        "sutras_in_progress": ["sutra_01", "sutra_02"],
        "sakha_submissions": {},
        "transformations_mastered": [],
        "error_hunt_completed": [],
        "translations_completed": [],
        "flashcard_stats": {"reviewed": 0, "mastered": 0},
        "daily_checklist": {}
    }
    if PANINI_PROGRESS_FILE.exists():
        try:
            with open(PANINI_PROGRESS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in default_progress.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception:
            pass
    save_panini_progress(default_progress)
    return default_progress

def save_panini_progress(prog: Dict[str, Any]):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(PANINI_PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(prog, f, ensure_ascii=False, indent=2)

class PaniniSakhaRequest(BaseModel):
    sutra_id: str
    user_text: str

class PaniniTransformRequest(BaseModel):
    id: str
    direction: str  # "schlicht_to_gehoben" or "gehoben_to_schlicht"
    user_text: str

class PaniniErrorHuntRequest(BaseModel):
    id: str
    user_correction: str
    sutra_identified: Optional[Any] = None

class PaniniProgressAction(BaseModel):
    action: str
    data: Optional[Dict[str, Any]] = None

@app.get("/api/panini/overview")
def get_panini_overview():
    """Returns general overview, stats, counts, and guiding principles."""
    counts = panini_data.get_total_counts()
    progress = get_panini_progress()
    return {
        "counts": counts,
        "adhyayis": panini_data.ADHYAYAS,
        "paribhasas": panini_data.PARIBHASAS,
        "progress_summary": {
            "current_week": progress.get("current_week", 1),
            "current_day": progress.get("current_day", 1),
            "streak_days": progress.get("streak_days", 1),
            "sutras_mastered_count": len(progress.get("sutras_mastered", [])),
            "total_sutras": len(panini_data.SUTRAS),
            "transformations_mastered_count": len(progress.get("transformations_mastered", [])),
            "total_transformations": len(panini_data.TRANSFORMATIONS),
            "cards_mastered": progress.get("flashcard_stats", {}).get("mastered", 0),
        }
    }

@app.get("/api/panini/today")
def get_panini_today():
    """Computes today's active study package (sutras, list items, drills, checklist)."""
    prog = get_panini_progress()
    week = prog.get("current_week", 1)
    day = prog.get("current_day", 1)
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    week_sutras = panini_data.get_sutras_for_week(week)
    schedule_entry = panini_data.get_schedule_for_week(week)
    
    active_sutra = None
    if week_sutras:
        sutra_idx = (day - 1) % len(week_sutras)
        active_sutra = week_sutras[sutra_idx]
    
    trans_idx = (day - 1 + (week - 1) * 2) % len(panini_data.TRANSFORMATIONS)
    today_trans = panini_data.TRANSFORMATIONS[trans_idx]
    
    err_idx = (day - 1) % len(panini_data.ERROR_HUNT)
    today_error = panini_data.ERROR_HUNT[err_idx]

    topic_idx = (week - 1) % len(panini_data.TOPICS)
    today_topic = panini_data.TOPICS[topic_idx]
    
    checklist_status = prog.get("daily_checklist", {}).get(today_str, {
        "sutras": False,
        "flashcards": False,
        "listening_reading": False,
        "speaking": False,
        "recitation": False,
    })

    return {
        "date": today_str,
        "week": week,
        "day": day,
        "focus": schedule_entry.get("focus", "B2 Vertiefung"),
        "active_sutra": active_sutra,
        "week_sutras": week_sutras,
        "schedule": schedule_entry,
        "transformation_drill": today_trans,
        "error_hunt_item": today_error,
        "topic": today_topic,
        "checklist": checklist_status,
        "mastered_sutra_ids": prog.get("sutras_mastered", []),
    }

@app.get("/api/panini/sutras")
def get_panini_sutras(week: Optional[int] = None, adhyaya: Optional[str] = None):
    """Returns list of sūtras with optional filters."""
    sutras = list(panini_data.SUTRAS.values())
    if week is not None:
        sutras = [s for s in sutras if week in s.get("weeks", [])]
    if adhyaya is not None:
        sutras = [s for s in sutras if s.get("adhyaya") == adhyaya]
    sutras = sorted(sutras, key=lambda s: s["number"])
    return {"total": len(sutras), "sutras": sutras}

@app.get("/api/panini/sutra/{sutra_id}")
def get_panini_sutra(sutra_id: str):
    """Returns details for a single sūtra."""
    s = panini_data.get_sutra_by_id(sutra_id)
    if not s:
        raise HTTPException(status_code=404, detail=f"Sutra '{sutra_id}' not found.")
    prog = get_panini_progress()
    return {
        "sutra": s,
        "is_mastered": sutra_id in prog.get("sutras_mastered", []),
        "previous_submissions": prog.get("sakha_submissions", {}).get(sutra_id, [])
    }

@app.get("/api/panini/lists")
def get_panini_lists():
    """Returns all 6 Gaṇapāṭha lists."""
    return panini_data.GANAPATHA

@app.get("/api/panini/list/{list_id}")
def get_panini_list(list_id: str):
    """Returns items of a specific list."""
    if list_id not in panini_data.GANAPATHA:
        raise HTTPException(status_code=404, detail=f"List '{list_id}' not found.")
    return panini_data.GANAPATHA[list_id]

@app.get("/api/panini/flashcards")
def get_panini_flashcards(list_id: Optional[str] = None):
    """Returns flashcards from Gaṇapāṭha."""
    cards = panini_data.get_all_flashcard_items()
    if list_id:
        cards = [c for c in cards if c.get("list") == list_id]
    return {"total": len(cards), "cards": cards}

@app.get("/api/panini/transformations")
def get_panini_transformations():
    """Returns all 13 bidirectional transformations and Nominalstil matrix."""
    return {
        "transformations": panini_data.TRANSFORMATIONS,
        "nominalstil_matrix": panini_data.NOMINALSTIL_MATRIX
    }

@app.get("/api/panini/error-hunt")
def get_panini_error_hunt():
    """Returns 10 error-hunt sentences."""
    return panini_data.ERROR_HUNT

@app.get("/api/panini/translations")
def get_panini_translations():
    """Returns 6 translation exercises."""
    return panini_data.TRANSLATIONS

@app.get("/api/panini/topics")
def get_panini_topics():
    """Returns 11 speaking and writing topics."""
    return panini_data.TOPICS

@app.get("/api/panini/schedule")
def get_panini_schedule():
    """Returns 12-week schedule and daily checklist structure."""
    return {
        "schedule": panini_data.SCHEDULE,
        "checklist": panini_data.DAILY_CHECKLIST,
        "paribhasas": panini_data.PARIBHASAS,
    }

@app.get("/api/panini/progress")
def get_panini_progress_endpoint():
    """Returns full progress state."""
    return get_panini_progress()

@app.post("/api/panini/progress")
def update_panini_progress_endpoint(action_req: PaniniProgressAction):
    """Updates progress state based on action."""
    prog = get_panini_progress()
    action = action_req.action
    d = action_req.data or {}

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if action in ("toggle_sutra_mastered", "mark_sutra_mastered", "unmark_sutra_mastered"):
        sid = d.get("sutra_id")
        if sid:
            mastered = set(prog.get("sutras_mastered", []))
            if action == "mark_sutra_mastered":
                mastered.add(sid)
            elif action == "unmark_sutra_mastered":
                mastered.discard(sid)
            else:
                if sid in mastered:
                    mastered.remove(sid)
                else:
                    mastered.add(sid)
            prog["sutras_mastered"] = sorted(list(mastered))

    elif action == "update_checklist":
        item_id = d.get("item_id")
        completed = d.get("completed", True)
        if "daily_checklist" not in prog:
            prog["daily_checklist"] = {}
        if today_str not in prog["daily_checklist"]:
            prog["daily_checklist"][today_str] = {}
        prog["daily_checklist"][today_str][item_id] = completed

    elif action == "advance_day":
        day = prog.get("current_day", 1) + 1
        week = prog.get("current_week", 1)
        if day > 7:
            day = 1
            week = min(12, week + 1)
        prog["current_day"] = day
        prog["current_week"] = week
        prog["streak_days"] = prog.get("streak_days", 0) + 1

    elif action == "set_week":
        week = max(1, min(12, int(d.get("week", 1))))
        prog["current_week"] = week

    elif action == "log_flashcards":
        reviewed = d.get("reviewed", 0)
        mastered = d.get("mastered", 0)
        fc = prog.get("flashcard_stats", {"reviewed": 0, "mastered": 0})
        fc["reviewed"] = fc.get("reviewed", 0) + reviewed
        fc["mastered"] = fc.get("mastered", 0) + mastered
        prog["flashcard_stats"] = fc

    elif action == "reset_progress":
        prog["sutras_mastered"] = []
        prog["current_week"] = 1
        prog["current_day"] = 1
        prog["streak_days"] = 1
        prog["sakha_submissions"] = {}
        prog["transformations_mastered"] = []
        prog["error_hunt_completed"] = []
        prog["flashcard_stats"] = {"reviewed": 0, "mastered": 0}
        prog["daily_checklist"] = {}

    prog["last_active_date"] = today_str
    save_panini_progress(prog)
    return prog

@app.post("/api/panini/evaluate-sakha")
def evaluate_panini_sakha(req: PaniniSakhaRequest):
    """Evaluates student's Śākhā sentence using Gemini or pedagogical fallback."""
    sutra = panini_data.get_sutra_by_id(req.sutra_id)
    if not sutra:
        raise HTTPException(status_code=404, detail=f"Sutra '{req.sutra_id}' not found.")
    
    evaluation = evaluate_sakha(sutra, req.user_text)
    
    prog = get_panini_progress()
    sid = req.sutra_id
    if "sakha_submissions" not in prog:
        prog["sakha_submissions"] = {}
    if sid not in prog["sakha_submissions"]:
        prog["sakha_submissions"][sid] = []
    
    submission_record = {
        "text": req.user_text,
        "score": evaluation.get("score", 0),
        "is_correct": evaluation.get("is_correct", False),
        "feedback": evaluation.get("feedback", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    prog["sakha_submissions"][sid].append(submission_record)

    if evaluation.get("score", 0) >= 8 and sid not in prog.get("sutras_mastered", []):
        prog.setdefault("sutras_mastered", []).append(sid)

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prog.setdefault("daily_checklist", {}).setdefault(today_str, {})["sutras"] = True

    save_panini_progress(prog)
    evaluation["sutra_mastered"] = sid in prog.get("sutras_mastered", [])
    return evaluation

@app.post("/api/panini/evaluate-transformation")
def evaluate_panini_transformation(req: PaniniTransformRequest):
    """Checks user's transformation (schlicht ↔ gehoben)."""
    target_item = None
    for t in panini_data.TRANSFORMATIONS:
        if t["id"] == req.id:
            target_item = t
            break
    if not target_item:
        raise HTTPException(status_code=404, detail=f"Transformation '{req.id}' not found.")
    
    is_to_gehoben = req.direction == "schlicht_to_gehoben"
    target_text = target_item["gehoben"] if is_to_gehoben else target_item["schlicht"]
    user_text = req.user_text.strip()
    
    target_words = set(re.findall(r"\w+", target_text.lower()))
    user_words = set(re.findall(r"\w+", user_text.lower()))
    
    overlap = len(target_words.intersection(user_words))
    total_target = max(1, len(target_words))
    ratio = overlap / total_target
    
    score = min(10, max(2, int(ratio * 10 + 2)))
    passed = score >= 6
    
    prog = get_panini_progress()
    if passed and req.id not in prog.get("transformations_mastered", []):
        prog.setdefault("transformations_mastered", []).append(req.id)
        save_panini_progress(prog)

    feedback = "Hervorragende Transformation! Das Zielregister wurde präzise getroffen." if score >= 8 else (
        "Guter Versuch! Vergleichen Sie Ihre Formulierung mit dem offiziellen Mustersatz." if passed else
        "Noch nicht ganz stimmig. Achten Sie auf die charakteristischen Merkmale des Zielstils (Nominal- vs. Verbalstil)."
    )

    return {
        "id": req.id,
        "score": score,
        "max_score": 10,
        "passed": passed,
        "feedback": feedback,
        "target_model": target_text,
        "explanation": target_item.get("explanation", ""),
        "relevant_sutras": target_item.get("sutras", []),
    }

@app.post("/api/panini/evaluate-error-hunt")
def evaluate_panini_error_hunt(req: PaniniErrorHuntRequest):
    """Checks user's error hunt correction and sutra identification."""
    target_item = None
    req_id_str = str(req.id).lower()
    for item in panini_data.ERROR_HUNT:
        iid = str(item.get("id", "")).lower()
        num_str = str(item.get("number", ""))
        if iid == req_id_str or num_str == req_id_str or req_id_str == f"eh_{num_str}" or req_id_str.endswith(num_str):
            target_item = item
            break
    if not target_item:
        raise HTTPException(status_code=404, detail=f"Error hunt item '{req.id}' not found.")

    correct_model = target_item.get("correct") or target_item.get("sentence", "")
    user_corr = req.user_correction.strip()
    expected_sutra_num = target_item.get("sutra_number")
    
    sutra_correct = False
    if req.sutra_identified:
        try:
            s_num = int(re.search(r"\d+", str(req.sutra_identified)).group(0))
            sutra_correct = (s_num == expected_sutra_num)
        except Exception:
            pass

    corr_words = set(re.findall(r"\w+", correct_model.lower()))
    user_words = set(re.findall(r"\w+", user_corr.lower()))
    overlap = len(corr_words.intersection(user_words))
    ratio = overlap / max(1, len(corr_words))
    
    score = int(ratio * 7 + (3 if sutra_correct else 1))
    passed = score >= 6
    
    prog = get_panini_progress()
    if passed and req.id not in prog.get("error_hunt_completed", []):
        prog.setdefault("error_hunt_completed", []).append(req.id)
        save_panini_progress(prog)

    return {
        "id": req.id,
        "score": score,
        "max_score": 10,
        "passed": passed,
        "sutra_identified_correctly": sutra_correct,
        "expected_sutra_number": expected_sutra_num,
        "official_correction": correct_model,
        "explanation": target_item.get("explanation", ""),
    }


# Mount content directory (for audio files)
if CONTENT_DIR.exists():
    app.mount("/content", StaticFiles(directory=str(CONTENT_DIR)), name="content")

# Mount static frontend
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Goethe B2 Exam Simulator API. Frontend index.html not yet installed."}
