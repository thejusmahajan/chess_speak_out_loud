# KAGGLE DIAGNOSIS SECOND PRE-RUN REVIEW — 2-Worker GPU-Split Audit

**Author**: Gemini 3.6 Flash (High)  
**Date**: 2026-07-25  
**Target Execution**: Kaggle (2×T4 GPUs sm_75, 30 GB RAM, 4 vCPUs, 15.3 GB VRAM per GPU, `/kaggle/input` READ-ONLY)  
**Target Configuration**: `LC0_WORKERS=2`, `MAX_GAMES=30`, `LC0_BACKEND="cuda-fp16"`  
**Verdict**: **GO** (All prior blockers F-01..F-06 verified resolved; zero new BLOCKER or CORRECTNESS defects found)

---

## 1. Findings Table

| ID | Severity | File : Line | Problem Summary | Evidence (exact code quote) | Proposed Fix (Description) |
|---|---|---|---|---|---|
| **F2-01** | **COSMETIC** | `colab/kaggle_diagnostic_run.py:378-388` | `_start_engines()` lacks a `try...finally` block around `CUDA_VISIBLE_DEVICES` environment restoration. If `w.start()` raises an exception during iteration `i` (e.g. binary missing library), `os.environ["CUDA_VISIBLE_DEVICES"]` remains set to `str(g)` in the parent process. | `for i, w in enumerate(engine._workers):\n    g = i % max(gpu_count, 1)\n    os.environ["CUDA_VISIBLE_DEVICES"] = str(g)\n    print(f"[pool] starting worker {i} -> GPU {g} (CUDA_VISIBLE_DEVICES={g})", flush=True)\n    await w.start()` | Wrap the worker startup loop in a `try...finally` block so `CUDA_VISIBLE_DEVICES` is restored even if a worker fails to start. (Non-fatal, script aborts on exception anyway). |

---

## 2. Dedicated Stale-Backend Drift Table (Bucket A)

Every interaction between `colab/kaggle_diagnostic_run.py` and the `backend` package (imported from the dataset under `/kaggle/input/.../backend/`) has been audited for signature, argument, method, and attribute drift.

| Diagnostic -> Backend Interaction | Location in `kaggle_diagnostic_run.py` | Target in `backend/` | Dataset Status | Verdict & Analysis |
|---|---|---|---|---|
| `LC0Engine(LC0_BIN, SEARCH_WEIGHTS)` | line 339: `return LC0Engine(LC0_BIN, SEARCH_WEIGHTS)` | `backend/engine_manager.py:61`: `__init__(self, engine_path=..., weights_path=..., custom_uci_options=..., gpu_id=...)` | **OLD / stable** | **SAFE**. Uses positional args 1 & 2 (`engine_path`, `weights_path`) present since initial `LC0Engine` implementation. `_factory` passes no `gpu_id` or `custom_uci_options` kwargs, preventing the `TypeError` seen in the prior run. |
| `EnginePool(LC0_WORKERS, _factory)` | line 341: `engine = EnginePool(LC0_WORKERS, _factory)` | `backend/engine_pool.py:20`: `__init__(self, n: int, engine_factory: Callable[[], Any])` | **OLD / stable in dataset** | **SAFE**. Passed positional args `(LC0_WORKERS, _factory)` matching expected `(n, engine_factory)`. Present in dataset from commit `55c1214`. |
| `engine._workers` attribute access | line 380: `for i, w in enumerate(engine._workers):` | `backend/engine_pool.py:24`: `self._workers: list = [engine_factory() for _ in range(n)]` | **OLD / stable in dataset** | **SAFE**. `_workers` is initialized in `EnginePool.__init__` at line 24. Accessing `engine._workers` to start workers serially is valid and safe. |
| `NeuralVision(onnx_path=ONNX)` | line 347: `vision = NeuralVision(onnx_path=ONNX)` | `backend/neural_vision.py:14`: `__init__(self, onnx_path: str)` | **OLD / stable** | **SAFE**. Keyword argument `onnx_path` matches signature. Reads `vision.mode` attribute (line 348, line 401), which is initialized to `"attention"` or `"policy_fallback"`. |
| `pipeline.run_diagnosis(...)` call | line 396: `await pipeline.run_diagnosis("kaggle_diag", pgn_text, "derdiedasdie", engine, vision)` | `backend/training/pipeline.py:134`: `async def run_diagnosis(job_id: str, pgn_text: str, player_name: str, engine, vision)` | **OLD / stable** | **SAFE**. 5 positional arguments passed match the exact signature `(job_id, pgn_text, player_name, engine, vision)`. |
| `pipeline._progress` monkey-patch | line 358-368: `_orig_progress = pipeline._progress`, `pipeline._progress = _tap` | `backend/training/pipeline.py:125`: `def _progress(job_id: str, **prog)` | **OLD / stable** | **SAFE**. `_tap` reads kwargs `stage_a_done`, `stage_b_done`, and `stage_steer_done`. `pipeline.py` emits these exact kwarg names at lines 256, 382, 452, 595. |
| `store.TRAINING_DIR` read | line 403: `_pp = os.path.join(_store.TRAINING_DIR, "profile.json")` | `backend/training/store.py:11`: `TRAINING_DIR = os.path.join(DATA_DIR, "training")` | **OLD / stable** | **SAFE**. `TRAINING_DIR` is a module-level constant in `store.py`. Respects `CSZERO_DATA_DIR` env set at line 38 (`/kaggle/working/data`). |
| `profile.json` schema validation | line 407-412: `_prof.get("findings")`, `_prof.get("steer_findings")`, `_prof.get("games_analyzed")`, `_prof.get("moves_analyzed")` | `backend/training/pipeline.py:685-697`: `profile = {"findings": ..., "steer_findings": ..., "games_analyzed": ..., "moves_analyzed": ...}` | **OLD / stable** | **SAFE**. Keys populated by `pipeline.py` match honest-[DONE] assertions in `kaggle_diagnostic_run.py`. |

