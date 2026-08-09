# TASK FOR GEMINI — Sprint 2 Phase B: Intuition Speed-Drill UI (frontend)

Front-end for the LC0 intuition drill (Phase A backend is done & merged). Show a position, run a
~10 s timer, the user drags a move as their guess of **LC0's top policy move**, then reveal LC0's
ranked policy and score. Lean, fast UI. `npm test` + `npm run build` stay green. No push. STOP for
leader review. Report `SPRINT2_PHASE_B_REPORT.md`.

## Backend endpoints already live (Phase A) — just consume
- `POST /api/training/intuition/session` body `{count:int}` → `[{epd, fen}]` (NO policy — the answer
  is server-side; do NOT try to fetch/derive it before the guess).
- `POST /api/training/intuition/guess` body `{epd, uci}` → `{correct:bool, rank:int|null,
  your_move:{uci,san,p}|null, top_move:{uci,san,p}, top_policy:[{uci,san,p} × up to 5]}`.
- `GET /api/training/intuition/stats` → `{total, correct, accuracy, recent_accuracy}`.

## Reuse — DO NOT rebuild
- **`frontend/src/components/Training/TrainingBoard.tsx`** already exposes `fen`, `interactive`, and
  `onMove(uci, san)`. Render `<TrainingBoard fen={pos.fen} interactive onMove={handleGuess} />` — the
  user's drag IS the guess. Do NOT build a new board.
- `frontend/src/components/Training/TrainingTab.tsx` `view` state machine — add an `'intuition'` view
  + tab button, mirroring the existing pattern.
- `frontend/src/api/training.ts` — add the 3 typed clients here (next to the others). Don't disturb
  existing types.

## Build
1. **api/training.ts:** `startIntuitionSession(count)`, `submitIntuitionGuess(epd, uci)`,
   `getIntuitionStats()` with TS interfaces matching the schemas above.
2. **`IntuitionDrill.tsx`** (new):
   - On mount / "Start": `startIntuitionSession(count)` (default count e.g. 12). Hold the list +
     current index + running score.
   - Per position: `<TrainingBoard fen interactive onMove={handleGuess}>` + a **~10 s countdown**
     (`INTUITION_SECONDS = 10`, a named const). Show the timer visibly.
   - `handleGuess(uci)`: stop the timer, `submitIntuitionGuess(epd, uci)` → show the **reveal panel**:
     LC0's `top_policy` as a labelled list/bar (san + p%), clearly mark **hit/miss** (was your move ==
     top_move?) and your **rank** (or "not in LC0's top moves"). Then a "Next" control.
   - **Timeout** (countdown hits 0 with no move): submit `submitIntuitionGuess(epd, "")` (backend
     returns correct=False, rank=null) → reveal as a miss. Never leave the user stuck.
   - Running score during the session; an **end-of-session summary** (accuracy this session). Show the
     lifetime trend from `getIntuitionStats()` (accuracy / recent_accuracy).
3. **TrainingTab wiring:** `'intuition'` view + a "Train Intuition" tab button rendering `<IntuitionDrill/>`.

## Constraints & gates
- Do NOT fetch or infer the answer before the guess (the session payload deliberately omits policy —
  keep it that way; the reveal only comes from the `guess` response).
- Do NOT reimplement the board; reuse `TrainingBoard`. Do NOT touch the backend, `metrics.py`, the TS2
  `ProfileReport` section, `UsualSuspects.tsx`, `DrillMode`, or the board/neural overlays.
- Handle empty states: no eligible positions → friendly "Run a diagnosis first / no positions yet".
- **Tests** (`components/Training/__tests__/IntuitionDrill.test.tsx`), mock the 3 endpoints, mutation-
  check mindset: (1) renders a board + timer for the first session position; (2) a move calls
  `submitIntuitionGuess` and shows the reveal (top_policy + hit/miss + rank); (3) timeout submits an
  empty guess and reveals a miss; (4) end-of-session summary shows the accuracy. Keep/extend existing
  tests; don't delete assertions.
- `npm test` green (30 + new), `npm run build` clean. No push. STOP for leader review.
