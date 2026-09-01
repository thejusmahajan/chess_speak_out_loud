# AUDIT — `2026-09-01_tal-configuration-steering-contemplation`

**Auditor:** leader (Opus 5), 2026-09-01
**Verdict: ACCEPT with two corrections.** No fabrication found. Every checkable number is real.

---

## 1. Numbers re-run against disk

All queries executed by the leader against `data/puzzles/puzzles.sqlite` and the working tree.

| claim in report | measured | verdict |
|---|---|---|
| `puzzles.sqlite` 1,336.73 MB | 1336.73 MB | ✅ exact |
| `puzzles` 5,527,851 rows | 5,527,851 | ✅ exact |
| `puzzle_flags` 1,472,045 rows | 1,472,045 | ✅ exact |
| `quiet_first` 401,437 | 401,437 | ✅ exact |
| `opening_motifs` 57,033 | 57,033 | ✅ exact |
| rating avg 1482.01, min 399, max 3347 | 1482.01 / 399 / 3347 | ✅ exact |
| solution lengths 4:2,790,084 6:1,487,690 2:783,476 8:332,992 | identical | ✅ exact |
| `steer.jsonl` 8,845 records, 33.80 MB | 8,845 lines, 35,439,821 B = 33.80 MB | ✅ exact |
| `steer_max_loss_cp: 60`, `steer_min_eval_cp: -60` | `metrics.py:102-103` | ✅ exact |
| named functions in `metrics.py` / `neural_vision.py` | all present | ✅ |
| line counts: 788 / 501 / 711 / 92 | 787 / 500 / 710 / 91 | ⚠ off by exactly 1, all four — a counting convention, not a claim about content. Harmless. |

**Citations** — all four are real and correctly attributed: McGrath et al. 2022 PNAS (arXiv:2111.09259), Silver et al. 2018 *Science* 362 (arXiv:1712.01815), Ng/Harada/Russell ICML 1999, McIlroy-Young et al. KDD 2020 Maia (arXiv:2006.01855). No fabricated reference. This is the third clean delivery in a row.

**Scope** — obeyed. One file created, nothing else modified, nothing trained, git history not searched.

---

## 2. Correction 1 — the puzzle FEN is NOT the puzzle position

The report's §2.3 diagram labels the `fen` column `s_0 [Puzzle Start]`. It is not. The Lichess
convention is that **`fen` is the position one ply *before* the tactic, with the losing side to
move; `moves[0]` is that side's error; the solver moves second.**

Proof, run today, not recalled:

```
odd-length solution lines: 0 of 5,527,851
00008 fen-to-move=black first=f2g3 -> solver=white nply=6
0000D fen-to-move=white first=d3d6 -> solver=black nply=4
```

Every one of 5.5M solution lines is even. If the FEN were the solver's turn, lines ending on the
solver's move would be odd. They never are.

This repository already implements the convention correctly —
`backend/training/puzzle_regime.py:96-105`, `puzzle_position()` pushes `moves[0]` before handing
the board to the drill. A dataset built naively from the `fen` column would have been silently
off by one ply for every one of its samples: the **metric-mislabel family**, `LEADER_BIBLE.md` §5.

**This correction is not a defect in the plan — it improves it.** See
`docs/plans/PLAN_CONFIGURATION_STEERING.md` §3: the position we actually want to steer toward is
the one in the `fen` column.

## 3. Correction 2 — precursor positions do not cost 500 GB

§3 Option C prices parent-game recovery at a *"~500 GB download"* of the Lichess archives. The
source file already on disk carries the game reference:

```
HEADER: PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl,OpeningTags
ROW1  : 00008,...,https://lichess.org/787zsVup/black#48,
```

`data/puzzles/lichess_db_puzzle.csv.zst` (289 MB, local) has **`GameUrl`, which encodes both the
game id and the exact ply (`#48`)**. `build_puzzle_db.py` simply does not copy that column into
the sqlite table. Recovering parent games is therefore a targeted API fetch per game, not a bulk
archive download. Noted for v2 only — Thejus demoted the roll-back idea in the brief itself
(*"do not cloud your thinking with this idea. First the initial idea."*).

---

## 4. Where the report drifted, and it is the leader's fault

The report's centre of gravity (§2.3, all of §3, and experiment E3) is a **precursor classifier**:
predict whether a position is *k* plies before a tactic. That is not what Thejus asked for first —
it is the roll-back device he explicitly demoted.

It is in the report because **the leader put it there**: brief §4.3 made "The backward step" a
required question. The worker answered the brief it was given. Same residue as the round table,
one level removed, and the second time in one day that the leader's framing steered an artefact
away from his.

**What survives and is used:** the inventory (§0.2), the negative-class taxonomy (§4, the naive /
hard-positional / near-miss split is genuinely useful), the three LC0 integration mechanisms (§6),
and the Ng-Harada-Russell shaping result, which is the principled version of §6 mechanism 3.

**What is set aside for now:** §2.3/§3 precursor construction, §5's hand-tuned λ reachability
score (no learned component, and three free parameters nobody can set), and §7's engine-vs-engine
falsification (expensive, and it tests engine strength rather than his coaching aim).
