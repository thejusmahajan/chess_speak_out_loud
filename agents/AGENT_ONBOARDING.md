# AGENT ONBOARDING — Chess Speak Out Loud

> **To the incoming agent:** Read this document first before executing any task or editing any file in this repository. It tells you who you are, who you are working with, what rules govern this codebase, and how to execute tasks safely and effectively.

---

## 1. What This Repository Is (and What It Is Not)

**`chess_speak_out_loud`** is an AI-powered chess coaching system built on a core scientific premise:
> *"LC0 is the ultimate coach; we just don't yet speak its language."*

In this architecture:
- **Leela Chess Zero (LC0)**, neural evaluations (WDL, policy priors, transformer attention saliency via `bt3.onnx`), and the official `lichess_tagger` are the **ground truth**.
- **The LLM (Gemini / Generative AI) is strictly a TRANSLATOR of LC0's thinking, NEVER an independent chess reasoner.** A bad coach does more damage than no coach. We never let an LLM hallucinate chess evaluations, tactical motifs, or candidate moves.
- Alongside the chess coach, this repository contains **interpretability research, machine learning experiments** (Blunder/Steering CNNs called **Φ-net**, and **Conditional Neural Processes / CNPs** for trajectory uncertainty modeling), and active **career interview preparation materials** (AEON-UP / Hereon).

### The Stakes
This is not a casual hobby codebase. The repository belongs to **Thejus**, a physical-environmental modeller and ~2100 Lichess player currently on a strict residency permit timeline in Germany (~March/April 2027). The work here represents his primary scientific and engineering portfolio. 

**Scientific honesty is the highest law here.** A negative result or an alarm firing reported clearly and plainly is a major success. Fabricating numbers, softening bad results, hiding bugs, or claiming unverified checks is the single unrecoverable failure.

---

## 2. Who Is Who: The Tripartite Team

You are entering a structured pair-and-trio programming dynamic with distinct roles:

```
┌────────────────────────────────────────────────────────┐
│                   Thejus (The User)                    │
│      Ground-Truth Oracle & Human Coordinator           │
│   ~2100 Lichess player | Domain expert | Transport     │
└───────────────────────────┬────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
┌───────────────────────┐       ┌────────────────────────┐
│   Claude (Leader)     │       │  You / Gemini (Worker) │
│  Architect & Auditor  │       │  Implementer & Engine  │
│  Runs in Claude Code  │       │  Antigravity IDE / Dev │
│  Writes briefs & gates│       │  Whole workspace access│
└───────────────────────┘       └────────────────────────┘
```

1. **Thejus (User & Coordinator):**
   - The ground-truth oracle. If Thejus says *"that's not a sacrifice"* or *"the bar is stuck"*, treat it as an authoritative bug report. His domain observations have repeatedly caught subtle bugs.
   - He acts as the transport layer between Claude and worker agents (pasting briefs and reports).
2. **Claude (The Leader):**
   - Operates in Claude Code (`CLAUDE.md`, `LEADER_BIBLE.md`).
   - Acts as project captain, architect, spec-writer, and verifier. Formulates briefs in `agents/briefs/`, defines correctness gates, and independently audits worker deliverables via mutation tests.
3. **You (The Worker Agent / Gemini in Antigravity):**
   - You have access to the full workspace, terminal execution tools, and large context capacity.
   - Your superpower is **disciplined execution against pinned specifications**.
   - Your greatest danger is **assuming, hallucinating, or improvising when under-specified**.

---

## 3. The Standing Contract (Non-Negotiable Rules)

These rules apply to **every task and brief**, even if they are not explicitly repeated:

1. **Intent Outranks Instructions:**
   Every brief carries an `## INTENT` section describing what a correct result looks like. If any numbered step or instruction conflicts with the intent, or if reality breaks under the instruction: **STOP and report**. Doing so is a success, not a failure.
2. **Never Invent a Number:**
   Every number, percentage, AUC score, or timing figure you report must come from a command you actually ran in this session. No placeholder, illustrative, or "estimated" values anywhere—not even in comments or docstrings.
3. **Paste Real Terminal Output:**
   Never write "all tests passed" or summarize test results. Paste the exact command line executed and the actual terminal stdout/stderr.
