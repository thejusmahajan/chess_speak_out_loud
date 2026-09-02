# Audit of the expert review

**Auditor:** leader (Opus 5), 2026-09-02.
**Reviewing:** `ROUNDTABLE_2026-09-02_training_optimization_EXPERT_REVIEW.md`.

**Verdict: mostly ACCEPT. One verified bug that is worth more than everything else in it, one
correction to my round table that I got wrong, one recommended code block that must not be used as
written, and one domain error that would quietly destroy the point of the project.**

---

## 1. The multi-GPU bug — VERIFIED, and it is a real find

Re-read against the actual files, not the review's quotation:

```
kaggle_files/diagnose_on_kaggle.py:342  def make_engine_instance(worker_idx: int = 0) -> LC0Engine:
kaggle_files/diagnose_on_kaggle.py:346      if gpu_count > 1:
kaggle_files/diagnose_on_kaggle.py:347          uci_opts["Gpu"] = worker_idx % gpu_count
kaggle_files/diagnose_on_kaggle.py:434  pool = EnginePool(8, lambda: make_engine_instance(0))
backend/engine_pool.py:24               self._workers = [engine_factory() for _ in range(n)]
```

The factory takes no argument from the pool, and the lambda hardcodes `0`. **All eight workers get
`Gpu = 0`. The second T4 idles while the session bills for it.**

**Why this matters more than the review says.** It is not merely lost throughput — it would have
**corrupted the one measurement the rehearsal exists to produce**. Table 2 is parallel scaling at 8
workers. Run as written it would have reported roughly half the true aggregate, and we would have
concluded that pool scaling on Kaggle is poor and set the node budgets from a wrong number. A
silent bug inside the instrument, which is this project's oldest failure shape.

**The fix, minimally.** Do **not** change `EnginePool`'s signature — `Callable[[], Any]` is what
`backend/tests/test_engine_pool.py` constructs against, and a signature change breaks tests to fix a
caller. Fix the caller:

```python
_worker_seq = itertools.count()
pool = EnginePool(8, lambda: make_engine_instance(next(_worker_seq)))
```

Then **assert it worked** rather than trusting it: print each worker's resolved `Gpu` option, and
have the benchmark fail if the set of distinct GPU ids is smaller than `torch.cuda.device_count()`.
A GPU-affinity bug that is invisible is the same bug again.

**Structural note, and it is ours not the reviewer's:** `kaggle_files/` is in `.gitignore` (line 63)
and has no git history. A fix applied there is untracked and dies the next time the bundle is
rebuilt. The runner should live in the tracked tree and be *copied* into the bundle by
`scripts/build_kaggle_bundle.py`.

---

## 2. `bfloat16` on a T4 — the reviewer is right and my round table was wrong

My DeepMind voice said *"AMP with `bfloat16` or `float16`"*. Kaggle's accelerators are **T4
(Turing, SM 7.5)** or **P100 (Pascal, SM 6.0)**; hardware `bfloat16` arrives with Ampere (SM 8.0).
On a T4, `bfloat16` is emulated and slower than fp32. **Correction accepted** — on Kaggle the only
half precision worth using is `float16`. The P100 is worse still: no tensor cores at all, so
half precision buys bandwidth and nothing else.

---

## 3. Accepted without argument

- **Unpack once into a resident `uint8` tensor**, not per batch. The review's arithmetic is right:
  a per-batch shift on 8,192 rows allocates an intermediate `(8192, 18, 64)` int64 tensor =
  **75.5 MB** every step, churning the caching allocator. My round table offered both forms; the
  one-shot unpack should have been the recommendation and the per-batch shift the fallback.
- **The 11h15m watchdog.** Genuinely important and I had not thought of it. A hard 12-hour kill
  discards the working directory, so hours of warmed cache vanish with no artefact. A graceful
  `sys.exit(0)` after flushing is the difference between a resumable run and a lost day.
- **The EPD cache should not stay `.jsonl` at 3.6 GB.** Line-by-line Python parsing at session
  start is pure waste. SQLite with WAL is the right shape.
- **LC0 process/thread topology:** fewer processes, `--threads` inside them, a large shared
  `nncache`, and a minibatch large enough to fill the card. This agrees with the round table's LC0
  voice and is now the thing to measure rather than assume.
- **Headless "Save & Run All"**, never an interactive tab, for anything long.

---

