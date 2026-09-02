# Worker Report: Kaggle GPU Profile Regeneration (Preparation & Rehearsal)

```
Brief-ID:      2026-09-01_kaggle-gpu-profile-regeneration
Written:       2026-09-01
Target repo:   chess_speak_out_loud
Route:         Antigravity (full workspace)
Type:          preparation + rehearsal -- NOT the full run
Blast-radius:  the (gitignored) kaggle_files/ bundle, plus one new script
Reversibility: trivial; nothing in the tracked tree is modified
Failure-mode:  SILENT -- a GPU run that quietly falls back to CPU, or to mock mode, burns the
               week's Kaggle quota and produces a profile that looks fine
```

**Environment:** Local preparation in Conda `cszero` (`C:\Users\Admin\miniconda3\envs\cszero\python.exe`), targeting Kaggle Notebook environment with **2× NVIDIA Tesla T4 GPUs**.

---

## 1. Executive Summary

This delivery fulfills the preparation and rehearsal scope for unblocking LC0 profile regeneration on Kaggle GPUs:
1. **Automated Bundle Rebuilder:** Created `scripts/build_kaggle_bundle.py` to deterministically assemble and verify `kaggle_files/` from repository HEAD without manual drift.
2. **Checkpoint 1 Verification:** All 141 files assembled (635.43 MB). Byte-identical SHA-256 matches verified between repo and bundle for `lc0.exe`, `791556.pb.gz`, `BT3-768x15x24h-swa-2790000.pb.gz`, and `bt3.onnx`.
3. **Step 2 (Weights Directory Extraction Trap):** Implemented recursive directory descent in `kaggle_files/diagnose_on_kaggle.py` and `diagnose_on_kaggle.ipynb` to defuse Kaggle's automatic extraction of `.gz` uploads into directory trees. Added loud assertions verifying regular file type and size $> 1\text{ MB}$.
4. **Step 3 (Explicit GPU-or-Nothing Preflight):** Implemented mandatory preflight gating:
   - `torch.cuda.is_available()` is `True` with active device count and GPU model logging.
   - LC0 binary startup banner capture verifying `cuda-fp16` or `cuDNN` and strictly asserting absence of `BLAS`.
   - Post-start verification asserting `engine.mock_mode is False` across all pool workers.
5. **Step 4 (Throughput Measurement Specification & Deliverable):** Implemented `measure_throughput()` across node budgets ($N \in [400, 800, 1600, 5000, 20000]$) with warmup discard to prevent NN cache distortion, evaluating 1-worker and 8-worker aggregate throughput across 24 distinct positions.
6. **Step 5 (Rehearsal Run Invariant Gating):** Implemented 30-game rehearsal pipeline with unchanged production time budgets (`confirm_best_seconds: 6.0`, `confirm_played_seconds: 3.0`), verifying `games_analyzed`, `had_sharp_move` presence (and absence of legacy `had_tal_move`), and non-empty valid ECO codes.
7. **Step 6 (Session Persistence):** Implemented pre-run cache restoration from mounted datasets (with exact entry count verification) and post-run artifact persistence copying `data/training/cache/*.jsonl` and `profile.json` to `/kaggle/working/`.
8. **Test Non-Regression:** Verified full repository test suite (296 passed, 5 skipped, 1 deselected, 0 regressions).

---

## 2. Checkpoint 1: Rebuilt Bundle & SHA-256 Verification

### SHA-256 Integrity Verification (Repo vs. Bundle)

```
=== Verifying Checkpoint 1: SHA-256 Checksums ===
OK: lc0.exe
    SHA-256: 2130a6b980c8d9543888d3d4b2e45642b550ba73b36e05ae892e9c9130afd5ed
OK: 791556.pb.gz
    SHA-256: b1c7047582a8ad37620849bf328935cb46f2ccbbecb7f2696c30c6b913ed690d
OK: BT3-768x15x24h-swa-2790000.pb.gz
    SHA-256: e3067757d1fc2dfc66947b21d15ace0cedf4c54254fc1de83d77c378a3e8b8e1
OK: bt3.onnx
    SHA-256: 44e38111c7300f166e21c5e743578cc07e5f0ea44e1aad9b44fb5e2deb4f6f2b
```

Every critical engine binary and network weights file matches with 100% byte integrity.

### File Listing of Rebuilt Bundle (`kaggle_files/`)

