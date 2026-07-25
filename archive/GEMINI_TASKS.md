# GEMINI WORKER SPEC — Realign "Chess Speak Out Loud" to the Neural-Vision Aim

> **You are Gemini, acting as an implementation worker agent.** You have a large context
> window but you are prone to hallucinating APIs, file paths, and library methods.
> This document is your single source of truth. Follow it **exactly and in order**.
> Do not invent APIs. When this spec tells you to *verify before coding*, you must run the
> verification step and paste the real output before writing the dependent code.

---

## 0. THE POINT (read this before touching anything)

This project drifted. It became **a coach that talks** (Gemini text commentary, 4 personas,
word-label motifs). The actual aim is **a coach that shows** — it translates Leela Chess
Zero's (LC0) *neural vision* into things a human **sees on the board, with ZERO
text-generation layer.**

There are exactly **three visual primitives**, and everything you build serves them:

| Primitive | Human concept | Data source | Where it lives |
|-----------|---------------|-------------|----------------|
| **Policy arrows** | "Energy / Initiative" | LC0 **policy priors** (`P`) via `lc0.exe` UCI `VerboseMoveStats` | Backend UCI, Phase 1 |
| **Saliency heatmap** | "Structure / Vision" (which squares the net *looks at*) | **True neural attention**, extracted in **PyTorch** via `lczerolens` | Backend PyTorch, Phase 2 |
| **Feedback flash** | "Intuitive blunder" | Policy disparity `P(best) − P(userMove)` + saliency squares | Frontend, Phase 3 |

**The LLM layer is NOT deleted — it is switched OFF behind a flag** (`LLM_ENABLED = False`)
and disconnected from the request path, so nothing calls Gemini/`google.generativeai` at
runtime. The code stays in the repo, dormant.

---

## 1. HARD RULES (violating any of these is a failure)

1. **No runtime LLM.** After Phase 0, `/api/analyze` must never call `llm_client.py`,
   `concept_mapper.py`, or `get_coach_summary`. No text commentary is generated at runtime.
2. **Do not delete** `llm_client.py`, `concept_mapper.py`, `mock_data.py`, `stockfish_manager.py`,
   or `tactics.py`. Leave them on disk. Only *disconnect* the LLM path.
3. **Do not invent library APIs.** For anything involving `lczerolens`, you MUST run the
   discovery script in Phase 2.0 and paste its real output before writing extraction code.
4. **Verify each phase before starting the next.** Each phase ends with an *Acceptance check*
   — a command and an expected result. If the check fails, STOP and report; do not proceed.
5. **The neural data must be REAL.** The saliency overlay must come from the network's
   attention activations, not from `heatmap.py`'s geometric attacker-count approximation.
   `heatmap.py` may remain as a *secondary* overlay but must NOT be labeled "saliency" or
   "attention" or "what LC0 sees".
6. **Absolute paths on this machine:**
   - LC0 engine: `C:\Users\Admin\Documents\chess_speak_out_loud\engine\lc0.exe`
   - LC0 weights: `C:\Users\Admin\Documents\chess_speak_out_loud\engine\791556.pb.gz`
   - Project root: `C:\Users\Admin\Documents\chess_speak_out_loud`
7. **Shell is PowerShell / Windows.** Use `python` (not `python3`), backslash paths, and
   activate the existing venv if there is one before installing packages.
8. If a phase is genuinely blocked (e.g., `lczerolens` cannot load this specific network),
   implement the **explicitly-labeled fallback** in that phase and clearly flag in the API
   response that it is a fallback (`"saliency_source": "policy_fallback"`), then continue.

---

## PHASE 0 — Realignment & flag off the LLM

**Goal:** the backend returns pure neural data; no LLM runs.

### 0.1 Add a global flag
In `backend/app.py` (near the config block, ~line 37) add:
```python
LLM_ENABLED = False  # Aim: bypass all text-generation. Keep code dormant, never call at runtime.
```

### 0.2 Gut the LLM branch in `/api/analyze`
In `backend/app.py`, the `analyze()` handler currently builds `coach_summary` via
`get_coach_summary` + `generate_conversation`. Replace that whole block so that:
- `coach_summary` is **not** produced.
- The response no longer contains `interpretation.summary` sourced from an LLM.
- Keep `concepts.get("observations", [])` ONLY if it is purely rule-based (it is — from
  `concept_mapper.analyze_position`). It is allowed as structured data, but it must NOT be
  fed to any LLM. If you are unsure, drop `interpretation` entirely for now.
