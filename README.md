# Chess Speak Out Loud — AI Chess Coach Trainer

> *"Never show Alex what to play without first teaching him what to look for and why it matters."*

A chess training tool that renders LC0's neural-network "thinking" as direct visual overlays — **policy arrows** (where the net feels energy/initiative) and an **attention saliency heatmap** (what the transformer is actually looking at) — instead of cryptic evaluation numbers.

## Running the app

👉 **See [`HOW_TO_RUN.md`](HOW_TO_RUN.md) — it is the authoritative, verified runbook.**

In short: two processes must both be running.

1. **Backend** (from the project root) — FastAPI + LC0, on `http://127.0.0.1:8000`:
   ```powershell
   C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn backend.app:app --reload
   ```
   Must use the `cszero` conda env (Python 3.11) — it has `torch` / `lczerolens`. `backend/requirements.txt` is empty; deps live in the conda env.
2. **Frontend** (from `frontend/`) — Vite / React, on `http://localhost:5173`:
   ```powershell
   cd frontend && npm run dev
   ```
3. Open **http://localhost:5173**.

> If LC0 fails to start, `/api/health` reports `engine_mode: "mock"` and the app serves pre-analyzed positions. See the troubleshooting section in `HOW_TO_RUN.md`.

## Neural nets (in `engine/`)

Two nets power the two visual signals (kept split for speed/stability):

- `791556.pb.gz` — fast SE-ResNet → **policy arrows** via LC0 `VerboseMoveStats`.
- `bt3.onnx` — BT3 transformer → **attention saliency** via `lczerolens` (hooks `module.encoder{0..14}/mha/QK/softmax`). A healthy analysis reports `saliency_source: "attention"`.

## Project Structure

```
chess_speak_out_loud/
├── backend/                # FastAPI orchestrator (run via cszero conda env)
│   ├── app.py              # FastAPI server & API endpoints (/api/analyze, /api/health, ...)
│   ├── engine_manager.py   # LC0/UCI wrapper — eval, best moves, policy priors
│   ├── neural_vision.py    # BT3 transformer attention saliency via lczerolens
│   ├── heatmap.py          # Square-by-square heatmap generation
│   ├── concept_mapper.py   # Engine output → positional observations
│   ├── llm_client.py       # Gemini wrapper — DORMANT (LLM_ENABLED = False)
│   ├── mock_data.py        # Mock analysis fallback when LC0 is absent
│   └── requirements.txt    # (empty — see conda env cszero)
├── frontend/               # Vite + React app (chessground board, PGN viewer)
│   ├── index.html          # Vite entry (loads src/main.tsx)
│   ├── src/                # App.tsx, main.tsx, components/ (PgnViewer.tsx)
│   └── package.json        # dev = vite, on port 5173
├── engine/                 # lc0.exe + 791556.pb.gz + bt3.onnx + stockfish/
├── HOW_TO_RUN.md           # Authoritative runbook
├── ARCHITECTURE.md         # Data flow & component boundaries
└── README.md               # This file
```

## Architecture

```
┌─────────────────────────────────────────────┐
│                  Frontend                    │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │Chessboard│  │ Heatmap  │  │  Verbal   │ │
│  │  + FEN   │  │  Canvas  │  │  Coach    │ │
│  └──────────┘  └──────────┘  └───────────┘ │
└────────────────────┬────────────────────────┘
                     │ REST API
┌────────────────────┴────────────────────────┐
│                  Backend                     │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │  LC0     │  │ Heatmap  │  │ Concept   │ │
│  │ Engine   │  │Generator │  │  Mapper   │ │
│  └──────────┘  └──────────┘  └───────────┘ │
└──────────────────────────────────────────────┘
```

## Hardware Recommendations

| Setup | LC0 Build | Network Size | Performance |
|-------|-----------|-------------|-------------|
| CPU only | `cpu-dnnl` or `cpu-openblas` | Small/Medium | ~1K nodes/sec |
| NVIDIA GPU (mid) | `cuda11` or `cuda12` | Medium/Large (T1) | ~10-50K nodes/sec |
| NVIDIA GPU (high) | `cuda12` + `cudnn` | Very Large (BT4) | ~100K+ nodes/sec |

## Future Roadmap

- [ ] **Theme Detector** — Pawn structure recognition + tactical precondition scanning
- [ ] **Template Game Library** — Curated model games per opening variation
- [ ] **Spaced Repetition Trainer** — Anki-style drilling on concepts, not just moves
- [ ] **Structure-Tactic Map** — Predict tactical motifs from pawn formations
- [ ] **Socratic Mode** — Ask questions before revealing answers

## License

MIT
