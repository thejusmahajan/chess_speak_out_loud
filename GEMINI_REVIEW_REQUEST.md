# TASK FOR GEMINI — Thorough pre-run review of the Kaggle diagnosis path (REPORT ONLY)

You are the **second eye** before we spend another ~6-min lc0 compile on Kaggle.
Use your token pool: go through EVERY detail of the code path the run will execute.
**You are NOT implementing.** Do not edit any `.py`. Do not run anything. Your only
output is ONE markdown file, `KAGGLE_RUN_REVIEW.md`, at the repo root. The leader
(Claude) will audit your findings line-by-line and decide GO / NO-GO. A confident
"looks good" with no file:line evidence is worthless here — cite everything.

---

## Mission context (what the run is)
We are trying to land **ONE clean end-to-end diagnosis run on Kaggle** (2×T4). Config:
`LC0_WORKERS=1`, `MAX_GAMES=30`. The backend is imported **from the Kaggle dataset
mount** (`/kaggle/input/...`, which is **READ-ONLY**); only `/kaggle/working` is
writable and it **resets every session**. We have already clawed through four layered
failures (async hang → oversubscription → missing deps → weights). The LATEST run got
all the way into `run_diagnosis` and died creating its cache dir on the read-only mount.

## Read these FULLY before reviewing (ground yourself, don't guess)
- `LEADER_BIBLE.md` — especially **§4 decisions (do not relitigate)**, **§5 failure
  catalog**, **§5b the Kaggle failure family**. These name the exact trap classes below.
- `colab/kaggle_diagnostic_run.py` — the instrument that runs the whole thing.
- `backend/training/pipeline.py` — `run_diagnosis()` is the entry point the run executes.
- `backend/training/store.py` — `EpdCache`, `DATA_DIR`, `TRAINING_DIR`, `_ensure_dirs`.
- `backend/engine_manager.py` — how lc0 is spawned, and the `--weights=` flag it passes.
- `backend/neural_vision.py` — the `bt3.onnx` load that FAILED (`policy_fallback`).
- `backend/training/metrics.py` — **leader-owned, READ-ONLY.** If you suspect a bug,
  file it in `QUESTIONS_FOR_LEADER.md`. Do NOT propose editing it.

## Environment facts (ground truth — do not contradict)
- Kaggle **T4×2 (sm_75), ~13 GB RAM, 4 vCPUs.** `/kaggle/input` READ-ONLY;
  `/kaggle/working` writable but wiped each session.
