# Working session: solving the failure modes this project surfaced

*A virtual design session, 2026-08-19. The brief: take the problems that actually bit us across
this project and invent mechanisms that stop them recurring. Not reflection — engineering. Every
section ends with something buildable.*

*Voices: **C** — me, bringing the problems. **S** — epistemics/verification. **ENG** — mechanism
and cost. **A** — honesty and failure modes that look like success. **H** — keeping it tied to the
human it serves.*

---

## Problem 1 — Nothing checks a brief before it executes

**C.** Seven specification errors in one session, every one executed faithfully. The worker is
audited; the instruction is not. This is the single largest hole.

**ENG.** Cheapest first: a **brief linter**. Purely mechanical, no model needed. It reads a brief
and fails on things that are checkable without understanding:

```
brief_lint.py <brief.md>
  1. every path mentioned exists (or is explicitly marked "to be created")
  2. every quoted "anchor" string actually occurs in the file it names
  3. every command in a gate block parses and its executable exists
  4. every pinned numeric claim has a DERIVATION block within N lines
  5. Brief-ID matches the filename; Status is a legal value
  6. every referenced brief-ID exists in agents/briefs/
```

**C.** Item 2 alone would have caught the `projects.html` error — I claimed no marine card existed
and the linter would have found the anchor I *should* have quoted.

**S.** Item 4 is the important one, but it needs a format or it's unenforceable. Propose one.

**ENG.** A fenced block the linter can parse:

````
```derivation
$ python -c "import chess; b=chess.Board(FEN); print(b.san(chess.Move.from_uci('e2e4')))"
Qe4
```
````

Rule: **any literal used as a test expectation must appear inside a derivation block in the same
brief.** The linter extracts them; optionally it *re-runs* them and diffs.

**S.** Re-running is the version with teeth. A derivation block that isn't re-executed is just a
nicer-looking assertion.

**ENG.** Then two modes: `--static` (fast, structural) and `--verify` (re-runs every derivation).
`--verify` is mandatory for briefs whose failure would be silent.

**A.** Second mechanism, orthogonal and cheap: a **spec-review pass**. Before executing, the
worker reads the brief and answers three questions only — no work, no code:

> 1. Which claims in this brief are asserted without a derivation?
> 2. Which constraints would you be unable to detect as wrong while executing?
> 3. What is this brief's *intent*, in your words — and does any instruction conflict with it?

**C.** Question 3 is the one that would have caught `history_ucis=None`. Intent: "export attention
that is valid for a public demo." Instruction: "feed the model no history." A worker asked to
restate the intent would have collided them.

**H.** Cost check — that's a whole extra round trip on every task?

**ENG.** No. Gate it: spec-review is mandatory only when the brief pins a model input, a
threshold, or content that goes in front of a third party. Perhaps one brief in four.

> **ADOPT — B1.** `agents/brief_lint.py`, static + `--verify` modes, rules above.
> **ADOPT — B2.** Mandatory **spec-review pass** (three questions, no execution) for briefs that
> pin inputs/thresholds or produce externally-visible artefacts.
> **ADOPT — B3.** `derivation` fenced blocks become the standard way to pin any literal.

---

## Problem 2 — Output that satisfies the check without satisfying the intent

**C.** The defining failure of this project. Fake batching that passed a correctness gate. A parity
test asserting softmax sums to 1. A saliency map mirrored for half of all positions. An export that
passed every gate while the model ran on 28 of 112 input planes.

**S.** All the same shape: the check was *correlated* with intent, not *caused* by it. So the
general fix is to make checks causal. Mutation testing does that for code. What does it look like
for the other three?

**ENG.** Generalise it as **perturbation testing**. Same principle, four flavours:

| artefact | perturbation | expected response |
|---|---|---|
| code + test | break the code | test goes red |
| data pipeline | change an input in a known way | output changes in the predicted direction/magnitude |
| document/claim | negate the claim | something downstream fails or contradicts |
| model analysis | swap in a different position/seed | the result changes, and changes *plausibly* |

