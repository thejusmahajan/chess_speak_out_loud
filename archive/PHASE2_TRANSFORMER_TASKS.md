# GEMINI WORKER SPEC — PHASE 2 (Transformer): Real Encoder Attention Saliency

> **Supersedes the network-dependent steps of `PHASE2_REDO_TASKS.md`.** The environment work
> (Python 3.11 `.venv311`, CPU torch, lczerolens) stands and is reused.
>
> **Verified facts (do not re-litigate):**
> - `engine\791556.pb.gz` is `NETWORK_SE_WITH_HEADFORMAT` — a **convolutional SE-ResNet**. It
>   has **no transformer encoder self-attention**. Confirmed via `lc0.exe describenet`.
> - The C++/`lczerolens[backends]` compile is **NOT needed**. `lc0.exe` (v0.32.1) has a
>   built-in `leela2onnx` converter. We convert `.pb.gz → .onnx` with it, then load the ONNX
>   in lczerolens' **pure-Python** mode (which supports `.onnx`/`.pt`).
>
> **Decision:** switch the Structure/Vision network to a **BT-series transformer** (real MHSA
> over the 64 squares). Same discipline as always: **no invented APIs, verify before coding,
> paste real output, honest reporting, stop at every `⛔ GATE`.**

---

## HARD RULES
1. Goal is `saliency_source: "attention"` from **real transformer encoder attention**. Fallback
   stays only as a runtime safety net; the acceptance check must show real attention.
2. No invented APIs — every lczerolens/torch/onnx symbol you call must appear in real output
   you pasted.
3. Stop at every `⛔ GATE`. Do not improvise past a failed gate.
4. Do NOT modify verified Phase 0/1 code except where Step 6/7 explicitly says so.
5. All commands run from the **`.venv311`** environment. Paths are on
   `C:\Users\Admin\Documents\chess_speak_out_loud`.

---

## STEP 1 — Download the transformer network

Download **BT3** (768×15×24h, ~190 MB — the most compact transformer; smaller than BT4) into `engine\`:
```powershell
cd C:\Users\Admin\Documents\chess_speak_out_loud\engine
curl.exe -L -o "BT3-768x15x24h-swa-2790000.pb.gz" "https://storage.lczero.org/files/networks-contrib/BT3-768x15x24h-swa-2790000.pb.gz"
# (Fallback if that path 404s — BT4, larger but same family:)
# curl.exe -L -o "BT4-1024x15x32h-swa-6147500.pb.gz" "https://storage.lczero.org/files/networks-contrib/big-transformers/BT4-1024x15x32h-swa-6147500.pb.gz"
```
Verify the file downloaded fully (size ≈ 190 MB, not an HTML error page):
```powershell
(Get-Item "BT3-768x15x24h-swa-2790000.pb.gz").Length
```

**⛔ GATE A — architecture check (this is the whole point):**
```powershell
.\lc0.exe describenet --weights=".\BT3-768x15x24h-swa-2790000.pb.gz" 2>&1 | Select-String -Pattern "Network|Encoder|Attention|Heads|Embedding|Blocks|Filters|Smolgen"
```
The output MUST indicate a **transformer / encoder / attention body** (e.g. an attention-body
network with encoder layers, heads, embedding size — NOT `NETWORK_SE_WITH_HEADFORMAT`). Paste
the real output. If it still reports a plain SE-ResNet, STOP — you downloaded the wrong file.

---

## STEP 2 — Convert to ONNX with lc0.exe (no compiler needed)

```powershell
.\lc0.exe leela2onnx --input=".\BT3-768x15x24h-swa-2790000.pb.gz" --output=".\bt3.onnx" --onnx-opset=17
(Get-Item ".\bt3.onnx").Length
```
**⛔ GATE B:** `bt3.onnx` exists and is non-trivial in size. Paste the converter's stdout and
the file size.

---

## STEP 3 — Ensure ONNX-loading deps in `.venv311`, then load

lczerolens loads ONNX via a torch conversion (e.g. `onnx` / `onnx2torch`). Install whatever the
import step reports missing:
```powershell
.\.venv311\Scripts\Activate.ps1
pip install onnx onnx2torch
```
Discover the real loader and load the ONNX (test candidates — DO NOT assume the name):
```python
import lczerolens
from lczerolens import LczeroModel, LczeroBoard
print("LczeroModel:", [x for x in dir(LczeroModel) if not x.startswith("_")])
for name in ["from_path", "from_onnx", "from_file", "load"]:
    print(name, hasattr(LczeroModel, name))
model = <working_loader>(r"C:\Users\Admin\Documents\chess_speak_out_loud\engine\bt3.onnx")
model.eval()
print(type(model))
```
**⛔ GATE C:** the ONNX model loads without error. Paste the loader that worked + printed type.

---

## STEP 4 — Locate the attention tensors (paste real output)

ONNX-derived modules often have **generic names** (`Softmax_42`, etc.), so identify attention by
BOTH name and **tensor shape**. The MHSA attention weights have shape `[batch, heads, 64, 64]`
(BT3: 24 heads). Do a discovery pass that registers hooks on every module and records which ones
emit a `[*, H, 64, 64]` (or `[*, 64, 64]`) tensor:
```python
import torch
from lczerolens import LczeroBoard
names = [n for n, _ in model.named_modules()]
print(len(names), "modules; sample:", names[:20])

hits = []
def mk(n):
    def hook(mod, inp, out):
        t = out[0] if isinstance(out, (tuple, list)) else out
        try:
            s = tuple(t.shape)
            if len(s) >= 2 and s[-1] == 64 and s[-2] == 64:
                hits.append((n, s))
        except Exception:
            pass
    return hook
