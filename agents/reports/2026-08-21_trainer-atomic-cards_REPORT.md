# Delivery Report: Atomic Cards, Concrete Examples & Anti-Repetition Engine

- **Date:** 2026-08-21
- **Brief:** `agents/briefs/2026-08-21_trainer-atomic-cards.md`
- **Branch:** `windows-dev`
- **Status:** Complete (Part A Engine Fixes + Part B Atomic Content Authoring delivered, verified, and passing all gates)

---

## 1. Overview of Delivered Changes

### Part A: Selection Engine Anti-Repetition & Fresh Content Prioritization
1. **Recency Buffer (`progress["recent"]`):**
   - Implemented tracking of the last 8 served card IDs in `progress["recent"]` (persisted to disk).
   - In `select_next_card`, excluded the last 8 cards from the candidate pool.
   - If the candidate pool is exhausted, gracefully relaxes to excluding the last 3 cards, and if still exhausted, serves from the full selectable pool (zero starvation).
2. **Prefer Unseen Cards:**
   - Prioritized candidate cards that have no entry in `progress["cards"]`. Unseen cards outrank reviewed cards to ensure new material is systematically met.
3. **Failed Cards Return Delay (>= 5 cards):**
   - Cards that failed on their last attempt (`score == 0.0`) are quarantined from appearing until at least 5 other cards have been served since the failure.
4. **Unit Tests & Guards:**
   - Added 4 dedicated unit tests in `trainer/tests/test_engine.py` (26 total test suite passing).
   - Mutation tested: verified that omitting the recency filter causes card repetitions in sliding 8-card windows.

### Part B: Atomic Cards with Worked Examples
1. **Thejus's Direct Comments Resolved (from `trainer/state/comments.jsonl`):**
   - `pyt-l0-001` (NumPy vs GPU): Explained the exact hardware and software constraints (CPU malloc, lack of CUDA device pointers, lack of compiled CUDA kernels, no autograd computation graph).
   - `pyt-l0-003` (Broadcasting): Explicitly corrected the misconception that broadcasting zero-pads (it repeats values) with a worked $(3, 1) + (1, 4) \to (3, 4)$ element-by-element addition.
   - `pyt-l0-005` (Gradient): Explained the gradient as the vector of steepest increase on the loss surface and why optimization subtracts it to descend.
   - `pyt-l0-007` (Softmax): Created a worked 3-number example $[1.0, 2.0, 3.0] \to [0.090, 0.245, 0.665]$ showing exponentiation and normalization to 1.0.
   - `unc-l0-001` & `unc-l0-005` (Variance $\sigma^2$ vs $\sigma$): Explained why variance is squared (squared deviations, additivity of independent variances) and how taking $\sqrt{\sigma^2} = \sigma$ restores physical measurement units with an air quality example ($40 \pm 5\,\mu\text{g}/\text{m}^3$).
   - `np-l0-002` (Covariance & Kernel Covariance): Explained statistical covariance first, followed by spatial kernel covariance ($k \approx 1$ nearby vs $k \approx 0$ far away).
   - `np-l0-003` (Retaining Data in Formulation): Concretely contrasted GP storing raw $(x_i, y_i)$ points in memory to compute kernel distances vs parametric neural nets with fixed weights $W$.
   - `own-l1-001` (Transformer Sub-ladder): Authored 6 step-by-step Level 0 transformer foundation cards (`own-l0-003` to `own-l0-008`: tokens as 64 board squares, embeddings, attention in plain words, Query/Key/Value roles, 24 attention heads, 15 stacked layers).
   - `de-gra-l0-001` (Genitive Prepositions): Authored a Genitive refresher card (`de-gra-l0-gen`) and split the 4 prepositions into atomic cards with DWDS example sentences (`aufgrund`, `trotz`, `während`, `wegen`).
   - `de-gra-l0-003` (n-Deklination): Split into masculine `-e` nouns (`de-gra-l0-003a`) and foreign loanword suffixes (`de-gra-l0-003b`) with DWDS examples.
   - `de-kon-l0-003` (Consecutive Connectors): Split into atomic cards for `folglich`, `demnach`, and `infolgedessen` with DWDS examples illustrating Position 1 inversion.

---

## 2. Card Splits & New Card Ledger