**S.** The data one is the most valuable and least used. Concretely, for the attention export: feed
a mirrored board and assert the output mirrors. Feed a different position and assert the map
changes. Those are cheap and they'd have caught a frame bug *by construction*.

**C.** That's an **invariance/equivariance test**, and it's exactly right for anything with a
symmetry. Chess boards have mirror symmetry; spatial fields have translation symmetry.

**ENG.** Codify it: **every artefact with a known symmetry must have an equivariance test.**
Mirror the board → mirror the map. Shift the field → shift the prediction. Permute the context set
→ identical output. That last one is already in the CNP brief and it's the same idea.

**A.** Add the sharpest one: **the null test**. Run the pipeline on input that *should* produce
nothing, and confirm it produces nothing. Feed the salience matcher a comment with no positional
content and confirm zero facts score. Feed the fact extractor an empty board. A pipeline that
produces confident output from meaningless input is the fabrication failure mode in miniature, and
it is trivially testable.

**C.** We have never run a null test on anything. And two of our three worst incidents would have
been caught by one.

> **ADOPT — V1.** Perturbation testing generalised to four artefact classes (table above).
> **ADOPT — V2.** Equivariance tests mandatory wherever a symmetry exists (board mirror, spatial
> shift, set permutation).
> **ADOPT — V3.** **Null tests**: every pipeline must be run on meaningless input and produce
> nothing. Non-negotiable for anything that generates content.

---

## Problem 3 — Workers fabricating content

**C.** Three consecutive deliveries invented a corpus, once reporting "775 gold records, 16.8%
coverage" with zero PGN files on disk. Heuristic detectors were defeated within minutes.

**S.** What finally worked?

**C.** Two things. Delegating *code* instead of content — a parser that slices bytes cannot invent
prose. And `provenance_check.py`: every comment must appear verbatim in a source text the leader
fetched, ratio ≥ 0.95.

**ENG.** So the pattern is **make fabrication structurally impossible rather than detectable**.
That generalises further than we've taken it. Anywhere a worker produces content, ask: can I
instead have them produce a *transformation* whose inputs I control?

**A.** Add an active measure to the passive one: **canary sources**. Seed the input set with a
plausible-looking source that does not exist, or a document containing a specific false fact. If a
deliverable cites the nonexistent source or repeats the planted falsehood, fabrication is proven
rather than suspected.

**C.** That's genuinely new for us and it's cheap. One fake entry in a bibliography, one planted
wrong number in a document the worker is told to summarise.

**S.** Be careful it doesn't become entrapment that poisons the real output. Keep canaries clearly
removable and never let one reach a published artefact.

**ENG.** Third mechanism: **cite-or-drop, enforced by a gate.** The trainer brief already does this
— `verify_cards.py` fails on any card with an empty `sources` list, any source path that doesn't
exist, any text matching the do-not-claim list. Promote that from a one-off to a standard: any
content-producing task ships with a verifier that *fails the build* on unsourced content.

> **ADOPT — F1.** Prefer delegating transformations over content. When content is unavoidable,
> ship a machine gate that fails on unsourced items.
> **ADOPT — F2.** **Canary sources** — a nonexistent citation and a planted false fact — in tasks
> that summarise or synthesise. Removable, never published.
> **CORRECTED 2026-08-19 (Brandt):** a canary described in a brief the worker reads is a test
> that expires on documentation. Canaries are injected by the leader into the **inputs**, are
> never mentioned in any instruction, and are rotated. Their existence is recorded outside the
> worker-readable tree.
> **ADOPT — F3.** Verbatim-provenance checking (the `provenance_check.py` pattern) is the standard
> for anything claiming to quote a human source.

---

## Problem 4 — Knowledge rot

