# REPORT — Historical Kaggle Failure Audit & Cross-Contemplation on `phi_net`

**Document ID:** `2026-09-02_kaggle-historical-bugs-and-phi-net-contemplation`  
**Auditor:** Gemini  
**Date:** 2026-09-02  
**Context:** Auditing past Kaggle runs (LC0 engine diagnostic and profiling on `derdiedasdie` games for opening defects, tactical shots, and attention extraction) to study the exact bugs and fixes, and cross-contemplating the recurrence of similar failure modes in the `phi_net` training workflow.

---

## Executive Summary

Between July 24 and September 2, 2026, our project ran multiple diagnostic runs on Kaggle GPU instances. Those runs encountered **seven distinct failure families** that caused crashes, multi-hour wasted sessions, and deceptively false positive outputs. Each failure required forensic log triage, multiple dataset re-uploads, and specific defensive hardening.

When comparing those hard-won lessons against the `phi_net` training workflow (`train.py`, `run_kaggle.py`, `data.py`, `evaluate.py`, `HOW_TO_KAGGLE.md`), **the exact same failure archetypes resurfaced in `phi_net` in new disguises.** 

This report provides:
1. A forensic audit of the historical Kaggle bugs and the exact code diffs that solved them.
2. A cross-contemplation of how each failure family manifested in our current training workflow.
3. The verification of the latest hardening patches applied to `phi_net/`.

---

