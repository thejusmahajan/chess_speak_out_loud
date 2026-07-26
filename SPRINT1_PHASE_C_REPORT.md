# Sprint 1 Phase C Report — "Usual Suspects" Review UI & Dashboard

## Summary of Implementation
Phase C ("Usual Suspects UI + Dashboard") delivers the complete front-end experience for reviewing recurring weaknesses, approving themes, building severity-blended drill decks, and running them directly through the existing `DrillMode` runner.

### 1. API Clients (`frontend/src/api/training.ts`)
Added typed API client interfaces and functions:
- `UsualSuspect`, `UsualSuspectsResponse`, `ApprovedSuspectsResponse`
- `getUsualSuspects()`: Fetches `/api/training/usual-suspects` (returns null on 404).
- `approveSuspects(themes)`: Posts approved themes to `/api/training/usual-suspects/approve`.
- `getApprovedSuspects()`: Fetches stored approved themes from `/api/training/usual-suspects/approved`.
- `buildSuspectsDeck(count)`: Posts target drill count to `/api/training/usual-suspects/deck` and returns drill set.

### 2. UsualSuspects Component (`frontend/src/components/Training/UsualSuspects.tsx`)
- **Compact Dashboard Panel (Q8.3)**:
  - Top Weakness: Displays `suspects[0].theme`.
  - Themes Needing Attention: Displays next top suspect themes.
  - Opening Focus: Displays placeholder `"Openings pending ECO fix"`.
  - SRS Due Drills: Displays due count from `getDueDrills()`.
- **Ranked Suspect Cards**:
  - Displays each suspect theme with its `severity_label` badge (high/medium/low styling), `games` × `occurrences`, and `rank_score`.
  - Checkboxes per theme, pre-checked if stored in `getApprovedSuspects()`.
  - Action button: **"Build my training deck"** calls `approveSuspects` and `buildSuspectsDeck(20)`, invoking `onDeckBuilt(setId)` on completion.
- **Empty / Error States**:
  - Friendly message when no profile exists (`"Run a diagnosis first to discover your usual suspects."`).
  - Friendly message when no clusters clear the 2-game floor (`"No recurring weaknesses detected yet (min 2 games floor)."`).

### 3. TrainingTab Navigation Wiring (`frontend/src/components/Training/TrainingTab.tsx`)
- Added `'usual_suspects'` view state and a **"Usual Suspects"** navigation tab button.
- Renders `<UsualSuspects onDeckBuilt={(id) => { setDrillSetId(id); setView('drills'); fetchSavedSets(); }} />`.
- **Unforked Execution Path**: Directly reuses `<DrillMode setId={drillSetId} />` verbatim.

### 4. Unit Tests (`frontend/src/components/Training/__tests__/UsualSuspects.test.tsx` & `TrainingQA.test.tsx`)
Added 4 comprehensive Vitest tests:
1. Renders ranked theme cards and dashboard summary from mocked payload.
2. Toggling checkboxes + clicking "Build my training deck" invokes `approveSuspects`, `buildSuspectsDeck`, and triggers `onDeckBuilt(id)`.
3. Displays empty-state message when suspects list is empty (`games < 2`).
4. Displays diagnosis prompt message when profile is absent (404).

## Verification Results
- **Vitest Suite (`npm test`)**: **30 / 30 passed** across 5 test files (100% green).
- **TypeScript & Vite Build (`npm run build`)**: `tsc -b && vite build` built cleanly with 0 errors.
- **Backend Test Suite (`pytest backend/tests`)**: **163 / 163 passed**.
- **Zero Push**: Code is stored locally and unpushed.
