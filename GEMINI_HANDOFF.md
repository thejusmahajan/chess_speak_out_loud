# HANDOFF → Gemini 3.6 Flash (High) — continue the GPU diagnosis work

The leader (Claude) is out of tokens until reset. You (local Gemini, `cszero` env,
BT3 loadable on CPU for correctness tests) continue. Keep the discipline: **prove
every change with a mutation-checkable test; batched==serial; suite green.**

## Where we are (branch `windows-dev`, HEAD ~`61aaef8`)
Goal: from a player's PGN, diagnose weaknesses + build a training repertoire.
Right now we're **validating a 30-game subset (`test_subset.pgn`) on a Colab A100**
to produce `data/training/` (→ `training.zip`) and check the UI (repertoire,
puzzles, tactical steering). The Colab notebook is `colab/diagnose_on_gpu.ipynb`.

**Working + committed:**
- BT3 runs on the GPU (device-aware `NeuralVision`, `cuda:0` confirmed).
- Batched primitives: `saliency_absolute_batch` (38× on GPU) and `evaluate_batch`
  (value+policy+wdl, 3 ms/pos) — both leader-verified + guarded (opt-in tests,
  `RUN_SLOW_BT3=1`).
- Node-limited search + `BT3_BUDGET` high/low toggle (Cell 5c).
- **a1a1 terminal crash FIXED** at all 3 lc0 call sites (`analyze`,
  `get_policy_distribution`, `search_lines`); `VerboseMoveStats` leak fixed.
- Progress bars fixed; validated-lc0 cache; Cell 3 always-pulls (reads `GH_TOKEN`
  from Colab Secrets); notebook saves outputs to Drive (`files.download` hangs).
- Test suite: **135 passed, 5 skipped** via
  `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests/ -q`.

## Immediate next steps
1. **Finish the subset run**: Cell 6 (30-game diagnosis) → Cell 8 (repertoire/gems/
   trees/drills) → Cell 9 (`training.zip` → Drive). User loads it into the local app
   and checks the UI. Fix whatever the UI reveals.
2. If a run **crashes**, capture the traceback and fix the root cause (don't paper
   over). The last two crashes were stale-clone + terminal positions — both about
   "runtime running old code / unhandled edge case."

## The roadmap (see `docs/discussion_5_saturating_the_a100.md`)
The diagnosis is **deep-lc0-search bound** (~1.5–2 h for 30 games at `high`). Levers:
- **Opt #2 — TS2 `evaluate_batch` screen (BIG):** Stage 1 (batch saliency in TS2)
  is done. Stage 2 = use `evaluate_batch` (3 ms) as a wide candidate screen and run
  deep lc0 search **only on the crux** candidates. It changes the *narrowness*
  signal (only a multipv search gives it today), so it is **quality-sensitive**:
  implement behind a flag and **validate by diffing `steer_findings` old-vs-new on
  the subset** before making it default. Spec it like the prior tasks.
- **Opt #4 — node-knee:** test whether `BT3_BUDGET="low"` (15k/8k) keeps the
  findings of `"high"` (40k/20k). **CLEAR `data/training/cache/` when switching
  budgets** — the cache is EPD-keyed, not budget-keyed, or you'll reuse stale evals.
- Deferred (logged in `TERMINAL_REVIEW_NOTES.md`): `StockfishEngine` terminal guard;
  a single choke-point for engine calls (so a 4th method can't forget the guard).
- After UI validation: `POST_VALIDATION_BACKLOG.md` (B1–B5). **TS2/tactical steering
  is a core deliverable and must run in every test** (user requirement).

## Gotchas that already bit us
- **Stale code:** a runtime restart keeps `/content/repo`; confirm Cell 3 prints the
  right `repo at: <hash>`. Stale `import` also lied (device fix) — restart runtime.
- **`files.download` hangs** in the browser → outputs go to Drive / the Colab file
  browser.
- **Private repo** needs `GH_TOKEN` in Colab Secrets (read-only fine-grained PAT).

## How to work with the leader when he's back
Small, verified commits; `Co-Authored-By: Claude Opus 4.8`. Leader-owned files:
`backend/training/metrics.py` (don't edit without a spec). Read `MEMORY.md`,
`WORKER_AGENT_COOKBOOK.md`, and this file first each session.
