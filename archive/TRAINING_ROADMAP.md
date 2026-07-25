# Training Roadmap — user expectations vs. system (2026-07-19)

Source: user's expectation list after the first real diagnosis
(derdiedasdie, 24 games). Each item: what exists today, the gap, and the
planned phase. Phases T1–T7 are ordered by leverage, not difficulty.

## Expectation → status map

| # | Expectation | Today | Gap |
|---|---|---|---|
| 1 | Repertoire that lets me sacrifice early, tactical opportunities, anchored in openings I already play | Repertoire Architect picks sharp+sound openings producing my *missed* motifs | Doesn't bias toward sacrifice motifs; ignores which openings I actually play (T3) |
| 2 | Training sets targeting where I went astray | own_game drills from confirmed findings | — (done) |
| 3 | General cross-game weaknesses → drills for those position types; critical points where I don't take advantage | Motif/concept aggregates; corpus drills by top motifs | No eval-context classes ("was better, failed to convert"); no phase filter (T4) |
| 4 | Blunders AND the moves leading to them / wrong plan; recurring series patterns in my style | Single-move analysis only | Sequence/drift analysis + clustering is new engineering (T7) |
| 5 | I go for the wrong motif — find motif confusion | Motifs of the line I *missed* | Not tagging the line I *played* → no confusion matrix yet (T5) |
| 6 | Opening principles I break → report + drills | Concept misses (center_control, king_safety…) already top-level in my profile | No phase-scoped report or drill filter (T4) |
| 7 | Spaced repetition; timestamped records; escalate when I re-fail a training goal | Drill attempts are checked but **not recorded anywhere** | Whole memory layer missing — foundation gap (T1) |
| 8 | Zero blunders (trend toward it) | Each diagnosis **overwrites** the profile — no history | Longitudinal store + trend report (T2) |
| 9 | Middlegame plans not understood — point out and teach | PV + motif/concept tags shown per finding | "Plans" need sequence drills (answer several moves, not one) (T6); verbal teaching would need the optional LLM layer (v2 decision) |

## Phases

### T1 — Training memory + spaced repetition (foundation)
`data/training/attempts.jsonl`: every drill attempt appended with
timestamp, drill id, source, tags, correct, set id. Scheduler (SM-2
family): failed drills re-queue at increasing intervals; a "due" queue
endpoint + UI badge. Escalation rule: if a motif marked "trained" produces
new blind findings in a later diagnosis, its drills gain weight and
interval resets — the "it must be more critical" requirement.

### T2 — Longitudinal profiles
Stop overwriting: `profile-<timestamp>.json` + `profile.json` symlink-like
"current". Trend endpoint: blindness rates, blunder count (confirmed
findings / 100 moves), per-motif trajectory across batches. This is the
only honest metric for "I want 0 blunders" — the number that must go down
batch over batch.

### T3 — Sacrificial repertoire mode  ⚠️ SUPERSEDED by Epoch II (2026-07-20)
`build_repertoire(..., style="sacrificial")`: target motifs overridden to
the puzzle DB's sacrifice family (sacrifice, attraction, deflection,
clearance …) instead of weakness motifs; candidate scoring multiplied by a
familiarity factor from `profile.aggregates.by_opening` (openings the user
already reaches). Output: lines that are one branch away from what I play,
scored by sacrifice-pattern density, still gated sound+sharp.

**Why superseded:** this picks openings from the puzzle corpus by a
*hardcoded* motif list (`SACRIFICE_TARGETS`) — "a random set of attacking
openings," which is exactly what the user rejected. It is not derived from
the user's own play beyond a thin familiarity nudge, and it has no notion
of *tactical complexity* — only motif frequency. Epoch II below replaces
the generative idea (build sharp openings from a canned list) with a
derivational one (mine the user's real repertoire, then steer it toward
soundly-sharp branches). The soundness/sharpness gate (`sharpness_from_wdl`,
`sound_eval_cp`) is reused; the target-selection is thrown away.

