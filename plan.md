# ARCHITECTURE PLAN: TRI-WORKSPACE DECOUPLING

**Goal:** Decouple the monolithic setup into three independent, focused Antigravity workspaces to maximize velocity toward getting hired, eliminate AI context dilution/token burn, and isolate runtime environments.

**Status:** DRAFT / PENDING REVIEW — DO NOT IMPLEMENT YET.

---

## 1. Executive Rationale & The Three Workspaces

Currently, `chess_speak_out_loud` acts as a composite holding chess engine research, a 24/7 daily timetable daemon, a Goethe B2 German simulator, and links to job search materials. This results in heavy token consumption (loading unrelated rules and ladders on every query), environment collisions, and Git branch friction.

We will partition the ecosystem into **three standalone workspaces**, while treating auxiliary repositories as decoupled evidence vaults:

```
C:\Users\Admin\Documents\
├── bioinformatics_project\job_search\     [WORKSPACE 1: Job Search War Room]
│   ├── applications/                      (Hereon AEON-UP, FZ Jülich, etc.)
│   ├── study_room/                        (06_do_not_claim.md, interview Q&A)
│   ├── .agents/AGENTS.md                  (Application rules, interview doctrine)
│   └── PORTFOLIO_RECEIPTS.md              (Cheat sheet of verified technical facts)
│
├── trainers\                              [WORKSPACE 2: Daily Harness & Drills]
│   ├── trainer\                           (SRS engine, timetable daemon, 14 ladders)
│   ├── goethe_b2_trainer\                 (Goethe B2 Exam Simulator)
│   ├── launch_*.bat / stop_*.bat          (Batch launchers & alarms)
│   └── .agents/AGENTS.md                  (SRS schema, German B2 orthography)
│
├── chess_speak_out_loud\                  [WORKSPACE 3: Engine & Research]
│   ├── backend\                           (LC0 orchestration, neural vision, hooks)
│   ├── frontend\                          (Interactive React analysis board)
│   └── .agents/AGENTS.md                  (LC0 management, engine rules)
│
├── cnp_synthetic\                         [Evidence Vault: Finished CNP PyTorch runs]
└── jax-water-column-port\                 [Evidence Vault / Dev: In-progress JAX port]
```

---

## 2. Detailed Workspace Specifications

### Workspace 1: `job_search` (Standalone War Room)
* **Location:** `C:\Users\Admin\Documents\bioinformatics_project\job_search`
* **Mission:** 100% dedicated to job scouting, tailoring LaTeX CVs (`cv_hereon_aeon_up.tex`), drafting bespoke cover letters, preparing talk slides, and drilling interview Q&A.
* **Deliverables to Create:**
  1. **`.agents/AGENTS.md`**:
     - Scoped strictly to hiring strategy, tone, and interview discipline.
     - Hardcodes the 6 non-negotiable boundaries from `06_do_not_claim.md` (no claiming published Bayesian papers, no claiming mechanistic circuit discovery, no claiming hands-on EPISODE-CityChem, etc.).
     - Calibrated honesty doctrine: *concede limitations before claiming strengths*.
  2. **`PORTFOLIO_RECEIPTS.md`**:
     - A 50-line high-density summary of verified empirical receipts from other projects:
       - **JAX Port:** In-progress port of 0-D/1D Lagrangian water column model (`C:\Users\Admin\Documents\jax-water-column-port\main.py`).
       - **CNP:** Finished PyTorch implementation with logged synthetic runs and epistemic variance measurement (`C:\Users\Admin\Documents\cnp_synthetic\RESULTS.md`).
       - **Chess Transformer Interpretability:** Forward hooks extracting BT3 attention over 64 tokens in 15 transformer blocks (`C:\Users\Admin\Documents\chess_speak_out_loud\backend\neural_vision.py`).
       - **Clinical Data Engineering:** 9 weeks of clinical ETL, data quality pipelines, and synthetic patient cohort analysis.
     - *Benefit:* Allows the agent to draft 100% grounded CV points and letters in <300 tokens without loading external codebases.

---