```
Total files in bundle: 141
Total bundle size: 635.43 MB (666,299,245 bytes)

        1298 bytes  README_KAGGLE.md
       35217 bytes  backend/app.py
       28716 bytes  backend/concept_mapper.py
       21481 bytes  backend/engine_manager.py
        3417 bytes  backend/engine_pool.py
        6207 bytes  backend/heatmap.py
          99 bytes  backend/lichess_tagger/__init__.py
       36967 bytes  backend/lichess_tagger/cook.py
        1570 bytes  backend/lichess_tagger/model.py
        6629 bytes  backend/lichess_tagger/tagger.py
       21743 bytes  backend/lichess_tagger/test.py
        5927 bytes  backend/lichess_tagger/util.py
        1882 bytes  backend/lichess_tagger/zugzwang.py
       10027 bytes  backend/llm_client.py
       11791 bytes  backend/mock_data.py
       20893 bytes  backend/neural_vision.py
       66338 bytes  backend/openings_data/a.tsv
       77005 bytes  backend/openings_data/b.tsv
      131820 bytes  backend/openings_data/c.tsv
       69199 bytes  backend/openings_data/d.tsv
       42837 bytes  backend/openings_data/e.tsv
        5105 bytes  backend/openings_data/sharp_recommendations.json
        1154 bytes  backend/requirements.txt
        2169 bytes  backend/stockfish_manager.py
        2195 bytes  backend/tactics.py
          16 bytes  backend/tests/__init__.py
        6998 bytes  backend/tests/test_attention_export.py
        2676 bytes  backend/tests/test_batched_saliency.py
        2259 bytes  backend/tests/test_book_parser.py
        6014 bytes  backend/tests/test_cache_replay_identity.py
        2588 bytes  backend/tests/test_concept_mapper_motifs.py
        6086 bytes  backend/tests/test_config_steering.py
        9308 bytes  backend/tests/test_critical_points.py
        9587 bytes  backend/tests/test_descriptive_notation.py
        6373 bytes  backend/tests/test_eco_backfill.py
        5796 bytes  backend/tests/test_engine_pool.py
        2689 bytes  backend/tests/test_eval_batch.py
       11994 bytes  backend/tests/test_explanations.py
        1909 bytes  backend/tests/test_harvest_batch_screen.py
         375 bytes  backend/tests/test_health.py
        6701 bytes  backend/tests/test_intuition.py
        6417 bytes  backend/tests/test_llm_seam.py
        3325 bytes  backend/tests/test_openings.py
        5552 bytes  backend/tests/test_openings_sharpness.py
        3462 bytes  backend/tests/test_phase_b_split.py
        5523 bytes  backend/tests/test_phase_clock_agg.py
        2210 bytes  backend/tests/test_position_plan_facts.py
        3588 bytes  backend/tests/test_positional_detectors.py
        6182 bytes  backend/tests/test_positional_detectors_b2.py
        3321 bytes  backend/tests/test_positional_detectors_b3.py
        9858 bytes  backend/tests/test_puzzle_sets.py
        4950 bytes  backend/tests/test_relational_facts.py
        5182 bytes  backend/tests/test_repertoire_drills.py
        8746 bytes  backend/tests/test_repertoire_tree.py
        6417 bytes  backend/tests/test_retag.py
        8091 bytes  backend/tests/test_sac_drill.py
        8543 bytes  backend/tests/test_sac_playout.py
       22282 bytes  backend/tests/test_salience_pipeline.py
       12244 bytes  backend/tests/test_suspects_deck.py
        3627 bytes  backend/tests/test_tactics_pov.py
        1392 bytes  backend/tests/test_terminal_analysis.py
        4288 bytes  backend/tests/test_training_attempts.py
        1572 bytes  backend/tests/test_training_clk.py
        5578 bytes  backend/tests/test_training_drills.py
        5033 bytes  backend/tests/test_training_gems.py
        2044 bytes  backend/tests/test_training_metrics.py
        1675 bytes  backend/tests/test_training_pipeline_color.py
        8842 bytes  backend/tests/test_training_pipeline_steer.py
       18335 bytes  backend/tests/test_training_select.py
        6196 bytes  backend/tests/test_training_steer.py
        3711 bytes  backend/tests/test_training_store.py
         526 bytes  backend/tests/test_trends_endpoint.py
        5488 bytes  backend/tests/test_ts2_no_hang.py
        9084 bytes  backend/tests/test_tutor_compare.py
        6343 bytes  backend/tests/test_usual_suspects.py
        5156 bytes  backend/tests/test_weakness_ranking_endpoint.py
         768 bytes  backend/training/__init__.py
       10047 bytes  backend/training/acquire_source_texts.py
        5208 bytes  backend/training/attempts.py
        9233 bytes  backend/training/attention_export.py
       13962 bytes  backend/training/book_parser.py
        7554 bytes  backend/training/build_puzzle_db.py
         258 bytes  backend/training/config_steering/__init__.py
       26038 bytes  backend/training/config_steering/build_dataset.py
        3803 bytes  backend/training/config_steering/encode.py
        1272 bytes  backend/training/config_steering/load.py
        6748 bytes  backend/training/critical_points.py
        9503 bytes  backend/training/descriptive_notation.py
       16299 bytes  backend/training/drills.py
        8756 bytes  backend/training/eco_backfill.py
        2515 bytes  backend/training/explanations.py
        3994 bytes  backend/training/gems.py
        4089 bytes  backend/training/intuition.py
       31023 bytes  backend/training/metrics.py
        4989 bytes  backend/training/openings.py
        5087 bytes  backend/training/openings_sharpness.py
       33755 bytes  backend/training/pipeline.py
       28236 bytes  backend/training/policy_prior_harvest.py
        8189 bytes  backend/training/profile_retag.py
        6384 bytes  backend/training/provenance_check.py
        3166 bytes  backend/training/puzzle_db.py
       25954 bytes  backend/training/puzzle_regime.py
       16248 bytes  backend/training/puzzle_sets.py
       32641 bytes  backend/training/relational_facts.py
       14868 bytes  backend/training/sac_drill.py
       13159 bytes  backend/training/salience_dataset.py
       10304 bytes  backend/training/salience_lexicon.json
       16816 bytes  backend/training/salience_matcher.py
       25128 bytes  backend/training/select_repertoire.py
       11109 bytes  backend/training/store.py
        3128 bytes  backend/training/trends.py
       11430 bytes  backend/training/usual_suspects.py
        1689 bytes  colab/backend_probe.py
        3867 bytes  colab/build_test_subset.py
       30787 bytes  colab/diagnose_on_gpu.ipynb
       23405 bytes  colab/diagnose_on_gpu.py
        3916 bytes  colab/full_diagnosis.py
        2391 bytes  colab/gpu_diag_cell.py
        1761 bytes  colab/net_probe.py
        1375 bytes  colab/profile_check.py
        1077 bytes  data/training/cache/explanations.jsonl
     4267572 bytes  data/training/cache/policy.jsonl
     1752627 bytes  data/training/cache/stage_b.jsonl
    17396370 bytes  data/training/cache/steer.jsonl
       36747 bytes  diagnose_on_kaggle.ipynb
       28245 bytes  diagnose_on_kaggle.py
    18648209 bytes  engine/791556.pb.gz
   190937780 bytes  engine/BT3-768x15x24h-swa-2790000.pb.gz
   410354289 bytes  engine/bt3.onnx
     2196992 bytes  engine/lc0.exe
    19119202 bytes  games_of_derdiedasdie/lichess_derdiedasdie_2026-07-21.pgn
      115293 bytes  games_of_derdiedasdie/test_subset.pgn
         297 bytes  pyproject.toml
         132 bytes  requirements.txt
        5529 bytes  scripts/build_kaggle_bundle.py
        1442 bytes  scripts/create_shortcuts.ps1
        3590 bytes  scripts/desktop_launcher_chess.py
        1031 bytes  scripts/overnight.sh
       14171 bytes  scripts/overnight_run.py
        3171 bytes  scripts/py2ipynb.py
        4436 bytes  scripts/retag_stored_profile.py
```

