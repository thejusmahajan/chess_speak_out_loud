# AUDIT — `2026-09-02_configuration-dataset-rebuild`

**Auditor:** leader (Opus 5), 2026-09-02
**Verdict: AUDITED ACCEPT. The leak is gone. The dataset is ready to train on.**

---

## 1. Every gate re-run independently from the `.npz`

Not read from the report — recomputed from the files on disk with the leader's own logistic
regression (torch LBFGS) and the leader's own decoder.

| gate | reported | **leader's re-run** | threshold | verdict |
|---|---|---|---|---|
| **A3** material-only AUC | 0.4870 | **0.4884** | < 0.65 | ✅ |
| **A4** 14-feature AUC | 0.5270 | **0.5298** | < 0.60 | ✅ |
| match rate | 65.44% | 65.44% (130,874 / 200,000) | ≥ 60% | ✅ no key widening |
| `source` per row | added | present; counts **exactly** match `STATS.md` in all three splits | required | ✅ |
| tests | 5 passed | 5 passed | — | ✅ |

## 2. The leak that killed the first build is gone

Recomputed by decoding 9,000 val positions to boards — the same probe that failed the previous
build, run against the new files:

| | in check | legal moves | capture available | checks available |
|---|---|---|---|---|
| positives (`s_err`) | **1.97%** | **30.20** | 82.1% | 1.20 |
| negatives (matched) | **2.01%** | **30.23** | 78.2% | 1.15 |
| *previous build* | *11.2% vs 36.7%* | *28.3 vs 19.4* | *77.9% vs 51.6%* | — |

`n_legal` was the strongest single leak at AUC 0.6621; it is now 0.4971. The fix worked, and the
14-feature model that scored 0.6637 on the old build scores **0.5298** on this one.

## 3. Mutation-check — the tests are guards, not decoration

A passing test proves nothing until the code it protects is broken. Disabled the colour flip in
`encode.py:39` (`b = board.mirror() if board.turn == chess.BLACK else board` → `b = board`):

```
FAILED backend/tests/test_config_steering.py::test_colour_invariance
FAILED backend/tests/test_config_steering.py::test_encode_decode_round_trip
2 failed, 3 passed
```

Restored; `git diff` clean; 5 passed. **The frame guard is real.** This is the class of bug that
cost this project months in `saliency()`, and it is now defended by a test that actually fails.

## 4. Two findings the brief did not ask for

Both are minor. Neither blocks training. Recording them so they are not rediscovered later.

**4a. En-passant is a small pure-leak channel.** A new probe on the castling and en-passant planes
— encoded, but *not* part of the matching key — gives AUC **0.5193** overall, which is fine. But the
ep plane alone is set in **2.4% of negatives and 0.1% of positives**, a 24× relative difference.
Cause: N2 samples every 3rd ply of real games, so a double pawn push has often just happened;
puzzle FENs almost never carry one.

It contributes almost nothing to the combined AUC, and en passant carries essentially no
configuration information. **Recommendation: zero plane 16 in the encoder** — it removes a leak
channel at no cost to the signal. Not urgent; do it before the final training run, not now.

**4b. 182 boards (0.695% of val) also appear in train; 5 carry contradictory labels.** Three boards
inside train alone carry both labels. The split is by puzzle-id hash, which cannot see two
*different* puzzles that transpose to the same position, nor a position that is a puzzle `s_err` in
one game and quiet play in another. That last case is genuine and irreducible — the same board
really can be both. At 0.019% contradictory it will not move an AUC, and it is a useful reminder
that Φ's ceiling is below 1.0 by construction.

## 5. What it cost, and it was worth it

The tighter key dropped the match rate from 75.28% to 65.44%, so the dataset shrank from 301,116
rows to **261,748** (train 209,036 / val 26,222 / test 26,490), and `train.npz` from 39.7 MB to
34.7 MB. N2's share rose from 25% to 40% of negatives, as intended.

**Fewer rows of an honest dataset beats more rows of an artefact.** The previous build had 15%
more data and measured whether the side to move was in check.

## 6. Where this leaves the plan

`PLAN_CONFIGURATION_STEERING.md` §8b's ladder: **B0 is passed** — F0 and the alarms are green, twice,
independently. **B1** (50k + 50k, does Φ learn anything) and **B2** (full set, held-out AUC = F1)
are Thejus's to run in PyTorch on Kaggle. Nothing here needs a GPU until he starts.

Reminder from §3 of the plan, to carry into any write-up: Φ learns **what a human in the 1500–2200
band gets wrong**, not objective attacking potential. That is the right target for coaching and it
must never be claimed as more.
