```
Brief-ID:     2026-08-19_attention-export-with-history
Written:      2026-08-19
Target repo:  chess_speak_out_loud (this one)
Route:        Antigravity (full workspace)
Type:         implementation (data regeneration)
Status:       ACTIVE
Depends on:   2026-08-19_attention-export-json (code AUDITED and ACCEPTED — reuse it, do not rewrite it)
Supersedes:   the DATA produced by that brief, not its code
```

# Regenerate the attention export with real move histories

## 0. What happened and what you are fixing

`backend/training/attention_export.py` and its tests were audited and **accepted** — the frame
handling is correct, verified against a live `saliency_absolute()` call to within quantisation
error, including for the Black-to-move position. **Do not rewrite that code.** You are changing
its inputs and regenerating the data.

The previous brief pinned `history_ucis=None`. That was a leader error. It causes BT3 to run
with **84 of its 112 input planes empty**, and the model emits its own warning saying so. The
leader measured the damage on a position with a known real move order:

| bare FEN vs real history | value |
|---|---|
| max absolute difference (0–1 scale) | **0.4802** |
| correlation | **0.8461** |
| top-6 attended squares, bare FEN | d8, d1, **e8, c8, h8** |
| top-6 attended squares, real history | d8, d1, **f8, a1, b5** |

The squares the network attends to genuinely change. This data feeds a **public** demo on a
researcher's website, and publishing it would repeat the exact history-planes error already
found and publicly corrected in this project.

**Every value must be real model output. No synthesis, no smoothing, no "cleaning up".**

## 1. Scope

**Edit:** `backend/training/attention_export.py`, `backend/tests/test_attention_export.py`
**Regenerate:** `scratch/attention_export.json`

**Do NOT modify** `backend/neural_vision.py`, `metrics.py`, or anything under `agents/`,
`docs/`, `data/`. Do not commit.

## 2. The three positions (pinned — real master games, full histories)

Replace the three bare-FEN positions entirely. Each below is a real position from a real game,
with its **complete** move sequence from the initial position — 28 to 31 plies, far more than
the 8-position history BT3 needs.

### `sharp` — label: `A sharp middlegame`
```
fen:     r2qr1k1/pp3ppp/2p2n2/3n4/2QN2b1/1N4P1/PP2PPBP/R2R2K1 w - - 4 15
history: g2g3 e7e5 g1f3 e5e4 f3d4 d7d5 d2d3 e4d3 d1d3 g8f6 f1g2 f8b4 c1d2 b4d2 b1d2 e8g8 c2c4 b8a6 c4d5 a6b4 d3c4 b4d5 d2b3 c7c6 e1g1 f8e8 f1d1 c8g4
source:  Réti vs Alekhine
```

### `quiet` — label: `A quiet middlegame`
```
fen:     r2qrnk1/pp2bpp1/2p1b2p/3p3n/3P4/2NBPNBP/PPQ2PP1/1R3RK1 w - - 3 15
history: d2d4 g8f6 c2c4 e7e6 b1c3 f8b4 d1c2 d7d5 c4d5 e6d5 c1g5 c7c6 e2e3 b8d7 f1d3 h7h6 g5h4 e8g8 g1f3 f8e8 e1g1 b4e7 h4g3 d7f8 h2h3 c8e6 a1b1 f6h5
source:  Capablanca vs Golombek
```

### `black_to_move` — label: `Black to move`
```
fen:     r3k2r/1b1nb1pp/pq2p3/1p1pPp2/1P3P2/P2PBN2/4Q1PP/2RNK2R b Kkq - 3 16
history: e2e4 e7e6 d2d4 d7d5 b1c3 g8f6 e4e5 f6d7 f2f4 c7c5 d4c5 f8c5 g1f3 a7a6 f1d3 b8c6 d1e2 c6b4 c1d2 b7b5 c3d1 b4d3 c2d3 d8b6 b2b4 c5e7 a2a3 f7f5 a1c1 c8b7 d2e3
source:  Steinitz vs Sellman
```

**Verify each one yourself before exporting**: replay the history from `chess.Board()` and assert
the resulting FEN equals the pinned FEN exactly. If any disagrees, **STOP and report** — do not
adjust the FEN to match. (These were extracted by the leader from
`scratch/annotated_games/source3_great_masters.pgn`; only the moves are used, never the
annotations.)

The `source` strings are the players' names as they appear in the PGN headers. **Do not add
dates, events, or move numbers** — those headers are `?` in the file and inventing them would be
fabrication.

## 3. Schema changes

Keep `bt3-attention-v1` structure. Per position:

- `history_ucis` — now the **real list of UCI strings**, not `null`.
- `source` — the new string field above.
- `label` — as pinned above.
- `saliency_absolute` — must now be the output of
  **`saliency_absolute(fen, history_ucis=<the real history>)`**. Passing the history here too is
  essential: otherwise the cross-check compares good data against a degraded reference.

Everything else (uint8 quantisation, per-layer `scale`, 4096 bytes, a1=index 0, ≤2 MB) is
unchanged.

## 4. Tests

Keep all five existing tests passing, with these changes:

1. **`test_no_missing_history_warning` — NEW, and the point of this brief.** Capture logging /
   `warnings` output while running the export for all three positions and assert the string
   `without move history` does **not** appear. This is the guard that this defect cannot come
   back. Mutation-check it yourself: temporarily pass `history_ucis=None`, confirm the test
   fails, restore.
2. **`test_positions_replay_from_history` — NEW.** For each position, replay `history_ucis` from
   the initial position and assert the resulting FEN equals the pinned `fen`.
3. **`test_frame_matches_the_audited_api`** — update it to pass `history_ucis` to
   `saliency_absolute`. It must still match to within `1e-4`.
4. `test_black_to_move_is_not_mirrored` — re-check against the **new** Black-to-move position.
   Report the max difference against its vertical reflection; if that value is small enough that
   the test cannot distinguish orientation, say so rather than weakening the assertion.
5. The shape, row-sum and quantisation tests carry over unchanged.

## 5. Gate — paste REAL output

```
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests/test_attention_export.py -v
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m backend.training.attention_export
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests -q
git status
```

Then paste:
- the regenerated file's size in bytes;
- **the full stderr/stdout of the export run**, so the absence of the history warning is visible;
- for each position, the **top 5 squares by attention received**, with values;
- confirmation that BT3 was actually loaded (state the mode) — if the model was unavailable and
  anything skipped, **say so plainly**; a skipped run reported as success is the worst outcome.

## 6. Your report

`agents/reports/2026-08-19_attention-export-with-history_REPORT.md`. Include: every gate result;
the mutation check on test 1 (proof it fails when history is removed); the symmetry value from
test 4; anything this brief got wrong about the files or the positions — **reporting a spec
error is a good outcome**; and anything not done.
