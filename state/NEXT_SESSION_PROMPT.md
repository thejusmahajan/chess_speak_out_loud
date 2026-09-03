# Start-of-session prompt — written 2026-09-03 for the next session

**Paste this whole file as your first message, or read it after `CLAUDE.md`.**
It is a snapshot, not doctrine. Where it disagrees with the code or `git`, they win.

---

## Read first, in this order

1. `CLAUDE.md` (auto-loaded) — routing and the non-negotiables.
2. **`state/NOW.md` §9, §10, §12** — where the work actually is.
3. `LEADER_BIBLE.md` **§6a** (current state), §4 (do-not-relitigate), §5 (failure catalog).
4. `docs/leadership/PLAYBOOK.md` — situation-indexed; use it mid-task.
5. `trainer/state/comments.jsonl` — the only channel Thejus has from inside the trainer. Read the
   tail. Anything newer than the last JOURNAL entry is unread.

---

## Where we are in one paragraph

Φ — a CNN that scores "is the side to move about to go wrong here" — is **trained, calibrated and
live in the UI**. It **failed its pre-registered F1 gate: test AUC 0.6908 against >0.70**, and that
number is recorded unrounded and must stay that way. The failure is informative: it is a
**representation ceiling**, not undertraining (4× the data bought +0.002). Two follow-on projects are
open: a **Φ-opening** dataset (Gemini built one; **its A5 alarm FIRED**) and the **profile
regeneration**, which is blocked on hardware and now has a better filter.

---

## ⚑ Three things blocked on Thejus's decision — do not decide these yourself

1. **The missing eval floor in live steering.** `compute_steering_analysis()` in `backend/app.py`
   never calls `metrics.steer_candidates()`; `grep -c "steer_max_loss_cp\|steer_min_eval_cp"
   backend/app.py` returns **0**. It uses its own 80/150 cp tiers with a **fallback that applies no
   eval constraint at all**. This is the cause of the spurious opening sacrifices Thejus reported.
   The options discussed with him: a hard `steer_min_eval_cp`, or a **narrowness-scaled "gamble
   floor"** where the permitted deficit grows with `policy_trap` (his idea: a sacrifice that is
   objectively unsound but whose refutation is a one- or two-move non-obvious sequence). **His call.**
2. **The sign-blind `decisiveness` term.** `sharpness_from_wdl` uses only the draw share, so a
   position where you are *dead lost* scores ~0.95 decisiveness — maximum. It is **40% of
   `tactical_complexity`**, the largest weight, and it dominates hardest in the opening where the
   other terms are naturally small (measured: narrowness 0.264 opening vs 0.560 middlegame). Fixing
   it means changing a leader-owned metric that feeds the profile. **Propose, don't ship.**
3. **Whether the 9,000-game profile regeneration happens at all**, and at what scope.

---

## Do this first

### 1. The Φ-opening dataset needs rebuilding — its alarm fired and its spec is stale

`data/training/config_steering_opening/` exists (built 13:25, 35,826 pairs) and **must not be
trained on**:

- **A5 (phase-only AUC) = 0.6213, threshold < 0.60 — FAILED.** A fired alarm is a stop, not a
  parameter. Do not tune it away.
- **The culprit is named in the single-feature table: `castling_count`, AUC 0.3799** (0.62
  inverted). Puzzle "opening" positions are often uncastled; the negatives come from his games at
  plies 9–20 where he has usually castled. **Castling rights discriminate the classes.** Likely fix:
  add castling rights to the matching key, and/or draw negatives from earlier plies. Both are cheap.
