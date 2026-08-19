# CV / Cover-Letter Module — Neural Network Interpretability

Drop-in module for `CORE_QUALIFICATIONS.md` in the `job_search` repo, written in
the same format as the existing "High-Performance Python / Deep Learning" entry.

**Every claim below was verified against the code on 2026-08-15, and re-verified after the history-planes fix.** Compiled CV: `applications/ml_interpretability_general/` in the job_search repo. File and line
references are given so you can defend each one in an interview. §5 lists what
you must *not* claim — read it before using any of this.

---

## 2. Neural Network Interpretability & Applied ML Engineering (PyTorch / ONNX / Transformers)

**Source Reference:** `chess_speak_out_loud` — `backend/neural_vision.py`, `backend/training/metrics.py`, `backend/engine_manager.py`
**Key Concepts:** Mechanistic interpretability, transformer attention extraction, PyTorch forward hooks, ONNX→PyTorch conversion, activation capture, batched GPU inference, policy-distribution analysis, async engine orchestration, FastAPI, React/TypeScript.

### **CV Bullets (Experience / Independent Research):**

- Built an interpretability toolchain for **Leela Chess Zero's BT3 transformer**, extracting internal attention from a 15-layer encoder stack by registering **PyTorch forward hooks** on each layer's query-key softmax module and capturing the per-head 64×64 attention tensors during inference.
- Identified and fixed a **reference-frame defect** in the attention pipeline: the network encodes its input from the side-to-move's perspective, so extracted attention maps were mirrored for half of all positions. Quantified the defect (mean per-square residual 0.0003 against the rank-flipped map across 40 positions) and shipped a corrected absolute-frame API with regression tests.
- Found a **second, larger defect while writing the first up**: the model's 112-plane input carries ~84 history planes that were being left empty, so every forward pass ran out of distribution — the value head returned a certain-loss verdict on 20/20 midgame positions. Rebuilt input construction to carry real move history and validated against the reference engine as ground truth: top-1 policy agreement rose from 1/6 to 5/6. Publicly corrected the earlier write-up rather than leaving it standing.
- Engineered a **batched inference path** computing attention for *N* positions in a single forward pass, with automatic CUDA/CPU device selection — the change that made whole-game analysis tractable.
- Authored a **normative metrics module** (710 lines, pure functions, fully unit-tested) formalising policy divergence, attention engagement and saliency concentration as the project's single mathematical source of truth.
- Built a **deterministic symbolic feature extractor** (787 lines) decoding board positions into grounded relational facts — absolute and relative pins, x-rays, outposts, pawn-structure weaknesses, colour-complex holes — used to ground model outputs in verifiable structure rather than generated prose.
- Designed **async orchestration for neural engine inference**: UCI process management, raw policy-head extraction at a single node (priors before search), multi-PV search, and an `EnginePool` providing position-level parallelism behind an identical interface.
- Delivered the whole system end to end: **~20,400 lines of Python** (FastAPI) and **~6,700 lines of TypeScript** (React 19), covered by an automated suite (**302 backend** passing as of 2026-08-19, plus frontend; re-run before quoting).

### **CV Bullets (Projects):**

