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

> Read `C:\Users\Admin\Documents\chess_speak_out_loud\agents\ACTIVE.md`, find the section
> for the folder I have open, and execute its topmost brief marked **ACTIVE**. Follow it
> exactly, and follow the standing contract in that folder's `README.md`.

Unless told otherwise, that is the task.

**ACTIVE.md is grouped by workspace, not by one global order**, because briefs target three
different repositories and a worker can only act on the one it has open. Never just take
the first `ACTIVE` in the file — take the first one under *your* repository's heading.
Reports always go to `agents/reports/` in `chess_speak_out_loud`, whichever repo the work
happened in.

### INTENT OUTRANKS INSTRUCTIONS

Every brief carries an `## INTENT` section: one paragraph describing what a correct result looks
like, *independent of the instructions*.

**If any instruction conflicts with the stated intent, the intent wins — stop and report.** Doing
so is a success, never a boundary violation.

This exists because a brief once told a worker to feed a neural network no move history. The
worker complied perfectly and produced a data set that passed every gate while the model ran on 28
of its 112 input planes. There was nothing for it to check the instruction against. Now there is.

### Risk header → how much verification this task gets

Every brief header carries three fields, and they determine the protocol — not the leader's mood:

```
Blast-radius:   private | repo | external      (who sees a mistake)
Reversibility:  trivial | costly | irreversible
Failure-mode:   loud | SILENT                  (does it announce itself?)
```

| profile | required |
|---|---|
| any `external` **or** `SILENT` | full protocol + null test + spec-review pass |
| `repo` + `loud` | diff + gate re-run + mutation test |
| `private` + `loud` + `trivial` | run it, read the diff |

`SILENT` does independent work here: every serious failure in this project's history was quiet,
and size was a poor predictor of severity.

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

**Audit before anything is believed.** Findings go in `reports/` next to the delivery.

An audit that lacks any of these five fields is not an audit:

```
- boundary check:             the git status output, pasted
- gate re-run:                MY command, MY output — never theirs
- mutation proof:             what I broke, which test went red, restore confirmed
- independent re-derivation:  one number reproduced by a DIFFERENT path than their test
                              (their test can encode their misunderstanding;
                               my re-derivation cannot inherit it)
- what I could not check:     explicit, and MUST BE NON-EMPTY
```

The last field is mandatory and non-empty by design: an audit claiming to have checked everything
is either untrue or trivial. Twice this session the worker's own "could not verify" section
contained the most important finding — read it first, not last.

Sign-off means "I checked", never "they said so".

**After auditing**, update the brief's `Status:` line and add the verdict row to
`ACTIVE.md`. That is what turns this folder into a bug-hunting tool: when something breaks
later, the brief that specified it, the report that delivered it, and the audit that passed
it are all findable from one place.
