# PLAN — Chess Game Trajectory Conditional Neural Process (CNP)

> **Status:** PROPOSAL / AWAITING USER REVIEW  
> **Date:** 2026-09-03  
> **Target Repository:** `chess_speak_out_loud`  
> **Script Location:** `scripts/chess_trajectory_cnp.py`  
> **Purpose:** Provide an active, hands-on, domain-grounded learning implementation of a Conditional Neural Process (CNP) in PyTorch. Bridges sparse engine evaluation to continuous trajectory uncertainty, giving an authentic, self-built answer to Dr. Ramacher's interview question.

---

## 1. Motivation: Why Chess Trajectories Demystify Neural Processes

In the earlier synthetic benchmark (`cnp_synthetic/`), the CNP was evaluated on abstract 1D curves drawn from a Gaussian Process prior. Because $x$ and $y$ were dimensionless floating-point values without physical or domain meaning, it was difficult to develop a visceral, intuitive grasp of what the model was actually learning and why its predictive variance failed on out-of-distribution shifts.

In chess, **the variables have immediate, concrete meaning**:
* **$x \in [0, 1]$ (or plies $t \in [1, T]$):** The move sequence of a chess game (normalized game progression).
* **$y \in [-1, 1]$:** The engine evaluation / win probability (e.g. $+1.0$ White winning, $-1.0$ Black winning, $0.0$ equal).
* **Context Set $C = \{(x_c, y_c)\}_{c=1}^{N_c}$:** Sparse plies where deep engine searches (LC0 / Stockfish) were computed (e.g., moves 6, 15, 24, 40).
* **Target Set $T = \{(x_t, y_t)\}_{t=1}^{N_t}$:** Plies where the engine was not run, or where continuous trajectory interpolation is required.

### The 1-to-1 Analogy to Urban Air Quality Downscaling
This maps directly to the challenge Dr. Ramacher tackles at Hereon:
* **Air Quality (Ramacher):** A continuous city grid has only 20 physical monitoring stations ($C$). You want to predict the pollution field at all unmonitored locations ($T$) with calibrated uncertainty, without paying the cubic $O(N^3)$ computational cost of a Gaussian Process.
* **Chess Trajectories:** A 60-move game has only 6 deep engine searches ($C$). You want to interpolate the continuous win-probability curve across all plies ($T$) with calibrated uncertainty in linear $O(N)$ time.

---

## 2. Mathematical Architecture: The 3 Building Blocks

A Conditional Neural Process (Garnelo et al., 2018) consists of three strictly modular components:

```
Context Points (x_c, y_c) 
       │
       ▼
 [ Encoder: e_θ ]  ──►  r_c ∈ ℝ^d (per context point)
       │
       ▼
 [ DeepSets Aggregator ] ──►  r = (1 / |C|) ∑ r_c (global game representation)
       │
       ├─────────────────────────────────────────┐
       ▼                                         ▼
Target Query x_t                           Target Query x_t'
       │                                         │
       ▼                                         ▼
 [ Decoder: d_ϕ ]                          [ Decoder: d_ϕ ]
       │                                         │
       ▼                                         ▼
 (μ_t, σ_t)                               (μ_t', σ_t')
```

### 1. The Encoder ($e_\theta$)
A Multi-Layer Perceptron (MLP) mapping each context observation pair to a latent representation:
$$r_c = e_\theta(x_c, y_c) \in \mathbb{R}^{d}$$
* Input: 2 dimensions (`[ply, eval]`)
* Layers: Linear(2, 128) $\rightarrow$ ReLU $\rightarrow$ Linear(128, 128) $\rightarrow$ ReLU $\rightarrow$ Linear(128, 128)

### 2. The DeepSets Aggregator
To allow the model to accept **any number of context points in any arbitrary order**, we apply uniform mean-pooling across the context representations:
$$r = \frac{1}{|C|} \sum_{c \in C} r_c \in \mathbb{R}^{d}$$
* **Permutation Invariance:** Swapping the order of context moves produces the exact same vector $r$.
* **Varying Context Size:** Works seamlessly whether 3 engine searches are provided or 20.

### 3. The Heteroscedastic Decoder ($d_\phi$)
A second MLP that queries the global context vector $r$ at any target ply $x_t$ and outputs a Gaussian predictive distribution:
$$d_\phi(r, x_t) \rightarrow \left(\mu(x_t), \log \sigma^2(x_t)\right)$$
* Input: $d + 1$ dimensions (`[r, target_ply]`)
* Mean head: $\mu(x_t) \in \mathbb{R}$ (predicted evaluation).
* Variance head: $\sigma(x_t) = \text{softplus}(\text{raw}_\sigma) + \epsilon$ (strictly positive uncertainty).

---

## 3. Training Objective: Gaussian Negative Log-Likelihood (NLL)

