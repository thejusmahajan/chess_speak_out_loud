# Workspace Rules: Goethe-Zertifikat B2 Exam Simulator & AI Coach

> **Status:** ⚠️ WORK IN PROGRESS / UNDER CONSTRUCTION (v1.0.0-alpha)

## Project Overview
This project is an AI-powered Goethe-Zertifikat B2 exam simulator and language coach. It combines:
1. **Full B2 Exam Simulator**: Exact time constraints, interactive question modules (Lesen, Hören, Schreiben, Sprechen), audio playback, live microphone recording, and scorecard generation.
2. **Gemini Multimodal AI Evaluator**: Native audio and text analysis applying the official Goethe-Institut B2 rubrics (Aussprache, Flüssigkeit, Wortschatz, Grammatik, Aufgabenerfüllung).
3. **B2 Knowledge Drills & Spaced Repetition**: Leitner/SM-2 flashcard ladders lifted from the knowledge trainer architecture for mastering B2 Konnektoren, Grammatik, and Wortschatz.

## Architecture
- **Backend**: FastAPI web server (`app.py`) running on port `8020`.
  - `gemini_evaluator.py`: Ingests raw voice recordings (`audio/webm`) and essay texts for rubric evaluation.
  - `exam_data.py`: Authored B2 tasks, texts, audio links, and questions for the 4 exam modules.
  - `content/`: Audio files and B2 study ladders (`de-konnektoren.json`, `de-grammatik.json`, `de-wortschatz.json`).
  - `state/`: Persistent storage for submissions, scorecards, and audio recordings (`audio_latest.webm`).
- **Frontend**: Single-Page Application (`static/`):
  - `index.html`: Clean, accessible interface with Goethe Institute exam aesthetics.
  - `css/style.css`: Dark/light mode, split pane layout, responsive typography, timers, waveform styling.
  - `js/audio_recorder.js`: HTML5 `MediaRecorder` + Web Audio API Canvas visualizer.
  - `js/exam_engine.js`: State machine, module step navigation, dual timer modes (Sprint vs. Official), scorecards.
- **Audio Synthesis**: `generate_neural_audio.py` (Microsoft Edge Neural TTS) & browser Web Speech API.

## Evaluation Modes
1. **Agent-Assisted Mode (Antigravity Direct)**:
   - Does not require an external API key.
   - When the candidate submits in the browser, the audio is stored in `state/audio_latest.webm`.
   - The user requests evaluation in chat ("Evaluate my exam"), and the Antigravity agent inspects the audio and writes results to `state/submissions/` and `/api/exam/update-eval`.
2. **Automated API Mode**:
   - Uses a free `GEMINI_API_KEY` (from Google AI Studio: `https://aistudio.google.com/app/apikey`) placed in `.env`.
   - Directly calls Gemini from the backend on submit.

## Agent Guidelines & Persona
- Act as an encouraging, pedagogical, and rigorous Goethe-Institut B2 Certified Examiner.
- When correcting spoken or written German, always provide:
  1. The exact mistake quoted.
  2. The correct German phrasing.
  3. The underlying grammatical rule (e.g. *Verbletztstellung nach Kausal- und Konzessivkonnektoren*, *Akkusativ/Dativ-Präpositionen*, *Adjektivdeklination*).
  4. 2-3 high-yield B2 *Redemittel* suitable for the topic.
- Preserve file integrity and keep the simulator lightweight and fast.
