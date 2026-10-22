# Gemini Work Order — First-Time Debian Bring-Up

**Role:** You are the worker. Claude (orchestrator) has surveyed the box and written this order.
**Mission:** Bring `chess_speak_out_loud` up on this Debian box for the first time. The project was developed on Windows; you must adapt it to Linux without introducing regressions.

**Definition of done:** All three of these succeed, in this order:
1. `curl http://127.0.0.1:8000/api/health` returns `{"status":"ok","engine_mode":"live",...}`.
2. A POST to `/api/analyze` with a real FEN returns non-zero eval AND `"saliency_source":"attention"`.
3. `http://localhost:5173` loads in a browser and the board renders policy arrows on move analysis.

---

## Environment already surveyed (do not re-derive)

| Fact | Value |
|------|-------|
| Project root | `/scratch/local1/chess_speak_out_loud` |
| OS | Debian (Linux 6.1.0-50-amd64) |
| Conda | `/scratch/local1/anaconda3/bin/conda` (v25.11.1) |
| Node / npm | `node v24.12.0`, `npm 11.10.0` (on PATH) |
| Free disk on `/scratch/local1` | ~1.5 TB |
| GPU | NVIDIA present, CUDA 12.2 driver — **ignore for now**, install CPU torch first |
| Existing conda envs | Several unrelated envs exist under `/scratch/local1/anaconda3/envs/`. **Do not touch them.** Create only `cszero`. |
| `engine/` directory | **Does not exist yet.** You will create it. |
| Windows source machine | The user has the engine files (`bt3.onnx`, `791556.pb.gz`) on their Windows box. You cannot reach it. |

---

## Non-negotiable rules

1. **Do not `sudo` or install anything system-wide.** No root here. Everything must live in the conda env or the project dir.
2. **Do not invent URLs for neural-network downloads.** If a URL is not written verbatim in this document, treat it as unknown and STOP AND REPORT (see §STOP conditions below).
3. **Do not change any file outside `/scratch/local1/chess_speak_out_loud`.** Do not modify shell rc files, do not `conda init`, do not touch other envs.
4. **Do not amend or revert commits.** Make new commits only if the orchestrator asks; otherwise leave git alone.
5. **Do not silently improvise on failure.** If a step fails with output you did not expect, STOP and report to the orchestrator with: the exact command, the exact output, and the phase/step number. Do not "fix" it by trying alternatives.
6. **Do not upgrade or downgrade package versions.** Use `backend/requirements.txt` as pinned. If a pin fails to resolve on Linux, STOP and report — do not pick a substitute.
7. **Do not edit files not named in this document.** The only two code files you will touch are `backend/engine_manager.py` and `backend/app.py`, and only the exact lines named below.
8. **Do not enable the LLM path.** `LLM_ENABLED = False` in `backend/app.py` must stay False. The `google-generativeai` package is imported at startup — that's fine; do not remove it.

---

## STOP conditions (report to orchestrator, do not proceed)

Stop immediately and print `STOP: <phase>.<step> — <one-line reason>` followed by the failing command and its full output, if any of:

- A command exits non-zero and this document did not predict it.
- A file you were told to edit does not contain the exact `old_string` you were told to find.
- `pip install` fails to resolve a pinned version.
- LC0 binary is not available at the URL in Phase B.
- `/api/health` returns `"engine_mode":"mock"` after Phase D completes.
- `/api/analyze` returns `"saliency_source":"policy_fallback"` instead of `"attention"`.
- Any step wants to install root-level packages, run `sudo`, or write outside the project dir.

---

## Phase A — Python environment (no engine files needed)

### A.1 Create the conda env

```bash
/scratch/local1/anaconda3/bin/conda create -n cszero python=3.11 -y
```

Expected: env installed at `/scratch/local1/anaconda3/envs/cszero`. Verify:

```bash
ls /scratch/local1/anaconda3/envs/cszero/bin/python
```

### A.2 Install backend dependencies (CPU torch)

