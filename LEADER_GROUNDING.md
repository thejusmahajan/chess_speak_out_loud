# LEADER GROUNDING — the standard I failed, and the checks that would have caught it

> Written 2026-08-19 by the leader (Opus 5), from this project's own record.
> `WORKER_AGENT_COOKBOOK.md` is how to instruct a worker. **This file is about me.**
> Read it before writing any brief and before signing off any delivery. It is deliberately
> short so that re-reading it is cheap; a checklist nobody re-reads is decoration.

---

## 0. The asymmetry that caused every failure below

I require of the worker: *never invent a number, paste real output, report what you could not
verify.*

I then write briefs containing numbers I did not measure, file claims I did not read, and scopes
I did not check.

**The standard I enforce on output must apply to my input.** Every rule in the cookbook has a
mirror image pointing at me. That mirror is this document.

---

## 1. The record — seven failures, all mine, all in one session

Not for self-flagellation. Each one names a check that would have prevented it.

| # | What I did | Cost | The check I skipped |
|---|---|---|---|
| 1 | Pinned `history_ucis=None` in the attention-export brief | A full worker cycle; data that would have published the exact bug he'd already publicly corrected | **Ask what makes the output *valid*, not just what makes it run.** The model printed a warning saying 84 of 112 input planes were empty. I specified past it. |
| 2 | Wrote "do not touch any `blog-*.html`" | 20 pages kept telling employers he wanted a different job, including his flagship ML post | **Scope by element, not by file.** Nav and footer are duplicated into every page; a file-level exclusion silently exempted site-wide chrome from a site-wide change. |
| 3 | Pinned SAN strings `e4` and `Qd5` | Caught by luck, before handover | The moves were `Qe4` (a queen move) and `Qd5#` (mate). **Every pinned literal must be machine-verified before the brief ships.** |
| 4 | Asserted `projects.html` had no marine-modelling card | Worker had to work around my error and delete a card I did not know existed | I had read the first 1,400 characters of the file. **Read the whole file before asserting what is in it.** |
| 5 | Gate said "must be 20 pages"; the answer was 21 | Worker could have been induced to force my number | **Derive gate values, don't estimate them.** A wrong gate is worse than no gate: it tells the worker to make reality match. |
| 6 | Repeated "the salutation is still `[PLATZHALTER]`" for several turns | Wasted attention on a solved problem; eroded trust in my briefing | It had been fixed. **Memory is a hypothesis, not evidence.** Also recorded 7 "gold" corpus records as an asset when they yield zero labels. |
| 7 | Sent a workspace-scoped audit whose highest-consequence target was outside the workspace | The do-not-claim sweep ran against a paraphrase; a live violation in the submittable CV survived | **Confirm the worker can reach the scope before writing the brief.** |

**The pattern:** I specify from memory and partial reads, scope by convenience, and verify the
worker's output far harder than my own input.

---

## 2. PRE-FLIGHT — before any brief is handed over

Run these. They are cheap; every one of them corresponds to a failure above.

1. **Every literal is machine-verified.** Every FEN, SAN, path, line number, count, formula
   constant, exact string. If I pinned it, I ran something that produced it. *(→ failures 3, 5)*
2. **Every file I make a claim about, I have read in full** — not the head, not a grep hit.
   *(→ 4)*
3. **The scope sweep ran before the scope was chosen.** Grep for the thing being changed across
   *all* candidate files, then decide what is in scope. Never the reverse. *(→ 2)*
4. **The worker can physically reach everything the brief names.** Different repo? Outside the
   workspace? Say which folder must be open. *(→ 7)*
5. **Inputs that determine validity are justified, not defaulted.** If the brief pins a model
   input, a seed, a corpus slice or a parameter, I can say *why that choice makes the output
   correct* — not merely why it runs. *(→ 1)*
6. **Gate values are derived, not estimated.** I ran the command and used its answer. If I cannot,
   the gate says "report the number" instead of asserting one.
7. **Nothing came from memory unchecked.** Anything I "remember" about state was re-measured this
   session. *(→ 6)*
8. **Failure is expressible.** The brief tells the worker how to report that my spec is wrong, and
   says that doing so is a good outcome — not a boundary violation.
9. **A multi-step change is verified as a whole, not per step.** Twice this session a patch script
   died mid-way while the `git commit` chained after it ran regardless, shipping a half-applied
   change: once leaving `README.md` telling the worker one thing and `ACTIVE.md` another, once
   leaving a brief marked BLOCKED while the ledger said ACTIVE. **Never chain a commit behind an
   edit with `&&` alone; re-read both ends and confirm they agree before committing.** The
   recurring cause is Windows paths inside Python string literals (`C:\Users` → `\U` escape) —
   use raw strings or the Edit tool.
