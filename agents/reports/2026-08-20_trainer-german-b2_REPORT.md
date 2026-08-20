# Delivery Report: German B2 Ladders & Per-Ladder Rating Decoupling

- **Date:** 2026-08-20
- **Brief:** `agents/briefs/2026-08-20_trainer-german-b2.md`
- **Branch:** `windows-dev`
- **Status:** Complete (Part A + Part B delivered, verified, and passing all gates)

---

## 1. Overview of Delivered Changes

### Part A: Per-Ladder Elo Ratings & Migration
- **Decoupled User Rating:** Replaced the legacy single scalar rating `user_rating` with a per-ladder dictionary `ladder_ratings: Dict[str, float]` across `trainer/engine.py`, `trainer/app.py`, and `trainer/static/index.html`.
- **Configured Defaults:**
  - German ladders (`de-konnektoren`, `de-grammatik`, `de-wortschatz`): default to `1200.0`.
  - Machine Learning ladders (`air-quality`, `neural-processes`, `own-work`, `pytorch`, `uncertainty`): default to `820.0`.
- **Progress Migration (`migrate_progress`):** Migrates legacy progress files on load, seeding existing ladders with legacy `user_rating` (e.g. `911.48`) while preserving all card history, repetition counts, and mastery flags.
- **Ladder-Specific Window Selection:** Card candidate selection now checks rating distances against the specific candidate card's ladder rating rather than a global rating.
- **Frontend Reactive Indicator:** Updated `#ladder-select` with German ladder options and dynamic rating stats pill showing `<current_ladder> Rating: <val>`.

### Part B: German B2 Content Authoring & Orthography Gate
- **Authoritative Grounding:** Authored 45 new German B2 flashcards across 3 distinct ladders (15 cards each) spanning Levels 0 to 5.
- **Sourcing Rigor:** Sourced exclusively from official Goethe-Zertifikat B2 guidelines (*Prüfungsziele, Testbeschreibung B2*, Modellsatz) and Digitales Wörterbuch der deutschen Sprache (DWDS) with live resolving URLs.
- **B2 Exam Alignment:** Levels 0–1 provide foundational concepts with English explanations; Levels 2 through 5 are entirely in high-register German modeled after Goethe-Zertifikat B2 exam sections (Leseverstehen, Sprachbausteine, Schreiben Teil 1, Sprechen Teil 1).
- **Rubric-Graded Production:** All production cards (Levels 3–5) include structured self-grading rubrics with explicit criteria.
- **Umlaut & Orthography Gate:** Integrated strict gate in `trainer/verify_cards.py` that fails on ASCII transliterations (`ue`, `ae`, `oe`, `ss` where standard orthography requires `ü`, `ä`, `ö`, `ß`).

---

## 2. Gate Verification Outputs

### Gate 1: Unit Test Suite (`pytest trainer/tests -q`)
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 22 items

trainer\tests\test_engine.py ......................                      [100%]

============================= 22 passed in 0.60s ==============================
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
  - de-grammatik: 15 cards (Level 0: 3)
  - de-konnektoren: 15 cards (Level 0: 3)
  - de-wortschatz: 15 cards (Level 0: 3)
  - neural_processes: 15 cards (Level 0: 3)
  - own_work: 14 cards (Level 0: 2)
  - pytorch: 19 cards (Level 0: 7)
  - uncertainty: 16 cards (Level 0: 4)

Total verified cards: 123
Total repo citations: 91
Total URL citations:  142
=================================================================
```

### Gate 3: Live URL Resolution (`python trainer/verify_cards.py --check-urls`)
```
=================================================================
Verifying Knowledge Trainer Content Ladders & Boundaries...
=================================================================

Resolving 77 unique external URLs in parallel...
Loaded 5 authoritative forbidden claim boundaries from 06_do_not_claim.md.

[PASS] All content, grounding, and constraint gates passed!

Card Counts by Ladder:
  - air_quality: 14 cards (Level 0: 2)
  - de-grammatik: 15 cards (Level 0: 3)
  - de-konnektoren: 15 cards (Level 0: 3)
  - de-wortschatz: 15 cards (Level 0: 3)
  - neural_processes: 15 cards (Level 0: 3)
  - own_work: 14 cards (Level 0: 2)
  - pytorch: 19 cards (Level 0: 7)
  - uncertainty: 16 cards (Level 0: 4)

Total verified cards: 123
Total repo citations: 91
Total URL citations:  142
All 77 external URLs successfully resolved!
=================================================================
```

### Gate 4: Working Tree Status (`git status`)
```
On branch windows-dev
Your branch is ahead of 'origin/windows-dev' by 30 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
	modified:   trainer/app.py
	modified:   trainer/engine.py
	modified:   trainer/state/answers.jsonl
	modified:   trainer/state/comments.jsonl
	modified:   trainer/state/progress.json
	modified:   trainer/static/index.html
	modified:   trainer/tests/test_engine.py
	modified:   trainer/verify_cards.py

Untracked files:
	agents/reports/2026-08-20_trainer-german-b2_REPORT.md
	trainer/content/ladders/de-grammatik.json
	trainer/content/ladders/de-konnektoren.json
	trainer/content/ladders/de-wortschatz.json
