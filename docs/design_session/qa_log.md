# Design Session Q&A Log — Decoding LC0 & Design Interview

This document logs our Q&A session for reference and design synthesis.

---

## 1. Linear Probes on LC0 Transformer Layers

### What Linear Probes Are (In Our Architecture)

When LC0 evaluates a position, it passes board information through 15 transformer layers. In the **middle layers** (layers 6–10), the network doesn't just evaluate the static current board—it implicitly simulates future moves 3 to 7 plies ahead in its hidden activations.

A **linear probe** is a simple, lightweight mathematical classifier (a single linear transformation) trained to read those internal activations at a specific layer. It acts like a targeted "brain scan" on LC0 while it's processing:

1. **Future-Board Reading:** The probe reads what LC0 foresees happening 3–7 moves down the line *inside a single forward pass*, without waiting for MCTS search trees.
2. **Suppressed-Win Detection (The "Tal Probe"):** Research shows that in middle layers, LC0 often internally discovers a winning sacrifice. But as the signal flows to the final output layer, LC0's trained policy priors can override the discovery—talked out of it because the move looks materially expensive or counter-intuitive. The probe catches moments where **LC0's deep layers saw the winning line, but its instinct suppressed it.**

---

## 2. The LC0 Binary vs. The Transformer Network Architecture

### 1. The LC0 Binary vs. The Neural Network File

The `lc0` binary (`lc0.exe`) is a C++ search engine (MCTS) and GPU runner. By itself, it has no chess knowledge. All of LC0's chess intuition and evaluation live inside the **network weights file** (`.pb.gz` or `.onnx`).

Historically, Leela networks were ResNets (Convolutional Neural Networks). However, modern flagship Leela networks—including **BT3** (`BT3-768x15x24h`), which powers our diagnosis—are **Transformers** (specifically Transformer Encoders, similar to BERT or Vision Transformers).

### 2. Where the Transformer & Layers Come In

When a position (FEN) is evaluated:

1. **Board as Tokens:** The 64 squares of the chessboard (plus piece planes, castling rights, etc.) are converted into 64 spatial tokens, each represented as a **768-dimensional vector**.
2. **The 15 Transformer Layers:** The data passes sequentially through **15 stacked Transformer Encoder layers**:
   `Board Input -> Layer 0 -> Layer 1 -> ... -> Layer 8 -> ... -> Layer 14 -> Output Heads`
   Each layer contains **24 Multi-Head Attention (MHA)** heads and feed-forward neural networks. In these layers, tokens "attend" to each other across the board (e.g., a Bishop on `c4` attending to `f7`).
