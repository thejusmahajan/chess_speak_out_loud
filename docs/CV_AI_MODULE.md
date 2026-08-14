# CV / Cover-Letter Module — Neural Network Interpretability

Drop-in module for `CORE_QUALIFICATIONS.md` in the `job_search` repo, written in
the same format as the existing "High-Performance Python / Deep Learning" entry.

**Every claim below was verified against the code on 2026-08-15.** File and line
references are given so you can defend each one in an interview. §5 lists what
you must *not* claim — read it before using any of this.

---

## 2. Neural Network Interpretability & Applied ML Engineering (PyTorch / ONNX / Transformers)

**Source Reference:** `chess_speak_out_loud` — `backend/neural_vision.py`, `backend/training/metrics.py`, `backend/engine_manager.py`
**Key Concepts:** Mechanistic interpretability, transformer attention extraction, PyTorch forward hooks, ONNX→PyTorch conversion, activation capture, batched GPU inference, policy-distribution analysis, async engine orchestration, FastAPI, React/TypeScript.

### **CV Bullets (Experience / Independent Research):**

- Built an interpretability toolchain for **Leela Chess Zero's BT3 transformer**, extracting internal attention from a 15-layer encoder stack by registering **PyTorch forward hooks** on each layer's query-key softmax module and capturing the per-head 64×64 attention tensors during inference.
- Identified and fixed a **reference-frame defect** in the attention pipeline: the network encodes its input from the side-to-move's perspective, so extracted attention maps were mirrored for half of all positions. Shipped a corrected absolute-frame API with regression tests.
- Engineered a **batched inference path** computing attention for *N* positions in a single forward pass, with automatic CUDA/CPU device selection — the change that made whole-game analysis tractable.
- Authored a **normative metrics module** (710 lines, pure functions, fully unit-tested) formalising policy divergence, attention engagement and saliency concentration as the project's single mathematical source of truth.
- Built a **deterministic symbolic feature extractor** (787 lines) decoding board positions into grounded relational facts — absolute and relative pins, x-rays, outposts, pawn-structure weaknesses, colour-complex holes — used to ground model outputs in verifiable structure rather than generated prose.
- Designed **async orchestration for neural engine inference**: UCI process management, raw policy-head extraction at a single node (priors before search), multi-PV search, and an `EnginePool` providing position-level parallelism behind an identical interface.
- Delivered the whole system end to end: **~20,400 lines of Python** (FastAPI) and **~6,700 lines of TypeScript** (React 19), covered by **252 automated tests** across 47 backend suites and 8 frontend suites.

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

**"Tell me about a bug you found."** ← *your strongest interview story; lead with it*
LC0 encodes the board from the side-to-move's perspective, so for a black-to-move position, network-internal square index 0 is h8, not a1. The original code mapped indices to squares as if white were always to move, so roughly half of all attention maps were mirrored — and crucially it *looked* fine: plausible heatmaps, no crash, no error. It only surfaced when I checked whether attention concentrated on squares that were tactically relevant in specific black-to-move positions and found it landing on the wrong side of the board. Fix was a separate absolute-frame API, `saliency_absolute()`, with the old frame-relative function kept and documented as unsafe for analysis. `backend/neural_vision.py:130-146`.

*Why this story works:* a silent correctness bug in a model pipeline, caught by domain reasoning rather than by a test failing, then fixed with an explicit API boundary. That is the single most transferable thing you have, and it's the same skill as catching a coordinate-frame error in an ocean model.

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
- ❌ **Any claim built on the sacrifice/Tal metric.** That metric measures complexity with no material check — it is documented as unsound in this repo. Keep it out of applications entirely.
- ❌ Duration claims. The current git history starts 2026-07-15. Say "ongoing independent research", not "two years".

**If asked "is this mechanistic interpretability?"** — the honest answer scores better than the inflated one: *"It's the activation-capture half of it. I extract and correct internal attention representations; I haven't done causal intervention work yet, and that's precisely what I want to move toward."* That answer signals you know where the frontier is.

---

## The gap this module does not close

This makes your AI experience **legible**. It does not make it **verifiable by a stranger** — a hiring manager still cannot check any of it without cloning the repo, which they will not do.

The missing artifact is one public writeup of the reference-frame finding: what BT3 attends to, how the frame bug hid it, before/after heatmaps for the same position. Two figures and ~1,200 words. That converts every bullet above from a claim into evidence, and it is the same document that serves as a MechInterp writing sample.

Estimated effort: one focused day, since the finding already exists and the code already produces the figures.
