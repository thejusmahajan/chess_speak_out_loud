# Gemini 3.6 Flash (High), local worker — TASK: real batched BT3 saliency

You are in the **local Antigravity workspace** with the repo checked out. You can
**edit files** and **run Python**, and — importantly — this machine **can run BT3**:
`engine/bt3.onnx` is present and the `cszero` env has `torch` + `lczerolens`, so
`NeuralVision` loads in **attention** mode on CPU (~1.5s/forward — slow but real).
That means **you can PROVE correctness locally.** Use your knowledge of the
AlphaZero/LC0 transformer input encoding to get the batching right.

Run everything with this interpreter (the `cszero` env):
`C:\Users\Admin\miniconda3\envs\cszero\python.exe`

## Goal
Add `NeuralVision.saliency_absolute_batch(fens: list[str]) -> list[dict[str,float]]`
that returns the **same** maps as calling `saliency_absolute(fen)` one at a time, but
computes them with **ONE forward pass over a stacked batch of all boards** — so on a
GPU it becomes one wide batch instead of hundreds of serial calls.

**Two hard requirements:**
1. **REAL batch.** The model's forward must run **once** for the whole list, not in a
   Python loop over boards. (CPU won't show a speedup — that's fine; the speed win is
   measured later on GPU. But it must genuinely be one batched forward.)
2. **Identical output.** `saliency_absolute_batch(fens)[i] == saliency_absolute(fens[i])`
   within `1e-3` per square, for **both** white- and black-to-move FENs.

## The serial code you must match (DO NOT change these methods)
`backend/neural_vision.py`. `__init__` sets:
```python
self._attn_module_names = [f"module.encoder{i}/mha/QK/softmax" for i in range(15)]
self.model = LczeroModel.from_onnx_path(onnx_path); self.model.eval()
```
Serial extraction (the ground truth, per board):
```python
def _attention_saliency(self, fen):
    import torch
    from lczerolens import LczeroBoard
    attention_tensors = []
    def hook_fn(module, inp, out):
        t = out[0] if isinstance(out, (tuple, list)) else out
        attention_tensors.append(t.detach())           # each: [batch, 24, 64, 64]
    hooks = [mod.register_forward_hook(hook_fn)
             for name, mod in self.model.named_modules() if name in self._attn_module_names]
    with torch.no_grad():
        self.model(LczeroBoard(fen))                    # ONE board
    for h in hooks: h.remove()
    stacked = torch.stack(attention_tensors)            # [15, 1, 24, 64, 64]
    avg_attn = stacked.mean(dim=(0, 1, 2))              # mean over layers,batch,heads -> [64,64]
    vec = avg_attn.mean(dim=0)                           # mean over queries -> [64]
    mx, mn = vec.max(), vec.min()
    vec = (vec - mn) / (mx - mn) if mx > mn else torch.zeros_like(vec)  # per-board [0,1]
    vec = vec.tolist()
    files, ranks = "abcdefgh", "12345678"
    return {f"{files[i%8]}{ranks[i//8]}": vec[i] for i in range(64)}     # token i -> square

def _saliency_absolute(self, board):
    if board.turn == chess.WHITE:
        return self._attention_saliency(board.fen())
    mirrored = board.mirror()                            # swap colors + flip ranks -> white-to-move
    s = self._attention_saliency(mirrored.fen())
    return {sq[0] + str(9 - int(sq[1])): v for sq, v in s.items()}   # flip ranks back
```
Per board: **mean over (15 layers, heads, queries) → normalize to [0,1] per board →
token→square**; for **black to move**, evaluate `board.mirror()` and flip rank digits
(`r -> 9-r`). Your batch must reproduce this per board, differing only in one shared
forward.

## How to batch the forward (use your architecture knowledge)
The single-board call `self.model(LczeroBoard(fen))` builds LC0 input planes
`[C, 8, 8]` and runs the transformer. To batch: build each board's input-plane tensor,
**`torch.stack` them into `[N, C, 8, 8]`, and run the model once** so each attention
hook fires a single time with shape **`[N, 24, 64, 64]`**. Then for board `b`, take
batch-slice `b` and apply the same mean/normalize/map/mirror as above.

