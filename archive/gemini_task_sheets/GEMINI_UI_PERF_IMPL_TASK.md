# TASK FOR GEMINI — Implement UI perf: memoization + Vite chunking ONLY (careful, incremental)

Implement the **two safest, highest-value** items from `UI_PERF_AUDIT.md` — nothing else.
The leader (Claude) deliberately scoped OUT the risky items; **do not touch them** (see the
FORBIDDEN list). Every change must be **behavior-preserving**: the UI must look and act
EXACTLY the same, only render/build faster. Work on a branch or leave staged; **do not push.**
STOP for leader review.

## IN SCOPE (do exactly these, nothing more)
### A. PERF-03 + PERF-06 — Memoization (do them TOGETHER, see Trap #1)
- Wrap in `React.memo`: `ProfileReport` (`frontend/src/components/Training/ProfileReport.tsx`),
  `WeaknessRanking` (`WeaknessRanking.tsx`), and `TrainingBoard` (`TrainingBoard.tsx`) — subject
  to Trap #2 for `TrainingBoard`.
- In `TrainingTab.tsx`: stabilize the props passed to those children — wrap handlers
  (`onFindingClick`, `onGenerateDrills`, and any other function props) in `useCallback`, and
  wrap array/object props (e.g. `policyCandidates`, any inline `{...}`/`[...]`) in `useMemo`, so
  the memo actually takes effect.

### B. PERF-08 — Vite production chunking
- In `frontend/vite.config.ts`, add `build.rollupOptions.output.manualChunks` splitting stable
  vendors (e.g. `vendor-react` for react/react-dom, `vendor-chess` for chessground/chessops/
  chess.js if present). Optionally add `rollup-plugin-visualizer` to **devDependencies** only.
- Do NOT change app code for this — build config only.

## FORBIDDEN — do NOT touch (leader will reject any diff that does)
- **PERF-05** `forceRender` in `PgnViewer.tsx` — it drives live-analysis updates; refactoring it
  risks silently breaking engine-callback rendering. LEAVE IT.
- **PERF-07** the imperative SVG / `neural-overlay` mutation code in `TrainingBoard.tsx` and
  `PgnViewer.tsx` — this renders the board's neural/attention overlays and arrows (a CORE
  feature). LEAVE IT untouched.
- **PERF-01 / PERF-04** virtualization — do NOT add `@tanstack/react-virtual` or any windowing
  library, and do NOT change how the findings/steer/move lists are mapped. (Separate later batch.)
- **PERF-02** `React.lazy` / `Suspense` code-splitting — do NOT convert imports. (Separate batch.)
- **PERF-09** asset conversion. Skip.
- `backend/` anything; `metrics.py`; tests-to-make-them-pass (see Gates).

## NAMED TRAPS (the whole point of this task — read twice)
1. **`React.memo` is useless unless props are referentially stable.** A memoized child still
   fed a fresh inline arrow (`onClick={() => ...}`) or inline array/object each render will
   re-render anyway (and you've added overhead for nothing). So A's two halves are ONE unit:
   memo the child AND `useCallback`/`useMemo` its props in the parent. Never do one without the
   other.
2. **DO NOT over-memoize `TrainingBoard` into staleness — this is the #1 risk.** `TrainingBoard`
   renders the live chess position + neural overlays. If you `React.memo` it but the props that
   carry the position/FEN/selected-finding/overlay data do NOT change reference when their VALUE
   changes, the board will FREEZE — it will stop updating when the user clicks a finding/steer
   card or steps a move. That is a severe, user-visible feature break. Before trusting the memo:
   click through several findings and steer cards and CONFIRM the board still updates every time.
   If any prop is a value that changes without a new reference, either fix the prop to be a stable
   reference that updates on value change, or DO NOT memo `TrainingBoard` at all. A slower-but-
   correct board beats a fast frozen one.
3. **Behavior-preserving only.** Do not change what any component renders, its props' shapes, its
   logic, or its output — only *when* it re-renders. No refactors "while you're in there."
4. Match the profile schema exactly (the TS2 fields `steer_findings`, `steer_summary`,
   `had_tal_move`, `steer.*` etc. were just added — don't disturb them).

## GATES (every one must pass before you call it done)
- `npm test` → **26/26 green** (the suite includes `ProfileReport.test.tsx`, `WeaknessRanking`,
  `RepertoireTrainer`, `TrainingQA`). Do NOT edit tests to make them pass. If a test legitimately
  needs a tweak because a prop is now stabilized, explain WHY in the report; don't delete assertions.
- `npm run build` → clean, and confirm the vendor chunks appear in `dist/assets/`.
- **Manual functional parity check (report the result):** (a) clicking findings AND steer cards
  still updates the board (Trap #2); (b) neural/attention overlays + arrows still render on the
  board; (c) all tabs still navigate; (d) the TS2 section still shows steer data.
- If you can, capture React DevTools Profiler render-count before/after for the finding-click
  interaction (the claimed PERF-03 win). If you can't run the profiler, say so — tests + parity
  are the hard gate.

## PROCESS & DELIVERABLE
- **One logical change per commit**, in this order, each independently revertable:
  1. Memoization (PERF-03 + PERF-06) — A.
  2. Vite chunking (PERF-08) — B.
- Write `UI_PERF_IMPL_REPORT.md`: per change → files touched (file:line), what changed, gate
  results (test/build), the manual parity-check outcome, and before/after evidence if available.
- Do NOT push. STOP for leader review. If anything about Trap #2 is uncertain, STOP and write the
  uncertainty into the report rather than guessing.
