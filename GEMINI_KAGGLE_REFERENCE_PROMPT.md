# TASK FOR GEMINI — Produce a Kaggle best-practices REFERENCE for this project

Write ONE markdown reference document, `KAGGLE_BEST_PRACTICES.md`, at the repo root. It is
a durable reference the leader (Claude) and the user will consult to fix a CLASS of Kaggle
problems we keep hitting, instead of patching each instance. Research + your own knowledge;
**cite official Kaggle docs where possible**, and mark anything version-dependent or
uncertain as **NEEDS-VERIFY** with the exact in-notebook command to check it (e.g.
`!free -h`, `!nvidia-smi`, `!df -h /kaggle/working`, `import psutil, os`). Concrete
commands/config over generic advice. Doc only — change no code, run nothing.

## Who this is for / what we run
A self-contained diagnostic (`colab/kaggle_diagnostic_run.py`) on a **Kaggle T4×2**
notebook: it compiles/loads the **lc0** chess engine, loads a **BT3 ONNX** net in PyTorch
for attention, and runs a multi-stage analysis (policy screen → node-limited MCTS search →
tactical steering) over 30 games. It can run 1 or 2 lc0 engines (a pool). One clean
single-engine run took ~2h36m.

## Our ACTUAL failure history (make the doc solve THESE, with named mitigations)
1. **exit 137 (OOM-killed) during the lc0 COMPILE**, at stage=init/GPU 0%. The build
   (`meson` + `ninja -j2`, which also builds gtest/gmock + `encoder_test`/`engine_test` +
   nvcc CUDA-fp16 kernels + LTO) ran the host out of RAM. (Earlier sessions DID compile
   fine — so it's near the memory ceiling and variable.)
2. **exit 137 / VRAM pressure at 2 engines:** two lc0 both landed on GPU0 → ~14.8/15.3 GiB
   VRAM, "Not enough GPU memory to capture CUDA graphs."
3. **`/kaggle/working` is wiped on Stop→Start**, so the ~6-min lc0 compile repeats every
   new session (and can OOM, per #1).
4. **Dataset auto-extraction mangles uploads:** a loose `X.pb.gz` was DECOMPRESSED and
   extracted into a DIRECTORY `X.pb/` containing the real file under another name → lc0
   got a directory path and hung ("Is a directory").
5. **Dataset versioning trap:** adding a new dataset version does NOT re-point the
   notebook; our uploaded `lc0` binary stayed invisible under `/kaggle/input`.
6. **`files.download` hangs** on Kaggle — retrieving outputs (e.g. `profile.json`) is awkward.

## Required sections in `KAGGLE_BEST_PRACTICES.md`
1. **Resource limits (T4×2), current values + how to verify in-notebook:** host RAM, per-GPU
   VRAM, vCPU count, `/kaggle/working` + `/kaggle/temp` disk, max session wall-clock, idle
   timeout, weekly GPU quota. Flag each as CITED or NEEDS-VERIFY with the check command.
2. **exit 137 / OOM — diagnosis & mitigation:** host-RAM vs GPU-VRAM OOM (how to tell them
   apart); how to watch RAM live; general mitigations.
3. **The lc0 compile-OOM specifically — ranked solutions:** e.g. build ONLY the `lc0` target
   (skip gtest/`encoder_test`/`engine_test`); `ninja -j1` vs `-j2` peak-RAM tradeoff;
   `ccache`; disabling LTO/tests via meson flags; limiting nvcc arch to sm_75 only; and the
   best solution — AVOID compiling by shipping a prebuilt binary. Give the concrete commands.
4. **Persisting a compiled binary across sessions:** how `/kaggle/working` reset works; the
   reliable way to store `lc0` in a Kaggle Dataset and ATTACH THE RIGHT VERSION so it appears
   under `/kaggle/input` (solve the versioning trap #5); the "Save Version" / output-to-dataset
   / Kaggle-API paths, with steps.
5. **Uploading binaries/gzips WITHOUT mangling (#4):** does wrapping in `.zip`/`.tar` prevent
   auto-extraction? how to ship a `.pb.gz` net so it stays a file; how to ship an extensionless
   binary intact. Concrete, tested-if-possible guidance.
6. **Runtime memory budgeting for 2 lc0 engines + PyTorch on T4×2:** keeping 2× lc0 (its
   `RamLimitMb`/`NNCacheSize`) + torch under the host-RAM cap; thread/process counts for
   4 vCPUs; pinning each engine to a distinct GPU; avoiding runtime exit 137.
7. **Reliable output retrieval (#6):** alternatives to `files.download` for pulling
   `profile.json` and logs out (Save Version outputs, output-to-dataset, Kaggle API/CLI).
8. **Session & GPU-quota hygiene:** avoiding wasted quota on recompiles; keeping a session
   alive; wall-clock/idle limits; when a restart is unavoidable.
9. **"Recommended setup for THIS project" — a checklist** the user can follow: dataset layout
   (nets + prebuilt lc0), how to attach/verify versions, the exact env/config to avoid OOM,
   and the run procedure that never recompiles.

## Constraints
- Cite Kaggle docs where possible; mark uncertain/changeable facts **NEEDS-VERIFY** + the
  in-notebook command to confirm. No fabricated limits stated as fact.
- Concrete commands/flags/steps, not platitudes. Tie each recommendation back to one of our
  6 failures where relevant.
- Doc only. STOP when written.