Find the input-plane path from the loaded model/board — inspect
`dir(LczeroBoard(fen))` and `dir(lczerolens)` for the encode entry point (e.g. a
board→tensor method, or a batch-encode helper); if a list `self.model([b1,b2,...])`
already yields a batch-N attention tensor, that's the simplest path. **Confirm by
printing the hooked tensor's shape — its first dim must be N.**

Black/white: build the batch from **mirrored FENs for black-to-move boards**, track a
per-board `is_black` flag, and flip those boards' final keys.

## Edit
In `backend/neural_vision.py`, add `saliency_absolute_batch` (public) +
`_saliency_absolute_batch` (the batched forward + per-board post-processing). **Leave
`saliency_absolute`, `_saliency_absolute`, `_attention_saliency` untouched** — they
are the reference. Contract:
- `[]` → `[]`. Not attention mode / `model is None` → `[self._policy_fallback(f,None) for f in fens]`.
- **On any exception in the batched path, fall back** to
  `[self._saliency_absolute(chess.Board(f)) for f in fens]` and log — never break diagnosis.
- Output: `list` in input order, each a 64-key `dict[str,float]`.

## PROVE it locally — write `scratch/verify_batch_saliency.py` and run it
```python
import sys; sys.path.insert(0, ".")
import torch
from backend.neural_vision import NeuralVision
v = NeuralVision(onnx_path="engine/bt3.onnx"); assert v.mode == "attention", "need attention mode"

fens = [
 "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
 "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",          # black to move
 "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
 "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",   # black to move
 "8/8/4k3/8/4P3/4K3/8/8 w - - 0 1",                                      # endgame white
 "6k1/5ppp/8/8/8/8/5PPP/6K1 b - - 0 1",                                  # endgame black
]

# (A) REAL-BATCH check: the model's forward must run ONCE for the whole list.
calls = {"n": 0}
orig = v.model.forward
def counting(*a, **k):
    calls["n"] += 1
    return orig(*a, **k)
v.model.forward = counting
_ = v.saliency_absolute_batch(fens)
v.model.forward = orig
assert calls["n"] == 1, f"REAL-BATCH FAIL: forward ran {calls['n']}x (looping, not batched)"
print(f"REAL-BATCH PASS — one forward for {len(fens)} boards")

# (B) CORRECTNESS check: batch == serial.
serial  = [v.saliency_absolute(f) for f in fens]
batched = v.saliency_absolute_batch(fens)
maxdiff = 0.0
for i,(s,b) in enumerate(zip(serial,batched)):
    assert set(s)==set(b), f"key mismatch at {i}"
    for sq in s: maxdiff = max(maxdiff, abs(s[sq]-b[sq]))
assert maxdiff < 1e-3, f"CORRECTNESS FAIL: max per-square diff {maxdiff}"
print(f"CORRECTNESS PASS — max per-square diff {maxdiff:.2e} over {len(fens)} FENs")
```
Run: `C:\Users\Admin\miniconda3\envs\cszero\python.exe scratch/verify_batch_saliency.py`
Both `REAL-BATCH PASS` and `CORRECTNESS PASS` must print. (If `v.model.forward` isn't
directly wrappable, wrap the actual `nn.Module` forward lczerolens calls, or report
what you found — but do not skip proving it's one forward.)

## Deliver
- The edited `backend/neural_vision.py` (two new methods only) + `scratch/verify_batch_saliency.py`.
- Paste the run output showing **both** PASS lines.
- A `WORKLOG_TRAINING.md` line ending `batched saliency implemented + locally verified`.

Then STOP for leader review. I will re-run this gate, mutation-check it (delete the
black-to-move rank-flip → CORRECTNESS must FAIL; force a per-board loop → REAL-BATCH
must FAIL), and measure the actual GPU speedup separately. **Scope: only these two
methods** — do not touch the serial methods, the pipeline, TS2, or anything else.
