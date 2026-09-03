# Opening Dataset Build & Alarms Evaluation Report

**Brief ID:** `2026-09-03_phi-opening-dataset-and-kaggle-training`  
**Execution Date:** 2026-09-03  
**Status:** **ALARM A5 FIRED — EXECUTION STOPPED PER BRIEF SPECIFICATION**  
**Environment:** Windows conda `cszero`  

---

## 1. Executive Summary & Stop Trigger

Per Section 1 and Section 4 of `agents/briefs/2026-09-03_phi-opening-dataset-and-kaggle-training.md`:
> *"Intent outranks instructions. If any instruction below conflicts with this paragraph, the intent wins — stop and report. Doing so is a success, never a boundary violation."*  
> *"A5 — phase-only AUC. Logistic regression on five features only ... Must be < 0.60. If A5 fires, stop and report. Do not tune it away. A fired alarm is a stop, not a parameter."*

The opening dataset builder was executed in strict adherence to the brief. All positive sampling constraints (50/50 side balance, family capping $\le 15\%$, and maximum sharp oversampling) and negative matching rules (preferring N1 over N2) were fulfilled.

During Step 6 evaluation of the pre-registered alarms:
- **Alarms A1, A2, A3, and A4 passed cleanly.**
- **Alarm A5 FIRED with validation AUC = 0.6213 (pre-registered threshold: < 0.60).**

As mandated by the brief, **execution has stopped immediately**. No weights were tuned away, no datasets were uploaded to Kaggle, and no downstream training was launched.

---

## 2. Checkpoint 1: Code Architecture & Function Reuse

### Imported Functions (from `backend/training/config_steering/build_dataset.py`)
1. `compute_material_and_phase`: Computes 10-piece counts, phase bucket, and material string key.
2. `compute_tactical_features`: Computes cheap tactical features (`in_check`, `n_legal_moves`, `capture_available`, `n_checks_available`, and mobility bucket).
3. `get_split_name`: Deterministic MD5 hash partitioning into `train` (<80), `val` (80..89), and `test` (>=90).
4. `compute_roc_auc`: Exact Mann-Whitney U rank-sum ROC AUC calculation.
5. `fit_logistic_regression_and_auc`: PyTorch L-BFGS logistic regression classifier with validation AUC calculation.
6. `encode` (from `backend.training.config_steering.encode`): 18-plane POV-flipped bitboard encoder.

### Freshly Written Functions (in `backend/training/config_steering/build_opening_dataset.py`)
1. `parse_opening_family(tag_str: str) -> str`:  
   *Rationale:* Constraint 2b requires rolling `opening_tags` up to a family key truncated at the second underscore, while strictly preserving `Accepted` or `Declined` variants (e.g. `Italian_Game_Evans_Gambit_Declined` $\to$ `Italian_Game_Declined`, `Danish_Gambit_Accepted_Classical_Defense` $\to$ `Danish_Gambit_Accepted`).
2. `is_sharp_opening(themes_str: str) -> bool`:  
   *Rationale:* Constraint 2a requires flagging puzzles carrying the `sacrifice` or `kingsideAttack` motifs to satisfy sharp subset oversampling.
3. `compute_a5_features(board: chess.Board) -> tuple[float, float, float, float, float]`:  
   *Rationale:* Alarm A5 requires exactly 5 development/phase features: total piece count, pawn count, castling rights count (0 to 4), `in_check`, and `n_legal_moves`.
4. `build_opening_dataset(...)`:  
   *Rationale:* Standalone builder incorporating positive oversampling, N1-preferential matching, flat `.npz` bitboard packing, and Alarms A1–A5.

---

## 3. Checkpoint 2: Positive Pool Sampling Statistics

- **Total Puzzles Scanned in Rating Window [1500, 2200]:** 1,907,960
- **Opening Puzzles Found (`themes LIKE '%opening%'`):** 85,797 (4.50%)
- **Raw Sharp vs Non-Sharp Breakdown:**
  - Sharp (`sacrifice` or `kingsideAttack`): **12,321** (14.36% of all opening puzzles)
    - White to move (WTM): 4,983
    - Black to move (BTM): 7,338
  - Non-sharp: **73,476** (85.64%)
    - White to move (WTM): 34,767
    - Black to move (BTM): 38,709
- **Positives Sampled:** **60,000**
  - White to move: **30,000** (50.0%)
  - Black to move: **30,000** (50.0%)
- **Sharp Positives Kept:** **12,321** (100% of all available sharp opening puzzles in the rating band were captured)
- **Achieved Sharp Share:** **20.54%** (12,321 / 60,000)
  *(Note: Reaching the nominal 25% target on 60,000 rows would require 15,000 sharp puzzles, but only 12,321 exist in the entire 1500–2200 population. 100% of available sharp puzzles were included.)*