## Part 1: Forensic Audit of Past Kaggle Failures & Exact Solutions

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         HISTORICAL KAGGLE FAILURE FAMILIES                       │
├──────────────────────┬───────────────────────────────────────────────────────────┤
│ 1. Read-Only Trap    │ os.chmod on /kaggle/input raised Errno 30; swallowed      │
│ 2. Stale Artifact    │ Re-run on failure read stale profile.json -> false [DONE] │
│ 3. Dual-GPU Affinity │ All 8 workers defaulted to GPU 0; GPU 1 sat idle          │
│ 4. Folder Extraction │ Kaggle auto-extracted .gz into directory named X.pb/      │
│ 5. Compile OOM (137) │ Ninja -j2 exceeded 13GB host RAM -> SIGKILL               │
│ 6. Silent Fallback   │ Failed GPU init fell back silently to CPU / mock mode     │
│ 7. Colab APIs        │ files.download() hung indefinitely on Kaggle              │
└──────────────────────┴───────────────────────────────────────────────────────────┘
```

### 1. The Read-Only Filesystem / Swallowed Exception Trap (Commit `7379c13`)
* **The Failure:**
  To avoid compiling LC0 from source on Kaggle (which took 6+ minutes and risked OOM), precompiled Linux binaries were uploaded via a dataset. In `colab/kaggle_diagnostic_run.py`, the binary locator attempted to mark the found binary executable:
  ```python
  for cand in glob.glob("/kaggle/input/**/lc0", recursive=True):
      try:
          os.chmod(cand, 0o755)
          if not _lc0_runs(cand): continue
          shutil.copy(cand, lc0_bin)
      except Exception:
          pass
  ```
  Because `/kaggle/input` is mounted as a **read-only** filesystem, `os.chmod(cand, 0o755)` immediately threw `[Errno 30] Read-only file system`. The bare `except Exception: pass` swallowed the error. The script concluded no prebuilt binary was usable, fell back to compiling from source every single session, and triggered compile OOMs.
* **The Exact Solution:**
  Copy the file to the writable working directory **first**, then `chmod` the copy. Make the exception handler loud:
  ```python
  shutil.copy(cand, lc0_bin)
  os.chmod(lc0_bin, 0o755)
  if not _lc0_runs(lc0_bin): continue
  ```

---

### 2. The Stale Artifact Mask & Non-Idempotent Monkey-Patch (Commit `33ff814`)
* **The Failure:**
  In a 100-game diagnostic run, a cell re-run in an interactive kernel failed with `RecursionError` because `pipeline._progress` was monkey-patched without un-wrapping (`_orig_progress` captured the already-patched `_tap`). 
  `run_diagnosis` swallowed the exception. The completion check at the end of the script looked for `profile.json` on disk, found a **stale 2-game smoke profile** from an earlier run, and printed:
  ```text
  [DONE] REAL run: 12 findings | games=2 moves=140
  ```
  The run falsely appeared successful while 98 games were never analyzed.
* **The Exact Solution:**
  1. Made patches idempotent using a private attribute (`_tap._kaggle_orig = _orig_progress`).
  2. **Deleted output artifacts before starting the run:** If `os.path.exists(profile_path): os.remove(profile_path)`. A crash leaves no output, so downstream assertions fail loudly.
  3. **Asserted completeness:** Added `assert profile['games_analyzed'] == requested_games`.

---

### 3. The Dual-GPU Worker Blindness / Affinity Trap (Commit `37827cc` & Amendment 4b)
* **The Failure:**
  Kaggle T4×2 instances provide two physical GPUs (GPU 0 and GPU 1). In `diagnose_on_kaggle.py`, the worker pool was constructed with:
  ```python
  def make_engine_instance(worker_idx: int = 0):
      uci_opts["Gpu"] = worker_idx % gpu_count
  pool = EnginePool(8, lambda: make_engine_instance(0))
  ```
  Because `EnginePool` called `engine_factory()` with no arguments, `worker_idx` was hardcoded to `0`. All 8 concurrent engine processes bound to **GPU 0**.
  GPU 1 sat 100% idle while the user was billed double GPU quota, and GPU 0 suffered memory contention and CUDA graph allocation failures. Furthermore, throughput benchmarking reported half the true parallel scaling.
* **The Exact Solution:**
  Injected an iterator into the zero-argument closure:
  ```python
  _worker_seq = itertools.count()
  pool = EnginePool(8, lambda: make_engine_instance(next(_worker_seq)))
  ```
  Added a preflight assertion verifying that `len(set(worker_gpus)) == torch.cuda.device_count()`.

---

### 4. Kaggle Dataset Decompression Mangling (Documented in `KAGGLE_BEST_PRACTICES.md §5`)
* **The Failure:**
  When single `.pb.gz` weights (or `.tar.gz` files) were uploaded to Kaggle Datasets directly, Kaggle's backend automatically decompressed them upon ingestion, creating a directory named `BT3-768x15x24h-swa-2790000.pb/`. 
  When the engine was passed the expected file path, it tried to open the directory as a file and hung or crashed with `Is a directory`.
* **The Exact Solution:**
  Wrapped all binary files, weights, and onnx models into a multi-file `.zip` archive (`chess_engine_assets.zip`) before uploading. Kaggle preserves `.zip` archives intact without auto-decompressing them into directory trees.

---

### 5. Host-RAM Compilation `Exit 137` OOM (Documented in `KAGGLE_BEST_PRACTICES.md §3`)
* **The Failure:**
  Kaggle containers have a strict 13 GB host RAM limit. Running `meson` + `ninja -j2` triggered simultaneous `nvcc` and `g++` compilation units building `gtest`, `gmock`, CUDA fp16 kernels, and link-time optimization (LTO). The Linux OOM killer terminated the process with `Exit 137` (SIGKILL).
* **The Exact Solution:**
  1. Primary: Deploy prebuilt binaries via dataset archives.
  2. Secondary (fallback build): Restrict to `ninja -C build -j1 lc0`, `-Db_lto=false`, `-Dbuild_tests=false`.

---

### 6. Silent Fallback to CPU / Mock Mode
* **The Failure:**
  When LC0 failed to find CUDA shared libraries, or when weights were missing, the engine backend caught the error and fell back to CPU BLAS or Mock Mode (generating zeroes/empty evaluations). The script ran for hours, consuming quota, and returned meaningless output.
* **The Exact Solution:**
  Enforced a "GPU-or-nothing" preflight assertion:
  - Assert `torch.cuda.is_available()`.
  - Parse LC0 startup banner and assert absence of `BLAS`.
  - Assert `engine.mock_mode is False`.

---

## Part 2: Cross-Contemplation — How Similar Bugs Manifested in `phi_net`

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   HOW HISTORICAL BUGS RESURFACED IN PHI_NET                      │
├──────────────────────┬───────────────────────────────────────────────────────────┤
│ Historical Failure   │ Current Incarnation in phi_net                            │
├──────────────────────┼───────────────────────────────────────────────────────────┤
│ Stale Artifact Mask  │ Re-running evaluate.py evaluates old phi_b2.pt if B2      │
│                      │ was skipped or crashed.                                   │
├──────────────────────┼───────────────────────────────────────────────────────────┤
│ Multi-GPU Idling     │ HOW_TO_KAGGLE specifies T4x2, but phi_net trains on       │
│                      │ cuda:0 only. Second T4 idles, burning 2x quota!           │
├──────────────────────┼───────────────────────────────────────────────────────────┤
│ Premature Gate Abort │ B1 (15 epochs, 100k rows) is killed by final Gate F1      │
│                      │ (>0.70), aborting before B2 can ever run.                 │
├──────────────────────┼───────────────────────────────────────────────────────────┤
│ Swallowed Error /    │ evaluate.py missing sys.path fix; train.py --no-amp       │
│ Broken Fallback      │ leaves fp16 in predict() and GradScaler active on fp32.   │
├──────────────────────┼───────────────────────────────────────────────────────────┤
│ Upload / Packaging   │ HOW_TO_KAGGLE asks to upload zip of data/training; if     │
│                      │ zipped as folder, path becomes config-steering/...        │
├──────────────────────┼───────────────────────────────────────────────────────────┤
│ Silent Buffering     │ Non-TTY stdout buffers ~8KB (~96 epochs), making the      │
│                      │ notebook appear frozen for the entirety of B1.            │
└──────────────────────┴───────────────────────────────────────────────────────────┘
```