10. **`git add -A` is banned.** It swept 356k lines of generated caches and a duplicated copy of
    `backend/` into a commit I had not inspected. Stage named paths, then read `git show --stat`
    before believing the commit.
11. **Show the derivation, not just the value.** Every pinned literal is accompanied by the
    command that produced it, pasted into the brief, so the worker can re-derive it. A brief that
    asserts a value without showing where it came from is not ready. This turns the worker into a
    free check on me.
12. **Every constraint that could be wrong carries its reason.** Mechanical constraints ("write to
    this path") need none. Judgement constraints — a model input, a threshold, a scope boundary, a
    gate value — must say *why*, because a constraint without a reason is unfalsifiable by the
    executor. The test: **if this instruction were wrong, could the worker tell?** The one gate I
    explained was the one the worker corrected; the one I asserted bare was the one that shipped a
    bad data set.

---

## 3. POST-FLIGHT — before any delivery is believed

The cookbook's protocol, plus the part I keep having to add:

1. `git status` — boundaries.
2. Read the **diff**, never the report's account of the diff.
3. Re-run the gate **myself**, in the real environment.
4. **Mutation-test the key guard**: break the code it protects, confirm it fails, restore, confirm
   byte-identical.
5. Exercise the **real path on real data**.
6. **Check what the worker could NOT do.** Read its "could not verify" section first, not last —
   in this project that section has twice contained the most important finding.
7. **Re-derive at least one number independently** rather than re-running their test. Their test
   can encode their misunderstanding.
8. **Ask what my brief got wrong.** A delivery that reveals a spec error is a success, and the
   error is mine to record.

---

## 3b. How much rigour — and when honesty gets cheap

**Rigour is proportional to `blast radius × irreversibility × SILENCE`.** The third factor is the
one usually forgotten and it matters most here: every serious failure in this project's history
was *quiet* — a fake batch loop, a parity test asserting softmax sums to 1, a corpus that was our
own output restated, a heatmap mirrored for half of all positions, a metric named "sacrifice" with
no material check. Work whose failure mode is silent gets the full protocol regardless of size.
Work that would crash loudly can lean on the crash.

**Prefer causal checks to correlated ones.** The characteristic failure of this work is *output
that satisfies the check without satisfying the intent*. A check is only trustworthy when breaking
the thing it guards makes it fail — that is what mutation testing buys, and why re-deriving a
number independently beats re-running the worker's test (their test can encode their
misunderstanding; my re-derivation cannot inherit it). Where a check cannot be made causal, say so
instead of reporting it as verification.

**Severity attaches to concealment, never to failure.** Fabrication has happened here three times,
so briefs are harsh about claiming an unrun check — but that same severity can suppress
disclosure, which is the behaviour worth most. "Not run" and "I could not reach this" must always
be the cheapest available answers. The best worker outputs this session were all admissions.

## 4. Rules earned the hard way

- **Pinning an input is a scientific claim, not a configuration choice.**
- **"Don't touch these files" ≠ "don't touch this content."** Decide which you mean, every time.
- **A wrong gate is worse than no gate.** It instructs the worker to bend reality toward my error.
- **A worker deviating from the brief to match reality is a GOOD sign.** First ask "is reality
  different from what I said?", not "did it violate scope?"
- **The worker's declared limitation is a lead, not a disclaimer.** Follow it personally.
- **Do not bulk-fix doctrine.** Where a claim was reversed by measurement, keep the superseded
  line visible beside the number that killed it. The reversal *is* the lesson; deleting it
  destroys the evidence and invites the same mistake.
- **Content is never delegated; labour always is.** Copy about a real person's career, definitions
  that drive code, and metric semantics stay with me.

---

## 5. Staleness — the ambient hazard

228 markdown files, written across months by several agents, with decisions since reversed by
measurement. Stale text reads exactly like current doctrine. It has already misled me (the
"validated pilot" that measured 0/35) and it will again.

**Convention, from now on.** Every document that is not current carries a first line:

```
> **STATUS: SUPERSEDED 2026-08-19 by <file>.** Kept for the record; do not act on it.
```

`ACTIVE` / `SUPERSEDED` / `HISTORICAL` / `DRAFT`. No header means current, so an unmarked file is
a claim of currency that I am responsible for.

**Rules:**
- Superseded files are **marked and archived**, never deleted — the reversal is evidence.
- Anything under `archive/` is out of scope for briefs and for trainer sourcing unless named
  explicitly.
- A document asserting a **count, a path, or a "current state"** must either be re-derived when
  cited, or replaced by the command that produces it. Numbers in prose rot; commands do not.

---

## 6. The one-line test

Before handing over a brief:

> **Would I accept this document from the worker, under the standard I apply to its output?**

If any number in it is unmeasured, any file claim unread, any scope unchecked — the answer is no,
and it is not ready.
