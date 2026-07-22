# Gemini 3.1 Pro (in Colab) — TASK: implement AND prove real batched BT3 saliency

You are running **inside the Colab session** that has the **A100 GPU** and the repo
cloned at **`/content/repo`**, with **`/content/repo/engine/bt3.onnx`** already
present and `NeuralVision` loading it in **attention** mode. You can run cells and
see output — **so you must actually TEST this, not just write it.** This is
Optimization #1 of `docs/discussion_5_saturating_the_a100.md`.

## The goal (one sentence)
Add `NeuralVision.saliency_absolute_batch(fens: list[str]) -> list[dict[str,float]]`
that returns the **same** saliency maps as calling `saliency_absolute(fen)` one by
one, but computed with **ONE batched GPU forward pass over all boards at once** —
so the A100 is fed a big batch instead of hundreds of 0.58s serial calls.

**Hard pass/fail:** `saliency_absolute_batch(fens)[i] == saliency_absolute(fens[i])`
for every `i` (within `1e-3` per square, mixing white- and black-to-move FENs) AND
the batched path is **materially faster** than serial (≥3× on 64 FENs). If your
speedup is ~1×, you are still looping the forward — that is a failure, fix it.

## What the serial code does (this is the ground truth to match — DO NOT change it)
From `backend/neural_vision.py`. `__init__` sets:
```python
self._attn_module_names = [f"module.encoder{i}/mha/QK/softmax" for i in range(15)]
self.model = LczeroModel.from_onnx_path(onnx_path); self.model.eval()   # lczerolens
```
Serial single-board extraction:
```python
def _attention_saliency(self, fen):
    import torch
    from lczerolens import LczeroBoard
    attention_tensors = []
    def hook_fn(module, inp, out):
        t = out[0] if isinstance(out, (tuple, list)) else out
        attention_tensors.append(t.detach())          # each: [batch, 24, 64, 64]
    hooks = [mod.register_forward_hook(hook_fn)
             for name, mod in self.model.named_modules() if name in self._attn_module_names]
    with torch.no_grad():
        self.model(LczeroBoard(fen))                   # ONE board
    for h in hooks: h.remove()
    stacked = torch.stack(attention_tensors)           # [15, 1, 24, 64, 64]
    avg_attn = stacked.mean(dim=(0, 1, 2))             # mean over layers,batch,heads -> [64,64]
    vec = avg_attn.mean(dim=0)                          # mean over queries -> [64]
    mx, mn = vec.max(), vec.min()
    vec = (vec - mn) / (mx - mn) if mx > mn else torch.zeros_like(vec)  # per-board [0,1]
    vec = vec.tolist()
    files, ranks = "abcdefgh", "12345678"
    return {f"{files[i%8]}{ranks[i//8]}": vec[i] for i in range(64)}     # token i -> square

def _saliency_absolute(self, board):                    # absolute-square frame
    if board.turn == chess.WHITE:
        return self._attention_saliency(board.fen())
    mirrored = board.mirror()                           # swap colors + flip ranks -> white-to-move
    s = self._attention_saliency(mirrored.fen())
    return {sq[0] + str(9 - int(sq[1])): v for sq, v in s.items()}   # flip ranks back
```
So per board the math is: **mean over (15 layers, heads, queries) → normalize per
board to [0,1] → map token→square**, and for **black to move** you evaluate the
`board.mirror()` FEN and flip the result's rank digits (`r -> 9-r`). Your batch must
reproduce this **per board**, differing only in that the forward is done once for all.

## Step 1 — discover how to batch the forward (do this LIVE in a cell first)
Prototype in cells before touching the file. Load vision, then find the batch path:
```python
import sys; sys.path.insert(0, "/content/repo")
import torch, chess
from backend.neural_vision import NeuralVision
from lczerolens import LczeroBoard
v = NeuralVision(onnx_path="/content/repo/engine/bt3.onnx"); assert v.mode == "attention"

# capture one attention tensor's shape for a single board (baseline):
caps=[]
h=[m.register_forward_hook(lambda mod,i,o: caps.append((o[0] if isinstance(o,(tuple,list)) else o).shape))
   for n,m in v.model.named_modules() if n in v._attn_module_names]
with torch.no_grad(): v.model(LczeroBoard("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"))
for x in h: x.remove()
print("single-board attn shape:", caps[0])   # expect [1, 24, 64, 64]
```
Now find the batched input. **Try these in order and keep the first that makes the
hook fire with batch dim N:**
1. **List input:** `v.model([LczeroBoard(f1), LczeroBoard(f2), ...])` — some
   lczerolens versions auto-batch a list. Check the captured shape is `[N,24,64,64]`.
