
## 2026-07-19 — Leader (as Claude worker) — Phases C1 + C2
Claude Opus 4.6 worker out of quota until tomorrow; leader implemented both
remaining phases. All gates below are REAL outputs.

### C1 — `backend/training/gems.py`
Budgeted filter funnel per spec (dedupe -> policy gate -> quiet gate -> BT3
attention gate -> confirmation); `gem_candidates_from_profile` supplies finding
fens; alt solutions castling-safe via `metrics.accepted_ucis`. Also fixed C3
findings M1 (corpus mock guard), M2 (real `scan_for_gems` signature + results
emitted as hidden_gem drills), M4 (own_game dedupe by EPD + solution move).

```
backend\tests\test_training_gems.py .......   7 passed in 0.29s
(funnel order, BT3 budget, mock skip, EPD dedupe, schema, candidates)
```

Live (server hot-reloaded, engine_mode "live"): drills/generate count=5 ->
4 drills, own_game dedupe visible (e6g4 + e6e8, no duplicate solutions);
gem funnel scanned all 18 finding fens, 0 gems — expected, flagged blunder
positions are rarely quiet. hidden_gem drills will appear when candidates
include quiet positions.

### C2 — `backend/training/select_repertoire.py`
Backwards selection per spec: targets = top-3 motifs by 2*blind+missed;
candidates from `puzzle_db.opening_tags_ranked` mapped to ECO lines via new
read-only `openings.lines_by_tag()` (leader addition to a Gemini file, spec
anticipated the need); score = sum(weight_t * motif_profile(tag)[t]);
soundness pov_cp >= -sound_eval_cp + sharpness gate on <= 15 candidates.
SPEC DEVIATION (documented in module): "first-move color" filter is
implemented as line ownership = side making the line's LAST move, since every
ECO line starts with white's move and the literal reading is impossible.
Endpoint: `POST /api/training/repertoire` now accepts `"build": true`
(uses app engine singleton; contract §10). Also landed M3 (mate-inflated
swing shown as "decisive (mate)" in DrillMode), M5 (startup sweep marks
orphaned running/queued jobs as error), and fixed the diagnose job-lock
scanning the wrong directory (`data/jobs` instead of `data/training/jobs` —
the one-job-at-a-time 409 never actually worked).

```
backend\tests\test_training_select.py ........   8 passed in 0.32s
Full suite: 28 passed. npm run build: exit 0.
```

Live run (white, real puzzle DB + LC0):
```
targets: advantage w=47, veryLong w=33, quietMove w=22
[C02] French Defense: Advance Variation score=6.3554 eval=24cp draw=41.1%
Rationale: "Play the French Defense: Advance Variation (1. e4 e6 2. d4 d5
3. e5). Structures from this opening produce advantage in 12.7% of tagged
master-game puzzles; LC0 holds the tabiya at 24cp with a 41% draw share —
sharp enough to force the patterns you miss."
```

All planned phases (G1-G5.2, C1-C3) complete. M1-M5 all resolved.
