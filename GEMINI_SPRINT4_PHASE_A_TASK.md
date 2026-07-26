# TASK FOR GEMINI — Sprint 4 Phase A: sharpness-by-opening + new-opening recommendations (backend)

Phase 0 (ECO backfill) is done & the real profile is enriched (54 real ECOs). Now surface, per
opening, WHERE the user can go sharp (from his own games), and RECOMMEND dynamic openings to explore.
No engine (pure profile analysis + curated data). Full suite green. No push. STOP for leader review.
Report `SPRINT4_PHASE_A_REPORT.md`.

## Grounded — the analysis already previewed correctly on the real profile
Per real ECO, count sac candidates (`steer_findings` with `had_tal_move`) + mean steer complexity.
Real numbers now: D02 London 13 sacs / 0.724, C44 13 / 0.564, C21 Center Game 11 / 0.731,
A46/A48 London 10 each, C35 King's Gambit 9 / 0.809, D00 6 / 0.845. This IS the feature.

## Build
### 1. `backend/training/openings_sharpness.py`
- `sharpness_by_opening(profile: dict) -> list[dict]`: group `steer_findings` (and `findings` for the
  count) by real `opening.eco` (skip `'???'`); per opening return
  `{eco, name, sacs, mean_complexity, n_positions, top_positions: [steer_finding_id ... sorted by
  steer.complexity DESC, top ~8]}`. Sort openings by a **sharpness score = sacs * mean_complexity**
  DESC (so opening-with-many-sharp-sacs ranks first). `top_positions` are the finding ids so the UI /
  SacDrill can drill straight into that opening's sacs.
- Route `GET /api/training/openings/sharpness` → `{openings: [...]}` (404 if no profile).
### 2. Curated new-opening recommendations
- `backend/openings_data/sharp_recommendations.json`: ~10-12 dynamic openings, each
  `{eco, name, color:"white"|"black", sac_idea:str, themes:[str], why:str}`. Cover 1.e4 gambits the
  user already flirts with + natural next steps: Evans Gambit (C51/52), Fried Liver / Two Knights
  (C57), Giuoco Piano Nc3 lines (C50/54), King's Gambit (C33-C39), Danish/Center Game (C21), Smith-
  Morra (B21), Scotch Gambit (C44), plus a Black sharp option or two (e.g. Albin Countergambit D08,
  which he already plays). Honest, concrete `sac_idea`/`why`.
- Route `GET /api/training/openings/recommendations` → `{recommendations: [...]}` (optionally accept a
  `?color=` filter). Static curated data — no analysis.

## Constraints & gates
- Do NOT touch `metrics.py`; no engine calls (pure profile + static data). Match the real
  `opening.eco`/`steer_findings` schema. Reuse existing patterns.
- **Tests** (`test_openings_sharpness.py`), mutation-check: (1) sac count per ECO = # had_tal
  steer_findings in that opening; (2) openings sorted by `sacs*mean_complexity` DESC; (3) `'???'`
  excluded; (4) `top_positions` are real finding ids sorted by complexity; (5) recommendations route
  returns the curated list (and honors `?color=`). Synthetic-profile fixture.
- `python -m pytest backend/tests` stays green (189 + new; note: `test_ts2_no_hang` orphan-cancel test
  is known-flaky/timing — re-run it alone if it flaps, it is NOT related to this change). No push. STOP.

## PHASE B (spec after A) — frontend "Sharp Openings" view
Extend/reuse `RepertoirePanel.tsx`: your openings ranked by sharpness (from `/openings/sharpness`),
each expandable to its sharp positions → "drill these" hands the `top_positions` to the existing
SacDrill; a "Dynamic openings to explore" card list from `/openings/recommendations`. Reuse the board /
repertoire tree. Lean; tests + build green.