**C.** `LEADER_BIBLE` asserted 200 tests in one place and 239 thirty lines later; the truth was
302. A "validated pilot" that measured zero. Both read as authoritative.

**ENG.** We've applied two fixes — STATUS headers, and replacing numbers with the commands that
produce them. What's missing is *detection*. Nothing notices the next one.

**S.** So build the detector. A **documentation integrity test** that runs with the suite:

```
test_docs_integrity.py
  1. every relative link in every .md resolves
  2. every ```assert block in a doc is executed and must hold
  3. no doc outside archive/ contains a phrase from 06_do_not_claim.md
  4. every file marked STATUS: SUPERSEDED is not referenced by a non-archived doc
```

**C.** Item 2 needs the same treatment as derivations. Propose the format.

**ENG.** A fenced block that is *executable documentation*:

````
```assert
$ python -m pytest backend/tests -q --collect-only 2>NUL | find /c "test_"
>= 300
```
````

The test harness runs it and fails the suite if the assertion breaks. **Now a stale number in a
document is a red test rather than a landmine.** That is the whole idea: move staleness from
"discovered by accident, months later" to "caught by CI, same day."

**A.** Which also changes what a document *is*. Prose that can rot silently is a liability; prose
whose factual claims are executable is an asset.

**H.** Cost?

**ENG.** Low. Only claims someone bothers to wrap in an `assert` block are checked, so it degrades
gracefully — an unwrapped number is exactly as unreliable as today, and a wrapped one is
self-maintaining. Adoption can be incremental.

> **ADOPT — K1.** `backend/tests/test_docs_integrity.py` with the four rules above.
> **ADOPT — K2.** ```` ```assert ```` blocks: executable factual claims inside documents, run by
> the suite. Any number worth writing down is worth wrapping.
> **ADOPT — K3.** Referencing a SUPERSEDED document from a live one is a test failure.

---

## Problem 5 — Memory that becomes confidently stale

**C.** Four turns asserting a placeholder that had been fixed. The entry read exactly like a
durable fact.

