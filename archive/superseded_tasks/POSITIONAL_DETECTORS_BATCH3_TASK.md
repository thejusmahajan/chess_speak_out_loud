# WORKER TASK — Positional-fact detectors, batch 3 (colour-complex weakness)

Adds the last recurring gap the pilot showed: *"the bishop rules the dark squares," "Black has very weak
dark squares."* A colour complex is fuzzy, so the definition is pinned around a **strong discriminator that
also keeps it accurate**: a complex is only a real, persistent weakness when the **defending bishop of that
colour is gone**. Add to `backend/training/relational_facts.py`; extend `docs/POSITIONAL_DEFINITIONS.md`.
Do NOT touch `metrics.py`. Suite green, no push, STOP for review.

**ACCURACY IS THE POINT.** Emit a fact ONLY when both conditions below hold; otherwise NOTHING. Prove the
starting position and a normal both-bishops middlegame produce ZERO complexes.

## Definition (PINNED)
`color_complex_weakness(board, color) -> [fact]` — is `color`'s own camp weak on a square colour?
For each `W` in {LIGHT, DARK}:
1. **Defender gone (hard gate):** `color` has NO bishop on colour `W` (`board.pieces(BISHOP, color)` has no
   square of colour `W`). If `color` still has that bishop → **skip** (no fact).
2. **Holes on `W` in `color`'s own camp:** let `camp` = the 4 ranks nearest `color`'s back rank (rank
   indices 0–3 for White, 4–7 for Black). A square `sq` of colour `W` in `camp` is a **hole** if NO `color`
   pawn can ever attack it — i.e. neither adjacent file has a `color` pawn on a rank *behind* `sq` that
   could advance to attack it (**reuse the exact hole logic already in `outposts`** — factor it into a
   shared helper `_is_hole(board, sq, color)` and use it in both).
3. Emit a fact ONLY if the count of such holes `>= 3`.
Fact: `{kind:"color_complex", complex_color:"light"|"dark", holes:[sq,...], bishop_gone: True, text:
"Black has a weak dark-square complex — 4 dark squares in its own camp that no pawn can cover, and its
dark-squared bishop is gone: e5, f6, g5, h6"}`. (Threshold starts at 3; if the acceptance position needs a
small adjustment, tune it so the positive fires AND the negatives stay clean — never one at the other's
cost.) Add to the composed `relational_facts(...)` position facts.

## Reuse
`chess.BB_LIGHT_SQUARES`/`BB_DARK_SQUARES`, `board.pieces`, `chess.square_file/rank`, and the **existing
outpost hole logic** (do not re-derive it — share the helper).

## Acceptance tests (`backend/tests/test_positional_detectors_b3.py`)
POSITIVE:
1. **Steinitz weak dark squares:** `b2r4/2qn1k2/p3p1p1/1p1pPp1p/1P3P2/P2P1N2/5BPP/2R3K1 w - - 0 32`
   (Black has only a light-squared bishop on a8 — the dark-squared bishop is gone) →
   `color_complex_weakness(board, BLACK)` reports a **dark** complex. (Steinitz: "the bishop rules the dark
   squares.") *If the hole count in this exact position is <3, report the actual count and add a second
   clean synthetic positive rather than lowering the bar below 3.*
NEGATIVE / mutation (must NOT fire):
2. **Starting position** → no complex for either side (both bishops present → hard gate blocks it).
3. **Both-bishops middlegame** (e.g. `r1bq1rk1/pppp1ppp/2n2n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 7`)
   → no complex (each side still has both bishops).
4. **Bishop gone but no holes:** a position where a side lacks its dark bishop but its pawns still cover the
   dark squares (few/no holes) → no complex. (Small synthetic.)
Each test states why it fails on the wrong behavior.

## Gate
Backend suite green; add the tests; extend `docs/POSITIONAL_DEFINITIONS.md` with the def (hard gate +
hole threshold). No `metrics.py`; no push. Report `file:line`, the acceptance results (incl. the actual
dark-hole count in the Steinitz position), the negatives, and confirm zero false complexes on the start +
both-bishops middlegame. STOP for leader review — the leader hunts false complexes across varied positions
before it feeds any surface.
