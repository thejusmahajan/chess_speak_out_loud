# TASK FOR GEMINI (Instance 3) — UI performance reference + audit (REPORT/PLAN ONLY)

Make the case for a faster UI **without losing features or quality**. This instance is
**READ-ONLY on `frontend/`** — another Gemini instance is editing `frontend/src` concurrently,
so you produce DOCUMENTS ONLY (no code changes). Deliver a reusable best-practices reference
plus a grounded audit + prioritized plan; the leader (Claude) reviews before any implementation.

## The stack (grounded)
- **Vite + React + TypeScript**, `frontend/`. Entry `frontend/src/main.tsx`, `App.tsx`.
  Training UI in `frontend/src/components/Training/*`. A chess board + PGN viewer
  (`frontend/src/components/PgnViewer.tsx` + `public/lichess_assets/lichess-pgn-viewer.min.js`).
  Assets include `frontend/src/assets/hero.png`.
- The diagnosis profile can contain **hundreds of items** to render (213 findings + 263
  steer_findings) — long-list rendering is a likely hotspot.
- Build config: `frontend/package.json`, `vite`, `tsconfig.*`.

## Deliverable 1 — `UI_PERFORMANCE_BEST_PRACTICES.md` (the reference, like KAGGLE_BEST_PRACTICES.md)
A durable reference of React + Vite performance best practices **relevant to THIS app** (not a
generic listicle). Cover, with concrete techniques + code patterns + when-to-use:
- Rendering large lists (200+ findings/steer): virtualization/windowing, keys, pagination.
- Avoiding needless re-renders: `React.memo`, `useMemo`/`useCallback`, stable props, context
  splitting, state colocation.
- Code-splitting & lazy-loading heavy/rarely-used views (board, PGN viewer) via `React.lazy`/
  dynamic import; route/tab-level splitting.
- Bundle size: analyzing it (`vite build` + a visualizer), tree-shaking, trimming heavy deps,
  loading the lichess PGN viewer only when needed.
- Asset optimization: image sizing/formats (`hero.png`), fonts, SVG sprites.
- Vite specifics: build target, chunking, dependency pre-bundling, dev vs prod.
- Measurement: React Profiler, Lighthouse, Web Vitals — how to measure before/after so wins are
  provable, not assumed.
Cite sources; mark version-specific advice. Concrete over platitudes.

## Deliverable 2 — `UI_PERF_AUDIT.md` (grounded audit + prioritized plan)
Audit the ACTUAL current frontend against the reference and report REAL hotspots with `file:line`:
- Long lists rendered without virtualization? Un-memoized components re-rendering on every
  keystroke/tick? Heavy components loaded eagerly? Large bundle contributors? Unoptimized assets?
- For each finding: `issue | file:line | why it costs | expected impact (High/Med/Low) | effort |
  RISK to features/quality`.
Then a **prioritized implementation plan** (highest impact / lowest risk first), each item with
the specific change and how to verify the win (metric + before/after method). Nothing that
removes or degrades a feature.

## Constraints
- **REPORT/PLAN ONLY — do not modify any code** (avoid colliding with the bug-hunt instance).
- Preserve all features and visual/UX quality — speed must not cost function.
- Ground every claim in a real file:line; label estimates as estimates; give the measurement
  method so the leader can verify. STOP when the two docs are written; implementation follows
  after leader review.