- **Distinct Opening Families Represented:** 148
- **Top 15 Families in Positives (Cap $\le 15.0\% = 9,000$):**
  1. `Sicilian_Defense`: 8,661 (14.44%) — **PASS** (< 15.0%)
  2. `French_Defense`: 4,081 (6.80%)
  3. `Italian_Game`: 3,233 (5.39%)
  4. `Caro-Kann_Defense`: 3,021 (5.04%)
  5. `Queens_Pawn`: 2,967 (4.95%)
  6. `Scandinavian_Defense`: 2,675 (4.46%)
  7. `Queens_Gambit_Declined`: 2,062 (3.44%)
  8. `English_Opening`: 1,839 (3.06%)
  9. `Ruy_Lopez`: 1,720 (2.87%)
  10. `Indian_Defense`: 1,700 (2.83%)
  11. `Scotch_Game`: 1,599 (2.67%)
  12. `Russian_Game`: 1,329 (2.21%)
  13. `Unknown`: 1,259 (2.10%)
  14. `Philidor_Defense`: 1,148 (1.91%)
  15. `Kings_Gambit_Accepted`: 1,097 (1.83%)

---

## 4. Checkpoint 3: Negative Pools & Matching Statistics

- **Pool N1 (spent tactic from disjoint opening puzzles):**
  - Leftover opening puzzles: 25,797
  - Dropped ending in check: 2,788
  - Dropped carrying `mate` theme: 1,677
  - **Surviving N1 Pool Size:** **21,332**
- **Pool N2 (quiet play from own games plies 1–20):**
  - Games scanned: 9,000
  - **Surviving N2 Pool Size:** **178,454**
- **Matching Priority:** **N1 preferred over N2** by matching key `(material_key, phase_bucket, in_check, mobility_bucket)` partitioned by side-to-move.
- **Match Rate:** **59.71%** (35,826 matched pairs from 60,000 positives)
- **Matched Dataset Size:** **71,652 rows** (35,826 positives, 35,826 negatives)
- **Source Breakdown of Matched Negatives:**
  - N1 (spent tactics): **3,506** (9.79%)
  - N2 (quiet play): **32,320** (90.21%)

---

## 5. Checkpoint 4: Alarm Results

| Alarm | Description | Measurement | Threshold | Result |
|---|---|---|---|---|
| **A1** | Side-to-move balance | Positives: 49.84% WTM<br>Negatives: 49.84% WTM | 50 ± 2% | **PASS** |
| **A2** | Top-10 Material Key Overlap | 10 / 10 keys shared | $\ge 8 / 10$ | **PASS** |
| **A3** | Material-only AUC (10 features) | **0.4733** | $< 0.65$ | **PASS** |
| **A4** | Cheap-tactical + material AUC (14 features) | **0.5672**<br>• N1-only: 0.5401<br>• N2-only: 0.5702 | $< 0.60$ | **PASS** |
| **A5** | **Phase-only AUC (5 features)** | **0.6213** | **$< 0.60$** | **FAIL (FIRED)** |

---

## 6. Forensic Diagnosis: Why Alarm A5 Fired

### 5-Feature Phase-Only Model Parameters (Validation Split)
- Normalized weights:
  - `total_pieces`: $+0.1677$
  - `pawn_count`: $-0.0575$
  - **`castling_count`: $-0.5149$** (Dominant feature, 3× magnitude over any other feature)
  - `in_check`: $\approx 0.0$ (Matched exactly)
  - `n_legal_moves`: $\approx 0.0$ (Matched via mobility bucket)

### Single-Feature ROC AUCs
- `total_pieces`: 0.4822
- `pawn_count`: 0.4961
- `in_check`: 0.5000 (Matched)
- `n_legal_moves`: 0.5012 (Matched)
- **`castling_count`: 0.6201 (directionally 0.3799)**

### Root Cause Analysis
In real quiet game play within plies 1–20 (N2), players retain their castling rights significantly longer (mean castling rights intact: 2.86 out of 4). In tactical opening puzzles (positives), tactics almost always arise after pieces have moved, king moves have occurred, or an exchange has stripped castling rights (mean castling rights intact: 2.15 out of 4).

Because 90.21% of matched negatives had to be drawn from N2 (due to N1 spent opening puzzles having different pawn/piece mobility distributions than sharp puzzles), the logistic regression model learns that positions with intact castling rights are game negatives, achieving AUC = 0.6213.

Per the pre-registered protocol:
> *"If a model that can see nothing but 'how developed is this position' separates the classes, the negatives are not really openings and the whole build is void. If A5 fires, stop and report. Do not tune it away. A fired alarm is a stop, not a parameter."*

Execution is stopped awaiting user instructions.
