# AEON-UP — external research rounds

Interview preparation for the Hereon AEON-UP post (ref. 1056). The application was **sent
2026-08-27**; the interview is the live item. Rounds here answer questions that cannot be settled
from any file on disk.

| round | asks | status |
|---|---|---|
| `research_01` | seven external facts: Karl's UFP citation, the TVöD Bund 2026 E13 table, both PIs' output since 2024, whether AEON-UP is a public funded project, Helmholtz interview conventions, the probabilistic-AQ landscape, the revised AAQD UFP provisions | **STALLED 2026-08-28 — superseded by `research_02`.** Kept for the record; do not run it |
| `research_02` | the same seven targets, split across **four short prompts** for Gemini Deep Research | **READY TO RUN** |

## Running round 02

The tool is **Gemini Deep Research** (the web app). It has no filesystem and no sight of this
repository — and it is **not** the Gemini in the Antigravity IDE. Its output is not a worker
delivery; nothing from it is filed under `agents/reports/`.

Paste each prompt in `research_02/` as one block, in order 1 → 4, and **attach nothing**. Drop each
returned document into `research_02/report/`.

**Why round 01 stalled.** Its `BRIEF.md` is 335 lines of scope contract, output schema and
checkpoints. That is the right shape for an agent that reads instructions and executes them; Deep
Research is not one. It takes a short statement of the goal, proposes a research plan, browses, and
returns a report with sources. Round 02 gives it a goal.

**Why four prompts and not one.** Deep Research writes one plan per prompt. A plan spanning the
TVöD Bund pay table *and* neural processes for air quality goes shallow on both.

## Reading a returned report

Nothing in it is believed until audited — every DOI resolved, every quotation re-fetched. This
application has already carried two fabricated citations (Cabaneros, Andersson) for months. A
target the agent marked **UNVERIFIED** is a success and needs no audit; a target it answered
confidently is where to look first.

The registered brief and the audit ledger live in `agents/` —
`agents/briefs/2026-08-28_aeon-up-external-facts.md` remains authoritative for **what** the seven
targets are and why. `research_01/BRIEF.md` was its web adaptation and is now dead weight;
`research_02/` is the live route.
