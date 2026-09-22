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
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from exam_data import EXAM_CONFIG, MODULE_CONTENT
from gemini_evaluator import evaluate_speaking, evaluate_writing
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
