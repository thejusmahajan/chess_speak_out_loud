"""
Gemini Evaluator for Goethe-Zertifikat B2 Exam Simulator.
Handles direct multimodal audio analysis for Sprechen (Speaking)
and linguistic/rubric analysis for Schreiben (Writing).
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

import google.generativeai as genai
from dotenv import load_dotenv

# Search for .env in current dir and parent directories
env_paths = [
    Path(__file__).resolve().parent / ".env",
    Path(__file__).resolve().parent.parent / ".env",
]
for p in env_paths:
    if p.exists():
        load_dotenv(p)
        break

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

DEFAULT_MODEL = "gemini-1.5-flash"


def _clean_json_response(text: str) -> Dict[str, Any]:
    """Extract and parse JSON from LLM response, even if surrounded by markdown fences."""
    text = text.strip()
    # Strip markdown code blocks if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except Exception as e:
        # Fallback if json is slightly malformed
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start : end + 1])
            except Exception:
                pass
        return {
            "error": "Failed to parse JSON response from Gemini",
            "raw_text": text,
        }


def evaluate_speaking(
    audio_bytes: bytes,
    mime_type: str = "audio/webm",
    task_prompt: str = "",
    model_name: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """
    Directly evaluates spoken German audio using Gemini multimodal capabilities.
    Assesses pronunciation, grammar, vocabulary, fluency, and task fulfillment.
    """
    if not GEMINI_API_KEY:
        return {
            "passed": False,
            "total_score": 0,
            "max_score": 30,
            "percentage": 0,
            "transcript": "Error: GEMINI_API_KEY is not configured.",
            "feedback": "Please add GEMINI_API_KEY in .env file to enable AI evaluation.",
            "scores": {
                "aufgabenerfuellung": 0,
                "koherenz_fluessigkeit": 0,
                "wortschatz_ausdruck": 0,
                "korrektheit_grammatik": 0,
                "aussprache_intonation": 0,
            },
            "corrections": [],
        }

    system_instruction = """
You are an expert, official Goethe-Institut B2 Certified Examiner evaluating the 'Sprechen' (Speaking) module.
You are evaluating a candidate's spoken German audio for 'Teil 1: Ein Thema präsentieren' (Vortrag).

OFFICIAL GOETHE B2 EVALUATION CRITERIA:
1. Erfüllung der Aufgabenstellung (0-6 points):
   - Did the candidate cover: Introduction, personal experience, situation in home country, pros & cons, own opinion/conclusion?
2. Kohärenz und Flüssigkeit (0-6 points):
   - Speaking rate, natural pauses, logical flow, discourse markers, connectors (z.B. außerdem, einerseits... andererseits, folglich).
3. Ausdruck und Wortschatz (0-6 points):
   - Richness and appropriateness of B2 vocabulary, idiomatic expressions, Redemittel.
4. Korrektheit / Grammatik (0-6 points):
   - Sentence structure, verb placement (Hauptsatz vs. Nebensatz mit weil/dass/obwohl), noun-verb connections, case declensions (Dativ/Akkusativ/Genitiv), adjective endings.
5. Aussprache und Intonation (0-6 points):
   - Clarity, intelligibility, German phonemes (ch-Laut, Umlaute ä/ö/ü, r-Laut), sentence melody, and word stress.

Total possible points: 30.
Passing threshold: 18 points (60%).

OUTPUT REQUIREMENTS:
You MUST respond with valid JSON ONLY (no commentary outside the JSON).
JSON structure:
{
  "transcript": "<Exact transcription in German of what the candidate actually said in the audio>",
  "scores": {
    "aufgabenerfuellung": <int 0-6>,
    "koherenz_fluessigkeit": <int 0-6>,
    "wortschatz_ausdruck": <int 0-6>,
    "korrektheit_grammatik": <int 0-6>,
    "aussprache_intonation": <int 0-6>
  },
  "total_score": <int sum of scores 0-30>,
  "max_score": 30,
  "percentage": <float 0-100>,
  "passed": <true/false depending if total_score >= 18>,
  "cefr_level_estimate": "<e.g. B1.2, B2.1, B2.2, C1.1>",
  "strengths": [
    "<Highlight 1-2 things done well in German>"
  ],
  "corrections": [
    {
      "spoken": "<Exact quote of spoken mistake>",
      "corrected": "<Correct German formulation>",
      "explanation": "<Linguistic explanation in English/German: why it was incorrect and what rule applies>"
    }
  ],
  "recommended_redemittel": [
    "<3-4 high-yield B2 Redemittel / phrases the candidate could have used for this specific topic>"
  ],
  "examiner_summary": "<2-3 sentences concise encouraging examiner summary in German/English>"
}
"""

    user_prompt = f"""
Task Topic / Instructions:
{task_prompt}

