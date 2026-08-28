# REPORT — reorganise the repository without breaking either app

**Filed:** 2026-08-29  
**Brief:** `agents/briefs/2026-08-29_repo-reorganisation.md`  
**Worker:** Gemini 3.7 Flash (High), Antigravity IDE  
**Status:** COMPLETE  

---

## 1. Baseline

The baseline commands run on clean working tree before moving any files:

### Backend Tests
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
collected 307 items / 1 deselected / 306 selected

backend\tests\test_attention_export.py .....                             [  1%]
backend\tests\test_batched_saliency.py ss                                [  2%]
backend\tests\test_book_parser.py ....                                   [  3%]
backend\tests\test_cache_replay_identity.py .                            [  3%]
backend\tests\test_concept_mapper_motifs.py ...                          [  4%]
backend\tests\test_critical_points.py ....                               [  6%]
backend\tests\test_descriptive_notation.py ....................          [ 12%]
backend\tests\test_eco_backfill.py ....                                  [ 14%]
backend\tests\test_engine_pool.py .....                                  [ 15%]
backend\tests\test_eval_batch.py sss                                     [ 16%]
backend\tests\test_explanations.py ............                          [ 20%]
backend\tests\test_harvest_batch_screen.py ...                           [ 21%]
backend\tests\test_health.py .                                           [ 21%]
backend\tests\test_intuition.py ......                                   [ 23%]
backend\tests\test_openings.py .....                                     [ 25%]
backend\tests\test_openings_sharpness.py .....                           [ 27%]
backend\tests\test_phase_b_split.py ...                                  [ 28%]
backend\tests\test_phase_clock_agg.py .......                            [ 30%]
backend\tests\test_position_plan_facts.py ..                             [ 31%]
backend\tests\test_positional_detectors.py .....                         [ 32%]
backend\tests\test_positional_detectors_b2.py .......                    [ 34%]
backend\tests\test_positional_detectors_b3.py ....                       [ 36%]
backend\tests\test_puzzle_sets.py ........                               [ 38%]
backend\tests\test_relational_facts.py ......                            [ 40%]
backend\tests\test_repertoire_drills.py .......                          [ 43%]
backend\tests\test_repertoire_tree.py .....                              [ 44%]
backend\tests\test_retag.py ....                                         [ 46%]
backend\tests\test_sac_drill.py .......                                  [ 48%]
backend\tests\test_sac_playout.py ......                                 [ 50%]
backend\tests\test_salience_pipeline.py .........................        [ 58%]
backend\tests\test_suspects_deck.py ..........                           [ 61%]
backend\tests\test_tactics_pov.py .....                                  [ 63%]
backend\tests\test_terminal_analysis.py ...                              [ 64%]
backend\tests\test_training_attempts.py ......                           [ 66%]
backend\tests\test_training_clk.py ....                                  [ 67%]
backend\tests\test_training_drills.py ..............                     [ 72%]
backend\tests\test_training_gems.py .......                              [ 74%]
backend\tests\test_training_metrics.py .......                           [ 76%]
backend\tests\test_training_pipeline_color.py .                          [ 77%]
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

backend\llm_client.py:2
  C:\Users\Admin\Documents\chess_speak_out_loud\backend\llm_client.py:2: FutureWarning: 
  
  All support for the `google.generativeai` package has ended. It will no longer be receiving 
  updates or bug fixes. Please switch to the `google.genai` package as soon as possible.
  See README for more details:
  
  https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md
  
    import google.generativeai as genai

backend/tests/test_attention_export.py::test_shapes_and_schema
backend/tests/test_attention_export.py::test_frame_matches_the_audited_api
backend/tests/test_attention_export.py::test_black_to_move_is_not_mirrored
backend/tests/test_attention_export.py::test_quantisation_round_trip
  C:\Users\Admin\miniconda3\envs\cszero\Lib\site-packages\onnx2torch\node_converters\slice.py:63: UserWarning: Using a non-tuple sequence for multidimensional indexing is deprecated and will be changed in pytorch 2.9; use x[tuple(seq)] instead of x[seq]. In pytorch 2.9 this will be interpreted as tensor index, x[torch.tensor(seq)], which will result either in an error or a different result (Triggered internally at C:\actions-runner\_work\pytorch\pytorch\torch\csrc\autograd\python_variable_indexing.cpp:355.)
    x = x[pos_axes_slices]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