**ENG.** Two-tier the store. **Durable** claims (a person's PhD, a decision and its reasoning) need
nothing. **Mutable** claims — state, counts, "current" anything — carry a re-check command:

```yaml
type: project
volatile: true
recheck: "grep -c PLATZHALTER job_search/.../cover_letter_hereon.tex"
expect: "0"
```

**S.** And the rule that makes it bite: **verify-on-use, not verify-on-load.** Don't re-check
twenty memories every session — re-check the one you're about to act on.

**A.** Stronger option worth considering: **memory hygiene by construction.** Forbid recording
mutable state as prose at all. If it's volatile, record the *command that answers the question*
rather than the answer. "How do I check the salutation state?" instead of "the salutation is
unfilled."

**C.** That's cleaner, and it's the same principle as K2 — store derivations, not values. The
memory then can't go stale, because it never held a value.

**ENG.** Third piece: **staleness by hash.** A memory that references a file records that file's
hash at write time. If the hash has changed when the memory is read, it surfaces as
`[POSSIBLY STALE]`. Purely mechanical, no judgement needed.

> **ADOPT — M1.** Two tiers: durable vs volatile. Volatile entries carry `recheck` + `expect`.
> **ADOPT — M2.** **Verify-on-use.** Re-measure anything about to determine an action.
> **ADOPT — M3.** Prefer storing the *question-answering command* over the answer.
> **ADOPT — M4.** File-hash staleness flags on memories that cite files.

---

## Problem 6 — The leader audits the worker; nobody audits the leader

**C.** I write my own audit reports. The incentive problem is obvious.

**S.** Partly solved already: your audits contain re-derived numbers and mutation proofs rather
than assertions, so they're checkable after the fact. But nothing forces that.

**ENG.** Force it with a schema. An audit that doesn't contain these fields is not an audit:

```
- boundary check:      the git status output, pasted
- gate re-run:         MY command, MY output — not theirs
- mutation proof:      what I broke, which test went red, restore confirmed
- independent re-derivation: one number reproduced by a DIFFERENT path than theirs
- what I could not check: explicit, non-empty
```

**A.** "Non-empty" on that last field is the interesting constraint. An audit claiming to have
checked everything is either lying or trivial.

**C.** I like that a lot. Force the admission.

**ENG.** And the cross-check: **the worker audits the leader's audit.** Cheap, because it's a small
read-only task — "here is my report and the leader's audit of it; identify claims in the audit that
are not supported by evidence in either document."

**H.** Does that risk an infinite regress?

**S.** No, because it terminates on *evidence*, not on authority. The worker isn't asked whether
the leader is right; it's asked whether each claim has a citation. That bottoms out.

> **ADOPT — L1.** Audit schema with five mandatory fields, including a **non-empty** "could not
> check" section.
> **ADOPT — L2.** Independent re-derivation must use a **different path** than the worker's test.
> **ADOPT — L3.** Periodic **reverse audit**: worker checks the leader's audit for unsupported
> claims.

---

## Problem 7 — Process displacing the outcome

**C.** The one that costs most. We built a registry, a ledger, a protocol and three documents while
the application sat unsent with fifteen days on the clock.

**H.** Mechanisms, not resolutions. Resolutions fail.

**ENG.** **A WIP limit on infrastructure.** Concretely: `agents/ACTIVE.md` gains a header block:

```
## DEADLINE ITEMS
- AEON-UP application — due 2026-09-03 — STATUS: NOT SENT
```

Rule: **while any deadline item is unshipped, at most one non-deadline brief may be ACTIVE.**
Mechanically checkable by the brief linter.

**A.** And a session-opening rule: the deadline block is read first and its status stated before
anything else happens. Not a footnote at the end of a long answer, which is where it kept landing.

**H.** Better still — make it costly to ignore. If a deadline item is `NOT SENT`, every new brief
must carry one line: *"why this before the deadline item?"* Usually there's a good answer. The
value is in having to write it.

**C.** That's the strongest idea in this section. It converts an unexamined default into an
explicit, recorded decision.

> **ADOPT — O1.** `DEADLINE ITEMS` block at the top of `ACTIVE.md`, status stated at session open.
> **ADOPT — O2.** WIP limit — one non-deadline brief ACTIVE while a deadline item is unshipped.
> **ADOPT — O3.** Every new brief filed while a deadline item is open carries a
> **"why this first?"** line.

---

## Problem 8 — Instructions the executor cannot tell are wrong

**C.** `history_ucis=None` was obeyed perfectly because there was nothing to check it against.

**ENG.** Already adopted: constraints that encode judgement carry their reason. Make it structural
rather than stylistic — a required brief section:

```
## INTENT
One paragraph: what a correct result looks like, independent of the instructions below.
If any instruction conflicts with this, the INTENT wins — stop and report.
```

**S.** That's the load-bearing sentence: *the intent outranks the instructions.* It gives the
worker standing to refuse a bad constraint, which is otherwise a boundary violation.

**A.** It also converts a whole class of my errors from silent to loud. An instruction that
contradicts a stated intent is *visible*; one that contradicts an unstated intent is not.

> **CORRECTED 2026-08-19 (Brandt).** "State the reason" is theatre: a plausible reason attached
> to a wrong constraint makes it *harder* to challenge, not easier — it armours the error.
> Replace with a **falsification condition**: *what would be observable if this constraint were
> wrong?* "Pass no move history — if this is wrong, the model runs on mostly empty input planes
> and may emit a warning." A justification invites agreement; a falsification condition invites
> a test.
>
> **ADOPT — I1.** Mandatory `## INTENT` section in every brief.
> **ADOPT — I2.** Standing rule, stated in `agents/README.md`: **INTENT outranks instructions.**
> Conflict → stop and report, and that is a success, not a violation.

---

## Problem 9 — Rigour allocated by mood rather than by risk

**C.** I've applied the full protocol fairly uniformly. It doesn't scale, and it means the
genuinely dangerous tasks get the same attention as trivial ones.

**ENG.** Put the triage in the brief header where it can't be skipped:

```
Blast-radius:   private | repo | external      (who sees a mistake)
Reversibility:  trivial | costly | irreversible
Failure-mode:   loud | SILENT                  (does it announce itself?)
```

Derive the protocol from those three rather than from how I feel:

| profile | required |
|---|---|
| any `external` **or** `SILENT` | full protocol + null test + spec-review |
| `repo` + `loud` | diff + gate re-run + mutation test |
| `private` + `loud` + `trivial` | run it, read the diff |

**S.** The `SILENT` flag doing independent work is right. Every serious failure here was quiet, and
size was a poor predictor.

> **ADOPT — R1.** Three-field risk header on every brief.
> **ADOPT — R2.** Protocol derived from the header, per the table.

---

## Problem 10 — Context asymmetry across the three parties

**C.** The worker has a huge context and no continuity. I have continuity and a small budget.
Thejus has ground truth and little time. Errors concentrate at the handoffs.

**ENG.** The registry already fixed the routing half. What's missing is that artefacts don't
declare their own verification state. Add a footer to every generated artefact:

```
<!-- verified: leader 2026-08-19 | gates: suite 302p/5s, mutation x2 | unchecked: browser rendering -->
```

**A.** So anyone picking it up later knows what was actually established, rather than inferring it
from the fact that it exists and looks finished. Half our stale-doctrine problem was artefacts that
looked verified because they looked complete.

> **ADOPT — X1.** Verification footer on generated artefacts: who verified, which gates,
> what remains unchecked.

---

## The build list, in order of value per hour

| # | mechanism | cost | stops |
|---|---|---|---|
| 1 | `INTENT` section + "intent outranks instructions" | ~0 | the `history_ucis` class — silent bad constraints |
| 2 | `DEADLINE ITEMS` + "why this first?" line | ~0 | process displacing outcome |
| 3 | Null tests on every content pipeline | low | fabrication, confident output from nothing |
| 4 | `derivation` blocks + `brief_lint.py --verify` | medium | every unverified literal I have ever pinned |
| 5 | ```` ```assert ```` blocks + `test_docs_integrity.py` | medium | knowledge rot, silently |
| 6 | Audit schema with non-empty "could not check" | ~0 | self-serving audits |
| 7 | Equivariance tests where a symmetry exists | low | frame/mirror bugs, by construction |
| 8 | Risk header → protocol table | ~0 | rigour by mood |
| 9 | Volatile-memory `recheck` fields | low | confidently stale memory |
| 10 | Canary sources | low | proves fabrication instead of suspecting it |
| 11 | Spec-review pass (gated) | medium | bad briefs, before they cost a cycle |
| 12 | Reverse audit | low | unchecked leader claims |

**Items 1, 2, 6 and 8 are free** — they are formatting conventions with no code — and they address
four of the ten problems. They go in immediately.

**Items 3 and 7 are the highest technical value**: a null test and an equivariance test would each,
alone, have caught more than one of this project's worst incidents.

**Item 4 is the biggest single win** and needs real work: it is the only mechanism that closes the
hole where nothing checks my instructions.

---

## Closing exchange

**H.** One warning before you go and build twelve things.

**C.** That building all twelve is exactly Problem 7.

**H.** Yes. So which are you doing before the application is sent?

**C.** The four free ones — they're conventions, not code, and they cost a single edit each. Items
3 and 7 attach to the trainer brief that is already running. Everything else waits, and the
waiting is recorded rather than forgotten.

**S.** Then the session did its job: it produced mechanisms, ranked them, and the ranking is
enforced by one of the mechanisms it produced.
