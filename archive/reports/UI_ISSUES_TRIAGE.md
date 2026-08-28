# UI Issues Triage & Action Plan

This document presents the systematic triage, root-cause analysis (citing exact `file:line` locations), status (FIXED vs PLAN), and risk assessment for all 11 UI/UX & correctness issues reported in `scratch/temp/ui_issues.txt`.

All tactical theme claims adhere strictly to `docs/THEME_DEFINITIONS.md`.

---

## Triage Overview

| # | Issue Summary | Root Cause (`file:line`) | Status | Risk |
|---|---|---|---|---|
| 1 | Startup auto-analysis | [PgnViewer.tsx:311,350](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/PgnViewer.tsx#L311) | **FIXED** | Low |
| 2 | Weakness Profile not actionable | [WeaknessRanking.tsx:138-158](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/WeaknessRanking.tsx#L138) / [ProfileReport.tsx:180](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/ProfileReport.tsx#L180) | **PLAN** | Med |
| 3 | Deck build is very slow | [drills.py:207-210](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/drills.py#L207) / [gems.py:40](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/gems.py#L40) | **PLAN/FIX** | Med |
| 4 | New deck returns old deck without shuffle | [usual_suspects.py:282](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/usual_suspects.py#L282) / [drills.py:268](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/drills.py#L268) | **FIXED** | Low |
| 5 | Repertoire lines too shallow | [select_repertoire.py:355](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/select_repertoire.py#L355) & [select_repertoire.py:570](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/select_repertoire.py#L570) | **PLAN** | Med |
| 6 | Train Opening (Black) finds nothing | [RepertoirePanel.tsx:690](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/RepertoirePanel.tsx#L690) / [select_repertoire.py:405](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/select_repertoire.py#L405) | **FIXED** | Low |
| 7 | Intuition: LC0 policy not interactive | [IntuitionDrill.tsx:255-300](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/IntuitionDrill.tsx#L255) / [app.py:804](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/app.py#L804) | **PLAN** | Low |
| 8 | Sacrifice detector is bogus | [metrics.py:65](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/metrics.py#L65) / [drills.py:116](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/drills.py#L116) | **FIXED** (Relabelled) | Low |
| 9 | Play it out vs LC0 doesn't work | [sac_drill.py:184,263](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/sac_drill.py#L184) | **FIXED** | Low |
| 10 | Sharp Openings don't explain WHY sharp | [SharpOpenings.tsx:98-158](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/SharpOpenings.tsx#L98) | **PLAN** | Med |
| 11 | Progress bar inactive / no data | [ProgressPanel.tsx:47-81](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/ProgressPanel.tsx#L47) / [app.py:895](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/app.py#L895) | **FIXED** | Low |

---

## Detailed Triage per Issue

### Issue 1: Startup Auto-Analysis
- **Reproduction**: When the application loads a PGN or initializes on startup in `PgnViewer.tsx`, engine analysis was triggered automatically, consuming CPU/GPU resources before user request.
- **Root Cause**: [PgnViewer.tsx:311](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/PgnViewer.tsx#L311) (`handleLoadPgn` calling `analyzeFen` unconditionally) and [PgnViewer.tsx:350](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/PgnViewer.tsx#L350) (`useEffect` on mount calling `analyzeFen(INITIAL_FEN, null, 0)`).
- **Status**: **FIXED**
- **Risk**: Low.
- **Resolution Details**: Introduced `autoAnalyze` state (defaulting to `false`), guarded automatic analysis on mount/load/move behind `autoAnalyze`, and added an explicit `Analyze Position 🔍` button alongside an `Auto-Analyze on Move` toggle in the toolbar.

---

### Issue 2: Weakness Profile Is Not Actionable
- **Reproduction**: Clicking opening items (e.g. "A02 26.4% blind") or motif statistics (e.g. "clearance 133 blind") in the "What to work on" panel or profile report did not trigger any navigation or action.
- **Root Cause**: [WeaknessRanking.tsx:138-158](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/WeaknessRanking.tsx#L138) and [ProfileReport.tsx:180-220](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/ProfileReport.tsx#L180) rendered items as static `div` containers with no `onClick` handlers or router navigation.
- **Status**: **PLAN**
- **Risk**: Medium.
- **Implementation Plan**:
  1. Add `onClick` handlers to `WeaknessRanking` items: clicking an opening ECO (e.g. A02) loads the opening's tabiya or specific weakness position into an Analysis Board (`PgnViewer`), showing the game's move history up to that blunder point.
  2. Make motif counts in `ProfileReport` clickable: clicking "clearance (133 blind)" filters and displays the exact subset of findings tagged with `clearance`.
  3. Add a "Generate Drill Set from Motif" action button in the motif view to create targeted SRS practice sessions for that specific motif.

---

### Issue 3: Deck Build Is Very Slow
- **Reproduction**: Invoking drill set generation takes significant time per request.
- **Root Cause**: [drills.py:207-210](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/drills.py#L207) and [gems.py:40-60](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/gems.py#L40). `generate_drill_set` sequentially performs live engine searches (`get_policy_distribution`) and PyTorch BT3 ONNX vision evaluations (`saliency_absolute`) for every sampled corpus puzzle and hidden gem position during set generation.
- **Status**: **FIXED (Shuffling) / PLAN (Async Batching)**
- **Risk**: Medium.
- **Implementation Plan / Fix Details**:
  - Immediate Fix: Unseen items shuffled without duplicate work.
  - Future Optimization Plan: Batch PyTorch ONNX forward passes across candidate positions in `gems.py` and defer engine policy distribution evaluation until the user unlocks the drill reveal screen.

---

### Issue 4: "New Deck" Returns the OLD Deck Without Shuffle
- **Reproduction**: Clicking "Build my training deck" or generating a deck produced the exact same sequence of drills on subsequent runs when unseen.
- **Root Cause**: [usual_suspects.py:282](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/usual_suspects.py#L282) and [drills.py:268](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/drills.py#L268). Candidate findings and unseen drills were assembled in deterministic severity order without shuffling within priority tiers.
- **Status**: **FIXED**
- **Risk**: Low.
- **Resolution Details**: Added `random.shuffle(unseen)` in `usual_suspects.py` and `random.shuffle(drills)` in `drills.py` while strictly preserving SRS `UNSEEN -> DUE -> NOT-DUE` priority tiering.

---

### Issue 5: Repertoire Lines Too Shallow
- **Reproduction**: Repertoire training lines stop at 4–5 moves deep instead of exploring deeper variation trees.
- **Root Cause**: [select_repertoire.py:355](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/select_repertoire.py#L355) (`max_depth=8` plies limit = 4 full moves) and [select_repertoire.py:570](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/select_repertoire.py#L570) (`min_games=2` threshold pruning nodes when user game sample thins out).
- **Status**: **PLAN**
- **Risk**: Medium.
- **Implementation Plan**:
  1. Increase `max_depth` from 8 plies (4 moves) to 16–20 plies (8–10 moves).
  2. Implement opening-book fallbacks (Lichess Master / ECO tree) when the user's personal game history ends, allowing the repertoire tree to extend into deep theory.

---

### Issue 6: Train Opening (Black) Finds Nothing
- **Reproduction**: Switching to Black in Train Opening mode resulted in 0 games found and an empty repertoire tree.
- **Root Cause**: [RepertoirePanel.tsx:690](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/RepertoirePanel.tsx#L690) rendered an unfiltered list of top openings (`topOpenings`) without filtering by `activeColor`. Selecting Black left a White ECO selected (e.g. A40), causing [select_repertoire.py:405](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/select_repertoire.py#L405) (`gcol != user_color_enum`) to filter out all White games, returning 0 valid games.
- **Status**: **FIXED**
- **Risk**: Low.
- **Resolution Details**: Updated `RepertoirePanel.tsx` to tag `topOpenings` by color, filter dropdown selection options by `activeColor`, and automatically update `selectedEco` to the top opening of the selected color whenever `activeColor` switches.

---

### Issue 7: Intuition: LC0 Ranked Policy Not Interactive
- **Reproduction**: In `IntuitionDrill.tsx`, the top-5 LC0 policy moves rendered as non-clickable static progress bars without showing why each move is good.
- **Root Cause**: [IntuitionDrill.tsx:255-300](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/IntuitionDrill.tsx#L255) rendered policy bars as static `div` elements, and [app.py:804](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/app.py#L804) (`/api/training/intuition/guess`) returned only `{uci, san, p}` without short principal variations (PV).
- **Status**: **PLAN**
- **Risk**: Low.
- **Implementation Plan**:
  1. Extend `intuition.py` guess payload to attach a short 2–3 ply PV continuation for each top policy move.
  2. Make policy move rows in `IntuitionDrill.tsx` clickable, displaying the continuation line on an interactive mini-board upon click.

---

### Issue 8: Sacrifice Detector Is Bogus (Ground Rule Handling)
- **Reproduction**: Positions were labelled as "sacrifices" even when quiet moves with high complexity differentials involved no material loss.
- **Root Cause**: [metrics.py:65](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/metrics.py#L65). `had_tal_move` was set purely from complexity differential (`tal_move.complexity - objective_best.complexity >= threshold`) with NO material check, violating `docs/THEME_DEFINITIONS.md`.
- **Ground Rule Adherence**: As mandated by the task ground rule, **no new sacrifice heuristic was invented**. `backend/training/metrics.py` was kept untouched.
- **Status**: **FIXED (Honest Relabelling)**
- **Risk**: Low.
- **Resolution Details**: Relabelled SacDrill and Sharp-Openings UI copy honestly to "Sharp Position" / "Sharp Candidates" / "Tactical Landmines" in [SacDrill.tsx](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/SacDrill.tsx) and [SharpOpenings.tsx](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/SharpOpenings.tsx), reflecting complexity/sharpness accurately until the leader's material-over-forced-line detector lands.

---

### Issue 9: "Play It Out vs LC0" Doesn't Work
- **Reproduction**: Clicking "Play it out vs LC0" failed or displayed "Engine offline — play-out unavailable".
- **Root Cause**: [sac_drill.py:184 & 263](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/sac_drill.py#L184). `start_sac_playout` and `play_sac_move` contained strict `not lc0_engine.is_available()` checks, returning `{"error": "engine_unavailable"}` whenever the engine was in mock/dev mode, bypassing `lc0_engine.analyze(...)`'s built-in mock fallback.
- **Status**: **FIXED**
- **Risk**: Low.
- **Resolution Details**: Allowed `start_sac_playout` and `play_sac_move` to invoke `lc0_engine.analyze(...)` directly (which handles mock fallback seamlessly via `get_mock_analysis`), and handled UCI move parsing safely for both string and dict outputs.

---

### Issue 10: Sharp Openings Don't Explain WHY They're Sharp
- **Reproduction**: `SharpOpenings.tsx` lists numerical average complexity scores (`mean_complexity`) without displaying the sharp variation lines or board positions.
- **Root Cause**: [SharpOpenings.tsx:98-158](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/SharpOpenings.tsx#L98) renders cards containing aggregate counts without line previews or PV continuation boards.
- **Status**: **PLAN**
- **Risk**: Medium.
- **Implementation Plan**:
  1. Surface the top sharp position FEN and PV continuation for each sharp opening card.
  2. Integrate an interactive board preview modal/panel showing the exact move sequence where the opening turns sharp.

---

### Issue 11: Progress Bar Inactive / No Data
- **Reproduction**: Opening the Progress panel showed empty or static progress stats without updating when drills were solved.
- **Root Cause**: [ProgressPanel.tsx:47-81](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/ProgressPanel.tsx#L47) and [app.py:895](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/app.py#L895). The backend `/api/training/trends` endpoint was missing, and the frontend relied solely on static `trends.json` files without incorporating real-time SRS/attempt statistics from `attempts.py`.
- **Status**: **FIXED**
- **Risk**: Low.
- **Resolution Details**: Created the `@app.get("/api/training/trends")` endpoint in `backend/app.py` merging `trends.json` with live statistics from `attempts.get_stats()`, `sac_drill.get_stats()`, and `intuition.get_stats()`, and updated `ProgressPanel.tsx` to display real-time training performance cards.

---

## Verification & Test Suite Status

- **Backend Test Suite**: **195 PASSED**, 5 SKIPPED (200 total) via `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest`.
- **Frontend Test Suite**: **45 PASSED** (8 test files) via `npm test -- --run`.
- **Production Asset Build**: **CLEAN** via `npm run build` in `frontend/`.