3. **The Output Heads (Layer 14):**
   - **Policy Head:** Outputs a probability distribution across all ~1,858 legal move candidates (LC0's raw move instinct).
   - **Value / WDL Head:** Outputs Win/Draw/Loss probabilities.

### 3. How We Intercept the Layers in Our Code

Because `lczerolens` exports the BT3 network into PyTorch / ONNX (see `backend/neural_vision.py`), we can attach **forward hooks** to any internal module—such as `module.encoder8/mha`. 

Instead of only reading the final move probabilities at Layer 14:
- **Attention Heatmaps:** We capture the attention matrices across all 15 layers to see which squares the net "looks at".
- **Linear Probes:** We tap into the 768-dimensional activation vectors at **Layer 6 or 8** (the middle layers) using a tiny linear model to read what future board states or tactical threats the network has internally computed before it reaches the final output.

---

## 3. PUCT MCTS Search: How LC0 Calculates

### How LC0 Calculates (PUCT MCTS)

It is **never random**. LC0 uses **PUCT (Predictor Upper Confidence bounds applied to Trees)**, where the neural network directs every single step of the calculation.

1. **The Instant Reaction (Policy Prior):**
   When MCTS considers a position, it doesn't play random moves. It passes the board to the Transformer network. The network's **Policy Head** outputs a probability `P` for every legal move (e.g., `e4`: 65%, `d4`: 25%, `h3`: 0.1%).

2. **Targeted Exploration (PUCT Formula):**
   The C++ binary uses the PUCT formula to decide which move to simulate next:
   `Priority = Average Win Rate (Q) + Neural Instinct (P) * (sqrt(Total Visits) / (1 + Move Visits))`
   - High-policy moves (high `P`) get calculated first and deepest.
   - Low-policy moves (low `P`) are ignored unless the high-policy moves fail during calculation (`Q` drops).

3. **Evaluation without Rollouts (Value Head):**
   When MCTS reaches a new position at the end of a candidate line, it **does not play out the game to the end**. It simply runs the position through the Transformer network's **Value Head**, which instantly outputs the Win/Draw/Loss probability (e.g., White Win 60%, Draw 30%, Black Win 10%).

4. **Backpropagation:**
   That win probability is passed back up the search tree, updating the evaluation of every move leading to it.

### Summary of the Marriage:
- **The Transformer (The Intuition):** Tells the binary *where to look* (`P`) and *how good a position is* (`WDL`).
- **The Binary (The Calculator):** Manages the tree, tracks visit counts, and tests if the network's intuition survives deep tactical calculation.

---

## 4. MCTS Node Expansion Loop: Step-by-Step

**User Question:** *"So, when a position is presented to the network, It gives the presenter a policy vector. The presenter then takes this to the MCTS and each move is then visited one by one. For each move, the position is again presented to the network to get back the policy vector. Is this correct?"*

**Answer:** **Yes, that is almost 100% accurate!** Here is the exact loop LC0 executes:

1. **Root Interrogation:** The root position is fed into the network. The network returns:
   - **Policy Vector ($P$):** Probabilities for all legal moves from the root.
   - **Value ($V/WDL$):** Evaluation of the root.
2. **Selection (PUCT):** MCTS uses the PUCT formula to pick the single most promising move to explore (based on high policy $P$ and high win rate $Q$).
3. **Expansion & Child Interrogation:** MCTS plays that move internally to reach a *new child position*. It feeds this **new child board** into the network, which returns:
   - A **new Policy Vector ($P_{child}$)** for all legal moves available from that *new* position.
   - A **new Value/WDL ($V_{child}$)** evaluating the *new* position.
4. **Backpropagation:** The child's evaluation ($V_{child}$) travels back up to the root, updating visit counts ($N$) and win rates ($Q$) along that path.
5. **Repeat:** MCTS goes back to step 2 for the next search iteration.

**Key Nuance:** MCTS doesn't cycle through moves in simple linear order (move 1, move 2, move 3). It continuously chooses the highest-priority leaf node according to PUCT, expanding one new board at a time and interrogating the network for that new board's Policy + Value.

---

## 5. What Is This Process Called?

**User Question:** *"So, this back and forth. What is this process called?"*

**Answer:** In AI architecture and computer science, this back-and-forth loop is called **Neural-Guided Monte Carlo Tree Search (Neural MCTS)**, or specifically the **Search-Inference Loop**.

It consists of two complementary systems:

1. **The Search-Inference Loop:** The operational cycle where the search engine queries the neural network (`lczerolens` / ONNX `evaluate_batch`) for a forward pass at every newly reached node.
2. **The 4 Phases of AlphaZero MCTS:**
   - **Selection:** Following the PUCT formula down the existing search tree.
   - **Expansion:** Creating a new leaf node for an unexplored move.
   - **Neural Evaluation (Inference):** Running the neural net to get Policy ($P$) + Value ($WDL$).
   - **Backpropagation:** Updating visit counts ($N$) and win-rates ($Q$) back up to the root position.

---

## 6. How They Fit Together: System Hierarchy

**User Question:** *"How does these concepts PUCT, Neural MCTS and search Inference loops comes together as a whole? Are they unrelated or used interchangeably?"*

**Answer:** They are not unrelated, nor are they strictly interchangeable. They represent **three nested layers of abstraction** describing the exact same system:

```
+-----------------------------------------------------------------------+
| 1. NEURAL MCTS (The Algorithm Family / Paradigm)                      |
|    Combining Monte Carlo Tree Search with Deep Neural Networks        |
|                                                                       |
|   +-----------------------------------------------------------------+ |
|   | 2. PUCT (The Selection Mathematics / Logic)                     | |
|   |    The formula balancing Neural Instinct (P) & Win Rate (Q)    | |
|   |                                                                 | |
|   |   +-----------------------------------------------------------+ | |
|   |   | 3. SEARCH-INFERENCE LOOP (The Hardware/Software Execution) | | |
|   |   |    CPU (Search Engine) <--> GPU (Neural Net Evaluation)   | | |
|   |   +-----------------------------------------------------------+ | |
|   +-----------------------------------------------------------------+ |
+-----------------------------------------------------------------------+
```

1. **Neural MCTS (The High-Level Paradigm):**
   This is the general architecture class (pioneered by AlphaZero / LC0). It means: *"We use a tree search, but instead of traditional evaluation functions or random rollouts, a neural network guides the search and evaluates nodes."*

2. **PUCT (The Decision Math):**
   This is the specific formula used *inside* Neural MCTS during the Selection step. It dictates how the engine weighs the neural net's move instinct ($P$) against accumulated search scores ($Q$).

3. **Search-Inference Loop (The Runtime Implementation):**
   This is the low-level execution pipeline. It describes the physical back-and-forth communication where the CPU (running MCTS tree management) sends batches of positions to the GPU (running the Transformer forward pass) and receives policy/value vectors back.

---

## 7. The Story Behind PUCT: From Slot Machines to AlphaZero

**User Question:** *"I don't understand PUCT. It can be any formula. Why is PUCT and what is the story behind its name?"*

**Answer:** 

### 1. The Name: What PUCT Stands For
**PUCT** stands for **Predictor Upper Confidence bounds applied to Trees** (or **Prior-UCT**).

### 2. The Evolution (The Story Behind the Math)

#### Step 1: The Slot Machine Problem (Multi-Armed Bandits, 1950s–1990s)
Imagine you are in a casino facing 10 slot machines ("multi-armed bandits"). You don't know which machines pay out. How do you play to maximize profit?
- If you only play the machine that won first, you miss a better machine (**Exploitation failure**).
- If you test all machines equally, you waste money on bad ones (**Exploration failure**).

#### Step 2: UCB1 (Upper Confidence Bound, 2002)
In 2002, computer scientists proved a formula called **UCB1**:
`Score = Average Payout (Q) + Uncertainty Bonus`
The *Uncertainty Bonus* grows for any machine you haven't pulled in a while. As soon as you test a machine, its uncertainty drops.

#### Step 3: UCT (Upper Confidence bounds applied to Trees, 2006)
In 2006, Kocsis & Szepesvári applied UCB1 to game trees. Instead of slot machines, every move choice at a chess position was treated as a bandit problem. This was called **UCT**. 
*Problem:* UCT had **zero prior knowledge**. At every new position, it was forced to test every legal move (including blunders like `1.g4`) equally at least once before focusing.

#### Step 4: PUCT (Predictor / Prior UCT — Rosin 2011, DeepMind AlphaGo 2016)
When DeepMind introduced Neural Networks (AlphaGo / AlphaZero / LC0), they had a **Policy Head** ($P$) that gave a prediction ("instinct") for moves *before searching*.

David Silver and DeepMind created **PUCT**: they multiplied the UCB uncertainty bonus by the Neural Net's prior prediction ($P$):

`Priority = Q(s, a) + c_puct * P(s, a) * [ sqrt(Parent Visits) / (1 + Child Visits) ]`

### 3. Why THIS Formula?
1. **At low visit counts (instant):** The UCB bonus dominates. The search focuses almost 100% of its compute on moves the neural network likes ($P$ is high).
2. **At high visit counts (deep calculation):** As `Child Visits` grows, the UCB bonus shrinks to zero. The search is driven purely by the calculated win rate ($Q$).
3. **Refutation:** If a top-policy move turns out to lose ($Q$ drops to 0), the formula automatically shifts search priority to the next best candidate move.

---

## 9. PUCT Explained via the Job Interview Analogy

**User Question:** *"I don't understand. We need to look at the formula differently. Lets say, a job interview instead of dating?"*

**Answer:** 

Imagine a hiring manager at a top company who has 100 job applicants (candidate moves) for 1 open position. The hiring manager has a limited budget of interview slots (MCTS node visit budget).

How does the manager decide who gets interviewed, and who gets invited to follow-up rounds?

### The Formula:
`Priority = Q(Interview Score) + c_puct * P(Resume Rating) * [ sqrt(Total Interviews Done) / (1 + Rounds Done with Candidate) ]`

---

### 1. $P$ (Policy Prior): The Resume / Portfolio Score
* **What it is:** The Neural Network's instant assessment of the board *before* doing any calculation.
* **In Hiring:** Before interviewing anyone, HR scans resumes. Candidate A (ex-Google, 10 yrs experience) gets a high resume rating ($P_A = 70\%$). Candidate B gets $20\%$. Candidate C gets $1\%$.

---

### 2. $Q$ (Exploitation / Real Value): The Actual Interview Performance
* **What it is:** The average calculated win rate resulting from deep MCTS search.
* **In Hiring:** Candidate A gets called in for an interview. $Q$ is Candidate A's average score across actual interview rounds conducted so far.

---

### 3. $N_{child}$ (Visit Count): Number of Interview Rounds Conducted
* **What it is:** How many search visits have been spent exploring candidate move $i$.
* **In Hiring:** The more interview rounds Candidate A completes ($N_A = 1, 2, 3...$), the more certainty HR has about Candidate A's true ability. 
* As $N_A$ grows, the denominator `(1 + Rounds Done)` gets larger, which **drives Candidate A's Curiosity/Uncertainty Bonus down to zero**. You no longer need to test Candidate A out of curiosity.

---

### 4. The Full Hiring Loop (How PUCT Allocates Compute)

1. **Round 1 (Initial Screening):** Nobody has been interviewed yet ($N=0$), so $Q=0$. HR uses the **Resume Rating ($P$)** to pick who gets called first. Candidate A ($P = 70\%$) gets the first interview round.
2. **Success Case (Promoting the Star):** Candidate A aces Round 1 ($Q_A = 0.95$). Because $Q_A$ is very high, Candidate A's priority stays high, so HR invites Candidate A back for Round 2 and Round 3.
3. **The Flop / Refutation (Pivoting):** Suppose Candidate A completely bombs Round 2 coding test ($Q_A$ drops from $0.95$ to $0.10$).
4. **The Automatic Pivot:** Candidate B had a lower resume rating ($P_B = 20\%$), but Candidate B has 0 interview rounds done ($N_B = 0$). Candidate B's **Uncertainty Bonus** now outscores Candidate A's failing interview performance ($Q_A = 0.10$).
5. **The Outcome:** The formula automatically forces HR to stop wasting time on Candidate A and invite Candidate B for an interview!

---

## 10. Current Ground-Level Design Questions

1. **Policy vs. MCTS Search in Feedback:** When reviewing your blunders, does it help you more to see **where your move ranked in LC0's instant policy instinct** (e.g., *"You played a move LC0 gave 0.1% instinct to"*), or **how LC0's calculated eval dropped along the MCTS line**?
2. **The "Policy Trap":** A central metric in TS2 is a position where a move looks completely natural to human instinct (high policy) but loses instantly upon MCTS calculation. Have you noticed these "looks good, loses fast" moments in your own games, and is training to spot them a high priority for you?






