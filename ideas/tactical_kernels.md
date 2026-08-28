# Brainstorm: Tactical Kernels and LC0 Feature Tensors

## Discussion Record

### Thejus says:
> Just as in images, we convolute a feature kernel to identify a feature, why can't we convolute a tactic kernal to the LC0 feature tensor? This tensor is not a snapshot of a game, but contains many positions of a single game and the positions that may possibly arise from them using a say, MCTS search?

### Gemini 3.7 Flash answers:
This is a fascinating and deep question that touches on the intersection of **computer vision, geometric deep learning, and game tree representation**. 

To answer why we don't (or how we could) "convolve a tactic kernel" over an LC0 tensor or an MCTS search tree, let's break this down into three core dimensions: **spatial structure (the board)**, **temporal/tree structure (MCTS search)**, and **what a "tactic" actually is mathematically**.

---

### 1. Spatial Structure: Why 2D/3D Vision Convolutions Struggle with Tactics
In computer vision, standard convolutions rely on two assumptions:
1. **Local spatial stationarity**: Features are local (an eye is a small patch of pixels) and behave similarly across regions.
2. **Translation invariance**: A cat ear looks the same whether it appears in the top-left or bottom-right corner.

**Why chess tactics violate this:**
* **Long-Range Relational Rays**: A *pin* or *skewer* is not a localized $3 \times 3$ patch. A bishop on `a1` pinning a queen on `g7` to a king on `h8` spans the entire board. A standard $3 \times 3$ CNN kernel cannot detect this in one step—it requires stacking 6–8 residual layers just for the receptive field to connect `a1` and `h8`.
* **Global Context**: Moving a single pawn on `d4` can unblock a bishop on `b2`, which suddenly attacks a knight on `f6`, which was defending a queen on `d8`. The "tactic" depends on the absence of blockers across multiple open lines simultaneously.
* **Why LC0 moved away from pure CNNs**: This is precisely why modern LC0 networks transitioned from pure ResNets to **Transformers and Attention mechanisms** (the T-series nets). Self-attention allows $O(1)$ direct message passing across arbitrary squares on the $8 \times 8$ grid without needing deep convolutional chains.

---

### 2. Search / MCTS Structure: Grids vs. Non-Euclidean Trees
If the tensor includes positions generated from a game history or an MCTS search:

* **Linear History ($T \times 8 \times 8$)**: 
  LC0 actually *does* do a form of spatiotemporal convolution on past moves! The LC0 input tensor stacks the past 8 plies as input planes ($112 \times 8 \times 8$). Early conv/attention layers process this entire stack to detect motion, tempo, and repetitions.
* **MCTS Search Space is a Tree/DAG, not a Tensor Grid**:
  MCTS does not produce a uniform grid of positions. It produces an **asymmetric, dynamically branching tree**:
  * Move $A$ might be searched 12 plies deep (tactical forcing line).
  * Move $B$ might be pruned after 2 plies.
  * In computer vision, a 3D convolution slides a fixed cuboid filter $[K_t \times K_x \times K_y]$ across regular spatial and temporal intervals. You cannot slide a regular Euclidean filter across an irregular, branching, pruned minimax tree.
* **The Equivalent: Tree Convolutions / GNNs**:
  To convolve across an MCTS tree, the mathematical equivalent is a **Graph Neural Network (GNN)**, **Tree-LSTM**, or **Message Passing Neural Network (MPNN)**, where nodes represent board states and directed edges represent move transitions and visit counts.

---

### 3. What is a "Tactic" Computationally?
A chess tactic (e.g., deflection, fork, attraction, clearance) is fundamentally **not a static pattern**, but a **conditional, minimax state-transition invariant**:
$$\text{Tactic} = \text{Sequence of forcing moves where } \forall \text{ replies } r \in R, \Delta \text{Eval} \ge M$$

* It requires evaluating **counterfactuals** ("If White plays $Q\times h7+$, Black *must* play $K\times h7$, allowing $Rh1\#$").
* A single static convolution or filter on activations cannot easily verify whether a counter-tactic exists (e.g., an in-between move / *zwischenzug*) without evaluating tree dynamics.

---

### 4. Do Deep LC0 Layers Already Learn "Tactic Kernels"?
Even though we don't hand-engineer fixed tactic kernels:

1. **Latent Concept Probes**:
   In DeepMind's paper (*"Acquisition of Chess Knowledge in AlphaZero"*, McGrath et al., 2022), probing AlphaZero's intermediate layers revealed that the network **spontaneously learns internal feature detectors** for tactical concepts (pins, forks, discovered checks, king safety, and material threats) in its middle-to-late layers.
2. **Current Engineering Practice**:
   * **Neural Network (LC0/AlphaZero)**: Uses self-attention / convolutions to evaluate static & contextual move priors and winning probabilities.
   * **Tree Search (MCTS / Alpha-Beta)**: Explores the sequential branching.
   * **Symbolic Motif Tagger (e.g. `lichess_tagger`)**: Inspects the resulting forced Principal Variation (PV) after search to deterministically classify the tactic (pins, skewers, forks, deflection, etc.) based on piece trajectory graphs.

---

### Thejus says:
> I am thinking of a dynamic kernal, that contains a series of moves resembling a tactical theme.

### Gemini 3.7 Flash answers:
Your intuition of a **dynamic kernel** that encodes a sequence of moves (a tactical theme) is a compelling idea. In modern deep learning and geometric deep learning, this connects directly to concepts like **Deformable 3D Convolutions**, **Dynamic Graph/Tree Kernels**, and **Temporal Cross-Attention**.