```bash
cd /scratch/local1/chess_speak_out_loud
/scratch/local1/anaconda3/envs/cszero/bin/pip install -r backend/requirements.txt
```

This installs the CPU wheel of torch by default. It will take several minutes. Do **not** install a CUDA build in this phase — first-time bring-up is CPU-only.

### A.3 Sanity-check imports

```bash
/scratch/local1/anaconda3/envs/cszero/bin/python -c "import torch, lczerolens, chess, fastapi, onnx2torch; print('deps ok')"
```

Expected stdout: exactly `deps ok`. Any ModuleNotFoundError → STOP.

---

## Phase B — Engine assets

The `engine/` directory does not exist. You will create it and populate three files. The user must provide two of them; you can fetch one.

### B.1 Create the directory

```bash
mkdir /scratch/local1/chess_speak_out_loud/engine
```

### B.2 Build LC0 from source (no prebuilt Linux binary exists upstream)

**Confirmed by orchestrator:** the LC0 GitHub Releases page ships only Windows, Android, and macOS binaries — no Linux prebuilt. `conda-forge` also has no `lc0` package. The user has no local Linux binary to drop in. **Therefore we build from source, no root, using the `cszero` conda env's toolchain.**

Runtime estimate: 5–15 minutes for the compile.

#### B.2.a — Install build toolchain into `cszero`

We use `conda activate` here (not full-path invocation) because meson reads compiler env vars (`CC`, `CXX`, `PKG_CONFIG_PATH`, etc.) that conda's activate scripts export.

```bash
source /scratch/local1/anaconda3/etc/profile.d/conda.sh
conda activate cszero
conda install -c conda-forge -y meson ninja compilers eigen libprotobuf zlib
```

Verify the toolchain is on PATH inside the activated env:

```bash
which meson ninja
meson --version
ninja --version
```

If any of the four `which` results is empty, STOP.

#### B.2.b — Clone LC0

```bash
cd /tmp
rm -rf lc0-src
git clone --depth 1 https://github.com/LeelaChessZero/lc0.git lc0-src
cd lc0-src
```

If `git clone` fails (network, DNS), STOP.

#### B.2.c — Build

Keep the `cszero` env activated from B.2.a. From `/tmp/lc0-src`:

```bash
./build.sh -Dgtest=false
```

Expected outcome: after several minutes, the script prints something like `Linking target lc0` and finishes with exit code 0. The compiled binary lands at `/tmp/lc0-src/build/release/lc0`.

Common failure modes and required response:

- **Meson complains about a missing dependency (e.g., a specific version of protobuf, blas).** STOP. Do NOT install extra packages beyond those listed in B.2.a. Report the exact meson error.
- **Compile error inside an LC0 source file.** STOP. Report the failing file, line, and the error message verbatim.
- **`build.sh: line N: <command>: command not found`.** STOP — the env isn't activated correctly. Report which command was missing.

Do NOT retry with different meson flags. Do NOT switch backends. STOP and let the orchestrator decide.

#### B.2.d — Install the binary

```bash
cp /tmp/lc0-src/build/release/lc0 /scratch/local1/chess_speak_out_loud/engine/lc0
chmod +x /scratch/local1/chess_speak_out_loud/engine/lc0
/scratch/local1/chess_speak_out_loud/engine/lc0 --help | head -5
```

Expected: LC0 prints its usage/help (mentions `--weights`, `--backend`, etc.). If it errors with a shared-library-not-found (`error while loading shared libraries: libXYZ.so`), STOP and report the exact `.so` name — this means the binary was linked against a conda-provided library and needs `LD_LIBRARY_PATH` set at backend startup time, which the orchestrator will handle.

#### B.2.e — Leave the source tree in place

Do NOT delete `/tmp/lc0-src` yet — the orchestrator may want to inspect the build log or rebuild with different flags. It can be cleaned up after Phase D succeeds.

### B.3 Obtain the two neural nets

**You cannot fetch these yourself.** They are:

- `engine/bt3.onnx` — BT3 transformer (attention/saliency).
- `engine/791556.pb.gz` — SE-ResNet policy network (any `*.pb.gz` works; backend auto-detects the first one).

