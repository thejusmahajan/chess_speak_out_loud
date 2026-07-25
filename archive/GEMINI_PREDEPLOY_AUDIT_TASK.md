# Gemini (3.6 Flash, High) — ORDER: pre-deploy airtight audit (READ-ONLY)

**Direct order:** Before we spend **rented A100 hours** on a full ~700-game corpus
diagnosis, do a detailed review of the diagnosis pipeline and the **newly landed
node-limit changes** and report every real bug. **Do NOT change any code — report
only.** Follow `WORKER_AGENT_COOKBOOK.md`: every finding needs exact `file:line`
evidence and a concrete failure scenario, and must be labelled **CONFIRMED**
(you traced it in the code) vs **SUSPECTED** (plausible, unproven). A guess is
SUSPECTED, not CONFIRMED. No style nits.

## Why this audit exists (the stakes — rank findings by this)
This is a **pre-deploy gate**. The next action is a multi-hour, paid GPU run over
the full corpus that writes `data/training/profile.json`, which the app then serves.
So prioritize, in order:
1. **Run-wasting bugs** — anything that would crash mid-run, hang, silently
   truncate coverage, or exhaust a budget partway and mislabel the result as
   complete. On a 4-hour rented run these are the most expensive.
2. **Profile-corrupting bugs** — anything that makes the produced diagnosis
   *wrong* (bad math, POV sign errors, cache cross-contamination, aggregate
   numerator/denominator mismatch).
3. Everything else.

## Already found & FIXED — do NOT re-report these (see `CODE_AUDIT_REPORT.md`)
- **F1 (critical)** `tactical_complexity` White-POV vs side-to-move — FIXED (`abs(s0-s1)`).
- **F2 (high)** `by_opening` weighted vs unweighted blind rate — FIXED.
- **F3 (high)** `start_diagnose` JSONDecodeError/OSError crash — FIXED (try/except continue).
- **F4 (high)** hardcoded corpus PGN path/username in endpoints — FIXED (`_corpus_pgn()`).
- **F5 (medium)** tree `user_blind_rate` cross-opening inflation — FIXED (scoped to game keys).

**Known-open, already logged — only re-raise with a NEW angle or a concrete fix:**
- **F6 (medium)** steer cache misses recompute saliency, saliency not persisted to disk.
- **F7 (low)** "no runtime LLM in v1" doc rule vs `enrich_tree_explanations`.
- **F8 (SUSPECTED)** `_walk_line` leaf-node truncation in `drills.py`.

Your value is in **new ground**, especially the areas below.

## Priority scope for THIS pass

### 1. The NEW node-limit search path (landed in commit `ee9afda`) — audit hard
Files: `backend/engine_manager.py`, `backend/training/metrics.py`,
`backend/training/pipeline.py`, and Colab `colab/diagnose_on_gpu.py` (Cell 5b + 6).
- `engine.analyze(nodes=…)` → `_do_analyze` builds `chess.engine.Limit(nodes=nodes)`
  and **drops the `time` limit entirely** when nodes is set. Questions to answer by
  reading code + lc0/python-chess behavior:
  - Is there any position where a **node-limited lc0 search never returns** (no time
    safety net → a hung paid run)? Should there be a fallback `time` cap alongside
    `nodes`? Trace what happens on mate/stalemate/terminal positions.
  - `multipv=2` with a node limit — does the node budget get split across PVs or
    applied per-search? Does that change eval quality vs the old time-based path?
  - Does dropping `depth` when `nodes` is set matter anywhere a caller relied on it?
- `metrics.TrainingConfig`: **only** `confirm_best_seconds`/`confirm_played_seconds`
  got node twins. Enumerate **every other time-limited search that runs during the
  full notebook run** — `gem_screen_seconds`, `gem_confirm_seconds`,
  `repertoire_eval_seconds`, `search_lines`, any `fast_analyze` — and report which
  ones **stay time-based and will therefore still be slow / GPU-wasting** during the
  repertoire/gem/tree build cells (6–9). Is that intended, or an oversight that makes
  the "full run" still take hours after diagnosis?
- `pipeline.py`: confirm Stage B passes `confirm_best_nodes` to the *best* eval and
  `confirm_played_nodes` to the *played* eval (not swapped), and TS2 passes
  `confirm_played_nodes`. Confirm `nodes=None` truly reproduces the old behavior.
