# Vision Panel Discussion: Technical Roundtable on Advanced Chess Training & Neural Diagnostics

> [!IMPORTANT]
> **DISCLAIMER & HONESTY GUARDRAIL (READ FIRST):**
> The panel dialogue in this document features voices modeled on real people (**Gukesh**, **Tal**) and technical roles (**LC0-DEV**, **AZ-SCIENTIST**, **CLAUDE-ARCHITECT**). These are **strictly simulated personas created for internal ideation and feature design**. Nothing in this document represents an actual quote, verified statement, or direct endorsement by any living or historical person. All technical concepts are strictly grounded in our repository's existing Leela Chess Zero (BT3-768x15x24h) engine pipeline, TS2 tactical steering system, saliency transformer attention, and diagnosed player metrics.

---

## 1. Executive Framing & Context

This document captures a technical roundtable designed to generate concrete, buildable features and research probes for the *Chess Speak Out Loud* platform. Ideas generated here feed into `POST_VALIDATION_BACKLOG.md` and inform post-validation development.

### Ground Truth Diagnostic & Tooling Baseline
- **The Target Player**: A hardworking club player whose primary headline weakness is **middlegame positional blindness** (policy-blindness score of `0.18`, compared to `0.08` in openings and `0.07` in endgames), consistent across all clock regimes. The player explicitly desires to cultivate a **sacrificial, Tal-style attacking repertoire**.
- **Existing Pipeline Capabilities**:
  1. **Stage A Policy Screen**: LC0 policy distribution (`get_policy_distribution`) on `BT3-768x15x24h` computing policy-blindness metrics.
  2. **Stage B Deep Search**: Node-limited LC0 search providing confirmed blunder analysis, eval swings, and WDL values.
  3. **Transformer Attention**: `saliency_absolute(fen)` rendering BT3 square-level attention heatmaps.
  4. **TS2 Tactical Steering**: Steering engine producing `steer_findings` (candidate sacrifices with calculated complexity scores and component breakdowns).
  5. **Motif Classification**: 50+ tactical motifs via `backend/tactics.py` (`lichess_tagger` integration).

---

## 2. Technical Roundtable Dialogue

### Thread A: Deeper Diagnosis of Middlegame Positional Blindness

**LC0-DEV**: Current policy blindness tells us *that* the player picked a move LC0's prior disliked, but it doesn't tell us *why*. In LC0, middlegame positional play involves subtle trade-offs in piece mobility, pawn structure, and square control. We can extract much deeper signal from MCTS search internals without running extra engine passes:
1. **MCTS Visit Entropy & PV Churn**: Tactical positions collapse MCTS search onto 1–2 sharp lines almost immediately (low visit entropy). In quiet positional middlegames where humans get lost, MCTS displays high visit entropy across 4–6 candidate moves, and frequent root move changes across iteration counts (**PV Churn**). If a player's move sits in a high-churn node with low policy prior, they aren't just missing a tactic—they are suffering from **plan instability**.
2. **Positional Friction Index ($V - P_{\text{rank}}$)**: BT3 has separate policy ($P$) and WDL value ($V$) heads. When a player makes a positional error, the move often retains decent WDL value ($V \approx 0.50$), but has a near-zero policy prior ($P < 0.01$). This gap represents "positional friction"—a move that doesn't lose outright, but systematically degrades piece coordination.
3. **Attention Saliency Divergence**: Using `saliency_absolute(fen)`, we can measure square-attention overlap. Positional blindness frequently stems from **tactical fixation**—the player focuses attention purely on contact squares (captures/checks) while LC0's attention is distributed across quiet rerouting squares on the unengaged flank.

