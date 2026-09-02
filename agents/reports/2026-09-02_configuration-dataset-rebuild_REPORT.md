# Worker Report: Configuration Dataset Rebuild

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

**Environment:** Conda `cszero` (`C:\Users\Admin\miniconda3\envs\cszero\python.exe`). CPU and local disk only. No GPU, no engine, no network.

---

## 1. Executive Summary & Defect Elimination

In the initial build (`2026-09-01`), the dataset passed all material-based gates (A1, A2, A3), but as identified in the leader's audit (`2026-09-01_configuration-dataset-build_AUDIT.md`), the N1 spent-tactic negatives were severely distorted by tactical artifacts: post-solution lines disproportionately ended in check (36.7% vs 11.2%) with suppressed mobility (19.4 vs 28.3 moves), yielding an unauthorized tactical classifier with A4 AUC = 0.6637.

This rebuild implements all five amendments specified in `2026-09-02_configuration-dataset-rebuild.md`:
1. **Excluded Pathological N1 (§2.1):** Excluded all puzzles with `"mate"` in themes and dropped any candidate where the post-solution position had `board.is_check() == True` (146,824 in-check candidates dropped).
2. **Extended Matching Key (§2.2):** Matched on `key = (material_key, phase_bucket, in_check, mobility_bucket)` where `mobility_bucket = len(list(board.legal_moves)) // 6`, partitioned by turn parity (`is_white_to_move`).
3. **Widened N2 Sampling (§2.3):** Sampled `games_of_derdiedasdie/lichess_derdiedasdie_2026-07-21.pgn` at every 3rd ply (step 3), doubling the N2 pool to **131,346 positions**.
4. **Added Alarm A4 (§2.4):** Evaluated 14-feature Logistic Regression (10 piece counts + `in_check`, `n_legal_moves`, `capture_available`, `n_checks_available`). **A4 AUC dropped from 0.6637 to 0.5270** (safely below the 0.60 ceiling).
5. **Stored `source` per row (§2.5):** Added `source` array (`uint8`: 0 = `s_err`, 1 = `n1_spent`, 2 = `n2_quiet`) to all three `.npz` files and exposed it through `load_split(name)`.

---

## 2. Checkpoint Outputs

### Checkpoint 1 — Candidate Pool Sizes
- **N2 Pool Size (every 3rd ply sampling):** **131,346 positions** (extracted from 9,000 games of `derdiedasdie`, plies 9 to $T-10$, step 3).
- **N1 Pool Size (after §2.1 exclusions):** **653,176 positions** (all `mate` puzzles excluded up front; 146,824 in-check post-solution candidates dropped).

---

### Checkpoint 2 — Match Rate & Final Split Counts
- **Extended Key:** `(material_key, phase_bucket, in_check, mobility_bucket)` partitioned by `is_white_to_move`.
- **Match Rate:** **65.44%** (130,874 matched pairs / 200,000 target positives). Safely exceeds the 60% threshold without widening `material_key`.
- **Final Positive Count (`s_err`):** **130,874**
- **Final Negative Count (Total):** **130,874**
  - **Matched $N_2$ (quiet play):** **52,301** (39.96% of negatives)
  - **Matched $N_1$ (spent tactic):** **78,573** (60.04% of negatives)
- **Total Dataset Size:** **261,748 rows**

| Split | Positives (`s_err`) | Negatives (Total) | $N_1$ (`n1_spent`) | $N_2$ (`n2_quiet`) | Total Rows |
|---|---|---|---|---|---|
| **train** | 104,712 | 104,324 | 62,858 | 41,466 | 209,036 |
| **val** | 12,999 | 13,223 | 7,917 | 5,306 | 26,222 |
| **test** | 13,163 | 13,327 | 7,798 | 5,529 | 26,490 |
| **TOTAL** | **130,874** | **130,874** | **78,573** | **52,301** | **261,748** |

---

### Checkpoint 5 — Tactical Balance Table (Audit Comparison)

Comparison of tactical leak features on the held-out validation set ($N = 26,222$ positions):

| Feature | Positives (`s_err`) | Negatives (Matched) | Delta (New Build) | Audit Baseline (Old Build) |
|---|---|---|---|---|
| **In check** | **1.88%** | **2.01%** | **0.13%** | Pos: 11.2% vs Neg: 36.7% (25.5% leak) |
| **Mean legal moves** | **30.08** | **30.22** | **0.14 moves** | Pos: 28.3 vs Neg: 19.4 (8.9 moves leak) |
| **Capture available** | **81.99%** | **78.76%** | **3.23%** | Pos: 77.9% vs Neg: 51.6% (26.3% leak) |