| Original Card ID | Status / Action | Resulting Atomic Card IDs | Description & Added Examples |
| :--- | :--- | :--- | :--- |
| *New Card* | Created | `unc-l0-005` | Variance $\sigma^2$ vs standard deviation $\sigma$ with $\text{NO}_2$ units example |
| *New Sub-ladder* | Created (6 cards) | `own-l0-003`<br>`own-l0-004`<br>`own-l0-005`<br>`own-l0-006`<br>`own-l0-007`<br>`own-l0-008` | Step-by-step LC0 Transformer sub-ladder at Level 0 (tokenization, embeddings, attention intuition, Q/K/V roles, 24 heads, 15 stacked layers) |
| *New Card* | Created | `de-gra-l0-gen` | Genitive case refresher (*Wessen?*, articles *des/der/des/der*, noun endings *-s/-es*) |
| `de-gra-l0-001` | **Split into 4** | `de-gra-l0-001a`<br>`de-gra-l0-001b`<br>`de-gra-l0-001c`<br>`de-gra-l0-001d` | Preposition *aufgrund* + Genitiv (DWDS example)<br>Preposition *trotz* + Genitiv (DWDS example)<br>Preposition *während* + Genitiv (DWDS example)<br>Preposition *wegen* + Genitiv (DWDS example) |
| `de-gra-l0-003` | **Split into 2** | `de-gra-l0-003a`<br>`de-gra-l0-003b` | n-Deklination masculine *-e* persons (*der Kunde*, DWDS)<br>n-Deklination foreign suffixes *-ant/-ent/-ist* (*der Student*, DWDS) |
| `de-kon-l0-003` | **Split into 3** | `de-kon-l0-003a`<br>`de-kon-l0-003b`<br>`de-kon-l0-003c` | Connector *folglich* (Pos 1 + Inversion, DWDS)<br>Connector *demnach* (Pos 1 + Inversion, DWDS)<br>Connector *infolgedessen* (Pos 1 + Inversion, DWDS) |

### Card Counts Summary by Ladder

| Ladder | Total Cards | Level 0 Cards (Foundational) | Levels 1–5 Cards |
| :--- | :---: | :---: | :---: |
| `air-quality` | 14 | 2 | 12 |
| `de-grammatik` | 20 | 8 | 12 |
| `de-konnektoren` | 17 | 5 | 12 |
| `de-wortschatz` | 15 | 3 | 12 |
| `neural-processes` | 15 | 3 | 12 |
| `own-work` | 20 | 8 | 12 |
| `pytorch` | 19 | 7 | 12 |
| `uncertainty` | 17 | 5 | 12 |
| **Total System** | **137** | **41** | **96** |

---

## 3. Real Gate Outputs

### Gate 1: Unit Test Suite (`pytest trainer/tests -q`)
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 26 items

trainer\tests\test_engine.py ..........................                  [100%]

============================= 26 passed in 0.63s ==============================
```

### Gate 2: Static Content & Boundary Verification (`python trainer/verify_cards.py`)
```
=================================================================
Verifying Knowledge Trainer Content Ladders & Boundaries...
=================================================================
Loaded 5 authoritative forbidden claim boundaries from 06_do_not_claim.md.

[PASS] All content, grounding, and constraint gates passed!

Card Counts by Ladder:
  - air_quality: 14 cards (Level 0: 2)
  - de-grammatik: 20 cards (Level 0: 8)
  - de-konnektoren: 17 cards (Level 0: 5)
  - de-wortschatz: 15 cards (Level 0: 3)
  - neural_processes: 15 cards (Level 0: 3)
  - own_work: 20 cards (Level 0: 8)
  - pytorch: 19 cards (Level 0: 7)
  - uncertainty: 17 cards (Level 0: 5)

Total verified cards: 137
Total repo citations: 103
Total URL citations:  148
=================================================================
```

### Gate 3: Live URL Resolution (`python trainer/verify_cards.py --check-urls`)
```
=================================================================
Verifying Knowledge Trainer Content Ladders & Boundaries...
=================================================================

Resolving 81 unique external URLs in parallel...
Loaded 5 authoritative forbidden claim boundaries from 06_do_not_claim.md.

[PASS] All content, grounding, and constraint gates passed!

Card Counts by Ladder:
  - air_quality: 14 cards (Level 0: 2)
  - de-grammatik: 20 cards (Level 0: 8)
  - de-konnektoren: 17 cards (Level 0: 5)
  - de-wortschatz: 15 cards (Level 0: 3)
  - neural_processes: 15 cards (Level 0: 3)
  - own_work: 20 cards (Level 0: 8)
  - pytorch: 19 cards (Level 0: 7)
  - uncertainty: 17 cards (Level 0: 5)

Total verified cards: 137
Total repo citations: 103
Total URL citations:  148
All 81 external URLs successfully resolved!
=================================================================
```

### Gate 4: Working Tree Status (`git status`)
```
On branch windows-dev
Your branch is ahead of 'origin/windows-dev' by 33 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
	modified:   trainer/app.py
	modified:   trainer/content/ladders/de-grammatik.json
	modified:   trainer/content/ladders/de-konnektoren.json
	modified:   trainer/content/ladders/neural_processes.json
	modified:   trainer/content/ladders/own_work.json
	modified:   trainer/content/ladders/pytorch.json
	modified:   trainer/content/ladders/uncertainty.json
	modified:   trainer/engine.py
	modified:   trainer/tests/test_engine.py
