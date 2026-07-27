# TASK FOR GEMINI — Work through the UI issues (triage + fix), grounded in the theme definitions

The user filed real UI/UX + correctness issues (`scratch/temp/ui_issues.txt`). Work through ALL of
them, but with discipline: **reproduce + root-cause each (cite file:line), fix the clear/low-risk
ones, and write a plan for the big/risky ones — do NOT make large blind rewrites.** Read
`docs/THEME_DEFINITIONS.md` FIRST — it is the ground truth for anything naming a tactical theme.
Output `UI_ISSUES_TRIAGE.md` (per-issue: repro, root cause file:line, FIXED or PLAN, risk). Keep
existing tests green; add tests for fixes. No push. STOP for leader review.

## Ground rule for #8 (sacrifice) — DO NOT patch superficially
Per `THEME_DEFINITIONS.md`, "sacrifice" detection is FUNDAMENTALLY wrong: `had_tal_move` is a
complexity differential with NO material check, so quiet moves are mislabelled sacrifices. **You may
NOT invent a new sacrifice heuristic.** The correct fix (material-over-forced-line, reusing
`lichess_tagger`) is leader-owned and will be specced separately. For this task: (a) confirm/repro the
root cause with file:line, (b) recommend the SacDrill + Sharp-Openings "sacrifice" surfaces be
**relabelled honestly ("sharp position") or disabled** until the leader's material-based detector
lands. That's the only acceptable interim handling.

## The issues (from ui_issues.txt) — repro, root-cause, then FIX or PLAN each
1. **Startup auto-analysis** — the app loads a PGN and starts the engine immediately, hogging
   resources. FIX: make analysis **user-initiated** (a toggle/button; no auto-analyze on load).
2. **Weakness Profile is not actionable** — clicking an opening (e.g. "A02 26.4% blind") or a motif
   ("clearance 133 blind / 95 missed") does nothing. PLAN (likely a feature): clicking should open an
   **analysis board at the weakness position, showing the full game up to that point**, explaining
   where it went wrong; motif counts should be clickable → the set of those positions; add a "generate
   drill set from these" action. "Notable findings" tiles are inactive — make them active or justify.
3. **Deck build is very slow** — profile the bottleneck (engine calls? cache misses? re-analysis?).
   Root-cause with evidence; FIX if it's a clear inefficiency, else PLAN.
4. **"New deck" returns the OLD deck without shuffle** — verify against the just-merged stable-id +
   SRS-aware ordering; determine why a rebuild isn't producing a fresh/reordered deck (caching? same
   set id? the frontend not re-fetching?). FIX.
5. **Repertoire lines too shallow** — trained openings stop at 4–5 moves; real lines go deeper. Root-
   cause the depth limit (`build_repertoire_tree` max_line_len / node pruning); PLAN a deeper build.
6. **Train Opening (Black) finds nothing** — debug why the black repertoire is empty (ECO/color
   filtering? now that ECOs are backfilled?). FIX or PLAN with the root cause.
7. **Intuition: LC0 ranked policy not interactive** — the reveal's policy moves should be **clickable**
   and show a short variation explaining WHY each is good. PLAN/FIX (needs a short PV per move).
8. **Sacrifice is bogus** — see the ground rule above. Repro + relabel/disable, do NOT re-heuristic.
9. **"Play it out vs LC0" doesn't work** — debug the C1/C2 play-out end-to-end (engine availability?
   the endpoint? the frontend wiring? mock vs live?). Root-cause with file:line; FIX.
10. **Sharp Openings don't explain WHY they're sharp** — an opening can't be "sharp" to the user
    without SHOWING the variation/line. PLAN: surface the continuation/why (ties to the analysis-board
    work in #2 and the real sacrifice detector in #8).
11. **Progress bar inactive / no data** — wire it to real SRS/attempt stats (`attempts.py`
    `get_stats`/`due_drills`, the intuition/sac stats). FIX.

## Constraints & gates
- Ground every theme claim in `THEME_DEFINITIONS.md`. Do NOT touch `backend/training/metrics.py`
  (leader-owned) or invent a sacrifice heuristic (#8). Cite file:line for every root cause.
- FIX only what's clear/low-risk this pass; everything else is a written PLAN in `UI_ISSUES_TRIAGE.md`
  for leader review (don't sprawl into large speculative rewrites).
- Keep backend (195) + frontend (45) suites green; add tests for any fix. `npm run build` clean.
  No push. STOP for leader review.
