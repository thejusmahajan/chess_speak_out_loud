# TASK FOR GEMINI — Triage the diagnosis profile (weaknesses + steer candidates)

Read the completed diagnosis and produce a human-readable triage the user can act on:
(1) what weaknesses to train, (2) what tactical/sacrificial (Tal) steering candidates were
found, and (3) a sanity verdict on whether the data is healthy ("actually working and
good"). **READ-ONLY** — analyze, do not modify code or the profile. Output ONE markdown
file, `PROFILE_TRIAGE.md`, at the repo root. Cite exact field paths + counts for every
claim; never fabricate a number; flag anything degenerate.

## Input
- `data/training/profile.json` (the canonical file the UI serves; identical to
  `downloads/profile.txt`). It is the result of a Kaggle 2×T4 run: **213 findings,
  256 steer_findings, 30 games, 880 moves, vision=attention**.

## Profile schema (top-level keys — read these exactly)
`version`, `created`, `games_analyzed`, `moves_analyzed`, `time_scramble_skipped`,
`opening_sidelines_excluded`, `findings[]`, `aggregates`, `steer_findings[]`,
`steer_summary{}`, `steer_budget_exhausted`, `regressions`.
- **finding** (in `findings[]`): move context, severity, played vs best move, eval/swing,
  motif/blindness tags (policy-blindness, attention-blindness, confirmed-mistake), phase,
  clock bucket, opening/ECO. (Inspect the actual objects to learn the exact sub-fields.)
- **steer_finding** (in `steer_findings[]`): `best` {uci,san,eval_cp,complexity,components},
  `steer` {uci,san,eval_cp,complexity,components}, `had_tal_move` (bool),
  `playable_candidates[]`, plus position/opening context.
- **steer_summary** (dict keyed by opening/ECO): each entry has `moves`, `tal_moves`,
  `mean_complexity`.
- **aggregates**: the phase/clock/opening rollups (e.g. the headline "middlegame positional
  blindness 0.18 vs 0.08/0.07"). Inspect and report its actual structure.

## Deliverable — `PROFILE_TRIAGE.md`

### Part 1 — Weaknesses (what to train)
- The **headline weakness** from `aggregates` (which phase/clock/opening is worst, with the
  actual numbers). Confirm/adjust the known "middlegame positional blindness" finding.
- Breakdown of findings by TYPE (policy-blindness vs attention-blindness vs confirmed
  mistakes) and by phase/clock/opening — with counts.
- **Top ~10 findings** by severity/eval-swing: move, played vs best, swing, tag, opening.
- Any `regressions`.
- A short ranked "train-this-first" list grounded in the counts.

### Part 2 — Tactical steering / Tal candidates
- Total steer_findings (256) and how many are `had_tal_move == true` (the sacrificial ones).
- **Top ~10 steer candidates** by `steer.complexity`: position/opening, the steered
  (sacrificial/Tal) move vs objective best, complexity, components.
- `steer_summary` by opening: which openings carry the most `tal_moves` / highest
  `mean_complexity` — i.e. where the user's sacrificial style shows up most.
- Verdict: is the sacrificial/Tal style well-represented, or thin?

### Part 3 — Health / "is it good?" (sanity gate — the user's real question)
- Are all sections NON-EMPTY and sensible? (findings, aggregates, steer_findings,
  steer_summary all populated?)
- **Attention-blindness present?** vision=attention ran, so attention-based findings should
  be non-trivial — NOT all-zero (all-zero would mean the saliency silently failed). Confirm.
- Ratios plausible? (213 findings / 880 moves ≈ 24% flagged; 256 steer / 880). Flag if
  degenerate (e.g. 0 of something, all identical values, NaNs).
- `steer_budget_exhausted`: true/false — did TS2 run to completion or hit its budget cap?
- Bottom-line: **GOOD / SUSPECT**, with the specific evidence.

## Constraints
- Read-only; cite `field.path` + counts for every claim; quote a couple of concrete example
  objects. No fabricated numbers; flag NaN/empty/degenerate. Keep it tight and actionable —
  this is for the user to decide training, and for the leader to sanity-check the pipeline
  end-to-end. STOP when the md is written.