- Remove `llm_model` from `AnalyzeRequest` (or leave the field but never read it).

The `/api/analyze` JSON response after Phase 0 must be shaped like:
```jsonc
{
  "fen": "...",
  "evaluation": { "type": "cp", "value": 34 },
  "best_moves": [ ... ],          // existing
  "wdl": [w, d, l],               // existing
  "heatmaps": { ... },            // existing geometric maps (secondary, NOT "saliency")
  "policy": [ ... ],              // ADDED in Phase 1
  "saliency": { ... }             // ADDED in Phase 2
}
```

### 0.3 Update `ARCHITECTURE.md`
Rewrite the mermaid diagram and data-flow so Gemini/`google.generativeai` is shown as a
**dormant, disabled** node, and the live pipeline is:
`UI → FastAPI → LC0 (UCI policy priors) + LC0 weights (PyTorch attention) → JSON → UI (overlays)`.

### 0.4 Acceptance check
```powershell
# Start the backend, then:
curl -s -X POST http://127.0.0.1:8000/api/analyze -H "Content-Type: application/json" -d '{\"fen\":\"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1\",\"multipv\":3}'
```
**Expected:** valid JSON, and **no** network call to `google.generativeai` occurs (grep the
logs — there must be no LLM request line). `interpretation.summary` from an LLM is gone.

---

## PHASE 1 — Policy priors → "Energy / Initiative" (LC0 UCI)

**Goal:** extract LC0's real policy-head priors per move, so the frontend can draw the
top-N candidate moves as arrows whose opacity ∝ policy probability.

### 1.1 What to extract
Leela exposes per-move stats when `VerboseMoveStats` is enabled. After a search it prints
`info string` lines, one per legal move, containing at least: the move (UCI), `N` (visits),
`P` (policy prior %), `Q` (value), and `WL/D` (win/draw/loss). The **`P` value is the raw
policy prior** — this is the "vision/intuition" number we want.

> To make `P` dominate (raw intuition, minimal search distortion) run a **low-node** search,
> e.g. `go nodes 1` or `go nodes 100`. Higher nodes shift weight from `P` toward `N/Q`.

### 1.2 Implement `get_policy_distribution` in `backend/engine_manager.py`
Add an async method to `LC0Engine`:
```python
async def get_policy_distribution(self, fen: str, nodes: int = 1) -> list[dict]:
    """
    Return LC0's raw policy-head distribution for a position.
    Each entry: {"uci","san","from","to","p","q","n","wdl"}
    Sorted descending by p. p is a float in [0,1] (fraction, not percent).
    Returns [] in mock mode.
    """
```
**Implementation approach (pick after testing 1.3):**
- Preferred: enable `VerboseMoveStats` and capture `info string` lines. python-chess surfaces
  these via the `info` stream / `InfoDict["string"]`. If python-chess drops them, fall back to
  a **raw subprocess UCI conversation** (`subprocess`/`asyncio` pipe): send `uci`,
  `setoption name VerboseMoveStats value true`, `position fen <fen>`, `go nodes <nodes>`,
  read lines until `bestmove`, and regex-parse each `info string` move line.
- Convert `P: 42.11%` → `0.4211`. Compute `from`/`to` square names from the UCI move.
  Compute `san` with `chess.Board(fen).san(move)`.

### 1.3 Verify the real verbose format FIRST (do not guess the regex)
Run this and paste the actual lines before finalizing the parser:
```powershell
cd C:\Users\Admin\Documents\chess_speak_out_loud\engine
".\lc0.exe" --weights=".\791556.pb.gz"
# then type:
# uci
# setoption name VerboseMoveStats value true
# position startpos
# go nodes 1
```
Read the real `info string` lines, confirm the exact token layout (`(P: xx.xx%)`, `(Q: ...)`,
`N: ...`, `(WL: ...)`/`(D: ...)`), and write the regex to match **that** output.

### 1.4 Wire into `/api/analyze`
Call `get_policy_distribution(fen)` and add its result as the `"policy"` field. Cap the list
to the top ~20 moves.

