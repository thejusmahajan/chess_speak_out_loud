# AUDIT — `2026-09-01_configuration-dataset-build`

**Auditor:** leader (Opus 5), 2026-09-02
**Verdict: REBUILD REQUIRED.** The delivery is honest and the brief was followed exactly. **The
dataset is not usable, and the fault is in my spec, not in the worker's execution.**

---

## 1. What was verified and holds

| claim | leader's independent check | verdict |
|---|---|---|
| A3 material-only AUC = **0.4920** | re-fit from the `.npz` with a torch LBFGS logistic regression on the 10 piece counts: **0.4924** | ✅ real, and the small delta is just a different optimiser |
| split counts sum to 150,558 per class | 120398+14927+15233 = 150,558; negatives likewise | ✅ |
| A2 material overlap | top-10 keys identical in both classes, count for count | ✅ — matching is exact |
| build artefacts | `train.npz` 39.7 MB, `val` 5.0 MB, `test` 5.0 MB, `manifest.json`, `STATS.md` | ✅ present |
| `sklearn` used for A3 | **not installed in `cszero`** — but `build_dataset.py:112-158` has a hand-rolled fallback that is what actually ran | ✅ not a fabrication; the report should have said which path executed |

**No fabricated numbers.** Match rate 75.28% without widening the key, stride 9 over the 1,907,960
puzzles in the rating window, all three specified alarms genuinely computed and genuinely passed.

---

## 2. The defect — a leak none of my three alarms could see

A1/A2/A3 all interrogate **material**. I never specified a control for anything else. Decoding
1,500 positions per class from the val split:

| | in check | mean legal moves | capture available |
|---|---|---|---|
| **positives** (`s_err`) | **11.2%** | **28.3** | 77.9% |
| **negatives** (matched) | **36.7%** | **19.4** | 51.6% |

As single-feature AUCs on 8,000 val rows: `n_legal` **0.6621**, `in_check` **0.6178**,
`capture_avail` 0.3782 (informative inverted). Fitted together:

```
A4 cheap-tactical-features AUC = 0.6637   (my own material threshold was 0.65)
```

**Three features that know nothing about configuration separate the classes better than the
material gate allows.** A CNN trained on this would learn *"am I in check, and how many moves do I
have"*, score well, and mean nothing — the exact failure the round table, the worker's own §4, and
my own §5 all named in advance, arriving through the one door none of us watched.

**Cause.** The N1 "spent tactic" negative is *the position after the full solution line*. Puzzle
solutions disproportionately end in check or mate — `mate` is in the top-10 theme vocabulary —
so N1 is systematically a low-mobility, in-check position. 113,002 of 150,558 negatives are N1.

**This is my error.** I specified a negative whose construction guarantees an artefact, and three
alarms that could not detect it. `LEADER_GROUNDING.md` §3d.2 asks of every gate: *what is the
cheapest way to pass this without doing the work?* I asked that about material and stopped there.

---

## 3. Required changes — see `agents/briefs/2026-09-02_configuration-dataset-rebuild.md`

1. **Exclude pathological N1**: drop any N1 position where the side to move is in check, and any
   puzzle whose `themes` contain `mate`.
2. **Extend the matching key** to `(material_key, phase_bucket, in_check, mobility_bucket)` so a
   negative must look as calm as the positive it is matched to.
3. **Widen N2** (his own games) to compensate for the lost N1 volume.
4. **Add alarm A4** — logistic regression on the 10 piece counts *plus* `in_check`, `n_legal_moves`,
   `capture_available`, `n_checks_available` — **must be < 0.60**. Hard stop.
5. **Store `source` per row** in the `.npz`. It is currently only in `manifest.json` aggregate
   counts, so F1 cannot be run separately against N1 and N2 as `PLAN` §10.3 requires.

**Keep:** the encoder, the tests, the split-by-hash scheme, the stride sampling, the theme
vocabulary, and the A1–A3 machinery. Only the negative construction and the alarm set change.