### T4 — Finding context classes + filtered drills
Classify every finding by phase (opening ≤ ply 12 / middlegame / endgame)
and eval context (converting advantage / balanced / defending). New
report sections: "opening principles broken" (phase=opening × concept),
"conversion failures" (was ≥ +150cp, swing ≥ 90). Drill generation gains
filters: `{"phase": "opening"}`, `{"context": "conversion"}`.

### T5 — Motif confusion matrix
Stage B already searches the played move; additionally motif-tag the
*played* continuation. Aggregate (played-motif → missed-motif) pairs:
"when the position wanted a quietMove you played a capture" becomes a
first-class, drillable stat.

### T6 — Sequence drills ("play the plan") + quiet gem candidates
Drill schema gains `solution_line_ucis`; UI walks the user through 2–3
moves of the PV with the opponent's replies animated — this is the
trainable form of "middlegame plans". Gem candidates: quiet positions
sampled from plies 15–60 of the user's own games (not just blunder spots),
finally feeding the hidden_gem funnel real input.

### T7 — Blunder preludes & style clustering (research-y)
Walk back N plies from each confirmed blunder; measure policy-divergence
drift to separate "sudden" from "slow-rolled" blunders. Cluster findings
by (structure hash, motif, phase) to surface recurring bad patterns.
Ship only what proves signal on real profiles.

## Ground rules carried over
No runtime LLM in v1 paths (T1–T6 are all deterministic); metrics changes
go through leader-owned `metrics.py`; every phase lands with tests + a
worklog gate like G/C phases. Verbal "teaching" of plans (natural-language
coaching) is a v2 decision — revisit after T6 sequence drills exist.

---

# Epoch II — Tactical Steering ("the Tal engine") — 2026-07-20

Reorientation after the user articulated the real aim. Not a restart: the
own-games → LC0 (policy + WDL + BT3 attention) → diagnosis substrate is the
right foundation. What changes is the *question we ask of it*.

## The two tracks (they must coexist — one bounds the other)

**Track A — objective mistake analysis (the realism anchor). KEEP.**
Find where the user actually went wrong in their own games — mistakes,
blunders, missed wins — as a first-class deliverable (the raw report), plus
drills tailored so those specific errors stop recurring. This is largely
T1/T2 + existing diagnosis. Its job in Epoch II: **bound** the steering.
Rationale (user): steering into an objectively lost "tactical" position only
beats sub-1100 opponents — unrealistic. Track A keeps Track B honest, and
lowering the real error rate is what lets the user *convert* the positions
steering creates.

**Track B — tactical steering & repertoire (the new engine).**
The inverted axis: instead of "how far from best did you play," measure
**how much tactical complexity a move creates for the opponent** — the Tal
sense — and steer toward the sharpest move that is *still sound*. Two hard
guardrails from the user:
1. **Bounded eval loss.** A steer move may be objectively 2nd/3rd best but
   must stay within `steer_max_loss_cp` of best AND not be objectively lost
   (`eval(m) ≥ steer_min_eval_cp`, mover POV). Never an inferior/losing move.
2. **Rooted in the user's real style.** The repertoire is *mined from the
   openings the user already plays*, not assembled from a list. Keep sound
   lines, **repair** leaky ones (Track A findings in that ECO), add a
   **tactical tint** at sound-but-sharper branch points within their lines.

## The metric (leader-owned, `metrics.py`) — the crux, done by the leader

`tactical_complexity(analysis, policy, saliency, cfg) -> {score, components}`
where `analysis` is `engine.analyze(P, multipv=K)` of the position **after**
our candidate move (opponent to move). Components, each 0..1, from oracles
already contracted (plan §2):
- **Decisiveness** `D` — `1 − draw_mass` from `wdl` (reuse
  `sharpness_from_wdl`). Flat/drawish WDL = calm.
- **Only-move narrowness** `N` — normalized eval gap between best and
  2nd-best reply (`best_moves[0].score − best_moves[1].score`). Big gap ⇒
  "find it or lose."
