# MISSION: Full A100 utilization, zero quality compromise (~20% credits left)

**Leader:** Fable 5 (budget-limited — escalate only through the gates below).
**Workers:** Gemini 3.6 Flash High (implementer, large token pool) · Claude Opus 4.6
(verifier, small token pool — short, surgical review passes only).
**Prime directive:** the remaining A100 credits (~20%) are nearly gone. **Nothing
runs on the A100 until it is proven locally.** Every change traces to this file.
The guiding principle of `GEMINI_HANDOFF.md` (anchor in detail, never guess, prove
by mutation, push after commit, regenerate the ipynb after any .py edit) remains law.

---

## 0. The engineering truth (recalibrate the success metric)

The A100 idles because **one lc0 process runs one latency-bound MCTS search at a
time**. The fix that fills the machine **without touching any eval** is
**parallelism across positions**: the pipeline's Stage B pairs and TS2 candidates
are independent positions — embarrassingly parallel. N lc0 workers, same net, same
node limits, same settings → **identical evals, N× throughput, N× more work per
credit.**

**Success metric = sustained GPU utilization % and games/hour — NOT GB of RAM.**
8 workers will use ~15–20 GB of the 80 GB; that is full *compute* saturation.
Watching RAM fill to 80 GB is the wrong meter (that's corpus-scale caching, later).
Do not "optimize" toward a RAM number.

Confirmed feasible: each `LC0Engine` owns its **own event-loop thread + own lock**
(`engine_manager.py:82,96`), so N instances already run truly concurrent searches.

---

## Phase A (Gemini · LOCAL CPU · zero credits) — `EnginePool`

New file `backend/engine_pool.py`:

```python
class EnginePool:
    """N LC0Engine workers behind the same duck-type interface as one engine.
    N=1 (default) must be byte-for-byte the behavior of a single LC0Engine."""
    def __init__(self, n: int, engine_factory):        # factory() -> LC0Engine
    async def start(self): ...                         # start all workers
    async def stop(self): ...                          # stop all workers
    # Same signatures as LC0Engine so pipeline code takes either object:
    async def analyze(self, fen, depth=None, multipv=1, time_limit=None, nodes=None)
    async def get_policy_distribution(self, fen, nodes=1)
    def is_available(self) -> bool                     # True if any worker is
```

**Pinned mechanics:** an `asyncio.Queue` holding the N engine objects. Each call:
`eng = await q.get()` → `try: return await eng.<method>(...)` → `finally: q.put_nowait(eng)`.
No new locks, no threads of your own — the engines already own their loops.
`n` comes from env `LC0_WORKERS` where the notebook constructs the pool (default 1).

**Tests (`backend/tests/test_engine_pool.py`, fake engines, mutation-checked):**
1. 10 concurrent `analyze` via `asyncio.gather` on a 3-worker pool → all correct
   results, and **observed max concurrency == 3** (fakes record enter/exit counts).
2. Results map to the right FENs (fakes echo the fen back) — no cross-wiring.
3. Mutation: delete the `finally` release → test must fail (guard with
   `asyncio.wait_for` timeout, never hang the suite).
4. n=1 pool passes an existing-behavior test (delegates transparently).

---

## Phase B (Gemini · LOCAL CPU · zero credits) — parallelize the two hot loops

Refactor **Stage B** (per flagged move) and **TS2** (per node's candidates) in
`backend/training/pipeline.py` to bounded-concurrency `asyncio.gather`
(bound = pool size, from `getattr(engine, "n", 1)` — sequential engines keep bound 1
and the code path is then equivalent to today).

**Pinned concurrency traps — these are the whole task, get each one right:**
1. **Budget reservation is synchronous.** `search_used`/`bt3_budget_remaining`
   check-AND-increment must happen with **no `await` between check and increment**
   (asyncio is single-threaded; an await between them is the race). Reserve first,
   then await the engine, refund on failure.
2. **Dedupe in-flight EPDs.** Two concurrent tasks may want the same position.
   Keep `in_flight: dict[epd, asyncio.Future]`; second requester awaits the first's
   future instead of re-searching (this also protects cache-append duplication).
3. **Deterministic output order.** Collect results, then sort findings by
   `(game_idx, ply)` and steer candidates by their policy order **before** building
   the profile — output must not depend on completion order.
4. **Budget exhaustion semantics:** once exhausted, schedule no new work; let
   in-flight tasks finish; set `steer_budget_exhausted=True` exactly as today.
5. Progress counts (`stage_b_done`, `steer_processed`, pbars) increment on task
   completion — totals must still match.

**Local gates (all zero-credit):**
- Full suite green (`cszero` python, currently 141 passed + skips).
- **Cache-replay identity gate (the quality proof):** copy the last Colab run's
  `data/training/cache/*.jsonl` into place and run the pipeline locally on
  `test_subset.pgn` — everything hits cache, near-zero engine calls. The produced
  `findings` and `steer_findings` must be **identical (count and ids)** between
  (a) HEAD before this refactor and (b) after, at `LC0_WORKERS=1` **and** `=4`.
  Any diff = a concurrency bug. This gate is non-negotiable.
- Mutation-check trap #1 (insert an await between check/increment in a copy → a
  budget-overrun test must catch it) and trap #3 (shuffle completion → same output).

Commit **and push** each phase; regenerate + push the ipynb with any notebook edit.

---

## Phase C (Opus 4.6 · LOCAL · small budget) — independent verification

Prompt Opus with ONLY: the two diffs, this file's Phase A/B trap list, and ask for:
(1) line-cited confirmation each trap is handled, (2) re-run of the cache-replay
identity gate, (3) one attempted counter-example (a scenario that would break
ordering or budgets). No restyling, no scope. If it flags a real hole → back to
Gemini with the finding. Keep the whole exchange short; its tokens are scarce.

## Phase D (user + Fable · COLAB · the credits) — the run protocol

Credits are the constraint. **A100 ≈ 6× the unit burn of a T4** — so rehearse cheap:
1. **Dress rehearsal on a T4** (cheap units): fresh runtime, confirm Cell 3 hash,
   `LC0_WORKERS=4`, run cells 1→5c + DIAGNOSIS only (3 games). Success = completes,
   findings sane, and a background `nvidia-smi --loop=10` cell shows **sustained
   high GPU util** with 4 workers. Any bug found here costs pennies.
2. **THE A100 run (one shot):** `LC0_WORKERS=8`, per-worker `Threads=2` (Colab has
   ~12 vCPUs — 8×4 threads would thrash), `STEER_SEARCH_BUDGET=50000`,
   `LC0_NN_CACHE_SIZE=5000000`, `LC0_RAM_LIMIT_MB=30000`, `BT3_BUDGET="high"`.
   Run subset cells 1→9. Watch the first 3 games' pace; if per-game time × 30 fits
   comfortably in the remaining credit window, optionally extend the game count —
   otherwise finish the subset, download the zip, **stop the runtime immediately.**
3. Deliverables: complete profile (openings + 100% steering), the measured
   games/hour at N=8 vs the old sequential pace, and GPU util evidence.

Notebook wiring (Gemini, part of Phase B): Cell 5 builds
`EnginePool(int(os.environ.get("LC0_WORKERS","1")), factory)` when >1 else the
single engine; env knobs set in a clearly-marked block; ipynb regenerated + pushed.

---

## Hard rules recap
- No A100 minute before Phases A–C are green. T4 before A100. Stop runtimes when done.
- `metrics.py` untouched. Evals must be bit-equivalent per position (same net,
  nodes, options) — parallelism only changes *when*, never *what*.
- Anything ambiguous → `QUESTIONS_FOR_LEADER.md`, never a guess.