## 4. The training code as written must not be used

The review's table says half precision must be *"`torch.float16` with `GradScaler`"* — and then the
code block does neither. It calls `model.half()` and hands fp16 parameters to `AdamW` with **no
`GradScaler` anywhere**.

**That is pure-fp16 training and it silently degrades.** Master weights in fp16 have ~10 mantissa
bits, so an update of order `lr × grad` added to a weight of order 1e-1 rounds to no change at all;
and `AdamW`'s default `eps=1e-8` is below the smallest normal fp16 (~6e-5), so the denominator term
underflows. The result is not a crash — it is a loss curve that looks plausible and a model that
learned less than it should have. **Use `torch.autocast('cuda', dtype=torch.float16)` with fp32
parameters and a `GradScaler`.** Keep the model in fp32; let autocast choose per op.

**Second defect in the same block.** `torch.compile(mode="reduce-overhead")` captures CUDA graphs,
which are shape-static, and the loop's last batch is ragged: 240,360 = 8,192 × 29 + **2,792**. That
shape change forces a re-capture every epoch, at best costing what the mode was meant to save.
Drop the last partial batch, or pad it — with 30 steps an epoch, dropping 2,792 samples per epoch
from a reshuffled permutation costs nothing.

**Third: the timings are predictions, not measurements.** *"Under 8 seconds"*, *"under 5 seconds"*,
*"40–60% fewer node evaluations"* — nobody in this exchange has run any of it on a T4. They are good
predictions and worth testing, and they must be recorded as predictions so that a slower result is
information rather than an embarrassment.

---

## 5. The domain error — and this one would have cost us the project's actual aim

The review proposes pruning candidate moves when *"a candidate's policy prior is below 1% **and** its
static value is > 150 cp worse than the principal variation"*, and calls this *"without sacrificing
tactical fidelity"*.

**Both halves of that filter select against exactly what this project exists to find.**

A sacrifice is, by construction, a move whose **static value is bad** — the material is gone and the
compensation only appears after search. And `metrics.py` already treats a **low policy prior** as a
*positive* signal of danger: `steer_w_policy_trap` weights the case where the sole saving reply has a
low prior. So a screen on low prior plus bad static eval is a well-designed detector for Tal moves,
used as a rule for throwing them away.

This is generic optimisation advice meeting a specific aim, and the aim loses silently. It would not
show up as an error; it would show up as a steering system that stopped finding sacrifices, months
later, with no failing test — the `had_tal_move` shape exactly.

**The round table's rule stands unchanged and is not negotiable:** a screen may decide **what gets
searched**; it may **never** produce a number that is reported; and its **miss rate against full
search is measured on a few hundred nodes before adoption**. If a screen is used at all, it must be
validated specifically on positions where `had_sharp_move` is true — the ones it is most likely to
throw away.

---

## 6. One economic correction

*"Kaggle allows 2 concurrent GPU sessions … completes in half the calendar time using 4 T4 GPUs."*

True about calendar time, and worth being clear-eyed about: **it does not create quota, it spends it
twice as fast.** Two concurrent 12-hour sessions consume ~24 of the ~30 weekly GPU-hours in a single
day. Given that the budget here is real money and Thejus is spending borrowed funds, concurrency is
for when we are confident the run is correct — not for the rehearsal.

Also, two sessions warming disjoint halves produce **two caches that must be merged**, which is
trivial for `.jsonl` (concatenate, dedupe on EPD) and a real operation for SQLite (`ATTACH` plus
`INSERT OR IGNORE`). Whichever store we adopt, the merge has to be written and tested before the
sharded run, not after it.

---

## 7. What changes as a result

1. **Fix the GPU-affinity bug in the caller, and assert distinct GPU ids at benchmark start.**
2. **Move the Kaggle runner into the tracked tree**; the bundle becomes a copy target.
3. **`float16` only, via `autocast` + `GradScaler`, fp32 parameters.** Never `model.half()` + Adam.
4. **Drop the ragged last batch** if `torch.compile(mode="reduce-overhead")` is used at all.
5. **Add the 11h15m watchdog** with a graceful flush and exit.
6. **Convert the EPD cache to SQLite/WAL**, and write the merge before any sharded run.
7. **Screening keeps the round table's rule**, and any screen is validated on `had_sharp_move`
   positions specifically.
8. **Every timing in the review is a prediction** until the rehearsal replaces it.
