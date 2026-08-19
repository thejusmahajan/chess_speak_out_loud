# Sprint 3 Phase A Report — Sacrifice / Tactical-Landmine Training Backend & Math

## Summary of Implementation
Sprint 3 Phase A introduces the backend logic and REST API endpoints for **Sacrifice / Tactical-Landmine Training (Jobs 1 + 7)**. The module selects Tal-style sacrifice positions discovered by LC0 in the user's own games from cached `steer_findings` without calling the live engine or external APIs.

### 1. Backend Module ([backend/training/sac_drill.py](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/sac_drill.py))
- **Selection & Filtering (`_get_tal_findings`)**:
  - Filters profile `steer_findings` where `had_tal_move == True`.
  - Ranks findings by `steer.complexity` DESC (sharpest positions first).
  - Deduplicates by canonical board EPD (`chess.Board(fen).epd()`).
- **`build_sac_session(count: int)`**:
  - Uniform-randomly samples up to `count` eligible positions.
  - Returns `[{"id", "fen"}]` ONLY — keeping sac move, safe move, evals, and candidate moves **strictly server-side**.
- **`score_sac_guess(finding_id: str, uci: str)`**:
  - Scores exact sac match (`correct = (uci == sac_uci)`).
  - Scores sound alternatives (`acceptable = (uci in playable_candidates and not correct)`).
  - Computes soundness comparison: `sac_move` (`uci`, `san`, `eval_cp`, `complexity`), `safe_move` (`san`, `eval_cp`), `eval_loss_cp`, and `playable_candidates`.
  - Atomically logs attempt to `training/sac_attempts.jsonl` (`{finding_id, uci, correct, acceptable, ts}`).
- **`get_stats()`**:
  - Calculates `total`, `correct`, `acceptable`, `accuracy` (`correct / total`), and `recent_accuracy` (last 50 guesses).

### 2. REST API Endpoints ([backend/app.py:808-825](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/app.py#L808-L825))
- `POST /api/training/sac/session` body `{count: int = 10}` -> `build_sac_session(count)`
- `POST /api/training/sac/guess` body `{finding_id: str, uci: str}` -> `score_sac_guess(finding_id, uci)` (404 if finding not found)
- `GET /api/training/sac/stats` -> `get_stats()`

### 3. Unit Tests ([backend/tests/test_sac_drill.py](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/tests/test_sac_drill.py))
Added 6 comprehensive unit and integration tests (mutation-check mindset):
1. `test_selection_filters_had_tal_move_and_dedupes`: Verifies selection filters `had_tal_move=True` and dedupes by board EPD.
2. `test_session_payload_no_answers_leaked`: Verifies session payload returns `id` and `fen` ONLY (zero answer/eval leakage).
3. `test_score_sac_guess_correct_and_acceptable`: Verifies `correct=True` for sac move, `acceptable=True` for sound alt, and `false` for miss.
4. `test_unknown_finding_id_returns_empty`: Verifies unknown `finding_id` returns empty `{}` (which yields HTTP 404).
5. `test_stats_accuracy_logging`: Verifies `get_stats()` accuracy and acceptable tracking over logged attempt sequences.
6. `test_api_endpoints_integration`: Verifies FastAPI routes `/session`, `/guess`, `/stats`, and 404 error handling.

## Verification Results
- **Pytest Test Suite (`pytest backend/tests`)**: **177 / 177 passed** (171 previous + 6 new).
- **TypeScript & Vite Build (`npm run build`)**: Clean build.
- **Metrics Contract**: `backend/training/metrics.py` untouched.
- **Git Push**: Zero pushes performed.