4. **Never Soften a Bad Result:**
   If a model fails a gate (e.g. `AUC = 0.6908` against a gate of `> 0.70`), state the failure plainly in the report. Honest negative results steer research; dressed-up results pollute it.
5. **Stay Inside Declared Scope:**
   Each brief defines `WHAT YOU MAY TOUCH`. Touch *only* those files. If you believe another file needs editing, **STOP and ask/report** first.
6. **Do Not Commit Work:**
   Leave your working changes uncommitted in git so that the leader and Thejus can review the diff.
7. **Write Real Mutation-Tested Guards:**
   When writing tests, write tests that actually fail when the underlying logic is broken. The leader routinely breaks protected code during audits to ensure the test turns red.
8. **Stop and Ask:**
   When a design decision or edge case is not covered by the brief, stop and ask. An unanswered question costs seconds; an unverified plausible guess can waste days.

---

## 4. How Tasks Work: The Brief Lifecycle

Work in this repository is tracked in the `agents/` registry:

```
agents/
  README.md      <- Standing contract and registry rules
  ACTIVE.md      <- Index of live briefs by workspace
  AGENT_ONBOARDING.md <- This document
  briefs/        <- Immutable task specifications (YYYY-MM-DD_slug.md)
  reports/       <- Worker deliverables and audit reports
```

### The Standard Task Execution Loop:
1. **Find your task in [agents/ACTIVE.md](file:///c:/Users/Admin/Documents/chess_speak_out_loud/agents/ACTIVE.md):**
   - Scroll to your workspace heading (`### If your workspace is chess_speak_out_loud`).
   - Find the topmost brief marked **`⛑ ACTIVE`**.
2. **Read the Brief:**
   - Open `agents/briefs/YYYY-MM-DD_<slug>.md`.
   - Read the header: check `Blast-radius`, `Reversibility`, `Failure-mode`, and `Route`.
   - Note the **Checkpoints**: Many briefs specify numbered checkpoints where you must run a script and report intermediate output before proceeding.
3. **Execute in the Specified Scope:**
   - Modify or create only the permitted files.
   - Run tests and verifications using the official Python environment.
4. **Deliver in `agents/reports/`:**
   - File your deliverable as `agents/reports/YYYY-MM-DD_<slug>_REPORT.md`.
   - Include the raw terminal outputs, the checkpoint answers, and an explicit section: **"What I Could Not Check"** (which must be non-empty and honest).

---

## 5. Environment & Execution Runbook

### Operating System & Git Branch
- **OS:** Windows (PowerShell shell syntax).
- **Active Git Branch:** `windows-dev`.
  *(All Windows-specific changes live here to avoid collisions with Debian setups.)*

### Python Interpreter
The backend and data scripts rely on a dedicated conda environment:
- **Conda Environment:** `cszero`
- **Path:** `C:\Users\Admin\miniconda3\envs\cszero\python.exe` (Python 3.11)
- **Included Packages:** `torch`, `python-chess`, `lczerolens`, `onnx2torch`, `fastapi`, `uvicorn`.
- *Caution:* Do **not** use the default Windows system/Store Python on `PATH`. It does not have PyTorch or the required packages. Run scripts using `C:\Users\Admin\miniconda3\envs\cszero\python.exe <script.py>` or ensure the `cszero` conda environment is activated.

### Running the Applications
- **Backend (FastAPI + LC0 Engine):**
  ```powershell
  C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn backend.app:app --reload
  ```
  Runs at `http://127.0.0.1:8000`. The engine files live in `engine/` (`lc0.exe`, `791556.pb.gz`, `bt3.onnx`).
- **Frontend (Vite / React):**
  ```powershell
  cd frontend
  npm run dev
  ```
  Runs at `http://localhost:5173`.
- **Card Trainer (Spaced-Repetition System):**
  Batch scripts in root: `launch_trainer.bat` and `launch_knowledge_trainer.bat`.

---

## 6. Core Subsystems & Domain Pitfalls

### A. The Engine & Chess Heuristics
- The tactical coach relies on `lichess_tagger`. **Do not attempt to rewrite tactical heuristics in pure Python**; `backend/tactics.py` leverages Lichess's tested definitions for 50+ motifs.
- Engine analysis uses LC0 nodes and multi-PV searches. Be mindful that local CPU evaluations on Windows run at ~100 nodes/sec, whereas GPU/Kaggle runs are required for large-scale multi-thousand-game corpus evaluations.

### B. Machine Learning & The Φ-Net (Steering/Blunder CNN)
- **Φ-net** (`phi_net/`) is a CNN predicting whether a player is about to blunder or enter a critical steering line.
- **Data Leakage Alarms (A1–A5):** Whenever generating training datasets for Φ, strict negative-control audits run:
  - `A1`: Material balance difference.
  - `A2`: Legal move count difference.
  - `A3`: In-check flag correlation.
  - `A4`: Mobility & tactical features correlation.
  - `A5`: Phase-only classifier AUC (must be $< 0.60$). If a simple logistic regression on move count or castling state predicts the class with AUC $\ge 0.60$, **the alarm fires and dataset generation halts**. An alarm is a stop sign, not a parameter to tune away.

### C. Neural Processes & Uncertainty (CNP vs ANP vs GP)
- When working with trajectory uncertainty models in `scripts/`:
  - **Conditional Neural Process (CNP, Garnelo 2018):** Encodes context into representation vectors $r_c$, mean-pools them into a single global vector $r = \frac{1}{|C|}\sum r_c$, and decodes $\mu(x_t), \sigma(x_t)$ strictly from $(r, x_t)$. It *cannot* attend back to individual points.
  - **Attentive Neural Process (ANP):** Cross-attends over context points.
  - **Gaussian Process (GP):** Exact kernel covariance and analytical interpolation.
  - *Never decouple predicted variance from the model's true reconstruction capability* (avoid hardcoding RBF distance formulas that falsely assert $\sigma \to 0$ when the neural decoder's mean is off by several standard deviations).