2. **Encoded tensor input:** find how a board becomes input planes
   (`dir(LczeroBoard(f))`, look for `get_input_tensor`/`to_tensor`/an encode fn in
   `dir(lczerolens)`), build each board's `[C,8,8]`, `torch.stack` to `[N,C,8,8]`,
   move to `next(v.model.parameters()).device`, and call the model on that tensor.
3. Whatever works, **verify empirically**: the hook must fire **once per layer** with
   a tensor whose **first dim is N**. Print the shape to prove it.

Mirror handling: build the batch from **mirrored FENs for black-to-move boards**,
track a per-board `is_black` list, and flip those boards' final keys — exactly as
`_saliency_absolute` does.

## Step 2 — write the two methods into `/content/repo/backend/neural_vision.py`
Add `saliency_absolute_batch` (public) and `_saliency_absolute_batch` (does the
batched forward + per-board slicing/normalize/map/mirror). **Leave
`saliency_absolute`, `_saliency_absolute`, `_attention_saliency` untouched.**
Contract:
- `[]` in → `[]` out. Not attention mode / `model is None` → `[self._policy_fallback(f,None) for f in fens]`.
- **On any exception in the batched path, fall back** to
  `[self._saliency_absolute(chess.Board(f)) for f in fens]` and log — never break diagnosis.
- Output: a `list` aligned to input order, each a `dict[str,float]` with 64 absolute-square keys.

## Step 3 — PROVE it (paste this output back)
```python
import importlib, backend.neural_vision as nv; importlib.reload(nv)
v = nv.NeuralVision(onnx_path="/content/repo/engine/bt3.onnx"); assert v.mode=="attention"
fens = [
 "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
 "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",          # black to move
 "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
 "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",   # black to move
 "8/8/4k3/8/4P3/4K3/8/8 w - - 0 1",                                      # endgame, white
 "6k1/5ppp/8/8/8/8/5PPP/6K1 b - - 0 1",                                  # endgame, black
]
serial  = [v.saliency_absolute(f) for f in fens]
batched = v.saliency_absolute_batch(fens)
assert len(batched)==len(fens)
maxdiff=0.0
for i,(s,b) in enumerate(zip(serial,batched)):
    assert set(s)==set(b), f"key mismatch at {i}"
    for sq in s: maxdiff=max(maxdiff, abs(s[sq]-b[sq]))
assert maxdiff < 1e-3, f"batch != serial, max diff {maxdiff}"
print(f"CORRECTNESS PASS — max per-square diff {maxdiff:.2e} over {len(fens)} FENs")
import time
big=(fens*16)[:64]
t=time.time(); [v.saliency_absolute(f) for f in big]; ts=time.time()-t
t=time.time(); v.saliency_absolute_batch(big);        tb=time.time()-t
print(f"SPEED — serial {ts:.1f}s vs batched {tb:.1f}s ({ts/max(tb,1e-9):.1f}x) over 64 FENs")
```
Both lines must print, with `maxdiff < 1e-3` and the batched time clearly lower.

## Step 4 — deliver
- If the Colab clone has a write token: commit `backend/neural_vision.py` and push to
  branch `windows-dev`, and paste the commit hash + the Step-3 output.
- If it can't push: **paste the full final `saliency_absolute_batch` +
  `_saliency_absolute_batch` code block** and the Step-3 output; the leader lands it.
- Add a `WORKLOG_TRAINING.md` line ending `batched saliency verified in Colab`.

Then STOP. The leader (Claude) re-runs the correctness gate and mutation-checks it
(e.g. deletes the black-to-move rank-flip → the test MUST fail) before it merges.
Do not touch the pipeline, TS2, or any other file — TS2's per-candidate saliency is
a separate task (Optimization #2).