- lc0 `v0.33.0-dev` compiled from source; backend `cuda-fp16`; search **node-limited**.
- Diagnosis net = **BT3-768x15x24h-swa-2790000** (per §4 the blindness metric is DEFINED
  on this net's policy; 791556 is the live-app net, NOT the diagnosis net).
- **Kaggle auto-decompressed the uploaded `.pb.gz` → the weights arrive as raw `.pb`.**
  lc0 loads a network by magic bytes, not extension, so `.pb` is valid.
- Just-applied fixes (audit them, section D): `_find_weights()` now accepts `.pb`+`.pb.gz`
  BT3-first; `CSZERO_DATA_DIR` is `setdefault`ed to `/kaggle/working/data` at the top of
  the diagnostic (BEFORE backend import) to escape the read-only mount.

## What the last run showed (the evidence)
- lc0 launched fine (`v0.33.0-dev`, "Search algorithm: classic").
- `WARNING NeuralVision attention unavailable (Could not load model at .../engine/bt3.onnx.)`
  → `vision.mode=policy_fallback` (NON-fatal; the run continued).
- `[DONE] completed 30 games in 0s` printed, THEN a traceback.
- Fatal: `OSError: [Errno 30] Read-only file system: '.../cszero-kaggle-dataset/data'`
  at `store._ensure_dirs → os.makedirs`, called from `EpdCache("policy")` in
  `run_diagnosis` (`pipeline.py:138`).

---

## THE REVIEW — find and rank every issue in these buckets

### A. Read-only-filesystem sweep  ← HIGHEST VALUE, do this most carefully
`store.py` is now redirected via `CSZERO_DATA_DIR`, but the SAME bug class almost
certainly recurs. **Trace every disk WRITE the executed path performs** and confirm its
target lands under `/kaggle/working` (writable), NOT under `ROOT_DIR`/`__file__`/the
dataset mount (read-only). At minimum check, with file:line and the RESOLVED Kaggle path:
- Where is the resulting **profile / diagnosis output** written? Is that path writable?
- lc0 scratch/log files; any LC0 disk cache; tablebase/syzygy dirs.
- onnx / onnx2torch / torch-hub / HF caches (could this be WHY bt3.onnx failed to load?).
- `jobs/`, `drills/`, `cache/`, metrics/log dirs, the `data/.gitignore` write in `store._ensure_dirs`.
- openings file, any repertoire output.
Report each as: **write-site (file:line) → resolved path on Kaggle → writable? → fix.**

### B. Silent-wrong-answer risks (bible's vacuous / POV-frame / cache-key families)
- **Net identity:** trace `engine_manager` → confirm the run actually loads **BT3 (.pb)**,
  not `791556`. Does ANY code branch on the `.pb.gz` vs `.pb` extension and misbehave on `.pb`?
- **`[DONE] completed 30 games in 0s`** — is that real, or does the game loop no-op /
  short-circuit? Trace the loop that produces that count. 0s for 30 games is a red flag.
- **Cache-key family (§5):** cache is EPD-keyed, NOT net/budget-keyed. On a fresh
  `/kaggle/working` the cache starts empty (probably fine) — CONFIRM there's no stale cache
  shipped inside the dataset that could poison results.
- **POV/frame family (§5):** any black-to-move handling in this path that could invert cp
  signs or mirror boards? Flag call sites that touch eval signs or board orientation.
- **TS2 must witness every test (§4/vision backlog):** confirm `run_diagnosis` produces
  BOTH findings AND steering output, and that `policy_fallback` (broken onnx) does NOT
  silently null the steering or corrupt the diagnosis.

### C. Remaining crash / hang risks before a real `[DONE]`
- **Import order:** verify `store.py` reads `CSZERO_DATA_DIR` at import and that the
  diagnostic sets it BEFORE `backend.training.store` is first imported (else the redirect
  is a no-op). Quote the import line and the setdefault line.
- **Memory (§5b, exit 137 = OOM):** single engine on a 13 GB / 4-vCPU box — are
  `LC0_NN_CACHE_SIZE` / `LC0_RAM_LIMIT_MB` set sanely, or defaulted dangerously? Any thread
  fan-out (engine threads × workers) that exceeds 4 vCPUs?
- **Subprocess:** UCI handshake / pipe-buffer deadlock risk; terminal-position guards
  present at ALL THREE engine call sites (§4)?
- **The onnx failure root cause:** WHY did `bt3.onnx` fail to load — read-only cache dir?
  missing `onnxruntime`? onnx opset / version mismatch? Is `policy_fallback` genuinely safe?

### D. Audit the just-applied fixes
- `_find_weights()` (.pb/.pb.gz, BT3-first ordering) — correct and complete?
- `CSZERO_DATA_DIR` `setdefault` placement — provably before backend import?
- `[input]` glob adding `".pb"` — any false-positive matches (e.g. does it also grab the
  lc0 binary or unrelated files)?

---

## Output format — `KAGGLE_RUN_REVIEW.md`
1. **Findings table**, ranked most-severe first:
   `ID | Severity | file:line | Problem | Evidence (quote the actual line) | Proposed fix (DESCRIBE — do NOT apply)`
   Severity ∈ {**BLOCKER** (will crash or yield a wrong diagnosis at n=1/30), CORRECTNESS,
   PERF, COSMETIC}.
2. **Read-only write-site table** (from bucket A).
3. **NEEDS-CHECK list** — anything you could not verify from the code alone.
4. **Bottom line:** GO / NO-GO for the next run, and the exact BLOCKERs that must clear first.

## Constraints (the leader will verify these)
- **REPORT ONLY.** No code edits, no "I went ahead and fixed…", no running anything.
- Every finding MUST cite `file:line` and quote the evidence line. No generic advice.
- Label speculation as speculation; use **NEEDS-CHECK** when unsure; never invent behavior
  you didn't read. If a claim depends on unseen code, say so instead of asserting.
- Do NOT touch `metrics.py`; route any concern to `QUESTIONS_FOR_LEADER.md`.
- **STOP when the md is written.** Do not proceed to implement anything.
