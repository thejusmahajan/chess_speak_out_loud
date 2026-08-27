```
Brief-ID:     2026-08-21_workflow-and-direction-review
Written:      2026-08-21
Target repo:  chess_speak_out_loud (primary) + job_search (Part D, read-only)
Route:        Antigravity (full workspace)
Type:         design/brainstorm
Status:       ACTIVE
Depends on:   none
```

# Read this project properly, then tell us what is wrong with it

## INTENT

A correct result is a document that makes Thejus and the leader see something about this
project they could not see from inside it: how it actually builds things (as opposed to how
its doctrine says it does), where the workflow wastes his time, what the speak-out-loud app
should become, and whether the stated aim is the right aim. Every claim about this repository
must be traceable to a file and a line. Every opinion must be **marked as an opinion and
argued**, not asserted.

**A report that concludes "the project is well organised and on track" is a failed report.**
It is a large, months-old, multi-agent codebase; it has drift. Find it.

**If any instruction below conflicts with this intent, the intent wins — stop and report.**

```
Blast-radius:   private   (a document; nothing ships from it without leader review)
Reversibility:  trivial
Failure-mode:   SILENT    <- this is the dangerous field. See §0.
```

---

## 0. Why this task is dangerous, and the one rule that contains it

This is a *contemplation* brief. You are being asked for judgement, which is exactly the
category where this project has been burned before: **three previous worker deliveries
contained fabricated content** — a DOI that does not exist (cited on 5 cards), a gate that
silently fell back to hardcoded values, a corpus of "findings" that was our own output
restated. None of them announced themselves. All read fluently.

Fluent prose about a codebase is free to produce and expensive to check. So:

> **THE RULE: every factual claim about this repository carries `path:line` and the quoted
> text. A claim without one is a defect, and the report is rejected for it — even if the
> claim happens to be true.**

Opinions and recommendations are *wanted* here, and they do not need a line number. They need
to be in the sections marked for them, phrased as opinion, and **argued against yourself at
least once**.

Two sections of your report are mandatory and must be non-empty:

- **"What I could not reach or could not check"** — put it near the TOP, not the end. Twice in
  this project the worker's own limitations section contained the single most important
  finding.
- **"If exactly one thing in this report is wrong, what is it most likely to be?"** — a
  prediction, not a disclaimer. A safe empty answer here is itself a failure.

**Never invent a number.** If you want to state a count, run the command and paste it.

---

## 1. Where to write

One file, and nothing else:

```
agents/reports/2026-08-21_workflow-and-direction-review_REPORT.md
```

**Change no other file. Write no code. Commit nothing.** If you believe something must be
edited, describe the edit in the report instead of making it.

---

## 2. Context you must read before forming any view

Read these in full — not the head, not a grep hit. They are the project's doctrine and they
contradict each other in places; finding where is part of the job.

**Doctrine (read line by line):**
```
LEADER_BIBLE.md                 (237 lines)   succession doctrine, do-not-relitigate table
COMMAND_BASE.md                 (124 lines)
LEADER_GROUNDING.md             (230 lines)   the leader's own failure catalogue
WORKER_AGENT_COOKBOOK.md        (384 lines)   how workers are instructed
GOAL_BOOK.md                    (134 lines)   product vision anchor
GOALBOOK_REVIEW.md              (111 lines)
agents/README.md                (156 lines)   the standing contract you are under
agents/ACTIVE.md                              the live index and the full ledger
docs/NORTH_STAR_decoding_lc0.md (153 lines)   the stated aim of the whole project
PLAN_SALIENCE_CNP.md            (267 lines)   the current research frontier
```

**The workflow's own self-examination (this is where the honest material is):**
```
discussions/WORKFLOW_SOLUTIONS_SESSION_2026-08-19.md   (450 lines)
discussions/CONSULTATION_ANTHROPIC_2026-08-19.md       (399 lines)
docs/SESSION_LOG_2026-08.md                            (226 lines)
agents/reports/*_AUDIT.md                              (12 audits — the verdicts are the record)
```

**The app itself:**
```
ARCHITECTURE.md   (37 lines)      HOW_TO_RUN.md (92 lines)      docs/api_contract.md
backend/          (app.py, neural_vision.py, engine_pool.py, engine_manager.py, ...)
frontend/         (src/, js/, index.html)
trainer/          (app.py, engine.py, content/ladders/*.json)   README.md is 11 lines
```

Pinned interpreter, for anything you run:
`C:\Users\Admin\miniconda3\envs\cszero\python.exe`

---

## 3. Measurements already taken — verify them, do not trust them

These were measured by the leader on 2026-08-21 in this repo. **The commands are given so you
can re-derive them.** If any number below is wrong, saying so is one of the more valuable
things you can deliver — it has happened before and it was reported as a success.

