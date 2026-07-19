# Workspace Rules: Chess Speak Out Loud

## Project Overview
This project is an AI-powered chess coach that bridges deep neural network evaluations (LC0) with conversational LLMs (Gemini).

## Architecture
- **Backend**: Python-based API.
  - `backend/app.py`: Main entrypoint.
  - `backend/engine_manager.py`: Manages the Leela Chess Zero (LC0) binary.
  - `backend/tactics.py`: Uses the official `lichess_tagger` logic to perfectly classify tactical motifs from forced PVs.
  - `backend/llm_client.py`: Integrates with Google Generative AI (`gemini-flash` models) to produce multi-persona educational commentary.
- **Frontend**: React-based UI (likely Vite).
- **Docs**: Documentation and theoretical brainstorms are kept in the `docs/` folder.
- **Scratch**: Experimental scripts (like engine diagnostics and puzzle streaming tests) are stored in `scratch/`.

## Agent Guidelines
- When modifying the LLM client, be aware of strict rate limits on the Free Tier for Gemini API keys (max 15-20 requests/min).
- The tactical coach relies on `lichess_tagger`. Do NOT attempt to rewrite the tactical heuristics in pure Python; the Lichess module handles the 50+ motifs perfectly.
- Ensure all Python dependencies are added to `requirements.txt` (e.g., `python-chess`, `google-generativeai`, `python-dotenv`).

## Branching Strategy
- **Windows Development**: All development specific to Windows (or diverging from Debian) should happen on the `windows-dev` branch. Ensure that agents are aware of this distinction to avoid conflicting with the parallel Debian setup.
