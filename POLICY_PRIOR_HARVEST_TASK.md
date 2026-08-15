# WORKER TASK — Policy-prior vs search harvest ("intuition vs calculation")

Harvest the data for a blog post comparing **what the network guesses before it
thinks** against **what it plays after it thinks** — and against **what Thejus
actually played** in his own games.

## Your job is DATA, not prose

You are producing a script, a dataset, and a table of measured numbers.

**You must NOT write the blog post, an interpretation, a narrative, or any
conclusion about what the numbers mean.** The leader writes all prose. Prior
worker deliveries on this project were rejected for fabricating content that
looked like results; do not summarise findings in words, do not characterise a
number as "interesting" or "as expected", and never invent a value you did not
compute. If a number surprises you, report the number.

Every figure you report must be reproducible by re-running your script.

**ACCURACY IS NON-NEGOTIABLE.** Work checkpoint by checkpoint. Each checkpoint
has a verification command whose real output you paste into your report before
moving on. If a checkpoint fails, STOP and report — do not fix forward.

---

## 0. Environment and read-first

Run everything with the conda env Python — **not** system Python, which has no torch:

```
C:\Users\Admin\miniconda3\envs\cszero\python.exe
```

| File | Why |
|---|---|
| `backend/engine_manager.py` | `LC0Engine`. `get_policy_distribution(fen, nodes=1)` at line 239 is the prior; `analyze(...)` at line 356 is the search. |
| `backend/app.py` lines 60–80 | How the engine is constructed and started. |
| `backend/training/puzzle_regime.py` | Style reference for a standalone module with a CLI. |
| `docs/writeup_attention_frame_bug.md` | The companion post. Same network, different head. |

### Weights provenance — the thing you must not get wrong

`app.py` constructs `LC0Engine` with **no `weights_path`**, so it runs LC0's
default network (791556). The attention post is about **BT3**. A harvest on the
default weights would silently describe a *different network* and make the post
false.

**You must pass BT3 explicitly:**

```python
engine = LC0Engine(
    engine_path=str(ROOT / "engine" / "lc0.exe"),
    weights_path=str(ROOT / "engine" / "BT3-768x15x24h-swa-2790000.pb.gz"),
)
await engine.start()
```

Record the resolved weights filename in the output JSON metadata. Every reported
number is about that file or it is worthless.

### Do NOT touch

`backend/training/metrics.py`, `relational_facts.py`, `attempts.py`,
`neural_vision.py`, `engine_manager.py`, `puzzle_regime.py`, `puzzle_sets.py`.
Import from them; do not edit. If you believe one needs a change, STOP and report.

Windows notes: the engine runs on its own ProactorEventLoop thread — just use
the async API as `app.py` does, never construct your own loop around it. Use
`store._write_json_atomic` for writes, never bare `os.replace`.

---

## Checkpoint 1 — Verify the primitives

Before harvesting anything, prove the two measurements behave.

Write `scratch/probe_policy.py` that starts the engine on BT3 weights and, for
the **starting position** and one middlegame FEN, prints:

- the top 6 entries of `get_policy_distribution(fen, nodes=1)` with `p`
- the sum of `p` over **all** returned entries
- `analyze(fen, nodes=20000)` best move and evaluation

### ✅ Verification 1 — paste the real output

Expected sanity conditions (state pass/fail for each):
1. On the start position the prior's top moves are opening moves (d2d4 / e2e4 /
   g1f3 / c2c4 territory), **not** a flat distribution.
2. `sum(p)` over all legal moves is close to 1.0 — report the actual value.
3. `nodes=1` returns `n` values of 0 or 1 for essentially every move. If many
   moves show large `n`, the search is not actually disabled — **STOP and report**,
   because then you are not measuring a prior at all.
4. `analyze(..., nodes=20000)` returns a plausible best move and a centipawn eval.

---

## Checkpoint 2 — Timing pilot

Measure before you commit to a sample size.

Extend the probe to time 20 positions end-to-end (prior + search each). Report
seconds per position for `nodes=1` and for `nodes=20000` separately.

Then choose N so the full harvest finishes in **under 3 hours**, and state the N
you chose and the arithmetic. If 20k nodes is too slow, drop to 10000 and say so
— do not silently change it.

---

## Checkpoint 3 — The harvest script

Write `backend/training/policy_prior_harvest.py`.

**Positions:** from `games_of_derdiedasdie/lichess_derdiedasdie_2026-07-21.pgn`,
games where `derdiedasdie` is a player. Take positions where **it is his turn**,
ply 16–80, at least 10 pieces on the board. Sample N of them with a fixed seed
(`random.Random(20260815)`) so the run is reproducible.

**Per position record exactly this schema:**

