# AUDIT — `phi_net` Pre-Flight Review & Kaggle Training Pipeline

**Auditor:** Gemini (independent clean-room audit)  
**Date:** 2026-09-02  
**Commit Audited:** `83a7500` ("phi_net: pre-flight self-review -- 12 defects found and fixed before Kaggle")  
**Verdict:** **ACTION REQUIRED BEFORE KAGGLE RUN.**  
Claude's pre-flight review caught genuine defects (most notably the $O(N)$ CUDA device-synchronization trap in `roc_auc`). However, **critical silent bugs persist in `phi_net` that will prematurely abort or degrade a Kaggle session.**

---

## 1. Independent Verification of Claude's 12 Fixes

Before reading `PREFLIGHT_REVIEW.md`, the pipeline was independently audited and tested against the workspace dataset (`data/training/config_steering/`, 261,748 rows).

| Defect / Fix | Independent Finding | Verification Result |
|---|---|---|
| **S1: `roc_auc` device sync / loop** | Confirmed. The old loop walked sorted scores with host-device syncs. Tested vectorized `unique_consecutive` against exact $O(N^2)$ brute-force pairwise definition with tie averaging. | **EXACT PASS** (`diff = 0.00e+00` across all random seeds with heavy ties). |
| **S2: Kaggle launch `ModuleNotFoundError`** | Confirmed for `run_kaggle.py`. Launching a script by path places the script's directory on `sys.path`. | **PARTIAL FIX** (Fixed in `run_kaggle.py`, but **missed in `evaluate.py`**; see Bug 2 below). |
| **S3: Frame error in README / PLAN §6** | Confirmed. $\Phi(before)$ scores own error-proneness, $\Phi(after)$ scores opponent's. | **VERIFIED** (Corrected in documentation). |
| **S4: Missing dataset manifest in ckpt** | Confirmed. Positional motif indices require build timestamp matching. | **VERIFIED** (Manifest recorded in `.pt` and checked in `evaluate.py`). |
| **5: Zero-batch epochs (`limit < batch`)** | Confirmed. `steps_per_epoch == 0` now triggers clean `SystemExit`. | **VERIFIED**. |
| **6: NaN AUC KeyError** | Confirmed. Guard present. | **VERIFIED**. |
| **7: `torch.randperm` CUDA generator** | Confirmed. Generator generated on CPU and moved to device. | **VERIFIED**. |
| **8: `--seed` ignored in B1 subset** | Confirmed. `rng = np.random.default_rng(seed)` now active. | **VERIFIED**. |
| **9: `float()` on grad tensor** | Confirmed. `.detach()` applied. | **VERIFIED**. |
| **10: `n_motifs` hardcoded** | Confirmed. Inferred from `motif.shape[1]`. | **VERIFIED**. |
| **11: Mask conditional branch** | Confirmed. Explicit if/else branch in calibration. | **VERIFIED**. |
| **12: Unicode `⚠` crash on cp1252** | Confirmed. Pure ASCII gate report. | **VERIFIED**. |

---

## 2. Persisting Bugs That Threaten Kaggle Execution

### 🚨 Bug 1: The B1 Gate Trap Aborts the Run Before B2 Ever Starts
* **Location:** `phi_net/run_kaggle.py:82-90`
* **Mechanism:**
  ```python
  b1 = rung("b1", args.b1_limit, args.b1_epochs)
  if not b1["gates_passed"]:
      print("\nB1 did not pass its gates. Stopping here deliberately...")
      return
  b2 = rung("b2", None, args.b2_epochs)
  ```
  `b1["gates_passed"]` checks whether the run passes the strict falsification gates:
  - F0: Material baseline AUC $< 0.65$
  - **F1: Held-out AUC $> 0.70$**
  - **F2: Margin over material $\ge 0.03$**
* **The Conflict with PLAN §8b:**
  According to `PLAN_CONFIGURATION_STEERING.md §8b`, **B1 is only 15 epochs on 100k rows** meant to answer: *"does $\Phi$ learn anything at all? Minutes on a T4."* Gate **F1 ($> 0.70$) is the final held-out falsification criterion for B2 (40 epochs on full 209k data)**.
* **Impact on Kaggle:**
  If B1 achieves an AUC of $0.66$–$0.68$ (proving strong signal and solid learning on halved data), `b1["gates_passed"]` is **`False`**. `run_kaggle.py` **aborts**, skipping B2 completely! A Kaggle commit job will run for 2 minutes, save only `phi_b1.pt`, never run B2, and exit.
* **Fix:**
  Decouple B1's continuation check from Gate F1. B1 should abort only if it fails F0 (corrupt/trivial data) or shows zero learning (e.g. $\text{AUC} \le 0.52$).

---

### 🚨 Bug 2: `evaluate.py` Misses the `sys.path` Repair
* **Location:** `phi_net/evaluate.py:18-22`
* **Mechanism:**
  While `run_kaggle.py` received `sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))`, `evaluate.py` did not.
