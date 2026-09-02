```
Brief-ID:      2026-09-01_kaggle-gpu-profile-regeneration
Written:       2026-09-01
Target repo:   chess_speak_out_loud
Route:         Antigravity (full workspace)
Type:          preparation + rehearsal -- NOT the full run
Blast-radius:  the (gitignored) kaggle_files/ bundle, plus one new script
Reversibility: trivial; nothing in the tracked tree is modified
Failure-mode:  SILENT -- a GPU run that quietly falls back to CPU, or to mock mode, burns the
               week's Kaggle quota and produces a profile that looks fine
```

**Why this before the interview?** The interview is still the live item. This is the unblock for a
regeneration Thejus has asked for that **cannot be done on his machine at all** — measured below —
and the preparation is free.

---

## 1. INTENT

*(Intent outranks instructions. If any instruction below conflicts with this paragraph, the intent
wins — stop and report. Doing so is a success, never a boundary violation.)*

Regenerating `data/training/profile.json` on this laptop is not viable. **Get the run onto Kaggle's
GPUs**, in two stages: first a small rehearsal that proves the bundle runs end-to-end and
**measures how fast LC0 actually is on a T4**, then — only after the leader has set the node budgets
from that measurement — the full run.

**This brief covers the rehearsal only.** Do not attempt the full run.

---

## 2. THE MEASUREMENTS THAT MOTIVATE THIS

Taken on Thejus's machine, 2026-09-01, not recalled:

| fact | measured |
|---|---|
| LC0 backend here | **BLAS / DNNL, 2 cores, 4 threads. No GPU.** |
| throughput | 400 nodes → **3.64 s/position**; 800 → 9.66 s; 1600 → 20.77 s (**≈ 100 nodes/s**) |
| production budgets | `confirm_best_seconds: 6.0` + `confirm_played_seconds: 3.0` per flagged move |
| cold cost, 25 games | Stage A 95 s; Stage B **10.2 s per flagged move** (77 timed) — both measured |
| per-game cold cost | Stage A+B ≈ 1.4 min/game **measured**; ≈ 8.2 min/game **including a PROJECTED TS2 term** (731 nodes × 4 candidates × ~3 s). TS2 was never timed — the run was stopped before it began. Do not quote 8.2 as measured. |
| corpus | `lichess_derdiedasdie_2026-07-21.pgn` = **9,000 games**, 8,617 of them 2+1 bullet |
| decision nodes after the 20 s clock filter | **228,020** of 272,974 user moves |
| full-corpus projection on this machine | **≈ 51 days of continuous engine time** |

**The structural point, and the reason the budgets must change:** the current budgets are
*time*-limited. A GPU does not make a 6-second search finish sooner — it makes it deeper. With
time-limited budgets the only speed-up Kaggle offers is worker parallelism (8×), which turns 51 days
into ~6 days: still impossible inside a 12-hour session cap.

**Node**-limited search is what converts GPU speed into wall-clock savings, and it is already this
project's decided doctrine (`LEADER_BIBLE.md` §4: *"Node-limited search … Hardware-independent
quality; GPU speed becomes wall-clock savings"*). `LC0Engine.analyze(..., nodes=N)` already
implements it — `backend/engine_manager.py:356-371` — and `metrics.TrainingConfig` already carries
`confirm_best_nodes` / `confirm_played_nodes`, both currently `None`.

**⚠ The EPD cache is keyed by position only, NOT by budget or net** (`LEADER_BIBLE.md` §5,
cache-key family). `data/training/cache/*.jsonl` currently holds 8,845 entries computed at 6 s/3 s.
The moment we switch to node budgets those entries are a different measurement wearing the same
key. **The cache must be cleared when the budget changes — but not before the leader says so, and
not by you.**

---

## 3. WHAT YOU MAY TOUCH

```
kaggle_files/                     (the whole bundle -- it is gitignored, so it is not in git)
scripts/build_kaggle_bundle.py    (new, if one does not already exist)
agents/reports/2026-09-01_kaggle-gpu-profile-regeneration_REPORT.md
```

**Do not modify anything under `backend/`, `data/`, `docs/` or `state/`.** In particular **do not
change `backend/training/metrics.py`** — it is leader-owned, and the node budgets are the leader's
decision after your measurement, not before it.

---

## 4. STEPS

### Step 1 — refresh the bundle from HEAD

`kaggle_files/` was assembled on 2026-07-25 and is gitignored, so it has drifted from the tracked
tree. Rebuild it from current HEAD: `backend/`, `scripts/`, `engine/` (lc0 + weights + `bt3.onnx`),
`games_of_derdiedasdie/`, `requirements.txt`, `pyproject.toml`, `diagnose_on_kaggle.py`,
`README_KAGGLE.md`.

Write the copy step as `scripts/build_kaggle_bundle.py` so it is repeatable rather than manual.

**CHECKPOINT 1.** Paste the file listing of the rebuilt bundle with sizes, and the SHA-256 of
`engine/lc0.exe` and the weights file both inside the bundle and in the repo — they must match.

---

### Step 2 — the named trap: weights arriving as a directory

The last Kaggle attempt (2026-07-25) died because **Kaggle unpacks loose `.gz` uploads into
directories**, so lc0 was handed a directory where it expected `791556.pb.gz` and hung with
*"Is a directory"*. A fix was written but **was never confirmed to work end-to-end**. Treat it as
unproven.

In `diagnose_on_kaggle.py`, before the engine starts:

1. Resolve the weights path. If it is a directory, descend until a real `.pb.gz` file is found and
   use that.
2. Assert the resolved path is a file and is larger than 1 MB.
3. **Fail loudly** with the resolved path printed if either check fails. Never continue.

---

### Step 3 — make GPU-or-nothing explicit

