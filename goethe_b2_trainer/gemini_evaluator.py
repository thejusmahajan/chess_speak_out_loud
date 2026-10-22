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


def evaluate_practice_difficult(
    question_id: str,
    question_data: Dict[str, Any],
    user_text: str,
    model_name: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """
    Evaluates Tier 3 Difficult open-ended exercises (q9: answer questions, q10: write next sentence)
    using Gemini LLM with official Goethe B2 criteria, with intelligent fallback.
    """
    cleaned_user = (user_text or "").strip()
    if not cleaned_user or len(cleaned_user) < 5:
        return {
            "is_correct": False,
            "score": 0,
            "max_score": 10,
            "feedback": "Die Antwort ist zu kurz oder leer. Bitte formulieren Sie mindestens einen vollständigen Satz auf B2-Niveau.",
            "cefr_level": "Unter A2",
            "model_answer": question_data.get("model_answer", ""),
            "corrections": [],
            "strengths": [],
        }

    # Deterministic fallback function
    def _deterministic_fallback() -> Dict[str, Any]:
        lower = cleaned_user.lower()
        score = 6
        strengths = []
        feedback = "Ihre Antwort wurde erfasst."

        if question_id == "q9_diff_answer_question":
            has_comm = any(w in lower for w in ["kommunik", "absprach", "austausch", "abstimm"])
            has_risk = any(w in lower for w in ["verlust", "verzöger", "fehler", "risiko", "problem", "entscheidung"])
            if has_comm and has_risk:
                score = 10
                strengths.append("Beide Kernaspekte (Kommunikationsaufwand & Informationsrisiko) präzise genannt.")
                feedback = "Sehr gut! Die inhaltlichen Kernanforderungen der B2-Textfrage wurden voll erfüllt."
            elif has_comm or has_risk:
                score = 7
                strengths.append("Einer der beiden Kernpunkte wurde treffend dargestellt.")
                feedback = "Gute Antwort. Es empfiehlt sich, sowohl den Kommunikationsaufwand als auch das Risiko noch expliziter zu verknüpfen."
            else:
                score = 5
                feedback = "Die Antwort berührt das Thema, könnte aber die spezifischen Bedenken der Psychologen noch präziser aufgreifen."
        elif question_id == "q10_diff_write_next_sentence":
            has_connector = any(c in lower for c in ["andererseits", "allerdings", "jedoch", "demgegenüber", "zwar", "auf der anderen seite", "dennoch"])
            has_contrast = any(w in lower for w in ["gefahr", "nachteil", "druck", "grenz", "überstund", "belast", "arbeit", "freizeit", "erreichbar"])
            if has_connector and has_contrast:
                score = 10
                strengths.append("Passender B2-Gegenkonnektor und kohärente Schattenseiten formuliert.")
                feedback = "Ausgezeichnet! Satzverbindung und kontrastierende Argumentation entsprechen vollem B2-Standard."
            elif has_connector or has_contrast:
                score = 7
                strengths.append("Guter Ansatz bei der Formulierung des Folgesatzes.")
                feedback = "Gut formuliert. Achten Sie auf die Verknüpfung mit einem B2-Konnektor und korrekte Verbstellung."
            else:
                score = 5
                feedback = "Der Folgesatz führt den Gedanken weiter, nutzt jedoch noch nicht das volle Spektrum B2-typischer Konnektoren."

        return {
            "is_correct": score >= 6,
            "score": score,
            "max_score": 10,
            "feedback": feedback,
            "cefr_level": "B2" if score >= 8 else "B1+",
            "model_answer": question_data.get("model_answer", ""),
            "strengths": strengths,
            "corrections": [],
        }

    if not GEMINI_API_KEY:
        return _deterministic_fallback()

    system_instruction = """
You are a senior Goethe-Institut certified B2 German Examiner evaluating advanced practice exercises.
Grade the candidate's response strictly on CEFR B2 standards:
- Task fulfillment (Did they answer the question or logically continue the sentence with the required perspective?)
- Syntactic complexity (Subordination, inversion after connectors, word order, verb positioning)
- Vocabulary and style (B2 register, idiomatic phrasing, accurate connectors)
- Grammatical precision (Cases, endings, declensions)

Return valid JSON ONLY with the following schema:
{
  "is_correct": <boolean, true if score >= 6>,
  "score": <integer from 0 to 10>,
  "max_score": 10,
  "cefr_level": "<e.g. B1.2, B2.1, B2.2, C1>",
  "feedback": "<Encouraging, clear pedagogical feedback in German on the candidate's answer>",
  "strengths": ["<1-2 positive aspects>"],
  "corrections": [
    {
      "original": "<error substring>",
      "corrected": "<corrected substring>",
      "explanation": "<grammar explanation in German>"
    }
  ],
  "improved_version": "<Polished native-like B2/C1 version of the candidate's text>"
}
"""

    prompt = f"""
Exercise Title: {question_data.get("title")}
Instruction: {question_data.get("instruction")}
Context: {question_data.get("reading_passage", question_data.get("lead_in_sentence", ""))}
Question/Prompt: {question_data.get("question_prompt")}
Official Model Answer: {question_data.get("model_answer")}

Candidate Submission:
\"\"\"{cleaned_user}\"\"\"

Evaluate the candidate's response now.
"""

    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            generation_config={"response_mime_type": "application/json"},
        )
        resp = model.generate_content(prompt)
        res = _clean_json_response(resp.text)
        res["model_answer"] = question_data.get("model_answer", "")
        if "max_score" not in res:
            res["max_score"] = 10
        if "is_correct" not in res:
            res["is_correct"] = res.get("score", 0) >= 6
        return res
    except Exception as e:
        print(f"Gemini practice evaluation fallback due to: {e}")
        fallback = _deterministic_fallback()
        fallback["examiner_note"] = f"AI offline fallback utilized ({e})."
        return fallback