The tactical disparity between positives and negatives has been completely flattened.

---

### Checkpoint 3 — STATS.md in Full

```markdown
# Configuration Steering Dataset Rebuild — STATS.md

**Build Date:** 2026-09-02T16:14:58.068801+00:00
**Seed:** 20260901
**Sampling Stride:** 9 (from 1907960 puzzles in rating window [1500, 2200])
**Match Rate:** 65.44% (130874 / 200000)

---

## 1. Summary Counts

| Split | Positives (s_err) | Negatives (Total) | N1 (n1_spent) | N2 (n2_quiet) | Total Rows |
|---|---|---|---|---|---|
| **train** | 104712 | 104324 | 62858 | 41466 | 209036 |
| **val** | 12999 | 13223 | 7917 | 5306 | 26222 |
| **test** | 13163 | 13327 | 7798 | 5529 | 26490 |
| **TOTAL** | 130874 | 130874 | 78573 | 52301 | 261748 |

---

## 2. Tactical Balance Table (Audit Checkpoint 5)

Comparison of tactical leak features on the held-out validation set:

| Feature | Positives (s_err) | Negatives (Matched) | Delta | Audit Baseline (Old Build) |
|---|---|---|---|---|
| **In check** | 1.88% | 2.01% | 0.13% | Pos: 11.2% vs Neg: 36.7% |
| **Mean legal moves** | 30.08 | 30.22 | 0.14 | Pos: 28.3 vs Neg: 19.4 |
| **Capture available** | 81.99% | 78.76% | 3.23% | Pos: 77.9% vs Neg: 51.6% |

---

## 3. The Four Alarms

| Alarm | Measurement | Target / Threshold | Status |
|---|---|---|---|
| **A1 Side-to-move balance** | Positives: 49.05% WTM<br>Negatives: 49.05% WTM | 50 ± 2% in both classes | **PASS** |
| **A2 Material key overlap** | Top 10 overlap: 10/10 shared | Substantial overlap | **PASS** |
| **A3 Material-only AUC** | 10 piece counts: **AUC = 0.4870** | **AUC < 0.65** | **PASS** |
| **A4 Cheap-tactical + material AUC** | 14 features: **AUC = 0.5270**<br>• N1-only: 0.5103<br>• N2-only: 0.5519 | **AUC < 0.60** | **PASS** |

---

## 4. Single-Feature AUCs (Validation Split)

| Feature | Single-Feature ROC AUC | Notes |
|---|---|---|
| `in_check` | 0.4993 | Exactly matched |
| `n_legal_moves` | 0.4971 | Mobility bucket matched |
| `capture_available` | 0.5161 | Informative / balanced |
| `n_checks_available` | 0.5064 | Tactical check threat |

---

## 5. A2 Material Key Comparison (Top 10)

| Rank | Positives (s_err) | Count | Negatives (Matched) | Count |
|---|---|---|---|---|
| 1 | `7-2-2-2-1|7-2-2-2-1` | 2359 | `7-2-2-2-1|7-2-2-2-1` | 2359 |
| 2 | `4-0-0-0-0|4-0-0-0-0` | 1491 | `4-0-0-0-0|4-0-0-0-0` | 1491 |
| 3 | `5-0-0-0-0|5-0-0-0-0` | 1433 | `5-0-0-0-0|5-0-0-0-0` | 1433 |
| 4 | `7-1-2-2-1|7-1-2-2-1` | 1398 | `7-1-2-2-1|7-1-2-2-1` | 1398 |
| 5 | `3-0-0-0-0|3-0-0-0-0` | 1398 | `3-0-0-0-0|3-0-0-0-0` | 1398 |
| 6 | `6-1-1-2-1|6-1-1-2-1` | 1375 | `6-1-1-2-1|6-1-1-2-1` | 1375 |
| 7 | `7-1-1-2-1|7-1-1-2-1` | 1193 | `7-1-1-2-1|7-1-1-2-1` | 1193 |
| 8 | `2-0-0-1-0|2-0-0-1-0` | 1102 | `2-0-0-1-0|2-0-0-1-0` | 1102 |
| 9 | `6-2-2-2-1|6-2-2-2-1` | 1101 | `6-2-2-2-1|6-2-2-2-1` | 1101 |
| 10 | `6-1-2-2-1|6-1-2-2-1` | 1067 | `6-1-2-2-1|6-1-2-2-1` | 1067 |

---

## 6. Top 20 Motif Themes (Vocabulary)

`crushing`, `short`, `endgame`, `middlegame`, `advantage`, `long`, `master`, `veryLong`, `fork`, `sacrifice`, `defensiveMove`, `mate`, `advancedPawn`, `pin`, `kingsideAttack`, `pawnEndgame`, `rookEndgame`, `quietMove`, `opening`, `discoveredAttack`
```

