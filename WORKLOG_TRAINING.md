# WORKLOG — Elite Training System

> Append-only shared log. Newest entry on top. Every entry: date, agent
> (Leader / Gemini / Claude), phase, what was done, pasted verification output,
> open questions. Workers: paste REAL command output, never summaries of it.

---

## 2026-07-19 — Gemini — Phase G1: Storage & job state
- Created `backend/training/store.py` with `EpdCache` and storage helpers for jobs, profiles, repertoires, and drill sets.
- Wrote and executed acceptance gate G1 test suite.

Gate G1 output:
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 5 items

backend\tests\test_training_store.py .....                               [100%]

============================== 5 passed in 0.27s ==============================
```

## 2026-07-19 — Leader (Claude Code) — Phase 0: design + foundations
- Verified oracle APIs (plan §2 table) directly against source.
- Added public `NeuralVision.saliency_absolute(fen)` (absolute frame, both colors,
  falls back gracefully) — training code must use this, never `saliency()`.
- Wrote and tested `backend/training/metrics.py` (normative math). Smoke tests:
  `ALL METRICS TESTS PASSED` (policy divergence severities, en-passant interaction
  squares, attention blindness, mover-POV confirmation swing incl. mate strings,
  quietness, top4 concentration, hidden-gem gate, WDL sharpness, alt solutions).
- Published `TRAINING_SYSTEM_PLAN.md`, `GEMINI_TRAINING_TASKS.md`,
  `CLAUDE_TRAINING_TASKS.md`.
- Open: nothing. Next: Gemini G1 ∥ Claude C1.
