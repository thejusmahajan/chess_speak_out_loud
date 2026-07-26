# TASK FOR GEMINI — Sprint 4 Phase B: "Sharp Openings" view (+ tiny backend hook)

Final piece of Sprint 4. Show the user where his openings can go sharp (Phase A data) and let him
drill an opening's sacrifices + explore recommended dynamic lines. Mostly frontend, plus ONE small
backend hook so "drill this opening" works. `npm test` + `npm run build` + backend suite green.
No push. STOP for leader review. Report `SPRINT4_PHASE_B_REPORT.md`.

## Backend endpoints already live (Phase A)
- `GET /api/training/openings/sharpness` → `{openings:[{eco,name,sacs,mean_complexity,n_positions,
  top_positions:[finding_id...],sharpness_score}]}` (ranked DESC).
- `GET /api/training/openings/recommendations?color=` → `{recommendations:[{eco,name,color,sac_idea,
  themes,why}]}`.

## Small backend hook (so "drill this opening" works)
- Add an OPTIONAL `eco` filter to the sac session: `sac_drill.build_sac_session(count, eco=None)` —
  when `eco` is set, restrict `_get_tal_findings()` to steer_findings whose `opening.eco == eco`
  (behavior-preserving when `eco is None`). Thread it through `POST /api/training/sac/session`
  (accept optional `eco` in the body). Add 1 test: session with `eco="D02"` returns only that
  opening's sacs. Do NOT change scoring or the no-answer-leak guarantee.

## Frontend build
1. **api/training.ts:** `getOpeningSharpness()`, `getOpeningRecommendations(color?)`, and extend
   `startSacSession` to pass an optional `eco`. Typed interfaces.
2. **`SharpOpenings.tsx`** (new):
   - Fetch `getOpeningSharpness()` → render your openings **ranked by sharpness**: eco, name,
     `sacs` (× sac icon), `mean_complexity`, `n_positions`. Headline framing at top, e.g. the #1
     opening: "Your {name} hides {sacs} sacrifices you're not taking."
   - Each opening row has a **"⚔ Drill this opening's sacrifices"** action → starts a SacDrill session
     filtered to that `eco` (reuse `SacDrill` — pass the `eco` so it calls `startSacSession(count, eco)`;
     the SacDrill flow/reveal/play-out are unchanged). Do NOT fork SacDrill.
   - A **"Dynamic openings to explore"** section from `getOpeningRecommendations()`: cards with name,
     `sac_idea`, `themes` chips, and `why`. Optional color toggle.
   - Empty state: no profile / no sharp openings → friendly prompt.
3. **TrainingTab wiring:** add a `'sharp_openings'` view + "Sharp Openings" tab → `<SharpOpenings/>`
   (mirror the existing view-switch pattern).

## Constraints & gates
- Reuse `SacDrill` (via the `eco` filter) and the board — do NOT reimplement drills or the board. Do
  NOT touch `metrics.py` or other modes' code. Keep the sac no-answer-leak guarantee intact.
- **Tests:** backend — the `eco`-filter test above (mutation-check: `eco="D02"` → only D02 sacs).
  Frontend (`SharpOpenings.test.tsx`, mock the 2 endpoints): (1) renders ranked openings with sac
  counts; (2) "Drill this opening" triggers a SacDrill session with the right `eco`; (3) recommendations
  render; (4) empty state. Keep/extend existing tests; don't delete assertions.
- Backend suite green (194 + 1); `npm test` green (41 + new); `npm run build` clean. No push. STOP.