```

---

## 4. Anti-Repetition & Mutation Proofs

### Mutation Test Proof (Recency Filter)
- **Check:** Tested behavior when omitting the recency filter and drawing 20 cards from a pool of 30 cards.
- **Result:** Without the recency filter, duplicate card draws occur frequently within short sliding windows:
  `Mutation Proof: Without recency filter, duplicate ['card-16', 'card-15', 'card-12', 'card-29', 'card-25', 'card-26', 'card-09', 'card-15'] observed in 8-window.`
  With the recency filter active, `test_no_card_repeats_within_recency_window` confirms 0 duplicates across all sliding 8-card windows.

---

## 5. Live Measurement & Simulation Outputs

### Live Progress Measurement (Before vs After)
```
=================================================================
LIVE PROGRESS MEASUREMENT
=================================================================
Total cards in repo: 137
Cards with history in progress.json: 34
Selectable right now: 29 of 137 (was 16)
Unseen among selectable: 24 (was 7)
=================================================================
```

### 30-Draw Real Sequence Demonstration
```
=================================================================
30-DRAW SEQUENCE (SHOWING WINDOW-OF-8 ANTI-REPETITION)
=================================================================
30-Draw Card Sequence:
   1. de-wor-l0-001
   2. de-gra-l0-001c
   3. de-gra-l0-gen
   4. de-kon-l0-003a
   5. de-kon-l0-003b
   6. de-wor-l0-002
   7. de-gra-l0-001b
   8. own-l0-004
   9. de-wor-l0-003
  10. unc-l0-005
  11. de-gra-l0-001a
  12. own-l0-008
  13. unc-l0-003
  14. de-kon-l0-003b
  15. de-gra-l0-001d
  16. de-kon-l0-001
  17. own-l0-003
  18. own-l0-005
  19. de-gra-l0-003b
  20. de-gra-l0-gen
  21. de-gra-l0-003a
  22. de-kon-l0-003c
  23. de-kon-l0-003a
  24. np-l0-001
  25. own-l0-007
  26. own-l0-006
  27. de-kon-l0-003b
  28. unc-l0-003
  29. de-gra-l0-001b
  30. de-gra-l0-001a

Window-of-8 Duplication Violations: 0 (0 expected)
=================================================================
```

### 400-Draw Full Simulation
```
=================================================================
400-DRAW SIMULATION AGAINST LIVE PROGRESS
=================================================================
Total draws simulated: 400

Draws and Final Status by Ladder:
  - air-quality       :  49 draws | Active Level: 5 | Final Rating: 1589.3 | Total Cards: 14
  - de-grammatik      :  61 draws | Active Level: 5 | Final Rating: 1686.5 | Total Cards: 20
  - de-konnektoren    :  50 draws | Active Level: 5 | Final Rating: 1653.5 | Total Cards: 17
  - de-wortschatz     :  45 draws | Active Level: 5 | Final Rating: 1634.0 | Total Cards: 15
  - neural-processes  :  45 draws | Active Level: 5 | Final Rating: 1518.0 | Total Cards: 15
  - own-work          :  53 draws | Active Level: 5 | Final Rating: 1512.0 | Total Cards: 20
  - pytorch           :  44 draws | Active Level: 5 | Final Rating: 1502.5 | Total Cards: 19
  - uncertainty       :  53 draws | Active Level: 5 | Final Rating: 1595.7 | Total Cards: 17

Draws by Level:
  - Level 0:  73 draws
  - Level 1:  44 draws
  - Level 2:  65 draws
  - Level 3: 128 draws
  - Level 4:  59 draws
  - Level 5:  31 draws
=================================================================
```

---

## 6. Required Reflection

> **"If exactly one thing in this delivery is still wrong, what is it most likely to be, and did I check it?"**

- **Honest Candidate:** Edge cases in prerequisite unlocking for Level 1 cards when previous Level 0 cards were split into multiple atomic items.
- **Specific Checks Executed:**
  - When `de-gra-l0-001` was split into `de-gra-l0-gen`, `de-gra-l0-001a`, `de-gra-l0-001b`, `de-gra-l0-001c`, and `de-gra-l0-001d`, all Level 1 and Level 3 cards in `de-grammatik.json` (such as `de-gra-l1-001`, `de-gra-l1-002`, `de-gra-l1-003`, `de-gra-l3-001`) that originally required `de-gra-l0-001` were inspected and updated to point to `de-gra-l0-001a`.
  - In `de-konnektoren.json`, `de-kon-l1-002` was updated from requiring `de-kon-l0-003` to `de-kon-l0-003a`.
  - `trainer/verify_cards.py` rigorously validates every single `requires` entry across all ladders, confirming that all prerequisite IDs exist and strictly reference cards of lower level ($< L$).
  - Verified against the live server that newly unlocked Level 0 cards are immediately accessible and served in the user's active session.

---

## 7. Active Status Update

The brief [`agents/briefs/2026-08-21_trainer-atomic-cards.md`](file:///C:/Users/Admin/Documents/chess_speak_out_loud/agents/briefs/2026-08-21_trainer-atomic-cards.md) is complete and delivered.
[`agents/ACTIVE.md`](file:///C:/Users/Admin/Documents/chess_speak_out_loud/agents/ACTIVE.md) has been updated to reflect the completed delivery.