---

## 3. Technical Bucket Audits

### Bucket B: `CUDA_VISIBLE_DEVICES` Serial-Start Audit (`_start_engines`)
- **Subprocess Env Inheritance**: `LC0Engine._start_impl()` (line 201) calls `chess.engine.popen_uci(cmd, **popen_kwargs)`. Because `_factory()` creates `LC0Engine` with `gpu_id=None`, `popen_kwargs` is `{}`. `popen_uci` delegates to Python's `asyncio.subprocess` with `env=None`, which inherits `os.environ` from the parent process at the time of process creation (`CreateProcess`/`execve`).
- **Race-Free Serial Spawn**: In `kaggle_diagnostic_run.py:372-390`:
  ```python
  async def _start_engines():
      if isinstance(engine, EnginePool):
          _saved = os.environ.get("CUDA_VISIBLE_DEVICES")
          for i, w in enumerate(engine._workers):
              g = i % max(gpu_count, 1)
              os.environ["CUDA_VISIBLE_DEVICES"] = str(g)
              print(f"[pool] starting worker {i} -> GPU {g} (CUDA_VISIBLE_DEVICES={g})", flush=True)
              await w.start()
  ```
  `await w.start()` suspends the main event loop until worker `w`'s dedicated loop thread finishes `_start_impl()` (spawning the `lc0` subprocess via `popen_uci` and sending UCI setup commands). Because the main loop awaits `w.start()` before continuing the `for` loop to worker `i+1`, worker `i`'s `lc0` subprocess is fully spawned while `CUDA_VISIBLE_DEVICES` is set to `str(g)`. No race condition exists between workers.
- **Restoring Environment**: Restoring `CUDA_VISIBLE_DEVICES` (lines 385-388) after all workers start has zero effect on already-spawned child processes (their OS environment block is fixed at spawn time).
- **PyTorch Isolation**: `NeuralVision(onnx_path=ONNX)` is instantiated at line 347 *before* `_main()` calls `_start_engines()`. PyTorch initializes its CUDA context on physical GPU 0 (`cuda:0`). Restoring `CUDA_VISIBLE_DEVICES` at the end of `_start_engines()` ensures PyTorch context on GPU 0 remains uncorrupted.
- **n=1 Path Verification**: When `LC0_WORKERS=1`, `engine` is an `LC0Engine` instance. `isinstance(engine, EnginePool)` is False, executing `elif hasattr(engine, "start"): await engine.start()` without modifying `CUDA_VISIBLE_DEVICES`. `lc0` starts on GPU 0, byte-identical to the baseline.

### Bucket C: Identity Gate (1-Worker vs 2-Worker Parity)
- **Node-Limited Search Parity**: `pipeline.py` uses node-limited searches (`nodes=30` in Stage B, `nodes=1` in Stage A policy screen). Search depth and MCTS node evaluation in LC0 are deterministic with respect to node count.
- **Position-Level Parallelism**: `EnginePool` distributes independent EPD position queries to available worker engines via `asyncio.Queue`.
- **Deterministic Aggregation**: In `pipeline.py`, results from concurrent `asyncio.gather` tasks in Stage B (lines 386-387) and Stage TS2 (lines 600-601) are sorted by original positional index `i`:
  - `b_results.sort(key=lambda x: x[0])`
  - `ts2_results.sort(key=lambda x: x[0])`
  This guarantees `findings` and `steer_findings` are populated in exact sequential order.
- **Deduplication Futures**: EPD caches (`EpdCache("stage_b")`, `EpdCache("steer")`) use `in_flight_b` (line 283) and `in_flight_steer` (line 409) futures maps to prevent duplicate evaluations while allowing concurrent workers to safely await in-flight results.
- **Parity Assertion**: A 2-worker run MUST yield **213 findings** and **263 steer_findings**, matching the 1-worker baseline exactly.

### Bucket D: Memory / VRAM & Host RAM Audit
- **GPU 0 VRAM**:
  - PyTorch `NeuralVision` (BT3 ONNX model + `lczerolens`): ~1.2 GiB VRAM.
  - LC0 Worker 0 (`cuda-fp16` backend, `NNCacheSize=500000`, CUDA context): ~4.0 GiB VRAM.
  - Total GPU 0 VRAM: **~5.2 GiB** / 15.3 GiB VRAM (**~34% utilization**, safe headroom).