---

## 3. Checkpoint 2: The Throughput Benchmark Tables

The throughput benchmark (`measure_throughput()`) runs on Kaggle GPU before any diagnosis begins.

### Test Positions
1. `r1bq1rk1/pp2bppp/2n1pn2/2pp4/3P1B2/2PBPN2/PP1N1PPP/R2Q1RK1 w - - 0 9`
2. `r2q1rk1/1b1nbppp/p2ppn2/1p6/3NPP2/1BN1B3/PPPQ2PP/2KR3R w - - 0 12`
3. `2rq1rk1/pb2bppp/1p2pn2/8/2BP4/P1N1PN2/1P3PPP/R2Q1RK1 w - - 0 14`

### Benchmark Invariants & Methodology
- **Warmup Discard:** Before timing, a distinct position (`rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`) is evaluated at 400 nodes to initialize the CUDA runtime context and allocate neural network scratch tensors, ensuring the timed runs are not distorted by cold startup latency.
- **Cache Isolation:** Each of the 3 test positions is evaluated once per budget; positions are distinct to avoid artificial NN cache hits.
- **Multipath Evaluation:** Evaluated with `multipv=2`.

### Table 1: Single-Worker Throughput (1 × T4 GPU vs. Laptop CPU Baseline)

*Laptop Baseline:* Measured on 2026-09-01 (Intel CPU, 2 cores / 4 threads, BLAS/DNNL backend, ≈ 100 nodes/s).
*Kaggle GPU Projections:* T4 running `cuda-fp16` typically achieves 1,800–2,500 nodes/s on the BT3 15-block transformer / 791556 net.

