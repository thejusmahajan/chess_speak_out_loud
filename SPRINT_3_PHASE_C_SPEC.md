# SPRINT 3 PHASE C SPEC — Play the sacrifice out vs LC0 (J1.2 — the user's most-wanted)

After the user finds the sac (Phase A/B), let them **play the attacking side while LC0 defends**
for a few moves, feeling the compensation and getting per-move feedback (Q7.2 step 5). This is the
FIRST engine-driven training feature — it uses the LIVE `lc0_engine`. Two sub-phases: **C1 backend**
(dispatch now), **C2 frontend** (after C1). Full suite green. No push. STOP for leader review.

## Grounded engine facts (verified — do not re-derive)
- `await lc0_engine.analyze(fen, nodes=N)` → `{"evaluation", "best_moves", "pv_lines", "nodes", "wdl"}`.
  **`evaluation` is WHITE-POV centipawns** (or a mate string like `"M5"`/`"-M3"`). `best_moves[0]` is
  LC0's top move (uci). Terminal positions are handled by analyze (±10000 white-POV / 0).
- `metrics.eval_cp_number(evaluation)` → normalizes evaluation (incl. mate strings) to **white-POV cp**.
  USE IT — don't parse evals yourself.
- `lc0_engine` is a module global in `app.py` (routes already `await lc0_engine.analyze(...)`). It may
  be in **mock mode** (`lc0_engine.is_available()` False) — handle gracefully.

## LEADER-PINNED — POV, judging, flow (implement VERBATIM; the POV is the #1 trap)
- **Attacker = the side to move at `fen_before`** (the side that plays the sac). `attacker_is_white`
  = board.turn at fen_before.
- **`attacker_eval_cp = white_cp if attacker_is_white else -white_cp`** where `white_cp =
  metrics.eval_cp_number(evaluation)`. Positive attacker_eval = the attack is working. (This is THE
  bug source — get it wrong and every eval/feedback is inverted. Trace it for a black attacker.)
- **Node budget:** `PLAYOUT_NODES` module constant (start ~4000 — responsive; the app's live net is
  fast). `PLAYOUT_PLIES` (target length, e.g. 8 = ~4 user moves).
- **Move judging** (after the user's attacking move, using analysis of the position BEFORE the move):
  `lc0_best = best_moves[0]`; `eval_best_att` = attacker-POV eval of the pre-move position; play the
  user move, `eval_after_att` = attacker-POV eval of the resulting position. `drop = eval_best_att -
  eval_after_att` (≥0). Classify: `great` if `user_uci == lc0_best or drop <= 30`; `ok` if `drop <=
  100`; else `drift`. Reveal `lc0_best` (san) ONLY after the user has moved.

## PHASE C1 (dispatch now) — backend playout, in `sac_drill.py` (extend) + routes + tests
STATELESS (the client holds the line; the server replays it each call — no session state).
1. `POST /api/training/sac/playout/start` body `{finding_id}`:
   - Look up the steer_finding; from `fen_before` play the sac (`steer.uci`); analyze → LC0 plays its
     best DEFENSE (`best_moves[0]`); apply it. Now attacker to move.
   - Return `{finding_id, fen, line:[sac_uci, defense_uci], attacker_is_white, attacker_eval_cp, ply:2,
     target_plies: PLAYOUT_PLIES, user_to_move:true}`. Do NOT return LC0's best attacking move.
2. `POST /api/training/sac/playout/move` body `{finding_id, line:[uci...], user_uci}`:
   - Rebuild the board from `fen_before` + `line`; validate it's the attacker's move and `user_uci` is
     legal (else 400). Judge per the pinned math (analyze pre-move → lc0_best + eval_best_att; apply
     user_uci → analyze → eval_after_att). Then LC0 defends (`best_moves[0]` of the post-user position);
     apply it. If the game ends (checkmate/stalemate) or `ply >= target_plies` → `is_complete:true`.
   - Return `{quality: "great"|"ok"|"drift", lc0_best_attack:{uci,san}, eval_after_cp, lc0_reply:
     {uci,san}|null, fen, line, ply, attacker_eval_cp, is_complete, summary?}`. On complete, `summary`
     = `{moves: N, great: n, ok: n, drift: n, final_eval_cp, verdict:str}` (verdict e.g. "You kept the
     attack" if final_eval_cp stays clearly positive, else "the attack fizzled — LC0 held").
   - **Terminal / mate:** if analyze reports mate/terminal, complete the playout with the right verdict
     (attacker mated the defender = best outcome).
3. **Mock-mode / no engine:** if `not lc0_engine.is_available()`, return `{"error":"engine_unavailable"}`
   (both endpoints) so the UI can disable the feature — never crash.
4. **Tests** (`backend/tests/test_sac_playout.py`) — MOCK `lc0_engine.analyze` (do NOT require a real
   engine): a deterministic fake returning scripted `{evaluation, best_moves}`. Assert, mutation-check:
   (1) POV — a BLACK-attacker position yields positive `attacker_eval_cp` when white_cp is negative;
   (2) judging thresholds (great/ok/drift by the pinned drop cutoffs, and great on exact lc0_best match);
   (3) `start` does NOT leak the best attacking move; (4) `is_complete` fires at `target_plies` and on a
   mocked terminal; (5) illegal user move → 400; (6) engine-unavailable → the error dict.
- **Gates:** full suite green (177 + new); do NOT touch `metrics.py` (reuse `eval_cp_number`); no
  reliance on a real engine in tests. No push. STOP. Report `SPRINT3_PHASE_C1_REPORT.md`.

## PHASE C2 (spec after C1) — frontend: continue the attack on the board
- After the Phase-B sac reveal, a **"Play it out vs LC0"** button → `playout/start` → interactive
  `<TrainingBoard>` where the user plays the attack; each move → `playout/move` → apply LC0's reply on
  the board, show the **quality badge** (great/ok/drift), the running **attacker eval**, and "LC0
  preferred {lc0_best_attack.san}" when the user drifted. End-of-line **summary** verdict. Disable the
  button if `start` returns `engine_unavailable`. Reuse the board; lean UI; tests + build green.

## Sequencing
Dispatch **C1 only** → leader audits (mutation-check the POV conversion for a black attacker, the
judging thresholds, and the no-leak/mock-mode handling) → then C2. This is the piece the user rated
most-wanted; the engine + POV make it the highest-risk phase, so the pinned math + mocked tests matter.
