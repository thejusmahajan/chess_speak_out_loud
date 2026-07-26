# TASK FOR GEMINI — Sprint 1 Phase B: approve gate + severity-blended deck from Usual Suspects

Turn approved "usual suspects" (Phase A, `backend/training/usual_suspects.py`) into a persisted,
**severity-weighted-blended** drill deck that rides the EXISTING drill/SRS/DrillMode rails. Backend
only. Full suite stays green. No push. STOP for leader review. Report `SPRINT1_PHASE_B_REPORT.md`.

## Reuse — DO NOT rebuild (all verified present)
- `usual_suspects.usual_suspects(profile)` → `[{theme, games, occurrences, mean_severity,
  rank_score, severity_label, finding_ids}]` (Phase A). `finding_severity(f)` also exported.
- `drills.generate_drill_set` (drills.py) — the **own_game finding→drill construction (lines
  ~110–163)** reads `store.EpdCache("policy")` + `store.EpdCache("stage_b")` (NO live engine) and
  builds the drill dict (`id, source, fen, solution_uci, line_uci, alt_solution_ucis, solution_san,
  tags, difficulty, origin.finding_id, reveal{...}`). Reuse this.
- `store.save_drill_set(ds)` / `load_drill_set(id)` / `list_drill_sets()` — persistence; a saved set
  "flows through the existing DrillMode + Review/SRS queues" (see the repertoire route as the pattern).
- `attempts.record_attempt` + `/api/training/drills/attempt` — SRS by drill id. **No SRS changes.**
- Frontend: none this phase (Phase C).

## Build
### 1. Approve gate (persist the user's chosen themes)
- `POST /api/training/usual-suspects/approve`  body `{"themes": ["sacrifice", ...]}` → validate each
  against the current `usual_suspects(profile)` theme set (**reject unknown themes with 400**), store
  to `training/approved_suspects.json` (`{"themes": [...], "updated": iso}`) via `store._write_json_atomic`.
- `GET /api/training/usual-suspects/approved` → the stored approval (or `{"themes": []}`).

### 2. Deck builder — `POST /api/training/usual-suspects/deck`  body `{"count": 20}`
- Load profile → `sus = usual_suspects(profile)` → keep only suspects whose `theme` ∈ approved.
- If none approved / no suspects: return `{"drills": [], ...}` gracefully (no 500).
- **LEADER-PINNED blending (implement verbatim):**
  - `total = Σ rank_score` over kept suspects. For each kept suspect `T`:
    `slots(T) = max(1, round(count * rank_score(T) / total))`  (every approved theme gets ≥1 slot;
    the #1 theme gets the most — this IS the "severity-weighted blend").
  - Adjust rounding drift: if `Σ slots(T) != count`, add/remove single slots from the HIGHEST-
    `rank_score` themes until it equals `count`.
  - For each `T` (highest rank_score first): take its findings (map `finding_ids` → finding objects
    from the profile), sort by `finding_severity(f)` **descending**, and build up to `slots(T)` drills
    via the reused finding→drill construction; **dedupe by board EPD across the WHOLE deck** (skip a
    finding whose EPD already appears). If `T` is exhausted before its slots fill, carry its leftover
    slots forward to the remaining themes (largest rank_score first).
  - Tag each drill with its suspect theme (add `"suspect_theme": T` to the drill and/or its `tags`) so
    Phase C can show which weakness it trains. Keep `origin.finding_id` intact.
- Assemble `drill_set = {"id": "suspects-"+uuid8, "label": "Usual Suspects", "source":
  "usual_suspects", "created": iso, "themes": [approved...], "drills": [...]}`, `store.save_drill_set(it)`,
  return it. It must be loadable via `load_drill_set` and appear in `list_drill_sets` so DrillMode +
  `/api/training/drills/{set_id}` + the attempt/SRS route work UNCHANGED.

## Constraints
- If you extract the finding→drill code into a helper (e.g. `_finding_to_drill(f, source)`) to reuse
  it, the refactor MUST be **behavior-preserving** — `generate_drill_set`'s existing output and its
  tests stay identical/green. If a clean extraction is risky, write a small dedicated builder that
  produces the SAME drill dict shape instead (don't let the two diverge). State which you chose.
- Do NOT touch `metrics.py` (leader-owned) or the Phase A math. Match all schemas exactly.
- **Tests** (`backend/tests/test_suspects_deck.py`), mutation-check mindset — each fails if its rule breaks:
  1. approve persists; unknown theme → 400.
  2. blending: given two approved themes with rank_score 3000 vs 1000 and count=8, the higher gets
     strictly MORE slots (hand-compute the expected split).
  3. every deck drill's `origin.finding_id` belongs to an approved theme's `finding_ids`.
  4. EPD dedupe: no two drills share a board EPD.
  5. deck size == count (after drift adjustment) when enough findings exist; ≤ count when a theme is thin.
  6. the built set is retrievable via `load_drill_set(id)` and listed by `list_drill_sets`.
  7. empty approval → `{"drills": []}`, no error.
- **Gate:** `python -m pytest backend/tests` stays green (156 + your new tests). No push. STOP.
