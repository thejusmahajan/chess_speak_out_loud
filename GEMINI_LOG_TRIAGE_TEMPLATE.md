# GEMINI LOG-TRIAGE TEMPLATE — Kaggle diagnostic run

Reusable spec. To delegate a log: "Gemini, triage `<LOGFILE>` per GEMINI_LOG_TRIAGE_TEMPLATE.md."
You READ the full log and REPORT structured findings. Do not edit code, run nothing.
**Quote actual log lines with their line numbers as evidence for every claim.** If a
marker is absent, write "NOT PRESENT" — never infer or invent it. Flag truncated/partial
logs. Numbers must be copied from the log, never estimated.

## What a HEALTHY run prints, in order (the success ladder)
1. `[cfg] MAX_GAMES=<n> LC0_WORKERS=<w> ... CSZERO_DATA_DIR=/kaggle/working/data`
2. `[input]` tree — weights should appear as `<DIR> ...pb` (Kaggle-extracted) + the inner file
3. `[weights] '...pb' is a DIR -> largest inner file ... (211 MB)` then `normalized ... search_weights.pb.gz (190.9 MB)`
4. `[lc0] found in working dir/dataset (validated)` (cached) OR `[lc0] compiling from source` (~6 min)
5. `[setup] vision.mode=attention`  ← MUST be `attention`, not `policy_fallback`
6. `[pool] starting worker 0 -> GPU 0`, `worker 1 -> GPU 1` (only when LC0_WORKERS>1)
7. `[hb ...s] stage=A|B|TS2 ...` with `GPU0:xx%` and `GPU1:xx%`
8. `[DONE] REAL run: <F> findings, <S> steer_findings | vision=attention | games=<g> moves=<m> | <secs>s`

## Known baseline & gates
- **Baseline (LC0_WORKERS=1): 213 findings, 263 steer_findings, games=30, moves=880, ~9352s.**
- **Identity gate:** a 2-worker run MUST reproduce **213 / 263** exactly (parallelism must not
  change evals). Report any deviation as a BLOCKER.
- **GPU-split gate (2-worker):** BOTH GPU0 AND GPU1 must show >0% util in the heartbeats.
  GPU1 flat at 0% = the split failed.

## Known failure families (name the one that fits, with evidence)
- Missing/mangled weights: `Is a directory`, `requires a network file`, `[input]` shows no net.
- Read-only FS: `OSError: [Errno 30] Read-only file system`.
- Vision broken: `NeuralVision attention unavailable` → `vision.mode=policy_fallback`.
- Vacuous done: `[DONE] ... 0s` with a Traceback above (crash disguised as success).
- Stale-backend drift: `TypeError: ... unexpected keyword argument` (e.g. gpu_id).
- GPU-split fail: two lc0 pids, GPU1 flat 0%, GPU0 VRAM near 15 GiB, "Not enough GPU memory to capture CUDA graphs".
- OOM: process killed / `exit 137`.
- Cancelled/incomplete: log ends mid-compile (`[NNN/330]`) or mid-stage with no `[DONE]` and no error = user cancelled or timed out, NOT a bug.

## Required output (structured)
1. **VERDICT:** SUCCESS / FAILED / CANCELLED / IN-PROGRESS (one word) + one-line why.
2. **Furthest stage reached:** init | A | B | TS2 | DONE, and the last wall-clock timestamp.
3. **Key numbers:** findings, steer_findings, vision.mode, games, moves, total secs — or "NOT PRESENT".
4. **GPU:** did BOTH GPUs light up? Per-GPU peak util% and peak VRAM MiB (quote a heartbeat line).
5. **lc0:** cached-and-validated, or compiled? Which weights file loaded (quote the line)?
6. **Error (if any):** exact message + log line number + which failure family above.
7. **Identity check (2-worker runs):** do findings/steer match 213/263? State match/mismatch.
8. **Recommendation to the leader:** 1–2 lines (what to do next), no code.

## Constraints
- Report only. Every claim cites a log line number + quotes the text. No fabricated numbers.
- If the log is partial/truncated, say so and report only what's present.
- Keep it tight — this is triage for the leader to act on, not prose.
