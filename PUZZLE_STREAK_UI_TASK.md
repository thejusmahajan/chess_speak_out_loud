# WORKER TASK — Puzzle Streak: sub-databases + lichess-style trainer in the UI

Bring the curated lichess puzzle database into the app as a **Puzzle Streak** trainer:
named sub-databases ("sets") filtered by rating band and theme, drilled in
**ascending difficulty** like lichess Puzzle Streak, reshuffled every session.

Backend module + API, then a React panel. **Reuse, do not reinvent** — the two
hardest parts (puzzle mechanics, the board) are already solved in this repo.

**ACCURACY IS NON-NEGOTIABLE.** Work checkpoint by checkpoint. Each checkpoint
has a verification command whose output you must paste into your report before
moving on. If a checkpoint fails, STOP and report — do not "fix forward" into
the next checkpoint. Cite `file:line` for every change. Suite green, no push,
STOP for leader review.

---

## 0. Read first (do not skip)

| File | Why |
|---|---|
| `backend/training/puzzle_regime.py` | **The puzzle mechanics live here.** `puzzle_position()` is the single source of truth for lichess' move convention. |
| `docs/PUZZLE_STORM_REGIME.md` | Why the decks are built the way they are. |
| `frontend/src/components/Training/TrainingBoard.tsx` | The chessground board. Already handles promotion, orientation, legal-move dests. **You will not write board code.** |
| `frontend/src/components/Training/DrillMode.tsx` | The closest existing component. Mirror its structure, state handling, and `applyUci` helper. |
| `frontend/src/api/training.ts` | Where API client functions go. |

### The one thing that will silently break everything

lichess puzzle rows encode the position **before** the opponent's blunder:

- `fen` = position before the blunder
- `moves[0]` = the blunder (must be applied before the user sees anything)
- `moves[1], moves[3], moves[5], …` = **the solver's moves**
- `moves[2], moves[4], …` = the opponent's forced replies

Getting this wrong shifts every puzzle by one ply and *looks plausible* — the
board renders, moves are legal, everything is simply wrong. **Never re-derive
this inline. Always call `puzzle_regime.puzzle_position(row)`.**

### Do NOT touch

`backend/training/metrics.py`, `relational_facts.py`, `attempts.py`,
`puzzle_regime.py` (import from it; do not edit it), `TrainingBoard.tsx`
(use it as-is; if you believe it needs a change, STOP and report).

---

## Checkpoint 1 — Backend module: `backend/training/puzzle_sets.py`

New file. Sets and sessions. Persist under `data/puzzles/regime/`.

```python
def create_set(name: str, min_rating: int = 1500, max_rating: int = 2000,
               themes: list[str] | None = None, size: int = 200,
               min_popularity: int = 80) -> dict
```
Samples from `data/puzzles/puzzles.sqlite` (reuse `puzzle_regime._connect()` and
the query shape in `puzzle_regime._sample`). Writes
`data/puzzles/regime/sets/<slug>.json` via `store._write_json_atomic`.
Returns `{id, name, min_rating, max_rating, themes, size, created}`.
`id` = slugified name (lowercase, non-alphanumerics → `-`). Re-creating an
existing id **overwrites**; that is intended.

```python
def list_sets() -> list[dict]          # metadata only, never the puzzle rows
def get_set(set_id: str) -> dict
def delete_set(set_id: str) -> bool
```

### Streak ordering — the core requirement

```python
def streak_order(puzzles: list[dict], seed: int | None = None) -> list[dict]
```
Puzzles must climb in difficulty while still varying between sessions:

1. Bucket by rating into 50-point bins (1500–1549, 1550–1599, …).
2. Shuffle **within** each bucket using `random.Random(seed)`.
3. Concatenate buckets in **ascending** order.

Result: order differs every session, but rating is non-decreasing across
buckets. **A plain global shuffle is wrong and will fail Checkpoint 2.**

```python
def start_session(set_id: str, seed: int | None = None) -> dict
def get_session(session_id: str) -> dict
def submit_move(session_id: str, uci: str) -> dict
def next_puzzle(session_id: str) -> dict
```

Session state in `data/puzzles/regime/sessions/<session_id>.json`
(`session_id` = `uuid4().hex[:12]`):

```json
{"id": "...", "set_id": "...", "seed": 12345, "index": 0, "ply": 0,
 "streak": 0, "best_streak": 0, "alive": true, "started": "iso",
 "order": ["puzzleId", "..."], "history": []}
```

