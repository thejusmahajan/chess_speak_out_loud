# Positional Fact Definitions (Batch 1)

This document contains the ground-truth definitions for positional-fact extractors implemented in `backend/training/relational_facts.py`.

---

## 1. Pawn Weaknesses (`pawn_weaknesses`)

For a pawn of color `color` on square `s` (file `f`, rank `r`), where `dr = +1` for White and `-1` for Black:

- **Isolated Pawn**: `color` has no pawn on adjacent files (`f-1` or `f+1`) on any rank (0–7).
- **Doubled Pawns**: `color` has more than one pawn on file `f` (reported once per file listing all pawns on that file).
- **Backward Pawn**: A pawn is backward if ALL three conditions hold:
  1. **No friendly support**: No friendly pawn on an adjacent file (`f-1` or `f+1`) sits at a rank *not ahead* of `r` (i.e. no adjacent friendly pawn with `rank_adj * dr <= r * dr`).
  2. **Stop square blocked/controlled**: Its stop square (`s + dr`) is controlled OR occupied by an enemy pawn.
  3. **Semi-open file**: No friendly pawn exists on file `f` ahead of `s` (i.e. `rank * dr > r * dr`).

### Fact Schema
```json
{
  "kind": "pawn_weakness",
  "weakness": "isolated | doubled | backward",
  "square": "e6",
  "color": "White | Black",
  "attacked": true,
  "text": "Black's e6 pawn is backward (and under attack)"
}
```

---

## 2. Tied Defenders (`tied_defenders`)

A friendly piece (excluding pawns and kings) of color `color` is **tied to defense** if:
1. It defends a friendly pawn `W` on square `W_sq` (i.e. the piece square is in `board.attackers(color, W_sq)`).
2. The pawn `W` is a identified weakness (`isolated`, `backward`, or `doubled`).
3. The pawn `W` is currently attacked by at least one enemy piece (`board.attackers(not color, W_sq)` is non-empty).

### Fact Schema
```json
{
  "kind": "tied_defender",
  "piece": "R | N | B | Q",
  "square": "d7",
  "defends": "e6",
  "text": "The B on d7 is tied to the defence of the weak e6 pawn"
}
```

---

## 3. Outposts (`outposts`)

An enemy piece (Knight, Bishop, or Rook) on square `sq` is an **outpost** in `color`'s structure when:
1. `sq` is located in `color`'s half of the board (ranks 1–4 for White's half as defended against Black; ranks 5–8 for Black's half).
2. **Hole condition**: No `color` pawn can EVER challenge `sq` — i.e. neither adjacent file (`file(sq)-1` or `file(sq)+1`) contains a `color` pawn on a rank behind `sq` (where `pawn_rank * dr < sq_rank * dr`).

### Fact Schema
```json
{
  "kind": "outpost",
  "enemy_piece": "N | B | R",
  "square": "d5",
  "defender_color": "Black",
  "text": "The enemy N on d5 sits on an outpost — a hole Black can no longer challenge with a pawn"
}
```