The model is trained end-to-end using standard backpropagation and Adam by maximizing the conditional log-likelihood across all target points:

$$\mathcal{L}(\theta, \phi) = - \frac{1}{|T|} \sum_{t \in T} \log \mathcal{N}\left(y_t \mid \mu(x_t), \sigma^2(x_t)\right) = \frac{1}{|T|} \sum_{t \in T} \left[ \frac{(y_t - \mu(x_t))^2}{2\sigma^2(x_t)} + \frac{1}{2} \log \sigma^2(x_t) + \frac{1}{2}\log(2\pi) \right]$$

### The Natural Self-Balancing Mechanism:
* If the model's mean prediction $\mu$ is inaccurate, the squared error term penalizes it heavily unless $\sigma^2$ widens.
* If $\sigma^2$ widens everywhere carelessly, the $\frac{1}{2}\log \sigma^2$ penalty penalizes it.
* Therefore, the network learns to be **sharp** where the context constrains the trajectory, and **uncertain** where no context data exists.

---

## 4. Implementation Specification (`scripts/chess_trajectory_cnp.py`)

The prototype will be written as a clean, self-contained, readable script with zero heavy external dependencies:

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt # or terminal ASCII fallback
```

### Components to Implement:
1. `class ChessTrajectoryDataset`:
   - Generates realistic chess game evaluation trajectories (or extracts them from game logs).
   - Trajectory characteristics: opening equality ($0.0 \pm 0.3$), positional momentum swings, tactical blunders (sharp step functions or sigmoid jumps), and endgame conversion.
   - For each batch, randomly samples $N_c \sim \mathcal{U}(3, 12)$ context points and $N_t$ target points.
2. `class ConditionalNeuralProcess(nn.Module)`:
   - Contains `Encoder`, `Aggregator`, and `Decoder`.
   - Forward pass: `forward(x_context, y_context, x_target) -> (mu, sigma)`.
3. `loss_fn(mu, sigma, y_target)`:
   - Exact Gaussian negative log-likelihood.
4. `train_cnp(model, dataset, epochs=500)`:
   - Standard PyTorch training loop on CPU (<60 seconds).
5. `visualize_game_interpolation(model, game_trajectory)`:
   - Takes a complete test game trajectory.
   - Masks all but 5 sparse "engine search" moves.
   - Queries the CNP across all 60 moves.
   - Plots:
     - Ground truth curve (dotted black).
     - Context points (red circles with markers).
     - Predicted mean $\mu(t)$ (blue curve).
     - Uncertainty ribbon $\mu(t) \pm 2\sigma(t)$ (shaded blue band).

---

## 5. What You Will Learn Visually and Articulate in the Interview

Running and inspecting this model provides four critical takeaways:

1. **The Pinching Ribbon:**
   At plies where an engine search is given, the shaded uncertainty band collapses tightly around the observation. At plies 25–40 where no engine was run, the ribbon naturally widens to reflect ignorance.
2. **Amortized Conditioning in Action:**
   Instead of inverting an $N \times N$ matrix ($O(N^3)$), conditioning is performed in a single forward pass ($O(N)$).
3. **The Limitation (Why ANPs exist):**
   Because DeepSets averages all context vectors into a single vector $r$, a dramatic tactical blunder at move 15 is averaged out across the entire game representation, causing the CNP to slightly oversmooth sharp local blunders. This directly explains why researchers invented the **Attentive Neural Process (ANP)** (replacing mean-pooling with cross-attention).
4. **The Direct Answer to Ramacher:**
   > *"I implemented a Conditional Neural Process in PyTorch to interpolate game evaluation trajectories from sparse engine evaluations. It uses an MLP encoder, DeepSets permutation-invariant aggregation, and a heteroscedastic decoder. 
   > 
   > It demonstrated how amortized conditioning collapses uncertainty around observed plies and widens over unsearched stretches in O(N) time. But it also showed me the exact bottleneck: uniform mean pooling averages the context into a single global vector, which causes underfitting on localized tactical spikes—the exact reason Attentive Neural Processes use cross-attention."*

---

## 6. Verification and Acceptance Criteria

1. **Execution:** `python scripts/chess_trajectory_cnp.py` runs out-of-the-box on CPU in under 60 seconds without errors.
2. **Convergence:** Training loss (NLL) monotonically decreases from $>1.5$ to $< -0.5$.
3. **Behavioral Invariant:**
   - Evaluated uncertainty $\sigma(x_c)$ at context points must be strictly smaller than $\sigma(x_{\text{gap}})$ in unobserved regions:
     $$\mathbb{E}[\sigma(x_c)] < \mathbb{E}[\sigma(x_{\text{gap}})]$$
4. **Visualization:** Generates an informative plot saved to `scratch/chess_trajectory_cnp_demo.png` illustrating the predicted mean and $\pm 2\sigma$ confidence envelope.
