# Terminal-position / 'a1a1' fix — review outcome & dispositions

Second-eye review by **Gemini 3.6 Flash (High)** on commit `cc3adb3`
(request: `GEMINI_TERMINAL_REVIEW.md`). Leader-verified; dispositions below.

## Verdict (confirmed by leader)
**The a1a1 crash fix is CORRECT and COMPLETE at the LC0 engine layer.** All three
LC0 entrypoints are guarded before touching the engine, and `fast_analyze` routes
through the guarded `_do_analyze`. Downstream metrics/steer loops tolerate the
synthetic terminal data (checkmate ±10000 white-POV, stalemate 0, empty
policy/best_moves) without exceptions or bad ranking. → **safe to re-run.**

## Findings & what we did
| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | `VerboseMoveStats` reset was inside `try` after the loop, not in `finally` → a mid-stream error leaves it ON for all later searches (state leak) | High | **FIXED** — reset moved to a `finally` with a `verbose_set` guard |
| 2 | `get_policy_distribution` had no wall-clock safety cap (could hang holding the lock) | Medium | **FIXED** — added `time=NODE_LIMIT_SAFETY_SECONDS` to the node Limit |
| 3 | `StockfishEngine.play()` unguarded for terminal positions | Low | **Deferred** — Stockfish is an offline baseline, not in the diagnosis path; guard when/if it's used online |
| 4 | 3 duplicated terminal checks; a 4th engine method could forget the guard → suggest a single choke-point | Design | **Noted** — kept explicit per-site guards for now (each has a different fallback: analyze→dict, policy/lines→[]); a single guarded dispatch is a good future refactor |
| 5 | Stage A `if not dist: raise "mock mode"` would misread `[]` from a terminal board as mock mode | Low | **Noted** — only reachable via a malformed PGN (a real game has no move after mate); Stage A boards are the position *before* the user's move, always non-terminal |

## Bottom line
The a1a1 fix stands; we additionally fixed the two concrete bugs it surfaced
(VerboseMoveStats leak, policy time cap). The choke-point refactor and Stockfish
guard are logged for later, not blockers.
