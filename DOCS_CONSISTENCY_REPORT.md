# Documentation Consistency & Reconciliation Report

> **Scope:** Cross-check surviving and archived documentation for contradictions, stale facts, and duplicate guidance.
> **Date:** 2026-07-25  
> **Rule Enforced:** Recommendations are reported for Leader review — no documentation content was modified.

---

## 1. Documentation Contradictions & Stale Facts

| Claim / Subject | Document & Line | Conflicting Document, Stale Claim, or Current Truth | Recommended Correction (Describe, Don't Apply) |
|:---|:---|:---|:---|
| **Kaggle Host RAM** | `archive/GEMINI_REVIEW_REQUEST.md:32,86`<br>`KAGGLE_RUN_REVIEW.md:5,17,60,96`<br>`KAGGLE_BEST_PRACTICES.md:252,259,264`<br>`LEADER_BIBLE.md:120,141` | Live readout on Kaggle T4×2 instances showed **~30 GiB (29.0 GB)** host RAM. `KAGGLE_BEST_PRACTICES.md:32` lists `~13 GB to 29 GB (NEEDS-VERIFY)`, but lines 252, 259, and 264 assert 13 GB as a hard system ceiling (`13 GB Host RAM Cap`). | Update `KAGGLE_BEST_PRACTICES.md` and `LEADER_BIBLE.md` to state that Kaggle T4×2 host instances provide ~30 GiB RAM. Retain recommendations to cap `LC0_RAM_LIMIT_MB` (e.g. 2048 MB per worker) for multi-worker concurrency safety without mischaracterizing 13 GB as physical host memory. |
| **`.zip` Prevents `.gz` Mangling** | `KAGGLE_BEST_PRACTICES.md:20,212-213` | Empirical Kaggle run (2026-07-25) proved that a `.pb.gz` file nested inside a `.zip` dataset archive was **still decompressed into a directory** (`.pb/`) by Kaggle's backend ingestion pipeline (as documented in `GEMINI_REPO_CLEANUP_TASK.md:45-46` and handled by `_find_weights()` in `colab/kaggle_diagnostic_run.py:166-167`). | Amend `KAGGLE_BEST_PRACTICES.md` §5 to remove the claim that `.zip` guarantees preservation of `.gz` files. Document dual-extension fallback handling (`.pb` and `.pb.gz`) in `_find_weights()` as the required mitigation. |
| **Current Baseline Findings** | `LEADER_BIBLE.md:87,128-129` | `LEADER_BIBLE.md` cites `28 findings / 22 steer_findings` (legacy 3-game subset) and `339 findings / 267 steer_findings` (truncated A100 run) as baselines. The first clean full diagnostic run established the official baseline: **213 findings / 263 steer_findings** (n=1, 30 games, 880 moves, ~9352s, 2026-07-25). | Update `LEADER_BIBLE.md` §5 to explicitly mark **213 findings / 263 steer_findings** (30 games) as the clean baseline, explicitly noting that 28/22 was a 3-game test subset and 339/267 was a budget-truncated run. |
| **Diagnosis Net vs Arrows Net** | `archive/GEMINI_COLAB_GPU_ITERATE_TASK.md:28,55`<br>`archive/GEMINI_TASKS.md:48,144,249`<br>`archive/PHASE2_REDO_TASKS.md:40,112`<br>`archive/implementation_plan.md:29` | `LEADER_BIBLE.md` §4 defines the official division: `BT3-768x15x24h` (`BT3-768x15x24h-swa-2790000.pb.gz`) is the **diagnosis search net**, while `791556.pb.gz` is the **live app policy arrows net**. Legacy task specs cite `791556.pb.gz` as the primary search/diagnosis weights file. | Keep legacy task docs archived. If referenced in active docs, ensure the distinction is preserved: `BT3` for deep diagnostic evaluation and attention saliency; `791556.pb.gz` for fast frontend policy arrow generation. |
| **Worker Engine Memory Defaults** | `KAGGLE_RUN_REVIEW.md:17,60`<br>`QUESTIONS_FOR_LEADER.md:1` | `KAGGLE_RUN_REVIEW.md` recommends `LC0_RAM_LIMIT_MB=2048`, whereas `QUESTIONS_FOR_LEADER.md` reverts engine defaults to `RamLimitMb=8192` for standalone desktop operations. | Clarify in `HOW_TO_RUN.md` and `KAGGLE_BEST_PRACTICES.md` that desktop local runs default to `8192 MB` (8 GB node cache), while Kaggle multi-worker diagnostic runs must set `LC0_RAM_LIMIT_MB=2048` to avoid host OOM when multiple engines run concurrently. |

---

## 2. Duplicate & Overlapping Guidance Across Runbooks

The surviving user-facing documentation (`HOW_TO_RUN.md`, `HOW_TO_USE.md`, and `USING_YOUR_PROFILE.md`) contains repetitive instructions that risk drift:

| Subject / Section | `HOW_TO_RUN.md` | `HOW_TO_USE.md` | `USING_YOUR_PROFILE.md` | Recommended Consolidation |
|:---|:---|:---|:---|:---|
| **Backend Startup Command** | Lines 34: `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn backend.app:app --reload` | Section 1 cross-references `HOW_TO_RUN.md` | Line 15: `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn backend.app:app` | Make `HOW_TO_RUN.md` §1 the sole authoritative source for the backend startup command. Remove command string in `USING_YOUR_PROFILE.md` and replace with hyperlink to `HOW_TO_RUN.md` §1. |
| **Frontend Startup Command** | Lines 49–53: `cd frontend && npm install && npm run dev` | Section 1 cross-references `HOW_TO_RUN.md` | Line 17: `cd frontend && npm run dev` | Remove redundant command snippet in `USING_YOUR_PROFILE.md` and hyperlink to `HOW_TO_RUN.md` §2. |
| **`data/training/` File Schema** | N/A | Lines 177–185: lists `profile.json`, `repertoire.json`, `drills/`, `jobs/`, `cache/` | Lines 6–12: lists `profile.json`, `repertoire.json`, `profiles/`, `cache/` | Keep structural file manifest in `HOW_TO_USE.md` §5. Streamline `USING_YOUR_PROFILE.md` §1 to focus only on replacing files via `training.zip`. |
| **Weakness Profile Interpretation** | N/A | Lines 69–96: details blind rates, attention blindness, top openings, top motifs | Lines 18–25 & 40–45: details multi-dimension ranking (middlegame vs opening/endgame) | Maintain general feature explanations in `HOW_TO_USE.md` §2.2. Keep `USING_YOUR_PROFILE.md` focused on interpreting sample dataset outputs. |
