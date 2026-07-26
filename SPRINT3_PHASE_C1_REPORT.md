# Sprint 3 Phase C1 Report — Play the sacrifice out vs LC0 (Backend)

## Executive Summary
Phase C1 backend implementation is complete and verified against all leader-pinned rules and mathematical specifications. The live engine playout service allows users to play the attacking side against LC0 defense following a sacrifice discovery.

---

## Implemented Components

### 1. Engine Playout Core ([sac_drill.py](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/sac_drill.py))
- Defined playout constants: `PLAYOUT_NODES = 4000`, `PLAYOUT_PLIES = 8`.
- Implemented `start_sac_playout(finding_id, lc0_engine)`:
  - Replays initial position from `fen_before`, executes sacrifice (`steer.uci`), and queries LC0 for top defense reply (`best_moves[0]`).
  - Evaluates position after LC0 defense to provide initial `attacker_eval_cp`.
  - **No Leakage**: Does NOT leak LC0's preferred attack move.
- Implemented `play_sac_move(finding_id, line, user_uci, lc0_engine, history)`:
  - Rebuilds board state from `fen_before` + `line`.
  - Performs pre-move position analysis (`nodes=4000`) to extract `lc0_best` and `eval_best_att`.
  - Executes `user_uci` and performs post-user analysis to extract `eval_after_att`.
  - Computes evaluation drop: `drop = eval_best_att - eval_after_att`.
  - Classifies quality:
    - `great`: `user_uci == lc0_best or drop <= 30`
    - `ok`: `drop <= 100`
    - `drift`: `drop > 100`
  - Handles LC0 defense reply and checks completion conditions (`ply >= PLAYOUT_PLIES` or `board.is_game_over()`).
  - Generates final `summary` on completion (`moves`, `great`, `ok`, `drift`, `final_eval_cp`, `verdict`).

### 2. FastAPI Endpoints ([app.py](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/app.py))
- `POST /api/training/sac/playout/start`: Takes `{finding_id}`, returns initial playout state.
- `POST /api/training/sac/playout/move`: Takes `{finding_id, line, user_uci, history?}`, returns move feedback, quality rating, and LC0 reply.
- Pydantic models: `SacPlayoutStartRequest`, `SacPlayoutMoveRequest`.
- Gracefully handles engine unavailability (`{"error": "engine_unavailable"}`).
- Returns HTTP 400 on illegal user moves or bad line state.

---

## Leader Audit Verification

| Audit Item | Specification | Implementation Verification | Status |
| :--- | :--- | :--- | :--- |
| **Black Attacker POV** | `attacker_eval_cp = white_cp if attacker_is_white else -white_cp` | Tested in `test_black_attacker_pov_conversion`: negative white-POV eval correctly yields positive attacker-POV eval for Black. | **VERIFIED** |
| **Judging Cutoffs** | `great` (exact match or drop ≤ 30), `ok` (drop ≤ 100), `drift` (> 100) | Tested in `test_judging_thresholds_great_ok_drift` across threshold boundaries. | **VERIFIED** |
| **No-Leak Guard** | Playout `start` payload must not leak best attack move | Verified in `test_start_does_not_leak_best_attacking_move`: response payload omits `lc0_best_attack` / `best_moves`. | **VERIFIED** |
| **Playout Completion** | Completion at `PLAYOUT_PLIES = 8` or game over | Tested in `test_is_complete_at_target_plies_and_summary`: returns complete flag and summary verdict. | **VERIFIED** |
| **Engine Unavailable** | Return `{"error": "engine_unavailable"}` | Verified in `test_engine_unavailable_returns_error_dict` when `lc0_engine.is_available()` is False. | **VERIFIED** |
| **Input Validation** | Illegal user move yields HTTP 400 | Tested in `test_illegal_user_move_returns_400`. | **VERIFIED** |

---

## Test Suite Execution
- **Playout Unit Test File**: [test_sac_playout.py](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/tests/test_sac_playout.py) — **6 / 6 PASSED**.
- **Full Backend Suite**: **183 / 183 PASSED** (177 pre-existing + 6 new).

---

## Gate Checklist
- [x] Phase C1 backend completed Verbatim.
- [x] Full test suite green (183 tests).
- [x] `metrics.py` UNTOUCHED (`metrics.eval_cp_number` reused).
- [x] No reliance on real engine in unit tests (fully mocked engine).
- [x] No Git push performed.
- [x] **STOP for Leader Review**.
