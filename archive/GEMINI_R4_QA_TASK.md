# Gemini Task — R4 Repertoire Trainer: QA hardening, empty-state fixes, and a real frontend test harness

**Model:** Gemini 3.6 Flash (high). **Token budget is not a concern — be exhaustive.** The goal is that the user never again hits an unhandled UI glitch. Test through everything you reasonably can.

## Context
R4 shipped the Repertoire Trainer:
- Frontend: the `RepertoireTrainer` component + `RepertoirePanel` in `frontend/src/components/Training/RepertoirePanel.tsx`
- API: `getRepertoireTree` in `frontend/src/api/training.ts`
- Backend: `POST /api/training/repertoire/tree` in `backend/app.py`

It passed `npm run build` and `npm run lint`, **but those don't test behavior, and this repo has NO frontend test harness.** As a result real runtime bugs shipped. Your job: reproduce and fix every reported bug, **stand up a real frontend test harness**, write thorough tests, and do a systematic QA sweep of the whole Training UI — finding and fixing inconsistencies.

## Reported bugs (reproduce + fix ALL of them)
The user opened **Training Mode → Repertoire → "Train Repertoire"**, selected the recommended white opening *"Ruy Lopez: Closed, Chigorin Defense, Panov System (C99)"*, and separately **"Weakness · Black" (D55)**. Observed:

