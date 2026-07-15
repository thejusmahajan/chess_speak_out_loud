# Architecture: Chess Speak Out Loud

This document provides a high-level overview of the data flow and system boundaries.

## System Diagram

```mermaid
graph TD
    UI[React Frontend] -->|REST API| API[FastAPI Backend]
    
    API -->|Evaluate FEN| LC0[Leela Chess Zero Binary]
    LC0 -->|Principal Variation| API
    
    API -->|PV + FEN| Tagger[Lichess Python Tagger]
    Tagger -->|Tactical Motifs| API
    
    API -->|Motifs + PV + Prompts| Gemini[Google Gemini API]
    Gemini -->|Commentary (4 Personas)| API
    
    API -->|JSON Response| UI
```

## Component Boundaries

1. **Frontend (`frontend/`)**: Pure UI. Should not contain chess logic. Strictly consumes `/api/*` endpoints.
2. **Backend (`backend/`)**: FastAPI orchestrator.
   - **`engine_manager.py`**: The *only* file that interacts with the `lc0.exe` subprocess.
   - **`tactics.py`**: The *only* file that bridges data into `lichess_tagger/cook.py`.
   - **`llm_client.py`**: The *only* file that talks to `google.generativeai`.

## Data Flow for Tactical Analysis
1. User requests analysis of a PGN.
2. FastAPI asks LC0 for the forced line (PV).
3. FastAPI sends the PV to the `lichess_tagger`.
4. `lichess_tagger` returns guaranteed accurate motifs (e.g., `["fork", "skewer"]`).
5. FastAPI constructs a prompt containing the FEN, the PV, and the Motifs.
6. Gemini generates conversational commentary discussing *why* the fork happens.
