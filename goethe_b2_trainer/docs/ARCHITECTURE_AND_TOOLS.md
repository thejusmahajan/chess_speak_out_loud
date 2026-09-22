# Technical Architecture & Tool Reference: Goethe B2 Exam Simulator

## 1. System Architecture

```mermaid
graph TD
    Client["Browser UI (HTML5 / Vanilla JS / CSS3)"]
    AudioRec["HTML5 MediaRecorder (audio/webm;codecs=opus)"]
    Waveform["Web Audio API Analyser & Canvas Visualizer"]
    TTS["Web Speech API (de-DE) / Edge-TTS"]
    
    Client --> AudioRec
    Client --> Waveform
    Client --> TTS

    FastAPI["FastAPI Backend (Port 8020)"]
    AudioRec -->|Base64 JSON / Multipart| FastAPI
    
    State["Persistent State (/state)"]
    FastAPI -->|Write Audio| State
    FastAPI -->|Write Scorecard JSON| State
    
    Gemini["Google Gemini Multimodal API"]
    Agent["Antigravity Agent (IDE)"]
    
    FastAPI -.->|Automated Mode (AIzaSy Key)| Gemini
    State -.->|Agent-Assisted Mode| Agent
    Agent -->|POST /api/exam/update-eval| FastAPI
```

---

## 2. Tools Breakdown & Operation

### A. Frontend Audio Pipeline
- **API**: `navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } })`
- **Recording Engine**: `MediaRecorder` collecting 250ms audio slices into an `audio/webm;codecs=opus` Blob.
- **Visualizer Engine**: `AudioContext` connected to an `AnalyserNode` (`fftSize = 256`). A 60 FPS `requestAnimationFrame` loop calculates byte frequency data and draws cyan-to-blue linear gradients on a `<canvas>` element.
- **State Machine**: Managed by `GoetheExamEngine` (`exam_engine.js`) tracking module progression, time remaining, answers, and audio data.

### B. Spoken Audio Evaluation Engine
- **Engine**: Google Gemini Multimodal Audio (`gemini-1.5-flash` / `gemini-2.0-flash`).
- **Direct Multimodal Ingestion**: Raw WebM bytes are passed without Speech-to-Text conversion:
  ```python
  audio_part = {
      "mime_type": "audio/webm",
      "data": audio_bytes
  }
  response = model.generate_content([system_rubric, audio_part])
  ```
- **Evaluation Dimensions (0-6 pts each, Total 30 pts, Pass Mark: 18 pts)**:
  1. *Aufgabenerfüllung*: Coverage of all prompt Leitpunkte (Einleitung, eigene Erfahrung, Heimatland, Vor-/Nachteile, Fazit).
  2. *Kohärenz & Flüssigkeit*: Natural pacing, hesitation frequency, logical transitions.
  3. *Ausdruck & Wortschatz*: Range of B2 vocabulary, idiomatic idioms, connectors (*infolgedessen, darüber hinaus*).
  4. *Grammatische Korrektheit*: Sentence structure (Verb-second in main clauses vs. Verb-end in subordinate clauses like *weil/dass/obwohl*), cases (*Dativ/Akkusativ/Genitiv*).
  5. *Aussprache & Intonation*: Phonemic accuracy (German *ch-Laut*, *Umlaute ä/ö/ü*, *st/sp*), sentence cadence, and word stress.

### C. Written Essay Evaluation Engine
- **Target**: B2 Diskussionsbeitrag (~150 words).
- **Evaluation Dimensions (0-25 pts each, Total 100 pts, Pass Mark: 60 pts)**:
  1. *Aufgabenerfüllung*: Response to all 4 Leitpunkte.
  2. *Kohärenz*: Paragraph transitions, discourse connectors.
  3. *Wortschatz*: Precision, academic/workplace expressions, avoidance of lower-level repetitions.
  4. *Korrektheit*: Orthography, comma rules, grammatical concordance, adjective endings.

### D. Listening Speech Synthesis Engine
- **In-Browser Web Speech API**: Uses local German voices (e.g. `Microsoft Katja (Natural)` or `Google Deutsch`) at rate `0.95`.
- **Microsoft Edge Neural TTS (`generate_neural_audio.py`)**: Uses `edge-tts` to generate multi-character broadcast dialogue with zero latency and studio audio fidelity.

---

## 3. Lifted Spaced Repetition Ladders (from LC0 Knowledge Engine)

The following JSON ladders are housed in `content/ladders/`:
- **`de-konnektoren.json`**:
  - Focuses on 2-part connectors (*zwar... aber, entweder... oder, weder... noch, nicht nur... sondern auch*).
  - Adverbial connectors (*folglich, demnach, infolgedessen, trotzdem*).
  - Subordinating conjunctions (*obwohl, da, sodass, während, indem*).
- **`de-grammatik.json`**:
  - Passive voice alternatives (*sich lassen + Infinitiv, sein + zu + Infinitiv, -bar/-lich Adjektive*).
  - Subjunctive II (*Konjunktiv II der Gegenwart und Vergangenheit*).
  - Prepositional verbs (*warten auf + Akk, abhängen von + Dat*).
- **`de-wortschatz.json`**:
  - High-frequency B2 vocabulary for academic, scientific, and corporate domains.

---

## 4. API Endpoints Reference

| Method | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/api/exam/config` | Returns examination duration rules, point scales, and module metadata. |
| `GET` | `/api/exam/module/{id}` | Fetches module-specific tasks, texts, audio URLs, and question choices. |
| `POST` | `/api/exam/evaluate-writing` | Grades written essays via Gemini. |
| `POST` | `/api/exam/evaluate-speaking` | Grades voice recordings via Gemini multimodal audio. |
| `POST` | `/api/exam/submit-complete` | Consolidates all 4 modules, grades answers, computes pass/fail status, and persists submission to `state/submissions/`. |
| `GET` | `/api/exam/latest-result` | Fetches the most recent evaluated scorecard for instant dashboard display. |
| `POST` | `/api/exam/update-eval` | Allows the Antigravity agent or external process to inject rubric scores and recalculate exam results. |
