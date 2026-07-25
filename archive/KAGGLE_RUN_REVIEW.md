# KAGGLE DIAGNOSIS RUN REVIEW — Thorough Code-Path Audit

**Author**: Gemini 3.6 Flash (High)  
**Date**: 2026-07-25  
**Target Execution**: Kaggle (2×T4 GPUs, 13 GB RAM, 4 vCPUs, `/kaggle/input` READ-ONLY)  
**Verdict**: **NO-GO** (4 BLOCKERs must clear before launching the ~6-min lc0 compile on Kaggle)

---

## 1. Findings Table

| ID | Severity | File : Line | Problem Summary | Evidence (exact code quote) | Proposed Fix (Description) |
|---|---|---|---|---|---|
| **F-01** | **BLOCKER** | `backend/neural_vision.py:33` | `NeuralVision` ONNX monkey-patch attempts to write a temp file into `Path(onnx_path).parent`. When `ONNX` is on `/kaggle/input` (read-only), `mkstemp` throws `OSError: Errno 30 Read-only file system`, breaking `bt3.onnx` load, forcing `mode=policy_fallback`, zeroing attention blindness findings, and artificially boosting TS2 candidate complexity scores by +0.10. | `fd, path = tempfile.mkstemp(dir=Path(onnx_model_or_path).parent)` | Modify `NeuralVision` monkey-patch to use `dir=tempfile.gettempdir()` or `/kaggle/working`, OR copy `bt3.onnx` to `/kaggle/working/engine/bt3.onnx` before passing it to `NeuralVision`. |
| **F-02** | **BLOCKER** | `backend/training/pipeline.py:705-708` | `run_diagnosis` wraps its entire execution in a `try...except Exception as e:` block that logs the exception and returns `None` without re-raising `e`. When `run_diagnosis` crashes (e.g. at `EpdCache` line 138), it returns cleanly to `_main()`, which prints `[DONE] completed 30 games in 0s`, disguising a fatal setup crash as a 0s completed run. | `except Exception as e:\n    import traceback\n    traceback.print_exc()\n    store.update_job(job_id, status="error", error=str(e))` | Re-raise `raise` after `store.update_job` in `run_diagnosis`, OR check `job["status"] == "done"` in `kaggle_diagnostic_run.py`. |
| **F-03** | **BLOCKER** | `colab/kaggle_diagnostic_run.py:166-167` | `_find_weights()` evaluates `791556.pb.gz` (index 1) BEFORE `BT3-768x15x24h-swa-2790000.pb` (index 2). If Kaggle auto-decompressed `BT3` to `.pb` while `791556.pb.gz` remains in `.gz`, `_find_weights()` will match `791556.pb.gz` first, silently running diagnosis on the wrong network! | `for name in ("BT3-768x15x24h-swa-2790000.pb.gz", "791556.pb.gz",\n             "BT3-768x15x24h-swa-2790000.pb", "791556.pb"):` | Group both BT3 extensions before any 791556 extension: `("BT3-768x15x24h-swa-2790000.pb.gz", "BT3-768x15x24h-swa-2790000.pb", "791556.pb.gz", "791556.pb")`. |
| **F-04** | **BLOCKER** | `backend/engine_manager.py:154`, `colab/kaggle_diagnostic_run.py:24` | `LC0Engine` defaults `"RamLimitMb"` to `8192` (8 GB). On Kaggle's 13 GB RAM box, 1 engine worker uses ~8 GB RAM + ~3 GB Python/Torch ≈ 11 GB RAM. If `LC0_WORKERS` defaults to `2` (or if 2 workers are launched), 2 × 8 GB = 16 GB RAM causes an immediate OOM Kill (Exit 137). | `"RamLimitMb": int(os.environ.get("LC0_RAM_LIMIT_MB", "8192")),` | Set default `LC0_RAM_LIMIT_MB` to `2048` in `kaggle_diagnostic_run.py` via `os.environ.setdefault("LC0_RAM_LIMIT_MB", "2048")`, and ensure `LC0_WORKERS=1` is enforced. |
| **F-05** | **CORRECTNESS** | `colab/kaggle_diagnostic_run.py:180` | The `.zip` probing fallback in `kaggle_diagnostic_run.py` checks `_wanted = ("BT3-768x15x24h-swa-2790000.pb.gz", "791556.pb.gz", "bt3.onnx")`. If weights are zipped as decompressed `.pb`, the probe fails to extract them. | `_wanted = ("BT3-768x15x24h-swa-2790000.pb.gz", "791556.pb.gz", "bt3.onnx")` | Add `"BT3-768x15x24h-swa-2790000.pb"` and `"791556.pb"` to `_wanted`. |
| **F-06** | **PERF / COSMETIC** | `colab/kaggle_diagnostic_run.py:230-233` | `_factory()` passes zero arguments to `LC0Engine` and sets `"Backend": "cuda-fp16"` with no GPU index. When `LC0_WORKERS > 1`, all workers pin to GPU 0, leaving GPU 1 0% utilized. | `def _factory():\n    return LC0Engine(LC0_BIN, SEARCH_WEIGHTS, custom_uci_options={"Backend": "cuda-fp16"})` | Update `_factory` to accept worker index and assign GPU device ID or set `CUDA_VISIBLE_DEVICES`. (Non-fatal for `LC0_WORKERS=1`). |