```bash
# 430 markdown files; 28 at repo root; 108 under archive/
find . -name '*.md' -not -path './node_modules/*' -not -path './.git/*' | wc -l   # 430
ls -1 *.md | wc -l                                                                # 28
find ./archive -name '*.md' | wc -l                                               # 108

# 253 python files
find . -name '*.py' -not -path './node_modules/*' -not -path '*/__pycache__/*' | wc -l  # 253

# LEADER_GROUNDING.md §5 mandates a "> **STATUS: ..." first line on any non-current doc.
# Root .md files actually carrying one:
grep -l '^> \*\*STATUS:' *.md | wc -l                                             # 2  (of 28)

# Trainer: 137 cards across 8 ladders; 85 of them on the five machine-learning ladders.
# Of the 85, only 40 have ever been answered; 45 have never been served to him.
# Mean score by ladder over the whole answer log:
#   np 0.36 (n=7)   pyt 0.55 (n=22)   de 0.56 (n=27)
#   own 0.62 (n=13) aq 0.67 (n=3)     unc 0.68 (n=11)
# Derived from trainer/content/ladders/*.json and trainer/state/answers.jsonl (83 lines).
```

**One defect found while writing this brief, given to you as a worked example of the standard:**

`LEADER_GROUNDING.md` §3c cites its source as `docs/CONSULTATION_2026-08-19.md`, and §3d cites
`docs/CONSULTATION_ANTHROPIC_2026-08-19.md`. **Neither path exists.** The real file is
`discussions/CONSULTATION_ANTHROPIC_2026-08-19.md`. So the document that tells the leader
"always go and look at the object" cites two objects it did not look at. That is the *kind* of
finding this brief wants, and the level of evidence it must carry.

---

## 4. The work — four parts

### PART A — How this project actually builds things

Not how the doctrine says it does. Reconstruct the real mechanism from the evidence:
`agents/ACTIVE.md`'s ledger, the 12 `_AUDIT.md` verdicts, the git log, the session log.

Answer, with citations:

1. **What is the actual unit of work here?** A brief? A session? A commit? What triggers one?
2. **Where does time go?** Use the ledger: how many briefs were delivered, how many were
   rejected or superseded, and *what caused the rework*? The audits name causes explicitly —
   several say "leader spec error". Count them. Categorise them.
3. **What does this workflow reliably catch, and what does it reliably miss?** The audit
   protocol is heavy. Find a real failure that got through it anyway, and say why.
4. **Where is the loop between "idea" and "Thejus sees it working" longest?** Be concrete —
   name the step.
5. **What in this repo is infrastructure that postpones exposure?** `COMMAND_BASE.md` warns
   about exactly this failure and `ACTIVE.md` records the warning being violated while quoted.
   Is it still happening right now? 430 markdown files for one app is your starting suspicion,
   but test it — some of them are load-bearing.

### PART B — What should change about the workflow

Opinion section. Argue, don't assert. For each proposal give: the problem (cited), the change,
**what it costs**, and **how we would know within a week if it was wrong**.

Constraints you must respect — these are not up for renegotiation, though you may note if one
looks harmful:

- The leader (Claude) and the worker (you, Gemini in Antigravity) are the two agents. Gemini is
  driven **manually** from the IDE, not via API.
- Content about Thejus's real career, metric definitions, and anything that drives code stays
  with the leader. Labour is delegated. (`LEADER_GROUNDING.md` §4)
- Hardware: HP EliteBook 8470p, i5-3340M, **2 cores / 4 threads**, 16 GB RAM, SSD, no usable
  GPU. GPU work goes to Colab or Kaggle. A proposal that assumes a workstation is void.
- Rules that require someone to feel careful do not count as solutions. See
  `LEADER_GROUNDING.md` §3c.6 — "interlocks, not signs".

Specifically address: **is `agents/` earning its keep, or is it ceremony?** Take the side you
actually believe after reading the ledger, and make the strongest case for the opposite view
before you conclude.

### PART C — The speak-out-loud app, and the aim

Read `GOAL_BOOK.md`, `docs/NORTH_STAR_decoding_lc0.md`, `GOALBOOK_REVIEW.md`,
`POST_VALIDATION_BACKLOG.md`, then the actual `backend/` and `frontend/` code.

1. **State the aim back in your own words**, then say whether the code is converging on it or
   drifting. Cite the code, not the docs, for the second half.
2. The North Star is: decode LC0's own plans into position-specific coaching, with the
   **LLM strictly as a translator of LC0's thoughts, never as a chess reasoner** — because a
   bad coach is worse than no coach. **Check `backend/llm_client.py` and its callers against
   that rule.** Is the LLM ever asked to reason about chess? Quote what you find.
