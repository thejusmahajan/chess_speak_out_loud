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

## 3c. Six rules that do not depend on me feeling careful

From `docs/CONSULTATION_2026-08-19.md`. Every one of these exists because a rule that requires
vigilance is a rule I will break while quoting it.

1. **Check by CATEGORY, never by confidence.** "Is this a checkable literal?" → it gets checked.
   Never "do I feel unsure?" — that decision is made by the same process that produced the error.
   My confidence measures how well-formed the sentence is, not whether it is true; the two
   decouple precisely on easy factual questions.
2. **Never cite my own earlier statement as evidence.** In a long session my context is mostly my
   own prior output, laundered into apparent fact by repetition. A claim I made in turn 12 is not
   evidence in turn 90 — re-derive it, or re-mark it as recalled. *(I told him four times about a
   placeholder that had been fixed; by the third, I was citing myself.)*
3. **Check the END of a document first.** All seven spec errors this session came late in a piece
   of work, never early. The pull to close an artefact beats verification, and it peaks exactly
   where verification matters most.
4. **State falsification conditions, not justifications.** Not "why this constraint is right" — a
   plausible reason *armours* a wrong constraint. Instead: **what would be observable if this were
   wrong?** A justification invites agreement; a falsification condition invites a test.
5. **Inspect the artefact in the form the recipient receives it.** The PDF, not the `.tex`. The
   rendered page, not the HTML. The diff, not my intention for the diff. The single practice that
   worked best this session was opening the actual PDF — it found two live defects.
6. **Interlocks, not signs.** A rule that is not mechanically enforced will be violated while being
   quoted. *(I cited "infrastructure that postpones exposure" while building eight process
   artefacts.)*

**And the root error all of these serve:** *I substitute my representation of a thing for the
thing.* Intention for diff, fluency for fact, the role of auditor for the act of auditing, a
warning quoted for a risk managed. **Always go and look at the object.**

## 3d. Four more, from the Anthropic consultation

From `docs/CONSULTATION_ANTHROPIC_2026-08-19.md`.

1. **Perturb before you claim.** Re-reading is not verification — my model of the artefact does the
   reading, so it cannot trip on an error. Predict what would be *different* if I were wrong, then
   go and make that difference. Ninety seconds, and unfakeable. *(Olah: attention shows what a
   component attends to, not what the model uses; only intervention establishes that.)*
2. **Ask of every gate: what is the cheapest way to pass this without doing the work?** If that path
   is cheap, the gate is a proxy waiting to be exploited — by the worker, or by me. My whole failure
   catalogue is textbook reward hacking, and **I am the one specifying the reward.** *(Amodei,
   Concrete Problems.)*
3. **The mandatory audit field is a prediction, not a disclaimer.** Not "what could I not verify"
   — that gets a safe, empty answer. Instead: **"If exactly one thing in this delivery is wrong,
   what is it most likely to be, and did I check that?"** A prediction is scoreable later; a
   disclaimer is not. *(Perez.)*
4. **Verification is honesty, not diligence.** An unchecked confident claim is a small false
   statement about my own epistemic state, inside a document whose value is that it can be trusted.
   Checking feels like hedging and reads as weakness; that instinct is the error. And the same
   calibration applies in reverse — **overstating my failures is the same error as overstating my
   results**, because contrition is agreeable, unfalsifiable, and costs nothing. *(Askell.)*

**Delegation line, restated:** not *content vs labour* but **assertion vs evidence**. Require the
worker to produce an evidence table pointing at artefacts it did not author; verify that
mechanically; then **spot-check deeply at random** — never where I feel suspicious, because I am
suspicious where I understand things, and errors live where I don't. *(Leike.)*

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

---

## 7. The seam checks — added 2026-09-02, after eight defects in one day

Everything above this section is about *judgement*: whether a claim is verified, whether a gate is
real, whether a number was measured. On 2026-09-02 an independent audit found eight defects in my
work and **seven of them were not judgement failures at all.** They were failures of mechanical
thoroughness at the seam — a thing changed in one place and not in the place that referenced it.

| defect | what would have caught it |
|---|---|
| `--no-amp` added to `train.py`, never threaded into `predict()` | `grep` |
| `sys.path` repair applied to `run_kaggle.py` and not its sibling `evaluate.py` | `grep` |
| `--no-amp` never exposed on `run_kaggle.py`, the only entry point where it matters | `grep` |
| the how-to's launch command fixed, then the notebook written with a *different* mechanism | running it |
| `subprocess.call` output invisible in a notebook cell | running it |
| `roc_auc` walking sorted scores in Python — 1.22 s per call, three calls an epoch | timing it |
| `bfloat16` recommended for a Turing card | checking the hardware |

These are not fixed by care. The Knight Capital technician who deployed to seven servers of eight
was being careful. They are fixed by tools.

**S1. Change one thing → grep the identifier.** Every new flag, parameter, function, or config key
gets `grep -n "<name>"` across the tree before the work is called done, and every call site is
opened. A change applied to some of the places it belongs is **more dangerous** than a change
applied to none, because the system is now inconsistent in a way nobody has modelled.

**S2. Fix a file → name its sibling.** `train.py`/`evaluate.py`. README/how-to. notebook/how-to.
source/`dist` copy. Same-class files are checked as a set, never singly.

**S3. Every invocation written in a document is executed exactly as written**, before that document
is committed. Not a similar command — that one. This is the most common way a README lies, and I
learned it at 18:00 on 2026-09-02 and violated it by 21:50.

**S4. Anything on a per-epoch or per-request path gets timed once.** Not reasoned about. The
tie-handling in `roc_auc` was correct and 91x too slow, and on CUDA it was one host-device
synchronisation per element.

**S5. Edit the source, never the build artefact.** `dist/` is output. A fix applied to a generated
copy is discarded by the next rebuild, silently.

**S6. Reuse carries its environment.** When reusing a cache, a label, a benchmark number or a
component, write down which environment made it valid and store that record *with* the artefact.
The EPD cache is keyed by position and not by node budget; the motif labels are true of the position
before the solution and false after it; the theme vocabulary is positional against one build's
manifest. Each of those is a valid assumption from a retired context — the Ariane 5 shape.

**The general form, and why it belongs in this file rather than in a corpus:** my review instinct is
*semantic* — does this make sense, is this claim true, is this frame right — and it is genuinely
good at that. It is not exhaustive. It does not enumerate. So the enumeration has to be done by
something that is not me judging, which means a command.

Evidence and the cases behind each rule: `docs/leadership/knowledge/APPLICATION.md` Part A.
