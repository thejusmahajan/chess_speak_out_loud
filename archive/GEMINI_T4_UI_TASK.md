# Gemini Task — Epoch III · Track T · T4: surface the "What to Work On" ranking (endpoint + Weakness Profile UI)

**Model:** Gemini 3.6 Flash (high). **Token budget is not a concern.** Follow `WORKER_AGENT_COOKBOOK.md` — detail is the biggest lever; every test must be a REAL guard (we mutation-check them); include the required real/unmocked path.

## Context
The leader shipped a Tutor-style ranking engine in `metrics.py` (T1–T3, pure, already tested): `weakness_ranking(profile, n)` grades the user's openings by *self-relative* blindness (each ECO's blind_rate vs the user's own baseline, weighted by move count) and returns a balanced, weakness-first list. Nothing surfaces it yet. T4 = expose it via an endpoint and render a **"What to Work On"** panel in the Weakness Profile view.

## Scope / boundaries (hard)
- **Edit:** `backend/app.py` (one new endpoint), `frontend/src/api/training.ts` (one fetch fn), `frontend/src/components/Training/ProfileReport.tsx` (add the panel — optionally via a small new child component + its own file). **Create** `backend/tests/test_weakness_ranking_endpoint.py` and a frontend test file.
- **Do NOT touch** `backend/training/metrics.py` (leader-owned — `weakness_ranking` is done; **call it, do not modify it**), `select_repertoire.py`, `pipeline.py`, `drills.py`, or `explanations.py`. If you think you need to, STOP and report.

## Data shapes (pinned — do not guess)
`metrics.weakness_ranking(profile: dict, n: int = 6) -> list[DimComparison]` where `DimComparison` is a frozen dataclass with fields:
```
dim: str          # the ECO code, e.g. "C61"
value: float      # this dimension's blind_rate (0..1)
count: int        # move count behind it
ref_value: float  # the user's own baseline (mean of the OTHER openings)
grade: float      # signed effect size; < 0 = WEAKNESS (worse than baseline), > 0 = STRENGTH
importance: float # ranking magnitude (>= 0)
```
The list is already sorted (weaknesses first, by importance). Serialize each item to a dict and add a `kind` field. **Endpoint response shape (fixed):**
```json
{ "ranking": [
  { "dim": "C61", "value": 0.40, "count": 120, "ref_value": 0.11,
    "grade": -2.9, "importance": 31.7, "kind": "weakness" }
] }
```

## Part A — Backend endpoint (`backend/app.py`)
Add:
```python
import dataclasses  # (top of file if not already imported)

@app.get("/api/training/weakness-ranking")
async def weakness_ranking_ep(n: int = 6):
    from backend.training import metrics
    profile = store.load_profile()
    if not profile:
        return {"ranking": []}
    ranking = metrics.weakness_ranking(profile, n)
    return {"ranking": [
        {**dataclasses.asdict(c), "kind": "weakness" if c.grade < 0 else "strength"}
        for c in ranking
    ]}
```
Requirements:
1. No profile (or empty `by_opening`) → `{"ranking": []}`, HTTP 200 (never 500).
2. `n` is a query param (default 6), passed through to `weakness_ranking`.
3. Uses the REAL `metrics.weakness_ranking` — do not reimplement the math.

## Part B — Frontend API (`frontend/src/api/training.ts`)
```ts
export async function getWeaknessRanking(n = 6): Promise<{
  ranking: { dim: string; value: number; count: number; ref_value: number;
             grade: number; importance: number; kind: 'weakness' | 'strength' }[];
}> {
  const res = await fetch(`${BASE_URL}/weakness-ranking?n=${n}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
```

## Part C — Weakness Profile UI (`ProfileReport.tsx`)
Add a **"What to Work On"** panel to the Weakness Profile (near the existing "Top Openings" table). `ProfileReport` receives `profile` as a prop but the ranking is server-computed, so fetch it (a `useEffect` in ProfileReport, or a small child component `WeaknessRanking.tsx` — if you export a non-component helper, put it in its own file to avoid the fast-refresh lint rule).
1. On mount, call `getWeaknessRanking(6)`.
2. **Loading** → a spinner/placeholder.
3. **Ranked list** (in the returned order): per item show the **ECO** (`dim`), **blind rate** (`value*100`, 1 dp, `%`), **games** (`count`), and a clear **weakness/strength badge** driven by `kind` (weaknesses visually prominent — e.g. red-tinted; strengths green-tinted). A short header explains it's relative to the user's own baseline.
4. **Empty** ranking (`[]`) → a friendly message ("Not enough games analyzed yet to rank your openings"), NOT a dead/empty panel.
5. **Error** → a graceful inline message, no crash, no uncaught console error.
6. Do not break the existing Weakness Profile (stats row, Top Openings incl. the Color column, findings cards).

*(Optional, only if quick: a "Train" affordance on a weakness row that switches to Repertoire → Train mode for that ECO. Not required; skip if it complicates.)*

## Part D — Tests

### Backend (`backend/tests/test_weakness_ranking_endpoint.py`, pytest)
Use the `TestClient` pattern from `test_health.py` — `client = TestClient(app)` WITHOUT a `with` block (so the lifespan/LC0 engine does NOT start). Monkeypatch `store.load_profile`. These exercise the REAL `weakness_ranking` + serialization end-to-end (this is the required real/unmocked path — it would catch a serialization or signature break).
1. **Leak surfaces first.** `load_profile` returns a profile whose `aggregates.by_opening` has three ~0.10 openings and one at 0.40 with a healthy move count → response 200; `ranking[0]["dim"]` is the leak; its `kind == "weakness"` and `grade < 0`.
2. **Serialized shape.** Every ranking item has exactly the keys `dim, value, count, ref_value, grade, importance, kind`.
3. **Empty/no profile → 200, empty ranking.** `load_profile` returns `None` → `{"ranking": []}`; and a profile with empty `by_opening` → `{"ranking": []}` (neither 500s).
4. **`n` is honored.** A profile with 8 openings and `?n=4` → at most 4 items returned.

### Frontend (Vitest + RTL, mock `getWeaknessRanking`)
Each a real guard; a test that would pass with the feature deleted is a reject.
5. **Loading** state renders while the fetch promise is pending.
6. **Renders ranked items in order** — mock a ranking of 3 (2 weakness, 1 strength); assert the ECOs appear in the returned order, weakness rows carry a weakness indicator/class and the strength row a strength one.
7. **Formatting** — a `value` of 0.40 renders as `40.0%` and `count` 120 as games; `ref_value`/`importance` are not dumped raw as noise.
8. **Empty ranking** (`{ranking: []}`) → the friendly "not enough games" message; no crash; the rest of the Weakness Profile still renders.
9. **Fetch error** → graceful inline message; no uncaught error; rest of the profile intact.

## Gate — paste REAL output into `WORKLOG_TRAINING.md`
- `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests/test_weakness_ranking_endpoint.py -q` → all pass.
- `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests/ -q` → full suite, ≥ 117 (113 now + your ~4 backend).
- From `frontend/`: `npm run build` (clean), `npm run lint` (0 errors, **no new warnings**), `npm run test` (all pass, with count).

## Reuse (don't reinvent)
- Backend TestClient pattern: `backend/tests/test_health.py`.
- Frontend test harness + patterns: `frontend/src/components/Training/__tests__/` (from the R4 QA work).
- The existing Weakness Profile layout + the `openingColorLabel` helper-in-own-file pattern.

Prepend a dated `WORKLOG_TRAINING.md` entry ending with `T4 ranking UI ready for review`. Modify only the files named above + the worklog. Await leader sign-off.
