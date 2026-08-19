# Delivery Report: Level 0 Foundation & Plain Text Cards (2026-08-20_trainer-level-zero)

**Brief ID:** `2026-08-20_trainer-level-zero`  
**Date:** 2026-08-19 / 2026-08-20  
**Status:** COMPLETED & VERIFIED  

---

## 1. Executive Summary & Intent Fulfillment

Thejus flagged eight Level 1 cards as incomprehensible due to unintroduced deep-learning jargon and unrendered raw LaTeX source (`$...$`). 

To address this:
1. **Removed All Raw LaTeX:** Swept all 5 ladders and eliminated all `$...$` syntax. Replaced notation with plain English descriptions and standard Unicode mathematical symbols (`θ`, `σ²`, `μ`, `P(move | position)`).
2. **Added Strict LaTeX Detection Gate:** Added an automated check in `trainer/verify_cards.py` that fails if any card field contains `$` followed by letters, backslashes, or brackets.
3. **Built Level 0 Ground Floor (18 New Cards):** Authored 18 foundational onboarding cards pitched specifically for a computational physicist (assuming strong physics, HPC, NetCDF, Fortran/Python/R, and zero deep learning vocabulary).
4. **Re-levelled Mis-tiered Cards:** Promoted `unc-l1-003` (Law of Total Variance in Deep Ensembles) to `unc-l3-003` (Level 3, difficulty 1480).
5. **Prerequisite Gating:** Chained Level 1 cards to require the corresponding Level 0 foundational cards.

---

## 2. Gate Verification Results (Real Terminal Outputs)

### Gate 1: Content & Grounding Validation
```
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer/verify_cards.py
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
  - neural_processes: 15 cards (Level 0: 3)
  - own_work: 14 cards (Level 0: 2)
  - pytorch: 19 cards (Level 0: 7)
  - uncertainty: 16 cards (Level 0: 4)

Total verified cards: 78
Total repo citations: 91
Total URL citations:  74
=================================================================
Exit code: 0
```

---

### Gate 2: Live External URL Resolution
```
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer/verify_cards.py --check-urls
```
**Output:**
```
=================================================================
Verifying Knowledge Trainer Content Ladders & Boundaries...
=================================================================

Resolving 19 unique external URLs in parallel...
Loaded 5 authoritative forbidden claim boundaries from 06_do_not_claim.md.

[PASS] All content, grounding, and constraint gates passed!

Card Counts by Ladder:
  - air_quality: 14 cards (Level 0: 2)
  - neural_processes: 15 cards (Level 0: 3)
  - own_work: 14 cards (Level 0: 2)
  - pytorch: 19 cards (Level 0: 7)
  - uncertainty: 16 cards (Level 0: 4)

Total verified cards: 78
Total repo citations: 91
Total URL citations:  74
All 19 external URLs successfully resolved!
=================================================================
Exit code: 0
```

---

### Gate 3: Unit Tests (Elo, SM-2, Prerequisite Gating, LaTeX Check)
```
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
```
**Output:**
```
=========== test session starts ===========
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 11 items

trainer\tests\test_engine.py ...........                                 [100%]

============ 11 passed in 0.39s ============
Exit code: 0
```

---

