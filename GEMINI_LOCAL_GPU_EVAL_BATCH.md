# Gemini 3.6 Flash (High), local worker — TASK: device-aware NeuralVision + batched position eval (Optimization #2 primitive)

Two deliverables in `backend/neural_vision.py`, both the enabling primitive for TS2's
batched candidate screen (discussion_5 Optimization #2). You can **edit files and run
Python on CPU** here (`engine/bt3.onnx` + `cszero` env). Use this interpreter:
`C:\Users\Admin\miniconda3\envs\cszero\python.exe`

**Context / why (this changes HOW you build it):** the BT3 torch model is currently
suspected to run on **CPU even on the A100**, because `torch.set_default_device("cuda")`
does NOT move an already-loaded model's parameters. And TS2 will soon evaluate many
candidate positions at once — so we need (1) the model *actually on the GPU*, and
(2) a batched forward that returns **value + policy** (not just saliency) for a list of
FENs in ONE pass. Correctness is CPU-verifiable; device/speed is confirmed on Colab.

Reuse the exact patterns already in the file: `saliency_absolute_batch` /
`_saliency_absolute_batch` (batched forward via `to_input_tensor()` → `torch.stack` →
one `self.model(batch_tensor)` + hook capture) and the black-to-move `mirror()` handling.

---

## Deliverable A — make NeuralVision device-aware (model + inputs on one device)

1. In `__init__`, after `self.model = LczeroModel.from_onnx_path(onnx_path)`:
   - Choose device: `self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")`.
   - Move the model: `self.model.to(self.device)` (and keep `.eval()`).
   - Store it so other methods can use `self.device`.
2. Ensure **every** input tensor fed to the model is on `self.device`:
   - Batched path: `batch_tensor = torch.stack(input_tensors).to(self.device)`.
   - Serial `_attention_saliency`: the input from `LczeroBoard(fen)` must also land on
     `self.device` — investigate how lczerolens builds the board input and move it there
     (e.g. `.to(self.device)` on the encoded tensor, or pass a device to the encode). If
     lczerolens already routes board input to the model's device, confirm it and note so.
3. **Must not change any OUTPUT** — saliency values must stay identical (device moves are
   numerically transparent). On CPU, `self.device == cpu`, so everything is a no-op and
   the existing `RUN_SLOW_BT3` saliency test must still pass unchanged.

## Deliverable B — `evaluate_batch(fens) -> list[dict]` (value + policy, one forward)

Add a public `evaluate_batch(fens: list[str]) -> list[dict]` that runs **one batched
forward** and returns, per FEN, a dict:
```python
{"value": float,        # side-to-move win-ish score in [-1,1] (or cp-equivalent — state which)
 "wdl": [w, d, l],      # if the net exposes WDL; else omit and say so
 "policy": [{"uci": str, "p": float}, ...]}   # legal moves, p in [0,1], sorted desc
```
- Use lczerolens to read the net's **value/wdl head and policy head** (it is a probing
  library built for exactly this — find the output accessors; inspect `dir(self.model)` /
  lczerolens docs). Map the policy logits/probs to **legal UCI moves** for each board.
- **Frame correctness:** value and policy are from the **side-to-move** POV. For
  black-to-move boards you evaluate the `mirror()` frame — so you must map the policy
  moves back to the ORIGINAL board's UCI (un-mirror), and keep value as side-to-move.
  This is the same class of care as the saliency rank-flip; get it right and test it.
- Contract: `[]`→`[]`; not attention mode / model None → per-FEN empty/fallback dict;
  on any exception, fall back to a per-FEN serial evaluation and log. Output aligned to input order.
- Leave `saliency_absolute`, `_saliency_absolute`, `_attention_saliency`,
  `saliency_absolute_batch`, `_saliency_absolute_batch` **untouched** (A only moves devices,
  it does not change their math).

---

## PROVE it locally (CPU) — write `scratch/verify_eval_batch.py` and run it
```python
import sys; sys.path.insert(0, ".")
import chess
from backend.neural_vision import NeuralVision
v = NeuralVision(onnx_path="engine/bt3.onnx"); assert v.mode == "attention"
print("device:", v.device)   # cpu here; cuda on Colab

fens = [
 "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
 "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",          # black
 "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
 "6k1/5ppp/8/8/8/8/5PPP/6K1 b - - 0 1",                                  # endgame black
]

# (A) REAL BATCH: one forward for the whole list.
calls={"n":0}; orig=v.model.forward
def c(*a,**k): calls["n"]+=1; return orig(*a,**k)
v.model.forward=c; v.evaluate_batch(fens); v.model.forward=orig
assert calls["n"]==1, f"REAL-BATCH FAIL: {calls['n']} forwards"
print(f"REAL-BATCH PASS — one forward for {len(fens)} positions")

# (B) CORRECTNESS: batched value/policy == single-position evaluation (define a serial
#     _evaluate_one you also add, OR compare against lczerolens single-board eval).
batched = v.evaluate_batch(fens)
assert len(batched)==len(fens)
for i,f in enumerate(fens):
    single = v.evaluate_batch([f])[0]      # batch-of-1 as the per-position reference
    assert abs(batched[i]["value"] - single["value"]) < 1e-3, f"value mismatch at {i}"
    # policy: top move must agree and be a LEGAL uci for the ORIGINAL board
    board = chess.Board(f)
    legal = {m.uci() for m in board.legal_moves}
    assert batched[i]["policy"][0]["uci"] in legal, f"illegal/mis-framed top move at {i}"
    assert batched[i]["policy"][0]["uci"] == single["policy"][0]["uci"], f"policy mismatch at {i}"
print("CORRECTNESS PASS — batched value+policy match per-position, legal in original frame")
```
Run: `C:\Users\Admin\miniconda3\envs\cszero\python.exe scratch/verify_eval_batch.py`
Both PASS lines must print. Also confirm the existing saliency guard still passes:
`set RUN_SLOW_BT3=1 && ...python.exe -m pytest backend/tests/test_batched_saliency.py -q`

## Colab GPU smoke-test (the LEADER/USER runs this — you cannot, no GPU here)
Provide this snippet in your report for the A100 (it confirms Deliverable A actually
uses the GPU and measures the payoff):
```python
print("device:", next(vision.model.parameters()).device)      # want cuda:0
import time
fens = [...]*16
t=time.time(); [vision.saliency_absolute(f) for f in fens[:16]]; print("serial 16:", time.time()-t)
t=time.time(); vision.evaluate_batch(fens[:64]); print("eval_batch 64:", time.time()-t)
```

## Deliver
- Edited `backend/neural_vision.py` (Deliverable A device moves + Deliverable B
  `evaluate_batch`; the five existing saliency methods' MATH untouched).
- `scratch/verify_eval_batch.py` + its output (both PASS lines) + the saliency-guard pass line.
- The Colab smoke-test snippet, for the leader to run on the A100.
- `WORKLOG_TRAINING.md` line ending `device-aware eval batch implemented + locally verified`.

Then STOP for leader review. I will re-run the CPU gate, mutation-check it (break the
black-to-move policy un-mirror → CORRECTNESS must FAIL; force a per-position loop →
REAL-BATCH must FAIL), and run the Colab GPU smoke-test to confirm `cuda:0` + the speedup.
**Scope: only `neural_vision.py`.** Do NOT touch the pipeline or TS2 — wiring the screen
into TS2 (deep search only on the crux) is the leader's integration step after this lands.
