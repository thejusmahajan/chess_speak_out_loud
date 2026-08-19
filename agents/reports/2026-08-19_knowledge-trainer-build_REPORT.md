# Knowledge Trainer Build Report

**Brief-ID:** `2026-08-19_knowledge-trainer-build`  
**Date:** 2026-08-19  
**Target Repo:** `chess_speak_out_loud`  
**Author:** Antigravity Worker (Gemini 3.7 Flash)  
**Status:** DELIVERED  

---

## 1. Executive Summary & Accomplishments

The **Knowledge Trainer** has been built from scratch as an independent, zero-build-step spaced-repetition application (`trainer/`) in accordance with all pinned specifications in Brief `2026-08-19_knowledge-trainer-build.md` and the standing contract in `agents/README.md`.

- **Pure-Function Engine (`trainer/engine.py`):** Implements exact Elo rating updates ($K=24$ user, $K=8$ card), SM-2 spaced repetition with interval progression $1 \rightarrow 6 \rightarrow 6 \cdot \text{ease}$, ease clamping $[1.3, 2.8]$, prerequisite gating (unlocked only when requirements scored 1.0 at least once), and dynamic rating-window candidate selection.
- **Content Verification Gate (`trainer/verify_cards.py`):** 6-layer validation gate enforcing non-empty sources, physical existence of cited repo paths, unique IDs, strictly lower-level prerequisite dependencies, presence of Level-5 capstone interview answers, and case-insensitive screening against forbidden claims from `06_do_not_claim.md`.
- **Authored Content Ladders (`trainer/content/ladders/*.json`):** 60 grounded cards across 5 ladders (12 cards each): `pytorch`, `uncertainty`, `neural-processes`, `air-quality`, and `own-work`.
- **FastAPI Server & Single-Page UI (`trainer/app.py`, `trainer/static/index.html`):** Clean, dark-mode web application running on port 8010 with live stats, Level 1–5 badges, question reveal, 3-tier grading (1.0/0.5/0.0), keyboard shortcuts (Space, 1, 2, 3), and the required Leader Feedback Channel (`state/comments.jsonl`).
- **Disk-Based Persistence:** All state is saved to plain JSON/JSONL (`state/progress.json`, `state/answers.jsonl`, `state/comments.jsonl`).
- **Isolation Invariant:** No existing project files (`backend/`, `frontend/`, `data/`, `docs/`, `agents/`) were modified.

---

## 2. Gate Verification & Live Test Results

### Gate 1: Unit Test Suite (`pytest trainer/tests -v`)
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\miniconda3\envs\cszero\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collecting ... collected 9 items

trainer/tests/test_engine.py::test_elo_harder_card_yields_higher_gain PASSED [ 11%]
trainer/tests/test_engine.py::test_elo_proportional_zero_sum PASSED      [ 22%]
trainer/tests/test_engine.py::test_sm2_three_consecutive_got_it PASSED   [ 33%]
trainer/tests/test_engine.py::test_sm2_missed_resets_reps_and_interval PASSED [ 44%]
trainer/tests/test_engine.py::test_sm2_ease_clamping PASSED              [ 55%]
trainer/tests/test_engine.py::test_prerequisite_gating PASSED            [ 66%]
trainer/tests/test_engine.py::test_selection_rating_window_widening PASSED [ 77%]
trainer/tests/test_engine.py::test_verify_cards_fails_on_missing_sources PASSED [ 88%]
trainer/tests/test_engine.py::test_verify_cards_fails_on_level_inversion_or_cycle PASSED [100%]

============================== 9 passed in 0.37s ==============================
```

### Gate 2: Content Gate Verification (`trainer/verify_cards.py`)
```
============================================================
Verifying Knowledge Trainer Content Ladders...
============================================================

[PASS] All content gates passed successfully!

  - air_quality: 12 cards
  - neural_processes: 12 cards
  - own_work: 12 cards
  - pytorch: 12 cards
  - uncertainty: 12 cards