- It also predates two amendments Thejus made after it was built: **`rating_window` is still
  [1500, 2200]** (he instructed: take **all** 265,339 opening puzzles, no rating filter) and the
  negative design changed (see the brief's Step 2b and Step 3).
- Watch `capture_available`: positives 93.77% vs negatives 83.75%, a **10-point** delta. A4 passes at
  0.5672 but that gap is the next leak channel if the castling one is closed.

**The brief is `agents/briefs/2026-09-03_phi-opening-dataset-and-kaggle-training.md`** and it is
current — Steps 2b and 3 carry the amendments. Hand it back to Gemini.

### 2. Two defects in the accepted wiring, already specified

From `agents/reports/2026-09-03_think-time-filter-and-phi-calibration-wiring_AUDIT.md` §3–§4:

- `aggregate_phase_clock` still **ANDs** the old clock filter — the aggregates use a stricter
  population than the findings. Drop the second condition.
- **Stage A's policy call runs on reflex moves and its result is discarded.** Either record a
  blindness tally for them or skip the call and save ~8 hours over the corpus.

### 3. Still only specified, never applied

`kaggle_files/diagnose_on_kaggle.py:434` binds **all 8 LC0 workers to GPU 0**
(`lambda: make_engine_instance(0)`). The fix is written in
`agents/briefs/2026-09-01_kaggle-gpu-profile-regeneration.md` §4b. **A report has described it in the
past tense; it is not in the code.** Do not run the LC0 rehearsal believing GPU 1 is in use.

---

## Numbers that are measured — do not re-derive, do not round

| | |
|---|---|
| Φ test AUC / material baseline | **0.6908** / 0.5017 — F1 (>0.70) **FAILED** |
| Φ per-source | N1 0.6955, N2 0.6841 (balanced ⇒ dataset honest) |
| Φ on **opening** positions | **0.7211** opening-vs-opening; 0.7543 vs all negatives |
| bootstrap on that baseline | SE 0.0164, 95% CI **[0.6876, 0.7536]** — a +0.03 gate is inside the noise |
| Φ on non-opening | 0.6867 — **Φ is strongest in the opening, not weakest** |
| calibration | test ECE **0.0522 → 0.0050**, isotonic fitted on val |
| general dataset | 261,748 rows; A3 0.4884, A4 0.5298 (leader-reverified) |
| opening puzzles in DB | **265,339** exact; ≥2200: **14,914**; ≥2700: 1,098; max 3118 |
| his corpus | **9,000 games**, 8,617 are 2+1 bullet; 228,020 nodes at the old filter |
| his think time | bullet median **2.0 s**, but **25.5%** of 252,365 bullet moves got ≥5 s |
| LC0 here | BLAS/DNNL, 2 cores, **~100 nodes/s**; 400 nodes → 3.64 s/position |
| full regeneration | **~51 days** on this machine (Stage A+B ≈1.4 min/game measured; the 8.2 total carries a *projected* TS2 term) |

---

## How to work with Thejus — read this, it is the part I got wrong twice today

- **He sets the aim. You lead the agents, not him.** His words: *"You are a leader of agents and not
  mine."* Do not re-open decisions he has made, do not reorder his priorities, do not answer a
  decision with a counter-proposal.
- **He is the ground-truth oracle** — ~2100 Lichess, ten years of modelling. When he makes a
  chess-domain claim, **think about what he means before deciding whether to check it**. Twice today
  I asserted against him without looking at data I had open, and he was right both times (the
  accepted/declined opening tags; what a puzzle's Glicko rating means).
- **Verify state, not judgement.** Re-run every number about the repo. Do not "correct" his domain
  reasoning reflexively — that is the habit he called out.
- He wants a verdict, not a survey, and honesty over comfort. Both at once.
- **Money is borrowed.** Finish a scoped batch in one turn; never end with a menu of remaining work.

---

## Traps live right now

- **A fired alarm is a stop, not a parameter.** A5 has fired. Rebuild, do not retune.
- **The negatives must be the same *shape* as the positives.** Measured: only **34.9%** of opening
  positives can find a spent-tactic partner in the same material bucket, because post-solution
  positions are down material by construction.
- **Rank on raw Φ, display the calibrated number.** Isotonic creates flat blocks; ranking on the
  calibrated value invents ties.
- **A variable named `playable` is not a guarantee.** That inference put a false safety claim in the
  live UI for a day. Follow it to its source.

---

## Session close, every time

1. Update `state/NOW.md` 2. Append `state/JOURNAL.md` 3. Commit 4. **Push to `windows-dev` and
verify `git log origin/windows-dev..HEAD` is empty.**
