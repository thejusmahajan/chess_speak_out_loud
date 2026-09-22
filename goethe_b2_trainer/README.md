# Goethe-Zertifikat B2 Prüfungssimulator & AI Language Coach

> ⚠️ **STATUS: WORK IN PROGRESS / UNDER CONSTRUCTION (Version 1.0.0-alpha)**  
> *This repository is actively being developed as a dedicated, distraction-free environment for Goethe-Zertifikat B2 preparation.*

---

## 📌 Project Overview

The **Goethe-Zertifikat B2 Prüfungssimulator** is an autonomous examination environment and intelligent language trainer designed to prepare candidates for the official Goethe-Zertifikat B2 exam. It provides:

1. **Full-Length Exam Simulation**: Real-world time constraints for all 4 official Goethe exam modules (**Lesen**, **Hören**, **Schreiben**, **Sprechen**).
2. **Multimodal AI Audio Evaluation**: Direct evaluation of spoken German voice recordings using Google Gemini's native audio understanding — assessing pronunciation (*Aussprache*), fluency (*Flüssigkeit*), grammar (*Korrektheit*), B2 vocabulary (*Wortschatz*), and task structure (*Aufgabenerfüllung*).
3. **In-Browser Audio Suite**: High-fidelity microphone capture with real-time waveform visualization, alongside native German speech synthesis for the listening comprehension module.
4. **Official Scorecard & Diagnostics**: Generates a Goethe-Institut certificate summary (Pass mark: ≥ 60% per module), detailed point breakdowns, line-by-line spoken error corrections, and suggested B2 *Redemittel*.
5. **Integrated B2 Study Ladders**: Spaced repetition flashcards lifted from the knowledge trainer architecture for mastering B2 connectors (*Konnektoren*), grammar (*Grammatik*), and vocabulary (*Wortschatz*).

---

## 🛠️ Tools Used & How They Are Used

| Component / Tool | Technology / Engine | How It Is Used in the Trainer |
| :--- | :--- | :--- |
| **Backend API** | **Python 3.10+ & FastAPI** | Serves API routes, orchestrates exam states, persists submissions, and computes weighted scores on port `8020`. |
| **Server Engine** | **Uvicorn (ASGI)** | High-performance asynchronous server running with hot-reloading for local development. |
| **AI Evaluation Engine** | **Google Gemini (Multimodal)** | Directly consumes raw candidate voice recordings (`audio/webm`) without speech-to-text translation, evaluating phonetic clarity, syntax, and CEFR B2 level. |
| **Audio Recording Cockpit** | **HTML5 MediaRecorder API** | Captures candidate microphone audio in Opus-encoded WebM format with zero external browser plugins. |
| **Live Waveform Visualizer** | **Web Audio API & HTML5 Canvas** | Renders real-time frequency oscillations and audio amplitude so candidates can visually verify microphone levels. |
| **Listening Audio Synthesis** | **Web Speech API & `edge-tts`** | Generates authentic, multi-speaker German radio discussions (*de-DE-KillianNeural* & *de-DE-KatjaNeural*) at real examination cadence. |
| **Frontend UI** | **Vanilla HTML5, CSS3, ES6+ JS** | Single-page application (SPA) with a modern dark/light Goethe exam theme, dual countdown timers, and split-pane viewports. |
| **Spaced Repetition (SRS)** | **SM-2 & Leitner Algorithms** | Retains high-yield B2 flashcards (*de-konnektoren*, *de-grammatik*, *de-wortschatz*) lifted from the LC0 trainer. |

---

## 🧠 Knowledge Lifted from Previous Trainers (LC0 & Knowledge Engine)

This project builds directly upon the pedagogical and technical insights gained from developing the LC0 chess coach and spaced-repetition knowledge trainer:

1. **State Persistence Pattern**: Exam answers and voice recordings are isolated under `state/` (`submissions/` and `audio_latest.webm`) using atomic JSON writes, preventing data loss across browser reloads.
2. **Dual Evaluation Architecture**:
   - **Standalone Mode**: Candidates with a free Google AI Studio key (`AIzaSy...`) get instantaneous in-browser grading.
   - **Antigravity Agent Mode**: Candidates can rely entirely on the Antigravity pair-programming agent inside the IDE to inspect audio, evaluate German syntax, and update the dashboard via `POST /api/exam/update-eval`.
3. **Structured B2 Content Ladders**:
   - Imported from `trainer/content/ladders/` into `content/ladders/`:
     - `de-konnektoren.json`: 30+ two-part connectors (*zwar... aber, nicht nur... sondern auch*), adverbial connectors (*folglich, demnach, infolgedessen*), and subjunctions (*obwohl, da, sodass*).
     - `de-grammatik.json`: B2 grammar rules (Passive voice substitutes, subjunctive II, relative clauses with prepositions).
     - `de-wortschatz.json`: Topic-specific B2 academic and workplace lexicon.