```json
{
  "game_site": "https://lichess.org/xxxx",
  "ply": 34,
  "fen": "...",
  "user_color": "white",
  "played_uci": "g1f3",
  "played_san": "Nf3",
  "prior": [{"uci": "...", "san": "...", "p": 0.31, "n": 0}, "... top 10 ..."],
  "prior_top1_uci": "...",
  "searched_best_uci": "...",
  "searched_eval_cp": 42,
  "played_eval_cp": -65,
  "prior_rank_of_searched_best": 3,
  "prior_p_of_searched_best": 0.08,
  "prior_rank_of_played": 1,
  "prior_p_of_played": 0.31
}
```

Definitions, so there is no ambiguity:

- **`prior_rank_of_X`** — 1-based index of move X in the prior sorted descending
  by `p`. If X is absent from the returned list, record `null`, and count those
  separately; never record 0 or a guess.
- **`searched_eval_cp`** — evaluation after searching the position, from the
  **side to move's** point of view. `analyze()` returns White's point of view —
  negate it when Black is to move, and say in your report that you did.
- **`played_eval_cp`** — same convention, for the position *after* his move
  (i.e. push the move, analyse, then negate appropriately so it remains from his
  point of view). Mate scores (`"M5"` / `"M-3"`) must be mapped to a fixed large
  magnitude (±10000) — state the mapping you used.
- **`eval_loss_cp`** = `searched_eval_cp - played_eval_cp`, clamped at 0 below.

Write results to `data/policy_prior/harvest.json` with a `meta` block containing:
weights filename, node counts used, N, seed, script git commit, timestamp.

Resume support: if the output file exists, skip positions already recorded. A
3-hour run must survive an interruption.

---

## Checkpoint 4 — Metrics (compute only, do not interpret)

Add a `report` subcommand printing exactly these, as numbers:

1. **Overturn rate** — fraction where `prior_top1_uci != searched_best_uci`.
2. **Rank histogram** — distribution of `prior_rank_of_searched_best`
   (counts for 1, 2, 3, 4–5, 6–10, >10, null).
3. **Prior mass on the searched best** — mean and median
   `prior_p_of_searched_best`; also the same split by whether it was overturned.
4. **His agreement with each** — fraction where `played_uci == prior_top1_uci`,
   and fraction where `played_uci == searched_best_uci`.
5. **The blunder subset** — positions with `eval_loss_cp >= 100`. For that subset
   report: n, and the fraction where `played_uci == prior_top1_uci`, plus mean
   `prior_p_of_played`. Report the same two numbers for the non-blunder subset
   so they can be compared.
6. **Sanity counts** — positions harvested, positions skipped and why, any
   `null` ranks.

Print as a plain table. **No commentary.**

### ✅ Verification 4

Paste the full `report` output, and separately paste **5 randomly chosen raw
records** from the JSON so the leader can spot-check the metrics against them.

---

## Checkpoint 5 — Cross-check against the ONNX path (diagnostic)

There is an open question about `NeuralVision.evaluate_batch`: on the FEN

```
1k1r4/1pp3pp/8/1Nnn3q/2P2pbB/P4N2/4BPPP/R3K2R b KQ - 1 19
```

it returned `value=-1.000`, `wdl=[0,0,1]` and a near-uniform policy (max 0.043),
while the same code on the start position looks correct (value 0.031, d2d4 0.156).

For **20 positions from the harvest**, print side by side:
- the engine's prior top-3 (`get_policy_distribution`, BT3 weights)
- `neural_vision.evaluate_batch([fen])[0]["policy"]` top-3, plus its `value`/`wdl`

Report how many of the 20 agree on the top-1 move, and list every position where
`wdl` is exactly `[0,0,1]` or `[1,0,0]` or the max policy `p` is below 0.05.

**Do not diagnose the cause.** Report the numbers and stop.

---

## Checkpoint 6 — Report

Write `POLICY_PRIOR_HARVEST_REPORT.md` at repo root containing:

1. Files created, with `file:line` for the key logic.
2. Pasted output of **all verifications** (1, 2, 4, 5).
3. The weights filename and node counts actually used.
4. Wall-clock time of the full run and the final N.
5. Anything you could not do, or deviated from — state it plainly.

**STOP. Do not push. Do not write the blog post. Do not interpret the results.**

---

## Anti-patterns that will fail review

- Writing any prose about what the numbers mean.
- Running on default weights instead of BT3, or not recording which was used.
- Reporting a metric you did not compute, or rounding away a surprising value.
- Treating `analyze()`'s White-POV eval as side-to-move POV.
- A harvest with no resume support that dies at hour two.
- Editing `engine_manager.py` or `neural_vision.py` instead of importing them.
- Claiming a checkpoint passed without pasting its real output.
