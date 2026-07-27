# THEME-TAGGER FIX SPEC — drive Lichess `cook()` correctly + real sacrifice (D1–D5)

Fixes the deviations in `docs/LICHESS_DEVIATIONS_REPORT.md`. Grounded in `docs/THEME_DEFINITIONS.md`.
This is leader-owned metric-correctness work — the math/structure below is PINNED; implement verbatim.
The core insight: Lichess's `Puzzle`/`cook` assume the game starts ONE ply before the solver's first
move (opponent plays a "setup" move, then the solver), and `pov = not game.turn()`. We currently feed
`cook` the flagged position directly (solver already to move) → **inverted pov + shifted parity +
dummy cp**. Fix = reconstruct the Lichess structure with the REAL prior move + real eval.

## Grounded pipeline facts
- Stage A (`pipeline.py:202-258`) iterates `game.mainline()` with a live `board`; at a flagged user
  move, `board` == `fen_before` (user to move) and `board.move_stack` HAS the full history — so the
  opponent's prior move + the pre-position are available HERE.
- Stage B (`pipeline.py:288`) rebuilds `board_before = chess.Board(fen_before)` (fresh, NO history) and
  calls `MotifDetector.analyze_pv(fen_before, pv_san)` (`tactics.py`). This is where pov/parity break.
- `tactics.py:analyze_pv` builds a Puzzle from `fen_before` + PV and calls `cook`; `Puzzle.pov = not
  game.turn()`; `cook` uses `puzzle.cp` (`>200` ⇒ "advantage"). We pass `cp=500` (fake).

## PHASE A (dispatch now) — correct the motif tagger (fixes D2/D3/D4)
### A1. Stage A: capture the setup move + pre-position for each flagged finding
Where a position is flagged (Stage A, the `board.turn == user_color` flag site), store on the flagged
dict, guarded by `board.move_stack`:
- `setup_uci = board.peek().uci()` (the opponent's move that reached `fen_before`), and
- `pre_fen`: `tmp = board.copy(); tmp.pop(); pre_fen = tmp.fen()` (position with the OPPONENT to move).
If `board.move_stack` is empty (flagged position is move 1 — rare), set `setup_uci=None`, `pre_fen=None`.

### A2. `tactics.py:analyze_pv` — new signature + Lichess-correct construction
`analyze_pv(pre_fen: str|None, setup_uci: str|None, pv_san: list[str], cp: int) -> set[str]`:
- If `pre_fen`/`setup_uci` is None OR `pv_san` empty → return `set()` (can't build a valid puzzle;
  do NOT guess).
- Build `board = chess.Board(pre_fen)`; `game.setup(board)`; add moves **`[setup_uci] + <pv ucis>`**
  to the mainline (convert `pv_san` on the running board; if any move is illegal, return `set()`).
- `Puzzle(id="lc0_pv", game=game, cp=cp)` → now `pov = not game.turn() = not (opponent) = the user`,
  and mainline parity matches Lichess (setup move = mainline[1]). `cook(puzzle)` → tags.
- **`cp` must be the REAL eval in the SOLVER's POV**: caller passes `cp = eval_best_cp` if the user is
  White else `-eval_best_cp` (white-POV eval → mover POV). No more hardcoded 500.

### A3. Stage B: pass the real args
Replace the `analyze_pv(flagged["fen_before"], pv_san_list)` call with
`analyze_pv(flagged["pre_fen"], flagged["setup_uci"], pv_san_list, cp_mover)` where
`cp_mover = b_data["eval_best_cp"] if mover_is_white else -b_data["eval_best_cp"]` (reuse the same
`mover_is_white` already computed at `pipeline.py:336`).

### A4. Tests (`test_tactics_pov.py`) — mutation-check; these must FAIL on the OLD code
Build small hand-made lines with `python-chess` (no engine):
1. **Real sacrifice, mover's side**: a line where the SIDE TO MOVE at `fen_before` gives up ≥2 material
   over the line and stays winning → `"sacrifice"` IS in the tags.
2. **Material-WINNING line (the old false positive)**: a line where the side to move WINS material
   (opponent ends down) → `"sacrifice"` is NOT in the tags. (This is exactly the `g004-p031` case the
   old code mislabelled — the test must catch it.)
3. **POV**: assert the constructed `Puzzle.pov` equals the side to move at `fen_before` (NOT inverted).
4. **cp**: with a real losing/quiet eval passed, the position is NOT force-tagged `"advantage"`.
5. **Edge**: `pre_fen=None` → `set()`.

## PHASE B (spec after A audited) — real "sacrifice" sourcing + relabel (fixes D1)
- **Re-source the SacDrill + Sharp-Openings "sacrifice"** from findings/positions whose corrected
  motifs (Phase A) include `"sacrifice"` (real, material-based) — NOT `had_tal_move`. (Bonus: a finding
  whose BEST line is a sacrifice = "a sound sacrifice you missed" — perfectly on-theme for J7.)
- **Relabel `had_tal_move`/`complexity`/`steer`** everywhere (metrics.py is leader-owned — leader will
  do this edit) as a **"sharpness"** signal, never "sacrifice"/"Tal". UI copy updated to match.

## PHASE C (spec after B) — re-tag the existing 100-game profile + re-verify
The stored profile lacks `pre_fen`/`setup_uci`. Re-tag WITHOUT a Kaggle re-run: backfill `pre_fen`/
`setup_uci` from the corpus PGN (locate each finding's game+ply, take the prior move — same alignment
approach as `eco_backfill.py`), re-run the corrected `analyze_pv` on stored PVs, rewrite `motifs` +
`by_motif`. Then **re-verify** usual-suspects / by_motif / sharpness on the corrected tags — the
"sacrifice/defensiveMove" ranking is only trustworthy AFTER this.

## Constraints & gates
- Ground in `THEME_DEFINITIONS.md`. Phase A does NOT touch `metrics.py` (only `tactics.py` +
  `pipeline.py` Stage A/B). Reuse `lichess_tagger` — never re-derive material. Suite stays green
  (some motif-dependent test expectations WILL change — update them to the corrected behavior and
  explain each in the report; do not delete assertions). No push. STOP for leader review.
- Dispatch **Phase A only**; leader audits (empirically re-run on `g004-p031`: it must NOT be
  "sacrifice"; pov must equal side-to-move) before Phase B.
