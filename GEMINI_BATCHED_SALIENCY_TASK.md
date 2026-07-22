# Gemini (3.6 Flash, High) — TASK: real batched BT3 saliency (Optimization #1)

**Goal:** make `NeuralVision` compute BT3 attention saliency for **many FENs in a
single batched GPU forward pass**, so the A100 is fed wide instead of one 0.58s
serial call at a time. This is Step 1 of `docs/discussion_5_saturating_the_a100.md`.
Follow `WORKER_AGENT_COOKBOOK.md`. The correctness bar is exact and non-negotiable:
**the batched result must equal the serial result square-for-square.**

## The one hard requirement (read twice)
Add `saliency_absolute_batch(fens: list[str]) -> list[dict[str,float]]` such that
for every input FEN:

```
saliency_absolute_batch(fens)[i]  ==  saliency_absolute(fens[i])   (within 1e-3 per square)
```

…AND it must do so with **ONE model forward pass over a stacked batch of boards**,
NOT a Python loop over `self.model(board)`. If you loop the forward, the task has
failed even if the numbers match — the entire point is to saturate the GPU with a
single big forward.

> ⚠️ A previous attempt (now reverted) added `_saliency_absolute_batch` but called
> `self.model(l_board)` **inside a `for` loop** (serial). Do not repeat that. The
> per-board normalization and black-to-move handling in that attempt were correct;
> the batching was fake. Fix the batching.

## The serial reference you must match (do NOT modify these methods)
`backend/neural_vision.py` — keep `saliency_absolute`, `_saliency_absolute`, and
`_attention_saliency` **exactly as they are**; they are the ground truth your batch
is tested against. The serial pipeline per board is:

1. **White to move:** run `self.model(LczeroBoard(fen))`; hooks on the 15 modules
   `self._attn_module_names` (`module.encoder{i}/mha/QK/softmax`, i=0..14) capture
   attention tensors of shape `[batch, heads=24, 64, 64]`.
2. Stack the 15 layer tensors → mean over **(layers, batch, heads)** → `[64,64]`,
   then mean over **queries (dim 0)** → `[64]`.
3. Normalize that 64-vector to `[0,1]` **per board** (min/max over its own 64
   squares; all-zeros if max==min).
4. Map token `i` → square `f"{'abcdefgh'[i%8]}{'12345678'[i//8]}"`.
5. **Black to move:** `_saliency_absolute` first does `board.mirror()` (python-chess
   mirror = swap colors + flip ranks → white-to-move frame), runs the above on the
   mirrored FEN, then flips the result keys back: `sq[0] + str(9 - int(sq[1]))`.

Your batch must reproduce steps 2–5 **independently per board**, differing only in
that step 1 is a **single batched forward** for all boards at once.

## How to actually batch the forward (the real work)
The crux is feeding N boards through `self.model` in one call so each captured
attention tensor has batch dim **N** (`[N, 24, 64, 64]`) instead of 1. Investigate,
in this order, and use whichever the installed `lczerolens` supports:

1. **lczerolens native batch encode.** Look for an encode/batch API (e.g.
   `lczerolens.encode`/board→input-planes, or passing a list/`torch.stack` of
   per-board input tensors) that yields a `[N, C, 8, 8]` input, then one
   `self.model(stacked_input)` (or the model's tensor-input entrypoint). Register
   the hooks ONCE, call the model ONCE, and each hook fires once with a batch-N
   tensor.
2. If the model only accepts a single `LczeroBoard`, find the tensor it builds
   internally (the input planes) and build+stack those yourself for the batch,
   then call the underlying `torch.nn.Module.forward` on the stacked tensor.
3. Ensure the stacked input is on the model's device (`next(self.model.parameters()).device`)
   so the forward runs on GPU.

After the single forward, each of the 15 hooks holds one `[N,24,64,64]` tensor.
For board `b`, slice index `b` out of the batch dim, then apply steps 2–5 above.
**Handle white/black per board:** build the batch from mirrored FENs for black-to-
move boards (track a per-board `is_black` list), and flip the keys of those boards'
final maps — exactly as `_saliency_absolute` does.

## Wiring (already half-done — verify, don't duplicate)
`backend/training/pipeline.py` Stage B already calls
`vision.saliency_absolute_batch(uncached_fens)` when the method exists (with a serial
fallback otherwise). So simply **adding a correct `saliency_absolute_batch` makes
Stage B use it automatically.** Do not change the pipeline in this task. (TS2's
per-candidate saliency is Optimization #2 — OUT OF SCOPE here.)

## Guardrails
- **Do not modify** `saliency_absolute`, `_saliency_absolute`, `_attention_saliency`,
  or anything outside `neural_vision.py`.
- **Empty input** `[]` → return `[]`. **Not in attention mode / model is None** →
  return `[self._policy_fallback(f, None) for f in fens]`.
- **On any exception in the batched path, fall back** to the serial per-fen result
  (`[self._saliency_absolute(chess.Board(f)) for f in fens]`) and log the error, so
  a batching failure degrades gracefully instead of breaking diagnosis.
- Preserve output type/shape exactly: `list` aligned to input order, each a
  `dict[str,float]` with the 64 absolute-square keys.

## Verification (this IS the deliverable — run it on the real BT3 model)
Because correctness can only be proven where `bt3.onnx` loads in attention mode
(Colab GPU or a machine with the net), write and RUN this and paste the output:

```python
from backend.neural_vision import NeuralVision
v = NeuralVision(onnx_path="<path>/bt3.onnx")
assert v.mode == "attention", "need attention mode to verify"

fens = [  # MUST include both white-to-move and black-to-move positions
  "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",  # black to move
  "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
  "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",  # black
  # add ~4 more, mixed side-to-move, incl. a middlegame + an endgame FEN
]
serial  = [v.saliency_absolute(f) for f in fens]
batched = v.saliency_absolute_batch(fens)
assert len(batched) == len(fens)
maxdiff = 0.0
for i,(s,b) in enumerate(zip(serial,batched)):
    assert set(s) == set(b), f"key mismatch at {i}"
    for sq in s:
        maxdiff = max(maxdiff, abs(s[sq]-b[sq]))
assert maxdiff < 1e-3, f"batch != serial, max per-square diff {maxdiff}"
print(f"CORRECTNESS PASS — max per-square diff {maxdiff:.2e} over {len(fens)} FENs")

import time
big = (fens * 16)[:64]
t=time.time(); [v.saliency_absolute(f) for f in big]; t_serial=time.time()-t
t=time.time(); v.saliency_absolute_batch(big);        t_batch =time.time()-t
print(f"SPEED — serial {t_serial:.1f}s vs batched {t_batch:.1f}s over 64 FENs "
      f"({t_serial/max(t_batch,1e-9):.1f}x)")
```

**Pass conditions:** `CORRECTNESS PASS` prints with `maxdiff < 1e-3`, AND the batched
time is materially lower than serial (target ≥ 3x on 64 FENs on the GPU). If the
speedup is ~1x, you are still looping the forward — fix it before reporting done.

## Deliverable / gate
- Edited `backend/neural_vision.py` (new `saliency_absolute_batch` +
  `_saliency_absolute_batch` only), the serial methods untouched.
- The verification script's pasted output showing CORRECTNESS PASS + the speedup.
- A `WORKLOG_TRAINING.md` entry ending with `batched saliency ready for review`.
Then STOP for leader review — I will re-run the correctness gate and mutation-check
it (e.g. break the black-to-move key flip → the test must fail) before it lands.