hs = [m.register_forward_hook(mk(n)) for n, m in model.named_modules()]
board = LczeroBoard("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1")
with torch.no_grad():
    out = model(board)          # confirm the real call signature from STEP 3
for h in hs: h.remove()
print("ATTENTION-SHAPED TENSORS:", hits)
print("OUTPUT KEYS:", list(out.keys()) if hasattr(out, "keys") else type(out))
```
**⛔ GATE D:** `hits` must contain multiple `[*, H, 64, 64]` tensors (one per encoder layer). Paste
them. If empty, the attention is fused inside a single op — report and stop; do not fake it.

---

## STEP 5 — Implement `_attention_saliency` in `backend/neural_vision.py`

Rewrite `NeuralVision` to load BT3's ONNX and extract real attention (keep `_policy_fallback`
as the runtime safety net from the earlier redo):
```python
class NeuralVision:
    def __init__(self, onnx_path: str):
        self.mode = "policy_fallback"
        self.model = None
        self._attn_module_names = []   # filled from the GATE-D discovery
        try:
            import torch
            from lczerolens import LczeroModel
            self.model = <working_loader>(onnx_path)
            self.model.eval()
            self.mode = "attention"
        except Exception as exc:
            logger.warning("NeuralVision attention unavailable (%s) — policy_fallback", exc)

    def saliency(self, fen, policy_dist=None) -> dict[str, float]:
        if self.mode == "attention" and self.model is not None:
            try:
                return self._attention_saliency(fen)
            except Exception as exc:
                logger.error("attention saliency failed (%s) — fallback", exc)
        return self._policy_fallback(fen, policy_dist)
```
`_attention_saliency(fen)` must:
1. Register forward hooks on the attention modules found in STEP 4 (match by the recorded
   names/shapes — not guessed). Capture each `[batch, heads, 64, 64]` tensor.
2. `with torch.no_grad():` run one forward pass on `LczeroBoard(fen)`.
3. Stack all layers, average over heads and layers → a single `[64, 64]` matrix.
4. Reduce to a 64-vector: **attention received per square** = mean over the query axis
   (i.e. `A.mean(axis=0)` for target squares), OR attention-rollout across layers. Pick one,
   document it.
5. Normalize to `[0,1]`. Map indices 0..63 to `a1..h8`. **Verify orientation** — LC0 token 0 is
   a1 from White's view. Sanity-check on a lopsided position that hot squares land where the
   action is; if mirrored, fix the mapping.
6. Return `{square: score}`.

---

## STEP 6 — Point the app at BT3's ONNX; keep `saliency_source` dynamic

In `backend/app.py`:
```python
neural_vision = NeuralVision(onnx_path=str(ENGINE_DIR / "bt3.onnx"))
...
"saliency": saliency,
"saliency_source": neural_vision.mode,   # dynamic, not hardcoded
```
The backend now imports torch/lczerolens, so it must launch from `.venv311`:
`.\.venv311\Scripts\python.exe -m uvicorn backend.app:app --reload`.

---

## STEP 7 — Acceptance checks (run from `.venv311`, paste output)

**7a — real mode:**
```powershell
.\.venv311\Scripts\python.exe -c "from backend.neural_vision import NeuralVision; nv=NeuralVision(r'C:\Users\Admin\Documents\chess_speak_out_loud\engine\bt3.onnx'); print('MODE', nv.mode)"
```
Expected: `MODE attention`.

**7b — structural & distinct from policy:**
```powershell
.\.venv311\Scripts\python.exe -c "from backend.neural_vision import NeuralVision; nv=NeuralVision(r'...\engine\bt3.onnx'); s=nv.saliency('r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1'); print('TOP', sorted(s.items(), key=lambda x:-x[1])[:8])"
```
Expected: values in `[0,1]`; top squares concentrated on meaningful (central/contested/king)
squares, **not** uniform/random, and **not** identical to the from/to squares of the top policy
moves (proves it is a *distinct* signal, not the arrows re-drawn).

**⛔ GATE E:** both 7a and 7b must pass. If 7a says `policy_fallback`, it is not working — do
not report success.

---

## STEP 8 (coherence — after GATE E passes) — OPTIONAL, ask before doing

For conceptual integrity the arrows (policy) and the glow (attention) should come from the SAME
network. Currently policy priors (Phase 1) come from `791556` and attention from BT3. If desired,
switch the LC0 engine's weights to BT3 as well (`engine_manager` weights path) and **re-run the
Phase 1 acceptance check** to confirm BT3 still yields sane priors. **Do not do this silently** —
note it and confirm, since BT3 on CPU is slower per eval than 791556.

---

## STEP 9 — Commit & report
- Commit: `Phase 2: real transformer (BT3) encoder-attention saliency via lc0 leela2onnx + lczerolens`.
- Update `REALIGNMENT_REPORT.md`: GATES A–E with real pasted output, final `saliency_source`,
  the reduction method chosen (received vs rollout), orientation notes, `.venv311` launch command.

### Self-audit
- [ ] GATE A showed a transformer/encoder body (not SE-ResNet).
- [ ] ONNX produced by `lc0.exe leela2onnx`; loaded via a real lczerolens loader.
- [ ] GATE D captured `[*,H,64,64]` attention tensors from named modules.
- [ ] `nv.mode == "attention"` in 7a.
- [ ] 7b top-squares differ from the raw policy from/to squares.
- [ ] Every lczerolens/torch/onnx symbol used appeared in real discovery output.
