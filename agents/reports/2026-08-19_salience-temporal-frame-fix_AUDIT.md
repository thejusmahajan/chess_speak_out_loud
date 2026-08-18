# AUDIT — `2026-08-19_salience-temporal-frame-fix`

**Auditor:** Leader (Claude Opus 5) · **Date:** 2026-08-19
**Verdict: ACCEPT.** The bug is fixed, the guards are real, the report matches the diff, and the
one instruction that mattered most (§6, change no scoring) was obeyed — verified by inspection,
not by the worker's word.

This is the cleanest worker delivery in the project's record.

---

## 1. Boundary check — PASS

Only the two permitted files changed: `backend/training/salience_matcher.py` (+57/−11) and
`backend/tests/test_salience_pipeline.py` (+104). `relational_facts.py`, `metrics.py`,
`salience_dataset.py`, `salience_lexicon.json` and `provenance_check.py` all untouched. The
`tmp_before.txt` scratch file was deleted as instructed. Nothing committed.

Other dirty paths in `git status` (`docs/study/*`, `docs/pytorch_learning/`, `downloads/`,
`kaggle_files/`, `profiles/`, `PUZZLE_STREAK_UI_REPORT.md`) predate this run.

## 2. Diff read in full — correct

SAN is derived by pushing moves onto a board built from the queried FEN, taking
`board.san(move)` **before** the push. Correct order, no hand-formatting, check/mate suffixes
preserved. All three tags (`delta_role`, `delta_move`, `delta_ply`) plus `text_raw` are set on
every branch. Dedup key widened to `(kind, text_raw, delta_role, delta_move)` at all three sites.

## 3. Gate re-run independently — PASS

```
297 passed, 5 skipped, 2 warnings in 106.39s
```
The worker reported a 290/5 baseline before its change and added 7 tests. 290 + 7 = 297,
matching my independent run exactly. `test_salience_pipeline.py` alone: 25 passed.

## 4. Mutation testing — PASS, both guards are real

Backed the file up, broke the production code, confirmed the tests go red, restored and
verified byte-identical.

| Mutation | Result |
|---|---|
| Removed the created-fact text qualification (`text = raw_text`) | **2 failed** — `test_created_facts_are_not_asserted_about_the_queried_position`, `test_san_prefix_is_correct` |
| Reverted the dedup key to `(kind, text_raw)` at all 3 sites | **2 failed** — `test_static_and_created_variants_both_survive_dedup`, `test_removed_facts_are_marked_as_no_longer_true` |

Neither is a vacuous test. The regression witness genuinely guards the original defect.

## 5. Real path on real data — PASS

The original false-fact witness, after the fix:

```
0.91 [created ply=2   ] After Bd3 Ng4 Qe4: P on e6 is pinned by e4 to Q on e7
0.56 [static  ply=None] White's c1 bishop is a bad bishop ...
0.46 [created ply=0   ] After Bd3: White's d3 bishop is active ...
0.46 [removed ply=2   ] No longer true after Bd3 Ng4 Qe4: White's d3 bishop is active ...
```

Every previously-false present-tense assertion is now temporally qualified and true. The
no-line path returns all-`static` facts with `text == text_raw`, unchanged.

**Independently verified the worker's test-5 claim** (the one place the brief allowed a weaker
substitute). It used a real position — rook leaves the d-file and returns — and three instances
of the same `text_raw` now survive with distinct roles:

```
role=created  move=e1d1  ply=2     After Re1 Kf8 Rd1: White's rook on the open d-file
role=removed  move=d1e1  ply=0     No longer true after Re1: White's rook on the open d-file
role=static   move=None  ply=None  White's rook on the open d-file
```

Under the old key only one of the three survived. The collision fix is demonstrated on a real board.

## 6. §6 compliance — verified, not trusted

Grepped the diff for any line touching `INFERENCE_PRIORS`, `salience_score`, `_inference_prior`
or the concept weights: **zero matches**. Created and removed facts receive exactly the same
score as static facts of the same kind. The temptation named in the brief was resisted.

## 7. Robustness checks the brief did not require

| Check | Result |
|---|---|
| `per_move[i]["move"] == line[i]` over **3,000** real puzzle lines | 0 mismatches — the positional `san_prefixes[ply_idx]` indexing is sound |
| Illegal move in the line | No new crash — identical to pre-change behaviour |
| Line continuing past checkmate | No new crash |
| Malformed UCI | Raises `InvalidMoveError` both before and after — pre-existing, not a regression |
| Does the SAN prefix contaminate prose alignment? | **No.** `_fact_squares` reads structured fields only, never `text`, so the added `d3`/`g4`/`e4` tokens cannot create false square grounding |

That last one was the risk I considered most likely to bite, and it does not.

---

## 8. Observations for whoever wires this up (not defects)

1. **A created/removed pair can co-occur and read oddly.** The witness returns both
   *"After Bd3: White's d3 bishop is active"* and *"No longer true after Bd3 Ng4 Qe4: White's d3
   bishop is active"*. Both are true and temporally distinct, but a consumer must handle the
   pair rather than present them as contradictory.
2. **The dedup key still omits `fact_pov`** — pre-existing behaviour, unchanged by this work.
   Two colours producing byte-identical text would collide, first-seen winning. Not triggered by
   current fact phrasing (texts embed the colour), but worth a follow-up brief.
3. **`san_prefixes` is indexed positionally** while `delta_move` has a lookup fallback. The
   invariant holds over 3,000 real lines, so this is low risk; noted only so it is on record.
