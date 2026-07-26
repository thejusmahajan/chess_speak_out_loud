# TASK FOR GEMINI — Sprint 3 Phase B: Sacrifice-Recognition Drill UI (frontend)

Front-end for the sac/landmine drill (Phase A backend done & merged). Show a position from the
user's own games where a sound sacrifice exists → the user finds it → reveal the sac vs the timid
safe move and how sound it is. This is the hesitation cure (J1/J7). **No timer** — this is
recognition/understanding, not speed. Lean UI. `npm test` + `npm run build` green. No push. STOP for
leader review. Report `SPRINT3_PHASE_B_REPORT.md`.

## Backend endpoints already live (Phase A)
- `POST /api/training/sac/session` body `{count:int}` → `[{id, fen}]` (NO answer — do not try to
  fetch/derive the sac before the guess).
- `POST /api/training/sac/guess` body `{finding_id, uci}` → `{correct:bool, acceptable:bool,
  sac_move:{uci,san,eval_cp,complexity}, safe_move:{san,eval_cp}, eval_loss_cp:int,
  playable_candidates:[{uci,complexity,eval_cp}]}`.
- `GET /api/training/sac/stats` → `{total, correct, acceptable, accuracy, recent_accuracy}`.

## Reuse — DO NOT rebuild
- **`TrainingBoard.tsx`** (`fen`, `interactive`, `onMove(uci,san)`) — the user's drag IS the guess.
  Do NOT build a new board. (Same pattern as `IntuitionDrill.tsx` — you may mirror its structure.)
- `TrainingTab.tsx` `view` state machine — add a `'sacrifices'` view + tab button.
- `api/training.ts` — add the 3 typed clients here.

## Build
1. **api/training.ts:** `startSacSession(count)`, `submitSacGuess(finding_id, uci)`, `getSacStats()`
   with TS interfaces matching the schemas above.
2. **`SacDrill.tsx`** (new):
   - On "Start": `startSacSession(count)` (default e.g. 10). Hold list + index + running score.
   - Per position: prompt **"A strong sacrifice is available here — find it."** +
     `<TrainingBoard fen interactive onMove={handleGuess}/>`. **No countdown timer.**
   - `handleGuess(uci)`: `submitSacGuess(id, uci)` → **soundness reveal panel**:
     - Banner: **HIT** (`correct`) "You found the sacrifice!" / **sound alternative** (`acceptable`)
       "A sound sharp try — LC0 preferred {sac_move.san}" / **miss** "You'd have played it safe."
     - The comparison, framed HONESTLY: *"Safe: {safe_move.san} ({safe_move.eval_cp}cp). Sacrifice:
       {sac_move.san} ({sac_move.eval_cp}cp) — concedes only {eval_loss_cp}cp of objective eval but
       goes into a far sharper position (complexity {sac_move.complexity})."* Do NOT claim the sac
       "wins" — it's a practical sharpening.
     - Then a "Next" control.
   - Running score + end-of-session summary; lifetime accuracy from `getSacStats()`.
3. **TrainingTab wiring:** `'sacrifices'` view + "Train Sacrifices" tab → `<SacDrill/>`.

## Constraints & gates
- Do NOT fetch/infer the answer before the guess (session omits it — keep it that way; reveal only
  from the `guess` response). Do NOT reimplement the board. Do NOT touch the backend, `metrics.py`,
  or the existing `IntuitionDrill`/`UsualSuspects`/`ProfileReport` TS2/`DrillMode`/board overlays.
- Empty state: no eligible sacs → friendly "Run a diagnosis first / no sacrifices found yet".
- **Tests** (`__tests__/SacDrill.test.tsx`), mock the 3 endpoints, mutation-check: (1) renders board +
  the find-the-sac prompt for the first position; (2) a move calls `submitSacGuess` and shows the
  reveal (sac vs safe + eval_loss + HIT/miss banner); (3) end-of-session summary shows accuracy.
  Keep/extend existing tests; don't delete assertions.
- `npm test` green (34 + new), `npm run build` clean. No push. STOP for leader review.