1. **Empty/degenerate tree renders a dead trainer.** For these openings the tree comes back as a **single root node with no `user_move` and no `opponent_replies`** (few/zero of the user's games reach them). The trainer then shows only the opening title and *"Best move: N/A"* over an interactive-but-useless board. **Root cause:** `RepertoireTrainer` assumes a populated tree. **Fix:** detect a degenerate tree — `nodes.length === 0`, OR a root user-node whose `user_move` is undefined, OR no node in the tree has a `user_move` — and render a clear friendly state, e.g. *"No variation tree could be built for {opening} ({eco}) — too few of your games reach this line."* Do **not** show an interactive board in that state.

2. **User move silently ignored.** Playing `e4` does nothing: `handleUserMove` returns early when `currentNode.user_move` is undefined, the piece snaps back, and there is zero feedback. **Fix:** never make the board interactive when there is no `user_move` to test; whenever the board *is* interactive, every user move must produce feedback (accept/advance or reject-with-message).

3. **No line / variation display.** The user expects to *see* the repertoire lines/variations — a move list or tree — not walk blindly. Today only a "Walked line" of already-played moves appears, and it's empty until moves happen. **Fix:** add a visible representation of what's being trained. Minimum: show the current node's expected `user_move` and the branch's `opponent_replies` up front. Better: a scrollable move list of the current line and/or a compact variation view so the user can see where the branches go.

4. **Inactive / confusing buttons.** On an empty tree "Walk Another Line" and "Reset Line" do nothing and the opponent-reply buttons are absent. **Fix** as part of (1)–(3): controls must be either functional or visibly disabled with a reason.

5. **Slow on-demand build with poor feedback.** Selecting an un-cached opening (e.g. D55) triggers a synchronous engine build that can take minutes; the UI shows a bland "Building…" and can look hung. **Fix (frontend only):** a robust long-load state — spinner + explanatory text ("Building the tree with the engine; this can take a minute…") + a client-side timeout that surfaces a clear error instead of hanging forever. (Making the endpoint async is a separate LEADER follow-up — do not change the endpoint's build logic beyond letting it return clear errors.)

## Part A — Stand up a frontend test harness (none exists yet)
- Add dev deps: **vitest, @testing-library/react, @testing-library/jest-dom, @testing-library/user-event, jsdom**.
- Add a **`vitest.config.ts`** (or extend the vite config) using the `jsdom` environment and a setup file that imports `@testing-library/jest-dom`.
- Add an **`npm run test`** script (`vitest run`) and confirm `npm run test` works.
- Tests must be **self-contained** — never require a running backend. Mock `../../api/training` (`getRepertoireTree`, `listRepertoires`, etc.).

## Part B — RepertoireTrainer tests (enumerate — every one a REAL guard)
Mock `getRepertoireTree` to return controlled trees and assert behavior. A test that would still pass if the feature were deleted is a reject.
1. **Loading** state renders while the fetch promise is pending.
2. **Error** state renders on a rejected fetch.
3. **Empty tree** (`nodes: []`) → friendly "no tree" message; **no interactive board**.
4. **Degenerate root** (1 node, user-node, no `user_move`) → same "no trainable tree" message; board not interactive.
5. **Happy path (rich tree)** — hand-build a 3–4 ply white-repertoire tree: board interactive at the user node; playing the correct `user_move` → success feedback, opponent auto-reply animates, advances to the next user node; playing a **wrong** move → error message naming the correct move, no advance; board FEN ends where expected.
6. **Black repertoire root** (opponent node at ply 0) → auto-plays a weighted opponent reply and lands on the first user node.
7. **Castling acceptance** — a move entered as `e1g1` is accepted when `user_move.uci` is `e1h1` (and vice-versa), both colors.
8. **Critical badge + stats** render for a critical node (reason + eval + complexity + blind-rate).
9. **Opponent reply re-roll** — clicking a different reply button changes which line is followed.
10. **Branch completion** — reaching a leaf shows "Branch complete!"; "Walk Another Line" and "Reset Line" behave.
11. **Child matching by FEN** — a tree whose child `fen_before` is reachable only through the exact move (include a position right after a double pawn push, to guard the en-passant/normalization path).

## Part C — Whole-Training-UI QA sweep (find + fix, then report)
Exercise the entire Training experience, **log every glitch, then fix it.** If you can drive a browser (Playwright against `http://localhost:5173`, backend on `:8000`), add an **E2E smoke spec** and paste its summary; otherwise cover it with component/interaction tests plus a careful manual checklist (pass/fail per item). Cover at least:
- **Top tabs:** Analysis Mode ↔ Training Mode switch (no console errors either way).
- **Training sub-nav:** Diagnose PGN, Weakness Profile, Training Drills, Repertoire, Review, Progress — each mounts without console errors; disabled states correct (e.g. Weakness Profile disabled with no profile; Review disabled at 0 due).
- **Weakness Profile:** tables render; the **Color** column shows White/Black/Both/—; finding cards open the board panel.
- **Training Drills:** Saved Sets list; "Generate New Set"; **Load** a set → DrillMode plays; correct/wrong feedback; line completion; SRS "Review" flow.
- **Repertoire:** Recommendations view (variant switch, per-rec preview render) AND Train mode (all of Parts A–B).
- **Review / Progress:** render both with data and empty.
- **Cross-cutting:** no uncaught console errors anywhere; no horizontal overflow / broken layout; every button has correct enabled/disabled/active state; every loading and empty state is graceful (no dead boards, no "N/A" soup, no infinite spinners).

## Gate — paste REAL output into `WORKLOG_TRAINING.md`
- `npm run build` → clean
- `npm run lint` → 0 errors, **no NEW warnings** (keep helpers in their own files to avoid the fast-refresh rule)
- `npm run test` → all pass, with the count
- A written **QA REPORT**: list every screen/state you checked, every bug found, and exactly how each was fixed. If you ran Playwright, paste the run summary.

## Ownership / constraints
- **Frontend only**, plus test-harness config/deps. Do **NOT** modify `backend/app.py`'s tree-build logic, `backend/training/select_repertoire.py`, or `backend/training/metrics.py`. If a bug traces to the tree **data** (the builder), **STOP and report it to the leader** — do not edit those files.
- The **Train-mode opening selector** (letting the user pick high-volume openings like A40/A46/D02 instead of only the low-volume recommendations) is a SEPARATE task the leader will do next. Don't build it here — but your empty-state handling MUST make today's low-volume selections behave gracefully.
- For happy-path manual/E2E testing, a rich pre-built tree is available instantly: `POST http://127.0.0.1:8000/api/training/repertoire/tree` with `{"eco":"A40","color":"white"}` → a 17-node tree, 8 critical nodes (cached).

Prepend a dated `WORKLOG_TRAINING.md` entry ending with `R4 QA + tests ready for review`. Modify only frontend files, `package.json`/test config, and the worklog. Await leader sign-off.