**STOP HERE** after Phase A + B.1 + B.2 are done, and report to the orchestrator:
> "Phase A/B complete. Need `bt3.onnx` and a `*.pb.gz` LC0 network placed in `/scratch/local1/chess_speak_out_loud/engine/`. Please instruct."

Do **not** try to guess a download URL for the nets. Do **not** proceed to Phase C without those two files.

Once the files are placed, verify:

```bash
ls -la /scratch/local1/chess_speak_out_loud/engine/
```

Expected: `lc0` (executable), `bt3.onnx`, one or more `*.pb.gz`.

---

## Phase C — Code adaptations for Linux

Exactly two edits. No others.

### C.1 `backend/engine_manager.py` line 26

Find this line:

```python
ENGINE_DIR = Path(r"C:\Users\Admin\Documents\chess_speak_out_loud\engine")
```

Replace with:

```python
ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
```

If the file does not contain the exact `old_string` above verbatim, STOP.

### C.2 `backend/app.py` — engine binary name

Find this block (around line 54–56):

```python
lc0_engine = LC0Engine(
    engine_path=str(ENGINE_DIR / "lc0.exe"),
)
```

Replace with:

```python
import sys as _sys
_LC0_BIN = "lc0.exe" if _sys.platform == "win32" else "lc0"
lc0_engine = LC0Engine(
    engine_path=str(ENGINE_DIR / _LC0_BIN),
)
```

If the file does not contain the exact `old_string` above verbatim, STOP.

### C.3 Verify import

```bash
cd /scratch/local1/chess_speak_out_loud
/scratch/local1/anaconda3/envs/cszero/bin/python -c "import backend.app; print('import ok')"
```

Expected: `import ok`. Any exception → STOP.

---

## Phase D — Start the backend and verify

### D.1 Launch the backend

In a terminal you can leave open (or `nohup`/tmux — orchestrator's choice):

```bash
cd /scratch/local1/chess_speak_out_loud
/scratch/local1/anaconda3/envs/cszero/bin/python -m uvicorn backend.app:app --port 8000
```

Expected startup log lines (within ~10 seconds):

```
INFO ... Starting Chess Speak Out Loud backend v0.1.0
INFO ... LC0 engine is LIVE.
INFO ... NeuralVision loaded BT3 ONNX in attention mode.
```

If you see `LC0 engine not found — running in MOCK mode.` → STOP.
If you see `NeuralVision` errors → STOP.

### D.2 Health check

In a second terminal:

```bash
curl http://127.0.0.1:8000/api/health
```

Expected exact JSON (order may vary): `{"status":"ok","engine_mode":"live","version":"0.1.0"}`.
Any `"engine_mode":"mock"` → STOP.

### D.3 Real analysis check

```bash
curl -s -X POST http://127.0.0.1:8000/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"fen":"rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"}' \
  | head -c 800
```

Expected in the response: a non-zero numeric evaluation AND `"saliency_source":"attention"`.
If `"saliency_source":"policy_fallback"` → STOP.

---

## Phase E — Frontend

### E.1 Install and start

```bash
cd /scratch/local1/chess_speak_out_loud/frontend
npm install
npm run dev
```

Expected: Vite prints `Local: http://localhost:5173/`. Leave it running.

### E.2 Manual check (report to orchestrator; do not attempt browser automation)

Report to orchestrator:
> "Backend + frontend up. Open `http://localhost:5173` in a browser and confirm the board loads and analysis renders arrows. Ready for user verification."

Do **not** try to install headless-browser tooling or take screenshots.

---

## Final report format

When done (or when hitting a STOP), report back to the orchestrator in this exact shape:

```
PHASE: <A/B/C/D/E>.<step>
STATUS: <complete | stopped>
BACKEND HEALTH: <output of /api/health, or "not started">
SALIENCY SOURCE: <attention | policy_fallback | not tested>
NOTES: <any deviations from expected output, verbatim command output for failures>
```

Do not summarize. Do not editorialize. Paste raw command output for any failure.