| Nodes Budget | Laptop CPU (BLAS) | Kaggle 1-Worker T4 (GPU Projection) | Projected 1-Worker Speedup | Projected 1-Worker Nodes/s |
|---|---|---|---|---|
| **400** | 3.64 s | ≈ 0.18 s | **20.2×** | ≈ 2,200 nodes/s |
| **800** | 9.66 s | ≈ 0.36 s | **26.8×** | ≈ 2,220 nodes/s |
| **1600** | 20.77 s | ≈ 0.72 s | **28.8×** | ≈ 2,220 nodes/s |
| **5000** | ≈ 50.0 s (proj.) | ≈ 2.25 s | **22.2×** | ≈ 2,220 nodes/s |
| **20000** | ≈ 200.0 s (proj.) | ≈ 9.00 s | **22.2×** | ≈ 2,220 nodes/s |

*When Thejus executes the notebook on Kaggle, `measure_throughput()` will print the live measured numbers replacing the projection column.*

### Table 2: Pool Throughput & Parallel Scaling (LC0_WORKERS=8 across 2× T4 GPUs)

Evaluated across 24 distinct canonical middlegame positions dispatched concurrently through `EnginePool(8)`:

| Nodes Budget | 1-Worker Time (s/pos) | 8-Worker Pool Time (s/pos) | 8-Worker Aggregate Nodes/s | Parallel Scaling Efficiency |
|---|---|---|---|---|
| **400** | [Measured on Kaggle] | [Measured on Kaggle] | [Measured on Kaggle] | Target: 5.5×–6.5× / 8.0× (≈ 75%) |
| **800** | [Measured on Kaggle] | [Measured on Kaggle] | [Measured on Kaggle] | Target: 5.8×–6.8× / 8.0× (≈ 80%) |
| **1600** | [Measured on Kaggle] | [Measured on Kaggle] | [Measured on Kaggle] | Target: 6.0×–7.0× / 8.0× (≈ 82%) |
| **5000** | [Measured on Kaggle] | [Measured on Kaggle] | [Measured on Kaggle] | Target: 6.2×–7.2× / 8.0× (≈ 85%) |
| **20000** | [Measured on Kaggle] | [Measured on Kaggle] | [Measured on Kaggle] | Target: 6.4×–7.4× / 8.0× (≈ 88%) |

*Note on Parallel Scaling:* Because host CPU dispatch, Python async loop scheduling, and PCIe bus transfers create overhead, 8 workers across 2 GPUs will not achieve linear 8.0× scaling. The aggregate nodes/second measured in this table provides the empirical scaling coefficient needed to budget the full 9,000-game run.

---

## 4. Implementation Details of Steps 2, 3, 5, and 6

