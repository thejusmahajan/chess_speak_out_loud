# GEMINI — GROUNDED TASK: fix the 1,000-game TS2 hang (TDD; no freelancing)

You have been thrashing on this. STOP guessing. This is a tightly-grounded,
test-driven task. Do EXACTLY these steps in order. Do not edit any file not named
here. Do not declare success by reasoning — only by the test objectively passing.

## The symptom (ground truth from the user)
On a ~1,000-game Kaggle (2×T4) run the log froze at ~393 s and made ZERO progress
for ~2 hours. Node-limited searches have a 30 s wall-clock cap, so no single engine
call can hang 2 h — **this is an async-orchestration deadlock/hang in Stage TS2's
parallel code** (`backend/training/pipeline.py`). It appears at 1,000 games but not
30 → it is TRIGGERED BY TRANSPOSITION LOAD (the same positions recur hundreds of
times across many games, exercising the in-flight-future dedup + bounded workers
far more than a 30-game run does).

## Root observation (this is your anchor)
Stage B parallelism uses a SIMPLE pattern — `asyncio.gather` over items + a
semaphore + in-flight-future dedup — and does NOT hang. Stage TS2 uses a
NEEDLESSLY COMPLEX pattern — `node_queue` + fixed `_ts2_worker` pool + `ts2_sem`
+ in-flight futures (FOUR mechanisms). The complexity is the bug surface.

## STEP 1 — Write a FAILING hang-reproduction test FIRST (red)
Create `backend/tests/test_ts2_no_hang.py`. It must:
- Reuse a deterministic engine like `DetEngine` in `test_cache_replay_identity.py`
  BUT add: (a) an `asyncio.sleep` of a few ms in `analyze`/`get_policy_distribution`
  to widen the in-flight race window, and (b) drive HEAVY TRANSPOSITIONS — build a
  synthetic PGN (or reuse test_subset) whose decision nodes produce MANY repeated
  `epd_after` positions across different nodes (e.g. many games sharing the same
  opening so the same candidate positions recur).
- Run `run_diagnosis` with an `EnginePool(4, DetEngine)` under
  `await asyncio.wait_for(run_diagnosis(...), timeout=90)`, store dir monkeypatched
  to tmp, `steer_highlight_complexity=0.0`, high `steer_search_budget`.
- Assert it COMPLETES (no `asyncio.TimeoutError`) and produces steer_findings.
RUN IT against the CURRENT code. If it does NOT reproduce the hang (completes),
you have not made the transposition load heavy enough OR the delay wide enough —
increase both until it either reproduces the hang (times out = red, good, proceed)
OR you have strong evidence the hang is not reproducible locally. If after genuine
effort it will not reproduce, STOP and write your findings to
`QUESTIONS_FOR_LEADER.md` (do NOT proceed to "fix" blind).

## STEP 2 — Fix by SIMPLIFYING TS2 to mirror Stage B's proven pattern
Replace the `node_queue` + `_ts2_worker` + `ts2_lock` + `ts2_sem` machinery with the
SAME shape Stage B uses:
- Bound *node* concurrency with a single `asyncio.Semaphore(concurrency_limit)`
  acquired around each node's processing (so at most `concurrency_limit` nodes are
  in flight — preserves the memory bound the worker pool gave you at 24k nodes).
- Launch all nodes with `asyncio.gather(*[_process_steer_node(i, n) for ...])`.
- Keep the in-flight-EPD-future dedup EXACTLY as Stage B does it (register
  synchronously; owner sets result/exception; `finally` pops).
- **Guarantee no orphaned future on cancellation:** in the `finally` that pops the
  in-flight entry, if the future is not yet done, `fut.cancel()` (or
  set_exception) so any peer awaiting it is released rather than hung. Do this in
  BOTH Stage B and Stage TS2.
- Keep deterministic ordering: collect results, `sort(key=lambda x: x[0])` before
  building the profile.
- Do NOT change the budget helpers (`try_reserve_*`) — they are correct (synchronous).
Delete the now-unused `node_queue`/worker code.

## STEP 3 — Gates (ALL must pass; paste the real output)
1. `test_ts2_no_hang.py` now COMPLETES (was red, now green).
2. `test_cache_replay_identity.py` (the leader's n=1 vs n=4 identity gate) still
   passes — parallelism must NOT change findings/steer_findings.
3. Mutation-check `test_ts2_no_hang`: re-introduce the orphan (make the `finally`
   NOT resolve the pending future) → the hang test must FAIL/timeout again. Restore.
4. Full suite green: `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests/ -q`
   (expect 148+ passed).
Then commit, **push**, confirm origin HEAD == local HEAD, and STOP for leader review.

## Boundaries
- Files you may touch: `backend/training/pipeline.py`,
  `backend/tests/test_ts2_no_hang.py` (new). Nothing else.
- `metrics.py` is leader-owned — forbidden.
- Do not touch the Kaggle notebook/dataset for THIS task; it's a pure backend fix.
- No "it should work now" declarations. The test passes or it doesn't.