---

### Checkpoint 4 — Pytest Output & Non-Regression Gate

**Command 1:**
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests/test_config_steering.py -q
```
**Output:**
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 5 items

backend\tests\test_config_steering.py .....                              [100%]

============================== 5 passed in 1.68s ==============================
```

**Command 2 (Full Test Suite):**
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests -q --deselect backend/tests/test_ts2_no_hang.py::test_ts2_orphan_future_cancellation_handled
```
**Output:**
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 302 items / 1 deselected / 301 selected

backend\tests\test_attention_export.py .....                             [  1%]
backend\tests\test_batched_saliency.py ss                                [  2%]
backend\tests\test_book_parser.py ....                                   [  3%]
backend\tests\test_cache_replay_identity.py .                            [  3%]
backend\tests\test_concept_mapper_motifs.py ...                          [  4%]
backend\tests\test_config_steering.py .....                              [  6%]
backend\tests\test_critical_points.py ....                               [  7%]
backend\tests\test_descriptive_notation.py ....................          [ 14%]
backend\tests\test_eco_backfill.py ....                                  [ 15%]
backend\tests\test_engine_pool.py .....                                  [ 17%]
backend\tests\test_eval_batch.py sss                                     [ 18%]
backend\tests\test_harvest_batch_screen.py ...                           [ 19%]
backend\tests\test_health.py .                                           [ 19%]
backend\tests\test_intuition.py ......                                   [ 21%]
backend\tests\test_llm_seam.py ..                                        [ 22%]
backend\tests\test_openings.py .....                                     [ 24%]
backend\tests\test_openings_sharpness.py .....                           [ 25%]
backend\tests\test_phase_b_split.py ...                                  [ 26%]
backend\tests\test_phase_clock_agg.py .......                            [ 29%]
backend\tests\test_position_plan_facts.py ..                             [ 29%]
backend\tests\test_positional_detectors.py .....                         [ 31%]
backend\tests\test_positional_detectors_b2.py .......                    [ 33%]
backend\tests\test_positional_detectors_b3.py ....                       [ 35%]
backend\tests\test_puzzle_sets.py ........                               [ 37%]
backend\tests\test_relational_facts.py ......                            [ 39%]
backend\tests\test_repertoire_drills.py .......                          [ 42%]
backend\tests\test_repertoire_tree.py .....                              [ 43%]
backend\tests\test_retag.py ....                                         [ 45%]
backend\tests\test_sac_drill.py .......                                  [ 47%]
backend\tests\test_sac_playout.py ......                                 [ 49%]
backend\tests\test_salience_pipeline.py .........................        [ 57%]
backend\tests\test_suspects_deck.py ..........                           [ 61%]
backend\tests\test_tactics_pov.py .....                                  [ 62%]
backend\tests\test_terminal_analysis.py ...                              [ 63%]
backend\tests\test_training_attempts.py ......                           [ 65%]
backend\tests\test_training_clk.py ....                                  [ 67%]
backend\tests\test_training_drills.py ..............                     [ 71%]
backend\tests\test_training_gems.py .......                              [ 74%]
backend\tests\test_training_metrics.py .......                           [ 76%]
backend\tests\test_training_pipeline_color.py .                          [ 76%]
backend\tests\test_training_pipeline_steer.py .....                      [ 78%]
backend\tests\test_training_select.py ............                       [ 82%]
backend\tests\test_training_steer.py ...........                         [ 86%]
backend\tests\test_training_store.py ........                            [ 88%]
backend\tests\test_trends_endpoint.py .                                  [ 89%]
backend\tests\test_ts2_no_hang.py .                                      [ 89%]
backend\tests\test_tutor_compare.py ....................                 [ 96%]
backend\tests\test_usual_suspects.py .......                             [ 98%]
backend\tests\test_weakness_ranking_endpoint.py .....                    [100%]

============================== warnings summary ===============================
..\..\miniconda3\envs\cszero\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\Admin\miniconda3\envs\cszero\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

backend/tests/test_attention_export.py::test_shapes_and_schema
backend/tests/test_attention_export.py::test_frame_matches_the_audited_api
backend/tests/test_attention_export.py::test_black_to_move_is_not_mirrored
backend/tests/test_attention_export.py::test_quantisation_round_trip
  C:\Users\Admin\miniconda3\envs\cszero\Lib\site-packages\onnx2torch\node_converters\slice.py:63: UserWarning: Using a non-tuple sequence for multidimensional indexing is deprecated and will be changed in pytorch 2.9; use x[tuple(seq)] instead of x[seq]. In pytorch 2.9 this will be interpreted as tensor index, x[torch.tensor(seq)], which will result either in an error or a different result (Triggered internally at C:\actions-runner\_work\pytorch\pytorch\torch\csrc\autograd\python_variable_indexing.cpp:355.)
    x = x[pos_axes_slices]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
==== 296 passed, 5 skipped, 1 deselected, 5 warnings in 115.87s (0:01:55) =====
```

