# GEMINI WORKER SPEC — Interactive Free-Play Board (chessground + chessops)

> **You are Gemini, the implementation worker.** Same discipline as every prior phase:
> **do not invent APIs, verify before coding, paste real output, stop at every `⛔ GATE`,
> report honestly.** The neural pipeline is DONE and working — this task only changes the
> **board interaction model**. Do not touch or "improve" the backend, the attention/policy
> extraction, or the no-LLM decision.

---

## GOAL

Replace the read-only PGN replayer with an **interactive board** the user can play on:
- Click-move and drag-move **any legal move** (illegal moves snap back).
- **Take-back** (undo) to explore.
- **Load a PGN** to set up a line and step through it; playing a move at any point **branches
  into a free line** from that position.
- Every resulting position flows through the **existing** `/api/analyze` → arrows + glow +
  blunder-flash pipeline, unchanged in behavior.
- Drop the variation-tree / move-list sidebar (out of scope by the user's choice).

---

## VERIFIED FACTS (do not re-derive)
- The current board is `@lichess-org/pgn-viewer` — a **read-only replayer**; it has no
  user-move mode. It must be replaced for interactivity.
- `chessops` **0.15.1 is already installed**. `chessground` is **bundled inside** the
  pgn-viewer but is **NOT** a direct dependency — you must `npm install chessground`.
- The overlay renderer (arrows/glow/flash) currently lives in `frontend/public/lichess_viewer.html`
  inside an **iframe**, fed via `postMessage` + a `curData()` **polling** bridge. That bridge
  existed only to embed the replayer. **You will remove the iframe entirely** and render the
  board directly in React — simpler and less fragile.
- Backend contract (keep using it exactly): `POST /api/analyze` with body
  `{ fen: string, multipv: <=10 }`. **`multipv` MUST be ≤ 10** (it is 5 today — keep it).
  Response contains `policy[]` ({uci,san,from,to,p}), `saliency{square:0..1}`,
  `saliency_source`, `evaluation`. No LLM is called — keep it that way.

---

## HARD RULES
1. Preserve the neural overlays exactly: policy arrows (opacity & width ∝ `p`), saliency glow
   (blue, intensity ∝ value), blunder flash (glow turns red when `p(best) − p(played) > 0.25`).
2. `multipv` in the request stays ≤ 10. Do not raise it. (Arrows come from `policy`, not multipv.)
3. No new backend calls, no LLM, no changes to `neural_vision.py` / `engine_manager.py`.
4. Verify every `chessops` / `chessground` import path & export in the **discovery step**
   before using it — versions differ. No assumed API names.
5. Stop at each `⛔ GATE`. Run from the frontend dir with `npm`/`npx` (Node, not conda).

---

## STEP 1 — Install chessground + discover the real APIs (paste output)

```powershell
cd C:\Users\Admin\Documents\chess_speak_out_loud\frontend
npm install chessground
```
Then discover the **actual** exports of the installed versions (chessops 0.15.1 module layout
has changed across versions — confirm, do not guess). Write a tiny script or use `node`:
```powershell
node -e "console.log(Object.keys(require('chessops/compat')))"        # expect: chessgroundDests, chessgroundMove, ...
node -e "console.log(Object.keys(require('chessops/chess')))"          # expect: Chess, ...
node -e "console.log(Object.keys(require('chessops/fen')))"            # expect: parseFen, makeFen, INITIAL_FEN, ...
node -e "console.log(Object.keys(require('chessops/util')))"           # expect: parseUci, makeUci, parseSquare, makeSquare, ...
node -e "console.log(Object.keys(require('chessops/pgn')))"            # expect: parsePgn, startingPosition, ...
node -e "console.log(Object.keys(require('chessground')))"             # expect: Chessground
```
**⛔ GATE 1:** paste the real key lists. Confirm you have: a legal-dests helper
(`chessgroundDests`), FEN parse/make, a `Chess` position with `.play(move)`/`.isLegal`,
UCI/square helpers, a PGN parser, and the `Chessground` factory. If a name differs, use the
real one from the output.

---

## STEP 2 — Render chessground directly in React; delete the iframe bridge

Rewrite `frontend/src/components/PgnViewer.tsx` so the board is a chessground instance mounted
on a `div` ref — **no iframe, no postMessage, no `curData` polling, no `lichess_viewer.html`**.

- Import chessground CSS so the board and pieces render. Verify these asset paths exist under
  `node_modules/chessground/assets/` and import the ones that do (typically
  `chessground.base.css`, a board theme, and a pieces theme). If the bundled pieces don't show,
  fall back to the piece-image CSS that already works (the `lichess1.org/assets/piece/cburnett/*`
  backgrounds from the old `lichess_viewer.html`).
- Keep the existing checkerboard look if the chessground board theme doesn't load: the CSS
  checkerboard (`conic-gradient` on `cg-board`) from `lichess_viewer.html` can be reused.
- Mount once in a `useEffect`; keep the `Api` instance in a ref.

**⛔ GATE 2:** the board renders with pieces in the starting position, no iframe in the DOM.

---

## STEP 3 — Legal moves, user input, and the analyze/overlay hook

- Hold the game position as a `chessops` `Chess` object in a ref; keep a **move-history stack**
  (list of prior positions or moves) for take-back.
- Configure chessground `movable`:
  ```
  movable: {
    free: false,
    color: 'both',
    dests: chessgroundDests(pos),      // from chessops/compat, recomputed each move
    events: { after: onUserMove }
  }
  ```
- `onUserMove(orig, dest)`:
  1. Build the move (UCI = orig+dest). **Promotion:** for v1 auto-promote to queen (append `q`
     when a pawn reaches the last rank). Verify legality via chessops; if illegal, reset the
     board to the current FEN (snap-back).
  2. Play it on the `chessops` position → new FEN; compute the **UCI** of the move played.
  3. Push previous state to the history stack; update chessground (`cg.set({ fen, turnColor,
     movable: { dests: newDests } })`); set `lastMove: [orig, dest]`.
  4. Call the **existing** `analyzeFen(fen, uciPlayed)` (keep `multipv: 5`). Reuse the current
     blunder-disparity logic (compare played move's `p` vs best `p` in the PREVIOUS position's
     policy) and the overlay draw.
- **Take-back button:** pop the history stack, restore that FEN into chessground and the
  chessops position, re-analyze that position (uci = null → no flash).

**⛔ GATE 3:** clicking or dragging a legal move updates the board and triggers a new analyze +
overlay; an illegal move snaps back; take-back restores the prior position.

---

## STEP 4 — PGN setup + branching

- Keep the PGN `textarea` + "Load Game" button.
- On load: parse with `chessops` `parsePgn` → take the **mainline** move list; set the board to
  the start of that line. Provide **Prev / Next** buttons to step the mainline.
- If the user **plays a move** while stepping, that becomes a new move from the current position
  (branch into a free line) — i.e. truncate "forward" history and continue from here. A simple
  linear history is fine; no variation tree UI.

**⛔ GATE 4:** load the default PGN, step forward a few moves with Next, then play your own move
— the board accepts it and analyzes the new position.

---

## STEP 5 — Port the overlay renderer into React

Move the SVG drawing from `lichess_viewer.html` into the React component (or a small helper),
drawing onto the chessground board element (`cg-board` / `.cg-wrap`). Keep it identical in
behavior:
- **Saliency glow:** radial-gradient circle per square with `val > 0.05`; color blue
  `0,150,255`, or red `255,0,50` when `blunderFlash` is true; opacity ∝ `val`.
- **Policy arrows:** line from `move.from`→`move.to`; opacity `max(0.2, p)`, width `max(1, p*4)%`.
- **Orientation:** honor board orientation when mapping square→coords (reuse the `getCoords`
  logic, including the black-orientation flip).
- Redraw on every analyze response; clear on new game load.
Then **delete** `frontend/public/lichess_viewer.html` (no longer used).

**⛔ GATE 5:** after a move, arrows and glow render on the live board; playing an obvious blunder
(e.g. hang the queen) turns the glow **red**.

---

## STEP 6 — Verify build, commit, report
- `npx vite build` must pass (no transform/type errors). **Run this before claiming done** —
  escaped backticks / stray `$` in generated TSX have bitten us before.
- Manually confirm GATES 2–5 in the browser (backend running from the conda env
  `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn backend.app:app`; `npm run dev`).
- Commit: `Interactive free-play board (chessground + chessops); remove iframe replayer`.
- Update `REALIGNMENT_REPORT.md` with GATES 1–5 results and note the iframe/postMessage bridge
  was removed.

### Self-audit
- [ ] Every chessops/chessground symbol used appeared in the GATE-1 output.
- [ ] `multipv` in the analyze request is still ≤ 10.
- [ ] No iframe / postMessage / curData polling remains; `lichess_viewer.html` deleted.
- [ ] Legal move → analyze → arrows+glow; illegal → snap back; take-back works; PGN load+step+branch works.
- [ ] `npx vite build` passes; blunder move flashes red.
- [ ] No backend/LLM changes.