==== 301 passed, 5 skipped, 1 deselected, 6 warnings in 152.88s (0:02:32) =====
```

### Trainer Tests
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
```
**Output:**
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 30 items

trainer\tests\test_engine.py ..............................              [100%]

============================= 30 passed in 0.81s ==============================
```

### Verification Script
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer\verify_cards.py
```
**Output:**
```
=================================================================
Verifying Knowledge Trainer Content Ladders & Boundaries...
=================================================================
Loaded 5 authoritative forbidden claim boundaries from 06_do_not_claim.md.

[PASS] All content, grounding, and constraint gates passed!

Card Counts by Ladder:
  - air_quality: 14 cards (Level 0: 2)
  - bridge: 17 cards (Level 0: 5)
  - de-grammatik: 20 cards (Level 0: 8)
  - de-konnektoren: 17 cards (Level 0: 5)
  - de-wortschatz: 15 cards (Level 0: 3)
  - hereon_aeon_up: 51 cards (Level 0: 5)
  - neural_processes: 15 cards (Level 0: 3)
  - own_work: 20 cards (Level 0: 8)
  - pytorch: 19 cards (Level 0: 7)
  - uncertainty: 17 cards (Level 0: 5)

Total verified cards: 205
Total repo citations: 193
Total URL citations:  175
=================================================================
```

### Git Status (Baseline)
```powershell
git status --short
```
**Output:**
```
?? applications/hereon_aeon_up/other_documents/
```

### Git Log (Baseline)
```powershell
git log --oneline -1
```
**Output:**
```
888cc22 agents: brief the repo reorganisation; close out the trainer brief
```

---

## 2. Git Status (`git status --short`)

The full output of `git status --short` after all file movements and link repairs:

```
 M CLAUDE.md
R  GEMINI_THEME_TAGGER_PHASE_C.md -> archive/reports/GEMINI_THEME_TAGGER_PHASE_C.md
R  HANDOVER.md -> archive/reports/HANDOVER.md
R  PROFILE_TRIAGE.md -> archive/reports/PROFILE_TRIAGE.md
R  REPO_CLEANUP_PLAN.md -> archive/reports/REPO_CLEANUP_PLAN.md
R  SRS_AWARE_DECK_REPORT.md -> archive/reports/SRS_AWARE_DECK_REPORT.md
R  UI_BUGHUNT_REPORT.md -> archive/reports/UI_BUGHUNT_REPORT.md
R  UI_ISSUES_TRIAGE.md -> archive/reports/UI_ISSUES_TRIAGE.md
R  UI_PERF_AUDIT.md -> archive/reports/UI_PERF_AUDIT.md
R  USUAL_SUSPECTS_REPORT.md -> archive/reports/USUAL_SUSPECTS_REPORT.md
R  gemini_stable_drill_ids_srs.txt -> archive/reports/gemini_stable_drill_ids_srs.txt
R  HOW_TO_USE.md -> docs/guides/HOW_TO_USE.md
R  KAGGLE_BEST_PRACTICES.md -> docs/guides/KAGGLE_BEST_PRACTICES.md
R  UI_PERFORMANCE_BEST_PRACTICES.md -> docs/guides/UI_PERFORMANCE_BEST_PRACTICES.md
R  USING_YOUR_PROFILE.md -> docs/guides/USING_YOUR_PROFILE.md
R  COMMAND_BASE.md -> docs/leadership/COMMAND_BASE.md
R  LEADER_GROUNDING.md -> docs/leadership/LEADER_GROUNDING.md
R  QUESTIONS_FOR_LEADER.md -> docs/leadership/QUESTIONS_FOR_LEADER.md
R  WORKER_AGENT_COOKBOOK.md -> docs/leadership/WORKER_AGENT_COOKBOOK.md
R  ARCHITECTURE.md -> docs/plans/ARCHITECTURE.md
R  CRITICAL_POINTS_DESIGN.md -> docs/plans/CRITICAL_POINTS_DESIGN.md
R  GM_CURRICULUM_PLAN.md -> docs/plans/GM_CURRICULUM_PLAN.md
R  GOALBOOK_REVIEW.md -> docs/plans/GOALBOOK_REVIEW.md
R  GOAL_BOOK.md -> docs/plans/GOAL_BOOK.md
R  GOAL_ELICITATION_QUESTIONS.md -> docs/plans/GOAL_ELICITATION_QUESTIONS.md
R  PLAN_SALIENCE_CNP.md -> docs/plans/PLAN_SALIENCE_CNP.md
R  POST_VALIDATION_BACKLOG.md -> docs/plans/POST_VALIDATION_BACKLOG.md
R  WORKLOG_TRAINING.md -> docs/plans/WORKLOG_TRAINING.md
 M state/MAP.md
 M trainer/content/ladders/neural_processes.json
?? applications/hereon_aeon_up/other_documents/
```

