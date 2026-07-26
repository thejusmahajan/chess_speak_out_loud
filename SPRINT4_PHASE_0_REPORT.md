# Sprint 4 Phase 0 Report — ECO Backfill (Backend)

## Executive Summary
Sprint 4 Phase 0 (ECO Backfill) is complete and verified. The backfill module (`backend/training/eco_backfill.py`) enables resolving `'???'` ECO codes in existing profiles directly against the user's corpus PGN without requiring a Kaggle GPU re-run.

This un-cripples the existing repertoire engine (`select_repertoire.py`) and paves the way for Phase A (Sharpness analysis & dynamic opening recommendations).

---

## Implemented Components

### 1. Backfill Module ([backend/training/eco_backfill.py](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/eco_backfill.py))
- `parse_game_idx_from_id(item_id: str) -> Optional[int]`: Extracts game index from finding IDs (`g001-p020`, `s-001-p020`).
- `backfill_ecos(profile: dict, pgn_path: str) -> Tuple[dict, dict]`:
  - Replicates diagnostic game selection: filters games containing `"derdiedasdie"` (case-insensitive) up to `games_analyzed`.
  - Classifies position openings by ply using `openings.classify(uci_moves[:ply])`.
  - **Alignment Verification**: Compares finding game headers (`white`, `black`) against PGN game headers. On index discrepancy, performs header fallback matching and reports discrepancies.
  - **Regrouped Aggregates**: Rebuilds `aggregates.by_opening` with real ECO codes, move counts (`moves`, `moves_white`, `moves_black`), missed/blind counts, and calculated `blind_rate`.

### 2. API Endpoint ([backend/app.py](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/app.py))
- `POST /api/training/openings/backfill-ecos`:
  - Loads profile from store.
  - Determines corpus path via `_corpus_pgn()`.
  - Executes `eco_backfill.backfill_ecos(profile, pgn_path)`.
  - Saves updated profile.
  - Returns `{openings: [{eco, name, count}...], unresolved: n, discrepancies: m}`.

### 3. Test Suite ([backend/tests/test_eco_backfill.py](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/tests/test_eco_backfill.py))
- `test_eco_backfill_resolves_ecos_and_regroups_aggregates`: Verifies findings and steer_findings receive real ECOs and `by_opening` regroups.
- `test_alignment_mismatch_fallback_search`: Verifies index mismatch triggers header search and reports discrepancy.
- `test_unclassifiable_opening_remains_unknown`: Verifies unclassifiable positions remain `'???'` gracefully.
- `test_backfill_ecos_api_endpoint`: Verifies full FastAPI endpoint integration and profile saving.

---

## Verification Results

| Test Target | Command | Result | Status |
| :--- | :--- | :--- | :--- |
| **ECO Backfill Unit Tests** | `python -m pytest backend/tests/test_eco_backfill.py` | **4 / 4 PASSED** | **VERIFIED** |
| **Full Backend Test Suite** | `python -m pytest backend/tests` | **187 / 187 PASSED** (5 skipped) | **VERIFIED** |

---

## Gate Checklist
- [x] Reused `openings.classify`; did NOT touch `metrics.py`.
- [x] Full test suite green (187 passed).
- [x] No Git push performed.
- [x] **STOP for Leader Review.** Leader will run backfill on the real 100-game profile before Phase A.