Here is how such a dynamic tactical kernel can be formulated, how it would operate, and the mathematical machinery required to make it work.

---

### 1. The Core Challenge: What Needs to be "Dynamic"?

A static vision kernel slides a fixed $3 \times 3$ matrix of weights over pixel coordinates. But a chess tactic like a **Greek Gift** (`Bxh7+ Kxh7`, `Ng5+ Kg8`, `Qh5...`) or a **Deflection/Back-Rank Mate** cannot use static coordinates:

1. **Spatial Deformation (Geometric Invariance)**:
   * A back-rank mate can occur on `e8`, `d8`, `c1`, or `g1`.
   * A knight fork can occur across `c7` (forking `a8` and `e8`) or `f7` (forking `d8` and `h8`).
   * *Requirement*: The spatial offsets of the kernel must dynamically warp along piece attack rays rather than fixed $(x, y)$ coordinates.

2. **Temporal & Branching Elasticity**:
   * Some tactics take 2 plies; others take 4 plies with a forced *in-between move* (*zwischenzug*).
   * *Requirement*: The temporal dimension must support non-rigid sequence alignment (like Dynamic Time Warping or soft attention).

---

### 2. Three Ways to Realize a "Dynamic Tactical Kernel"

```
[ Tactical Theme Prototype ]          [ MCTS Branch / Game State Tensor ]
(e.g., Sacrifice -> Forcing Reply -> Fork)       (Sequence of states: S_0 -> S_1 -> S_2 ...)
             \                                      /
              \                                    /
               [ Dynamic Ray-Deformable / GNN Kernel ]
                                  |
                                  v
                [ Motif Activation Score & Attribution ]
                   ("Greek Gift": 0.94 | "Pin": 0.12)
```

#### Approach A: Deformable Spatiotemporal Convolutions (Deformable 3D-CNN)
In computer vision, **Deformable Convolutions** learn spatial offset vectors $(\Delta x, \Delta y)$ so a kernel can deform to wrap around non-rigid objects.
* **In Chess**: Over a rollout sequence $(S_0, S_1, \dots, S_T)$, the kernel dynamically computes offsets:
  $$p_k' = p_k + \Delta p_k(\text{Ray}(a_t))$$
  where $\Delta p_k$ shifts the receptive field along the vector of the moved piece and the squares it suddenly attacks or vacates.
* **Result**: The filter tracks the *attracted king* and the *infiltrating queen* across time, measuring whether the delta in king safety and piece control matches the tactical template.

---

#### Approach B: Graph Motif Convolution (Tree-GNN Kernel)
Instead of treating the MCTS search as a regular tensor, represent the MCTS search tree as a directed graph where:
* **Nodes ($V$)**: Board embeddings (LC0 hidden states).
* **Edges ($E$)**: Move transitions with metadata (action type, visit count $N$, evaluation $\Delta Q$).

A **Tactical Motif Kernel** is a parameterized subgraph template:
$$\text{Score}(\text{Theme}, \text{Tree}) = \sum_{v \in \text{MCTS}} \sigma \left( \mathbf{W}_{\text{motif}} \cdot \left[ h(v) \,\|\, h(\text{child}(v)) \,\|\, \Delta \text{Eval} \right] \right)$$

* **Why this is powerful**: A "Deflection" motif kernel looks for a specific structural pattern in the graph:
  $$\text{Node } A \xrightarrow[\text{Piece Sac}]{\text{Eval drops}} \text{Node } B \xrightarrow[\text{Only 1 legal reply}]{\text{Forced capture}} \text{Node } C \xrightarrow[\text{Target square free}]{\text{Checkmate or decisive win}}$$

---

#### Approach C: Dynamic Query Cross-Attention (Transformer "Kernel")
In modern architectures, a dynamic kernel is often implemented as a **learned latent query vector** in a cross-attention layer:
1. Define a set of learnable **Tactical Theme Embeddings** $\mathbf{Q}_{\text{tactics}} \in \mathbb{R}^{K \times D}$ (e.g., $K=50$ tactical themes like Fork, Pin, Skewer, Deflection, Clearance).
2. The MCTS search branch or game sequence forms keys and values $\mathbf{K}_{\text{tree}}, \mathbf{V}_{\text{tree}}$.
3. Compute the theme-matching cross-attention:
   $$\mathbf{A} = \text{Softmax}\left( \frac{\mathbf{Q}_{\text{tactics}} \mathbf{K}_{\text{tree}}^T}{\sqrt{d}} \right) \mathbf{V}_{\text{tree}}$$
* **Activation**: If a branch exhibits a Queen sacrifice followed by a back-rank deflection, the "Deflection" query activates strongly on that branch.

---

### 3. What This Enables in Practice

1. **XAI / Natural Language Commentary**:
   * Instead of just knowing an engine move evaluates to `+4.5`, the dynamic kernel output directly provides the **reasoning chain**: *"White plays `Re8+` to trigger a back-rank deflection motif, overloading the black queen."*
2. **Search Guidance / Tactical Pruning**:
   * If a dynamic kernel fires with high probability on a candidate branch during early MCTS rollouts, MCTS can boost exploration parameters ($c_{\text{puct}}$) for that branch, preventing the engine from missing "horizon-effect" tactical traps.
3. **Automated Curriculum & Training**:
   * Analyzing a player's game tree with dynamic kernels can instantly highlight blind spots (e.g., *"You consistently fail to detect candidate lines matching the clearance-sacrifice kernel"*).
