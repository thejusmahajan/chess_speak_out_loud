# TASK FOR GEMINI — Second pre-run review: the 2-worker GPU-split run (REPORT ONLY)

Second-eye audit before we spend another Kaggle run on the 2-worker (GPU-split)
diagnosis. Your first review (`KAGGLE_RUN_REVIEW.md`) caught real blockers — do the same
here. **Report only.** No code edits, run nothing. Output ONE md file,
`KAGGLE_RUN_REVIEW_2.md`, at the repo root. The leader (Claude) audits your findings
line-by-line and decides GO / NO-GO. Cite `file:line` + quote evidence for everything;
a confident "looks good" with no citations is worthless.

## Where we are (verified)
- **Milestone already hit** at LC0_WORKERS=1: `[DONE] REAL run: 213 findings, 263
  steer_findings | vision=attention | games=30 moves=880 | 9352s`. **That is the baseline.**
- TS2 = ~85% of that 2h36m, serial on GPU0 → the bottleneck we're parallelizing.
- Prior blockers fixed (weights-dir dig+normalize, onnx copy to writable dir, CSZERO_DATA_DIR,
  honest-[DONE] profile assert). See `KAGGLE_RUN_REVIEW.md`.
- **The last 2-worker attempt failed two ways:** (a) lc0 IGNORED UCI `BackendOptions="gpu=N"`
  → both engines on GPU0, VRAM ~14.8/15.3 GiB, "Not enough GPU memory to capture CUDA
  graphs"; (b) `TypeError: LC0Engine.__init__() got an unexpected keyword argument 'gpu_id'`
  — because the backend is imported FROM THE DATASET (an OLDER snapshot without gpu_id).
- **Current fix (the thing to review hardest):** GPU pinning is now done ENTIRELY in the
  diagnostic — `_factory` passes NO gpu_id; `_start_engines()` starts pool workers SERIALLY,
  setting `os.environ["CUDA_VISIBLE_DEVICES"]=<i>` right before each worker's subprocess
  spawns, then restoring the env.

## Read these (CURRENT repo state)
- `colab/kaggle_diagnostic_run.py` — the instrument (all logic lives here).
- `backend/engine_pool.py`, `backend/engine_manager.py`, `backend/neural_vision.py`,
  `backend/training/pipeline.py`, `backend/training/store.py`.
- `LEADER_BIBLE.md` (§4 decisions, §5 failure catalog, §5b Kaggle family) and
  `KAGGLE_RUN_REVIEW.md` (your prior review).
- **`metrics.py` is leader-owned, READ-ONLY** — route concerns to `QUESTIONS_FOR_LEADER.md`.

## Environment facts (ground truth)
- Kaggle T4×2 (sm_75), ~30 GiB RAM, 4 vCPUs, each GPU ~15 GiB VRAM. `/kaggle/input`
  READ-ONLY; `/kaggle/working` writable, wiped on Stop/Start.
- **CRITICAL:** the diagnostic runs by being PASTED into a Kaggle cell, and it imports
  `backend.*` FROM THE DATASET (`/kaggle/input/.../backend/`), which is an OLDER snapshot
  than this repo. So repo-side backend edits DO NOT reach Kaggle — only the pasted
  diagnostic does. This is why the gpu_id fix had to live in the diagnostic.

## Review buckets (ranked by how badly each has bitten us)

### A. STALE-BACKEND SIGNATURE DRIFT  ← HIGHEST VALUE
The `gpu_id` TypeError was ONE instance. Find EVERY call the diagnostic makes into
backend and flag any that depend on RECENTLY-ADDED backend API (a kwarg, method, or
attribute) that an OLDER dataset copy might not have. Use `git log -p --since=...` /
`git log --oneline backend/` to see what changed recently, and cross-check against what
the diagnostic uses. At minimum check:
- `LC0Engine(...)` args used by `_factory` (must be only long-stable ones now).
- `EnginePool(...)` construction AND the diagnostic reaching into `engine._workers` —
  is `_workers` present in the dataset's EnginePool? Is that attribute access safe/robust?
- `NeuralVision`, `saliency*`, `evaluate*` methods the diagnostic or pipeline call.
- `pipeline.run_diagnosis(...)` signature and `pipeline._progress` keys the `_tap` monkey
  patch reads (`stage_a_done`/`stage_b_done`/`stage_steer_done`).
- `store.TRAINING_DIR`, `store.read_job`, profile schema keys the honest-[DONE] reads
  (`findings`, `steer_findings`, `games_analyzed`, `moves_analyzed`).
For each: is it OLD/stable (safe) or RECENT (risk)? If recent, that's a BLOCKER.

### B. The CUDA_VISIBLE_DEVICES serial-start (`_start_engines`)
- Does a subprocess spawned by `chess.engine.popen_uci` (→ `subprocess_exec`, env=None)
  actually INHERIT the parent's `os.environ["CUDA_VISIBLE_DEVICES"]` at spawn time?
- The engine spawns on a DEDICATED event-loop THREAD (`_submit`/`_start_impl`). Does
  `await w.start()` fully complete the spawn before returning, so SERIAL setting is
  race-free? Any window where two workers read the env?
- Restoring/removing the env after starting: does it affect already-spawned children
  (it must not) or the parent's already-initialized torch vision on GPU0?
- n=1 path: confirm it still starts with NO CUDA_VISIBLE_DEVICES override → GPU0 →
  byte-identical to the 213/263 baseline.

### C. Identity (correctness gate)
Position-level parallelism must not change ANY eval. Trace whether 2 workers can produce
counts DIFFERENT from 213/263 (e.g., ordering-dependent aggregation, shared mutable state
in EpdCache across workers, nondeterminism from GPU device). If any such risk exists, name
it — the run must reproduce 213/263 exactly.

### D. Memory / OOM at 2 workers
Last run OOM-pressured GPU0 (both engines there). With worker1 now on GPU1, does GPU0
drop to a safe margin? Any host-RAM risk (2 lc0 + torch on ~30 GiB)? Is the onnx vision
model (on GPU0) + worker0 within GPU0's 15 GiB?

### E. lc0 compile fallback (user requirement)
Confirm `get_linux_lc0()` ALWAYS falls back to compiling when no cached binary is found
or a cached one fails `_lc0_runs()`, and NEVER hard-fails on "not found". Confirm the
`assert LC0_BIN` can only trip on a failed COMPILE, not a cache miss.

### F. Anything else that crashes or hangs before `[DONE]`.

## Output — `KAGGLE_RUN_REVIEW_2.md`
1. Findings table: `ID | Severity (BLOCKER/CORRECTNESS/PERF/COSMETIC) | file:line | Problem
   | Evidence (quoted line) | Proposed fix (describe, don't apply)`. BLOCKER = will crash or
   yield wrong/inconsistent results on the 2-worker/30-game run.
2. A dedicated **stale-backend drift table** (bucket A): each diagnostic→backend call →
   OLD/stable or RECENT/risk → verdict.
3. NEEDS-CHECK list.
4. Bottom line: GO / NO-GO + the exact blockers to clear.

## Constraints
- Report only; cite file:line and quote evidence; label speculation; NEEDS-CHECK when unsure.
- Don't touch `metrics.py`. STOP when the md is written.
