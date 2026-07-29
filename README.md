# Chess Speak Out Loud — AI Chess Coach Trainer

> *"Never show Alex what to play without first teaching him what to look for and why it matters."*

A personalized chess coach for one serious ~2100 player, built to help him move from dry/positional play toward sharp, Tal-style chess. It renders LC0's neural-network "thinking" as visual overlays — **policy arrows** and an **attention saliency heatmap** — and diagnoses his own games for recurring weaknesses.

**The north star (see [`docs/NORTH_STAR_decoding_lc0.md`](docs/NORTH_STAR_decoding_lc0.md) and `LEADER_BIBLE.md` §1):** *decode LC0's own thinking into accurate, position-specific coaching.* LC0 is the coach; an LLM may only ever **translate** its thoughts, never reason about chess (a bad coach is worse than no coach). The core engine of this is the **relational-fact extractor** (`backend/training/relational_facts.py`) — it turns any position + LC0's line into grounded, true piece-relationship facts (pins, passers, backward pawns, outposts, bishop quality, colour complexes, and plan-level maneuvers). The open frontier is **salience** ([`docs/SALIENCE_PROBLEM.md`](docs/SALIENCE_PROBLEM.md)): learning *which* of those facts a grandmaster would actually say, from public-domain master annotations ([`GM_CURRICULUM_PLAN.md`](GM_CURRICULUM_PLAN.md)).

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

## Where the project is now (2026-07-29)

The diagnosis pipeline, training drills (usual-suspects / intuition / sac-drill / sharp-openings, SRS-aware),
and Critical Points are built. The active work is the **north star**:

- ✅ **Relational-fact extractor** (`backend/training/relational_facts.py`) — tactical + positional +
  plan-level facts, all audited for accuracy. Definitions in `docs/POSITIONAL_DEFINITIONS.md`.
- ✅ **LC0-line plan facts** — `critical_points.position_plan_facts()` runs the engine and describes the plan.
- ⏳ **Salience** (`docs/SALIENCE_PROBLEM.md`) — pick the few facts that matter, by learning from
  grandmaster annotations (`GM_CURRICULUM_PLAN.md`; sources in `docs/public_domain_chess_library.md`).
- ⏳ **The translator** — an LLM that renders LC0's facts into coaching prose, constrained to say only what
  the facts support (north-star S1).

> **For an agent taking over this project: read `LEADER_BIBLE.md` in full first** — §1 (the motto), §6
> (current handover state), and the failure catalog. It is the operating system for whoever leads this.

## License

MIT