Please listen to the attached spoken audio recording of the candidate and perform the Goethe-Zertifikat B2 evaluation now.
"""

    audio_part = {
        "mime_type": mime_type,
        "data": audio_bytes,
    }

    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            generation_config={"response_mime_type": "application/json"},
        )
        response = model.generate_content([user_prompt, audio_part])
        parsed = _clean_json_response(response.text)
        return parsed
    except Exception as e:
        # If model fails or rate limited, return error dict
        return {
            "error": str(e),
            "passed": False,
            "total_score": 0,
            "max_score": 30,
            "percentage": 0,
            "transcript": f"[Audio evaluation failed: {e}]",
            "scores": {
                "aufgabenerfuellung": 0,
                "koherenz_fluessigkeit": 0,
                "wortschatz_ausdruck": 0,
                "korrektheit_grammatik": 0,
                "aussprache_intonation": 0,
            },
            "corrections": [],
            "examiner_summary": f"Evaluation could not complete: {e}",
        }


def evaluate_writing(
    essay_text: str,
    task_prompt: str = "",
    model_name: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """
    Evaluates written German text for Goethe B2 Schreiben Teil 1 (Diskussionsbeitrag).
    Assesses task fulfillment, coherence, vocabulary, and grammar.
    """
    if not GEMINI_API_KEY:
        return {
            "passed": False,
            "total_score": 0,
            "max_score": 100,
            "percentage": 0,
            "feedback": "Please add GEMINI_API_KEY in .env file to enable AI evaluation.",
            "scores": {
                "aufgabenerfuellung": 0,
                "koharenz": 0,
                "wortschatz": 0,
                "korrektheit": 0,
            },
            "corrections": [],
        }

    word_count = len(essay_text.strip().split())

    system_instruction = """
You are an expert Goethe-Institut B2 Examiner evaluating 'Schreiben Teil 1' (Diskussionsbeitrag / Forumsbeitrag).
Target length: approximately 150 words.

OFFICIAL GOETHE B2 WRITING CRITERIA:
1. Erfüllung der Aufgabenstellung (0-25 points):
   - Were all required Leitpunkte (points/bullet points) addressed with sufficient depth and detail?
2. Kohärenz (0-25 points):
   - Clear paragraph structure, logical progression of thoughts, appropriate connectors (z.B. darüber hinaus, folglich, im Gegensatz dazu, zusammenfassend).
3. Wortschatz (0-25 points):
   - B2 level range, variety, topic-specific terminology, idiomatic expressions, avoiding basic A2/B1 repetitions.
4. Korrektheit (0-25 points):
   - Grammatical accuracy (Verb conjugation, Verbstellung in Haupt- und Nebensätzen, Kasus, Adjektivendungen, Präpositionen) and orthography (Rechtschreibung, Kommasetzung).

Total points: 100 points.
Pass mark: 60 points (60%).

OUTPUT REQUIREMENTS:
Respond with valid JSON ONLY (no commentary outside the JSON).
JSON structure:
{
  "word_count": <int>,
  "word_count_verdict": "<e.g. Perfekt (140-170 Wörter), Etwas zu kurz, or Zu lang>",
  "scores": {
    "aufgabenerfuellung": <int 0-25>,
    "koharenz": <int 0-25>,
    "wortschatz": <int 0-25>,
    "korrektheit": <int 0-25>
  },
  "total_score": <int sum 0-100>,
  "max_score": 100,
  "percentage": <float 0-100>,
  "passed": <true/false depending if total_score >= 60>,
  "cefr_level_estimate": "<e.g. B1.2, B2.1, B2.2, C1.1>",
  "strengths": [
    "<1-2 strong aspects in the text>"
  ],
  "corrections": [
    {
      "original": "<Original excerpt containing error>",
      "corrected": "<Corrected version>",
      "explanation": "<Why this was wrong and the grammar rule (e.g. Verbletztstellung nach 'weil')>"
    }
  ],
  "improved_sample": "<An exemplary rewrite of the candidate's text polished to a stellar B2/C1 standard, preserving their original ideas>",
  "examiner_feedback": "<Concise paragraph of personalized feedback>"
}
"""

    user_prompt = f"""
Task Topic & Leitpunkte:
{task_prompt}

Candidate's Written Text ({word_count} words):
\"\"\"
{essay_text}
\"\"\"

Please evaluate this text according to the Goethe B2 criteria now.
"""

    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            generation_config={"response_mime_type": "application/json"},
        )
        response = model.generate_content(user_prompt)
        parsed = _clean_json_response(response.text)
        parsed["word_count"] = word_count
        return parsed
    except Exception as e:
        return {
            "error": str(e),
            "passed": False,
            "total_score": 0,
            "max_score": 100,
            "percentage": 0,
            "word_count": word_count,
            "scores": {
                "aufgabenerfuellung": 0,
                "koharenz": 0,
                "wortschatz": 0,
                "korrektheit": 0,
            },
            "corrections": [],
            "examiner_feedback": f"Evaluation failed: {e}",
        }
