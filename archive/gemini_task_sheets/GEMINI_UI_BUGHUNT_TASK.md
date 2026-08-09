# TASK FOR GEMINI (Instance 2) — UI bug hunt, anchored on "tactical steering not visible"

Find and FIX real UI bugs, anchored on a concrete symptom the user reported: **the successful
30-game diagnosis produced 263 `steer_findings`, but the user does NOT see tactical steering
(TS2) results anywhere in the UI.** You edit `frontend/src`. The leader (Claude) audits every
change before merge. Work on a branch / leave staged; **do not push.**

## The stack (grounded)
- Frontend: **Vite + React + TypeScript**, `frontend/`. Training UI in
  `frontend/src/components/Training/`: `DiagnosePanel.tsx`, `ProfileReport.tsx`,
  `WeaknessRanking.tsx`, `RepertoirePanel.tsx`, `DrillMode.tsx`, `TrainingBoard.tsx`,
  `ProgressPanel.tsx`, `TrainingTab.tsx`. API client: `frontend/src/api/training.ts`.
  Tests exist under `frontend/src/components/Training/__tests__/`.
- The diagnosis writes a **`profile.json`** consumed by the UI. Its schema (from
  `backend/training/pipeline.py`) includes: `findings` (213), `aggregates`,
  **`steer_findings` (263)**, `steer_summary`, `steer_budget_exhausted`, `games_analyzed`,
  `moves_analyzed`, `regressions`.

## THE ANCHOR — why is tactical steering invisible? (highest priority)
**Grounding fact:** `steer_findings` is referenced throughout the BACKEND
(`pipeline.py`, `metrics.py`, `drills.py`, `select_repertoire.py`, `trends.py`), but in the
FRONTEND the string "steer" appears ONLY in `DrillMode.tsx` — NOT in `ProfileReport.tsx` or
`WeaknessRanking.tsx`. So TS2 is very likely **computed and stored but never surfaced in the
diagnosis/profile view**, only (maybe) reachable through drills.

Trace the full path and determine the true cause, then fix it:
1. **Backend → API:** does an endpoint expose `steer_findings`/`steer_summary`? Find the route
   in `backend/app.py` (or wherever) that serves the profile. Does it include these fields?
2. **API client:** does `frontend/src/api/training.ts` type/fetch them? Are the TS types missing
   `steer_findings`, causing them to be dropped/ignored?
3. **Render:** which component (if any) renders tactical steering? Is it only `DrillMode`
   (needs enough data / a drill session), or genuinely nowhere in `ProfileReport`?
4. **Decide the true cause** among: (a) not surfaced in UI at all; (b) only in DrillMode and
   the user never entered that path; (c) field-name/type mismatch dropping the data;
   (d) filtered by a threshold; (e) empty because of a real data issue.
5. **FIX:** surface tactical steering appropriately in the diagnosis view (e.g. a TS2 section in
   `ProfileReport.tsx` showing steer_findings / steer_summary — count, top sacrificial/Tal
   candidates, complexity), WITHOUT removing existing features. If the API doesn't expose the
   fields, that's a backend-shape gap — **file it in `QUESTIONS_FOR_LEADER.md`; do NOT edit
   `backend/training/metrics.py` (leader-owned).** Small read-only additions to a non-metrics
   API route are OK but flag them for review.

## Secondary — general UI bug hunt (Training components)
Look for and fix: crashes/blank states on real profile data, missing empty-data handling,
console errors/warnings, TS type mismatches vs the profile schema, dead/unused props, broken
loading/error states, incorrect field access (e.g. reading a key the backend renamed).

## Deliverables
1. `UI_BUGHUNT_REPORT.md`: (a) the tactical-steering root-cause diagnosis with the exact
   file:line trace across backend-route → api/training.ts → component; (b) a findings table
   `bug | file:line | symptom | root cause | fix applied`; (c) anything that needs the leader
   (API-shape/backend gaps).
2. Code fixes in `frontend/src` (+ minimal non-metrics API additions if unavoidable, flagged).
3. `npm run build` clean and `npm test` green (update/extend the existing __tests__ as needed;
   don't delete tests to make them pass).

## Constraints
- Preserve all existing features/quality — surface TS2, don't rip anything out.
- Profile schema (backend) is the source of truth; match its field names exactly.
- Do NOT touch `backend/training/metrics.py`; route backend-shape needs to `QUESTIONS_FOR_LEADER.md`.
- Every fix cites file:line + the concrete symptom. Present all changes for leader review; don't
  push. STOP for go.
