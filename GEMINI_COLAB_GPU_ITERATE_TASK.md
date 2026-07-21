# Antigravity/Gemini Task — Get the two GPU cells of the Colab notebook working

**This is an EMPIRICAL iteration task, not a spec-and-build task.** You have the
thing the leader does not: a live **Colab GPU runtime**. So the loop is: run the
cell → read the ACTUAL error/output → fix → rerun, until the success criteria
below are met. Do not add unit tests; the "test" is the cell running green on the
GPU. Report back what you changed and any repo-worthy fixes.

## The notebook
`colab/diagnose_on_gpu.py` (open in Colab; `# %%` cells). Cells 1–3 (GPU check,
Drive mount, repo clone + pip installs) should just work — get them green first.
Your job is the two cells marked **`⚠️ ITERATE`**: **Cell 4 (CUDA LC0)** and the
BT3 part of **Cell 5 (NeuralVision on GPU)**. Do not change the pipeline cells
(6–9) — they are how the app runs it.

## Ground rules
- **Only touch** the two ITERATE cells (and, if strictly needed, tiny supporting
  edits in the notebook). Do NOT change `backend/training/*` or the pipeline logic.
- If a fix genuinely belongs in the repo (e.g. `backend/neural_vision.py` needs a
  device flag to use the GPU), **do NOT edit those files yourself — write down the
  exact change and report it to the leader** to apply and test on CPU first.
- Prefer the smallest change that meets the success criterion. If GPU for BT3
  proves intractable, the CPU fallback is acceptable (see Cell 5).

---

## Cell 4 — CUDA LC0 (the reliable, must-have GPU win)
**Goal:** an `lc0` binary that runs on the **GPU** and loads the `791556.pb.gz`
weights, so `engine.analyze()` returns real evals fast.

**Success criteria (verify all, empirically):**
1. `lc0 --help` (stderr banner) lists a **CUDA backend** among the available
   backends (e.g. `cuda`, `cuda-fp16`, or `cudnn`/`cudnn-fp16`).
2. In Cell 5, after `await engine.start()`, `engine.is_available()` is `True`.
3. A quick probe returns a real (non-mock) eval within ~1s:
   ```python
   print(await engine.analyze("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                              depth=None, multipv=1, time_limit=1.0))
   ```
4. While that runs, `!nvidia-smi` shows an `lc0` process using GPU memory.

**Likely things to fix (iterate):**
- **Wrong release URL / 404** on `LC0_URL`: go to
  https://github.com/LeelaChessZero/lc0/releases, pick the latest, and use the
  **linux GPU / nvidia-cuda** asset name for that version (the exact filename
  changes per release).
- **CUDA/cuDNN mismatch** (lc0 fails to init the GPU backend, or errors on a
  missing `libcudnn*.so`): check Colab's CUDA version (`!nvcc --version` /
  `!nvidia-smi`), and pick an lc0 build matching it, or `pip install nvidia-cudnn-cuXX`
  to supply the libs, or use the plain `cuda` (not `cudnn`) backend build.
- **lc0 silently fell back to a CPU/BLAS backend**: force the GPU backend via a
  UCI option — construct the engine and set `Backend`:
  ```python
  # in Cell 5, if needed:
  engine = LC0Engine(engine_path=LC0_BIN, weights_path=".../791556.pb.gz")
  # then confirm the backend; if it picked blas, pass Backend via a small edit
  # to the engine start options, or run `lc0 benchmark --backend=cuda` to confirm CUDA works.
  ```
  Confirm with `!<LC0_BIN> benchmark --backend=cuda-auto` printing a high nps.

---

## Cell 5 (BT3 part) — NeuralVision on GPU (nice-to-have; CPU fallback OK)
**Goal:** `NeuralVision` loads `bt3.onnx` in **attention** mode and runs saliency
on the **GPU** (fast). If GPU can't be made to work, fall back to CPU (correct,
just slower) and record why.

**Success criteria:**
1. `vision.mode == "attention"` (NOT `"policy_fallback"` — fallback means the net
   didn't load; that must be fixed regardless of device).
2. A probe runs without error and returns a dict of ~64 square→float:
   ```python
   import time; t=time.time()
   s = vision.saliency_absolute("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
   print(len(s), "squares,", round(time.time()-t,2), "s")
   ```
3. **GPU target:** that timing is well under the CPU baseline (~1.5s) — more like
   tens of ms — and `!nvidia-smi` shows the python process holding GPU memory.
   **CPU fallback:** if you can't get it on GPU, the same probe must still succeed
   (attention mode, correct output) on CPU.

**Likely things to fix (iterate):**
- `NeuralVision.__init__` loads via `lczerolens.LczeroModel.from_onnx_path(onnx_path)`
  and calls `self.model(board)` (it passes a *board*, so lczerolens builds the
  input tensor internally — that's why device handling is non-obvious).
- **First get attention mode working at all** (criterion 1): if it logs
  `policy_fallback`, read the exception it logged — likely an `onnx2torch` /
  `lczerolens` install or shape-inference issue. `torch.set_default_device("cuda")`
  BEFORE constructing NeuralVision (as the cell does) can BREAK the onnx load — if
  so, **remove that line, load on CPU first**, confirm attention mode, then attempt
  GPU (next bullet).
- **Then attempt GPU:** check the lczerolens API for a device option
  (`dir(vision.model)` — look for `.to`, `.cuda`, a `device=` kwarg on the board
  forward, or a module-level default). Common working pattern: load on CPU, then
  `vision.model.to("cuda")` and ensure the board→tensor input is moved to cuda
  (may require a small monkeypatch of the forward, or a lczerolens device setting).
- **If GPU is intractable:** leave BT3 on CPU, keep `set_default_device` OFF, and
  note it — LC0-on-GPU still delivers the main speedup, and `steer_bt3_budget`
  already caps BT3 calls per run.

---

## When done — report back (to the leader)
Paste:
1. The final working **Cell 4** (the exact `LC0_URL` / setup that worked) and the
   `engine.is_available()` + probe output + the `nvidia-smi` line showing lc0 on GPU.
2. The final **Cell 5 BT3** state: attention-mode confirmed, the saliency probe
   timing, whether it's on GPU or CPU, and if GPU — the exact device-placement
   code that worked.
3. Any change that should move into the repo (e.g. a `neural_vision.py` device
   flag) — described precisely, NOT applied — for the leader to add and test.
4. A one-line note of the observed full-run speed (from Cell 6's subset timing).
