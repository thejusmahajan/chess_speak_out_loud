# TASK FOR GEMINI — Stable drill IDs + SRS-aware Usual-Suspects deck ordering (backend)

Fix two real gaps so the Usual Suspects deck REMEMBERS what the user has solved and surfaces what
he still needs: (1) finding-drills use random UUID ids → SRS can't track a position across rebuilds;
(2) `build_suspects_deck` ignores the SRS, so reopening gives the same static order regardless of
what's solved. Backend only. Full suite stays green. No push. STOP for leader review. Report
`SRS_AWARE_DECK_REPORT.md`.

## Grounded facts
- `drills.build_drill_from_finding` sets `"id": f"d-{uuid.uuid4().hex[:8]}"` (drills.py:70) — RANDOM,
  changes every build. Contrast the repertoire path which uses a STABLE id
  `_rep_drill_id(color, epd) = "rep-"+sha1(f"{color}:{epd}")[:12]` (drills.py:281–284). Mirror that.
- `attempts.py` SM-2 SRS: `load_srs() -> {drill_id: {..., next_review/interval...}}`, `due_drills(now)`,
  `record_attempt(set_id, drill, correct)`. Inspect the actual srs entry shape before using it.
- `usual_suspects.build_suspects_deck` builds `deck_drills` via `drills.build_drill_from_finding`,
  severity-blended, EPD-deduped — but does NOT look at the SRS.

## Fix 1 — Stable, deterministic drill IDs (finding-drills)
In `build_drill_from_finding`, derive the id deterministically from the finding so the SAME position
always gets the SAME drill id across rebuilds → SRS persists:
`drill_id = "d-" + hashlib.sha1(f["id"].encode("utf-8")).hexdigest()[:12]` when `f.get("id")` exists,
else fall back to an EPD-based hash. Keep the exact drill DICT otherwise identical (behavior-preserving
beyond the id). Do NOT change the repertoire or puzzle id schemes.

## Fix 2 — SRS-aware ordering in `build_suspects_deck`
After assembling the blended, deduped `deck_drills` (keep the severity/rank_score blend as the WITHIN-
group order), reorder using `attempts.load_srs()` into three groups, concatenated in this order:
1. **UNSEEN** — drill id not present in the SRS map (never attempted).
2. **DUE** — in the SRS map and due now (its `next_review`/schedule has elapsed, per the SM-2 entry
   shape — reuse `attempts.due_drills()` or read `load_srs()` directly; match the actual field).
3. **NOT-DUE** — solved and scheduled for later — placed LAST (do not drop them; the user may still
   want them, just deprioritized).
Within each group, preserve the existing severity-blended order. This makes a reopen surface
unseen+due first and push already-mastered/not-due to the end. Everything else in the deck build
(slot allocation, dedup) is unchanged.

## Constraints & gates
- Behavior-preserving except the id scheme + the new ordering. Do NOT touch `metrics.py`. Do NOT
  change `generate_drill_set`'s other paths beyond the shared helper's id.
- Update the EXISTING deck/drill tests that assumed a UUID id or a pure-severity order — adjust them to
  the new stable-id + SRS-order behavior; do NOT delete assertions, and explain each change in the report.
- **Tests** (extend `test_suspects_deck.py`), mutation-check: (1) the SAME finding yields the SAME drill
  id across two `build_drill_from_finding` calls (deterministic); (2) with a seeded SRS, an UNSEEN drill
  is ordered before a NOT-DUE (solved) drill; (3) a DUE drill is ordered before a NOT-DUE drill;
  (4) a solved-not-due drill still appears (deprioritized, not dropped).
- `python -m pytest backend/tests` stays green (183 + updated/new). No push. STOP for leader review.