**`submit_move` semantics** (this is the whole trainer — get it exactly right):

- Load the row, call `puzzle_position(row)`, replay the solver+opponent moves
  already recorded in `session["ply"]` to reach the current board.
- Compare the submitted UCI against the expected solver move.
- **Promotion:** compare full UCI including the promotion suffix (`g2g1q`).
- **Mate exception:** at the *final* solver ply, any move delivering checkmate
  counts as correct even if it differs from the stored solution (lichess does
  this; `puzzle_regime.drill()` already implements the check — mirror it).
- Correct and more solver moves remain → apply the solver move **and** the
  opponent's reply; return `{"correct": true, "solved": false, "fen": <new>,
  "opponent_uci": <uci>, "ply": <new ply>}`.
- Correct and that was the last solver move → `{"correct": true, "solved": true,
  "streak": n+1, ...}`. Increment `streak`, update `best_streak`.
- Wrong → `{"correct": false, "solved": false, "alive": false,
  "solution": [uci, ...], "solution_san": "...", "streak_ended_at": n}`.
  **One mistake ends the run** — that is Puzzle Streak. Set `alive: false`.
- Every attempt also calls `puzzle_regime.record(...)` so failures feed the
  existing SRS/leech machinery. Pass `timed_out=False` (streak mode is untimed).

Return payloads always include `fen` (position the user faces **now**),
`orientation` (`"white"`/`"black"` = side to move), `rating`, `themes`,
`index`, `total`, `streak`, `best_streak`, `alive`, and
`puzzle_url` (`https://lichess.org/training/<id>`).

### ✅ Verification 1 — paste this output

```bash
python -c "
from backend.training import puzzle_sets as ps
s = ps.create_set('band-1500-2000', 1500, 2000, size=120)
print('set:', s)
sess = ps.start_session(s['id'], seed=1)
import json; rows=[ps.get_set(s['id'])]
o = sess['order']
from backend.training.puzzle_sets import _rows_for
rs = _rows_for(o)
ratings = [r['rating'] for r in rs]
buckets = [r//50 for r in ratings]
print('non-decreasing buckets:', all(b1<=b2 for b1,b2 in zip(buckets, buckets[1:])))
print('first 12 ratings:', ratings[:12])
print('last 12 ratings:', ratings[-12:])
a = ps.start_session(s['id'], seed=1)['order']
b = ps.start_session(s['id'], seed=2)['order']
print('reshuffles between sessions:', a != b)
"
```
Must print `non-decreasing buckets: True` and `reshuffles between sessions: True`,
with first ratings near 1500 and last near 2000. (Expose whatever small helper
`_rows_for(ids)` you need for this check.)

---

## Checkpoint 2 — Tests: `backend/tests/test_puzzle_sets.py`

Match the style of `backend/tests/test_salience_pipeline.py`. Required cases:

1. `streak_order` produces non-decreasing rating buckets.
2. `streak_order` with different seeds produces different orders, **and both
   still satisfy case 1**.
3. A full correct playthrough of a known multi-move puzzle solves it and
   increments `streak`.
4. A wrong first move sets `alive: false` and returns the full solution.
5. **Convention guard:** for a fixed puzzle row, assert `puzzle_position()`
   returns the board with the expected side to move and that the first
   expected solver move equals `moves[1]`. This is the regression test for the
   off-by-one-ply trap.
6. Promotion puzzle: submitting `...q` is accepted, bare `...` (no suffix) is not.