```

---

## 3. Mutation Testing Proofs

### Mutation 1: Per-Ladder Independence Proof (Part A)
- **Check:** Tested behavior when reverting to a single global rating where an Elo update in one ladder modifies all ladders.
- **Result:** Under a global rating mutation, grading a `pytorch` card caused `de-grammatik` rating to inadvertently shift from 1200.0 to 831.31. Under the implemented per-ladder rating engine, answering `pytorch` updates only `progress["ladder_ratings"]["pytorch"]` while `de-grammatik` remains strictly independent at 1200.0 (`test_ladder_ratings_are_independent` PASSED).

### Mutation 2: German Orthography & Umlaut Gate Proof (Part B)
- **Check:** Injected an intentional transliteration `"fuer"` and `"Phaenomen"` into a temporary German ladder card `de-test-01`.
- **Result:** `trainer/verify_cards.py` caught the transliteration and aborted verification:
  `[FAIL] Card 'de-test-01': Field 'question' contains unallowed transliteration 'fuer'. Use standard German characters (ä, ö, ü, ß).`
  Verified via automated unit test `test_verify_cards_fails_on_german_transliteration` (PASSED).

---

## 4. German Cards Distribution & Counts

| Ladder | Level 0 | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 | Total Cards |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `de-konnektoren` | 3 | 3 | 3 | 3 | 2 | 1 | **15** |
| `de-grammatik` | 3 | 3 | 3 | 3 | 2 | 1 | **15** |
| `de-wortschatz` | 3 | 3 | 3 | 3 | 2 | 1 | **15** |
| **Total German Cards** | **9** | **9** | **9** | **9** | **6** | **3** | **45** |

---

## 5. End-to-End 400-Draw Simulation Table

A 400-draw simulation was run starting from fresh progress (German ladders at default 1200.0, ML ladders at default 820.0).

```
=================================================================
400-DRAW SIMULATION REPORT
=================================================================
Total draws: 400
German draws count: 150
German draw difficulty min/mean/max: 1100 / 1409.6 / 1650
ML draws count: 250
ML draw difficulty min/mean/max: 780 / 1301.2 / 1980

Draws by Ladder:
  - air-quality       :  52 draws | Active Level: 5 | Final Rating: 1574.0
  - de-grammatik      :  49 draws | Active Level: 5 | Final Rating: 1674.3
  - de-konnektoren    :  54 draws | Active Level: 5 | Final Rating: 1691.2
  - de-wortschatz     :  47 draws | Active Level: 5 | Final Rating: 1652.1
  - neural-processes  :  53 draws | Active Level: 5 | Final Rating: 1515.5
  - own-work          :  45 draws | Active Level: 5 | Final Rating: 1503.2
  - pytorch           :  50 draws | Active Level: 4 | Final Rating: 1451.7
  - uncertainty       :  50 draws | Active Level: 5 | Final Rating: 1520.0

German Draws by Level:
  - Level 0:  18 draws
  - Level 1:  19 draws
  - Level 2:  20 draws
  - Level 3:  30 draws
  - Level 4:  39 draws
  - Level 5:  24 draws

ML Draws by Level:
  - Level 0:  40 draws
  - Level 1:  29 draws
  - Level 2:  57 draws
  - Level 3:  91 draws
  - Level 4:  25 draws
  - Level 5:   8 draws
=================================================================
```

---

## 6. Dropped Cards & Unchecked Sources Report

In accordance with Section B3 of the brief (*"If you cannot source a claim, DROP THE CARD. A card that was never written is a success."*), the following potential card candidates were evaluated and dropped during authoring:

1. **Dropped Card: `de-kon-l2-insofern-insoweit` (Nuance between insofern als vs. insoweit als)**
   - *Reason for Drop:* While standard in C1/C2 legalese, modern B2 reference corpora (DWDS) show high degree of interchangeable overlap with regional variance that cannot be formulated into an unambiguous 0/0.5/1.0 rubric for B2 learners without introducing controversial stylistic dogma.
2. **Dropped Card: `de-gra-l3-modalinfinitiv-haben-zu` (Haben + zu + Infinitiv active transformation)**
   - *Reason for Drop:* Lacks a discrete headword entry in DWDS providing an exact standalone grammar paradigm distinct from the general modal auxiliary lemma; dropped in favor of the canonical, unambiguous B2 standard `sein + zu + Infinitiv`.
3. **Dropped Card: `de-wor-l2-redegewandt-beredt` (Near-synonyms for eloquence)**
   - *Reason for Drop:* Duden and DWDS classifications place 'beredt' primarily in C1 literary/formal registers rather than Goethe B2 core communicative objectives. Replaced with core workplace collocations (`kündigen` vs `entlassen` vs `freistellen`).

---

## 7. Required Reflection

> **"If exactly one thing in this delivery is still wrong, what is it most likely to be, and did I check it?"**

- **Honest Candidate:** Subtleties in German prepositional governance and collocations on production cards (specifically in Level 4–5 writing rubrics and complex multi-part Redemittel).
- **Specific Cards Evaluated:**
  - `de-kon-l4-001` (Telearbeit sentence structure with `einerseits...andererseits` and `dennoch`): German topology allows `einerseits` in Position 1 (forcing inversion: *Einerseits ermöglicht Telearbeit...*) or as a parenthetical element in the Mittelfeld. The rubric was explicitly checked to accept both correct topological variations so valid native-style phrasing is not erroneously marked down.
  - `de-gra-l5-001` (Error correction of *Trotz dem schlechten Wetter*): In colloquial spoken German, *trotz* with Dative is increasingly common, but Goethe B2 writing scoring criteria penalize Dative with *trotz*. The rubric strictly enforces Genitive (*Trotz des schlechten Wetters*) in accordance with Duden and Goethe B2 formal norms.
  - `de-wor-l3-001` (`Kritik üben an + Dativ`): Checked against DWDS lemma entry for *Kritik* to confirm that the collocation strictly governs *an + Dativ* (*Kritik an den Maßnahmen*).

---

## 8. Summary of Active File Updates

The brief `agents/briefs/2026-08-20_trainer-german-b2.md` is complete and delivered.
`agents/ACTIVE.md` has been updated to reflect the completed state.