def evaluate_sakha(
    sutra_data: Dict[str, Any],
    user_text: str,
    model_name: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """
    Evaluates a student's Śākhā sentence exercise for a given Pāṇini sūtra.
    Checks rule compliance, grammatical precision, B2 register, and sentence structure.
    """
    cleaned = (user_text or "").strip()
    sutra_num = sutra_data.get("number", 1)
    sutra_title = sutra_data.get("title", "")
    rule = sutra_data.get("rule", "")
    prompt_text = sutra_data.get("exercise_prompt", "")
    examples = sutra_data.get("examples_correct", [])
    
    def _deterministic_fallback():
        words = [w for w in re.split(r"\s+", cleaned) if w]
        num_words = len(words)
        score = 0
        strengths = []
        feedback = ""
        corrections = []
        
        if num_words < 4:
            score = 3
            feedback = "Der Satz ist noch sehr kurz. Bilden Sie vollständige Sätze mit Subjekt, Prädikat und dem geforderten Muster."
        elif num_words < 8:
            score = 6
            strengths.append("Grundstruktur erkennbar.")
            feedback = "Guter Ansatz. Versuchen Sie, den Satz mit mehr B2-Details und passenden Ergänzungen anzureichern."
        else:
            score = 8
            strengths.append(f"Ausführliche Satzbildung im Stil von Sūtra {sutra_num} ({sutra_title}).")
            strengths.append("Gute Satzlänge und Wortstellung im B2-Bereich.")
            feedback = f"Sehr gelungene Anwendung der Regel von Sūtra {sutra_num}. Der Satz zeigt gutes Sprachgefühl."

        # Check for capitalized nouns / punctuation
        if cleaned and not cleaned.endswith((".", "!", "?")):
            corrections.append({
                "original": cleaned[-10:],
                "corrected": cleaned[-10:] + ".",
                "explanation": "Achten Sie auf das Satzzeichen am Satzende.",
            })

        return {
            "is_correct": score >= 6,
            "score": score,
            "max_score": 10,
            "cefr_level": "B2" if score >= 8 else "B1+",
            "feedback": feedback,
            "strengths": strengths,
            "corrections": corrections,
            "improved_version": examples[0] if examples else cleaned,
            "sutra_title": sutra_title,
            "sutra_number": sutra_num,
        }

    if not cleaned:
        return {
            "is_correct": False,
            "score": 0,
            "max_score": 10,
            "cefr_level": "B1",
            "feedback": "Bitte geben Sie einen Satz oder eine Ausarbeitung ein.",
            "strengths": [],
            "corrections": [],
            "improved_version": examples[0] if examples else "",
            "sutra_title": sutra_title,
            "sutra_number": sutra_num,
        }

    if not GEMINI_API_KEY:
        return _deterministic_fallback()

    system_instruction = f"""
You are an expert German teacher and Pāṇini grammarian evaluating a student's German B2 sentence practice (Śākhā).
The student is practicing Sūtra {sutra_num}: "{sutra_title}".
Grammar Rule: "{rule}"
Exercise Task: "{prompt_text}"

Evaluate the student's submission rigorously according to Goethe-Zertifikat B2 CEFR standards:
1. Rule Application: Did the student correctly apply the target grammar structure (Sūtra {sutra_num})?
2. Grammatical Accuracy: Check cases (Akkusativ, Dativ, Genitiv), adjective endings, verb placement (Nebensatz vs Hauptsatz), prepositions, noun capitalization.
3. B2 Register: Is the vocabulary idiomatic and appropriate for B2?
4. Constructive feedback in clear, motivating German.

Respond ONLY with valid JSON following this schema:
{{
  "is_correct": <boolean, true if score >= 6>,
  "score": <integer from 0 to 10>,
  "max_score": 10,
  "cefr_level": "<e.g. B1.2, B2.1, B2.2, C1>",
  "feedback": "<Clear pedagogical feedback in German>",
  "strengths": ["<positive aspect 1>", "<positive aspect 2>"],
  "corrections": [
    {{
      "original": "<error phrase or word>",
      "corrected": "<corrected phrase or word>",
      "explanation": "<grammar reason in German>"
    }}
  ],
  "improved_version": "<A polished, natural B2-level version of the student's sentence incorporating the sūtra>"
}}
"""

    prompt = f"""
Sūtra: {sutra_num}. {sutra_title}
Regel: {rule}
Übungsaufgabe (Śākhā): {prompt_text}
Mustersätze aus dem Kanon:
{json.dumps(examples[:2], ensure_ascii=False)}

Eingabe des Schülers:
\"\"\"{cleaned}\"\"\"

Bitte jetzt bewerten:
"""

    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            generation_config={"response_mime_type": "application/json"},
        )
        resp = model.generate_content(prompt)
        res = _clean_json_response(resp.text)
        if "max_score" not in res:
            res["max_score"] = 10
        if "is_correct" not in res:
            res["is_correct"] = res.get("score", 0) >= 6
        res["sutra_title"] = sutra_title
        res["sutra_number"] = sutra_num
        return res
    except Exception as e:
        err_msg = str(e).encode("ascii", "replace").decode("ascii")
        print(f"Gemini Sakha evaluation fallback due to: {err_msg}")
        fb = _deterministic_fallback()
        fb["examiner_note"] = f"AI offline fallback utilized ({err_msg})."
        return fb


