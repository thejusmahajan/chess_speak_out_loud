```
Brief-ID:     2026-08-19_knowledge-base-audit
Written:      2026-08-19
Target repo:  chess_speak_out_loud (this one) — write ONLY to agents/reports/
Route:        Antigravity (full workspace)
Type:         design/audit
Status:       ACTIVE
Depends on:   none  (blocks 2026-08-19_knowledge-trainer-build)
```

# Audit the knowledge base for errors, contradictions and rot

This repository's markdown files are not notes. They are the **doctrine the project is built
on** and, increasingly, **the material Thejus will study before a job interview**. An error in
them propagates twice: into code, and into his head.

Your job is to find what is **wrong, contradictory, stale, or unfalsifiable** across them. This
is a reading-and-reasoning task. **Write no code. Change no file except your one report.**

**Be adversarial.** A report that says "the documentation is largely consistent" is a failed
report. Assume there are errors — there are, because these files were written over months by
several agents, and several documented decisions have since been reversed by measurement.

---

## 1. Scope, in three tiers

Audit depth should follow authority. Do not spread yourself evenly over 228 files.

### Tier 1 — DOCTRINE. Audit line by line. Everything here is load-bearing.
```
LEADER_BIBLE.md                  GOAL_BOOK.md               COMMAND_BASE.md
WORKER_AGENT_COOKBOOK.md         PLAN_SALIENCE_CNP.md       HOW_TO_RUN.md
agents/README.md                 agents/ACTIVE.md
docs/NORTH_STAR_decoding_lc0.md  docs/SALIENCE_PROBLEM.md
docs/THEME_DEFINITIONS.md        docs/POSITIONAL_DEFINITIONS.md
```

### Tier 2 — STUDY MATERIAL. He will memorise this, so factual errors matter most.
```
docs/study/*.md   (esp. MCTS_COMPANION_STUDY_GUIDE.md, STUDY_CROSS_ENTROPY_AND_OPTIMIZATION.md)
docs/research_learned_lookahead.md
C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\STUDY_BOOK.md
C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\study_room\*.md
```

### Tier 3 — HISTORY. Skim only. Flag a file solely where it **contradicts Tier 1**.
Session logs, `agents/reports/*`, `docs/discussion_*.md`, `*_REPORT.md`, old task briefs.

---

## 2. What counts as a finding

For every one, give: **file, line number, the quoted text, what is wrong, the evidence, and the
severity.**

1. **Factual error.** A statement about mathematics, machine learning, chess, or this codebase
   that is simply false. *Verify against the code by running it where you can* — the pinned
   interpreter is `C:\Users\Admin\miniconda3\envs\cszero\python.exe`.
2. **Internal contradiction.** Two documents (or two parts of one) asserting incompatible
   things. Name both sides with line numbers and say which you believe and why.
3. **Stale claim.** A statement that was true when written and is now false — a superseded
   decision, a test count, a file path, a "current state" that has moved on. These are the most
   dangerous, because they read as authoritative.
4. **Doctrine violated in practice.** A rule the documents state, which the code does not obey.
   Cite the rule and the code that breaks it.
5. **Unfalsifiable or circular claim.** An assertion presented as established that has no
   evidence behind it, or that is justified only by another document.
6. **Definition drift.** A term used with different meanings in different places. This project
   has already been burned by exactly this (a metric named "sacrifice" that measured
   complexity). Hunt for more.
7. **Study-material error (Tier 2).** A wrong formula, a misstated concept, an outdated API. Say
   what the correct version is, with a source.

**Severity:** `CRITICAL` (would cause wrong code or a wrong statement in an interview) ·
`HIGH` (misleads a reader) · `MEDIUM` (stale, confusing) · `LOW` (cosmetic).

## 3. Specific things worth checking (not a complete list — find your own)

Do not treat these as the answer key. They are examples of the *shape* of what to look for.

- Do the **stated test counts, record counts and file paths** in Tier 1 still match reality?
  Run the suite. Count the records. Check the paths exist.
- `LEADER_BIBLE.md` states rules about **hand-coded salience** and about which engine/network is
  authoritative for which purpose. Does the code obey them? Check
  `backend/training/salience_matcher.py` and `backend/neural_vision.py`.
- `docs/SALIENCE_PROBLEM.md` describes an approach to salience. `PLAN_SALIENCE_CNP.md` reports a
  measurement about how well it works. **Are they consistent?** If not, which is stale?
- `docs/THEME_DEFINITIONS.md` and `docs/POSITIONAL_DEFINITIONS.md` are supposed to be the ground
  truth for what each detector means. Do the detectors in `backend/training/relational_facts.py`
  actually implement those definitions? Sample at least four and check the code.
- `HOW_TO_RUN.md` — do the commands work as written?
- Tier 2: are the **formulas** correct? Check the cross-entropy and MCTS material especially, and
  the uncertainty material in `STUDY_BOOK.md` (CRPS, calibration, aleatoric vs epistemic).
- `study_room/06_do_not_claim.md` lists things Thejus must not claim. **Does any other document,
  CV, or study file claim one of them anyway?** This is the highest-consequence check in the
  whole audit.

## 4. Also assess the knowledge base as a *system*

Beyond individual errors, answer these:

1. **What is authoritative?** If two files disagree, is there a stated rule for which wins? If
   not, say so — that is itself a finding.
2. **What is duplicated?** Which facts are stated in several places and will therefore drift?
   Recommend a single home for each.
3. **What is missing?** What does a new reader (or a new agent) need that no document provides?
4. **What should be deleted or archived?** 228 markdown files is a liability. Name specific files
   that are dead weight and say why.
5. **Is there a maintenance mechanism?** How would anyone notice these documents going stale
   again? Propose one that is cheap.

## 5. Output

Write **one file**: `agents/reports/2026-08-19_knowledge-base-audit_REPORT.md`. Structure:

```
## PART 0 — METHOD        what you read, what you ran, what you could not check
## PART 1 — CRITICAL      findings that would cause wrong code or a wrong interview answer
## PART 2 — HIGH
## PART 3 — MEDIUM / LOW  may be a table
## PART 4 — CONTRADICTION MAP   pairs of documents that disagree, and which you believe
## PART 5 — THE BASE AS A SYSTEM   your answers to §4
## PART 6 — WHAT I COULD NOT VERIFY   be explicit and generous here
```

Rules: quote the text and give line numbers for every finding — a finding I cannot locate is
useless. Where you ran something, paste the real output. Where you are uncertain, **say so**
rather than asserting. **Do not fix anything** — the leader decides what changes; several of
these documents are deliberately worded and a "correction" could destroy a hard-won lesson.
