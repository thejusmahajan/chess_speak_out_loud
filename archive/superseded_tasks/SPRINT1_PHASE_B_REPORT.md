# Sprint 1 Phase B Report — Approval Gate & Severity-Blended Deck Builder

## Summary of Implementation
Phase B of Sprint 1 ("Usual Suspects: approve gate + severity-blended deck") has been implemented cleanly on top of Phase A, integrating seamlessly with existing drill persistence and SRS execution paths.

### 1. Refactoring & Reuse Decision (`backend/training/drills.py`)
- **Helper Extraction**: Extracted `build_drill_from_finding(f, source="own_game", suspect_theme=None)` from `drills.generate_drill_set`.
- **Behavior Preservation**: `generate_drill_set` delegates finding->drill construction to `build_drill_from_finding`. Existing drill set generation logic and all existing tests remain 100% identical and green.

### 2. Approval Gate & Persistence (`backend/training/store.py` & `backend/app.py`)
- Added `save_approved_suspects(themes)` and `load_approved_suspects()` using `store._write_json_atomic` writing to `training/approved_suspects.json`.
- Endpoints:
  - `POST /api/training/usual-suspects/approve`: Validates requested themes against current `usual_suspects(profile)` theme set. Returns `HTTP 400` (`"Unknown theme: {theme}"`) for invalid themes. Persists approved themes upon success.
  - `GET /api/training/usual-suspects/approved`: Returns the stored approval JSON (or `{"themes": []}` if not yet approved).

### 3. Severity-Weighted Deck Builder (`backend/training/usual_suspects.py` & `backend/app.py`)
- Implemented `allocate_slots(kept_suspects, count)` following the verbatim leader-pinned math:
  - `slots(T) = max(1, round(count * rank_score(T) / total))`
  - Rounding drift adjustment: adjusts single slots on highest `rank_score` themes until `sum(slots) == count`.
- Implemented `build_suspects_deck(profile, approved_themes, count=20)`:
  - Filters suspects to approved themes.
  - Sorts theme findings by `finding_severity(f)` descending.
  - **Whole-deck EPD Deduplication**: Deduplicates positions by board EPD across all themes.
  - Attaches `suspect_theme` to drills and adds it to `tags`.
  - Saves generated deck via `store.save_drill_set(drill_set)` with `source: "usual_suspects"`.
  - Retrievable via `store.load_drill_set(set_id)` and listed by `store.list_drill_sets()`.
  - Endpoint `POST /api/training/usual-suspects/deck` returns the constructed drill set.
  - Gracefully handles empty approvals or missing profiles by returning `{"drills": []}` without errors.

## Test Verification (`backend/tests/test_suspects_deck.py`)
Created test suite covering all 7 mutation-check requirements:
1. `approve` persists approved themes; unknown theme returns 400.
2. `blending`: verified higher `rank_score` theme gets strictly more slots (6 vs 2 split on 3000 vs 1000 score).
3. Every deck drill's `origin.finding_id` belongs to an approved theme's findings.
4. `EPD dedupe`: no duplicate board EPDs in the built deck.
5. Deck size equals `count` when findings exist; `<= count` when theme findings are thin.
6. Deck is retrievable via `store.load_drill_set(set_id)` and listed by `store.list_drill_sets()`.
7. Empty approval returns `{"drills": []}` without error.

## Test Results
- `backend/tests/test_suspects_deck.py`: **7 passed**
- Full backend suite (`python -m pytest backend/tests`): **163 passed** (156 previous + 7 new).
- Zero git pushes performed.