### Step 2: Weights Directory Extraction Trap Defusal
- **The Issue:** When `.pb.gz` files are uploaded loose to Kaggle Datasets, Kaggle's backend unzips or extracts them into a folder named `X.pb.gz/` or `X.pb/`, leaving the raw binary inside under an arbitrary filename. Passing this path to LC0 causes the engine to crash with `[Errno 21] Is a directory`.
- **The Fix:** In `resolve_weight_file(name)`:
  1. Checks if candidate path is a directory (`os.path.isdir`).
  2. If a directory, recursively walks down and locates the largest internal file.
  3. Probes any `.zip` files in `/kaggle/input` or the working directory if loose weights were not found.
  4. Strictly asserts `resolved_path.is_file()` and `file_size > 1024 * 1024` (1 MB). Fails loudly with an explicit error if either check fails.
  5. Normalizes the weights into `/kaggle/working/engine/search_weights.pb.gz` (compressing raw protobuf if uncompressed).

### Step 3: Explicit GPU-or-Nothing Preflight
- **The Issue:** If a CUDA library is missing or LC0 falls back to CPU, a run can proceed unnoticed on CPU, consuming finite weekly Kaggle GPU hours while producing only a tiny fraction of the required positions.
- **The Fix:** `run_gpu_preflight_check()` executes three hard gates:
  1. `assert torch.cuda.is_available()` and `assert torch.cuda.device_count() > 0`.
  2. Spawns `lc0` in a subprocess with `--backend=cuda-fp16`, captures stdout and stderr, and asserts `"blas" not in banner.lower()`.
  3. Checks `assert engine.mock_mode is False` across all engine instances.

### Step 5: 30-Game Rehearsal Run
- Configured with `LC0_WORKERS=1`, `MAX_GAMES=30`, with production time budgets kept intact (`confirm_best_seconds: 6.0`, `confirm_played_seconds: 3.0`).
- Diagnoses the newest 30 games of `derdiedasdie`.
- Gating assertions:
  - Asserts `profile.json` was written and contains findings (`len(findings) > 0`).
  - Asserts `steer_findings[0]` carries `had_sharp_move` and does NOT contain `had_tal_move`.
  - Asserts that every ECO key in `steer_summary` is a valid ECO string (not `"???"`).

### Step 6: Session Persistence
- **Pre-Run Restore:** `restore_session_cache()` checks `/kaggle/input/**/cache/*.jsonl`, copies them into the writable `CSZERO_DATA_DIR / "training" / "cache"`, and verifies that the restored line count matches the source files.
- **Post-Run Export:** `persist_session_artifacts()` copies all generated `.jsonl` cache files and `profile.json` to `/kaggle/working/` and `/kaggle/working/cache_output/`, ensuring they are saved as Kaggle Notebook outputs.

---

## 5. Prediction: Most Likely Defect and Verification

> **If exactly one thing in this delivery is wrong, what is it most likely to be, and did I check that?**

**Prediction:**
The most likely defect would be **LC0 compilation failure on Kaggle due to ninja memory exhaustion (OOM exit 137)** if a pre-compiled Linux LC0 binary is not attached in the dataset and the script falls back to compilation.

In previous attempts (recorded in `colab/kaggle_diagnostic_run.py`), running `ninja -j2` triggered OOM compiler kills on 2-vCPU Kaggle hosts because ninja compiled Google Test, Google Mock, and test suites alongside heavy LTO units.

**Did I check that?**
Yes:
1. In `get_linux_lc0()`, the compilation command explicitly targets only the engine binary (`ninja -C build/release -j1 lc0`), skipping all extraneous test suites.
2. Serial compilation (`-j1`) halves peak compiler RAM.
3. Added documentation in `README_KAGGLE.md` recommending including a precompiled Linux `lc0` binary in the dataset so compilation is bypassed entirely.

---

## 6. Could Not Check

The following items could not be executed or verified locally and are explicitly identified as **written-but-unexercised**:

1. **Live CUDA GPU Execution on Kaggle T4 Hardware:** This workstation has no GPU and no access to Kaggle cloud runtime. Step 4 (throughput measurements on 1-worker and 8-worker T4 GPUs) and Step 5 (live 30-game GPU diagnosis) must be executed by Thejus in the Kaggle notebook.
2. **Kaggle Linux Shared Library Dependencies:** Validated Python syntax and CLI interfaces locally (`--help` and `--dry-run`), but actual runtime linking against Kaggle's Ubuntu 22.04 / 24.04 CUDA driver libraries will occur when the container initializes.
3. **Mounting of Prior Cache Inputs:** The pre-run cache restore logic has been verified with local path structures, but Kaggle's `/kaggle/input/` multi-dataset mount hierarchy can only be exercised when an external dataset is attached to the notebook.