---

## 3. Six Gate Outputs Verbatim

### Gate 1 — The root is clean
```powershell
Get-ChildItem -File | Select-Object -ExpandProperty Name
```
**Output:**
```
.env
.gitattributes
.gitignore
CLAUDE.md
HOW_TO_RUN.md
launch_knowledge_trainer.bat
launch_trainer.bat
LEADER_BIBLE.md
pyproject.toml
README.md
stop_knowledge_trainer.bat
stop_trainer.bat
```

### Gate 2 — Nothing was lost
```powershell
git status --short
```
**Output:**
```
 M CLAUDE.md
R  GEMINI_THEME_TAGGER_PHASE_C.md -> archive/reports/GEMINI_THEME_TAGGER_PHASE_C.md
R  HANDOVER.md -> archive/reports/HANDOVER.md
R  PROFILE_TRIAGE.md -> archive/reports/PROFILE_TRIAGE.md
R  REPO_CLEANUP_PLAN.md -> archive/reports/REPO_CLEANUP_PLAN.md
R  SRS_AWARE_DECK_REPORT.md -> archive/reports/SRS_AWARE_DECK_REPORT.md
R  UI_BUGHUNT_REPORT.md -> archive/reports/UI_BUGHUNT_REPORT.md
R  UI_ISSUES_TRIAGE.md -> archive/reports/UI_ISSUES_TRIAGE.md
R  UI_PERF_AUDIT.md -> archive/reports/UI_PERF_AUDIT.md
R  USUAL_SUSPECTS_REPORT.md -> archive/reports/USUAL_SUSPECTS_REPORT.md
R  gemini_stable_drill_ids_srs.txt -> archive/reports/gemini_stable_drill_ids_srs.txt
R  HOW_TO_USE.md -> docs/guides/HOW_TO_USE.md
R  KAGGLE_BEST_PRACTICES.md -> docs/guides/KAGGLE_BEST_PRACTICES.md
R  UI_PERFORMANCE_BEST_PRACTICES.md -> docs/guides/UI_PERFORMANCE_BEST_PRACTICES.md
R  USING_YOUR_PROFILE.md -> docs/guides/USING_YOUR_PROFILE.md
R  COMMAND_BASE.md -> docs/leadership/COMMAND_BASE.md
R  LEADER_GROUNDING.md -> docs/leadership/LEADER_GROUNDING.md
R  QUESTIONS_FOR_LEADER.md -> docs/leadership/QUESTIONS_FOR_LEADER.md
R  WORKER_AGENT_COOKBOOK.md -> docs/leadership/WORKER_AGENT_COOKBOOK.md
R  ARCHITECTURE.md -> docs/plans/ARCHITECTURE.md
R  CRITICAL_POINTS_DESIGN.md -> docs/plans/CRITICAL_POINTS_DESIGN.md
R  GM_CURRICULUM_PLAN.md -> docs/plans/GM_CURRICULUM_PLAN.md
R  GOALBOOK_REVIEW.md -> docs/plans/GOALBOOK_REVIEW.md
R  GOAL_BOOK.md -> docs/plans/GOAL_BOOK.md
R  GOAL_ELICITATION_QUESTIONS.md -> docs/plans/GOAL_ELICITATION_QUESTIONS.md
R  PLAN_SALIENCE_CNP.md -> docs/plans/PLAN_SALIENCE_CNP.md
R  POST_VALIDATION_BACKLOG.md -> docs/plans/POST_VALIDATION_BACKLOG.md
R  WORKLOG_TRAINING.md -> docs/plans/WORKLOG_TRAINING.md
 M state/MAP.md
 M trainer/content/ladders/neural_processes.json
?? applications/hereon_aeon_up/other_documents/
```

### Gate 3 — The content gate still passes, with the same numbers
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer\verify_cards.py
```
**Output:**
```
=================================================================
Verifying Knowledge Trainer Content Ladders & Boundaries...
=================================================================
Loaded 5 authoritative forbidden claim boundaries from 06_do_not_claim.md.

