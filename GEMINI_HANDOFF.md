# HANDOFF → Gemini 3.6 Flash (High) — continue the GPU diagnosis work

The leader (Claude) is out of tokens until reset. You have a large token budget.
**That is exactly why you must read this whole file and obey the guiding principle
below before touching anything.** Abundant tokens without an anchor is how you
"helpfully" steer off-course and break things. Stay anchored in the detail.

---

## 🧭 GUIDING PRINCIPLE (read twice) — DETAIL DECIDES THE COURSE
The dense, deliberate detail in our design docs **is** the plan. It is not
background reading; it is the specification you execute against. Therefore:

1. **Do not freelance.** Do not invent a new direction, refactor for taste, or
   "improve" beyond the task. Every change must trace to a documented decision in
   `docs/discussion_5_*.md`, `docs/discussion_6_*.md`, `POST_VALIDATION_BACKLOG.md`,
   or this file. If it isn't written down, it isn't approved.
2. **When a detail is missing or ambiguous, STOP and write the question** into a
   `QUESTIONS_FOR_LEADER.md` file — do not guess and proceed. A wrong guess made
   confidently is the most expensive thing you can do here (it already cost us: a
   *fake* batched loop that looked right, and a fix that only closed 1 of 3 crash
   doors). Guessing burns the user's finite compute units on invalid runs.
3. **Prove everything.** No change ships without a **mutation-checkable test**
   (break the guard → the test must fail). For batched/GPU work the proof is
   `batched == serial within tolerance`. For pipeline changes the proof is
   `findings/steer_findings do not degrade` vs a saved baseline.
4. **Scope is a hard wall.** Touch only the files a task names. `backend/training/
   metrics.py` is **leader-owned** — do not edit it. If you think you must, that's a
   `QUESTIONS_FOR_LEADER.md` entry.
5. **Small, verified commits**, message ending `Co-Authored-By: Claude Opus 4.8`.
   The suite must stay green:
   `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests/ -q`
   → baseline **135 passed, 5 skipped**. BT3 tests: prefix `RUN_SLOW_BT3=1`.

Read, in order, before working: this file → `MEMORY.md` →
`WORKER_AGENT_COOKBOOK.md` → `docs/discussion_6_filling_the_machine.md` →
`docs/discussion_5_saturating_the_a100.md`.

---

## Where we are (branch `windows-dev`, HEAD ~`33260b7`)
Goal: from a player's PGN, diagnose weaknesses + build a training repertoire.
We're **validating a 30-game subset (`test_subset.pgn`) on a Colab A100** →
`data/training/` → `training.zip` → check the UI (repertoire, puzzles, **tactical
steering**). Notebook: `colab/diagnose_on_gpu.ipynb`. Compute units are finite
(~39) — do not burn them on unvalidated runs.

**Working + committed:** BT3 on `cuda:0` (device-aware `NeuralVision`); batched
`saliency_absolute_batch` (38×) + `evaluate_batch` (value/policy/wdl, 3 ms/pos),
both leader-verified + guarded; node-limited search + `BT3_BUDGET` high/low toggle;
**a1a1 terminal crash fixed** at all 3 lc0 call sites; `VerboseMoveStats` leak
fixed; progress bars fixed; validated-lc0 cache; Cell 3 always-pulls via Colab
Secrets `GH_TOKEN`; outputs saved to Drive (`files.download` hangs).

## Immediate task (finish what's running)
Let Cell 6 (30-game diagnosis) → Cell 8 (repertoire/gems/trees/drills) → Cell 9
(`training.zip`) complete. User loads it locally and checks the UI. Fix what the UI
reveals — **root-cause only**, with a test. Save the resulting `steer_findings` and
`findings` counts as the **baseline** every later optimization must not degrade.

---

## THE COURSE (from `docs/discussion_6_filling_the_machine.md` — this is the plan)
The A100 is ~10% used (8.5/80 GB GPU, 5.8/167 GB RAM) because the pipeline is
sequential/latency-bound. Gukesh's demand is **depth + breadth + sight**, not merely
speed. Execute the six levers **in this gated order** — each is a spec'd task with a
findings-not-degraded gate; do NOT reorder or skip the gates:

1. **Lever 1 — Harvest-then-batch wide screen** *(do first: highest leverage, near
   quality-neutral).* Restructure: collect ALL decision positions + candidates into
   RAM, then run `evaluate_batch` in **huge batches (thousands)** for the corpus-wide
   policy/candidate screen. Fills the 80 GB. **Gate:** screen output reproduces the
   current per-position policy/eval; `steer_findings` unchanged on the subset.
2. **Lever 3 — Colossal NN cache** *(do alongside 1: config-only).* Raise lc0
   `NNCacheSize` to tens of millions and `RamLimitMb` to tens of GB (in
   `engine_manager` UCI options and/or Cell 5). **Gate:** evals identical; verify no
   drift; measure the transposition hit-rate win.
3. **Lever 2 — Parallel lc0 workers** for the deep-search crux (8–16 processes
   sharing the GPU). **Gate:** per-worker evals identical to single-process; wall-
   clock (and compute units) drop.
4. **Lever 5 — fp32 / ensemble on the crux only.** **Gate:** eval stability;
   findings not worse.
5. **Lever 6 — Tal rollout furnace** on the sharpest flagged nodes (bounded N/depth
   to fit the unit budget). New signal; validate it's meaningful, not noise.
6. **Lever 4 — Activation harvesting ("sight": suppressed-win / vision features).**
   Only **after** UI validation; research-y; prototype in isolation. Ties to
   `docs/research_learned_lookahead.md` and `POST_VALIDATION_BACKLOG.md` (B1/B2).

Also pending from Discussion 5, gated: **Opt #2 TS2 `evaluate_batch` screen** (deep
search only on the crux) — it changes the *narrowness* signal, so implement behind a
flag and diff `steer_findings` old-vs-new before default. Deferred (see
`TERMINAL_REVIEW_NOTES.md`): Stockfish terminal guard; single-choke-point for engine
calls. **Standing requirement: TS2 / tactical steering runs in EVERY test.**

## Gotchas that already bit us (respect them)
- **Stale code:** a runtime restart keeps `/content/repo`; confirm Cell 3 prints the
  right `repo at: <hash>`. Stale `import` also lies — restart the runtime.
- **Cache vs budget:** `data/training/cache/` is EPD-keyed, NOT budget-keyed. If you
  change `BT3_BUDGET` (or node counts), **delete the cache first** or you reuse stale
  evals and the comparison is meaningless.
- **`files.download` hangs** → outputs go to Drive / the Colab file browser.
- **Private repo** needs `GH_TOKEN` (read-only fine-grained PAT) in Colab Secrets.

## How to spec a task for yourself (mirror the leader's style)
For each lever, before coding, write a short spec: exact files, pinned data shapes,
numbered requirements, the enumerated tests (each a real guard), the run command,
and the gate. Then implement, run the gate, mutation-check, and STOP for leader
review. If the detail to write that spec isn't in the docs → `QUESTIONS_FOR_LEADER.md`.
