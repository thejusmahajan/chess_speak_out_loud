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

### T3 — Sacrificial repertoire mode
`build_repertoire(..., style="sacrificial")`: target motifs overridden to
the puzzle DB's sacrifice family (sacrifice, attraction, deflection,
clearance …) instead of weakness motifs; candidate scoring multiplied by a
familiarity factor from `profile.aggregates.by_opening` (openings the user
already reaches). Output: lines that are one branch away from what I play,
scored by sacrifice-pattern density, still gated sound+sharp.

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
