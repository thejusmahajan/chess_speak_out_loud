# Sprint 3 Phase B Report — Sacrifice / Tactical-Landmine Training UI (frontend)

## Summary of Implementation
Sprint 3 Phase B delivers the frontend user interface for **Sacrifice & Tactical-Landmine Training (Jobs 1 + 7)**. The UI presents positions from the user's own games where LC0 identified sound Tal-style sacrifices (`had_tal_move == true`), allowing the user to practice finding sacrifices and viewing honest soundness comparisons.

### 1. API Client Extension ([frontend/src/api/training.ts](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/api/training.ts#L278-L347))
Added TypeScript interfaces and client functions for the 3 Phase A backend endpoints:
- `SacPosition`, `SacMove`, `SafeMove`, `PlayableCandidate`, `SacGuessResult`, `SacStats`
- `startSacSession(count)`: Posts to `/api/training/sac/session`.
- `submitSacGuess(finding_id, uci)`: Posts to `/api/training/sac/guess`.
- `getSacStats()`: Fetches `/api/training/sac/stats`.

### 2. SacDrill Component ([frontend/src/components/Training/SacDrill.tsx](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/SacDrill.tsx))
- **Interactive Training Board**: Reuses `<TrainingBoard fen={pos.fen} orientation={sideToMove} interactive={!currentResult} onMove={handleGuess} />` verbatim.
- **Find-the-Sac Prompt**: Prompt header: `"💡 A strong sacrifice is available here — find it."` (No timer — focused on calculation/recognition).
- **Soundness Reveal Panel**:
  - **Verdict Banner**:
    - **HIT**: Green banner (`🎯 HIT! You found the sacrifice!`).
    - **Sound Alternative**: Yellow banner (`⚡ SOUND ALTERNATIVE! A sharp try — LC0 preferred...`).
    - **Miss**: Red banner (`❌ MISS! You played it safe...`).
  - **Honest Soundness Framing**:
    Displays comparison: *"You'd safely play {safe_move.san} ({safe_move.eval_cp}cp). The sac {sac_move.san} ({sac_move.eval_cp}cp) concedes only {eval_loss_cp}cp of objective eval but goes into a far sharper position (complexity {sac_move.complexity}) where the opponent is likely to go wrong."*
  - **Next Control**: Advances to the next position or triggers session completion.
- **End-of-Session Summary**:
  - Displays session score (`score / positions.length`), sound alternatives found count, and accuracy.
  - Displays lifetime overall accuracy, sound alternatives total, and recent accuracy (last 50 guesses) from `getSacStats()`.
- **Empty State Handling**: Displays clear message when no eligible sacrifice positions are found in the profile.

### 3. TrainingTab Navigation Wiring ([frontend/src/components/Training/TrainingTab.tsx](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/TrainingTab.tsx#L147-L261))
- Added `'sacrifices'` view state and a **"Train Sacrifices"** tab button.
- Renders `<SacDrill />` when `'sacrifices'` view is selected.

### 4. Unit Tests ([frontend/src/components/Training/__tests__/SacDrill.test.tsx](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/Training/__tests__/SacDrill.test.tsx))
Added 3 comprehensive Vitest unit tests:
1. `Renders board and find-the-sac prompt for the first position`: Verifies component mounting, prompt rendering, board display, and position index counter.
2. `Making a move calls submitSacGuess and displays soundness reveal panel`: Verifies guess submission, hit banner, soundness framing text, and complexity display.
3. `Completing session displays session summary accuracy and lifetime stats`: Verifies session flow across positions and end-of-session summary display.

## Verification Results
- **Vitest Suite (`npm test`)**: **37 / 37 passed** across 7 test files (100% green).
- **TypeScript & Vite Production Build (`npm run build`)**: `tsc -b && vite build` built cleanly with **0 errors**.
- **Backend Test Suite (`pytest backend/tests`)**: **177 / 177 passed**.
- **Git Push**: Zero pushes performed.
