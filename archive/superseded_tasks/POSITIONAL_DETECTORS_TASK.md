# WORKER TASK — Positional-fact detectors, batch 1 (pawn weaknesses + tied defenders + outposts)

Extend the relational-fact extractor toward the POSITIONAL vocabulary that grandmaster annotations use.
Driven by pilot data: on Steinitz/Capablanca positions our tactical extractor caught the pin but was blind
to *"e6 is backward,"* *"a piece tied to its defence,"* *"the weak dark squares."* This batch adds those.

**ACCURACY IS THE WHOLE POINT — a false positional fact is a bad coach, worse than none (the motto).** The
definitions below are PINNED; implement them verbatim, reuse python-chess primitives, and prove zero false
positives on the negative tests. Add to `backend/training/relational_facts.py`. Do NOT touch `metrics.py`.
Ground the definitions in a new `docs/POSITIONAL_DEFINITIONS.md`. Suite green, no push, STOP for review.

## Definitions (PINNED — implement exactly; `dr = +1` for White, `-1` for Black = direction of advance)

### 1. `pawn_weaknesses(board, color) -> [fact]`
For each `color` pawn on square `s` (file `f`, rank `r`):
- **isolated**: `color` has NO pawn on file `f-1` or `f+1` (any rank).
- **doubled**: `color` has another pawn on file `f` (report once per file, listing the squares).
- **backward**: ALL of —
  (a) no friendly pawn on an adjacent file (`f-1`/`f+1`) sits at a rank *not ahead* of `r`
      (i.e. no adjacent friendly pawn with `rank*dr <= r*dr`) — so no pawn can support it; AND
  (b) its stop square `s+dr` is **controlled OR occupied by an enemy pawn** (it cannot safely advance); AND
  (c) semi-open for it: no friendly pawn on file `f` ahead of `s`.
Each fact: `{kind:"pawn_weakness", weakness:"isolated"|"doubled"|"backward", square, color, attacked: bool}`
where `attacked` = the pawn is currently attacked by an enemy piece. `text` e.g. `"Black's e6 pawn is
backward (and under attack)"`.

### 2. `tied_defenders(board, color) -> [fact]`
A `color` piece (not pawn/king) is **tied** if it defends a friendly pawn `W` that is BOTH a weakness
(isolated/backward/doubled, from #1) AND currently attacked by an enemy piece, and the piece is in
`board.attackers(color, W)`. Fact: `{kind:"tied_defender", piece, square, defends: W_square, text:
"The <piece> on <sq> is tied to the defence of the weak <W> pawn"}`.

### 3. `outposts(board, color) -> [fact]`  (color = the side whose HALF contains the hole)
An **enemy** piece (knight/bishop/rook) on square `sq` is an outpost when: `sq` is in `color`'s half
(ranks 1–4 for White's half seen by Black, symmetric), and NO `color` pawn can EVER attack `sq` — i.e.
neither adjacent file (`file(sq)±1`) has a `color` pawn on a rank behind `sq` (one that could advance to
attack it). Fact: `{kind:"outpost", enemy_piece, square, text:"The enemy <piece> on <sq> sits on an
outpost — a hole <color> can no longer challenge with a pawn"}`. (Occupied outposts only in this batch;
"controlled holes" and full color-complexes are a later batch — do NOT approximate them.)

## Reuse (don't reinvent)
python-chess: `board.pieces(PAWN, color)`, `board.attacks(sq)`, `board.attackers(color, sq)`,
`board.piece_at`, `chess.square_file/rank/square`. The existing `relational_facts.py` helpers + style.

## Acceptance tests (`backend/tests/test_positional_detectors.py`)
POSITIVE (must fire — these are the GM-annotated positions the pilot used):
1. **Backward:** `r1b1k2r/3nbppp/pq2p3/1p1pP3/1P3P2/P2P1N2/3BQ1PP/R2NK2R b KQkq - 0 14`, play `f7f5`;
   `pawn_weaknesses(board, BLACK)` includes **e6 backward**. (Steinitz–Sellman — GM: "e6 is now backward.")
2. **Outpost:** a position with a White knight on **d5** that no black pawn can attack (e.g.
   `3rk3/pp3ppp/8/3N4/8/8/PPP2PPP/3RK3 b - - 0 1`) → `outposts(board, BLACK)` reports the d5 knight.
3. **Tied defender:** a position with a weak, attacked black pawn defended by exactly one black piece →
   `tied_defenders(board, BLACK)` reports that piece. (Construct a clean synthetic fixture.)
NEGATIVE / mutation (must NOT fire — zero false positives):
4. **No false backward:** the starting position → `pawn_weaknesses(...,WHITE)` reports NO backward pawns
   (every pawn is defensible / can advance). Assert empty backward list.
5. **No false outpost:** a knight on d5 that a black c- or e-pawn CAN still attack (pawn on c6/e6 behind it)
   → `outposts` does NOT report it.
Each test states why it fails on the wrong behavior.

## Gate
Backend suite green; add the tests; write `docs/POSITIONAL_DEFINITIONS.md` (the pinned defs above, as the
grounding record). No `metrics.py`. No push. Report: `file:line` per detector, the acceptance results
(esp. that Steinitz's e6 is flagged backward and the negatives are clean), the mutation rationale, and
confirm zero false positives. STOP for leader review — the leader re-runs the acceptance against the master
positions before this feeds any surface.
