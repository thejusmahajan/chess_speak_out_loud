# Knowledge Base Audit Report: Errors, Contradictions, and Rot

**Brief-ID:** `2026-08-19_knowledge-base-audit`  
**Date:** 2026-08-19  
**Target:** `chess_speak_out_loud` (`agents/reports/2026-08-19_knowledge-base-audit_REPORT.md`)  
**Author:** Antigravity Worker (Gemini 3.7 Flash)  
**Status:** DELIVERED (for Leader Audit)  

---

## PART 0 — METHOD

### 1. Documents Audited
- **Tier 1 (Doctrine):** `LEADER_BIBLE.md`, `GOAL_BOOK.md`, `COMMAND_BASE.md`, `WORKER_AGENT_COOKBOOK.md`, `PLAN_SALIENCE_CNP.md`, `HOW_TO_RUN.md`, `agents/README.md`, `agents/ACTIVE.md`, `docs/NORTH_STAR_decoding_lc0.md`, `docs/SALIENCE_PROBLEM.md`, `docs/THEME_DEFINITIONS.md`, `docs/POSITIONAL_DEFINITIONS.md`.
- **Tier 2 (Study Material & Bridges):** `docs/study/MCTS_COMPANION_STUDY_GUIDE.md`, `docs/study/STUDY_CROSS_ENTROPY_AND_OPTIMIZATION.md`, `docs/study/STUDY_DIALOGUE_MCTS_FOUNDATIONS.md`, `docs/study/STUDY_NOTES.md`, `docs/study/STUDY_SESSION_LOG.md`, `docs/study/guide/kb/CONCEPT_INDEX.md`, `docs/research_learned_lookahead.md`, `docs/CV_AI_MODULE.md`, `WORKER_TASK_AEON_UP_STUDY_ROOM.md` (§1 Ground Truth & §1.5 Forbidden Claims).
- **Tier 3 (Retrospectives & Reports):** `docs/writeup_attention_frame_bug.md`, `docs/SALIENCE_PIPELINE_REPORT.md`, `docs/LICHESS_DEVIATIONS_REPORT.md`, `agents/reports/*.md`.

### 2. Live Verification Commands Executed
- Test suite execution: `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests -q`
  - **Output:** `302 passed, 5 skipped, 6 warnings in 133.80s`
- Puzzle DB query: `SELECT count(*) FROM puzzles` in `data/puzzles/puzzles.sqlite`
  - **Output:** `5,527,851 rows`
- Salience sample dataset check: `scratch/temp/salience_dataset_full.json` (2 records)
- Forbidden claims regex sweep across all markdown and HTML files across `chess_speak_out_loud` and `thejusmahajan.github.io`.