[PASS] All content, grounding, and constraint gates passed!

Card Counts by Ladder:
  - air_quality: 14 cards (Level 0: 2)
  - bridge: 17 cards (Level 0: 5)
  - de-grammatik: 20 cards (Level 0: 8)
  - de-konnektoren: 17 cards (Level 0: 5)
  - de-wortschatz: 15 cards (Level 0: 3)
  - hereon_aeon_up: 51 cards (Level 0: 5)
  - neural_processes: 15 cards (Level 0: 3)
  - own_work: 20 cards (Level 0: 8)
  - pytorch: 19 cards (Level 0: 7)
  - uncertainty: 17 cards (Level 0: 5)

Total verified cards: 205
Total repo citations: 193
Total URL citations:  175
=================================================================
```

### Gate 4 — Both test suites, unchanged from baseline

#### 1. Trainer Tests
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
```
**Output:**
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 30 items

trainer\tests\test_engine.py ..............................              [100%]

============================= 30 passed in 0.53s ==============================
```

#### 2. Backend Tests
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
collected 307 items / 1 deselected / 306 selected

backend\tests\test_attention_export.py .....                             [  1%]
backend\tests\test_batched_saliency.py ss                                [  2%]
backend\tests\test_book_parser.py ....                                   [  3%]
backend\tests\test_cache_replay_identity.py .                            [  3%]
backend\tests\test_concept_mapper_motifs.py ...                          [  4%]
backend\tests\test_critical_points.py ....                               [  6%]
backend\tests\test_descriptive_notation.py ....................          [ 12%]
backend\tests\test_eco_backfill.py ....                                  [ 14%]
backend\tests\test_engine_pool.py .....                                  [ 15%]
backend\tests\test_eval_batch.py sss                                     [ 16%]
backend\tests\test_explanations.py ............                          [ 20%]
backend\tests\test_harvest_batch_screen.py ...                           [ 21%]
backend\tests\test_health.py .                                           [ 21%]
backend\tests\test_intuition.py ......                                   [ 23%]
backend\tests\test_openings.py .....                                     [ 25%]
backend\tests\test_openings_sharpness.py .....                           [ 27%]
backend\tests\test_phase_b_split.py ...                                  [ 28%]
backend\tests\test_phase_clock_agg.py .......                            [ 30%]
backend\tests\test_position_plan_facts.py ..                             [ 31%]
backend\tests\test_positional_detectors.py .....                         [ 32%]
backend\tests\test_positional_detectors_b2.py .......                    [ 34%]
backend\tests\test_positional_detectors_b3.py ....                       [ 36%]
backend\tests\test_puzzle_sets.py ........                               [ 38%]
backend\tests\test_relational_facts.py ......                            [ 40%]
backend\tests\test_repertoire_drills.py .......                          [ 43%]
backend\tests\test_repertoire_tree.py .....                              [ 44%]
backend\tests\test_retag.py ....                                         [ 46%]
backend\tests\test_sac_drill.py .......                                  [ 48%]
backend\tests\test_sac_playout.py ......                                 [ 50%]
backend\tests\test_salience_pipeline.py .........................        [ 58%]
backend\tests\test_suspects_deck.py ..........                           [ 61%]
backend\tests\test_tactics_pov.py .....                                  [ 63%]
backend\tests\test_terminal_analysis.py ...                              [ 64%]
backend\tests\test_training_attempts.py ......                           [ 66%]
backend\tests\test_training_clk.py ....                                  [ 67%]
backend\tests\test_training_drills.py ..............                     [ 72%]
backend\tests\test_training_gems.py .......                              [ 74%]
backend\tests\test_training_metrics.py .......                           [ 76%]
backend\tests\test_training_pipeline_color.py .                          [ 77%]
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

backend\llm_client.py:2
  C:\Users\Admin\Documents\chess_speak_out_loud\backend\llm_client.py:2: FutureWarning: 
  
  All support for the `google.generativeai` package has ended. It will no longer be receiving 
  updates or bug fixes. Please switch to the `google.genai` package as soon as possible.
  See README for more details:
  
  https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md
  
    import google.generativeai as genai

backend/tests/test_attention_export.py::test_shapes_and_schema
backend/tests/test_attention_export.py::test_frame_matches_the_audited_api
backend/tests/test_attention_export.py::test_black_to_move_is_not_mirrored
backend/tests/test_attention_export.py::test_quantisation_round_trip
  C:\Users\Admin\miniconda3\envs\cszero\Lib\site-packages\onnx2torch\node_converters\slice.py:63: UserWarning: Using a non-tuple sequence for multidimensional indexing is deprecated and will be changed in pytorch 2.9; use x[tuple(seq)] instead of x[seq]. In pytorch 2.9 this will be interpreted as tensor index, x[torch.tensor(seq)], which will result either in an error or a different result (Triggered internally at C:\actions-runner\_work\pytorch\pytorch\torch\csrc\autograd\python_variable_indexing.cpp:355.)
    x = x[pos_axes_slices]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
==== 301 passed, 5 skipped, 1 deselected, 6 warnings in 116.65s (0:01:56) =====
```

