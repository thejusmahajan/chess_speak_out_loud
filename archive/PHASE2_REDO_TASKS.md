# GEMINI WORKER SPEC — PHASE 2 REDO: Real Neural Attention (no fallback)

> **You are Gemini, the implementation worker.** You previously fell back to
> `policy_fallback` for saliency because `torch`/`lczerolens` would not install on the
> **Windows Store Python 3.9** interpreter. That fallback is **not acceptable as the final
> state** — it makes the "saliency" overlay identical to the policy arrows, destroying the
> whole point of a *separate* Structure/Vision signal.
>
> This document supersedes Phase 2 of `GEMINI_TASKS.md`. Your job now is to build a **clean
> Python 3.11 environment**, extract **real transformer attention** from the LC0 network, and
> only keep `policy_fallback` as a runtime safety net — never as the delivered result.
>
> The same discipline applies: **do not invent APIs, verify before coding, paste real output,
> report honestly, stop at each gate.**

---

## WHY THE OLD BLOCKER WAS NOT A REAL WALL

- The install "stalled" downloading a ~241 MB **CUDA** torch wheel. You do not need CUDA —
  single-position inference runs fine on **CPU torch**, which is a different, smaller wheel
  from a different index. That removes the stall.
- Windows Store Python 3.9 is a poor ML interpreter. The fix is a proper **Python 3.11 venv**,
  not abandoning the pillar.

---

## HARD RULES

1. **The goal is `saliency_source: "attention"`.** `policy_fallback` may remain in the code as
   an automatic runtime safety net (if torch/lczerolens are missing), but the acceptance check
   MUST show real attention working. Do not declare success while still on the fallback.
2. **No invented APIs.** Every `lczerolens`/`torch` method or class you call must have appeared
   in real `dir()` / printed output you captured. Paste that output in your report.
3. **Stop at every GATE.** Gates are marked `⛔ GATE`. If a gate fails, STOP and report — do
   not improvise past it.
4. **Do not touch** Phases 0/1 code (`app.py` LLM flag, `engine_manager.get_policy_distribution`).
   They are verified and committed.
5. **Paths (this machine):**
   - Weights: `C:\Users\Admin\Documents\chess_speak_out_loud\engine\791556.pb.gz`
   - Project root: `C:\Users\Admin\Documents\chess_speak_out_loud`
6. **Shell is PowerShell / Windows.** Report the *exact* commands and their real output.

---

## STEP 1 — Discover available Python interpreters (do not assume)

Run and paste the real output:
```powershell
py -0p                 # lists all installed Python versions + paths
where.exe python
where.exe conda 2>$null
python --version
```
Decide the interpreter for the new environment, in this order of preference:
1. An existing **Python 3.10 / 3.11 / 3.12** shown by `py -0p` (use `py -3.11` etc.).
2. `conda` if present (`conda create -n cszero python=3.11`).
3. If none exists: install one, e.g. `winget install Python.Python.3.11` (or download from
   python.org), then re-run `py -0p` to confirm.

**⛔ GATE 1:** You must have a working Python **3.10–3.12** interpreter before continuing.
Paste `<chosen_python> --version` proving it. Do NOT use the Windows Store 3.9 build.

---

## STEP 2 — Build a clean venv and install the stack

Create the venv at the project root as `.venv311` (adjust the interpreter to what GATE 1 found):
```powershell
cd C:\Users\Admin\Documents\chess_speak_out_loud
py -3.11 -m venv .venv311
.\.venv311\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Install **CPU torch first** (this is the key fix — CPU index, not the default CUDA wheel):
```powershell
pip install torch --index-url https://download.pytorch.org/whl/cpu
```
Then lczerolens with the backends extra (needed to load `.pb.gz`), then the existing backend deps:
```powershell
pip install lczerolens
pip install "lczerolens[backends]"
pip install -r backend\requirements.txt
```
If any download is slow, raise the timeout instead of giving up:
`pip install --default-timeout=1000 <pkg>`. A slow download is not a blocker; a failed one is.

**⛔ GATE 2:** All three imports must succeed in the new venv. Paste the real output of:
```powershell
python -c "import torch, lczerolens; print('torch', torch.__version__); print('lczerolens OK')"
```

---

## STEP 3 — lczerolens API discovery (paste real output)

The README under-documents `.pb.gz` loading, so discover the true API. Run and paste output:
```python
import lczerolens
from lczerolens import LczeroModel, LczeroBoard
print("lczerolens:", [x for x in dir(lczerolens) if not x.startswith("_")])
print("LczeroModel:", [x for x in dir(LczeroModel) if not x.startswith("_")])
# Which loader accepts our .pb.gz? Test candidates — DO NOT ASSUME:
for name in ["from_path", "from_onnx", "from_pb", "load", "from_file"]:
    print(name, hasattr(LczeroModel, name))
