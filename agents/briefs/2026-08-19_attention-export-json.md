```
Brief-ID:     2026-08-19_attention-export-json
Written:      2026-08-19
Target repo:  chess_speak_out_loud (this one)
Route:        Antigravity (full workspace)
Type:         implementation (data export, correctness-critical)
Status:       ACTIVE
Depends on:   none  (blocks 2026-08-19_attention-demo-page)
```

# Export REAL BT3 attention as JSON for the public demo

This produces the data behind a public, animated attention demo on Thejus' website. The
single hardest requirement: **the exported squares must be TRUE absolute board squares**, for
black-to-move positions as well as white.

BT3's internal representation **mirrors the board when it is Black to move**. This project has
already shipped that bug once publicly and corrected it — `saliency()` is frame-buggy and
`saliency_absolute()` is the fixed public API (`backend/neural_vision.py:224`). Shipping a
public demo with a mirrored board would repeat, in front of employers, the exact error the
accompanying write-up is about.

**Everything exported must be real model output. Do not synthesise, interpolate, smooth, or
"make it look nicer". If a value is ugly, it ships ugly.**

## 1. Scope

**Create ONLY:**
```
backend/training/attention_export.py
backend/tests/test_attention_export.py
```
Output data file (git-ignored is fine, it gets copied to the website by hand):
```
scratch/attention_export.json
```

**Do NOT modify** `backend/neural_vision.py`, `metrics.py`, `salience_matcher.py`, or anything
under `agents/`, `docs/`, `data/`. Read `neural_vision.py` — do not edit it. If you believe it
needs a change, **STOP and report**.

Do not commit.

## 2. Where the data comes from

`backend/neural_vision.py` already hooks `module.encoder{i}/mha/QK/softmax` for `i in range(15)`
and produces tensors of shape **`[15, N, 24, 64, 64]`** — 15 layers, batch, 24 heads, and a
64×64 square-to-square attention matrix. Today the code averages this to `[64, 64]` and reduces
it further to a per-square dict.

You need the **per-layer** matrices, head-averaged: **`[15, 64, 64]`** per position, expressed
in **absolute squares on both axes**.

Read how `_saliency_absolute` performs its frame correction and apply the *same* transform to
both axes of the 64×64 matrix. Do not invent your own mirroring logic.

## 3. Positions to export (pinned)

Exactly three, and **at least one must be Black to move** — that position is what proves the
frame handling is right.

| id | label (shown to the public) | fen |
|---|---|---|
| `tactical` | A tactical position | `r1b2rk1/pp1nqppp/2pbpn2/8/2BP4/2N1PN2/PP2QPPP/R1B2RK1 w - - 0 11` |
| `quiet` | A quiet middlegame | `r1bq1rk1/pp2bppp/2n1pn2/3p4/3P4/2NBPN2/PP3PPP/R1B1QRK1 w - - 0 9` |
| `black_to_move` | Black to move | `4r1k1/3q1rp1/p1pbpp1p/3p3N/3P2QP/4P1P1/PP4P1/2R2RK1 b - - 2 29` |

Pass `history_ucis=None` for all three and record that in the output. (Note for the record: the
history-planes issue means bare-FEN input leaves most input planes empty; that is a known
property of this export and it is disclosed in §6, not hidden.)

## 4. Output schema (pinned exactly)

```json
{
  "schema": "bt3-attention-v1",
  "net": "BT3-768x15x24h",
  "n_layers": 15,
  "n_heads": 24,
  "generated_utc": "<ISO-8601>",
  "note": "Head-averaged attention per layer. Absolute board squares on both axes.",
  "positions": [
    {
      "id": "tactical",
      "label": "A tactical position",
      "fen": "...",
      "side_to_move": "white",
      "history_ucis": null,
      "layers": [
        {
          "layer": 0,
          "scale": 0.0412,
          "attn_u8": "<base64 of exactly 4096 bytes>"
        }
      ],
      "saliency_absolute": { "a1": 0.0, "e4": 0.13 }
    }
  ]
}
```

Rules:
- `attn_u8` decodes to **exactly 4096 bytes**, row-major **`[from_square][to_square]`**, where
  index `0` is **a1** and index `63` is **h8** (python-chess square numbering) on **both** axes.
- Quantise per layer: `u8 = round(255 * value / scale)` where `scale` is that layer's maximum
  value. Store `scale` so the consumer can recover the float.
- `layers` has exactly 15 entries, `layer` ascending 0…14.
- `saliency_absolute` is the verbatim output of `NeuralVision.saliency_absolute(fen)` for the
  same position — it exists so the demo and the audited API can be cross-checked.
- Round floats to 6 decimal places. Keep the file under **2 MB**.

## 5. Tests — real guards, mutation-checked

`backend/tests/test_attention_export.py`. Skip cleanly (`pytest.mark.skipif`) when the BT3 model
is unavailable, so the suite still passes on a machine without the net — but the frame test must
run whenever the model IS present.

1. `test_shapes_and_schema` — 3 positions, each with 15 layers, each `attn_u8` decoding to
   exactly 4096 bytes; all required keys present.
2. `test_rows_are_probability_distributions` — the attention comes from a softmax, so each
   **row** of the de-quantised 64×64 matrix must sum to approximately 1.0. Assert within `0.02`
   (quantisation error) for every row of at least 3 sampled layers. **If this fails, the axes
   are transposed** — report it rather than swapping them silently.
3. `test_frame_matches_the_audited_api` — **THE critical guard.** For each position, reduce the
   exported `[15,64,64]` tensors the same way `_saliency_absolute` reduces its attention, and
   assert the result equals `saliency_absolute(fen)` for every one of the 64 squares, to within
   `1e-4`. Read the reduction out of `neural_vision.py`; do not guess it.
4. `test_black_to_move_is_not_mirrored` — for the `black_to_move` position, assert the exported
   per-square totals match `saliency_absolute(fen)` **and** that they do **not** match the
   vertically-mirrored version of themselves (i.e. the board is genuinely oriented, not
   symmetric by accident). If the position happens to be near-symmetric so the test cannot
   distinguish, **say so in your report and pick a different black-to-move FEN**, reporting the
   change.
5. `test_quantisation_round_trip` — de-quantised values are within `scale/255` of the originals.

## 6. Gate — paste REAL output

```
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests/test_attention_export.py -v
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m backend.training.attention_export
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests -q
git status
```

Then paste, from the generated file: its size in bytes, the three `side_to_move` values, and for
the `tactical` position the **top 5 squares** by total attention received, with their values.

Also state plainly in your report: **was the BT3 model actually available on this machine, or
did the tests skip?** If it skipped, the export did not really run and you must say so — a
skipped run reported as a success is the worst possible outcome here.

## 7. Your report

`agents/reports/2026-08-19_attention-export-json_REPORT.md`, covering: gate output; whether the
model was present; the answer to test 4's symmetry question; anything the brief got wrong about
`neural_vision.py` (reporting a spec error is a good outcome); and anything not done.
