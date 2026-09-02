```
Brief-ID:      2026-09-02_configuration-dataset-rebuild
Written:       2026-09-02
Target repo:   chess_speak_out_loud
Route:         Antigravity (full workspace)
Type:          amendment to 2026-09-01_configuration-dataset-build -- rebuild, not a fresh build
Blast-radius:  backend/training/config_steering/ (existing), data/training/config_steering/ (rebuilt)
Reversibility: trivial
Failure-mode:  SILENT -- the previous build passed every gate it was given and was still unusable
```

**Your previous delivery was correct.** It followed the brief exactly, invented no numbers, and its
three alarms genuinely passed — the leader re-fitted A3 independently and got 0.4924 against your
0.4920. **The dataset is being rebuilt because the brief was wrong, not because you were.**

---

## 1. INTENT

*(Intent outranks instructions. If any instruction below conflicts with this paragraph, the intent
wins — stop and report.)*

The negatives are separable from the positives by three features that have nothing to do with chess
configuration. Fix the negative construction so that they are not, and add the alarm that would have
caught it.

**Read `agents/reports/2026-09-01_configuration-dataset-build_AUDIT.md` §2 first** — it has the
measured numbers.

The short version: the N1 "spent tactic" negative is the position after the *full* solution line,
and puzzle solutions disproportionately end in check or mate. So:

| | in check | mean legal moves |
|---|---|---|
| positives (`s_err`) | 11.2% | 28.3 |
| negatives | 36.7% | 19.4 |

`n_legal` alone gives AUC 0.6621; the three together give **0.6637**, above the 0.65 bar that was
set for material.

---

## 2. WHAT CHANGES — five things, nothing else

Keep the encoder, the tests, the split-by-puzzle-id-hash, the stride sampling, the theme vocabulary
and the A1–A3 machinery exactly as they are.

### 2.1 Exclude pathological N1
Drop an N1 candidate if **either**:
- the side to move in the post-solution position **is in check**, or
- the puzzle's `themes` contains `mate` (its line ends terminally by construction).

### 2.2 Extend the matching key
```
key = (material_key, phase_bucket, in_check, mobility_bucket)
mobility_bucket = len(list(board.legal_moves)) // 6
```
A negative must now look as calm as the positive it is matched to. Positives with no match are
**dropped, never back-filled** — unchanged from before.

### 2.3 Widen N2 to compensate
N1 volume will fall sharply (it was 113,002 of 150,558 negatives). Sample his games
(`games_of_derdiedasdie/lichess_derdiedasdie_2026-07-21.pgn`, **9,000 games**) at **every 3rd ply**
instead of every 6th, still skipping the first 8 and last 10 plies. Report the resulting N2 pool
size before matching.

If the match rate still falls below 60%, **stop and report** — do not widen `material_key` on your
own initiative.

### 2.4 Add alarm A4 — the one that would have caught this
Logistic regression, fit on train, AUC on val, over **14 features only**:

```
the 10 piece counts, in_check, n_legal_moves, capture_available, n_checks_available
```

**A4 must be < 0.60.** If it fires, **stop and report** — do not tune it away, and do not proceed
to write the splits. Report A4 both over the whole negative set and separately for N1-only and
N2-only negatives, so we can see which pool carries any residual artefact.

Also report each single-feature AUC, as the audit did, so a marginal pass cannot hide one bad
feature.

### 2.5 Store `source` per row
Add a `source` array to each `.npz` (uint8: 0 = positive `s_err`, 1 = `n1_spent`, 2 = `n2_quiet`).
It currently exists only as aggregate counts in `manifest.json`, and `PLAN` §10.3 requires F1 to be
runnable against N1 and N2 separately.

---

## 3. CHECKPOINTS

1. N2 pool size at every-3rd-ply sampling, and the N1 pool size after the §2.1 exclusions.
2. Match rate under the extended key, and the final per-class, per-source counts.
3. **`STATS.md` in full, with A1, A2, A3, A4 and the four single-feature AUCs.**
4. `python -m pytest backend/tests/test_config_steering.py -q` and the full suite with the usual
   deselect, both against the baseline you recorded last time.
5. The in-check / mean-legal-moves / capture-available table for positives vs negatives, in the same
   shape as the audit's, so the fix can be read at a glance.

---

## 4. REPORT

`agents/reports/2026-09-02_configuration-dataset-rebuild_REPORT.md`, with every checkpoint's real
pasted output and:

> **If exactly one thing in this delivery is wrong, what is it most likely to be, and did I check
> that?**

---

## 5. STOP AND ASK

Not covered: widening `material_key`; changing the rating window, the 200,000 target, the seed or
the split ratios; touching anything outside `backend/training/config_steering/` and
`data/training/config_steering/`; training anything; committing.

**A fired alarm is a stop, not a parameter.** Reporting one is a successful delivery.