### 1.5 Acceptance check
```powershell
python -c "import asyncio; from backend.engine_manager import LC0Engine; e=LC0Engine(); asyncio.run(e.start()); print(asyncio.run(e.get_policy_distribution('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'))[:5])"
```
**Expected:** a list of dicts, each with a `p` between 0 and 1, sorted descending, top move a
sensible opening move (e.g. `e2e4`, `d2d4`, `g1f3`), `p` values summing toward ~1 across all moves.

---

## PHASE 2 — True neural attention → "Structure / Vision" (PyTorch / lczerolens)

**Goal:** load the LC0 network into PyTorch, run a forward pass on the FEN, and extract the
**attention activations** from the transformer encoder layers, collapsed to a per-square
saliency score in `[0,1]` for all 64 squares. This is the heatmap of "what squares the
network is looking at."

> **Why this is the risky phase:** `lc0.exe`'s UCI interface does NOT expose attention
> tensors. We must run the network ourselves in PyTorch. `lczerolens` is the real library
> for this. **You will verify its actual API before writing extraction code.** Do not
> hallucinate `AttentionLens`/`ActivationLens` method names — confirm what exists.

### 2.0 API DISCOVERY (mandatory — paste real output)
```powershell
pip install lczerolens
pip install "lczerolens[backends]"   # needed to load .pb.gz via LC0 backend conversion
```
Then run and **paste the actual printed output** into your working notes:
```python
import lczerolens
from lczerolens import LczeroModel, LczeroBoard
print("lczerolens dir:", [x for x in dir(lczerolens) if not x.startswith("_")])
print("LczeroModel methods:", [x for x in dir(LczeroModel) if not x.startswith("_")])
# Try to load THIS network. The exact loader name is uncertain — test the candidates
# and keep whichever one actually works. DO NOT assume; run it:
for name in ["from_path", "from_onnx", "from_pb", "load"]:
    print(name, hasattr(LczeroModel, name))
```
Confirm from the real output:
- the correct **loader** for `engine\791556.pb.gz` (may require an intermediate ONNX
  conversion — the `[backends]` extra provides this; follow the library's documented
  conversion if `from_path` on a raw `.pb.gz` fails),
- the **output dict keys** from a forward pass (`policy`, `value`/`wdl`, etc.),
- the **module names** of the attention layers (see 2.2).

### 2.1 New module `backend/neural_vision.py`
Create a `NeuralVision` class (loaded once, reused):
```python
class NeuralVision:
    def __init__(self, weights_path: str): ...
    def is_available(self) -> bool: ...
    def saliency(self, fen: str) -> dict[str, float]:
        """
        Returns {square_name: score in [0,1]} for all 64 squares, derived from the
        network's attention activations on this position. Higher = the network is
        attending more to that square.
        """
```

### 2.2 Extract attention (the core step)
Modern Leela nets are transformers over 64 tokens (one per square). To get attention:
1. Load the model (per 2.0), set `eval()` mode.
2. Build the board tensor from the FEN via `LczeroBoard` and the model's `prepare_boards`.
3. **Register forward hooks** on the encoder attention sub-modules (identify them from the
   module names printed in 2.0 — likely containing `attn`/`attention`/`mha`). Capture the
   attention weight tensors (shape roughly `[batch, heads, 64, 64]`).
4. Run one forward pass.
5. Collapse to a 64-vector saliency: average attention over heads and layers, then reduce the
   `[64, 64]` attention matrix to a per-square score (e.g. **attention received** = column-sum,
   or attention-rollout across layers). Normalize to `[0,1]`.
6. Map the 64 values to square names `a1..h8` (mind LC0's board orientation — verify the
   token→square ordering; LC0 tokenizes from White's a1. Test with a lopsided position to
   confirm the hot squares land where the action is).

> If `lczerolens` exposes a purpose-built activation/attention hook helper (check 2.0 output,
> and its `tdhook`/`nnsight` integration), prefer that over manual `register_forward_hook`.

### 2.3 Wire into `/api/analyze`
Instantiate `NeuralVision` once at startup (like the engine singleton). In `analyze()`, add
`"saliency": neural_vision.saliency(fen)` when available. Add
`"saliency_source": "attention"` on success.

