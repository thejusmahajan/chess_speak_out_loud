# WORKER TASK — Positional-fact detectors, batch 2 (piece activity + control of key lines)

Continues batch 1. Adds the vocabulary the pilot demanded: *"White's active bishop on d3,"* *"the c8
bishop's activity diminished,"* *"controls the 7th rank."* Add to `backend/training/relational_facts.py`;
extend `docs/POSITIONAL_DEFINITIONS.md`. Do NOT touch `metrics.py`. Suite green, no push, STOP for review.

**ACCURACY IS THE POINT.** "Active"/"bad" are judgment words — so they are earned ONLY from countable
metrics with conservative thresholds, never a guess. Report neutral pieces as NOTHING (silence beats a
wrong label). Prove zero false positives on the negatives.

## Definitions (PINNED — implement exactly; reuse python-chess only)

### 1. `rook_on_seventh(board, color) -> [fact]`
A `color` rook or queen on the enemy's second rank (**rank index 6 for White, rank index 1 for Black**).
Fact: `{kind:"rook_seventh", piece, square, text:"White's rook on c7 occupies the 7th rank"}`. (Placement
only — the classic motif; do not try to judge its effect.)

### 2. `open_file_pieces(board, color) -> [fact]`
A `color` rook or queen on file `f` where: **open** = no pawns of EITHER color on `f`; **half-open** = no
`color` pawns on `f` but the enemy has ≥1. Fact: `{kind:"file_control", piece, square, file, kind_of:
"open"|"half-open", text:"Black's rook on the open d-file"}`. (Files with a friendly pawn: no fact.)

### 3. `bishop_quality(board, color) -> [fact]`  (metric-based; conservative)
For each `color` bishop on `sq`:
- `own_pawns_on_color` = number of friendly pawns on squares of the **same color as `sq`**
  (`chess.BB_LIGHT_SQUARES`/`BB_DARK_SQUARES`, matched to the bishop's square color).
- `mobility` = count of squares in `board.attacks(sq)` NOT occupied by a friendly piece.
Emit a fact ONLY at a clear extreme (else nothing):
- **bad / restricted** when `own_pawns_on_color >= 4` (its own pawns wall it in). text: `"Black's c8 bishop
  is a bad bishop — 5 of its own pawns sit on its colour, restricting it (mobility 2)"`.
- **active** when `own_pawns_on_color <= 1` AND `mobility >= 7` (unobstructed, long diagonals). text:
  `"White's d3 bishop is active — unobstructed by its own pawns, controlling 10 squares"`.
Always include the raw numbers (`own_pawns_on_color`, `mobility`) in the fact — the metric is the evidence.

## Reuse
`board.pieces`, `board.attacks(sq)`, `board.piece_at`, `chess.square_file/rank`, `chess.BB_LIGHT_SQUARES` /
`BB_DARK_SQUARES`, `chess.SquareSet`. Match the existing `relational_facts.py` style. Also add these to the
composed `relational_facts(fen, line_ucis, pov)` position facts.

## Acceptance tests (`backend/tests/test_positional_detectors_b2.py`)
POSITIVE (GM-annotated pilot positions):
1. **Rook on 7th:** `b2r4/2qn1k2/p3p1p1/1p1pPp1p/1P3P2/P2P1N2/5BPP/2R3K1 w - - 0 32`, play `c1c7` →
   `rook_on_seventh(WHITE)` reports the c7 rook. (Steinitz: "controls the 7th rank.")
2. **Active bishop:** `r1bqr1k1/pp1nbpp1/2p2n1p/3p4/3P4/2NBPNB1/PPQ2PPP/R4RK1 b - - 7 12` →
   `bishop_quality(WHITE)` flags the **d3** bishop **active**. (Capablanca: "White's active bishop on d3.")
3. **Bad bishop:** `r1b1k2r/3nbppp/pq2p3/1p1pP3/1P3P2/P2P1N2/3BQ1PP/R2NK2R b KQkq - 0 14`, play `f7f5` →
   `bishop_quality(BLACK)` flags the **c8** bishop **bad/restricted**. (Steinitz: "c8 bishop's activity
   diminished.")  *If the thresholds don't classify these two correctly, tune them so BOTH the GM cases and
   the negatives below hold — do not force one at the cost of the other.*
NEGATIVE / mutation (must NOT fire):
4. **No false 7th:** a rook on its own back rank → `rook_on_seventh` empty.
5. **No false "active":** a fianchetto bishop hemmed by its own pawns → NOT flagged active. And a bishop on
   a genuinely open long diagonal is NOT flagged "bad." (Two small fixtures.)
6. **No false open-file:** a rook on a file that still has a friendly pawn → no `file_control` fact.
Each test states why it fails on the wrong behavior.

## Gate
Backend suite green; add the tests; extend `docs/POSITIONAL_DEFINITIONS.md` with the three defs (including
the exact thresholds). No `metrics.py`; no push. Report `file:line` per detector, the acceptance results
(Steinitz 7th + Capablanca active-d3 + Steinitz bad-c8), the mutation rationale, the raw metric numbers for
the two bishops, and confirm zero false positives. STOP for leader review — the leader re-runs the detectors
across varied positions hunting for false "active"/"bad" labels before this feeds any surface.