**Neural Network Interpretability for Chess Engines** • [GitHub Repository](https://github.com/thejusmahajan/chess_speak_out_loud)
- Extracts and visualises the internal attention of a 15-layer transformer (Leela Chess Zero BT3) via PyTorch forward hooks on ONNX-converted weights, mapping learned attention onto board squares to expose what the network attends to when it evaluates a position.
- Full-stack research tool: FastAPI + React, LLM-generated explanations grounded in extracted model internals rather than free-form generation.

### **Cover Letter Paragraph:**

**Neural Network Interpretability:** Alongside my applied statistics work I conduct independent research into neural-network interpretability, building a toolchain that opens up **Leela Chess Zero's BT3 transformer** — a 15-layer attention model — and reads out what it computes internally. I convert the network from ONNX to PyTorch and register **forward hooks** on each encoder layer's query-key softmax to capture the raw per-head attention tensors during inference, then project them back onto the board to show which squares the model actually attends to. Doing this rigorously surfaced a subtle **reference-frame bug** — the network encodes positions from the side-to-move's perspective, so every attention map for one side was silently mirrored — which I diagnosed and fixed with regression tests. I also extract the policy head's raw prior distribution before any search, separating what the network *intuits* from what it *calculates*. This is exactly the discipline I brought to ecosystem modelling and clinical data: not trusting a model's output until I understand the mechanism producing it.

### **Short version (for CV summary / LinkedIn headline):**

> Independent research in neural-network interpretability: extracting and correcting internal attention representations from a 15-layer transformer (Leela Chess Zero), in PyTorch/ONNX, with a full-stack research tool around it.

---

## Interview defence — what to say when probed

Assume an ML engineer reads the bullet and asks. Short, true answers:

**"What do you mean by extracting attention?"**
The ONNX graph is converted to a PyTorch module tree; the encoder layers appear as named submodules (`module.encoder{i}/mha/QK/softmax`, i = 0…14). I register a forward hook on each, run one forward pass under `torch.no_grad()`, and the hooks capture the post-softmax attention tensors — shape `[batch, heads, 64, 64]`, since every board square is a token. I then aggregate over layers, heads and queries to get attention received per square. `backend/neural_vision.py:70-128`.

**"How is that different from just plotting a saliency map?"**
It isn't gradient saliency at all — no backward pass. It reads the model's actual internal attention weights, which is activation capture, the same mechanism `TransformerLens` uses for hook-based interpretability work. That's a fair thing to say and a fair place to note the limitation: I'm reading attention, not yet doing causal intervention (see below).

**"Tell me about a bug you found."** ← *your strongest interview story; lead with it. There are now two, and the pair is better than either alone.*
LC0 encodes the board from the side-to-move's perspective, so for a black-to-move position, network-internal square index 0 is a8, not a1 (a vertical reflection, rank-flipped, files unchanged). The original code mapped indices to squares as if white were always to move, so roughly half of all attention maps were mirrored — and crucially it *looked* fine: plausible heatmaps, no crash, no error. It only surfaced when I checked whether attention concentrated on squares that were tactically relevant in specific black-to-move positions and found it landing on the wrong side of the board. Fix was a separate absolute-frame API, `saliency_absolute()`, with the old frame-relative function kept and documented as unsafe for analysis. `backend/neural_vision.py:130-146`.

**The second one, and why the pair matters.** Writing up the first bug, I checked whether the figures would survive a properly-fed forward pass. They did not: BT3's input is 112 planes, ~84 of them the previous eight positions, and the code was building tensors from a bare FEN — every history plane empty. The tell was the value head returning `wdl = [0,0,1]` on 20/20 midgame positions while the engine on the same weights was sharp. I corrected the published post rather than leaving it standing.

*Why this pair works:* the first is a silent correctness bug caught by domain reasoning rather than a failing test. The second is the same discipline turned on my own published result — which is the part most candidates cannot demonstrate. Together they say: I do not trust a number because it has the right shape, including when the number is mine. Same skill as catching a coordinate-frame error in an ocean model.

**"What's the policy head thing?"**
Running the engine at `nodes=1` with `VerboseMoveStats` gives the raw policy prior — the network's move distribution *before* any tree search. Comparing that to the post-search choice separates learned intuition from calculation. `backend/engine_manager.py:239`.

**"Have you worked with GPUs?"**
Yes — batched inference with automatic CUDA/CPU selection, and the batching work was specifically to make per-position analysis tractable across whole games. Be straightforward that this is inference and analysis, not large-scale training.

---

## What you must NOT claim

The fastest way to lose a technically strong interviewer is one inflated claim. These are **not** in the code:

- ❌ **"Causal interventions" / "activation patching" / "circuit discovery."** You capture and read activations. You do not ablate, patch, or trace circuits. (This is also the obvious next step — see below.)
- ❌ **"Trained" or "fine-tuned" LC0.** You run inference on published weights.
- ❌ **"Probing classifiers."** No trained probes in the codebase yet.
- ❌ Any figure or reading from the *first* version of the write-up. Those were computed on bare-FEN input; the corrected figures are h5/b8/d8/f3/d5/e2.
- ❌ **Any claim built on the sacrifice/Tal metric.** That metric measures complexity with no material check — it is documented as unsound in this repo. Keep it out of applications entirely.
- ❌ Duration claims. The current git history starts 2026-07-15. Say "ongoing independent research", not "two years".

**If asked "is this mechanistic interpretability?"** — the honest answer scores better than the inflated one: *"It's the activation-capture half of it. I extract and correct internal attention representations; I haven't done causal intervention work yet, and that's precisely what I want to move toward."* That answer signals you know where the frontier is.

---

## The gap this module does not close

This makes your AI experience **legible**. It does not make it **verifiable by a stranger** — a hiring manager still cannot check any of it without cloning the repo, which they will not do.

The missing artifact is one public writeup of the reference-frame finding: what BT3 attends to, how the frame bug hid it, before/after heatmaps for the same position. Two figures and ~1,200 words. That converts every bullet above from a claim into evidence, and it is the same document that serves as a MechInterp writing sample.

**Status: done.** Published at
[thejusmahajan.github.io/blog-lc0-attention-frame.html](https://thejusmahajan.github.io/blog-lc0-attention-frame.html),
with the corrected figures and a section on the second bug. The remaining gap is
a *causal* result — ablate the heads carrying the king-square attention and
measure whether the evaluation moves. That is what turns "reads attention" into
"tested whether attention is load-bearing".