- **Policy trap** `T` — the *prior* of the only saving reply from
  `get_policy_distribution`. When the sole move that holds has a **low**
  prior, a human is unlikely to find it → maximal practical danger.
- **Attention diffusion** `A` (secondary) — `saliency_concentration`;
  fires-everywhere boards are hard to read.

`steer_candidates(node_analysis, per_move_complexity, cfg) -> [ranked]`:
among our legal moves passing the eval bound, rank by complexity; a "Tal
move" exists when the top playable-complexity move is materially sharper
than the objective-best move. **Pure math over oracle outputs** — the engine
calls that gather per-candidate `multipv` happen in the caller (pipeline /
select_repertoire), never in metrics.

Also leader-owned (Track A correctness): **phase-aware mistake gating** —
`is_opening_mistake(...)` so a sound pet sideline (policy-divergent but
objectively fine, ply ≤ `opening_max_ply`) is NOT flagged as an error. Without
this, Track A tells the user to abandon the very repertoire we mean to polish.

## Phases

### TS1 — Tactical-complexity metric (LEADER)
`metrics.py`: `tactical_complexity`, `steer_candidates`, `is_opening_mistake`,
new `TrainingConfig` fields (`steer_max_loss_cp`, `steer_min_eval_cp`,
complexity component weights, `opening_max_ply`). Unit tests with
hand-built analysis/policy/wdl fixtures (no engine). This unblocks TS2–TS4.

### TS2 — Steering pass over own games (GEMINI, `pipeline.py`)
A second, budgeted pass: at each user decision point already cached from
Track A, gather `multipv=K` for the top few legal moves and call
`steer_candidates`. Emit, per position, whether a bounded Tal move existed,
its complexity, and the objective-best for contrast. Store on the profile as
`steer_findings` (distinct from mistake `findings`). EPD-cached; hard BT3/
search budget per run.

### TS3 — Style-rooted tactical repertoire (OPUS, `select_repertoire.py`)
Replace the `SACRIFICE_TARGETS` path. Mine the user's ingrained repertoire
from `profile.aggregates.by_opening` (ECOs with ≥ N played moves). Classify
each: **sound-keep / leaky-repair** (has Track A findings) **/ dry** (low
steer-complexity potential). Build recommendations = their openings, tinted:
at branch points inside their lines, the sound-but-sharper continuation
(`steer_candidates`, bounded). Each rec tags `origin: kept|repaired|tinted`,
carries complexity + the eval-bound proof. Still gated sound+sharp.

### TS4 — Steering drills + minefield view (GEMINI, `drills.py` + frontend)
New drill source `"steer"`: positions from TS2 where a Tal move existed;
the solution is the sharpest *sound* move (accepted within bound), scored
separately from objective-best drills. **Minefield visualization:** per-move
complexity as heat/arrows + the `saliency_absolute` map as "how LC0 sees the
fire" — the requested "see the board as Tal senses it" view.

### TS5 — Interlock report (OPUS review + LEADER sign-off)
One report reconciling both tracks per opening: error rate (Track A) beside
steer-opportunity density (Track B), so "repair vs tint" decisions are
visible. Confirms the guardrails held on real profiles (no losing steers, no
sound pet lines flagged as mistakes).

## Ownership (no file edited by two agents; carries over §7 of the plan)
| Owner | Files | Scope |
|---|---|---|
| **Leader (me)** | `metrics.py` | TS1 metric + steering + phase gating — the delicate math |
| **Gemini** | `pipeline.py`, `drills.py`, frontend | TS2 steering pass, TS4 drills + minefield UI — heavy, detailed, gated |
| **Opus** | `select_repertoire.py`, its tests | TS3 style-rooted repertoire, TS5 review — precision, self-contained |

Worker specs: `GEMINI_TRAINING_TASKS.md` (§TS2, §TS4),
`CLAUDE_TRAINING_TASKS.md` (§TS3, §TS5). Both build against this section and
the frozen oracle APIs in `TRAINING_SYSTEM_PLAN.md` §2 — do not re-derive
metric math; import `backend.training.metrics`.
