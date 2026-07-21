# Gemini Task — Surface multi-dimension "What to Work On" (phase + time, alongside openings)

**Model:** Gemini 3.6 Flash (high). **Token budget is not a concern.** Follow `WORKER_AGENT_COOKBOOK.md` — pinned shapes, enumerated real-guard tests, include the real/unmocked path, respect boundaries.

## Context
The leader generalized the ranking in `metrics.py` (already done + tested):
`weakness_ranking_all(profile, n) -> {"openings": [...], "phase": [...], "clock": [...]}`,
each a list of the same `DimComparison`s the T4 endpoint already serializes.
Currently only **openings** are surfaced (the T4 "What to Work On" panel). This task
extends the endpoint and the panel to ALSO show **Game Phase** (opening/middlegame/
endgame) and **Time Pressure** (fast/normal/slow), so "what to work on" spans all
three dimensions.

## Important behavioral note (this drives the UI states)
`by_phase`/`by_clock` were added to the pipeline AFTER the existing profiles were
built, so **no current profile carries them** — `weakness_ranking_all` returns
`phase: []` and `clock: []` until the user runs a **fresh diagnosis**. Your UI MUST
handle empty phase/clock sections gracefully (see requirements) — this is the common
case right now, not an edge case.

## Scope / boundaries (hard)
- **Edit** `backend/app.py` (extend the existing `weakness_ranking_ep`),
  `frontend/src/api/training.ts` (extend the return type), and
  `frontend/src/components/Training/WeaknessRanking.tsx` (render the new sections).
  Update the existing tests as needed:
  `backend/tests/test_weakness_ranking_endpoint.py` and
  `frontend/src/components/Training/__tests__/WeaknessRanking.test.tsx`.
- **Do NOT touch** `backend/training/metrics.py` (leader-owned — call
  `weakness_ranking_all`, do not modify it), the pipeline, or other modules.

## Pinned shapes (do not guess)
- `metrics.weakness_ranking_all(profile, n=6) -> {"openings": list[DimComparison],
  "phase": list[DimComparison], "clock": list[DimComparison]}`.
- `DimComparison` fields (serialize with `dataclasses.asdict` + a `kind`):
  `dim, value, count, ref_value, grade, importance`; `kind = "weakness" if grade < 0 else "strength"`.
  - `openings` `dim` = ECO ("C61"); `phase` `dim` ∈ {"opening","middlegame","endgame"};
    `clock` `dim` ∈ {"fast","normal","slow"} (fast = <60s remaining, normal = 60–180s, slow = >180s).
- **Endpoint response (ADDITIVE — keep `ranking` = openings for backward-compat):**
```json
{
  "ranking": [ { "dim": "C61", "value": 0.40, ... "kind": "weakness" } ],
  "phase":   [ { "dim": "opening", "value": 0.14, ... "kind": "weakness" } ],
  "clock":   [ { "dim": "normal", "value": 0.13, ... "kind": "weakness" } ]
}
```

## Part A — Backend (`weakness_ranking_ep` in `app.py`)
Replace the body to use `weakness_ranking_all` and serialize all three lists.
```python
def _ser(items):
    return [{**dataclasses.asdict(c), "kind": "weakness" if c.grade < 0 else "strength"} for c in items]

@app.get("/api/training/weakness-ranking")
async def weakness_ranking_ep(n: int = 6):
    from backend.training import metrics
    profile = store.load_profile()
    if not profile:
        return {"ranking": [], "phase": [], "clock": []}
    allr = metrics.weakness_ranking_all(profile, n)
    return {"ranking": _ser(allr["openings"]), "phase": _ser(allr["phase"]), "clock": _ser(allr["clock"])}
```
1. No profile → `{"ranking": [], "phase": [], "clock": []}`, HTTP 200.
2. `ranking` still carries the openings list (existing consumers unaffected).

## Part B — Frontend API (`training.ts`)
Extend `getWeaknessRanking`'s return type to add `phase` and `clock` arrays (same
item type as `ranking`). Keep the function name and `ranking` field.

## Part C — UI (`WeaknessRanking.tsx`)
Render **three labelled sections** in the "What to Work On" panel — **Openings**,
**Game Phase**, **Time Pressure** — reusing the existing ranked-item rendering for each.
1. Map `dim` to human labels: phase → capitalized ("Opening"/"Middlegame"/"Endgame");
   clock → "Under time pressure (<1 min)" / "Normal (1–3 min)" / "Plenty of time (>3 min)".
   Openings keep the raw ECO.
2. **Empty section handling (the common case for phase/clock now):** a section whose
   list is `[]` shows a small muted note ("Run a fresh diagnosis to rank by game
   phase") rather than a blank gap — and the Openings section still renders normally.
3. Preserve all existing behavior: loading, error, and the openings list exactly as
   today (weakness/strength badges, `40.0% blind`, games count).
4. No new lint warnings (helpers in their own file if you export any).

## Part D — Tests (each a REAL guard)

### Backend (`test_weakness_ranking_endpoint.py`, extend it)
Use the existing `TestClient(app)` (no `with`) + monkeypatch `store.load_profile`
pattern — these hit the REAL `weakness_ranking_all` (the required unmocked path).
1. **All three keys present.** A profile with `by_opening` + `by_phase` + `by_clock`
   → response has non-empty `ranking`, `phase`, and `clock`, each item with the full
   serialized shape incl. `kind`.
2. **`phase`/`clock` empty when absent.** A profile with only `by_opening` (no
   `by_phase`/`by_clock`) → `phase == []` and `clock == []`, `ranking` non-empty.
3. **Back-compat.** `ranking` is still the openings list (dims are ECOs), unchanged
   from before. (Keep/adapt the existing leak-first assertion.)
4. **No profile → all three empty, 200.**

### Frontend (`WeaknessRanking.test.tsx`, extend it)
Mock `getWeaknessRanking` to return `{ranking, phase, clock}`.
5. **Renders all three sections** with their items and human labels (e.g. a `phase`
   item `dim: "middlegame"` shows "Middlegame"; a `clock` item `dim: "normal"` shows
   the "Normal (1–3 min)" label).
6. **Empty phase/clock** (`phase: [], clock: []`, openings non-empty) → the openings
   section renders its items AND each empty section shows the muted "run a fresh
   diagnosis" note (not a blank).
7. **Existing openings behavior preserved** — badges, `40.0% blind`, games count
   still render for the openings section (adapt the existing tests to the new markup).
8. Loading + error states still work (keep those tests green).

## Gate — paste REAL output into `WORKLOG_TRAINING.md`
- `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests/test_weakness_ranking_endpoint.py -q` → pass.
- `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests/ -q` → full suite (≥ 128).
- From `frontend/`: `npm run build` (clean), `npm run lint` (0 errors, no new warnings), `npm run test` (all pass, count).

Prepend a dated `WORKLOG_TRAINING.md` entry ending with `multi-dim ranking UI ready for review`. Modify only the files named above + the worklog. Await leader sign-off.
