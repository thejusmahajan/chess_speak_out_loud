# GEMINI WORKER SPEC — Live Move-List / Notation Panel

> **You are Gemini, the implementation worker.** Same discipline as always: **verify before
> coding, no invented APIs, run the build, report honestly, and COMMIT at the end** (explicitly
> requested this time). This is a **frontend-only, additive** task in
> `frontend/src/components/PgnViewer.tsx`. Do not touch the backend, the neural pipeline, or the
> no-LLM decision.

---

## GOAL

Add a **move-list (notation) panel** that records moves in SAN as they happen and lets the user
navigate:
- Shows the current line's moves as `1. e4 e5  2. Nf3 Nc6 …` (numbered, White/Black columns).
- Updates **live** when the user plays a move (including branches) and when a PGN is loaded.
- Each move is **clickable** → jumps to that position.
- The move at the current position is **highlighted**; the panel auto-scrolls to it.
- It is separate from the existing PGN input `<textarea>` (keep that for loading games).

---

## CRITICAL — DO NOT REGRESS THE STATE MODEL (read before editing)

`PgnViewer.tsx` was just repaired for a cluster of React reactivity bugs. **Preserve this exact
model — do not revert to stale closures or ref-only mutation without re-render:**
- `gameStates` is a `useRef<GameState[]>`; `currentIndexRef` is a `useRef<number>` and is the
  **source of truth** read by the stable chessground move handler; `currentIndex` is `useState`
  mirroring it for JSX; `forceRender()` (a `useReducer`) re-renders on async data updates.
- **All navigation goes through `goToIndex(i)`** (it updates `currentIndexRef`, `setCurrentIndex`,
  `syncBoard`, overlays, and analyzes if needed). Your clickable moves MUST call `goToIndex(i)` —
  do not write your own navigation.
- The chessground `movable.events.after: handleMove` handler reads live state from refs. **Do not
  move state into that closure.**
- Overlays are drawn imperatively via `drawOverlays(...)`. Leave that as-is.
- `multipv` in the analyze request stays **≤ 10** (it is 5). No backend calls change.

If you break "play both sides", "Load Game", or "Prev/Next", you have regressed — re-check against
this list.

---

## STEP 1 — Store SAN on each GameState

The move list needs SAN. Extend the `GameState` type with `san: string | null` (null for the
start position).

Populate it where states are created:
- **`handleMove`**: compute SAN from the position **before** the move. Verify the chessops API
  first — use the **non-mutating** `makeSan(pos, move)` from `chessops/san`. ⚠️ There is also
  `makeSanAndPlay(pos, move)` which **mutates** `pos` — do NOT use that here (you clone & play
  separately). Confirm with:
  ```powershell
  cd C:\Users\Admin\Documents\chess_speak_out_loud\frontend
  node -e "console.log(Object.keys(require('chessops/san')))"
  ```
  Compute `san = makeSan(cur.pos, move)` on the current position, before cloning/playing.
- **`handleLoadPgn`**: while walking the mainline, you already have `child.data.san` — store that
  (or `makeSan(pos, move)` before `pos.play(move)`).
- The initial/start state has `san: null`.

**⛔ GATE 1:** paste the `chessops/san` key list and confirm `makeSan` exists and is the
non-mutating one you use. If the mainline SAN and hand-played SAN both look correct in the panel
(Step 2), the storage is right.

---

## STEP 2 — Render the notation panel

Add a scrollable move-list panel to the JSX (a sensible spot: in the right `input-section`
between the evaluation readout and the PGN `<textarea>`, or beside the board — your call, keep it
readable in the existing glass-panel style).

- Iterate `gameStates.current` from index **1** (skip the start position). Group into move pairs:
  move number = `Math.ceil(i/2)`; White move at odd `i`, Black at even `i` (for a game starting
  from the standard position; if a loaded PGN has a FEN header with Black to move first, base the
  numbering on `pos.turn` of the start state — acceptable to keep it simple for v1 and note it).
- Each move renders its `state.san`; clicking calls `goToIndex(i)`.
- Highlight the entry where `i === currentIndex` (e.g. a background/border via inline style or a
  CSS class in `PgnViewer.css`).
- The panel scrolls vertically (fixed max-height, `overflow-y: auto`) and should auto-scroll the
  highlighted move into view (a `ref` on the active element + `scrollIntoView({block:'nearest'})`
  in a `useEffect` keyed on `currentIndex`).

Because navigation and moves already trigger re-render (`setCurrentIndex`/`forceRender`), the
panel updates live with no extra state needed — just read `gameStates.current` in render.

**⛔ GATE 2 (manual):**
1. Play several moves for both sides → each appears in the panel immediately, correctly numbered.
2. Click an earlier move in the panel → board + overlays jump to it (via `goToIndex`).
3. From a mid-line position, play a new move → forward moves are replaced (branch) and the panel
   reflects the new line.
4. Click **Load Game** → the loaded mainline fills the panel; **Next/Prev** highlight advances.

---

## STEP 3 — Build, verify, COMMIT

1. **Must pass before claiming done** (escaped backticks / stray `$` in generated TSX have bitten
   us before, and type errors won't fail the Vite build — run both):
   ```powershell
   cd C:\Users\Admin\Documents\chess_speak_out_loud\frontend
   npx tsc --noEmit
   npx vite build
   ```
   Both must be clean (0 errors).
2. Manually confirm GATE 2 in the browser (backend from the conda env:
   `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn backend.app:app`; `npm run dev`).
3. **Commit all current working state** (there is a lot uncommitted — Phase 3, the interactive
   board, earlier fixes, and this panel). From the repo root:
   ```powershell
   cd C:\Users\Admin\Documents\chess_speak_out_loud
   git add -A
   git commit -m "Interactive board + neural overlays + live move-list notation panel"
   ```
   Do **not** use `--no-verify`. If a hook fails, fix the cause and report.

### Self-audit
- [ ] `makeSan` (non-mutating) confirmed from real `chessops/san` output; SAN stored on each state.
- [ ] Move list updates live on play, branches correctly, and click → `goToIndex(i)`.
- [ ] State model untouched (refs + forceRender + goToIndex + stable handleMove); play-both-sides,
      Load Game, and Prev/Next still work.
- [ ] `multipv` ≤ 10; no backend/LLM changes.
- [ ] `npx tsc --noEmit` and `npx vite build` both clean.
- [ ] Working state committed (no `--no-verify`).