3. **What would make this app good for its one user?** He is a ~1500-2000 player training
   specific weaknesses. Three concrete improvements, ranked, each with the cheapest possible
   version that would test whether the idea is right at all.
4. **What should be deleted?** Name features or modules that exist, cost maintenance, and do
   not serve the aim. Being wrong here is fine — being vague is not.
5. Then the harder question: **is the North Star reachable by this project, on this hardware,
   by one person?** If your answer is "not as stated", say what the honest reduced version is.
   This project's own history says its worst outcomes came from optimism that nobody checked.

### PART D — The job application  ⚑ read §5 first, this may be out of your reach

**This is the highest-stakes part of the brief and it is in a different repository.** If you
cannot read the folder named below, **say so at the top of your report and skip Part D
entirely.** Do not reconstruct it from memory or from mentions elsewhere in the chess repo —
a previous audit's single biggest gap was exactly this, and it hid a live error in a document
that was about to be submitted.

```
C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\
    cover_letter_hereon.tex   cover_letter_hereon.pdf
    cv_hereon_aeon_up.tex     cv_hereon_aeon_up.pdf
    STUDY_BOOK.md
    study_room/00_START_HERE.md ... 11_glossary.md   (12 files, ~2900 lines)
```

**The facts:** Postdoc, Helmholtz-Zentrum Hereon, Institute of Coastal Environmental Chemistry,
Geesthacht. Project **AEON-UP** — probabilistic deep learning for urban air quality. PIs
Dr. Matthias Karl (EPISODE-CityChem, aerosol/dispersion) and Dr. Martin Ramacher (urban emission
inventories, UrbEm/CMAQ). **Deadline 2026-09-03. Not yet sent.** Thejus's background: physics →
marine ecosystem modelling → bioinformatics, now moving to ML. He is in Hamburg; the visa
timeline is real pressure.

Do this:

1. **Read the PDF, not just the `.tex`.** The recipient gets the PDF; the project has twice
   found live defects only by opening the rendered artefact. If you cannot open a PDF, say so.
2. **Adversarial read of the cover letter and CV.** Where would a physics-based modelling group
   that is *hiring a capability it does not have* be unconvinced? Where does it overclaim?
   Cross-check every claim against `study_room/06_do_not_claim.md`, which is the binding list.
   Quote any violation exactly.
3. **The gap the leader already measured, for you to extend:** the 85 machine-learning trainer
   cards contain **zero** occurrences of `GOTM`, `FABM`, `NetCDF`, `HPC`, `marine`, `ocean`,
   `Karl`, `Ramacher`, `UrbEm`, `AEON` or `Hereon`.
   (`cd trainer/content/ladders && grep -oi 'GOTM\|NetCDF\|Ramacher\|AEON' *.json | wc -l` → 0.)
   So he is drilling the methods but not the employer, and not the bridge from his own strongest
   asset — a decade of large-scale numerical environmental modelling on Linux/HPC. **Is that the
   right reading?** Check it against `study_room/04_the_bridge.md` and say whether you agree.
4. **Maximising his chances.** Opinion section, and the one place in this brief where being
   bold is more useful than being safe. What would you do in the next 13 days? Consider: what
   to put in the letter that is not in it, whether contacting a PI before applying is right for
   *this* institute and *this* culture, what a 1-page technical addendum could do, and what he
   should stop doing. Rank by expected value per hour.
5. **State what he should NOT do.** The failure mode of this file's genre is a list of
   plausible, generic career advice. Anything you write must be specific to Hereon, to AEON-UP,
   or to his actual documents.

---

## 5. Scope and reachability — check this BEFORE starting

At the very top of your report, state plainly:

- Which of these you could actually read: `chess_speak_out_loud`, `job_search`.
- Whether you could open the two PDFs.
- Any file listed in §2 or §4 you could not reach.

If `job_search` is not in your workspace, **do Parts A–C in full and stop.** A complete A–C
plus an honest "D unreachable" is a success. A guessed Part D is the single unrecoverable
failure of this brief, because its output would be used on a real application with a deadline.

---

## 6. Report shape

```
1. What I could read, and what I could not               <- FIRST. Non-empty.
2. If exactly one thing here is wrong, it is most likely <- a prediction
3. PART A — how this project actually builds things       (findings, all cited)
4. PART B — workflow changes                              (opinion, argued both ways)
5. PART C — the app and the aim                           (findings + opinion, separated)
6. PART D — the application                               (or: why it was unreachable)
7. The three things I would tell Thejus if I had one paragraph
```

Length is not a virtue. A tight report with twenty cited findings beats a long one with two.
Where you disagree with the leader's doctrine, say so directly — the doctrine is wrong often
enough that agreement is not evidence of anything.