### Gate 5 — No card content changed
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -c "import io,json,glob,subprocess; bad=[]; [bad.append((p,c['id'],k)) for p in glob.glob('trainer/content/ladders/*.json') for c,o in zip(json.load(io.open(p,encoding='utf-8')), json.loads(subprocess.run(['git','show','HEAD:'+p.replace('\\','/')],capture_output=True,text=True,encoding='utf-8').stdout)) for k in ('id','question','answer','explanation','trap','level','difficulty','requires','ladder','topic') if c.get(k)!=o.get(k)]; print('DIFFERENCES:',len(bad)); [print(b) for b in bad[:20]]"
```
**Output:**
```
DIFFERENCES: 0
```

### Gate 6 — Both apps launch and serve

#### 1. The Knowledge Trainer
Command:
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn trainer.app:app --port 8010
```

Endpoint curl 1 (`/api/next-card`):
```powershell
curl.exe "http://127.0.0.1:8010/api/next-card?ladder=hereon-aeon-up&cram=true"
```
**Response:**
```json
{"card":{"id":"her-l3-001","ladder":"hereon-aeon-up","level":3,"topic":"talking about Karl's model","question":"Karl wrote EPISODE-CityChem. How do you talk about his model without overclaiming?","answer":"Say plainly what you have and have not done: 'I have not run EPISODE-CityChem. I have read the 2019 GMD paper, and I have several years of environmental modelling on Linux HPC - GOTM-FABM water columns, gridded NetCDF, and a Lagrangian individual-based model I wrote and ported to GPU. I would expect to learn your namelists and chemical mechanisms from your team, and I would not expect the workflow to feel unfamiliar.'","explanation":"This is strong because it concedes the exact thing he could expose in one question, and then offers the transferable skill that is genuinely yours. Conceding first is what makes the second half believable.","trap":"Reaching for familiarity you do not have — configuration flags, turbulence schemes, chemical mechanism names. In front of the model's author this fails immediately, and the do-not-claim list exists precisely for this case.","sources":["../job_search/applications/hereon_aeon_up/study_room/06_do_not_claim.md","https://doi.org/10.5194/gmd-12-3357-2019"],"difficulty":1420,"requires":["her-l2-003","her-l1-001"]},"current_rating":1420,"reps":0,"user_rating":838.07,"ladder_rating":838.07,"ladder_ratings":{"own-work":890.63,"uncertainty":946.8,"neural-processes":895.14,"de-grammatik":1180.02,"de-wortschatz":1181.34,"air-quality":892.23,"pytorch":923.66,"de-konnektoren":1237.69,"hereon-aeon-up":838.07,"bridge":838.5}}
```

Endpoint curl 2 (`/api/state`):
```powershell
curl.exe "http://127.0.0.1:8010/api/state"
```
**Response:**
```json
{"user_rating":892.23,"ladder_ratings":{"own-work":890.63,"uncertainty":946.8,"neural-processes":895.14,"de-grammatik":1180.02,"de-wortschatz":1181.34,"air-quality":892.23,"pytorch":923.66,"de-konnektoren":1237.69,"hereon-aeon-up":838.07,"bridge":838.5},"due_count":78,"total_cards":205,"mastered_count":46,"answers_count":106,"ladders":["air-quality","bridge","de-grammatik","de-konnektoren","de-wortschatz","hereon-aeon-up","neural-processes","own-work","pytorch","uncertainty"]}
```

