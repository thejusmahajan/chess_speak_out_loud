# `agents/` — the worker brief registry

One home for every task handed to a worker agent, and a permanent archive of them.

Before this existed, briefs were dropped in whatever directory was convenient. That made
two things impossible: telling a worker *"just do the current one"*, and answering
*"which brief produced this bug?"* months later. Both are now cheap.

---

## Layout

```
agents/
  README.md      <- this file: the standing contract, and how to use the folder
  ACTIVE.md      <- the index. What is live right now, and every brief's status
  briefs/        <- every brief ever written. Date-prefixed. IMMUTABLE after handover
  reports/       <- what workers hand back, plus the leader's audit verdict
```

**`briefs/` is append-only.** A brief is never edited once it has been given to a worker.
If the task changes, write a new dated brief that supersedes the old one and say so in
both. This is what makes the archive trustworthy as forensic evidence — a brief on disk
is exactly what the worker was told, not a later tidy-up of it.

Naming: `YYYY-MM-DD_short-slug.md`. The date prefix sorts chronologically, so "the
latest" is unambiguous.

---

## For the worker agent (Gemini, in Antigravity)

The standing instruction, which is all that needs to be typed:

> Read `agents/ACTIVE.md`, then execute the brief it marks **ACTIVE**. Follow it exactly.

Unless told otherwise, that is the task. If more than one is marked ACTIVE, do the
topmost. If a brief targets a different repository, its header says so — write there,
not here.

### The standing contract — applies to EVERY brief, without being restated in it

1. **Stay inside the declared scope.** Each brief names the files you may create or edit.
   Touch nothing else. If you believe you need to, **STOP and report** rather than doing it.
2. **Never invent a number.** Every figure in any document you write must come from a run
   you actually performed. No estimated, illustrative, or placeholder values — anywhere,
   including comments and docstrings.
3. **Never claim a check you did not run.** "Not run" is a valid and welcome answer.
4. **Never soften a bad result.** If the thing loses to its baseline, say it lost, plainly,
   in the table. A negative result reported honestly is a success; a dressed-up one is the
   single unrecoverable failure.
5. **Paste real terminal output** for every gate command. Not a summary, not "all tests
   passed".
6. **Deviating from the brief because reality contradicts it is GOOD** — report it clearly
   with the evidence. Deviating to make a gate pass is not.
7. **Tests must be real guards.** They are mutation-checked: the leader breaks the code a
   test claims to protect and confirms the test fails. A test that would still pass with
   the feature deleted rejects the whole submission.
8. **Commit nothing.** Leave work uncommitted so the diff can be reviewed.
9. **When a design decision is not covered by the brief, STOP and ask.** An unanswered
   question is cheap; a plausible wrong choice found later is not.

### Working in Antigravity vs. through the API

In the IDE the worker has the **whole workspace**, so briefs may reference repo files by
path (`docs/SALIENCE_PROBLEM.md`, `backend/training/relational_facts.py`) and expect them
to be read. Through the API they cannot — a brief written for that route has to inline
everything it needs. Each brief's header declares which route it was written for, because
a workspace brief pasted into a bare chat window will silently lose half its context.

---

## For the leader (Claude)

Every brief opens with this header, so provenance is greppable:

```
Brief-ID:     2026-08-19_some-slug
Written:      2026-08-19
Target repo:  chess_speak_out_loud | cnp_synthetic | job_search
Route:        Antigravity (full workspace) | API (must be self-contained)
Type:         implementation | design/brainstorm | research | audit
Status:       ACTIVE | DELIVERED | AUDITED | SUPERSEDED by <id> | ABANDONED
Depends on:   <brief-id or none>
```

**Two kinds of brief, calibrated oppositely** — this is the most common mistake:

- **Implementation, with a correctness gate** → keep it TIGHT and self-contained. Pin the
  data shapes, enumerate the tests, state the gate. The gate is the discipline; handing
  over the wider roadmap invites scope creep.
- **Design or brainstorm** → the opposite. Load it with context, prior decisions and
  constraints. Here the context *is* the work. Ask it to argue against us; a worker that
  only agrees has produced nothing.

**Audit before anything is believed.** Findings go in `reports/` next to the delivery:
`git status` (boundaries), read the **diff not the report**, re-run the gate yourself,
mutation-test the key guard, run the real path on real data, check each metric measures
what its name claims. Sign-off means "I checked", never "they said so".

**After auditing**, update the brief's `Status:` line and add the verdict row to
`ACTIVE.md`. That is what turns this folder into a bug-hunting tool: when something breaks
later, the brief that specified it, the report that delivered it, and the audit that passed
it are all findable from one place.