The silent failure that would waste the week's quota is a run that quietly proceeds on CPU or in
mock mode. Add a preflight that **aborts** unless all three hold, printing each:

1. `torch.cuda.is_available()` is True, and the device name and count are printed.
2. lc0's own startup banner reports a **CUDA/cuDNN** backend — not BLAS. Capture lc0's stderr and
   assert the backend line does not contain `BLAS`.
3. `engine.mock_mode is False` after `start()`.

---

### Step 4 — the throughput measurement (this is the point of the rehearsal)

Add a cell/function `measure_throughput()` that runs **before** any diagnosis, on these three
positions, and prints a table:

```
r1bq1rk1/pp2bppp/2n1pn2/2pp4/3P1B2/2PBPN2/PP1N1PPP/R2Q1RK1 w - - 0 9
r2q1rk1/1b1nbppp/p2ppn2/1p6/3NPP2/1BN1B3/PPPQ2PP/2KR3R w - - 0 12
2rq1rk1/pb2bppp/1p2pn2/8/2BP4/P1N1PN2/1P3PPP/R2Q1RK1 w - - 0 14
```

For each of `nodes = 400, 800, 1600, 5000, 20000`: `analyze(fen, multipv=2, nodes=N)`, timed,
averaged over the three positions, **discarding a warm-up pass first** (the NN cache makes a repeat
of the same position much cheaper, which is how a misleading number gets produced).

Report seconds/position and nodes/second at each budget, for **1 worker**.

Then repeat at `LC0_WORKERS=8` over 24 distinct positions to measure the pool's aggregate
throughput — parallel scaling on 2×T4 is the number that sizes the whole run, and it will not be 8×.

**CHECKPOINT 2 — the deliverable.** The two tables. The direct comparison against this laptop
(400 nodes → 3.64 s/position) is what the leader uses to set the budgets.

---

### Step 5 — the rehearsal run

`LC0_WORKERS=1`, `MAX_GAMES=30`, **time budgets unchanged** (do not set node budgets yet — this run
must be comparable to the local one). Diagnose the newest 30 games of `derdiedasdie`.

Then **stop**. Report:

- wall clock for the 30 games, split by stage, against this laptop's **measured** Stage A+B
  ≈1.4 min/game (the ≈8.2 min/game total carries a projected TS2 term — your run is what finally
  measures it);
- `games_analyzed`, `len(findings)`, `len(steer_findings)`, `steer_budget_exhausted`;
- whether `steer_findings[0]` carries `had_sharp_move` (it must) and **not** `had_tal_move`;
- the ECO keys present in `steer_summary` (they must be real ECO codes, not `"???"`).

---

### Step 6 — session persistence, written but not exercised

A Kaggle GPU session is capped at ~12 hours and the weekly GPU quota is finite, so the full run will
span sessions. Implement, and describe in the report:

1. At the end of a run, copy `data/training/cache/*.jsonl` and `data/training/profile.json` to
   `/kaggle/working/` so they are saved as notebook output.
2. At the start of a run, if an input dataset containing a previous cache is mounted, copy it in
   **before** the engine starts, and print the entry count restored.

Because the EPD cache makes repeats free, a resumed session then costs nothing for what is already
done. **Verify the count printed matches the file** — a resume that silently restores 0 entries
looks identical to a fast run.

---

### Step 7 — how the full run is batched (design it now, do not run it)

A Kaggle GPU session is capped at ~12 h, so the full run must span sessions. **The batching scheme
is not "one profile per chunk" — that would produce N unmerged profiles.** It is:

1. **Warming sessions.** Each session diagnoses a disjoint chunk of games. Its only purpose is to
   fill the EPD cache. Its profile output is discarded.
2. **One assembly pass.** The last session submits **all** the games at once. Every position is a
   cache hit, so it does no engine work and emits a single coherent profile.

This is sound because cached positions cost nothing and do not consume `steer_search_budget` —
`try_reserve_search()` is only reached on a cache miss (`pipeline.py`, TS2 node body).

**Measured anchor for the assembly pass:** a fully-cached 25-game diagnosis on Thejus's *laptop*
took **32.4 s** end to end. Extrapolated, 9,000 games ≈ **3.2 h** warm. Treat that as an
extrapolation, not a measurement, and report the real figure when it happens.

**Two things to size and state in your report, both consequences of scale:**

- **Cache volume.** 8,845 entries = 35 MB today. The full corpus implies roughly 900k entries
  ≈ **3.6 GB** to shuttle in and out of Kaggle each session. State whether that fits the notebook
  output limit and how long the copy takes.
- **Profile size.** 100 games → 1.9 MB. 9,000 games extrapolates to **~170 MB** of
  `profile.json`, loaded whole by `store.load_profile()`. Say whether anything downstream chokes
  on that; do not fix it, just report it.

**Batching solves the session cap. It does not make the run cheaper** — the total engine work is
unchanged. Cost is reduced only by node budgets and GPU throughput, which is what Step 4 measures.

---

## 5. REPORT

`agents/reports/2026-09-01_kaggle-gpu-profile-regeneration_REPORT.md` — every checkpoint's real
pasted output, the two throughput tables, and:

> **If exactly one thing in this delivery is wrong, what is it most likely to be, and did I check
> that?**

A non-empty "could not check" section is expected — you cannot run Kaggle yourself, so say plainly
which steps are written-but-unexercised and which were actually executed.

---

## 6. STOP AND ASK

Not covered: the full 9,000-game run; setting node budgets; clearing or editing any file under
`data/training/cache/`; modifying `backend/training/metrics.py` or anything else under `backend/`;
committing; buying Kaggle compute.

**Thejus runs the notebook on Kaggle — you prepare it.** After Step 5 the leader sets the node
budgets from your measured numbers, and only then does the full run get specced.
