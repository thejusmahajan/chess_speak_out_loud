# Sprint 3 Phase C2 Report — Play the sacrifice out vs LC0 (Frontend)

## Executive Summary
Phase C2 frontend implementation is complete and verified against all requirements. The interactive playout mode seamlessly integrates into `SacDrill.tsx`, allowing users to play out sacrifice positions against LC0 defense with per-move quality feedback, running attacker-POV centipawn evaluation, and an end-of-playout summary verdict.

---

## Implemented Components

### 1. API Client Extension ([api/training.ts](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/api/training.ts))
- Defined `SacPlayoutResult` interface covering start and move responses.
- Implemented `startSacPlayout(finding_id)` to initiate engine playout.
- Implemented `submitPlayoutMove(finding_id, line, user_uci, history)` to post user attack moves and receive quality ratings & LC0 replies.

### 2. Sacrifice Drill Component ([SacDrill.tsx](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/training/SacDrill.tsx))
- **"▶ Play it out vs LC0" Button**: Rendered in the soundness reveal panel after a sacrifice guess.
- **Engine Offline Guard**: Catches `engine_unavailable` error response and displays `"Engine offline — play-out unavailable"` without breaking UI flow.
- **Attacker Board Orientation**: Reuses `<TrainingBoard>` and sets board orientation strictly to `attacker_is_white ? 'white' : 'black'`.
- **Running Attacker Eval & Feedback**:
  - Displays `attacker_eval_cp` (e.g. `+120cp (Attack working)`).
  - Displays Quality Badges: `great` 🟢 / `ok` 🟡 / `drift` 🔴.
  - Displays `"LC0 preferred {san}"` when move quality is not `great`.
- **Summary Verdict Card**:
  - Rendered when `is_complete` is true.
  - Displays `verdict` banner text (e.g. `"You kept the attack"`).
  - Displays stats grid (`Moves`, `Great 🟢`, `OK 🟡`, `Drift 🔴`, `Final Eval`).
  - Action buttons: **"Back to sacrifices"** and **"Next Position"** / **"Finish Session"**.

### 3. Test Suite Extension ([SacDrill.test.tsx](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/training/__tests__/SacDrill.test.tsx))
Added tests covering all 4 spec mutation checks:
1. **Play it out Button & Playout Start**: Verifies button appearance after reveal and state transition to playout mode.
2. **Attacking Move & LC0 Reply**: Verifies move submission with accumulated `line` and `history`, and quality badge / LC0 reply rendering.
3. **Summary Verdict**: Verifies rendering of completion summary verdict card.
4. **Engine Offline Handling**: Verifies `engine_unavailable` error message display.

---

## Verification & Build Results

| Test / Build Target | Command | Result | Status |
| :--- | :--- | :--- | :--- |
| **Frontend Unit Tests** | `npm test` | **41 / 41 PASSED** (7 test files) | **VERIFIED** |
| **Frontend Production Build** | `npm run build` | `tsc -b && vite build` completed in 1.13s (dist/ 340.40 kB) | **VERIFIED** |
| **Backend Test Suite** | `python -m pytest backend/tests` | **183 / 183 PASSED** | **VERIFIED** |

---

## Gate Checklist
- [x] Reused `TrainingBoard`; did NOT reimplement board or touch backend/`metrics.py`/other training modes.
- [x] `npm test` green (41 passed).
- [x] `npm run build` clean (zero TypeScript/Vite errors).
- [x] No Git push performed.
- [x] **STOP for Leader Review**.