**Non-Regression Summary:**
- Baseline: 296 passed, 5 skipped, 1 deselected.
- Current: 296 passed, 5 skipped, 1 deselected.
- Zero regressions.

---

## 3. Storage Verification of `source` Array

Verified via Python on disk:
- `train.npz`: `source` array shape `(209036,)`, dtype `uint8`, counts: `[104712, 62858, 41466]`
- `val.npz`: `source` array shape `(26222,)`, dtype `uint8`, counts: `[12999, 7917, 5306]`
- `test.npz`: `source` array shape `(26490,)`, dtype `uint8`, counts: `[13163, 7798, 5529]`
- `load_split(name)` correctly unpacks `"source"` with shape `(N,)` and values in `{0, 1, 2}`.

---

## 4. Wall-Clock Timings

| Stage | Operations | Wall-Clock (s) |
|---|---|---|
| **Step 2** | Scan 1.9M puzzles, extract 200,000 $s_{err}$ positive bitboards & 14 tactical features | 321.25s |
| **Step 3 (N1)** | Replay 800,000 candidate lines, filter out 146,824 in-check positions & mate themes | 659.00s |
| **Step 3 (N2)** | Parse 9,000 PGN games, extract 131,346 quiet play positions at step 3 | 172.02s |
| **Step 4** | Exact bucketed matching under extended 4-tuple key | 15.34s |
| **Step 5** | Deterministic hash split, write 3 `.npz` files with `source` array + `manifest.json` | 9.88s |
| **Step 6** | Fit PyTorch L-BFGS Logistic Regression for A3 & A4, compute 4 single-feature AUCs | 3.38s |
| **Total Pipeline** | Complete end-to-end dataset rebuild | **1,180.87s (19.68 min)** |

---

## 5. Prediction: Most Likely Defect and Verification

> **If exactly one thing in this delivery is wrong, what is it most likely to be, and did I check that?**

**Prediction:**
The most likely defect would be **leakage of tactical check-threat features** (e.g. `n_checks_available`, the count of moves the side to move has that give check to the opponent).

While `in_check` controls whether the side to move *is* in check, and `mobility_bucket` controls overall move count, if blunder-prone positions systematically had more forcing checks available than calm positions, a classifier could still distinguish them with AUC $> 0.55$.

**Did I check that?**
Yes:
1. Measured single-feature AUC for `n_checks_available` on the held-out validation set: **AUC = 0.5064** (almost exact 0.500 chance level).
2. The 14-feature model combining piece counts, `in_check`, `n_legal_moves`, `capture_available`, and `n_checks_available` achieved **AUC = 0.5270**, confirming that neither check status nor check-giving threats create an exploitable separation.

---

## 6. Could Not Check

1. **Downstream CNN Convergence on Kaggle GPUs:** As with the initial delivery, actual PyTorch CNN training convergence is in Thejus's hands. The dataset on disk has been verified for all structural, tactical, and shape invariants.
2. **LC0 Inference Re-Ranking (Gate F3):** Real-time potential-guided move selection on LC0 was out of scope for this dataset build brief.