### Workspace 2: `trainers` (Standalone Daily Harness & Drills)
* **Location:** `C:\Users\Admin\Documents\trainers`
* **Mission:** Maintain the 24/7 daily execution rhythm (03:00 wake-up to 20:00 wind-down), fire auditory timetable alarms, run the Goethe B2 exam simulator, and serve active-recall flashcards.
* **Migration Steps:**
  1. Create directory `C:\Users\Admin\Documents\trainers\`.
  2. Move `trainer/` from `chess_speak_out_loud` into `trainers/trainer/`.
  3. Move `goethe_b2_trainer/` from `chess_speak_out_loud` into `trainers/goethe_b2_trainer/`.
  4. Move desktop launchers (`launch_schedule.bat`, `launch_trainer.bat`, `launch_b2_trainer.bat`, `stop_*.bat`) into `trainers/`.
  5. **Update Path Resolution in `trainer/verify_cards.py`**:
     - Adapt `PROJECT_ROOT` and external references so that the 14 ladders (`air_quality.json`, `bridge.json`, `clinical_project.json`, etc.) continue resolving external sources cleanly.
  6. **Update `trainer/app.py`**:
     - Ensure `GOETHE_DIR` cleanly targets `../goethe_b2_trainer` within the new directory structure.
  7. **Create `trainers/.agents/AGENTS.md`**:
     - Governs card verification rules, KaTeX syntax formatting, German B2 orthography/umlaut standards, and daemon heartbeat logging.

---

### Workspace 3: `chess_speak_out_loud` (Pure Research & LC0 Engine)
* **Location:** `C:\Users\Admin\Documents\chess_speak_out_loud`
* **Mission:** Standalone deep neural network interpretability (LC0) and chess coaching interface.
* **Refactoring Steps:**
  1. Clean `.agents/AGENTS.md` to remove job search and timetable rules, keeping only LC0 orchestration, `manage_lc0` skill, and `windows-dev` branch rules.
  2. Clean root directory of trainer launcher scripts.
  3. Retain pure engine codebase (`backend/`, `frontend/`, `docs/`, `engine/`).

---

## 3. Step-by-Step Implementation Sequence (When Approved)

*Note: Execution will NOT start until your explicit go-ahead.*

1. **Phase 1 — Setup `job_search` Workspace (Zero Risk)**:
   - Author `bioinformatics_project/job_search/.agents/AGENTS.md`.
   - Author `bioinformatics_project/job_search/PORTFOLIO_RECEIPTS.md`.
   - Test opening `job_search` as an Antigravity workspace; verify agent loads context cleanly without chess rules.

2. **Phase 2 — Stage `trainers` Workspace**:
   - Create `C:\Users\Admin\Documents\trainers`.
   - Copy `trainer/`, `goethe_b2_trainer/`, and batch scripts to `trainers/`.
   - Adjust `verify_cards.py` paths and run validation: `python -m trainer.verify_cards`.
   - Confirm all 205+ cards pass validation.
   - Test `launch_schedule.bat` and `launch_b2_trainer.bat` from `trainers/`.
   - Once verified green, clean up the redundant copies from `chess_speak_out_loud`.

3. **Phase 3 — Streamline `chess_speak_out_loud`**:
   - Update `chess_speak_out_loud/.agents/AGENTS.md`.
   - Run backend test suite (`pytest backend/tests`) to ensure chess engine and interpretability modules are 100% unaffected.

---

## 4. Verification Gate (Pass/Fail Criteria)

| Test Item | Target Workspace | Success Criterion |
| :--- | :--- | :--- |
| **Card Verification Gate** | `trainers` | `python -m trainer.verify_cards` exits 0 with all 14 ladders and 205+ cards validated. |
| **B2 Simulator Launch** | `trainers` | `python goethe_b2_trainer/check_imports.py` passes without error; server starts on port 8020. |
| **Timetable Daemon Alarm** | `trainers` | `schedule_daemon.py` initializes, writes heartbeat to `schedule_daemon.json`, and triggers buzzer/popup. |
| **Agent Context Purity** | `job_search` | Starting a chat session in `job_search` loads zero chess engine tokens; adheres to `06_do_not_claim.md`. |
| **Engine Test Suite** | `chess_speak_out_loud` | `pytest backend/tests/test_neural_vision.py` passes with no broken imports. |

---

## 5. Rollback Strategy

Because files will be copied and verified before any deletions:
- If `trainers` fails verification, `chess_speak_out_loud` remains completely untouched and runnable.
- `job_search` changes are additive only (`.agents/AGENTS.md` and `PORTFOLIO_RECEIPTS.md`), posing zero risk to existing LaTeX CVs or study room documents.