Use a **temporary directory** for `sets/` and `sessions/` (monkeypatch the
module's dir constants) — tests must not write into `data/puzzles/regime/`.

### ✅ Verification 2

```bash
python -m pytest backend/tests/test_puzzle_sets.py -v
```
Paste full output. All green, no skips.

---

## Checkpoint 3 — API routes in `backend/app.py`

Follow the existing `/api/training/...` route style exactly (Pydantic request
models, `HTTPException` on bad input). Add:

| Method | Path | Body / returns |
|---|---|---|
| `POST` | `/api/training/puzzles/sets` | `{name, min_rating, max_rating, themes?, size?}` → set metadata |
| `GET` | `/api/training/puzzles/sets` | list of set metadata |
| `DELETE` | `/api/training/puzzles/sets/{set_id}` | `{deleted: bool}` |
| `POST` | `/api/training/puzzles/session` | `{set_id}` → session + first puzzle payload |
| `GET` | `/api/training/puzzles/session/{session_id}` | current puzzle payload |
| `POST` | `/api/training/puzzles/session/{session_id}/move` | `{uci}` → submit_move payload |
| `POST` | `/api/training/puzzles/session/{session_id}/next` | next puzzle payload |

Unknown `set_id`/`session_id` → **404**, not 500.

### ✅ Verification 3

Start the backend per `HOW_TO_RUN.md` (conda env `cszero`), then paste output of:

```bash
curl -s -X POST localhost:8000/api/training/puzzles/sets \
  -H 'Content-Type: application/json' \
  -d '{"name":"Band 1500-2000","min_rating":1500,"max_rating":2000,"size":100}'
curl -s localhost:8000/api/training/puzzles/sets
curl -s -X POST localhost:8000/api/training/puzzles/session \
  -H 'Content-Type: application/json' -d '{"set_id":"band-1500-2000"}'
curl -s localhost:8000/api/training/puzzles/session/DOESNOTEXIST -w '\nHTTP %{http_code}\n'
```
The last one must show `HTTP 404`.

---

## Checkpoint 4 — Frontend

### `frontend/src/api/training.ts`
Append typed client functions for all seven routes. Follow the existing
`export async function` + `if (!res.ok) throw new Error(await res.text())`
pattern. Add a `PuzzlePayload` interface matching the backend payload.

### `frontend/src/components/Training/PuzzleStreak.tsx`
New component. **Mirror `DrillMode.tsx`'s structure.** Requirements:

- Set picker: list existing sets, plus a small form (name, min/max rating
  defaulting to 1500/2000, size) to create one. "Start streak" begins a session.
- Board: `<TrainingBoard fen={...} orientation={...} onMove={...}
  interactive={alive && !resultShown} lastMove={...} />`. **No new board code.**
- `onMove` sends the UCI to `/move`.
  - Correct + not solved → animate the opponent reply in (reuse DrillMode's
    `applyUci` + `setIsAnimating` timing pattern), then wait for the next move.
  - Solved → green flash, brief pause, auto-advance via `/next`.
  - Wrong → red, board goes non-interactive, show the full solution in SAN, the
    lichess link, and **"Streak over — N solved"** with a "New streak" button.
- Header strip: current streak, best streak, puzzle rating, `index+1 / total`,
  and a rating progress bar showing the climb from 1500 → 2000.
- Themes for the current puzzle stay **hidden until it is solved or failed**
  (showing "fork" first is a spoiler).

### Wire into `TrainingTab.tsx`
Add a "Puzzle Streak" entry to the existing mode switcher, following exactly how
the other modes are registered there.

### `frontend/src/components/Training/__tests__/PuzzleStreak.test.tsx`
Mirror `__tests__/UsualSuspects.test.tsx`. Mock the API client. Cover:
1. Renders the set list and starts a session.
2. A correct move advances; streak counter increments.
3. A wrong move ends the run, shows the solution, and disables the board
   (assert `interactive` is false / no further moves accepted).
4. Themes are not in the DOM before the puzzle resolves.

### ✅ Verification 4

```bash
cd frontend && npm test -- --run && npm run lint && npm run build
```
Paste full output. All green.

---

## Checkpoint 5 — Report

Write `PUZZLE_STREAK_UI_REPORT.md` at repo root containing:

1. Every file created/changed with `file:line` citations for the key logic.
2. Pasted output of **all five verifications**.
3. The exact `streak_order` bucketing you implemented, and a printed sample of
   30 consecutive ratings from a real session proving the climb.
4. Anything you could not do, or where you deviated from this spec — **state it
   plainly; do not paper over it.**
5. Any place you were tempted to edit `puzzle_regime.py` or `TrainingBoard.tsx`
   and what you did instead.

**STOP. Do not push. Do not start other work.**

---

## Anti-patterns that will fail review

- Re-implementing the lichess move convention instead of calling `puzzle_position()`.
- A global shuffle instead of bucketed ascending order.
- New board/chessground code instead of `TrainingBoard`.
- Tests that write into `data/puzzles/regime/`.
- Reporting a checkpoint as passing without pasting its command output.
- Silently widening scope (timers, sound, new deck formats). Not this task.
