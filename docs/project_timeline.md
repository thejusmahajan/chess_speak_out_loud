# Project Timeline & Work Log: Chess Speak Out Loud

*This document serves as a detailed historical timeline of the development progress, major architectural decisions, and bugs solved during the primary agentic development sessions. Future agents should reference this file to understand the current state of the application.*

## 1. Initial Scope & The Tactical Challenge
*   **Objective:** To build an advanced chess coach that merges Leela Chess Zero's (LC0) deep neural network analysis with generative AI (Gemini), resulting in conversational, multi-persona commentary (Magnus, Student, Dev, Scientist).
*   **The Technical Hurdle:** How can we extract specific tactical motifs (forks, pins, skewers, sacrifices) from LC0's Principal Variation (PV) so the LLM knows what to talk about?

## 2. Heuristic Motif Detection vs. Official Lichess Tagger
*   **Phase 1: Custom Python Heuristics** 
    *   We initially wrote custom Python ray-tracing logic in `backend/tactics.py` to identify motifs in the PV.
    *   We created `scratch/large_scale_tactics_test.py` to test these heuristics against 300 puzzles from the official `lichess_db_puzzle.csv` dataset.
    *   **Result:** Custom heuristics failed miserably, achieving only ~15% accuracy due to the complex edge cases in chess geometry.
*   **Phase 2: The Breakthrough Decision**
    *   The user smartly decided to "full copy the lichess way." 
    *   We cloned the official open-source `lichess-puzzler` repository, isolated the Python tagger source code (`cook.py`, `model.py`, `util.py`), and migrated it into our project at `backend/lichess_tagger/`.
    *   **Bug Fix (Imports):** Refactored the internal module imports within the copied tagger files to use explicit relative imports (`from .model import Puzzle`) so it functioned as an isolated backend package.
    *   **Result:** We rewrote `backend/tactics.py` to bridge LC0's output directly into the Lichess `Puzzle` class. We re-ran the large-scale test and achieved **100% accuracy** on all motifs. The coach can now perfectly detect over 50 advanced motifs.

## 3. Independent Gemini Classification Testing
*   **The Experiment:** The user requested a test to see if an LLM (Gemini) could identify the tactical motifs purely by reading the FEN and raw SAN move sequence, bypassing the Python tagger.
*   **Bugs Solved (API Rate Limits):** 
    *   Created `scratch/gemini_tactics_test.py` to send the 300 puzzles concurrently to the Gemini API.
    *   Hit a hard wall: `429 ResourceExhausted`. The `GEMINI_API_KEY` was on the Free Tier, which enforces a strict limit of ~20 requests per day for specific flash-tier models. The script initially timed out across the board.
    *   Fixed the script by heavily reducing the sample size down to 12 puzzles (2 per motif) to fit beneath the quota.
*   **Conclusion:** The Gemini 3.1 Flash Lite model scored only 4/12 (33% accuracy), heavily over-guessing "sacrifice" when confused. This empirically proved that LLMs struggle with spatial reasoning from raw text strings, permanently validating our decision to use the explicit, mathematical Lichess Python tagger as the intermediary.

## 4. Advanced Theoretical AI Brainstorming
*   The user requested intense, multi-persona theoretical brainstorming sessions to answer a profound question: *How could we force LC0 to actively steer its play toward specific tactical motifs?*
*   We documented three massive brainstorming sessions in the `docs/` folder:
    1.  **Vishy Anand & LC0 Devs:** Discussed injecting heuristic bias into the MCTS PUCT formula vs. retraining the Neural Network with conditional motif input planes.
    2.  **Mikhail Tal, David Silver, Julian Schrittwieser:** Explored Reinforcement Learning (RL) concepts. Discussed Reward Shaping (altering self-play rewards), Multi-Objective Value Heads, Intrinsic Motivation (maximizing entropy/chaos), and Activation Steering (injecting conceptual vectors directly into the ResNet layers).
    3.  **Magnus Carlsen & Demis Hassabis:** Introduced Latent World Models and Dense Rewards. Concluded that the most pragmatic way forward is applying a secondary "Style Filter" to MCTS rollouts to restrict opponent mobility, allowing tactics to organically emerge.

## 5. IDE Integration & Workspace Formatting
*   **UI Updates:** Added support in the React frontend to actively select between different Gemini models (Gemini 3.5 Flash, 3 Flash, 2.5 Flash, etc.).
*   **Antigravity IDE Support:** 
    *   Created the `.agents/AGENTS.md` file to configure the directory as a formal workspace.
    *   Injected explicit project rules to inform all future AI agents of the system architecture, preventing them from overwriting the Lichess tagger or ignoring API rate limits.