### 2.4 FALLBACK (only if 2.2 is genuinely infeasible for this network)
If, after honest effort, attention cannot be extracted from `791556.pb.gz` via `lczerolens`:
derive a saliency proxy by aggregating the **Phase-1 policy priors** onto squares (sum each
move's `p` onto its `from` and `to` square, normalize). Set
`"saliency_source": "policy_fallback"` so it is never mistaken for real attention. Report the
blocker in your summary so the human can decide next steps. **Do not silently pass off the
geometric `heatmap.py` output as saliency.**

### 2.5 Acceptance check
```python
python -c "from backend.neural_vision import NeuralVision; nv=NeuralVision(r'C:\Users\Admin\Documents\chess_speak_out_loud\engine\791556.pb.gz'); import json; print(json.dumps(nv.saliency('r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1'), indent=0)[:400])"
```
**Expected:** 64 entries, values in `[0,1]`, with elevated scores concentrated on the active
central/kingside squares of this Italian-game position (e.g. `f7`, `e5`, `c4`, `f3` region) —
not a uniform or random spread. If uniform/random, the hook captured the wrong tensor — fix
before proceeding.

---

## PHASE 3 — Frontend: render the vision, no words

**Goal:** the board shows neural data directly. Remove text-commentary UI.

Work in `frontend/src/components/PgnViewer.tsx` (+ its CSS) and the board overlay. Use the
existing Lichess `chessground`/pgn-viewer already vendored in `frontend/public/lichess_assets/`.

### 3.1 Saliency heatmap overlay
Consume `response.saliency` (square → `[0,1]`). Render a per-square glow (CSS/Canvas overlay
aligned to the board grid). Intensity ∝ value. This is the "structure/vision" layer.

### 3.2 Policy arrows ("energy/initiative")
Consume `response.policy` (top-N). Draw each move as a semi-transparent arrow from `from`→`to`;
**opacity and width ∝ `p`.** Rendering the top ~10–20 simultaneously makes "initiative" visible
as a dense arrow cluster. Provide a toggle to show top-5 vs top-20.

### 3.3 Direct feedback loop (the "intuitive blunder" flash)
When the user plays a move:
1. Call `/api/analyze` on the pre-move FEN.
2. `disparity = p_best − p_userMove` (look up the user's move in `policy`; if absent, treat
   `p_userMove ≈ 0`).
3. If `disparity` exceeds a threshold (start at `0.25`), **flash the board** and turn the
   **saliency squares red** (reuse the 3.1 overlay, red palette). No text is shown — the red
   squares are the explanation.

### 3.4 Remove text-commentary UI
Delete/disable any component or JSX that rendered the 4-persona conversation / coach summary
text. The value/WDL may be shown as a **visual bar only**, not prose.

### 3.5 Acceptance check
Manual: load a position, confirm (a) saliency glow appears, (b) top policy moves render as
arrows scaled by probability, (c) playing an obviously bad move flashes the board red on the
saliency squares, (d) no generated sentences appear anywhere in the UI.

---

## PHASE 4 — Final verification & report

Run all four acceptance checks in order. Then write a short `REALIGNMENT_REPORT.md` in the
project root stating, per phase: PASS/FAIL, the actual command output, and — critically —
whether `saliency_source` is `"attention"` (real) or `"policy_fallback"` (degraded), plus any
blockers. **Report honestly.** If attention extraction failed, say so plainly; do not claim
the fallback is real neural attention.

---

## APPENDIX — Anti-hallucination checklist (self-audit before you claim done)

- [ ] No runtime code path reaches `google.generativeai` / `llm_client.py`.
- [ ] `policy[].p` values are real LC0 priors parsed from actual `VerboseMoveStats` output
      (you pasted the raw lines and matched the regex to them).
- [ ] `saliency` comes from attention activations you captured via a hook whose module name
      you confirmed from the printed model structure — OR it is honestly flagged
      `policy_fallback`.
- [ ] You did not rename the geometric `heatmap.py` output to "saliency".
- [ ] Every method/class you called on `lczerolens` appeared in the real `dir()` output from
      Phase 2.0 — none were assumed.
- [ ] All four acceptance checks were actually run, with output pasted into the report.
