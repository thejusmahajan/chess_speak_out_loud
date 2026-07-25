# Gemini — ORDER: deep code audit for bugs and aim-alignment (READ-ONLY)

**Direct order:** Deeply analyze the training codebase for (1) **correctness bugs**
and (2) **misalignment with the system's stated aim**. Produce a ranked findings
report. **Do NOT change any code — report only.** Follow `WORKER_AGENT_COOKBOOK.md`:
every claimed finding needs exact evidence and a concrete failure scenario, and you
must label each **CONFIRMED** vs **SUSPECTED**. A plausible-but-unverified claim is
SUSPECTED, not CONFIRMED. Do not pad the report with style nits.

## The aim (what the system is SUPPOSED to do — audit against this)
Read these first; they define intent:
- `TRAINING_SYSTEM_PLAN.md`, `TRAINING_ROADMAP.md`, `REPERTOIRE_TUTOR_EPOCH.md`,
  `ARCHITECTURE.md`, and the **normative docstrings in `backend/training/metrics.py`**
  (it is the "single mathematical source of truth"). `WORKLOG_TRAINING.md` records
  what each phase intended.

Summary of the aim: from a player's PGN, **diagnose weaknesses** (policy-divergence
"blindness", attention blindness, tactical complexity — time-scramble moves
excluded), **rank "what to work on"** self-relative to the player's own baseline
across openings/phase/clock, and **train the repertoire** — variation trees built
from the player's own games, critical-node SRS drills, and cached LLM coach
explanations. Metrics must compute what their names/docstrings claim.

## Scope (audit in this priority order)
1. `backend/training/pipeline.py` — the diagnosis pipeline (Stage A/B, steering,
   aggregation incl. by_opening/by_phase/by_clock).
2. `backend/training/metrics.py` — all metric math (policy divergence, attention,
   tactical_complexity, steer_candidates, is_opening_mistake, ValueCount/grade/
   importance, compare_to_dim_avg, rank_dimension, classify_phase).
3. `backend/training/select_repertoire.py` — repertoire + variation-tree builder.
4. `backend/training/drills.py`, `attempts.py` (SRS), `explanations.py`.
5. `backend/app.py` — the training endpoints (shapes, error handling, path resolution).
6. Secondary: `store.py`, `openings.py`, `gems.py`, `trends.py`, `llm_client.py`,
   `engine_manager.py`, `neural_vision.py`.
Frontend is out of scope for this pass unless a backend contract mismatch forces a look.

## What to hunt (both axes)

### A. Correctness bugs
- **Cross-module data-shape mismatches** — the highest-yield class here. Trace a
  value across producer→consumer and confirm the shapes agree. Real examples we've
  already hit: an eval passed as a dict when the parser wanted an int/"M5" string;
  findings keyed by `game_idx` that don't carry `game_idx` (only an `id` like
  `"g003-p045"`); an endpoint calling a function with `model=` when the param is
  `llm_model`. **Find more of these.**
- **Off-by-one / index / key-matching errors** (e.g. ply conventions that must match
  between producer and consumer).
- **Silent-degeneracy** — code paths that produce empty/all-zero/vacuous output
  instead of erroring, so a bug hides (e.g. a tree that collapses to 1 node; an
  aggregate whose numerator never matches its denominator).
- **Wrong semantics** — a metric/field whose implementation ≠ its name/docstring
  intent (real example: `user_blind_rate` once computed move-*inconsistency*, not
  blindness). Check each metric's definition against its docstring.
- **Unhandled edge cases** — empty inputs, missing dict keys, None evals, single-
  element dimensions, division by zero, games without clocks, mate scores.
- **Inconsistent filtering** — e.g. is the time-scramble exclusion applied
  consistently everywhere it should be (Stage A vs aggregates vs steering)?
- **Concurrency / resource** — engine-loop usage, caches, atomic writes.

### B. Aim-misalignment
- Places where the code does something **different from the documented intent**.
- **Dead / vestigial** code or flags that no longer serve the aim (e.g. is
  `LLM_ENABLED`/bypassed paths coherent? are retired features fully removed?).
- Metrics or gates whose thresholds/logic contradict the plan docs.
- Features half-wired (produced but never consumed, or consumed but never produced).

## Report format (create `CODE_AUDIT_REPORT.md`)
Rank findings **most-severe first**. For EACH finding:
```
### [SEV: critical|high|medium|low] <short title>  (CONFIRMED|SUSPECTED)
- category: data-shape | off-by-one | silent-degeneracy | wrong-semantics | edge-case | aim-mismatch | dead-code | other
- location: backend/…/file.py:LINE (and the consumer location if cross-module)
- evidence: the exact code/quote that shows it (both sides for a shape mismatch)
- failure scenario: concrete input/state → wrong output/crash/aim-gap (be specific)
- why it matters (for aim-mismatch): which documented goal it violates, citing the doc
- suggested fix: 1–3 lines, DESCRIBED not applied
```
End with:
- an **aim-alignment verdict**: does the implemented system achieve the documented
  aim? List the top gaps, if any.
- a count of CONFIRMED vs SUSPECTED findings by severity.

## Constraints
- **READ-ONLY.** Do not edit any source file. The only file you create is
  `CODE_AUDIT_REPORT.md` (+ a `WORKLOG_TRAINING.md` entry).
- Cite **real** line numbers you actually read — no invented locations.
- If you cannot prove a finding by reading the code, mark it **SUSPECTED** and say
  what would confirm it. Do not present suspicion as fact.
- Prefer 15 well-evidenced, real findings over 60 shallow ones. Correctness and aim
  first; ignore formatting/style unless it causes a bug.

## Gate / deliverable
- `CODE_AUDIT_REPORT.md` with ranked, evidenced findings + the aim-alignment verdict.
- A `WORKLOG_TRAINING.md` entry ending with `code audit ready for review`.
Await leader sign-off — the leader will independently verify the CONFIRMED findings
(and spot-check SUSPECTED ones) before any fixes are made.