**AZ-SCIENTIST**: The neural mechanism behind human middlegame positional failure is fascinating. In AlphaZero self-play, positional understanding relies on multi-step non-forcing maneuvers (prophylaxis, improving the worst piece, creating pawn levers). Humans often evaluate positions statically by material and immediate tactical threats.
- When LC0 evaluates a position, its transformer layers compute inter-piece attention. If a human plays a move that drops LC0's internal pawn-structure or king-safety value expectation without dropping immediate tactical eval, they have committed **prophylactic plan drift**.
- We can formalize this into a **Policy-Search Gap Quadrant**:
  - *High Policy, High Search*: Standard GM technique (must-know baseline).
  - *High Policy, Low Search*: Human intuitive trap / positional illusion (player's instinct tricks them).
  - *Low Policy, High Search*: Hidden positional gem or tactical refutation.
  - *Low Policy, Low Search*: Pure unforced error.

**GUKESH (simulated)**: From a practical coaching perspective, a grandmaster doesn't calculate 15-ply deep in a quiet Italian or Catalan structure. We look at candidate squares, pawn levers, and piece harmony.
- If the player's policy blindness is 0.18 in the middlegame, it means their default move-generation intuition is proposing moves that the engine disallows. But showing them a 14-move engine principal variation (PV) of computer shuffling (`1. Kh1 a6 2. h3...`) is completely useless for human learning.
- **Positional Plan Verification Drill**: Instead of asking the player to guess the exact engine move, present the middlegame position and ask them to choose the *strategic direction*—e.g., "Reroute Knight to e3", "Initiate b-file pawn lever", or "Consolidate King safety". Compare their choice against LC0's top policy moves and MCTS visit distribution. This drills strategic decision-making rather than engine line memorization.

---

### Thread B: Operationalizing the Suppressed-Win Probe ("Forgotten Wins")

**AZ-SCIENTIST**: In `docs/research_learned_lookahead.md`, we documented the phenomenon of **Learned Look-Ahead in BT3**. The network's middle transformer layers (layers 8–12) implicitly simulate future moves 3–7 plies ahead inside a single forward pass. A linear probe on these middle layers can predict a winning line with ~92% accuracy.
- However, as activations flow to the final output policy head, deep **training priors can override the discovery**. The policy head suppresses the winning line (assigning prior $P < 0.05$) because the move "looks" positionally unappealing, materially extravagant, or counter-intuitive.
- This creates the **Suppressed-Win Phenomenon**: positions where LC0's internal representation *knows* a winning move exists, but its own policy prior buries it. If MCTS runs with low node counts, search never discovers it.

**LC0-DEV**: We can operationalize this without needing to retrain linear probes on intermediate layers immediately. We can detect suppressed wins using our existing Stage A & B tooling:
1. **Delta Probe (Policy vs. TS2 Steer)**: Screen positions where standard policy prior $P(a_{\text{sac}}) < 0.04$, but under TS2 tactical steering (or moderate MCTS search), $Q(a_{\text{sac}})$ surges into a decisive win ($WDL > +0.75$).
2. **False Positive Filtering**: Not every low-prior winning move is a "suppressed win". Many are hyper-deep computer calculations that no human can or should play. To ensure a suppressed win is **human-trainable**, we check its **attention coherence**: using `saliency_absolute(fen)`, the move must exhibit clear, high-density attention rays connecting the sacrificial piece to key target squares or the enemy King.

**TAL (simulated)**: This is the exact core of dynamic chess! A "suppressed win" is a position where conventional positional logic says *"Do not sacrifice!"*, but the concrete geometry of the board contains an explosive, winning breakthrough.
- Standard puzzle sets teach memorized patterns (Greek Gift, Back-Rank mate). But a **Forgotten-Win Drill** trains the player to overcome their own mental inhibition. It forces the player to ask: *"What move is my intuition actively suppressing because it looks too scary?"*
- Training these positions is how you transform a cautious positional player into a fearless attacker.

---

### Thread C: Cultivating the Tal Style (Sacrificial Intuition & TS2 Integration)

**TAL (simulated)**: Cultivating an attacking style is not about memorizing tactical lines; it is about developing **king-zone sensitivity** and **dynamic risk tolerance**.
- **Sound vs. Speculative Sacrifices**: In practical play, a sacrifice does not need an engine eval of `+3.50`. A sacrifice that yields `= 0.00` (eval equality) can be practically winning if it imposes immense defensive complexity on the opponent while leaving the attacker with simple, natural attacking moves.
- **Trainable Sac vs. Blunder**: A blunder drops material for zero dynamic compensation. A *trainable sacrifice* satisfies three criteria:
  1. Opens lines against the enemy King or clears vital attack corridors.
  2. Deprives the opponent of defensive harmony.
  3. Forces high tactical complexity (measured by high TS2 `complexity_score`), where the refutation is narrow and difficult to find over the board.

**GUKESH (simulated)**: Modern preparation requires marrying Tal's creative courage with engine rigor. You cannot just launch random sacrifices against prepared opponents; you must recognize **attack triggers**—a weak f7/h7 square, a pinned defender, opposite-colored bishops, or an uncastled King.
- To train this effectively, the platform must categorize sacrifices on a 2D matrix: **Soundness (WDL Eval)** vs. **Refutation Difficulty (TS2 Complexity)**.
- We shouldn't just present tactical puzzles. We should construct an **Attacking Repertoire**, where every opening line selected naturally leads to middlegame structures with high sacrificial potential.

**CLAUDE-ARCHITECT**: We can map this directly onto our existing TS2 steering infrastructure:
- TS2 already generates `steer_findings` with complexity scores and component breakdowns.
- **Tal Repertoire & Sparring Pipeline**:
  1. **Extraction**: Filter the player's database or curated master games for positions where TS2 identifies high-complexity candidate sacrifices ($C > 0.60, Q > 0.55$).
  2. **Motif Tagging**: Pass candidates through `backend/tactics.py` to label motifs (`greekGift`, `attractingSacrifice`, `clearance`, `kingAttack`).
  3. **Refutation Sparring (Backlog B3)**: Drop the player into the sacrificial position. If they hesitate or pick a passive move, LC0 plays the defending side. If the player plays an unsound sacrifice, LC0 demonstrates the precise refutation in interactive play.
  4. **Tal Persona (Backlog B4)**: Attach a dynamic, text-based LLM commentary persona that highlights dynamic initiative, piece activity over material, and king-safety threats.

---

### Thread D: Engine-Truth vs. Human-Practical Abstraction

**GUKESH (simulated)**: The biggest trap in AI chess coaching is **engine overfitting**. Engines see chess as a mathematical tree; humans see chess as concepts, plans, and pattern relationships.
- When an engine says a move is `+0.40` and another is `+0.10`, a human often cannot tell the difference, nor should they care. What matters is: *Is the position easy to play for a human, or is it a tightrope walk?*
- **Drillable Abstraction of Positional Understanding**:
  - Instead of training exact 10-move move sequences, train **Conceptual Milestones**: (1) Identify the weak square, (2) Identify your worst-placed piece, (3) Find the maneuvering path to improve it.
  - If the player gets the conceptual plan right (e.g., placing a Knight on an outpost), credit them even if the engine preferred a slightly different move order.

**AZ-SCIENTIST**: We can bridge engine truth and human practicality using the **Policy Prior as a Human Proxy**.
- MCTS search depth provides raw "Engine Truth", but LC0's unsearched policy prior $P(a|s)$ reflects human GM intuition (trained on millions of high-level games).
- By scoring moves along both axes (Policy Prior vs. Deep Search WDL), we can categorize positions into actionable training categories:
  - **Optical Traps (Backlog B1)**: High policy prior, but refuted by search. (Train the player to stop falling for seductive, bad moves).
  - **Hidden Gems**: Low policy prior, high search evaluation. (Expand the player's candidate move vision).
  - **Solid Technique**: High policy prior, high search evaluation. (Reinforce core positional patterns).

---

## 3. Comprehensive Feature Synthesis Table

*(Owned and synthesized by **CLAUDE-ARCHITECT**)*

| Feature / Idea | Thread | What it Gives the Player | Feasibility Tag | Uses Which Existing Piece |
| :--- | :--- | :--- | :--- | :--- |
| **Optical Trap Board Overlay (Backlog B1)** | Thread A / D | Visual overlay rendering Green (Agreement), Red (High policy, refuted by search), Gold (Hidden Gem). | **AVAILABLE** | Stage A policy screen + Stage B MCTS search evals + `gems.py` |
| **Motif-Level Blind-Rate Matrix (Backlog B5)** | Thread A / C | Pinpoints exact tactical/positional motifs (e.g., `clearance`, `outpost`) where player blind-rate spikes in middlegames. | **AVAILABLE** | Existing phase/clock aggregation joined with `backend/tactics.py` (`lichess_tagger`) |
| **Tal Persona Text Coach (Backlog B4)** | Thread C | Attacking, dynamic commentary linked directly to TS2 steer findings without audio complexity. | **AVAILABLE** | `llm_client.py` prompt templates + TS2 `steer_findings` |
| **Positional Friction Index ($V - P_{\text{rank}}$)** | Thread A | Quantifies positional plan degradation where move keeps static eval but violates piece coordination priors. | **AVAILABLE** | Stage A policy distribution + Stage B WDL evals |
| **Attention Saliency Divergence Map** | Thread A | Shows visual heatmap difference between human move target squares and LC0 transformer attention. | **AVAILABLE** | `neural_vision.saliency_absolute(fen)` |
| **Refutation Sparring Engine (Backlog B3)** | Thread C / D | Interactive drill loop: when player misses a positional/tactical move, LC0 plays the exact refutation line over the board. | **BUILDABLE** | SRS drills (`drills.py`, `attempts.py`) + node-limited LC0 engine pool |
| **Tal Sacrificial Repertoire & Complexity Builder** | Thread C | Generates a custom attacking repertoire curated for high complexity ($C > 0.60$) and sacrificial motifs. | **BUILDABLE** | TS2 `steer_findings` + `tactics.py` motif tagger + profile database |
| **Positional Plan Verification Drills** | Thread A / D | Drills strategic plan selection (piece rerouting, pawn levers) instead of exact move sequence memorization. | **BUILDABLE** | Stage A policy top-$k$ + MCTS visit distribution + PGN parser |
| **MCTS Visit Entropy & PV Churn Metric** | Thread A | Measures MCTS search tree instability to distinguish calculation failure from positional plan confusion. | **BUILDABLE** | LC0 verbose search output parsing (`test_lc0_verbose.py`) |
| **Suppressed-Win Probe ("Forgotten Wins")** | Thread B | Detects winning/sacrificial lines where BT3 intermediate look-ahead found a win suppressed by final policy priors. | **RESEARCH** | Research note `docs/research_learned_lookahead.md` + TS2 delta screening / `lczerolens` |
| **Spatial Tensor Attention Rays (Backlog B2)** | Thread A / B | Directed piece-to-piece sightlines extracted from intermediate transformer layers ($QK^T$). | **RESEARCH** | Intermediate layer extraction via `lczerolens` (expensive/experimental) |

---

## 4. Top 3 "Do Next" Recommendations

Following the completion and validation of the current diagnostic pipeline, the following three features are recommended as the top post-validation priorities. They are strictly biased toward **AVAILABLE** and **BUILDABLE** implementations that directly attack the player's **middlegame positional blindness** and **Tal-style repertoire goals**:

1. **Tal Sacrificial Repertoire & Refutation Sparring (TS2 + Backlog B3 & B4)**
   - **Feasibility**: **BUILDABLE / AVAILABLE**
   - **Why**: Directly fulfills the user's primary desire (cultivating a Tal-style attacking repertoire) by converting TS2 `steer_findings` and `tactics.py` motifs into interactive sparring drills with dynamic Tal-persona text coaching.

2. **Positional Friction Index & Plan Verification Drills**
   - **Feasibility**: **AVAILABLE / BUILDABLE**
   - **Why**: Directly targets the player's headline weakness (middlegame positional blindness, policy blindness `0.18`) by identifying positions where static evals hold but piece harmony is ruined, training conceptual strategic planning over raw calculation.

3. **Optical Trap Surfacing & Unified Board Overlay (Backlog B1)**
   - **Feasibility**: **AVAILABLE**
   - **Why**: Immediate visual UI payoff using data already computed in the diagnostic pipeline (Stage A policy mass vs. Stage B MCTS search refutations), instantly revealing where player intuition diverges from neural engine reality.
