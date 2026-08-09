# TASK FOR GEMINI — Sprint 1 Phase C: "Usual Suspects" review UI + dashboard (frontend)

Front-end for the Usual Suspects loop (Phases A+B are done & merged). Show the user his ranked
recurring weaknesses, let him **approve** which to train, **build the deck**, and run it in the
**existing `DrillMode`** (do NOT fork it). Plus a minimal dashboard. Lean, fast UI — no animation
bloat (user's explicit bar). `npm test` + `npm run build` stay green. No push. STOP for leader review.
Report `SPRINT1_PHASE_C_REPORT.md`.

## Backend endpoints already live (Phases A+B) — just consume them
- `GET  /api/training/usual-suspects` → `{ suspects: [{theme, games, occurrences, mean_severity,
  rank_score, severity_label, finding_ids}], by_phase: [...], by_concept: [...] }`
- `POST /api/training/usual-suspects/approve` body `{themes: string[]}` → 200 `{themes}` (400 on unknown)
- `GET  /api/training/usual-suspects/approved` → `{themes: string[]}`
- `POST /api/training/usual-suspects/deck` body `{count: number}` → a **drill_set** `{id, drills, ...}`,
  already saved server-side (loadable via the existing `getDrillSet(id)` / `/drills/{id}`).

## Reuse — DO NOT rebuild or fork
- `frontend/src/components/Training/DrillMode.tsx` runs any set via its `setId` prop
  (`<DrillMode setId={id} onExit={...}/>`). **Launch the suspects deck through this exact path.**
- `frontend/src/components/Training/TrainingTab.tsx` is a `view` state machine. The existing
  `generateDrills(5) → setDrillSetId(id) → setView('drills')` flow is your TEMPLATE — mirror it.
- `frontend/src/api/training.ts` — add the 4 typed clients + interfaces here (next to `getDrillSet`,
  `generateDrills`). Do NOT disturb the existing `ProfileData`/steer types.

## Build
1. **api/training.ts:** add `getUsualSuspects()`, `approveSuspects(themes)`, `getApprovedSuspects()`,
   `buildSuspectsDeck(count)` with TS interfaces (`UsualSuspect`, etc.) matching the schema above.
2. **`UsualSuspects.tsx`** (new, in `components/Training/`):
   - Fetch `getUsualSuspects()`; render suspects as a **ranked list of theme cards**: theme name,
     `severity_label` badge (high/medium/low), `games` × `occurrences`, and `rank_score`. Pre-check
     any already in `getApprovedSuspects()`.
   - A checkbox per theme + a **"Build my training deck"** button → `approveSuspects(checked)` then
     `buildSuspectsDeck(count)` (default count e.g. 20) → hand the returned deck's `id` up to the
     parent to launch DrillMode (via a prop callback, e.g. `onDeckBuilt(setId)`).
   - (Optional/nice-to-have, keep MVP lean:) expand a card to preview its positions by
     cross-referencing `getProfile().findings` by `finding_id` — skip if it complicates the MVP.
3. **TrainingTab wiring:** add a `'usual_suspects'` view + a tab button; render `<UsualSuspects
   onDeckBuilt={(id) => { setDrillSetId(id); setView('drills'); }} />`. That reuses the existing
   `<DrillMode setId={drillSetId}/>` render path verbatim.
4. **Minimal dashboard (Q8.3)** — a compact panel (top of `UsualSuspects.tsx` or a small sibling):
   **top weakness** = `suspects[0].theme`; **theme needing attention** = next few; **opening** =
   a placeholder "Openings pending ECO fix" (ECO is `'???'` until that fix ships — do NOT invent
   opening data); **drill progress** = the existing due-count (`getDueDrills`, already used in
   TrainingTab). Keep it lean and information-dense, not decorative.

## Constraints & gates
- **Do NOT fork `DrillMode`** — reuse via `setId`. Do NOT touch the backend, `metrics.py`, or the
  Phase A/B code. Do NOT disturb the TS2 section added to `ProfileReport.tsx` (earlier bug-hunt) or
  the board/neural overlays.
- Match the endpoint schemas exactly. Handle empty states (no profile → suspects empty → friendly
  "Run a diagnosis first"; no suspects clearing the 2-game floor → "No recurring weaknesses yet").
- **Tests** (`components/Training/__tests__/UsualSuspects.test.tsx`), mock the 4 endpoints:
  (1) renders ranked theme cards from a mocked suspects payload; (2) toggling checkboxes + "Build
  deck" calls `approveSuspects` then `buildSuspectsDeck` and fires `onDeckBuilt(id)`; (3) empty
  suspects → the empty-state message. Keep/extend existing tests; don't delete assertions.
- `npm test` green (26 + new), `npm run build` clean. No push. STOP for leader review.
