# TASK FOR GEMINI — Sprint 3 Phase C2: play the sacrifice out vs LC0 (frontend)

The final piece of Sprint 3. After the user finds the sac (Phase B), let them **play the attack
out while LC0 defends**, with per-move feedback and a running "is the attack working?" eval,
ending in a verdict. C1 backend is done & merged. Reuse the board. `npm test` + `npm run build`
green. No push. STOP for leader review. Report `SPRINT3_PHASE_C2_REPORT.md`.

## Backend endpoints already live (C1) — STATELESS (client holds `line` + `history`)
- `POST /api/training/sac/playout/start` `{finding_id}` → `{finding_id, fen, line:[uci], attacker_is_white,
  attacker_eval_cp, ply, target_plies, user_to_move}` — OR `{"error":"engine_unavailable"}`.
- `POST /api/training/sac/playout/move` `{finding_id, line:[uci], user_uci, history:[quality]}` →
  `{quality:"great"|"ok"|"drift", lc0_best_attack:{uci,san}, eval_after_cp, lc0_reply:{uci,san}|null,
  fen, line:[uci], ply, attacker_eval_cp, is_complete, summary?}` (summary on complete:
  `{moves, great, ok, drift, final_eval_cp, verdict}`). 400 on illegal move.

## Reuse — DO NOT rebuild
- **`TrainingBoard.tsx`** (`fen`, `orientation`, `interactive`, `onMove(uci,san)`) — the user's drag is
  the attacking move. Orient the board to the **attacker** (`attacker_is_white ? 'white' : 'black'`).
- Integrate the play-out INTO **`SacDrill.tsx`** as a continuation AFTER the sac reveal (a "Play it out
  vs LC0" button on/after the reveal panel) — do not make a whole separate tab. Keep the existing
  find-the-sac flow intact.
- `api/training.ts` — add the 2 typed clients + interfaces.

## Build
1. **api/training.ts:** `startSacPlayout(finding_id)`, `submitPlayoutMove(finding_id, line, user_uci,
   history)` with interfaces matching the schemas above.
2. **In `SacDrill.tsx`:** after a reveal, show **"▶ Play it out vs LC0"**. On click:
   `startSacPlayout` → if `error==="engine_unavailable"`, show "Engine offline — play-out unavailable"
   and don't enter play-out. Else enter play-out mode:
   - Hold `line` (uci[]) and `history` (quality[]) in state (STATELESS server — you accumulate both).
   - Render `<TrainingBoard fen={playout.fen} orientation={attackerColor} interactive={playout.user_to_move
     && !complete} onMove={handleAttackMove} />`.
   - `handleAttackMove(uci)`: `submitPlayoutMove(finding_id, line, uci, history)` → append `quality` to
     `history`, set `line`/`fen` from the response, show a **quality badge** (great 🟢 / ok 🟡 / drift 🔴),
     the **running attacker eval** (`attacker_eval_cp`, + = attack working), and **"LC0 preferred
     {lc0_best_attack.san}"** when `quality !== "great"`. Then apply LC0's reply (it's already in the
     returned `fen`/`line`).
   - On `is_complete`: show the **summary verdict** (moves, great/ok/drift counts, final eval, `verdict`
     text) + a "Back to sacrifices" / "Next position" control.
   - Handle the 400 (illegal move) gracefully (the board only offers legal moves, but guard anyway).

## Constraints & gates
- Reuse `TrainingBoard`; do NOT reimplement the board or touch the backend/`metrics.py`/other modes
  (UsualSuspects, IntuitionDrill, ProfileReport TS2, DrillMode, board overlays).
- **Tests** (extend `SacDrill.test.tsx` or a new `SacPlayout.test.tsx`), mock the 2 endpoints,
  mutation-check: (1) the "Play it out" button appears after a reveal and start enters play-out;
  (2) an attacking move calls `submitPlayoutMove` with the accumulated line+history and shows the
  quality badge + LC0 reply; (3) `is_complete` shows the summary verdict; (4) `engine_unavailable`
  disables the play-out with a message. Keep/extend existing tests; don't delete assertions.
- `npm test` green (37 + new), `npm run build` clean. No push. STOP for leader review.
