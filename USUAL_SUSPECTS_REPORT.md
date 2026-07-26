# Phase A Report — "Usual Suspects" Recurring Weakness Detection

## Summary of Implementation
Phase A of Sprint 1 ("Usual Suspects") has been built strictly following the Leader-Pinned Math specification without altering `backend/training/metrics.py`.

### 1. Core Module (`backend/training/usual_suspects.py`)
Created pure module implementing recurring tactical theme clustering and rank scoring:
- **Constants**:
  - `GENERIC_MOTIFS = {"advantage", "veryLong", "quietMove"}`
  - `SEVERITY_CAP = 800.0`
  - `UNCONFIRMED_WEIGHT = 0.5`
  - `MIN_GAMES_FLOOR = 2`
  - `HIGH_SEVERITY_THRESHOLD = 400.0`
  - `MEDIUM_SEVERITY_THRESHOLD = 150.0`
- **Functions**:
  - `game_key(f)`: Extracts game key prefix (e.g. `"g014"` from `"g014-p026"`).
  - `finding_severity(f)`: Computes `min(swing_cp, 800) * (1.0 if confirmed else 0.5)`.
  - `severity_label(mean_sev)`: Maps mean severity to `"high"`, `"medium"`, or `"low"`.
  - `usual_suspects(profile)`: Performs theme clustering, game floor filtering (`games >= 2`), metric calculation (`rank_score = games * mean_severity`), and descending sort by `rank_score`. Includes a `# TODO` marking opening grouping as deferred until the ECO fix.
  - `get_broad_aggregates(profile)`: Extracts and surfaces `by_phase` and `by_concept` from profile aggregates.

### 2. API Endpoint (`backend/app.py`)
Added `@app.get("/api/training/usual-suspects")`:
- Loads profile via `store.load_profile()`.
- Returns `HTTP 404` (`{"detail": "Profile not found"}`) if no profile exists.
- Returns JSON matching output schema: `{"suspects": [...], "by_phase": [...], "by_concept": [...]}`.

### 3. Test Verification (`backend/tests/test_usual_suspects.py`)
Created comprehensive test suite covering all 6 mutation-check requirements + API route:
1. Theme in 3 games clusters with `games == 3`, while single-game themes are excluded by the floor (`games >= 2`).
2. Exact hand-computed math verification: `rank_score == games * mean_severity`.
3. Excludes `GENERIC_MOTIFS` (`"advantage"`, `"veryLong"`, `"quietMove"`) from suspect themes.
4. Weighs unconfirmed findings at 0.5x and caps swing_cp at 800.
5. Descending sort order by `rank_score`.
6. Handles empty profiles and non-qualifying profiles gracefully.
7. API route testing for 404 and 200 responses.

## Test Results
- `backend/tests/test_usual_suspects.py`: **7 passed**
- Full backend suite (`python -m pytest backend/tests`): **156 passed** (149 original + 7 new).

## Schema & Specification Notes
- **Finding Schema Compatibility**: Verified against `profile.json` structure (`id`, `motifs`, `severity`, `confirmation.swing_cp`, `confirmation.confirmed`, `opening.eco`, `game`, `fen_before`).
- **Opening Grouping**: Explicitly deferred as requested; labelled with `# TODO: Opening grouping DEFERRED until ECO fix ships`.
- **Zero Schema Ambiguities Hit**: All fields match the pinned specification verbatim.