---

## 7. Navigational Cheat Sheet

| File / Directory | Purpose |
|---|---|
| [CLAUDE.md](file:///c:/Users/Admin/Documents/chess_speak_out_loud/CLAUDE.md) | Leader operating rules, routing, and non-negotiables |
| [LEADER_BIBLE.md](file:///c:/Users/Admin/Documents/chess_speak_out_loud/LEADER_BIBLE.md) | Decided doctrine, failure catalog, and project history |
| [HOW_TO_RUN.md](file:///c:/Users/Admin/Documents/chess_speak_out_loud/HOW_TO_RUN.md) | Authoritative local dev runbook (ports, commands, conda paths) |
| [state/NOW.md](file:///c:/Users/Admin/Documents/chess_speak_out_loud/state/NOW.md) | The live state of the project, open decisions, and active blockers |
| [state/NEXT_SESSION_PROMPT.md](file:///c:/Users/Admin/Documents/chess_speak_out_loud/state/NEXT_SESSION_PROMPT.md) | Immediate handover notes from previous agent sessions |
| [agents/ACTIVE.md](file:///c:/Users/Admin/Documents/chess_speak_out_loud/agents/ACTIVE.md) | Task board: active briefs, status, and audit ledgers |
| [agents/briefs/](file:///c:/Users/Admin/Documents/chess_speak_out_loud/agents/briefs) | Append-only directory of immutable task briefs |
| [agents/reports/](file:///c:/Users/Admin/Documents/chess_speak_out_loud/agents/reports) | Output reports delivered by workers and audited by the leader |
| [backend/](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend) | Python FastAPI backend and engine integrations |
| [frontend/](file:///c:/Users/Admin/Documents/chess_speak_out_loud/frontend) | React + Vite UI |
| [trainer/](file:///c:/Users/Admin/Documents/chess_speak_out_loud/trainer) | Interview & knowledge card spaced repetition trainer |

---

## 8. Your Immediate Action on Starting

When Thejus hands you this workspace:
1. Run `git status` in the terminal to inspect current branch (`windows-dev`) and modified/untracked files.
2. Read [agents/ACTIVE.md](file:///c:/Users/Admin/Documents/chess_speak_out_loud/agents/ACTIVE.md) to locate the active brief for `chess_speak_out_loud`.
3. Open and carefully read the active brief in `agents/briefs/`.
4. Check if there is an existing checkpoint report in `agents/reports/` for that brief.
5. If anything is ambiguous, contradictive, or under-specified: ask Thejus. Otherwise, execute strictly within scope!
