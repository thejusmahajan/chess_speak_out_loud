# Epoch III — Repertoire Trainer + Tutor-style weakness ranking

> Two parallel tracks. Track T (Tutor-ranking) = **leader**, `metrics.py`.
> Track R (Repertoire trainer) = **Gemini**, `pipeline.py` / `select_repertoire.py`
> / `drills.py` / `llm_client.py` / frontend. Same gate discipline as the TS
> epoch: paste REAL command output in `WORKLOG_TRAINING.md`, leader signs off,
> and **workers' green tests get independently re-run** (see the vacuous-steer-
> test lesson — a passing test that guards nothing is a reject).

## Vision
1. Turn static repertoire lines (currently a single line to the tabiya + a
   template rationale) into **deep, SRS-tracked training**: variation trees
   built from the user's *own games*, critical-move marking, and cached
   LLM explanations.
2. Add a **Tutor-style ranking** that tells the user *what* to train, ranked by
   a principled importance score instead of raw counts.

The tracks interlock: Track T says *what* opening/phase is worst; Track R is
*how* the user drills it. Both feed the existing SRS.

## Decisions (locked 2026-07-21)
- Variations come from the user's **own games first** (engine-vetted), backfilled
  by the Lichess explorer only later.
- Explanations are **LLM-generated (gemini via `llm_client`) and cached to disk**.
- **Peer-relative** comparison is deferred (needs an external cohort dataset);
  ship **self-relative (DimAvg)** first.

## Reuse — do NOT reinvent
- **SRS**: `backend/training/attempts.py` (SM-2-lite: interval ladder, lapses,
  due-sorting). Repertoire critical-nodes become SRS items keyed by node id.
- **Line walking**: `drills.check_attempt` (walks a line, accepts alts, completes
  at the end) — the trainer's move-validation primitive.
- **Criticality signals**: `metrics.tactical_complexity`, `metrics.steer_candidates`,
  and per-position user blind-rate from the profile.
- **LLM plumbing**: `llm_client.generate_conversation` shows the gemini call
  pattern; add a sibling for move explanations.

---

## Track T — Tutor-style weakness ranking (LEADER, `metrics.py`)

Lifted from lila `modules/tutor` (`TutorNumber`, `TutorCompare`).

- **T1 — `ValueCount` + `Grade`.** Every metric = `(value, count)`. `grade(mine,
  ref)` normalizes the gap by a *meaningful* divisor (percent-scaled for rates;
  a tuned cp/rate divisor for ours) so only material gaps surface. Support
  `reverse` metrics (lower = better, e.g. time-trouble). Unit-tested in isolation.
- **T2 — comparison + importance.** `DimAvg` reference: each dimension vs the
  user's own count-weighted mean across dimensions. Rank by
  `importance = grade · sqrt(count · position_weight)` (game-level weighted over
  move-level). `mixed_bag` (balanced top strengths+weaknesses) +
  dedupe-similar. Replaces today's raw blind-count/rate sort, which lets a
  1-game 100%-blind opening outrank a real weakness.
- **T3 — new dimensions from the existing parse** (no new inputs): **phase**
  (ply buckets → opening/middle/end), **time/clock** (from the `[%clk]` we
  already extract + the time-scramble flag), **conversion** (won a winning
  position?), **resourcefulness** (saved a lost one?).
- **T4 — surface it.** Emit a ranked "what to work on" block into the profile
  aggregates; Gemini renders it in the Weakness Profile UI.
- *(Deferred: peer baselines.)*

## Track R — Repertoire trainer (GEMINI)

- **R1 — variation-tree builder (`select_repertoire.py` / `pipeline.py`).** For
  each repertoire opening, aggregate the user's games into a move **tree**:
  `user move → observed opponent replies (frequency-weighted) → user reply`, to
  depth D. Engine-vet each user node for soundness; **mark CRITICAL nodes**
  (high eval-swing on a wrong reply / high user blind-rate / high
  tactical-complexity). Persist as `data/training/repertoire_tree_<eco>.json`.
  **Leader reviews this data model before R2/R3 build on it.**
- **R2 — drills + SRS from the tree (`drills.py` + `attempts.py`).** Convert
  critical nodes into line-drills reusing `check_attempt` (opponent replies
  auto-played, weighted by frequency; the user must find the right reply). Each
  critical node = one SRS item (`next_due`/`lapses`) in the existing scheduler.
- **R3 — cached LLM explanations (`llm_client.py`).** For each critical node,
  generate once and cache a short "why this move / what to watch for" via gemini;
  store on the node. Never regenerate a cached node.
- **R4 — Repertoire Trainer UI (frontend).** Replace the static
  move-list + final-position view with an interactive board that walks the tree,
  drills critical nodes, reveals the explanation + best/critical contrast, and
  shows per-opening SRS due-counts. Reuse `DrillMode` / `TrainingBoard`.

## Ownership & guardrails
- `metrics.py` — **leader only** (the grade/importance math).
- Data models (`repertoire_tree_*.json`, SRS item shape) — **leader signs off
  the schema before workers build against it.**
- Keep tracks decoupled: R1 defines the tree; T-track ranking can *point at*
  openings by ECO without depending on the tree internals.

## First tasks
- **Gemini → R1** (variation-tree builder + data model).
- **Leader → T1** (ValueCount/Grade in `metrics.py`, unit-tested).