Total verified cards: 60
============================================================
```

### Gate 3: Live Server Execution & Simulated Drill Session
- **Server:** `uvicorn trainer.app:app --port 8010` (PID 9188, Status RUNNING).
- **Client & Interaction:** Evaluated via HTTP client interacting against the live server endpoints. Five cards across Levels 1–5 were answered, followed by feedback submission to the leader.

#### Pasted `trainer/state/comments.jsonl`:
```json
{"timestamp": "2026-08-19T19:50:44.320777+00:00", "card_id": "own-l5-001", "ladder": "own-work", "level": 5, "category": "answer unclear", "comment": "The distinction between side-to-move vertical reflection a8 vs 180-deg rotation h8 is crystal clear and verified against neural_vision.py.", "user_rating": 1269.79, "revealed": true}
```

#### Pasted `trainer/state/progress.json` (after 5 answers):
```json
{
  "user_rating": 1269.79,
  "cards": {
    "pyt-l1-001": {
      "rating": 978.24,
      "ease": 2.6,
      "interval_days": 1,
      "reps": 1,
      "last_seen": "2026-08-19T19:50:44.141461+00:00",
      "due_date": "2026-08-20T19:50:44.141461+00:00",
      "mastered": true,
      "history": [
        {
          "timestamp": "2026-08-19T19:50:44.141461+00:00",
          "score": 1.0,
          "user_rating": 1205.28,
          "card_rating": 978.24
        }
      ]
    },
    "pyt-l2-001": {
      "rating": 1176.29,
      "ease": 2.6,
      "interval_days": 1,
      "reps": 1,
      "last_seen": "2026-08-19T19:50:44.166521+00:00",
      "due_date": "2026-08-20T19:50:44.166521+00:00",
      "mastered": true,
      "history": [
        {
          "timestamp": "2026-08-19T19:50:44.166521+00:00",
          "score": 1.0,
          "user_rating": 1216.41,
          "card_rating": 1176.29
        }
      ]
    },
    "unc-l3-001": {
      "rating": 1457.58,
      "ease": 2.35,
      "interval_days": 1,
      "reps": 0,
      "last_seen": "2026-08-19T19:50:44.217739+00:00",
      "due_date": "2026-08-20T19:50:44.217739+00:00",
      "mastered": false,
      "history": [
        {
          "timestamp": "2026-08-19T19:50:44.217739+00:00",
          "score": 0.5,
          "user_rating": 1223.67,
          "card_rating": 1457.58
        }
      ]
    },
    "np-l4-001": {
      "rating": 1682.51,
      "ease": 2.6,
      "interval_days": 1,
      "reps": 1,
      "last_seen": "2026-08-19T19:50:44.251235+00:00",
      "due_date": "2026-08-20T19:50:44.251235+00:00",
      "mastered": true,
      "history": [
        {
          "timestamp": "2026-08-19T19:50:44.251235+00:00",
          "score": 1.0,
          "user_rating": 1246.14,
          "card_rating": 1682.51
        }
      ]
    },
    "own-l5-001": {
      "rating": 1972.12,
      "ease": 2.6,
      "interval_days": 1,
      "reps": 1,
      "last_seen": "2026-08-19T19:50:44.299252+00:00",
      "due_date": "2026-08-20T19:50:44.299252+00:00",
      "mastered": true,
      "history": [
        {
          "timestamp": "2026-08-19T19:50:44.299252+00:00",
          "score": 1.0,
          "user_rating": 1269.79,
          "card_rating": 1972.12
        }
      ]
    }
  }
}
```

---

## 3. Card Inventory & Source Breakdown

| Ladder | File | Card Count | Repo Sources | URL / DOI Sources | Level-5 Question Focus |
|---|---|:---:|:---:|:---:|---|
| **PyTorch** | `pytorch.json` | 12 | 18 | 8 | Attention extraction via forward hooks without model modifications |
| **Uncertainty** | `uncertainty.json` | 12 | 14 | 11 | Convincing a city environmental agency that model uncertainty is calibrated |
| **Neural Processes** | `neural_processes.json` | 12 | 15 | 11 | Producing high-resolution pollutant concentration fields with uncertainty from 3 sparse stations |
| **Air Quality** | `air_quality.json` | 12 | 16 | 9 | Hybrid architecture coupling CTM physics (CityChem) with a learned ConvCNP |
| **Own Work** | `own_work.json` | 12 | 17 | 6 | Diagnosing and remediating the coordinate-frame reflection and empty history planes bugs |
| **TOTAL** | — | **60** | **80** | **45** | — |

---

## 4. Cards Dropped or Modified for Lack of Sourcing

1. **Dropped Draft: "Exact CMAQ chemical mechanism comparison (CB6r3 vs SAPRC07)"**  
   - *Reason:* Required deep specific knowledge of CMAQ photochemical gas-phase ODE formulations that could not be grounded in this repository's documents or primary literature without risking hallucination. Replaced with grounded card on CTM advection-diffusion and regional/urban scale boundary interfaces (`aq-l3-001`).
2. **Modified Draft: "Activation patching on BT3 attention heads"**  
   - *Reason:* Replaced with `own-l2-003` ("Activation capture vs causal intervention") to explicitly emphasize the strict boundary between what the codebase has implemented (observational hook extraction) versus what is future causal intervention work, preventing violation of `06_do_not_claim.md`.

---

## 5. Notes & Observations on Brief Specifications

- **Browser Subagent Playwright Driver:** The automated browser subagent encountered an initialization failure because pre-compiled Playwright driver binaries were not installed on the Windows environment. Verification was executed directly against the live running server endpoints (`http://127.0.0.1:8010/`), successfully testing all UI endpoints, rating calculations, and disk logging.
- **Path Resolution for `career_strategy_conversation_aug2026.md`:** The brief mentioned `docs/career/` for career files; the file actually lives at `docs/career_strategy_conversation_aug2026.md`. Citations were resolved to its physical disk location.
- **Corrected Coordinate Frame:** All cards in `own_work.json` strictly teach the corrected transformation ($i \oplus 56$, mapping `a1` to **`a8`**, flipping rank and preserving file).

---

## 6. How to Run

```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn trainer.app:app --port 8010
```
Open `http://127.0.0.1:8010/` in any browser.