### Gate 4: Working Tree Status
```
git status
```
**Output:**
```
On branch windows-dev
Your branch is ahead of 'origin/windows-dev' by 26 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
	modified:   trainer/content/ladders/air_quality.json
	modified:   trainer/content/ladders/neural_processes.json
	modified:   trainer/content/ladders/own_work.json
	modified:   trainer/content/ladders/pytorch.json
	modified:   trainer/content/ladders/uncertainty.json
	modified:   trainer/static/index.html
	modified:   trainer/tests/test_engine.py
	modified:   trainer/verify_cards.py

Untracked files:
	gemini_stable_drill_ids_srs.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

---

## 3. Level 0 Cards Breakdown (18 Cards)

| Ladder | Card ID | Topic | Difficulty | Grounding Source |
|---|---|---|---|---|
| `pytorch` | `pyt-l0-001` | tensors vs numpy arrays | 780 | `pytorch.org/docs/stable/tensors.html` |
| `pytorch` | `pyt-l0-002` | tensor shape notation `(B, 1, D)` | 790 | `pytorch.org/docs/stable/tensor_attributes.html`, `backend/neural_vision.py` |
| `pytorch` | `pyt-l0-003` | broadcasting mechanics `(3,1)+(1,4)` | 800 | `pytorch.org/docs/stable/notes/broadcasting.html` |
| `pytorch` | `pyt-l0-004` | tensor device placement (CPU vs GPU) | 810 | `pytorch.org/docs/stable/tensor_attributes.html`, `backend/neural_vision.py` |
| `pytorch` | `pyt-l0-005` | gradient concept in one sentence | 820 | `pytorch.org/docs/stable/autograd.html` |
| `pytorch` | `pyt-l0-006` | `optimizer.zero_grad()` mechanics | 830 | `pytorch.org/docs/stable/optim.html` |
| `pytorch` | `pyt-l0-007` | logits vs probabilities | 840 | `pytorch.org/docs/stable/generated/torch.nn.Module.html` |
| `uncertainty` | `unc-l0-001` | variance concept in predictions | 780 | `arxiv.org/abs/1703.04977` |
| `uncertainty` | `unc-l0-002` | aleatoric vs epistemic intuition | 790 | `arxiv.org/abs/1703.04977` |
| `uncertainty` | `unc-l0-003` | model ensembles & disagreement | 810 | `arxiv.org/abs/1703.04977` |
| `uncertainty` | `unc-l0-004` | calibration in one sentence | 820 | `doi.org/10.1198/016214506000001437` |
| `neural-processes` | `np-l0-001` | model capacity concept | 780 | `arxiv.org/abs/1807.01613` |
| `neural-processes` | `np-l0-002` | kernel & kernel matrix concept | 790 | `arxiv.org/abs/1807.01613` |
| `neural-processes` | `np-l0-003` | parametric vs non-parametric intuition | 800 | `arxiv.org/abs/1807.01613` |
| `own-work` | `own-l0-001` | policy vs value concept | 780 | `docs/study/STUDY_CROSS_ENTROPY_AND_OPTIMIZATION.md` |
| `own-work` | `own-l0-002` | win-draw-loss (WDL) distribution | 800 | `docs/study/STUDY_CROSS_ENTROPY_AND_OPTIMIZATION.md` |
| `air-quality` | `aq-l0-001` | criteria air pollutants | 780 | `doi.org/10.1175/JAM2536.1` |
| `air-quality` | `aq-l0-002` | emission rate vs concentration | 790 | `doi.org/10.5194/gmd-12-3357-2019` |

---

## 4. Proof of LaTeX Gate & Prerequisite Gating

### A. Proof of LaTeX Mutation Gate
1. **Mutation Injected:** Added `Containing unrendered $\theta$ formula.` to `pyt-l0-001`.
2. **Gate Execution:**
   ```
   =================================================================
   Verifying Knowledge Trainer Content Ladders & Boundaries...
   =================================================================
   Loaded 5 authoritative forbidden claim boundaries from 06_do_not_claim.md.

   [FAIL] Found 1 content verification error(s):

     1. Card 'pyt-l0-001': Field 'answer' contains unrendered LaTeX notation '$\'. Rewrite using plain English words and Unicode symbols (e.g. θ, σ², μ, P(move | pos)).

   =================================================================
   Exit code: 1
   ```
3. **Restoration:** Card restored and verified passing.

### B. Proof of Prerequisite Gating (Automated Test)
Tested in `trainer/tests/test_engine.py::test_level_zero_prerequisite_gating`:
- With user rating 800 and zero cards answered: Level 1 card (`pyt-l1-001`, requires `pyt-l0-001`) is locked. Selector offers only Level 0 card (`pyt-l0-001`).
- When Level 0 card is answered with partial score 0.5: Level 1 card remains locked.
- When Level 0 card is answered with score 1.0 (mastered): Level 1 card unlocks immediately and enters the selectable queue.

---

## 5. Re-leveling Table

| Card ID | Old Level & Difficulty | New Level & Difficulty | Reason |
|---|---|---|---|
| `unc-l1-003` | Level 1 (1070) | Level 3 (1480) (`unc-l3-003`) | Requires Law of Total Variance and deep ensemble variance decomposition. Re-levelled to Level 3; replaced at Level 1 by foundational uncertainty cards. |
| `pyt-l1-001` | Level 1 (980) | Level 1 (980) | Added prerequisites `["pyt-l0-001", "pyt-l0-002"]`. |
| `pyt-l1-002` | Level 1 (1020) | Level 1 (1020) | Added prerequisite `["pyt-l0-004"]`. |
| `pyt-l1-003` | Level 1 (1050) | Level 1 (1050) | Added prerequisite `["pyt-l0-003"]`. |
| `np-l1-001` | Level 1 (990) | Level 1 (990) | Added prerequisites `["np-l0-002", "np-l0-003"]`. |
| `np-l1-002` | Level 1 (1040) | Level 1 (1040) | Added prerequisite `["np-l0-002"]`. |
| `np-l1-003` | Level 1 (1060) | Level 1 (1060) | Added prerequisite `["np-l0-003"]`. |
| `own-l1-003` | Level 1 (1050) | Level 1 (1050) | Added prerequisites `["own-l0-001", "own-l0-002"]`. |
| `aq-l1-001` | Level 1 (990) | Level 1 (990) | Added prerequisites `["aq-l0-001", "aq-l0-002"]`. |
| `aq-l1-002` | Level 1 (1020) | Level 1 (1020) | Added prerequisite `["aq-l0-001"]`. |
| `aq-l1-003` | Level 1 (1050) | Level 1 (1050) | Added prerequisite `["aq-l0-001"]`. |

---

## 6. Required Reflection Question

> **"If exactly one thing in this delivery is still wrong, what is it most likely to be, and did I check it?"**

**Answer:**  
The most likely risk is that a Level 0 card could inadvertently use an implicit deep learning analogy that seems elementary to an ML engineer but remains opaque to a physicist (for example, assuming the word "batch" or "linear layer" is self-evident). 

**How it was checked:**  
I audited every sentence in all 18 Level 0 cards against Thejus's verbatim comment logs. Specifically:
1. `pyt-l0-002` explicitly defines B, 1, and D as named dimension sizes and ties them to a concrete chess board batch (16 positions, 64 squares).
2. `pyt-l0-003` gives a concrete `(3, 1) + (1, 4) -> (3, 4)` numerical matrix example to illustrate broadcasting.
3. `pyt-l0-006` directly addresses his twice-asked question about `zero_grad()`, explaining that PyTorch adds gradients by default (`+=`).
4. `pyt-l0-007` explicitly refutes the misconception that logits are percentages, showing negative and real-valued examples (`[-2.1, 0.5, 3.4]`).
5. `unc-l0-002` explains aleatoric vs epistemic uncertainty strictly with physical sensor noise vs spatial sensor absence, with zero mathematical formulas.
