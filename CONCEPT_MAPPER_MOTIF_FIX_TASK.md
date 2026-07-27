# WORKER TASK — fix the silently-broken tactical-motif observation in concept_mapper

**Token discipline:** all facts are inlined below (the leader already did the recon) — do NOT re-Read/Grep to
rediscover signatures or the bug. Cite `file:line` for every change. Do NOT touch `backend/tactics.py`
(its `analyze_pv` is CORRECT) or `backend/training/metrics.py` (leader-owned). Suite green, no push, STOP for
leader review.

## The confirmed bug (live since theme-tagger Phase A)
`backend/concept_mapper.py:117` calls the **legacy 2-arg** form `MotifDetector.analyze_pv(fen, top_pv)`.
`tactics.py:24-31` handles legacy calls by reassigning `pv_san = setup_uci` and setting `setup_uci = None`,
then the guard `if not pre_fen or not setup_uci or not pv_san: return set()` fires (setup_uci is None) →
**it ALWAYS returns `set()`.** So the "LC0's primary forcing line involves tactical motifs: …" observation
NEVER appears, for any position. Silent (no crash) because the feature just degrades to "no motifs."

## The correct contract (what `analyze_pv` actually needs — DO NOT change it)
`MotifDetector.analyze_pv(pre_fen, setup_uci, pv_san, cp) -> set[str]`:
builds a game starting at `pre_fen` (OPPONENT to move), pushes `setup_uci` (the opponent move that reaches
the analyzed position), then the solver's `pv_san` line. This makes `Puzzle.pov = the side to move at the
analyzed position` (the solver) and the mainline parity correct. `cp` = the eval in the SOLVER's POV.
It returns `set()` (safely) if `pre_fen`/`setup_uci` is None or `pv_san` empty.
**Consequence:** a bare FEN with no known prior move CANNOT be tagged correctly — and must NOT be tagged at
all (tagging it via the 2-arg path is the bug; tagging it with a fabricated setup is worse).

## Grounded caller facts
`analyze_position(fen: str, engine_analysis: Optional[dict] = None)` — `concept_mapper.py:80`. Called from:
- `app.py:263` — `POST /analyze` (`AnalyzeRequest`): an ARBITRARY position, generally NO move history.
- `app.py:439` — `POST /analyze_pgn`: walks a PGN; at each `fen_before` it HAS the prior move (the game
  context). This is the path where motifs actually matter (game review).
`engine_analysis` shape (from `lc0_engine.analyze`): `{"evaluation": <white-POV int | "M5">, "best_moves":
[...], "pv_lines": ["<SAN SAN …>", …]}`. `top_pv = pv_lines[0]` is a space-joined SAN string (the block
already extracts it at `concept_mapper.py:113-116`).
Eval→mover POV: `cp = metrics.eval_cp_number(evaluation) or 0; cp = cp if <side to move at fen> == white
else -cp`. Side to move: `chess.Board(fen).turn == chess.WHITE`. (`from backend.training import metrics`.)
Pipeline Stage A already captures `setup_uci`/`pre_fen` at a game node — mirror that pattern
(`pipeline.py:207-242`): `setup_uci = board.peek().uci()`, `tmp = board.copy(); tmp.pop(); pre_fen =
tmp.fen()`, guarded by `board.move_stack`.

## Requirements
1. **`analyze_position` signature** → add optional `pre_fen: Optional[str] = None`, `setup_uci: Optional[str]
   = None`. In the motif block (`concept_mapper.py:106-130`): call `MotifDetector.analyze_pv(pre_fen,
   setup_uci, top_pv.split() if isinstance(top_pv, str) else top_pv, cp_mover)` **only when `pre_fen` AND
   `setup_uci` are both present** (and `top_pv` non-empty). Otherwise **skip the motif observation entirely**
   — do NOT call the 2-arg form. (`top_pv` is a SAN string; `analyze_pv` wants a SAN list → `.split()`.)
   Compute `cp_mover` per the eval→mover-POV rule above.
2. **`/analyze_pgn` (`app.py:439`)** — derive `setup_uci` + `pre_fen` from the game walk (the move that
   reached `fen_before`, via the Stage-A pattern) and pass them to `analyze_position(...)`. This restores
   correct motifs on the game-review path.
3. **`/analyze` (`app.py:263`)** — leave `pre_fen`/`setup_uci` as None (bare FEN, no history) → motifs are
   honestly skipped. (A future frontend change can send the prior move; OUT OF SCOPE.)

## Tests (`backend/tests/test_concept_mapper_motifs.py`) — mutation-checked, no engine
1. **Real tactic tagged**: build a fixture `fen` (solver to move) with the correct `pre_fen`+`setup_uci` and
   an `engine_analysis` whose `pv_lines[0]` is a real forcing tactic (e.g. a fork/mate line) → the returned
   observations include a `category=="tactical_motifs"` entry. (Mutation: fails if the motif call is dropped
   or fed the wrong pov.)
2. **No context → no false observation**: call `analyze_position(fen, engine_analysis=...)` WITHOUT
   `pre_fen`/`setup_uci` → observations contain NO `tactical_motifs` entry, and it does not raise. (Mutation:
   fails if the old silent-empty 2-arg path or a crash returns.)
3. **Eval POV**: solver is black, `evaluation` white-POV positive → assert `cp_mover` passed is negated (use
   a spy/monkeypatch on `MotifDetector.analyze_pv` to capture the `cp` arg). (Mutation: fails if flip dropped.)

## Gate
`... -m pytest backend/tests` green; add the 3 tests; `npm run build` not required (backend only). No push.
Report: `file:line` per change, the 3 tests + why each fails on the wrong behavior, and confirm you did NOT
touch `tactics.py`/`metrics.py`. STOP for leader review.