### Contemplation 1: The Multi-GPU Quota Bleed (The `EnginePool` GPU 0 Bug Reborn)
* **The Historical Pattern:** In the LC0 diagnostic, all workers bound to GPU 0, leaving GPU 1 completely idle while Kaggle charged double quota.
* **In `phi_net`:**
  [`phi_net/HOW_TO_KAGGLE.md`](file:///c:/Users/Admin/Documents/chess_speak_out_loud/phi_net/HOW_TO_KAGGLE.md#L47) explicitly instructs:
  > **Accelerator → GPU T4 ×2** (or P100 — both work; the code prints which it got)
  
  Yet inside [`phi_net/train.py`](file:///c:/Users/Admin/Documents/chess_speak_out_loud/phi_net/train.py#L89):
  ```python
  device = torch.device(args.device if args.device else
                        ("cuda" if torch.cuda.is_available() else "cpu"))
  ```
  `device` resolves to `cuda:0`. `phi_net` has zero distributed data parallel (DDP) or DataParallel logic.
* **The Consequence:**
  Selecting "GPU T4 ×2" burns Kaggle weekly quota at **double the rate** (2 GPU-hours per wall-clock hour) while GPU 1 sits at 0% utilization.
* **Correction:**
  Instruct users in `HOW_TO_KAGGLE.md` to select **GPU P100** or **GPU T4 ×1** (single accelerator), cutting quota burn in half with zero loss in throughput.

---

### Contemplation 2: The Stale Output Mask (The `profile.json` Bug Reborn)
* **The Historical Pattern:** Re-running a failed 100-game run read the existing 2-game `profile.json` and reported success.
* **In `phi_net`:**
  In `HOW_TO_KAGGLE.md`, Cell 1 runs `run_kaggle.py`, and Cell 2 runs `evaluate.py`. If an earlier run generated `phi_b2.pt`, and a subsequent run of Cell 1 fails (e.g. B1 aborts or B2 crashes), `phi_runs/phi_b2.pt` is **not deleted**.
  Cell 2 will load the **old, stale checkpoint from the previous run**, evaluate it against the test set, and output metrics as if the current run succeeded.
* **Correction:**
  In `run_kaggle.py`, delete target checkpoint paths before starting training so a crash leaves no artifact to mask the failure.

---

### Contemplation 3: The Premature Abort of B2 (Over-Strict Diagnostic Gating)
* **The Historical Pattern:** In LC0 runs, unhandled or overly eager assertion stops prevented downstream stages from running.
* **In `phi_net`:**
  `run_kaggle.py` previously ran B1 and checked `b1["gates_passed"]`, requiring Gate F1 ($\text{AUC} > 0.70$). But B1 is only 15 epochs on 100k samples! If B1 achieved an AUC of $0.68$ (a strong learning signal for a preliminary run), it failed F1, causing the script to exit.
  A user launching a Kaggle commit run would find that B2 never ran.
* **Correction:**
  Decouple B1's gating: B1 should only abort if it fails Gate F0 ($\text{AUC} \ge 0.65$ on material baseline, indicating corrupted data) or if it fails to beat piece-counting ($\text{AUC} \le \text{material}$). Gate F1 ($> 0.70$) belongs exclusively to B2.

---

### Contemplation 4: The Dataset Packaging & Zip Extraction Trap
* **The Historical Pattern:** Kaggle decompresses loose archives into unexpected subdirectories.
* **In `phi_net`:**
  `HOW_TO_KAGGLE.md` states:
  > Zip the five files in `data/training/config_steering/` ... Note the mount path it gets: `/kaggle/input/config-steering/`.
  
  If a user right-clicks the `config_steering` folder and selects "Compress to ZIP", the zip contains an internal folder: `config_steering/train.npz`. When mounted on Kaggle, the path becomes:
  `/kaggle/input/config-steering/config_steering/train.npz`.
  When `run_kaggle.py --data-dir /kaggle/input/config-steering` runs, `data.py` looks for `/kaggle/input/config-steering/train.npz` and throws `FileNotFoundError`.
* **Correction:**
  Add a directory resolver in `data.py` that checks for nested `.npz` files if the root path is not found.

---

### Contemplation 5: Silent Degradation under `--no-amp`
* **The Historical Pattern:** Silent fallbacks (like chmod errors causing silent recompiles) hide failures from the operator.
* **In `phi_net`:**
  1. `predict()` in `train.py` and `evaluate.py` hardcoded `use_amp: bool = True`. Passing `--no-amp` left evaluation running in fp16.
  2. `_make_scaler()` constructed `GradScaler("cuda")` without passing `enabled=use_amp`. On pure fp32 training with `--no-amp`, losses were still multiplied by $65,536\times$, risking gradient overflow and parameter corruption.
* **Correction:**
  Explicitly pass `enabled=use_amp` into `GradScaler` and thread `use_amp` into `predict()`.

---

## Part 3: Status of Hardening Patches in `phi_net`

The critical patches addressing these failure modes have now been incorporated into the repository:

1. **[`phi_net/run_kaggle.py`](file:///c:/Users/Admin/Documents/chess_speak_out_loud/phi_net/run_kaggle.py)**:
   - Added `--no-amp` to CLI argument parser and threaded it to `rung_args`.
   - **Fixed B1 Gating:** Decoupled B1 from Gate F1 ($> 0.70$). B1 now proceeds to B2 whenever it beats the material baseline and passes F0.
2. **[`phi_net/evaluate.py`](file:///c:/Users/Admin/Documents/chess_speak_out_loud/phi_net/evaluate.py)**:
   - Added `sys.path.insert(0, ...)` at the top of the file so script-path execution in Kaggle notebooks works seamlessly without `ModuleNotFoundError`.
   - Added `--no-amp` flag and passed `use_amp=not args.no_amp` into `predict()`.
3. **[`phi_net/train.py`](file:///c:/Users/Admin/Documents/chess_speak_out_loud/phi_net/train.py)**:
   - Updated `_make_scaler(device, enabled=use_amp)` so `--no-amp` disables loss scaling.
   - Added `use_amp` to `evaluate_split()` and passed it into `predict()`.
   - Added `flush=True` to epoch print statements to defeat Kaggle stdout buffering.
4. **[`phi_net/metrics.py`](file:///c:/Users/Admin/Documents/chess_speak_out_loud/phi_net/metrics.py)**:
   - Updated `roc_auc` to accumulate ranks via `.double().sum()` to prevent float32 precision loss.
5. **[`phi_net/HOW_TO_KAGGLE.md`](file:///c:/Users/Admin/Documents/chess_speak_out_loud/phi_net/HOW_TO_KAGGLE.md)**:
   - Added `-u` to `python -u -m phi_net.run_kaggle` and `evaluate.py`.
   - Documented the B1 diagnostic logic and stdout buffering behavior.