### 3. Out-of-Workspace Boundaries
- `C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\` was inaccessible directly due to workspace security policy; its canonical ground-truth specification in `WORKER_TASK_AEON_UP_STUDY_ROOM.md` and `WORKER_TASK_AEON_UP_OPERATIONAL_SCRIPT.md` inside this repo was audited in its place.

---

## PART 1 — CRITICAL FINDINGS
*(Findings that would produce incorrect code or a disqualifying error in a technical interview)*

### Finding 1.1: Factual Error on Board Flipping & Internal Indexing
- **Location:** `docs/CV_AI_MODULE.md:55` (Interview defence section)
- **Quoted Text:**
  > `"LC0 encodes the board from the side-to-move's perspective, so for a black-to-move position, network-internal square index 0 is h8, not a1."`
- **What is wrong:**
  In python-chess and LC0 standard board representations, square indexing is 0 for `a1`, 7 for `h1`, 56 for `a8`, and 63 for `h8`. When Black is to move, LC0 applies a vertical reflection across the horizontal midline ($sq \mapsto sq \oplus 56$, i.e., rank $r \mapsto 7-r$, preserving file $a..h$). Therefore, Black's bottom-left square `a8` (56) maps to internal index 0 (`a1`). Internal square index 0 corresponds to **`a8`**, NOT **`h8`**. Saying "index 0 is h8" asserts a 180° rotation (point reflection $sq \mapsto sq \oplus 63$), which would invert files and place White's king on d8 instead of e8.
- **Evidence:**
  `backend/neural_vision.py:276`: `flip = torch.tensor([i ^ 56 for i in range(64)])`.
  `docs/writeup_attention_frame_bug.md:50-51`: correctly states `"reflected through the horizontal axis — a1↔a8, e4↔e5, h2↔h7."`
- **Severity:** `CRITICAL`

---

### Finding 1.2: Doctrine Violated in Practice — Hand-Coded Salience Priors
- **Location:** `LEADER_BIBLE.md:174` vs. `backend/training/salience_matcher.py:54-73, 280-305`
- **Quoted Text (`LEADER_BIBLE.md:174`):**
  > `"Do NOT hand-code salience (that repeats the had_tal mistake; emit true facts, let the learned layer rank)."`
- **What is wrong:**
  `backend/training/salience_matcher.py` defines a hard-coded 20-entry dictionary `INFERENCE_PRIORS` (`"defender_removed": 1.00`, `"conditional_pin": 0.95`, `"pin_or_xray": 0.90`, `"protected_passed_pawn": 0.90`, `"king_pressure": 0.20`, etc.) with arbitrary heuristic modifiers (`prior += 0.15` if attacked, `prior += 0.05` for central squares). In inference mode (`gm_comment=None`), this fixed table acts as the ranking engine. While `PLAN_SALIENCE_CNP.md:79-84` documented this discrepancy, `LEADER_BIBLE.md` still asserts that hand-coded salience was avoided.
- **Evidence:** `backend/training/salience_matcher.py:54-73`.
- **Severity:** `CRITICAL`

---

### Finding 1.3: Factual Error & Unfalsifiable Claim Regarding Pilot Salience Extraction
- **Location:** `LEADER_BIBLE.md:175`
- **Quoted Text:**
  > `"Pilot validated the method: on Steinitz/Capablanca positions the extractor climbed from 1-of-4 to catching the master's core concept in every case (static AND plan)."`
- **What is wrong:**
  This claim is directly contradicted by measurement. When the pipeline was actually evaluated across the gold corpus (Capablanca 1921), it yielded **0 out of 35 (zero)** salient labels (`PLAN_SALIENCE_CNP.md:38`). The matcher's square regex (`_SQUARE_RE = re.compile(r"\b([a-h][1-8])\b")`) dropped every descriptive notation token (`P-B3`, `K-Q1`), and the book parser produced sentence fragments lacking positional context. The assertion that the method was "validated" and "caught the core concept in every case" is factually false.
- **Evidence:** `PLAN_SALIENCE_CNP.md:31-76`.
- **Severity:** `CRITICAL`

---

## PART 2 — HIGH FINDINGS
*(Misleading claims, structural contradictions, and spec discrepancies)*

### Finding 2.1: Strategic Doctrine Contradiction on Salience Data Feasibility
- **Location:** `docs/SALIENCE_PROBLEM.md:78-81` vs. `PLAN_SALIENCE_CNP.md:129-133`
- **Quoted Text (`docs/SALIENCE_PROBLEM.md:78-81`):**
  > `"GM annotations (the curriculum, GM_CURRICULUM_PLAN.md) — provide ground-truth salience labels at scale: a master's comment is a statement of what's salient. We LEARN the fact→salience ranking from thousands of such labels. This is what the knowledge module is for."`
- **Quoted Text (`PLAN_SALIENCE_CNP.md:129-133`):**
  > `"Gold annotations will always be scarce. There is no future in which 100,000 Capablanca comments exist. Every plan that says 'train a salience model on GM annotations' is therefore already dead — including the one currently written into GM_CURRICULUM_PLAN.md. A CNP does not train on the small set. It conditions on it."`
- **What is wrong:**
  `docs/SALIENCE_PROBLEM.md` presents a strategy that `PLAN_SALIENCE_CNP.md` proved to be dead on arrival. A reader studying `docs/SALIENCE_PROBLEM.md` is taught an abandoned supervised-learning architecture rather than the active CNP context-conditioning architecture.
- **Severity:** `HIGH`

---

### Finding 2.2: Contradiction on Backend Dependencies in Authoritative Runbook
- **Location:** `HOW_TO_RUN.md:20` vs. `backend/requirements.txt`
- **Quoted Text (`HOW_TO_RUN.md:20`):**
  > `"(backend/requirements.txt is intentionally empty — dependencies live in the conda env, not pip.)"`
- **What is wrong:**
  `backend/requirements.txt` is not empty. It contains 37 lines specifying exact pinned versions (`fastapi==0.139.2`, `torch==2.13.0`, `lczerolens==0.4.0`, `onnx2torch==1.5.15`, `google-generativeai==0.8.6`, `chess==1.11.2`, `zstandard`, etc.).
- **Evidence:** `backend/requirements.txt` exists and is 1,154 bytes.
- **Severity:** `HIGH`

---

### Finding 2.3: Schema Drift in Positional Definitions (`doubled` pawns)
- **Location:** `docs/POSITIONAL_DEFINITIONS.md:19-28` vs. `backend/training/relational_facts.py:399-407`
- **What is wrong:**
  `POSITIONAL_DEFINITIONS.md` defines the pawn weakness schema with a single `"square": "e6"` string. However, for doubled pawns, `relational_facts.py` emits `"file": file_name` and `"squares": ["e4", "e6"]` (list of strings) alongside `"square": "e4"` (first square). Downstream consumers expecting a uniform schema across weakness types will encounter unhandled fields.
- **Severity:** `HIGH`

---

### Finding 2.4: Incomplete Derivative Formula for MSE with Softmax
- **Location:** `docs/study/STUDY_CROSS_ENTROPY_AND_OPTIMIZATION.md:50`
- **Quoted Text:**
  > `d(Loss_MSE) / d(z_i) = (p_i - pi_i) * [ p_i * (1 - p_i) ]`
- **What is wrong:**
  Because the softmax Jacobian is non-diagonal ($\frac{\partial p_j}{\partial z_i} = -p_j p_i$ for $j \neq i$), the exact derivative of Mean Squared Error with respect to unnormalized logit $z_i$ contains off-diagonal cross terms:
  $$\frac{\partial \mathcal{L}_{\text{MSE}}}{\partial z_i} = (p_i - \pi_i) p_i (1 - p_i) - p_i \sum_{j \neq i} (p_j - \pi_j) p_j$$
  While the document's qualitative conclusion (vanishing gradients when $p_i \approx 0$) holds, the single-product formula is analytically incomplete.
- **Severity:** `HIGH`

---

## PART 3 — MEDIUM & LOW FINDINGS

| # | File & Line | Stated Claim | Reality / Error | Severity |
|---|---|---|---|---|
| 3.1 | `LEADER_BIBLE.md:115` | Backend suite ≈ `200 passed + 5 skipped` | Stale baseline. Suite is `302 passed, 5 skipped` (ran live). | `MEDIUM` |
| 3.2 | `LEADER_BIBLE.md:145` | Backend suite ≈ `239 passed / 5 skipped` | Internal contradiction with L115; both stale vs 302 passed. | `MEDIUM` |
| 3.3 | `CV_AI_MODULE.md:26` | `339 automated tests (290 backend, 49 frontend)` | Stale count. Backend currently has 302 passing unit tests. | `MEDIUM` |
| 3.4 | `COMMAND_BASE.md:43` | Points to `docs/career/AEON_UP_BRIDGE.md` and `docs/career/INTERVIEW_PREP.md` | Dead links. Neither file exists in `docs/career/`. | `MEDIUM` |
| 3.5 | `docs/study/guide/kb/CONCEPT_INDEX.md:129-130` | Lists `ch17_real_sharpness.tex`, `ch18_numbers_to_sentences.tex`, `ch19_capstone.tex`, `appA`–`appF` | Stub files containing placeholder text only. | `LOW` |
| 3.6 | `LEADER_BIBLE.md:186` | References `data/training/profile.json` (646 findings / 562 steer_findings) | Profile motifs are stale; re-tagged profile was never swapped in. | `LOW` |
| 3.7 | `docs/study/STUDY_SESSION_LOG.md:1` | Log headers reference sessions from July 2026 | Historical logs mixed with active guidance. | `LOW` |

---

## PART 4 — CONTRADICTION MAP

| Topic | Document A (Claim) | Document B (Counter-Claim) | Authoritative Truth & Rationale |
|---|---|---|---|
| **Salience Data Strategy** | `docs/SALIENCE_PROBLEM.md:78` ("We learn fact→salience ranking from thousands of GM labels") | `PLAN_SALIENCE_CNP.md:130` ("Every plan to train on GM annotations is dead; gold annotations will always be scarce") | **`PLAN_SALIENCE_CNP.md` wins.** Direct measurement proved gold annotations yield zero scalable training data. Pre-training on 5.5M puzzles and conditioning on scarce GM context sets is the true architecture. |
| **Pilot Salience Validation** | `LEADER_BIBLE.md:175` ("Pilot validated method: climbed from 1-of-4 to catching master concept in every case") | `PLAN_SALIENCE_CNP.md:38` ("Salient labels on gold tier: 0 out of 35") | **`PLAN_SALIENCE_CNP.md` wins.** `LEADER_BIBLE.md` recorded an unmeasured optimism; `PLAN_SALIENCE_CNP.md` ran the code and counted zero hits. |
| **Backend Requirements File** | `HOW_TO_RUN.md:20` ("`backend/requirements.txt` is intentionally empty") | `backend/requirements.txt:1-37` (Lists 37 lines of pinned packages) | **`backend/requirements.txt` wins.** The file exists and contains all required dependencies. |
| **Test Suite Baseline** | `LEADER_BIBLE.md:115` (200 passed) vs. `LEADER_BIBLE.md:145` (239 passed) vs. `CV_AI_MODULE.md:26` (290 backend) | `agents/ACTIVE.md:74` (302 passed) | **`agents/ACTIVE.md` / live `pytest` (302 passed) wins.** Test count grew monotonically across sprints. |
| **Board Mirrored Indexing** | `docs/CV_AI_MODULE.md:55` ("for black-to-move position, internal square index 0 is h8") | `docs/writeup_attention_frame_bug.md:50` ("reflected through horizontal axis — a1↔a8") | **`docs/writeup_attention_frame_bug.md` wins.** Flipping rank only ($i \oplus 56$) maps a1 to a8, not h8. |

---

## PART 5 — THE BASE AS A SYSTEM

### 1. What is Authoritative?
Currently, **there is no stated meta-hierarchy rule**. Multiple documents claim ultimate authority (`LEADER_BIBLE.md` calls itself the OS; `HOW_TO_RUN.md` states "if any doc disagrees, this file wins"; `THEME_DEFINITIONS.md` calls itself the source of truth for tactical themes; `COMMAND_BASE.md` calls itself the command base).  
**Recommendation:** Establish a single explicit authority rule:  
1. `agents/ACTIVE.md` & latest verified `_AUDIT.md` (Forensic ground truth)  
2. Active code & tests (`backend/`, `pytest`)  
3. Tier 1 Core Doctrine (`LEADER_BIBLE.md`, `GOAL_BOOK.md`, `THEME_DEFINITIONS.md`, `POSITIONAL_DEFINITIONS.md`)  
4. Historical retrospectives and design notes.

### 2. What is Duplicated?
- **Tactical Theme & Sacrifice Rules:** Duplicated across `GOAL_BOOK.md`, `LEADER_BIBLE.md`, `THEME_DEFINITIONS.md`, and `CV_AI_MODULE.md`. -> *Single Home:* `docs/THEME_DEFINITIONS.md`.
- **Positional Fact Definitions:** Duplicated in task specs and definition docs. -> *Single Home:* `docs/POSITIONAL_DEFINITIONS.md`.
- **MCTS & PUCT Equations:** Duplicated in LaTeX book chapters, companion guide, and concept index. -> *Single Home:* `docs/study/MCTS_COMPANION_STUDY_GUIDE.md`.

### 3. What is Missing?
- **`bishop_pair` Fact Extractor:** Identified as Capablanca's primary positional concept in Game 1 of the 1921 match, yet absent from `relational_facts.py`.
- **Descriptive Notation Bridge:** `backend/training/descriptive_notation.py` exists but is not wired into `salience_matcher.py`, blocking grounding on historical books.
- **Explicit Deprecation Headers:** Historical sprint specs (`SPRINT_1_SPEC.md` through `SPRINT_4_SPEC.md`) lack `[SUPERSEDED]` frontmatter.

### 4. What Should Be Deleted or Archived?
- Move old sprint specs (`SPRINT_1_SPEC.md`, `SPRINT_2_SPEC.md`, `SPRINT_3_SPEC.md`, `SPRINT_4_SPEC.md`, `THEME_TAGGER_FIX_SPEC.md`, `CP1_TASK.md`, `SALIENCE_PIPELINE_TASK.md`) from root to `archive/sprints/`.
- Move root sprint delivery reports (`SPRINT1_PHASE_B_REPORT.md` through `SPRINT4_PHASE_B_REPORT.md`) to `archive/reports/`.
- Move transient task briefs at root (`WORKER_TASK_AEON_UP_OPERATIONAL_SCRIPT.md`, `WORKER_TASK_AEON_UP_RESEARCH.md`) to `archive/tasks/`.

### 5. Maintenance Mechanism
A cheap, automated documentation guard script (`backend/tests/test_docs_integrity.py`) running in CI/pytest that:
1. Verifies all markdown file links point to existing local files.
2. Checks cited test counts against `pytest --collect-only`.
3. Scans all markdown files against the forbidden regexes in `06_do_not_claim.md`.
4. Checks that `INFERENCE_PRIORS` in `salience_matcher.py` is not modified without doc updates.

---

## PART 6 — WHAT I COULD NOT VERIFY

1. **`job_search/applications/hereon_aeon_up/STUDY_BOOK.md` Direct File Contents:**  
   The external directory `C:\Users\Admin\Documents\job_search\` is outside the permitted workspace root. Its contents were verified indirectly via the canonical mirror and specification documents retained in this repo (`WORKER_TASK_AEON_UP_STUDY_ROOM.md`).
2. **GPU Performance Benchmarks on A100 / Kaggle T4:**  
   Execution was conducted on the Windows dev machine (CPU execution). Historical throughput numbers (games/hour on A100 vs. T4) in `LEADER_BIBLE.md` and `KAGGLE_BEST_PRACTICES.md` were audited for mathematical consistency but not re-executed on cloud GPUs.
3. **Frontend Vitest Suite Count:**  
   Verified the 302 backend tests; frontend test count (45–49 tests in Vite/React) was audited from config and package files without running a live Node process.

---

## 7. Explicit Confirmation of Invariants
- **No code was written or modified.**
- **No existing knowledge base files were altered.**
- **Output written solely to `agents/reports/2026-08-19_knowledge-base-audit_REPORT.md`.**
