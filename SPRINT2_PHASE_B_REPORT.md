# Sprint 2 Phase B Report — LC0 Intuition Speed-Drill UI (frontend)

## Summary of Implementation
Sprint 2 Phase B delivers the frontend user interface for the **LC0 Intuition Speed-Drill (Jobs 4 + 5)**. The UI allows users to train policy-blindness reduction by making speed guesses of LC0's #1 policy move on cached positions under a 10-second timer.

### 1. API Client Extension ([frontend/src/api/training.ts](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/api/training.ts#L220-L277))
Added TypeScript interfaces and client functions for the 3 Phase A backend endpoints:
- `IntuitionPosition`, `IntuitionMove`, `IntuitionGuessResult`, `IntuitionStats`
- `startIntuitionSession(count)`: Posts to `/api/training/intuition/session`.
- `submitIntuitionGuess(epd, uci)`: Posts to `/api/training/intuition/guess`.
- `getIntuitionStats()`: Fetches `/api/training/intuition/stats`.

### 2. IntuitionDrill Component ([frontend/src/components/Training/IntuitionDrill.tsx](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/IntuitionDrill.tsx))
- **Interactive Training Board**: Reuses `<TrainingBoard fen={pos.fen} orientation={sideToMove} interactive={!currentResult} onMove={handleGuess} />` verbatim.
- **10s Countdown Timer**: Visual countdown (`INTUITION_SECONDS = 10`). Highlights red when 3 seconds or fewer remain. If countdown reaches `0` without a move, automatically submits an empty guess `""` (timeout miss).
- **Reveal Panel**:
  - **Hit / Miss Banner**: Displays green banner for top-1 match (`🎯 HIT! You guessed LC0's #1 policy move!`), or red banner showing your move's rank (`❌ MISS! Your move was LC0's #N choice...`) or indicating move was off-list.
  - **Top-5 Policy List**: Renders LC0's top 5 ranked policy moves as visual percentage bars (`(p * 100).toFixed(1)%`), highlighting both the top move and the user's guessed move.
  - **Next Position Control**: Advances to next position or triggers session completion.
- **End-of-Session Summary**:
  - Displays session score (`score / positions.length`) and accuracy percentage.
  - Displays lifetime overall accuracy and recent accuracy (last 50 guesses) from `getIntuitionStats()`.
- **Empty State Handling**: Displays clear message when no eligible cache positions are found.

### 3. TrainingTab Navigation Wiring ([frontend/src/components/Training/TrainingTab.tsx](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/TrainingTab.tsx#L143-L253))
- Added `'intuition'` view state and a **"Train Intuition"** tab button.
- Renders `<IntuitionDrill />` when `'intuition'` view is selected.

### 4. Unit Tests ([frontend/src/components/Training/__tests__/IntuitionDrill.test.tsx](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/__tests__/IntuitionDrill.test.tsx))
Added 4 comprehensive Vitest tests:
1. `Renders board and timer for the first session position`: Verifies mounting, board rendering, position counter, and 10s timer display.
2. `Making a move calls submitIntuitionGuess and displays reveal panel`: Verifies guess submission, hit banner, top policy bars, and rank display.
3. `Timeout (timer hitting 0) submits empty guess and displays miss reveal`: Verifies fake timer advance to 10s triggers timeout submit `""` and displays miss banner.
4. `Completing session shows end-of-session accuracy summary and lifetime stats`: Verifies session flow across positions and end-of-session accuracy summary.

## Verification Results
- **Vitest Suite (`npm test`)**: **34 / 34 passed** across 6 test files (100% green).
- **TypeScript & Vite Production Build (`npm run build`)**: `tsc -b && vite build` built cleanly with **0 errors**.
- **Backend Test Suite (`pytest backend/tests`)**: **171 / 171 passed**.
- **Git Push**: Zero pushes performed.