---

## 2. Read-Only Write-Site Sweep (Bucket A Table)

Below is the exhaustive trace of every disk WRITE operation performed during the execution of `kaggle_diagnostic_run.py` -> `run_diagnosis`.

| Write-Site (file:line) | Resolved Target Path on Kaggle | Writable? | Detailed Status & Analysis |
|---|---|---|---|
| `backend/training/store.py:14-20` (`_ensure_dirs()`) | `/kaggle/working/data/training/cache`, `/kaggle/working/data/training/jobs`, `/kaggle/working/data/training/drills` | **YES** | Redirected via `CSZERO_DATA_DIR` set in `kaggle_diagnostic_run.py:32` to `/kaggle/working/data`. |
| `backend/training/store.py:21-22` (`data_gitignore`) | `/kaggle/working/data/.gitignore` | **YES** | Redirected via `CSZERO_DATA_DIR`. |
| `backend/training/store.py:49-50` (`EpdCache.put`) | `/kaggle/working/data/training/cache/*.jsonl` | **YES** | EpdCache write target lands in writable working dir. |
| `backend/training/store.py:62, 127` (`_write_json_atomic`, `save_profile`) | `/kaggle/working/data/training/profile.json`, `/kaggle/working/data/training/profiles/*.json` | **YES** | Profile output lands in writable working dir. |
| `backend/training/attempts.py:53, 85` (`_save_srs`, `record_attempt`) | `/kaggle/working/data/training/srs.json`, `/kaggle/working/data/training/attempts.jsonl` | **YES** | SRS state lands in writable working dir. |
| **`backend/neural_vision.py:33`** (`mkstemp`) | **`/kaggle/input/.../engine/tmpXXXXXX`** | **NO (READ-ONLY)** | **CRITICAL FAIL (F-01)**: `tempfile.mkstemp(dir=Path(onnx_path).parent)` attempts to create a temp file inside the dataset folder under `/kaggle/input`. Throws `OSError: [Errno 30] Read-only file system`, crashing `NeuralVision` initialization. |
| `colab/kaggle_diagnostic_run.py:127` (`mkdir`) | `/kaggle/working/engine` | **YES** | Writable working directory. |
| `colab/kaggle_diagnostic_run.py:138, 156` (`shutil.copy`) | `/kaggle/working/engine/lc0` | **YES** | Binary copy destination is writable. |
| `colab/kaggle_diagnostic_run.py:151, 155` (`subprocess` meson/ninja) | `/kaggle/working/lc0_src/build` | **YES** | Source compile tree is writable. |
| `colab/kaggle_diagnostic_run.py:193` (`zip extract`) | `/kaggle/working/engine/*` | **YES** | Extracted weight files land in writable working dir. |
| `backend/engine_manager.py` (LC0 process) | stdout / stderr pipes (UCI protocol) | **YES** | LC0 process writes strictly to stdio pipes. No log file path configured. |

---

## 3. Deep-Dive Analysis of Technical Bucket Verification

### Bucket A: Read-Only Filesystem Verification
- **Store Redirection**: `CSZERO_DATA_DIR` is set to `/kaggle/working/data` at line 32 of `kaggle_diagnostic_run.py`. Because this executes BEFORE line 228 (`from backend.training import pipeline`), `store.py` initializes `DATA_DIR` to `/kaggle/working/data`. All store operations (`cache`, `jobs`, `profiles`, `drills`, `srs`, `.gitignore`) land under `/kaggle/working/data`.
- **The ONNX Trap**: The single read-only write violation remaining in the codebase is `backend/neural_vision.py:33`. The monkey-patch for `lczerolens.model.safe_shape_inference` forces `tempfile.mkstemp` to use `dir=Path(onnx_model_or_path).parent`. Since `ONNX` is resolved from `/kaggle/input`, `Path(...).parent` points to `/kaggle/input/.../engine`, which is read-only. This explains why `bt3.onnx` failed to load in the last run!

### Bucket B: Silent-Wrong-Answer Risks
- **Net Identity Risk (F-03)**: `_find_weights()` evaluates `"791556.pb.gz"` before `"BT3-768x15x24h-swa-2790000.pb"`. If Kaggle auto-decompressed `BT3...pb.gz` to `BT3...pb` and left `791556.pb.gz` intact, `_find_weights()` will match `791556.pb.gz` and run the diagnosis on the **wrong net** (791556 instead of BT3).
- **`[DONE] completed 30 games in 0s` Explanation (F-02)**: In `pipeline.py:705-708`, `run_diagnosis()` catches all exceptions, prints the traceback, updates job status to `"error"`, and returns `None` normally without re-raising. In `kaggle_diagnostic_run.py:269`, `_main()` awaits `run_diagnosis()`, receives the normal return after line 138 crashed, and executes line 269: `print(f"\n[DONE] completed {len(mine)} games in {time.time()-t0:.0f}s")`. Zero games were analyzed; the script reported `[DONE]` because `run_diagnosis` swallowed the `OSError`.
- **Cache-Key Integrity**: `CSZERO_DATA_DIR` points to `/kaggle/working/data`. On a fresh Kaggle session, `/kaggle/working` is clean and empty, ensuring no stale EPD cache from previous runs or datasets can pollute the diagnosis.
- **POV / Eval Sign Frame Verification**:
  - `metrics.confirmation_swing(eval_best_cp, eval_played_cp, mover_is_white)`: Accurately converts centipawn evaluation swing to mover-POV (`b - p` for White, `p - b` for Black).
  - `metrics.tactical_complexity`: Uses `abs(s0 - s1)` for the reply eval gap, correctly handling White-POV vs Black-POV score magnitudes (`audit F1`).
  - `saliency_absolute`: Mirrors black-to-move boards to White-POV, computes attention, and flips rank coordinates (`9 - rank`), preserving absolute board orientation.