* **Impact on Kaggle:**
  If a user runs `python /kaggle/working/phi_net/evaluate.py ...` (the standard invocation pattern in Jupyter notebooks), Python puts `/kaggle/working/phi_net` on `sys.path`, and the script immediately crashes with:
  ```text
  ModuleNotFoundError: No module named 'phi_net'
  ```
* **Fix:** Add the standard two-line `sys.path` repair to the top of `evaluate.py`.

---

### 🚨 Bug 3: `predict()` Ignores `--no-amp` in Validation & Test
* **Location:** `phi_net/train.py:57-67`, `phi_net/train.py:74`, `phi_net/evaluate.py:71`
* **Mechanism:**
  [`train.py`](file:///c:/Users/Admin/Documents/chess_speak_out_loud/phi_net/train.py#L57) defines:
  ```python
  def predict(model, split, batch_size: int = 16384, use_amp: bool = True) -> torch.Tensor:
  ```
  `evaluate_split()` calls `predict(model, split)` with no `use_amp` argument.
  `evaluate.py` calls `predict(model, test_split)` with no `use_amp` argument.
* **Impact on Kaggle:**
  `HOW_TO_KAGGLE.md` advises passing `--no-amp` if fp16 instability or NaNs occur. However, because `predict()` hardcodes `use_amp=True`, validation evaluation at every epoch and test evaluation on Kaggle **will still run under fp16 autocast**, ignoring the user's flag.
* **Fix:** Pass `use_amp` from `train.py`'s args into `evaluate_split()`, and add a `--no-amp` option to `evaluate.py`.

---

### 🚨 Bug 4: `GradScaler` Remains Active on CUDA Even with `--no-amp`
* **Location:** `phi_net/train.py:41-54`, `phi_net/train.py:140-141`
* **Mechanism:**
  ```python
  scaler = _make_scaler(device)
  use_amp = device.type == "cuda" and not args.no_amp
  ```
  `_make_scaler` does not check `use_amp`. On a CUDA device with `--no-amp`, `use_amp` is `False`, but `scaler` is still a live `GradScaler` multiplying fp32 losses by $65,536.0$.
* **Fix:** Pass `enabled=use_amp` to `GradScaler`:
  ```python
  def _make_scaler(device: torch.device, enabled: bool = True):
      if device.type != "cuda":
          ...
      return torch.amp.GradScaler("cuda", enabled=enabled)
  ```

---

### ⚠️ Bug 5: Stdout Block-Buffering Causes "Deceptive Freeze" on Kaggle
* **Location:** `phi_net/HOW_TO_KAGGLE.md:57`, `phi_net/train.py:184`
* **Mechanism:**
  When launched via a notebook shell command (`!cd /kaggle/working && python -m phi_net.run_kaggle ...`), standard output is connected to a non-TTY pipe and block-buffered (~8 KB). Because an epoch log line is only ~85 bytes, the buffer does not flush for ~96 epochs.
* **Impact on Kaggle:**
  In interactive mode, B1 (15 epochs) will print the preflight header and then **show zero progress for minutes**, misleading the user into thinking the session has hung or crashed.
* **Fix:**
  - In `HOW_TO_KAGGLE.md`: Document `python -u -m phi_net.run_kaggle ...`.
  - In `train.py`: Add `flush=True` to epoch print statements.

---

### ⚠️ Bug 6: Float32 Precision Loss in `roc_auc` Summation
* **Location:** `phi_net/metrics.py:42-46`
* **Mechanism:**
  ```python
  ranks = torch.empty_like(s)  # float32
  ranks[order] = ranks_sorted
  return float((ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))
  ```
  On large splits ($N \ge 200,000$), $n_{pos} \approx 100,000$ and rank sum $\approx 10^{10}$. In IEEE 754 float32, integers above $2^{24} \approx 1.67 \times 10^7$ lose exactness. Summing in float32 introduces truncation noise.
* **Fix:** Accumulate the sum in float64: `ranks[y == 1].double().sum()`.

---

## 3. Required Patch Checklist

Before uploading `phi_net/` to Kaggle:

- [ ] **Patch `phi_net/run_kaggle.py`**: Change B1 continuation gate so failure of final Gate F1 ($> 0.70$) does not kill B2 prematurely.
- [ ] **Patch `phi_net/evaluate.py`**: Add `sys.path.insert(0, ...)` at top of file.
- [ ] **Patch `phi_net/train.py`**:
  - Thread `use_amp` into `evaluate_split()` and `predict()`.
  - Pass `enabled=use_amp` into `_make_scaler()`.
  - Add `flush=True` to `print()` statements.
- [ ] **Patch `phi_net/metrics.py`**: Use `.double().sum()` in `roc_auc()`.
- [ ] **Patch `phi_net/HOW_TO_KAGGLE.md`**: Add `-u` flag to the notebook command.