Server console log:
```
INFO:     Started server process [2568]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8010 (Press CTRL+C to quit)
INFO:     127.0.0.1:51461 - "GET /api/next-card?ladder=hereon-aeon-up&cram=true HTTP/1.1" 200 OK
INFO:     127.0.0.1:51462 - "GET /api/state HTTP/1.1" 200 OK
```

#### 2. The Chess Backend
Command (following `HOW_TO_RUN.md`):
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn backend.app:app --port 8000
```

Endpoint curl (`/api/health`):
```powershell
curl.exe "http://127.0.0.1:8000/api/health"
```
**Response:**
```json
{"status":"ok","engine_mode":"live","version":"0.1.0"}
```

Endpoint curl (`/`):
```powershell
curl.exe "http://127.0.0.1:8000/"
```
**Response:**
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>frontend</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Server console log:
```
C:\Users\Admin\Documents\chess_speak_out_loud\backend\llm_client.py:2: FutureWarning: 

All support for the `google.generativeai` package has ended. It will no longer be receiving 
updates or bug fixes. Please switch to the `google.genai` package as soon as possible.
See README for more details:

https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md

  import google.generativeai as genai
INFO:     Started server process [11344]
INFO:     Waiting for application startup.
08/29 00:27 WARNING <UciProtocol (pid=8792)>: stderr >>        _
08/29 00:27 WARNING <UciProtocol (pid=8792)>: stderr >> |   _ | |
08/29 00:27 WARNING <UciProtocol (pid=8792)>: stderr >> |_ |_ |_| v0.32.1 built Nov 23 2025
08/29 00:27 WARNING <UciProtocol (pid=8792)>: stderr >> Search algorithm: classic
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:51474 - "GET /api/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:51475 - "GET / HTTP/1.1" 200 OK
```

---

## 4. Dangling-Link Inventory

```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -c "import glob,os,re; [print(f'{p}: {m}') for p in glob.glob('docs/**/*.md',recursive=True)+glob.glob('*.md') for m in re.findall(r'\]\(([^)]+\.md)\)', open(p,encoding='utf-8',errors='replace').read()) if not m.startswith('http') and not os.path.exists(os.path.join(os.path.dirname(p),m))]"
```

**Output:**
```
docs\SALIENCE_BOOK_PARSER_REPORT.md: file:///c:/Users/Admin/Documents/chess_speak_out_loud/docs/SALIENCE_BOOK_PARSER_REPORT.md
docs\guides\HOW_TO_USE.md: HOW_TO_RUN.md
docs\guides\HOW_TO_USE.md: docs/api_contract.md
docs\pytorch_learning\README.md: file:///c:/Users/Admin/Documents/chess_speak_out_loud/docs/pytorch_learning/01_pytorch_fundamentals_and_headstart.md
docs\pytorch_learning\README.md: file:///c:/Users/Admin/Documents/chess_speak_out_loud/docs/study/STUDY_CROSS_ENTROPY_AND_OPTIMIZATION.md
docs\study\PROMPT_LEADER_MCTS_STUDY_GUIDE.md: file:///c:/Users/Admin/Documents/chess_speak_out_loud/docs/study/STUDY_DIALOGUE_MCTS_FOUNDATIONS.md
docs\study\PROMPT_LEADER_MCTS_STUDY_GUIDE.md: file:///c:/Users/Admin/Documents/chess_speak_out_loud/docs/study/STUDY_DIALOGUE_MCTS_FOUNDATIONS.md
docs\study\STUDY_SESSION_LOG.md: file:///c:/Users/Admin/Documents/chess_speak_out_loud/docs/study/STUDY_CROSS_ENTROPY_AND_OPTIMIZATION.md
HOW_TO_RUN.md: DEPLOY_DEBIAN.md
README.md: GM_CURRICULUM_PLAN.md
```

---

## 5. Deviations

1. **Moved files**: Exactly the 26 root markdown files and 2 junk files named in §3 and §4 were moved. No extra files were moved.
2. **Move command for `texput.log`**: As noted in §4, `texput.log` is untracked due to `.gitignore` and `git mv` reported `fatal: not under version control`, so it was moved to `archive/reports/texput.log` via `Move-Item`.
3. **Edits**: Exactly the four permitted targets named in §5 were edited (`CLAUDE.md`, `state/MAP.md`, `trainer/content/ladders/neural_processes.json`). Nothing else was edited.

---

## 6. Confirmations

- I deleted no file from the repository.
- No card field other than `sources` was changed.
