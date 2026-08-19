# WORKER TASK — Relational-fact extractor (north-star Tier B, hardened)

Build the **relational-fact extractor** that turns a position + LC0's line into the concrete
piece-relationship facts that carry a move's objective. This is the north-star core
(`docs/NORTH_STAR_decoding_lc0.md`, `LEADER_BIBLE.md` §1 motto). The leader has already **proven the
approach** (passed-pawn, attacks-on-queen, defender-removal all extract cleanly on the acceptance
position); your job is to build the correct, complete module and HARDEN the parts the prototype got
wrong. **Accuracy is the whole point — a false fact is a bad coach, worse than none. Reuse proven
primitives; never re-derive geometry.** No LLM. Cite `file:line`. Suite green, no push, STOP for review.

## Non-negotiable (the motto)
Every fact emitted MUST be true and checkable. NO false positives (the prototype's bug: it reported
"Bc5 x-rays to g1" from a loose collinearity check that didn't verify a clear ray). When in doubt,
emit nothing. Do NOT touch `metrics.py`.

## Inlined facts (reuse these — do not re-derive)
- python-chess: `board.attacks(sq)`, `board.attackers(color, sq)`, **`board.pin(color, sq)`** (returns the
  pin ray as a BB, `chess.BB_ALL` if not pinned — USE THIS for pins, not hand-rolled collinearity),
  `chess.SquareSet.between(a,b)`, `board.is_capture`, `board.piece_at`.
- `backend/lichess_tagger/cook.py` already has CORRECT pin logic: `pin_prevents_attack` /
  `pin_prevents_escape` (they use `board.pin`). Mirror that approach; do not invent your own.
- `backend/lichess_tagger/util.py`: `material_diff`, `squares_are_collinear`, `is_hanging`, piece values.
- Piece values for "valuable": Q/R (>=5) are the pieces whose attack/pin matters most.

## Build `backend/training/relational_facts.py`
Pure, deterministic, no engine. Functions returning typed facts (dicts with a `kind` + human string):

1. `protected_passed_pawns(board, pov) -> [fact]` — pawns with no enemy pawn able to stop them (same/adjacent
   file ahead), defended by a friendly piece; include promotion distance + defenders. *(Prototype: works.)*
2. `attacks_on_valuable(board, pov) -> [fact]` — pov pieces/pawns attacking an enemy Q or R. *(Works.)*
3. `pins_and_xrays(board, pov) -> [fact]` — **use `board.pin`** for real pins; a fact only when the
   pinned enemy piece is genuinely pinned to a MORE valuable piece and the ray is clear. NO false pins.
4. `conditional_pins(board, pov, square) -> [fact]` — the "what-if the opponent recaptures on `square`"
   case: if an enemy piece were placed on `square`, would it be pinned by a pov slider to a more valuable
   piece? (e.g. after ...bxc2, a White `Nxc2` is pinned by `Ba4` to `Qd1`.) This is the fact the static
   board misses.
5. `defender_removed(board_before, move, pov) -> fact|None` — if `move` captures an enemy piece, report
   which squares that piece controlled (esp. a friendly passer's path / promotion square). *(Works.)*
6. `king_pressure(board, pov) -> [fact]` — enemy king: shield pawns present, adjacent non-pawn defenders,
   king square. (Reuse the earlier logic; correct attribution.)
7. `relational_facts(fen, line_ucis, pov) -> {position_facts, per_move: [{move, creates, removes}]}` —
   apply 1–6 to the position and along the line, tagging what each move CREATES (a passer, an attack, a
   pin) and REMOVES (a defender). This is the composed output the leader/user judge for salience.

## Acceptance test (`backend/tests/test_relational_facts.py`) — MUST reproduce the proven read
Position `rn3rk1/pp3ppp/1q3n2/2b5/b1pN4/1P2P1PP/P1P1P1BK/R1BQ1R2 b - - 0 17`, pov = Black.
After `...c4b3` (White waits) `...b3c2`:
1. `protected_passed_pawns` includes **c2**, defended by **a4**, 1 from queening.
2. `attacks_on_valuable` includes **Pc2 attacks the Q on d1**.
3. `conditional_pins(..., c2)` reports **a White piece on c2 would be pinned by Ba4 to Qd1**.
4. `defender_removed(start, Bxd4=c5d4, Black)` reports the captured knight controlled **c2**.
5. **Negative / mutation:** `pins_and_xrays` on the start position must NOT report the bogus
   "Bc5 x-rays to g1" family — assert no pin fact naming g1 as the pinned-to target through a blocked ray.
Each test states why it fails on the wrong behavior.

## Gates
Reuse `lichess_tagger` + python-chess `board.pin` (no hand-rolled pins). Backend suite green; add the
tests; no `metrics.py`; no push. Report `file:line`, the acceptance results, the mutation rationale, and
confirm zero false pins. STOP for leader review — the leader validates salience with the user before this
feeds any surface.