### Bucket C: Remaining Crash & Memory Risks
- **Import Order**: `os.environ.setdefault("CSZERO_DATA_DIR", ...)` is called at line 32 of `kaggle_diagnostic_run.py`, provably before `backend.training.pipeline` (line 228) imports `store.py`.
- **Memory / OOM Risk (F-04)**: `LC0Engine` sets `RamLimitMb = 8192` MB (8 GB) by default. On Kaggle's ~13 GB RAM environment:
  - 1 LC0 Engine worker: ~8 GB RAM + PyTorch/ONNX ~3 GB + OS/Python ~2 GB = ~13 GB RAM (tight).
  - 2 LC0 Engine workers (`LC0_WORKERS=2` default in script line 24): `2 * 8192 = 16384` MB RAM -> **Exit 137 (OOM Killed)**.
- **Subprocess & UCI Guards**: Terminal positions (checkmate/stalemate) are properly guarded at all 3 engine call sites (`get_policy_distribution`, `search_lines`, `_do_analyze`) via `terminal_analysis()` / empty returns, preventing LC0 `bestmove a1a1` UCI protocol crashes.
- **ONNX Failure Cascading Impact**: When `bt3.onnx` fails to load due to F-01:
  1. `saliency_absolute()` returns a 64-square dict of all `0.0`s.
  2. `attention_blindness()` returns `blind = False` for every move (0 attention blindness findings detected).
  3. `tactical_complexity()` sees `len(saliency) == 64` (>0), calculates `top4_mass = 0.0`, resulting in `attention = 1.0 - 0.0 = 1.0` (maximum value), artificially inflating candidate complexity scores by `+0.10` for ALL moves in TS2.

### Bucket D: Audit of Just-Applied Fixes
- **`_find_weights()`**: Accepts both `.pb` and `.pb.gz`. However, the ordering has a priority bug (F-03) where `791556.pb.gz` is placed before `BT3...pb`.
- **`CSZERO_DATA_DIR` Placement**: Correctly placed before `backend` imports.
- **`[input]` glob**: `endswith((".pb.gz", ".pb", ".onnx", ".pgn", ".zip"))` accurately identifies dataset files without false positives against the `lc0` executable binary.

---

## 4. NEEDS-CHECK List

1. **Jupyter Notebook Kernel State Across Cell Re-runs**: If the user re-runs `kaggle_diagnostic_run.py` inside an existing Kaggle notebook session without restarting the Python kernel, `backend.training.store` remains in `sys.modules`. In that scenario, line 32 (`os.environ.setdefault`) will not update `store.DATA_DIR` if it was already imported under a different configuration.
2. **Kaggle Dataset Auto-Decompression Behavior**: Kaggle automatically decompresses single `.gz` uploads (converting `.pb.gz` -> `.pb`), but leaves `.pb.gz` files uncompressed if they are inside a `.zip` archive. `_find_weights()` must handle both loose `.pb` and zipped `.pb`.

---

## 5. Bottom Line Verdict & Action Plan

### **VERDICT**: **NO-GO**

### **BLOCKERS THAT MUST CLEAR BEFORE RUNNING**:

1. **Fix F-01 (`backend/neural_vision.py:33`)**:
   Change `tempfile.mkstemp(dir=Path(onnx_model_or_path).parent)` to use `dir=tempfile.gettempdir()` or `/kaggle/working` to prevent read-only filesystem crash on `/kaggle/input`.
2. **Fix F-02 (`backend/training/pipeline.py:705-708`)**:
   Re-raise `raise` after handling exceptions in `run_diagnosis()`, so setup failures fail fast instead of returning `None` and printing `[DONE] completed 30 games in 0s`.
3. **Fix F-03 (`colab/kaggle_diagnostic_run.py:166-167`)**:
   Reorder `_find_weights()` tuple to check `BT3...pb.gz` AND `BT3...pb` BEFORE checking any `791556` weights.
4. **Fix F-04 (`colab/kaggle_diagnostic_run.py:24, 34`)**:
   Add `os.environ.setdefault("LC0_RAM_LIMIT_MB", "2048")` and set `LC0_WORKERS = int(os.environ.get("LC0_WORKERS", "1"))` to protect the ~13 GB RAM budget from OOM (Exit 137).
