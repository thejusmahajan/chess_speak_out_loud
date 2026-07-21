# Gemini Task — Pipeline aggregation: by_phase + by_clock blind-rate dimensions

**Model:** Gemini 3.6 Flash (high). **Token budget is not a concern.** Follow
`WORKER_AGENT_COOKBOOK.md` — especially §3.3 (real-data check), §4b (design for
cheap verification via a PURE function), and "each test a REAL guard."

## Context
The Tutor-style ranking (`metrics.weakness_ranking`) currently ranks only
*openings* (the one dimension the profile carries with a blind_rate). This task
makes the diagnosis pipeline also emit **`by_phase`** (opening/middlegame/endgame)
and **`by_clock`** (time-management) blind-rate aggregates into the profile, so
those become rankable dimensions too. This is subtle pipeline logic — the spec
pins every detail; do not improvise.

## Scope / boundaries (hard)
- **Edit** `backend/training/pipeline.py`: add ONE pure module-level function and
  call it from `run_diagnosis`, merging two keys into the `aggregates` dict.
- **Create** `backend/tests/test_phase_clock_agg.py`.
- **Do NOT touch** `backend/training/metrics.py` (leader-owned — `classify_phase`
  is done; **call it, don't modify it**), and do NOT change the finding schema or
  any other module. If you think you need to, STOP and report.

## Pinned facts (do not guess)
- `metrics.classify_phase(board_or_fen) -> "opening" | "middlegame" | "endgame"`
  (already implemented, pure). Call it with a `chess.Board`.
- `pipeline.clock_seconds(comment) -> Optional[float]` (already in this file) —
  seconds left on the mover's clock from a `[%clk]` comment, or `None`.
- `pipeline.is_time_scramble(comment, cfg)` — True when the move was played below
  `cfg.min_clock_seconds` (default 20s). The existing `by_opening` aggregate
  **excludes** time-scramble moves; match that.
- A **finding** dict carries: `game_idx` (int), `ply` (int), `fen_before` (str),
  `severity` (`"blind" | "missed" | ...`). It does NOT carry the clock.
- `games_to_process` is a `list[(chess.pgn.Game, user_color)]` where `user_color`
  is `chess.WHITE`/`chess.BLACK`.
- **PLY CONVENTION (critical):** Stage A sets ply by incrementing at the TOP of the
  mainline loop — `ply = 0` before the loop, `ply += 1` as the first statement
  inside `for node in game.mainline()`. Findings' `ply` uses this. **Your walk MUST
  use the identical convention** so `(game_idx, ply)` keys match the findings. An
  off-by-one here silently yields zero blind matches (all blind_rate = 0) — the
  real-data gate below is what catches it.

## Part A — the pure aggregator (in `pipeline.py`)
```python
def aggregate_phase_clock(games_to_process, findings, cfg=DEFAULT_CONFIG):
    """Pure. Returns (by_phase, by_clock), each
    {bucket: {"moves","blind","missed","blind_rate"}}, computed over the user's
    NON-time-scramble decision nodes (the analyzed population). No engine, no I/O."""
```
Algorithm (implement exactly):
1. `blind_keys = {(f["game_idx"], f["ply"]) for f in findings if f["severity"] == "blind"}`
   and `missed_keys = {... "missed"}`.
2. For each `game_idx, (game, user_color)` in `enumerate(games_to_process)`:
   - `board = game.board()`, `ply = 0`.
   - For `node in game.mainline()`: `ply += 1` FIRST.
     - If `board.turn == user_color and not is_time_scramble(node.comment, cfg)`:
       - `phase = metrics.classify_phase(board)`
       - `bucket = _clock_bucket(clock_seconds(node.comment))`
       - increment `by_phase[phase]["moves"]` and `by_clock[bucket]["moves"]`.
       - if `(game_idx, ply) in blind_keys`: increment both `["blind"]`.
       - if `(game_idx, ply) in missed_keys`: increment both `["missed"]`.
     - `board.push(node.move)`.
3. For every bucket in both dicts: `blind_rate = blind / moves` if `moves > 0` else `0.0`.
4. Return plain dicts (not defaultdicts).

`_clock_bucket(secs)` (module-level helper): `None -> "no_clock"`;
`secs < 60 -> "fast"`; `60 <= secs < 180 -> "normal"`; `secs >= 180 -> "slow"`.
(Scramble moves are already excluded, so "fast" means 20–60s.)

## Part B — wire into `run_diagnosis`
In the aggregation section, after `by_opening`/`by_motif` are built, call:
```python
by_phase, by_clock = aggregate_phase_clock(games_to_process, findings, cfg)
```
and add `"by_phase": by_phase, "by_clock": by_clock` to the `aggregates` dict.
Change nothing else in `run_diagnosis`.

## Part C — tests (`backend/tests/test_phase_clock_agg.py`, pure, no engine)
Each a REAL guard. Build small synthetic games (python-chess) + hand-written
findings; call `aggregate_phase_clock` directly.
1. **Phase bucketing + blind_rate.** A game where the user has, say, 3 opening
   decision moves (1 flagged blind) and 2 middlegame moves (0 blind) → `by_phase`
   has `opening: {moves:3, blind:1, blind_rate:~0.333}` and `middlegame:
   {moves:2, blind:0, blind_rate:0.0}`. Assert the numbers.
2. **Clock bucketing.** Moves annotated with `[%clk 0:00:45]` (fast) / `0:02:00`
   (normal) / `0:05:00` (slow) / no-clock → land in the right `by_clock` buckets.
3. **`(game_idx, ply)` matching is correct (the off-by-one guard).** A finding at a
   specific `(game_idx, ply)` increments blind for exactly the phase/clock of THAT
   node — and mutating the finding's ply by ±1 moves/removes the blind count.
   (Encode this as: the blind lands on the node whose position/clock you expect,
   not a neighbor.)
4. **Time-scramble moves excluded.** A user move with `[%clk 0:00:05]` (below 20s)
   contributes to NEITHER `moves` nor `blind` in any bucket.
5. **Opponent moves ignored.** Only `board.turn == user_color` nodes count.
6. **`missed` counted; empty inputs safe.** `missed` findings increment `["missed"]`;
   empty games or empty findings → all-zero dicts, no error, `blind_rate == 0.0`.

## Part D — REAL-DATA gate (cheap, no engine — this is the point of §4b)
Because the aggregator is pure, run it over the REAL archived data with a throwaway
script (put it in `scratch/`), and paste the output into `WORKLOG_TRAINING.md`:
- Load findings from the archived 693-game profile:
  `data/training/profiles/profile-20260720T095953932767.json` (has 4840 findings
  with `game_idx`/`ply`), and the games from
  `games_of_derdiedasdie/lichess_derdiedasdie_2026-07-19.pgn` (parse with
  `chess.pgn`, pairing each game with `user_color` = whichever side is
  `derdiedasdie`; take the same 693 the profile used — the newest 693, sorted by
  UTCDate/UTCTime, matching `scripts/overnight_run.select_recent_games`). If exact
  pairing is fiddly, it's acceptable to run over all `derdiedasdie` games and note
  it — the point is real, non-degenerate output.
- Call `aggregate_phase_clock(games, findings)` and print `by_phase` and
  `by_clock`. **The output MUST be non-degenerate**: multiple buckets populated,
  non-zero blind counts, sensible rates. **If every `blind` is 0, the ply matching
  is wrong — fix it before submitting.**

## Gate — paste REAL output into `WORKLOG_TRAINING.md`
- `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests/test_phase_clock_agg.py -q` → all pass.
- `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests/ -q` → full suite, ≥ 123 (117 now + your ~6).
- The real-data `by_phase` / `by_clock` printout (Part D), showing non-zero blind counts.

## Not in scope (leader follow-ups)
- Generalizing `weakness_ranking` to rank phases/clock buckets, and any UI — the
  leader will do that on top of these aggregates.
- `conversion` / `resourcefulness` dimensions (need per-move eval trajectories — a
  separate design decision).

Prepend a dated `WORKLOG_TRAINING.md` entry ending with `by_phase/by_clock ready for review`. Modify only `pipeline.py`, the new test, the worklog, and a throwaway `scratch/` script. Await leader sign-off.