```
Then actually load THIS network with whichever loader exists (follow the library's documented
`.pb.gz`/ONNX conversion path if a raw loader isn't present — the `[backends]` extra provides
the converter):
```python
model = <the_working_loader>(r"C:\Users\Admin\Documents\chess_speak_out_loud\engine\791556.pb.gz")
model.eval()
print(type(model))
```

**⛔ GATE 3:** The model must load without error. Paste the loader call that worked and the
printed model type.

---

## STEP 4 — Confirm the network HAS attention (critical architecture gate)

Attention only exists if `791556` is a **transformer** net. Inspect the module tree:
```python
names = [n for n, _ in model.named_modules()]
print(len(names), "modules")
attn = [n for n in names if any(k in n.lower() for k in ["attn", "attention", "mha", "encoder"])]
print("ATTENTION-LIKE MODULES:", attn[:40])
```
Also print one forward pass's output keys:
```python
board = LczeroBoard(r"r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1")
out = model(board)     # confirm the real call signature from STEP 3
print("OUTPUT KEYS:", list(out.keys()) if hasattr(out, "keys") else type(out))
```

**⛔ GATE 4 (decision point — STOP and report if it fails):**
- If `attn` is **non-empty** → this is a transformer; continue to STEP 5.
- If `attn` is **empty** → `791556` is NOT a transformer and has no attention to extract.
  **Do not fake it.** STOP and report: state that a transformer weights file is required
  (e.g. a BT/T-series LC0 net) and ask the human whether to download one. Do not download a
  new network on your own — that is the human's decision.

---

## STEP 5 — Implement real attention extraction in `backend/neural_vision.py`

Rewrite `NeuralVision` so it **tries real attention first, falls back only on failure**:

```python
class NeuralVision:
    def __init__(self, weights_path: str):
        self.weights_path = weights_path
        self.model = None
        self.mode = "policy_fallback"     # becomes "attention" on successful load
        try:
            import torch                    # lazy — so backend still starts if venv is wrong
            from lczerolens import LczeroModel
            self.model = <working_loader>(weights_path)
            self.model.eval()
            self.mode = "attention"
        except Exception as exc:
            logger.warning("NeuralVision: attention unavailable (%s) — using policy_fallback", exc)

    def is_available(self) -> bool:
        return True

    def saliency(self, fen: str, policy_dist=None) -> dict[str, float]:
        if self.mode == "attention" and self.model is not None:
            try:
                return self._attention_saliency(fen)
            except Exception as exc:
                logger.error("attention saliency failed (%s) — fallback", exc)
        return self._policy_fallback(fen, policy_dist)   # keep the existing proxy
```

`_attention_saliency(fen)` must:
1. Build the board (`LczeroBoard(fen)`) and prepare input per STEP 3's real signature.
2. **Register forward hooks** on the attention modules identified in STEP 4 (match by the real
   module names you printed — not guessed). Capture the attention weight tensors
   (shape ≈ `[batch, heads, 64, 64]`). Prefer any `lczerolens` activation/hook helper if STEP 3
   revealed one; otherwise use `torch.nn.Module.register_forward_hook`.
3. Run one forward pass (`with torch.no_grad():`).
4. Collapse to a 64-vector: average over heads and layers, reduce the `[64,64]` matrix to a
   per-square score (attention **received** = column mean, or attention rollout across layers).
5. Normalize to `[0,1]`, map the 64 values to `a1..h8`. **Verify orientation** (LC0 tokenizes
   from White's a1). Return `{square: score}`.

Keep the existing `_policy_fallback` method (rename the current `saliency` body into it).

---

## STEP 6 — Expose the real mode in the API

In `backend/app.py`, set `saliency_source` **dynamically from the instance**, not hardcoded:
```python
saliency = neural_vision.saliency(fen, policy_dist=policy_dist)
...
"saliency": saliency,
"saliency_source": neural_vision.mode,   # "attention" when real, else "policy_fallback"
```
**Important:** the backend now depends on torch/lczerolens, so it must be launched from
`.venv311`. Note in your report the exact command to run the server in the new venv, e.g.:
`.\.venv311\Scripts\python.exe -m uvicorn backend.app:app --reload`.

---

## STEP 7 — Acceptance checks (run from `.venv311`, paste output)

**7a — mode is real attention:**
```powershell
.\.venv311\Scripts\python.exe -c "from backend.neural_vision import NeuralVision; nv=NeuralVision(r'C:\Users\Admin\Documents\chess_speak_out_loud\engine\791556.pb.gz'); print('MODE', nv.mode)"
```
Expected: `MODE attention`.

**7b — saliency is structural, not uniform/random, and DIFFERENT from the policy proxy:**
```powershell
.\.venv311\Scripts\python.exe -c "from backend.neural_vision import NeuralVision; nv=NeuralVision(r'...\engine\791556.pb.gz'); s=nv.saliency('r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1'); import json; top=sorted(s.items(), key=lambda x:-x[1])[:8]; print('TOP', top)"
```
Expected: values in `[0,1]`; the top squares are concentrated on meaningful squares (central /
kingside / contested), **not** a flat spread and **not** identical to the from/to squares of the
top policy moves. If it's uniform or random, the wrong tensor was hooked — fix before claiming done.

**⛔ GATE 5:** Both 7a and 7b must pass. If 7a still says `policy_fallback`, the environment/
extraction is not actually working — do not report success.

---

## STEP 8 — Commit and report

- Commit: `Phase 2 REDO: real transformer attention saliency (lczerolens/torch, py3.11)`.
- Update `REALIGNMENT_REPORT.md` (or create it): record GATES 1–5 with the **real pasted
  output**, the final `saliency_source`, the venv launch command, and any orientation notes.
- If you were stopped at GATE 4 (no attention modules), report that instead and await the
  human's decision on a transformer network.

### Self-audit before claiming done
- [ ] `nv.mode == "attention"` in the acceptance check (not fallback).
- [ ] Attention came from hooks on modules whose names you printed in STEP 4.
- [ ] Saliency top-squares differ from the raw policy from/to squares (proves it's a distinct signal).
- [ ] Every lczerolens/torch symbol you used appeared in real discovery output.
- [ ] Backend documented to run from `.venv311`.
