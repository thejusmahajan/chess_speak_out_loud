# SRS-Aware Usual Suspects Deck Ordering Report

## Executive Summary
This update fixes two gaps in training memory for the Usual Suspects feature:
1. **Deterministic Drill IDs**: `drills.build_drill_from_finding` now derives stable IDs (`d-` + SHA1 hash of `finding_id` or `epd`) instead of random UUIDs, enabling SM-2 SRS state persistence across rebuilds.
2. **SRS-Aware Deck Ordering**: `usual_suspects.build_suspects_deck` queries `attempts.load_srs()` and orders the severity-blended deck into **UNSEEN** -> **DUE** -> **NOT-DUE**, surfacing unattempted and due positions first while pushing solved/not-due positions to the end without dropping them.

---

## Implemented Changes

### 1. Deterministic Finding-Drill IDs ([backend/training/drills.py](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/drills.py))
- Replaced `f"d-{uuid.uuid4().hex[:8]}"` with:
  `"d-" + hashlib.sha1(str(finding_id).encode("utf-8")).hexdigest()[:12]` (or SHA1 of `epd` if `finding_id` is missing).
- Preserved all other drill object attributes and origin fields (`finding_id: f.get("id")`).

### 2. SRS-Aware Deck Ordering ([backend/training/usual_suspects.py](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/usual_suspects.py))
- Imported `attempts` module.
- After assembling the severity-blended, EPD-deduped `deck_drills`, partitioned drills into:
  - **UNSEEN**: `drill_id not in srs` (never attempted).
  - **DUE**: `srs[drill_id]["due"] <= now_iso`.
  - **NOT-DUE**: `srs[drill_id]["due"] > now_iso` (solved, scheduled for later).
- Concatenated `unseen + due + not_due`, retaining severity-blended order within each bucket.

### 3. Extended Unit Tests ([backend/tests/test_suspects_deck.py](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/tests/test_suspects_deck.py))
- `test_deterministic_drill_ids`: Verified identical findings produce identical drill IDs across calls.
- `test_srs_aware_deck_ordering`: Verified UNSEEN > NOT-DUE, DUE > NOT-DUE, and retention of NOT-DUE drills.

---

## Verification Results

| Test Target | Command | Result | Status |
| :--- | :--- | :--- | :--- |
| **Suspects Deck Tests** | `python -m pytest backend/tests/test_suspects_deck.py` | **9 / 9 PASSED** | **VERIFIED** |
| **Full Backend Test Suite** | `python -m pytest backend/tests` | **189 / 189 PASSED** (5 skipped) | **VERIFIED** |

---

## Gate Checklist
- [x] Behavior-preserving except drill ID scheme and SRS bucket ordering.
- [x] `metrics.py` untouched.
- [x] All 4 mutation checks verified by tests.
- [x] Full test suite green (189 passed).
- [x] No Git push performed.
- [x] **STOP for Leader Review.**
