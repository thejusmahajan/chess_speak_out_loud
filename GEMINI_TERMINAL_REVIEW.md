# Gemini 3.6 Flash (High) — REVIEW (READ-ONLY): the terminal-position / 'a1a1' crash

**Direct request:** be a second set of eyes on a crash fix. **Read the code, give
your perspective, change NOTHING.** We'll decide what to do after your opinion.
Follow `WORKER_AGENT_COOKBOOK.md`: back claims with exact `file:line` evidence.

## The problem
On the Colab A100, the diagnosis pipeline crashes with:
```
chess.engine.EngineError: invalid uci (use 0000 for null moves): 'a1a1'
```
Cause: lc0 emits `bestmove a1a1` for a **terminal position** (no legal moves —
checkmate or stalemate). python-chess's `_parse_uci_bestmove` rejects `a1a1` and
raises `EngineError`, which corrupts the UCI protocol and kills the whole run.
It triggers when a **candidate/tree move delivers mate** (or stalemates), so the
position handed to the engine afterward is game-over. It's data-dependent — the
30-game `test_subset.pgn` hits it; earlier corpora didn't.

It bit us **twice**: first in Stage B/TS2 via `analyze()`, then again in Cell 8
(repertoire) via a *different* engine method — which is the whole reason for this
review.

## The fix under review (commit cc3adb3, `backend/engine_manager.py`)
lc0 is called from **three** methods; each now short-circuits terminal positions
BEFORE touching the engine:
1. `_do_analyze` (used by `analyze`) → `return terminal_analysis(board)` — a
   synthetic dict: checkmate → `evaluation` **±10000 white-POV** (−10000 if the
   side to move is mated, +10000 if the opponent is mated), stalemate → `0`, with
   a matching `wdl`; `best_moves`/`pv_lines` empty, `nodes` 0.
2. `_get_policy_distribution_impl` (used by Stage A, **TS2, repertoire**) →
   `return []` (no legal moves = no policy).
3. `_search_lines_impl` (Calculation Glow) → `return []`.
See also `terminal_analysis()` (module-level) and `backend/tests/test_terminal_analysis.py`.

## What we want your perspective on (read + reason, cite lines)
1. **Completeness.** Are those really the only 3 places code talks to lc0? Grep
   the whole repo for engine calls (`self.engine.analyse`/`.analysis`/`.play`,
   `engine.analyze`/`.get_policy_distribution`/`.search_lines`/`.fast_analyze`).
   Any call site — in `engine_manager.py`, `pipeline.py`, `select_repertoire.py`,
   `gems.py`, `app.py`, anywhere — that can receive a terminal FEN and is NOT
   guarded? `fast_analyze` in particular.
2. **Correctness of the synthetic values.** Is the white-POV sign right for both
   colors mated? Is `±10000` consistent with how `metrics.eval_cp_number` and the
   consumers (`confirmation_swing`, `tactical_complexity`, `steer_candidates`)
   treat evals? Does an empty `best_moves`/`policy` break any of those (e.g.
   `narrowness`, `policy_trap`, `eval_cp_number(None)`)? Trace it.
3. **Downstream tolerance.** In `pipeline.py`, when `get_policy_distribution`
   returns `[]` for a mating candidate in TS2, does the loop handle it cleanly, or
   does it mis-count / mis-rank? Should a move that forcibly mates even be a
   "steer" candidate, or be surfaced differently?
4. **Deeper design question.** Is guarding at the engine layer the right call, or
   should the pipeline avoid *generating* terminal positions for the engine in the
   first place (e.g. detect a mating candidate upstream)? And: three duplicated
   `if is_checkmate() or is_stalemate()` checks — would a **single choke-point**
   (one internal wrapper all engine entrypoints pass through) be more robust
   against the next new call site? Recommend, don't implement.
5. **Other lc0 landmines.** Any *non-terminal* inputs that could similarly make
   lc0 emit something python-chess rejects (illegal/ malformed FEN, positions with
   a single legal move, insufficient-material draws, 960/variant FENs)? Anything
   else in this integration that's fragile?

## Deliverable
A written analysis (paste it back, or a short `TERMINAL_REVIEW_NOTES.md`):
- a **verdict** — is the fix correct + complete, or are there gaps? List them with
  `file:line`.
- your answer to #4 (choke-point vs per-site) with a recommendation.
- any additional landmines from #5.
**Do not edit code.** The leader verifies your findings before any change.
