# Deploying on Debian (no root, conda available) + cluster notes

> **Audience: an agent (or human) bringing this repo up on a Debian box.** Read this fully before
> running anything. The app was developed on Windows; it is **mostly portable** but there are a few
> concrete, small changes required for Linux. This document lists every one of them.
>
> **Verified working on Windows as of 2026-07-17:** LC0 live, BT3 attention, adjustable thinking
> time, and the new **Calculation Glow** feature all pass end-to-end. See `HOW_TO_RUN.md` for the
> canonical run steps and `CALCULATION_GLOW_TASKS.md` / `THINKING_TIME_TASKS.md` for what those
> features are.

---

## TL;DR — is it doable? Can we deploy immediately?

**Doable: yes.** The hard part (the async engine loop) is already cross-platform — `engine_manager.py`
uses a ProactorEventLoop only on Windows and a normal loop elsewhere, so Linux needs no loop hack.

**Immediately: no — but close.** There are **4 small blockers**, none deep. Budget ~1 focused hour,
not days:

1. **Dependencies** — `backend/requirements.txt` is now populated (was empty). Recreate the env. ✅ ready
2. **A Linux LC0 binary** — the repo ships no engine binaries (they're gitignored). The Windows
   `lc0.exe` will NOT run on Debian. You must obtain a Linux `lc0`.
3. **Two hardcoded Windows paths/names in code** — `engine_manager.py` and `app.py`. Exact fixes below.
4. **Engine assets** — copy the two networks (`bt3.onnx`, the `.pb.gz`) onto the box; they are
   platform-independent but not in git.

Do those four and it runs. Details follow.

---

## What is NOT in the repo (gitignored — you must supply it)

`.gitignore` excludes the whole `engine/` dir and all binaries. So after cloning you will have **no**
`engine/` folder. You need to create it and populate:

| File | How to get it on Debian |
|------|-------------------------|
| `engine/lc0` | **Linux build of LC0.** Download a Linux release from the LC0 GitHub releases, or build it. Do NOT copy `lc0.exe`. `chmod +x engine/lc0`. |
| `engine/bt3.onnx` | **Copy from the Windows machine** (platform-independent). This is the BT3 transformer that powers attention/Calculation Glow. |
| `engine/791556.pb.gz` (or any `*.pb.gz`) | **Copy from the Windows machine**, or download an LC0 network. Powers the policy arrows. The backend auto-detects the first `*.pb.gz` in `engine/`. |

> The `.pb.gz` and `.onnx` files are just data — scp/rsync them over. Only the LC0 **executable** is
> platform-specific.

---

## Step-by-step

### 1. Environment (conda, no root)

```bash
conda create -n cszero python=3.11 -y
conda activate cszero
pip install -r backend/requirements.txt   # see the torch/CUDA note inside that file for GPU nodes
```

Sanity: `python -c "import torch, lczerolens, chess, fastapi; print('deps ok')"`.

### 2. REQUIRED code changes for Linux (do these before first run)

**2a. `backend/engine_manager.py` — remove the hardcoded Windows engine dir.**
Near the top it has:
```python
ENGINE_DIR = Path(r"C:\Users\Admin\Documents\chess_speak_out_loud\engine")
```
Change to a path derived from the file location (works on any OS):
```python
ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
```
(This dir is used to auto-detect the `*.pb.gz` weights; if it points at a Windows path, LC0 starts
with no network and analysis is broken.)

**2b. `backend/app.py` — platform-correct engine binary name.**
It constructs the engine path as `ENGINE_DIR / "lc0.exe"`. On Linux the binary is `lc0` (no `.exe`).
Make it OS-aware, e.g.:
```python
import sys
LC0_BIN = "lc0.exe" if sys.platform == "win32" else "lc0"
lc0_engine = LC0Engine(engine_path=str(ENGINE_DIR / LC0_BIN))
```
Also make sure the file is executable: `chmod +x engine/lc0`.

> After 2a/2b, verify: `python -c "import backend.app"` imports with no error.

### 3. Run the backend

```bash
conda activate cszero
python -m uvicorn backend.app:app --port 8000            # local only
# or, to reach it from another machine on the network / cluster:
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

Confirm it's live (NOT mock):
```bash
curl http://127.0.0.1:8000/api/health      # -> {"status":"ok","engine_mode":"live",...}
```
`--reload` is optional on Linux and safe (the Windows Proactor issue does not apply here).

### 4. Run the frontend

```bash
cd frontend
npm install
npm run dev        # dev server on http://localhost:5173
# or for a static/prod serve:  npm run build  (outputs frontend/dist/)
```

**If backend and frontend are on different hosts (e.g. frontend on your laptop, backend on the
cluster):** the frontend currently hardcodes the backend URL as `http://127.0.0.1:8000` in
`frontend/src/components/PgnViewer.tsx` (two `fetch(...)` calls: `/api/analyze` and
`/api/calculation-glow`). Point these at the backend's reachable address, or (better) introduce a
`VITE_API_BASE` env var and read `import.meta.env.VITE_API_BASE`. Track this as a follow-up if you
need remote access; for an all-on-one-box deploy it works as-is.

---

## Cluster / GPU notes (this is where the clusters actually help)

The performance wall is **BT3 attention: ~1.5s per forward pass on CPU**. That's why Calculation Glow
is capped at 8 positions (~12s) and is on-demand only. Two ways the clusters help:

1. **GPU acceleration (unlocks real-time Calculation Glow).** `backend/neural_vision.py` currently
   runs the model on CPU (no device placement). On a CUDA node you can move the model and the input
   board tensor to `cuda`, which should cut forward time by ~10–50×. Required work:
   - Install a CUDA torch build (see `backend/requirements.txt` note).
   - In `NeuralVision.__init__`, after loading, `self.model.to("cuda")` (guarded by
     `torch.cuda.is_available()`), and ensure the `LczeroBoard` input tensor is moved to the same
     device inside `_attention_saliency`. Verify attention values are unchanged vs CPU on a test FEN.
   - With that, the "future phase" real-time streaming glow in `CALCULATION_GLOW_TASKS.md` becomes
     practical.

2. **Batch/offline precompute.** The cluster is ideal for precomputing Calculation Glow across entire
   games (every position) offline and caching the maps, so the interactive UI is instant. No code
   change needed beyond a batch script that calls the same `neural_vision.calculation_saliency(...)`.

The target deploy box you described ("more capable but not super powerful, Debian") will run the
current CPU pipeline fine for interactive single-position use; lean on the cluster for GPU speedups
and bulk precompute.

---

## Portability checklist (tick before calling it deployed)

- [ ] `conda`/`cszero` env created, `pip install -r backend/requirements.txt` succeeded
- [ ] `engine/lc0` (Linux, executable), `engine/bt3.onnx`, `engine/*.pb.gz` all present
- [ ] `engine_manager.py` ENGINE_DIR made relative (fix 2a)
- [ ] `app.py` engine binary name made OS-aware (fix 2b)
- [ ] `python -c "import backend.app"` imports clean
- [ ] `/api/health` returns `engine_mode: "live"`
- [ ] `/api/analyze` returns non-zero eval + `saliency_source: "attention"`
- [ ] `/api/calculation-glow` returns a 64-square map with `positions_used > 0`
- [ ] `npm run build` succeeds; UI reaches the backend
- [ ] (if remote) frontend `fetch` URLs point at the backend host
```