- Is `120_000 / 60_000` (Cell 5b) sane? Not a correctness bug, but flag if any code
  path assumes a *time* limit semantically (e.g. a timeout, a progress estimate).

### 2. Full-corpus reliability (bugs that only bite at ~700 games / multi-hour)
- **Caches** (`stage_b_cache`, `steer_cache`, `store.EpdCache`): are keys collision-safe
  across positions with different side-to-move / castling / en-passant? Can one game's
  cached analysis be wrongly reused for another? Are writes atomic under a long run?
- **Budgets**: `steer_search_budget=4000`, `steer_bt3_budget=200` are **per diagnosis
  run**. Over ~700 games, do these exhaust partway and then **silently stop producing
  steer/saliency findings for the rest of the corpus** while the profile still reports
  as complete? Trace `steer_budget_exhausted` → is the partial-ness surfaced honestly,
  or does it look like "the player has no tactical finds after game N"?
- **Progress `total`**: does the reported `total` match the actual work count, so a
  4-hour run doesn't look frozen (and so a real freeze is distinguishable)?
- **Unbounded growth**: any list/dict/cache that grows per-move for 700 games and
  could blow memory or slow to a crawl by game 600?
- **Crash recovery**: if the run dies at game 500, is *anything* persisted/resumable,
  or is the whole paid run lost? (Report the current behavior; suggest the minimal
  checkpointing if none exists.)

### 3. Re-verify the eval-POV handling everywhere (F1 was critical and here)
Trace **every** centipawn comparison in `pipeline.py` Stage B confirmation and
`metrics.steer_candidates` / `is_opening_mistake`: with **Black to move**, are
`eval_best_cp` vs `eval_played_cp` and the steer floors compared with the correct
sign? `analyze()["evaluation"]` is **White-POV**. Any place that treats it as
mover-POV without flipping is a profile-corrupting bug. This is the highest-risk
class — check it exhaustively, don't assume F1 was the only instance.

### 4. Aggregation correctness (post-F2)
Re-check `by_phase` / `by_clock` / `by_opening` and the confirmed/unconfirmed counts:
after the F2 fix, are all three now consistent? Any remaining numerator/denominator
mismatch, double-count, or phase/clock bucket that can never be hit?

## Report format — create `PREDEPLOY_AUDIT_REPORT.md`
Rank **most-severe first**, using the stakes ranking above. For EACH finding:
```
### [SEV: critical|high|medium|low] <short title>  (CONFIRMED|SUSPECTED)
- category: run-wasting | profile-corrupting | pov-sign | cache | budget | node-limit | edge-case | aim-mismatch | other
- location: file.py:LINE  (+ consumer location if cross-module)
- evidence: exact code/quote (both sides for a shape/POV mismatch)
- failure scenario: concrete input/state → wrong output / crash / wasted-run (specific)
- blast radius on a full corpus run: does it waste GPU $, corrupt the profile, or both?
- suggested fix: 1–3 lines, DESCRIBED not applied
```
End with:
- a **GO / NO-GO recommendation** for the full paid run: is the pipeline airtight
  enough to spend the A100 hours, or are there must-fix-first blockers? List blockers.
- a count of CONFIRMED vs SUSPECTED by severity.

## Constraints
- **READ-ONLY.** Edit nothing. Only create `PREDEPLOY_AUDIT_REPORT.md` (+ a
  `WORKLOG_TRAINING.md` entry). `backend/training/metrics.py` is leader-owned.
- Cite **real** line numbers you actually read — no invented locations.
- Prove it or mark it **SUSPECTED**. Prefer ~12 airtight findings over 50 shallow ones.
- Correctness and run-safety only; ignore formatting/style unless it causes a bug.

## Gate / deliverable
- `PREDEPLOY_AUDIT_REPORT.md` with ranked findings + the GO/NO-GO recommendation.
- A `WORKLOG_TRAINING.md` entry ending with `pre-deploy audit ready for review`.
Await leader sign-off — the leader independently verifies every CONFIRMED finding
(and spot-checks SUSPECTED) before any fix is made or the paid run is launched.
