# AUDIT — `2026-08-19_attention-export-json`

**Auditor:** Leader (Claude Opus 5) · **Date:** 2026-08-19
**Verdict: ACCEPT THE CODE. REJECT THE DATA FOR PUBLICATION.**
The exporter and its tests are correct and independently verified. The exported JSON must be
regenerated, because **the brief told the worker to feed the network mostly-empty inputs.**
That is a leader error, and the worker disclosed it exactly as instructed.

---

## 1. Boundary check — PASS

Only the two permitted files were created (`backend/training/attention_export.py`,
`backend/tests/test_attention_export.py`) plus the intended `scratch/attention_export.json`.
`neural_vision.py` untouched. Nothing committed.

## 2. Model availability — PASS, and honestly reported

The report states plainly that BT3 was **present and active** (`engine/bt3.onnx`, 410,354,289
bytes), that no tests skipped, and that all guards ran against live forward passes. I confirmed
the model loads in `attention` mode. This was the disclosure most open to quiet fudging and it
was made straight.

## 3. Independent verification — PASS on every checkable claim

I did not re-run the worker's tests as proof; I re-derived the results.

**Structure and the softmax property** (no model needed):

| check | result |
|---|---|
| schema / net / layer / head fields | `bt3-attention-v1`, `BT3-768x15x24h`, 15, 24 |
| positions and sides | `tactical` (white), `quiet` (white), `black_to_move` (**black**) |
| 15 layers each, `attn_u8` decoding to exactly 4096 bytes | yes, all 45 |
| **row sums across all layers** | **[0.9939, 1.0052]** — within 0.006 of 1.0 |
| file size | 256,313 bytes (cap was 2 MB) |

Row sums ≈ 1 confirm the axes are **not transposed**: rows are the softmax distributions, as
specified.

**The frame gate — the critical one.** I decoded the exported tensors, applied the reduction
recipe read out of `neural_vision.py` myself (mean over layers → mean over queries → min-max
normalise → index 0 = a1), and compared against a **live** `saliency_absolute()` call:

| position | my reduction vs live | stored field vs live |
|---|---|---|
| `tactical` (white) | 0.00049 | 0.0000005 |
| `quiet` (white) | 0.00048 | 0.0000005 |
| **`black_to_move` (black)** | **0.00043** | 0.0000005 |

0.0005 is exactly uint8 quantisation error. **The frame is correct, including for Black to
move.** The bug this project shipped publicly once has not been repeated here.

## 4. Suite — PASS

`302 passed, 5 skipped` — reproduced independently. Consistent with the 297-pass baseline plus
five new tests.

---

## 5. THE BLOCKING DEFECT — the data was generated from mostly-empty inputs

Running the export path emits the project's own warning:

> *NeuralVision called without move history: 84 of BT3's 112 input planes will be empty and
> results are unreliable for anything but the starting position. Pass history_ucis.*

**Brief §3 pinned `history_ucis=None` for all three positions.** The worker complied and
disclosed it. The instruction was wrong.

This is not cosmetic. Measured on a position with a known real move order
(`r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4`, reached by
`e2e4 e7e5 g1f3 b8c6 f1b5 a7a6`):

| metric, bare-FEN vs real history | value |
|---|---|
| max absolute difference (0–1 scale) | **0.4802** |
| mean absolute difference | 0.0908 |
| correlation | **0.8461** |
| top-6 squares, bare FEN | d8, d1, **e8, c8, h8** |
| top-6 squares, real history | d8, d1, **f8, a1, b5** |

The most-attended squares genuinely differ — and `b5`, the square the bishop just moved to,
appears **only** when the model is given the move history.

**Why this blocks publication specifically.** The history-planes defect is the *second* silent
bug Thejus already found and publicly corrected; his blog posts were amended because of it.
Shipping a public demo whose data was produced by exactly that mistake would repeat, in front of
employers, an error the accompanying write-up is about. The frame bug was caught here; this one
would have gone out.

**Fix:** regenerate with real move histories. Positions must be defined *by a full move sequence
from the initial position*, not by a bare FEN. `scratch/annotated_games/` already holds master
games with complete movetext and is the natural source. Follow-up brief:
`2026-08-19_attention-export-with-history`.

## 6. Note on the session mix-up (not a worker fault)

The user believed `website-repoint-part2` had been delivered. It had not — no part-2 report
exists, the website repo has no new commits, the clinical footer is still on all 20 pages, and
the new footer on 1. The worker had the **chess repo** open, so the workspace-routed `ACTIVE.md`
correctly sent it to `attention-export-json`. The routing worked as designed; only the
expectation was off. `website-repoint-part2` remains ACTIVE and needs the website folder open.

## 7. Lesson

**A brief that pins model inputs is making a scientific claim, not a configuration choice.** I
chose `history_ucis=None` for convenience and it silently degraded the model to 28 of 112 input
planes. When specifying an export for publication, pin the inputs that make the output *valid*,
and require the worker to show the model's own warnings — the warning was there in plain text
the whole time.
