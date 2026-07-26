# Sprint 2 Phase A Report — LC0 Intuition Speed-Drill Backend & Math

## Summary of Implementation
Sprint 2 Phase A introduces the backend logic and API endpoints for the **LC0 Intuition Speed-Drill (Jobs 4 + 5)**. The drill runs exclusively on cached LC0 policy evaluations (`store.EpdCache("policy")`) without calling the live engine.

### 1. `store.EpdCache.keys()` Addition ([store.py:45-46](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/store.py#L45-L46))
- Added `keys(self) -> List[str]` to `EpdCache` returning `list(self._data.keys())`.

### 2. Backend Module ([backend/training/intuition.py](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/intuition.py))
- **Module Constants**:
  - `NEAR_FORCED_THRESHOLD = 0.9`
  - `REVEAL_TOP_K = 5`
- **`build_session(count: int)`**:
  - Filters positions where `len(policy) >= 2` AND `policy[0]["p"] < 0.9` (excluding near-forced moves and single-move positions).
  - Uniform-randomly samples `count` eligible EPDs (without repeats within a session).
  - Returns `[{"epd", "fen"}]` ONLY — keeping policy and solution moves **strictly server-side**.
- **`score_guess(epd: str, uci: str)`**:
  - Computes exact top-1 match (`correct = (uci == top_uci)`).
  - Computes 1-based `rank` of guessed move in policy (`None` if move is not in LC0's top 20).
  - Returns `your_move` (`uci`, `san`, `p`), `top_move` (`uci`, `san`, `p`), and `top_policy` (top 5 choices).
  - Logs attempt atomically to `training/intuition_attempts.jsonl` (`{epd, uci, correct, rank, ts}`).
- **`get_stats()`**:
  - Reads `training/intuition_attempts.jsonl` and returns `total`, `correct`, `accuracy` (`correct / total`), and `recent_accuracy` (last 50 guesses).

### 3. REST API Endpoints ([backend/app.py:774-790](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/app.py#L774-L790))
- `POST /api/training/intuition/session` body `{count: int = 10}` -> `build_session(count)`
- `POST /api/training/intuition/guess` body `{epd: str, uci: str}` -> `score_guess(epd, uci)`
- `GET /api/training/intuition/stats` -> `get_stats()`

### 4. Unit Tests ([backend/tests/test_intuition.py](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/tests/test_intuition.py))
Added 6 comprehensive unit and integration tests (mutation-check mindset):
1. `test_epd_cache_keys`: Verifies `EpdCache.keys()` returns all cached EPD keys.
2. `test_sampling_filters_forced_and_single`: Verifies positions with `p >= 0.9` or `len(policy) < 2` are excluded.
3. `test_build_session_does_not_leak_answers`: Verifies `build_session` returns `epd` and `fen` ONLY (zero policy/solution leakage).
4. `test_score_guess_top1_match_and_rank`: Verifies top-1 scoring, 1-based rank, and off-list move handling (`rank=None`, `your_move=None`).
5. `test_stats_accuracy_logging`: Verifies `get_stats()` accuracy math over logged attempt sequences.
6. `test_api_endpoints_integration`: Verifies FastAPI routes `/session`, `/guess`, and `/stats`.

## Verification Results
- **Pytest Test Suite (`pytest backend/tests`)**: **171 / 171 passed** (165 original + 6 new).
- **TypeScript & Vite Build (`npm run build`)**: Clean build.
- **Metrics Contract**: `backend/training/metrics.py` untouched.
- **Git Push**: Zero pushes performed.
