# Repository Cleanup & Archival Plan

> **Scope:** Repo root clutter audit and safe, reversible archival via `git mv`.
> **Date:** 2026-07-25  
> **Status:** Archival executed & staged for Leader review. No files deleted.

---

## 1. Root File Classification & Audit Table

The table below lists every root-level file, task-doc, report, scratch script, binary artifact, and configuration file evaluated during this cleanup pass.

| File | Classification | One-Line Rationale & Evidence |
|:---|:---:|:---|
| `.env` | **KEEP** | Local environment configuration file containing API keys; gitignored. |
| `.gitattributes` | **KEEP** | Mandatory project configuration forcing LF line endings for shell scripts. |
| `.gitignore` | **KEEP** | Mandatory project git ignore rules. |
| `ARCHITECTURE.md` | **KEEP** | Mandatory architecture documentation (Phase 0 realignments). |
| `ARROW_WEIGHTS_TASKS.md` | **ARCHIVE** | Completed Phase 0/1 spec (`04786e9`: policy-arrow rendering & opacity scaling). |
| `CALCULATION_GLOW_TASKS.md` | **ARCHIVE** | Completed spec (`5fd19b3`: calculation glow feature & runbook specifications). |
| `CLAUDE_TRAINING_TASKS.md` | **ARCHIVE** | Completed worker task spec (`0789f4a`: Epoch II Tactical Steering & TS1–TS5 worker specs). |
| `CODE_AUDIT_REPORT.md` | **ARCHIVE** | Completed audit report (`2886278`: F1–F8 findings; all fixes verified & landed). |
| `cszero_kaggle_data.zip` | **DELETE-CANDIDATE** | Untracked 515 MB local archive built 2026-07-25 for Kaggle deployment. |
| `DEBIAN_SYNC_2026-07-20.md` | **ARCHIVE** | Completed one-off sync guide (`fc3ed41`: Debian sync & Linux runner setup for 2026-07-20). |
| `DEPLOY_DEBIAN.md` | **ARCHIVE** | Completed/superseded runbook (`5fd19b3`: Debian deploy guide; core runbook is `HOW_TO_RUN.md`). |
| `discovery.py` | **ARCHIVE** | Seed throwaway python script (`8309032`: 2026-07-16 dev scratch). |
| `frontend/discover.mjs` | **ARCHIVE** | Seed throwaway dev scratch script (`8309032`: 2026-07-16 frontend dev scratch). |
| `frontend/discover2.mjs` | **ARCHIVE** | Seed throwaway dev scratch script (`8309032`: 2026-07-16 frontend dev scratch). |
| `frontend/discover3.mjs` | **ARCHIVE** | Seed throwaway dev scratch script (`8309032`: 2026-07-16 frontend dev scratch). |
| `frontend/discover_pgn.mjs` | **ARCHIVE** | Seed throwaway dev scratch script (`8309032`: 2026-07-16 frontend dev scratch). |
| `GEMINI_CODE_AUDIT_TASK.md` | **ARCHIVE** | Completed order spec (`0945e09`: Gemini deep read-only code audit). |
| `GEMINI_COLAB_GPU_ITERATE_TASK.md` | **ARCHIVE** | Completed task spec (`ba05036`: Colab GPU iteration & cookbook §4d). |
| `GEMINI_HANDOFF.md` | **ARCHIVE** | Superseded handoff document (`2c259a1`: 2026-07-23 Gemini handoff). |
| `GEMINI_HANG_FIX.md` | **ARCHIVE** | Completed TDD task spec (`8f97c0b`: 1000-game TS2 hang-repro test). |
| `GEMINI_KAGGLE_REFERENCE_PROMPT.md` | **KEEP** | Active Kaggle-campaign reference prompt (Mandatory hard rule). |
| `GEMINI_LOCAL_BATCHED_SALIENCY.md` | **ARCHIVE** | Completed task spec (`2b96bae`: redefined batched-saliency task for local Gemini). |
| `GEMINI_LOCAL_GPU_EVAL_BATCH.md` | **ARCHIVE** | Completed task spec (`445336f`: NeuralVision & batched eval optimization #2). |
| `GEMINI_LOG_TRIAGE_TEMPLATE.md` | **KEEP** | Active Kaggle-campaign log triage template (Mandatory hard rule). |
| `GEMINI_MULTIDIM_RANKING_UI_TASK.md` | **ARCHIVE** | Completed task spec (`3f1cd76`: multi-dimension ranking UI in Weakness Profile). |
| `GEMINI_PHASE_CLOCK_AGG_TASK.md` | **ARCHIVE** | Completed task spec (`ff228b0`: phase & clock aggregation module). |
| `GEMINI_PREDEPLOY_AUDIT_TASK.md` | **ARCHIVE** | Completed task spec (`b045c2f`: pre-deploy audit for node-limit path & corpus reliability). |
| `GEMINI_R3_EXPLANATIONS_TASK.md` | **ARCHIVE** | Completed task spec (`beb9292`: LLM coach explanations for repertoire nodes). |
| `GEMINI_R4_QA_TASK.md` | **ARCHIVE** | Completed task spec (`c29f6a8`: frontend test harness & whole-UI QA sweep). |
| `GEMINI_REPO_CLEANUP_TASK.md` | **KEEP** | Active task spec for this repo cleanup pass (Mandatory hard rule). |
| `GEMINI_REVIEW_REQUEST.md` | **ARCHIVE** | Completed review request (`84cf5a5`: Kaggle diagnostic .gz mangling & F-01..F-05 fixes). |
| `GEMINI_REVIEW_REQUEST_2.md` | **ARCHIVE** | Completed review request (`7371b7f`: second pre-run audit for 2-worker GPU split). |
| `GEMINI_T4_UI_TASK.md` | **ARCHIVE** | Completed task spec (`1258ead`: Weakness Profile ranking endpoint & UI). |
| `GEMINI_TASKS.md` | **ARCHIVE** | Completed task spec (`8309032`: interactive board & move-list notation panel). |
| `GEMINI_TERMINAL_REVIEW.md` | **ARCHIVE** | Completed review request (`f49a607`: terminal-position/a1a1 crash fix review). |
| `GEMINI_TRAINING_TASKS.md` | **ARCHIVE** | Completed worker task spec (`0789f4a`: Epoch II Tactical Steering & worker specs). |
| `GEMINI_UI_BUGHUNT_TASK.md` | **KEEP** | Active Kaggle-campaign task spec (Mandatory hard rule). |
| `GEMINI_UI_PERF_TASK.md` | **KEEP** | Active Kaggle-campaign task spec (Mandatory hard rule). |
| `GEMINI_VISION_PANEL_PROMPT.md` | **ARCHIVE** | Completed prompt spec (`5a06ccb`: vision panel prompt & lc0 binary caching). |
| `HOW_TO_RUN.md` | **KEEP** | Authoritative system runbook (Mandatory hard rule). |
| `HOW_TO_USE.md` | **KEEP** | Authoritative user manual (Mandatory hard rule). |
| `implementation_plan.md` | **ARCHIVE** | Completed initial implementation plan (`8309032`: 2026-07-16 project kickoff plan). |
| `INTERACTIVE_BOARD_TASKS.md` | **ARCHIVE** | Completed feature spec (`8309032`: interactive board, neural overlays & move-list). |
| `KAGGLE_BEST_PRACTICES.md` | **KEEP** | Active Kaggle-campaign best practices guide (Mandatory hard rule). |
| `KAGGLE_RUN_REVIEW.md` | **ARCHIVE** | Completed review report (`84cf5a5`: initial Kaggle run audit F-01..F-05). |
| `KAGGLE_RUN_REVIEW_2.md` | **ARCHIVE** | Completed review report (`7371b7f`: 2-worker GPU-split pre-run audit). |
| `kaggle_files.zip` | **DELETE-CANDIDATE** | Untracked 509 MB local archive built for Kaggle deployment. |
| `LEADER_BIBLE.md` | **KEEP** | Central state-of-the-union handbook for agent lead (Mandatory hard rule). |
| `MISSION_FULL_A100.md` | **ARCHIVE** | Completed mission spec (`39c463c`: parallel lc0 pool plan for full GPU usage). |
| `MOVELIST_TASKS.md` | **ARCHIVE** | Completed task spec (`8309032`: live move-list notation panel). |
| `overnight.bat` | **ARCHIVE** | Seed throwaway batch script (`8433de2`: 2026-07-20 runner script). |
| `PHASE2_REDO_TASKS.md` | **ARCHIVE** | Completed task spec (`8309032`: Phase 2 redo tasks). |
| `PHASE2_TRANSFORMER_TASKS.md` | **ARCHIVE** | Completed task spec (`8309032`: Phase 2 transformer integration). |
| `POST_VALIDATION_BACKLOG.md` | **KEEP** | Active project backlog for future enhancements (Mandatory hard rule). |
| `PREDEPLOY_AUDIT_REPORT.md` | **ARCHIVE** | Completed audit report (`4cad9e7`: pre-deploy audit report for node-limit path). |
| `pyproject.toml` | **KEEP** | Mandatory project configuration file (Mandatory hard rule). |
| `python311.exe` | **DELETE-CANDIDATE** | Untracked 26 MB standalone Python executable binary in root. |
| `QUESTIONS_FOR_LEADER.md` | **KEEP** | Active questions log for project leader (Mandatory hard rule). |
| `README.md` | **KEEP** | Project overview and quickstart (Mandatory hard rule). |
| `REALIGNMENT_REPORT.md` | **ARCHIVE** | Completed report (`120cc6f`: interactive free-play board realignment). |
| `REPERTOIRE_TUTOR_EPOCH.md` | **ARCHIVE** | Completed plan (`5784d42`: Epoch III Repertoire Trainer & Tutor ranking). |
| `sample_games_to_analyze/` | **ARCHIVE** | Seed throwaway directory (`lichess_derdiedasdie_2026-07-14.imported.pgn` is 0 B). |
| `scratch_analyze.json` | **ARCHIVE** | Seed throwaway JSON file (`8309032`: 2026-07-16 dev scratch). |
| `TERMINAL_REVIEW_NOTES.md` | **ARCHIVE** | Completed review notes (`61aaef8`: terminal-position/a1a1 crash fix). |
| `test_api.py` | **ARCHIVE** | Seed throwaway test script (`8309032`: 2026-07-16 dev scratch). |
| `test_fallback.py` | **ARCHIVE** | Seed throwaway test script (`8309032`: 2026-07-16 dev scratch). |
| `test_lc0_verbose.py` | **ARCHIVE** | Seed throwaway test script (`8309032`: 2026-07-16 dev scratch). |
| `test_lc0_verbose2.py` | **ARCHIVE** | Seed throwaway test script (`8309032`: 2026-07-16 dev scratch). |
| `test_policy.py` | **ARCHIVE** | Seed throwaway test script (`8309032`: 2026-07-16 dev scratch). |
| `THINKING_TIME_TASKS.md` | **ARCHIVE** | Completed feature spec (`5fd19b3`: thinking time feature tasks). |
| `tmp.json` | **ARCHIVE** | Seed throwaway 0-byte JSON file (`8309032`: 2026-07-16 dev scratch). |
| `TRAINING_ROADMAP.md` | **ARCHIVE** | Superseded roadmap (`0789f4a`: Epoch II roadmap). |
| `TRAINING_SYSTEM_PLAN.md` | **ARCHIVE** | Superseded foundation plan (`a8d6fb6`: training system plan). |
| `USING_YOUR_PROFILE.md` | **KEEP** | Active user guide for reading diagnosis profiles in the app. |
| `uvicorn.log` | **DELETE-CANDIDATE** | Untracked 431 B dev server log output file. |
| `VISION_PANEL_DISCUSSION.md` | **ARCHIVE** | Completed discussion document (simulated vision panel notes). |
| `WORKER_AGENT_COOKBOOK.md` | **KEEP** | Active worker agent prompt & protocol cookbook (Mandatory hard rule). |
| `WORKLOG_TRAINING.md` | **KEEP** | Active project worklog tracking training system progress. |

---

## 2. Archived This Pass (`git mv` executed)

The following 54 items were safely moved into `archive/` via `git mv`. All movements are currently staged in git and fully reversible.

```
R  ARROW_WEIGHTS_TASKS.md -> archive/ARROW_WEIGHTS_TASKS.md
R  CALCULATION_GLOW_TASKS.md -> archive/CALCULATION_GLOW_TASKS.md
R  CLAUDE_TRAINING_TASKS.md -> archive/CLAUDE_TRAINING_TASKS.md
R  CODE_AUDIT_REPORT.md -> archive/CODE_AUDIT_REPORT.md
R  DEBIAN_SYNC_2026-07-20.md -> archive/DEBIAN_SYNC_2026-07-20.md
R  DEPLOY_DEBIAN.md -> archive/DEPLOY_DEBIAN.md
R  GEMINI_CODE_AUDIT_TASK.md -> archive/GEMINI_CODE_AUDIT_TASK.md
R  GEMINI_COLAB_GPU_ITERATE_TASK.md -> archive/GEMINI_COLAB_GPU_ITERATE_TASK.md
R  GEMINI_HANDOFF.md -> archive/GEMINI_HANDOFF.md
R  GEMINI_HANG_FIX.md -> archive/GEMINI_HANG_FIX.md
R  GEMINI_LOCAL_BATCHED_SALIENCY.md -> archive/GEMINI_LOCAL_BATCHED_SALIENCY.md
R  GEMINI_LOCAL_GPU_EVAL_BATCH.md -> archive/GEMINI_LOCAL_GPU_EVAL_BATCH.md
R  GEMINI_MULTIDIM_RANKING_UI_TASK.md -> archive/GEMINI_MULTIDIM_RANKING_UI_TASK.md
R  GEMINI_PHASE_CLOCK_AGG_TASK.md -> archive/GEMINI_PHASE_CLOCK_AGG_TASK.md
R  GEMINI_PREDEPLOY_AUDIT_TASK.md -> archive/GEMINI_PREDEPLOY_AUDIT_TASK.md
R  GEMINI_R3_EXPLANATIONS_TASK.md -> archive/GEMINI_R3_EXPLANATIONS_TASK.md
R  GEMINI_R4_QA_TASK.md -> archive/GEMINI_R4_QA_TASK.md
R  GEMINI_REVIEW_REQUEST.md -> archive/GEMINI_REVIEW_REQUEST.md
A  archive/GEMINI_REVIEW_REQUEST_2.md
R  GEMINI_T4_UI_TASK.md -> archive/GEMINI_T4_UI_TASK.md
R  GEMINI_TASKS.md -> archive/GEMINI_TASKS.md
R  GEMINI_TERMINAL_REVIEW.md -> archive/GEMINI_TERMINAL_REVIEW.md
R  GEMINI_TRAINING_TASKS.md -> archive/GEMINI_TRAINING_TASKS.md
R  GEMINI_VISION_PANEL_PROMPT.md -> archive/GEMINI_VISION_PANEL_PROMPT.md
R  INTERACTIVE_BOARD_TASKS.md -> archive/INTERACTIVE_BOARD_TASKS.md
R  KAGGLE_RUN_REVIEW.md -> archive/KAGGLE_RUN_REVIEW.md
A  archive/KAGGLE_RUN_REVIEW_2.md
R  MISSION_FULL_A100.md -> archive/MISSION_FULL_A100.md
R  MOVELIST_TASKS.md -> archive/MOVELIST_TASKS.md
R  PHASE2_REDO_TASKS.md -> archive/PHASE2_REDO_TASKS.md
R  PHASE2_TRANSFORMER_TASKS.md -> archive/PHASE2_TRANSFORMER_TASKS.md
R  PREDEPLOY_AUDIT_REPORT.md -> archive/PREDEPLOY_AUDIT_REPORT.md
R  REALIGNMENT_REPORT.md -> archive/REALIGNMENT_REPORT.md
R  REPERTOIRE_TUTOR_EPOCH.md -> archive/REPERTOIRE_TUTOR_EPOCH.md
R  TERMINAL_REVIEW_NOTES.md -> archive/TERMINAL_REVIEW_NOTES.md
R  THINKING_TIME_TASKS.md -> archive/THINKING_TIME_TASKS.md
R  TRAINING_ROADMAP.md -> archive/TRAINING_ROADMAP.md
R  TRAINING_SYSTEM_PLAN.md -> archive/TRAINING_SYSTEM_PLAN.md
A  archive/VISION_PANEL_DISCUSSION.md
R  discovery.py -> archive/discovery.py
R  frontend/discover.mjs -> archive/frontend/discover.mjs
R  frontend/discover2.mjs -> archive/frontend/discover2.mjs
R  frontend/discover3.mjs -> archive/frontend/discover3.mjs
R  frontend/discover_pgn.mjs -> archive/frontend/discover_pgn.mjs
R  implementation_plan.md -> archive/implementation_plan.md
R  overnight.bat -> archive/overnight.bat
R  sample_games_to_analyze/lichess_derdiedasdie_2026-07-14.imported.pgn -> archive/sample_games_to_analyze/lichess_derdiedasdie_2026-07-14.imported.pgn
R  scratch_analyze.json -> archive/scratch_analyze.json
R  test_api.py -> archive/test_api.py
R  test_fallback.py -> archive/test_fallback.py
R  test_lc0_verbose.py -> archive/test_lc0_verbose.py
R  test_lc0_verbose2.py -> archive/test_lc0_verbose2.py
R  test_policy.py -> archive/test_policy.py
R  tmp.json -> archive/tmp.json
```

---

## 3. Recommended Deletions (For Leader Approval)

The following untracked files are proposed for deletion (`rm`). No deletion command was run.

1. **`cszero_kaggle_data.zip`** (515 MB): Stale local dataset zip file. Can be re-generated via script if needed.
2. **`kaggle_files.zip`** (509 MB): Stale local dataset zip file. Can be re-generated via script if needed.
3. **`python311.exe`** (26 MB): Stale standalone installer binary in root.
4. **`uvicorn.log`** (431 B): Local dev server log file.