---

## 📁 Repository Structure

```
goethe_b2_trainer/
├── .agents/
│   └── AGENTS.md                  # Antigravity workspace rules & examiner persona
├── docs/
│   └── ARCHITECTURE_AND_TOOLS.md  # Deep technical specifications & rubrics
├── content/
│   ├── audio/
│   │   ├── hoeren_sample.mp3      # Synthesized German radio dialogue
│   │   └── hoeren_sample.wav      # Fallback speech audio
│   └── ladders/                   # Lifted B2 study card ladders
│       ├── de-konnektoren.json    # Connectors drill cards
│       ├── de-grammatik.json      # Grammar drill cards
│       └── de-wortschatz.json     # Vocabulary drill cards
├── state/
│   ├── audio_latest.webm          # Most recently recorded candidate speech
│   └── submissions/               # Historical scorecards & evaluated exams (JSON)
├── static/
│   ├── css/
│   │   └── style.css              # Goethe examination styling & responsive layouts
│   └── js/
│       ├── audio_recorder.js      # MediaRecorder & Canvas visualizer
│       └── exam_engine.js         # State machine, timers & scorecard renderer
├── index.html -> static/index.html
├── app.py                         # FastAPI application (Port 8020)
├── exam_data.py                   # 4 Goethe B2 exam modules & authentic tasks
├── gemini_evaluator.py            # Gemini multimodal audio & text grader
├── generate_neural_audio.py       # Multi-speaker German TTS generator
├── requirements.txt               # Pinned Python dependencies
├── launch_b2_trainer.bat          # 1-click startup script (starts uvicorn on 8020)
├── stop_b2_trainer.bat            # Clean shutdown script for port 8020
└── README.md                      # Master documentation (this file)
```

---

## 🚀 How to Launch & Use

### Prerequisites
- Python 3.10 or higher (e.g. `miniconda3` environment `cszero` or virtualenv).
- Chrome, Edge, or Firefox browser with microphone access enabled.

### 1-Click Launch
Double-click:
```cmd
launch_b2_trainer.bat
```
This automatically boots the FastAPI server on port `8020` and opens:
👉 **[http://127.0.0.1:8020/](http://127.0.0.1:8020/)**

### Stopping the Server
Double-click:
```cmd
stop_b2_trainer.bat
```

---

## 🎯 The 4 Exam Modules in v1.0.0-alpha

1. **📖 Modul 1: Lesen (Reading)**:
   - Text: *"Die Viertagewoche: Ein Modell mit Zukunft?"*
   - Comprehension multiple-choice task with instant scoring (30 pts).
2. **🎧 Modul 2: Hören (Listening)**:
   - Topic: *"Digitale Erreichbarkeit im Feierabend"*
   - In-player playback counter (max 2 plays) + Web Speech API synthesis button (30 pts).
3. **✍️ Modul 3: Schreiben (Writing)**:
   - Task: Forum post on *"Plastikfreie Supermärkte"* (Target: ~150 words).
   - Live word counter and 4 required Leitpunkte guidelines (100 pts).
4. **🎙️ Modul 4: Sprechen (Speaking)**:
   - Topic: Short presentation on *"Sollten Universitätsvorlesungen dauerhaft online stattfinden?"*
   - Real-time microphone recorder with audio waveform canvas (30 pts).

---

## 📋 Evaluation Workflow

### Option A: Antigravity Agent-Assisted Evaluation (Default)
1. Complete the exam in your browser and click **"Prüfung abgeben & Auswerten"**.
2. Return to the Antigravity chat window and state:  
   👉 **"Evaluate my exam submission"**
3. Antigravity analyzes `state/audio_latest.webm` and your essay, scores them against the official Goethe rubric, and injects the results into the web app.
4. Click **"📊 Letztes Prüfungsergebnis anzeigen"** in the browser to inspect your graded scorecard!

### Option B: Direct Gemini API Key
1. Obtain a 100% free Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Add it to `.env`:
   ```env
   GEMINI_API_KEY=AIzaSyYourKeyHere
   ```
3. Submitting the exam evaluates speech and writing automatically within 4–6 seconds.

---

## 🗺️ Roadmap & Upcoming Features
- [ ] **Full-Length Mock Exams**: Multiple complete 5-part reading and 4-part listening exams.
- [ ] **Live Spoken Conversation Partner (Teil 2)**: Real-time oral dialogue with Gemini acting as your Goethe exam partner to negotiate and reach an agreement (*Gemeinsam etwas planen*).
- [ ] **Interactive Spaced Repetition Web UI**: Flashcard training interface for `de-konnektoren.json` and `de-grammatik.json`.
- [ ] **Telc B2 Mode**: Optional toggle for Telc *Sprachbausteine* (cloze test grammar).

---
*Created with ❤️ for German B2 fluency and academic excellence.*