- **GPU 1 VRAM**:
  - LC0 Worker 1 (`cuda-fp16` backend, `NNCacheSize=500000`, CUDA context): **~4.0 GiB** / 15.3 GiB VRAM (**~26% utilization**, safe headroom).
  - *Contrast with prior run*: Both workers on GPU 0 caused >10 GiB VRAM contention and failed CUDA graphs allocation. GPU-split cuts GPU 0 pressure in half.
- **Host RAM**:
  - `LC0_RAM_LIMIT_MB` is defaulted to `"4096"` (4 GiB per LC0 worker cache cap).
  - 2 LC0 worker processes: max 2 × 4 GiB = 8.0 GiB RAM.
  - Python process (PyTorch, dataset, PGN, EpdCache): ~3.5 GiB RAM.
  - Total Host RAM: **~11.5 GiB** / 30.0 GiB RAM (**~38% utilization**, 18.5 GiB headroom).

### Bucket E: `lc0` Compile Fallback Audit
- **Validation Cascade**: `get_linux_lc0()` (`colab/kaggle_diagnostic_run.py:159-199`) checks in sequence:
  1. `WORKING / "engine" / "lc0"`
  2. Dataset search `/kaggle/input/**/lc0`
  3. System `PATH` (`shutil.which("lc0")`)
- **Execution Validation**: Each candidate binary is validated via `_lc0_runs(path)` (`line 147`), running `[path, "--help"]` with `stdin=subprocess.DEVNULL` and `timeout=30`. If execution fails (e.g. incompatible CUDA/glibc libraries from an older Kaggle image), it is skipped.
- **Compilation Fallback**: If no candidate binary passes validation, control flow reaches line 186 (`print("[lc0] compiling from source...")`). It installs dependencies (`meson`, `ninja-build`), clones `https://github.com/LeelaChessZero/lc0.git`, and builds via `ninja -j2`.
- **Assert Mechanics**: `LC0_BIN = get_linux_lc0()` followed by `assert LC0_BIN` (line 314) can ONLY trip if compilation raises an unhandled exception or returns empty. It NEVER hard-fails on a cache miss.

### Bucket F: Failure & Crash Prevention Sweep
- **ONNX Temp Path Fix (F-01)**: `kaggle_diagnostic_run.py:297-308` copies `bt3.onnx` from `/kaggle/input` to `/kaggle/working/engine/bt3.onnx`. When `NeuralVision` initializes, `Path(onnx_path).parent` points to `/kaggle/working/engine`, which is writable. `tempfile.mkstemp` succeeds without `Errno 30 Read-only file system` errors.
- **Honest-[DONE] Assertion (F-02)**: `kaggle_diagnostic_run.py:403-413` asserts that `profile.json` exists and `findings > 0` before printing `[DONE] REAL run...`. If `run_diagnosis` internal exception swallowing occurs, the assertion fails loud instead of reporting false completion.
- **Weights Prioritization (F-03)**: `_find_weights()` (lines 233-234) checks `BT3-768x15x24h-swa-2790000.pb.gz` and `BT3-768x15x24h-swa-2790000.pb` BEFORE any `791556` network, preventing silent fallback to the wrong search net.
- **RAM Cap Default (F-04)**: `os.environ.setdefault("LC0_RAM_LIMIT_MB", "4096")` (line 33) keeps host RAM capped safely under 12 GiB.
- **Kaggle Directory Resolver (F-05)**: `_resolve_weight_file()` (line 208) handles Kaggle-extracted directories (`.pb` extracted into a directory named `X.pb`) by resolving to the largest inner file.
- **Worker GPU Pinning (F-06)**: `_start_engines()` isolates worker processes to separate physical GPUs using `CUDA_VISIBLE_DEVICES`.

---

## 4. NEEDS-CHECK List

1. **Dataset Version Attachment**: Ensure the Kaggle notebook cell is attached to the newly created dataset containing `cszero_kaggle_data.zip` (built 2026-07-25), which includes the updated `backend/` package, `bt3.onnx`, weights, and PGN files.
2. **Notebook Internet Access**: Internet toggle in the Kaggle notebook settings must be **ON** if `lc0` requires fallback compilation from source (to run `apt-get` and `git clone`). If a validated precompiled `lc0` binary is present in the dataset, internet access is not required.

---

## 5. Bottom Line Verdict & Action Plan

### **VERDICT**: **GO**

All prior blockers (F-01 through F-06) have been verified resolved in `colab/kaggle_diagnostic_run.py`. GPU pinning via serial `CUDA_VISIBLE_DEVICES` assignment is race-free, backend-agnostic, and keeps PyTorch CUDA context on GPU 0 intact. Memory and VRAM usage are well within safety bounds.

### **Action Plan**:
Paste `colab/kaggle_diagnostic_run.py` into a fresh Kaggle notebook cell with env variables:
```python
os.environ["LC0_WORKERS"] = "2"
os.environ["MAX_GAMES"] = "30"
```
Execute the cell and confirm output matches:
`[DONE] REAL run: 213 findings, 263 steer_findings | vision=attention | games=30 moves=880`
