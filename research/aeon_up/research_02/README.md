# research_02 — the same seven targets, rebuilt for Gemini Deep Research

**Filed 2026-08-28.** Supersedes `research_01`, which **stalled**: its `BRIEF.md` is 335 lines of
scope contract, output schema and checkpoints, and Gemini Deep Research is not that kind of worker.
It takes a short statement of what is wanted, proposes a research plan, browses, and returns a
sourced report. The brief was written for an agent that reads instructions; Deep Research reads a
*goal*.

> **This tool has nothing to do with the Gemini in the Antigravity IDE.** It is the web app, it has
> no filesystem, it cannot see this repository, and nothing here reaches it except what Thejus
> pastes into the box. Do not file its work under `agents/` as a worker delivery.

## The four prompts

Each is self-contained and pastes as one block. Run them in order; 1 and 2 gate things he must not
say until they return.

| # | file | targets | why the order |
|---|---|---|---|
| 1 | `PROMPT_1_people_and_project.md` | R1, R3, R4 | R1 is the highest-value fact in the whole round — he may name Karl's paper to Karl |
| 2 | `PROMPT_2_pay_and_panel.md` | R2, R5 | the €75,000 expectation is unrecalibrated until the TVöD Bund table is in hand |
| 3 | `PROMPT_3_ufp_regulation.md` | R7 | the factual base of his strongest argument |
| 4 | `PROMPT_4_probabilistic_aq_landscape.md` | R6 | genuine nice-to-have; a thin answer costs nothing |

**Why four and not one.** Deep Research writes one plan per prompt. A plan spanning the TVöD Bund
pay table *and* neural processes for air quality goes shallow on both. Each prompt here is one
coherent research question, which is the shape the tool is built for.

**Attach nothing to any of them.** Every fact asked for is public. The four files in
`research_01/inputs/` exist to stop a *reading* agent re-researching known ground; handed to Deep
Research they would produce a summary of themselves, which is the failure this round is avoiding.

## What survives from research_01

The **seven targets and their reasoning** — unchanged, and still authoritative in the registered
brief `agents/briefs/2026-08-28_aeon-up-external-facts.md`. What was dropped is the machinery: the
exclusion list, the output schema, the seven-question checkpoint. Two things were kept because they
change what comes back, and both are inlined in every prompt in one short paragraph:

- **UNVERIFIED is a complete success**, with the reason attached — these facts get said aloud to
  the people who wrote the underlying papers, so a gap costs nothing and a plausible reconstruction
  is a disaster. The banned words are "likely", "appears to be", "approximately".
- **A URL and a verbatim quotation per fact**, never a paraphrase.

## Returned reports

Drop each into `report/` as `R<n>_<slug>.md`. **Nothing in a report is believed until audited** —
every DOI resolved, every quotation re-fetched against its source. This application has already
carried two fabricated citations (Cabaneros, Andersson) for months. A target marked UNVERIFIED
needs no audit; a target answered confidently is where to look first.
