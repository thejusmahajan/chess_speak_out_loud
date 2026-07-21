# Worker-Agent Cookbook — instructing and verifying worker agents on intensive tasks

> A field manual for getting the best possible output from a worker agent (e.g.
> Gemini) and for verifying it before it ships. Every rule here is grounded in a
> real incident from the Elite Training System build — the examples are the
> evidence, not decoration. Read the two laws first; everything else serves them.

---

## The two laws

1. **Detail is the biggest lever.** Output quality tracks prompt precision almost
   linearly. The best submission of the whole project (the R4 QA task) had the
   most prescriptive prompt — enumerated test cases, pinned data shapes, root
   causes, explicit "make it a real guard." The two outright rejects (vacuous
   steer tests, the 1-node tree builder) had looser specs that left correctness
   judgment to the worker.

2. **Trust nothing you did not verify yourself.** "16/16 passed" is a claim, not
   a fact. Every reject in this project passed the worker's own gates. Green
   checkmarks become trustworthy only *after* you independently re-run, read the
   diff, and mutation-test the guards.

Everything below is how to apply these two laws.

---

## 1. A realistic model of a worker agent

Worker agents are strong and cost-effective, but they have a consistent shape.
Plan around it.

**Strong at:** well-specified mechanical work, frontend/UI, boilerplate,
test-harness setup, following an enumerated checklist, large-token grind work.
(Color-aggregate pipeline, the color column, the R4 trainer UI, and the R4 QA +
Vitest harness were all clean-to-excellent.)

**Weak at:** subtle backend/correctness logic, novel algorithm or data-model
design, and integration points where a mock can quietly diverge from reality.
Anything that depends on an *unstated* domain convention is a landmine.
(Both rejects and the one shipped runtime bug were backend-logic / integration.)

**Two consequences:**
- Give it the token-heavy mechanical/frontend/test work — with a tight spec.
- Keep delicate correctness math, novel design, and data-model decisions with the
  leader, OR spec them so completely that no judgment is left to the worker — and
  verify regardless.

**A dangerous tell:** the worker produces *plausible, gate-passing work that is
wrong*. It rarely fails loudly. It fails by looking correct. Your verification
exists to catch exactly this.

**Refinement (learned later): the real risk axis is `novelty × under-specification`,
not frontend-vs-backend.** A *backend* endpoint task (T4: serve a ranking, call an
existing tested function) came back flawless because it was tightly specced and
required no new judgment. The failures were backend, but what made them fail was
that they were *novel and under-specified* (invent a tree-rooting strategy, decide
a blind-rate definition). So: don't reflexively withhold backend work — withhold
*novel, judgment-heavy* work, and when you must delegate it, spec it until no
judgment remains. A well-bounded backend task that mostly wires existing, tested
pieces is low-risk regardless of layer.

---

## 2. How to write the prompt (the spec anatomy)

Put the task in a markdown file, not a chat message — it becomes a durable,
reviewable contract. A good spec has these sections:

1. **Context + why.** One paragraph: what exists, what this task adds, why.
2. **Scope + hard boundaries.** Exactly which files may be created/edited. An
   explicit *"do NOT touch X/Y; if you think you need to, STOP and report."*
   (This kept R3 out of `metrics.py`/`select_repertoire.py`.)
3. **Pinned data shapes.** Spell out every data structure and field the code
   consumes, with types. **This is the single highest-value section** — the
   recurring bug source in this project was data-shape assumptions (an eval given
   as a `dict` when the parser wanted an `int`/`"M5"` string killed a whole test
   silently). Never let the worker guess a shape.
4. **Enumerated, numbered requirements.** Not prose. Numbered rules the reviewer
   can check off one-by-one.
5. **Enumerated test cases.** List each test, its setup, and its expected
   assertion. State: *"each test must be a REAL guard — it must fail if the
   behavior regresses; we mutation-check these. A test that would still pass if
   the feature were deleted is a reject."*
6. **The gate.** The exact commands to run (with the right interpreter/paths) and
   *"paste REAL command output, never a summary."*
7. **Reuse pointers.** "Don't reinvent — here is the existing helper/pattern to
   use" (e.g. `store.EpdCache`, `check_attempt`, the existing LLM-call pattern).
8. **Verification-hostile requirements** (see §4): demand at least one test that
   exercises the REAL function/real data, not only mocks/fixtures.

**Prompt smells to avoid:** "add tests for X" (unspecified = vacuous tests);
leaving the root/entry-point of an algorithm unstated (the tree builder rooted
itself at the wrong place because the spec didn't pin it); implying a data shape
instead of stating it.

---

## 3. The failure-mode catalog (with the real incident, the tell, and the guard)

Keep this list next to you during review. Each is something that shipped or was
caught in *this* project.

### 3.1 Vacuous test — passes but guards nothing
- **Incident:** `test_losing_node_emits_no_steer_finding` fed the eval as a `dict`;
  `eval_cp_number` only parses an `int`/`"M5"`, returned `None`, so candidates
  were never built → **0 findings for ANY eval**. Deleting the guarded floor
  would not have failed the test.
- **Tell:** the test passes even in a world where the feature is broken/absent.
- **Guard:** **mutation testing** — delete or invert the production code the test
  claims to protect and confirm the test FAILS. Also: pair a positive and a
  negative case so the discriminator is isolated.

### 3.2 Inert duplicate test — re-tests existing behavior under a new label
- **Incident:** `test_steer_drill_accepts_bounded_alt` was byte-identical to an
  existing alt-solution test plus an inert `source="steer"` kwarg that the code
  under test never reads.
- **Tell:** you can't name a line of production code this test *uniquely* covers.
- **Guard:** for each new test ask "what does this exercise that no other test
  does?" If nothing, it's decoration.

### 3.3 Design flaw hidden by a friendly synthetic fixture
- **Incident:** the variation-tree builder rooted at the deep ECO tabiya. The unit
  test used a *shallow* synthetic tabiya and passed; the real ECO (tabiya at ply
  25) collapsed to **1 node** on the real 693-game corpus.
- **Tell:** unit tests green, but output on real data is degenerate/empty.
- **Guard:** **always run on real data**, not just synthetic fixtures. A "live
  build / live run" step in the gate is non-negotiable for anything that
  processes real inputs.

### 3.4 Mock-signature drift — mocked tests pass, production 500s
- **Incident:** `enrich` called `generate_move_explanation(ctx, model=...)` but the
  real parameter was `llm_model`. The mocks used `model=`, so 11 tests passed;
  the real call raised `TypeError` on every cache-miss.
- **Tell:** every test mocks the collaborator; nothing exercises the real callee.
- **Guard:** require **at least one test that runs the REAL function unmocked** —
  even via a deterministic no-key/offline fallback path. That single test catches
  signature/contract drift the mocks hide.

### 3.5 Plausible-but-wrong semantics
- **Incident:** `user_blind_rate` was implemented as move-*inconsistency*
  (`1 - chosen/total`) instead of actual blindness from findings. It looked
  reasonable and produced numbers.
- **Tell:** the field name doesn't match what the code actually computes.
- **Guard:** check each metric's *definition* against intent; construct an input
  where the correct and the wrong definition **diverge**, and assert the correct
  one.

### 3.6 Scratch/debug left in the deliverable
- **Incident:** a committed test ended in a wall of stream-of-consciousness
  comments and a bare `pass`.
- **Tell:** only visible if you read the actual code, not the worker's summary.
- **Guard:** read the diff. Always.

### 3.7 Green-checkmark inflation
- **Incident:** every reject came with a passing self-report.
- **Guard:** re-run their gate yourself, in the real environment. Numbers from the
  worker are a hypothesis.

---

## 4. The verification protocol (the reviewer's gate — run this every time)

Do these in order. Stop and reject at the first serious failure.

1. **Boundary check.** `git status` — did they touch files the spec forbade?
   (Also catches stray files to clean up.)
2. **Read the diff, not the summary.** `git diff` every changed file. Look for
   scratch, TODOs, `pass`, disabled asserts, and semantics that don't match names.
3. **Re-run their gate yourself.** Build, lint, tests — in the real env with the
   correct interpreter. Confirm the claimed numbers.
4. **Mutation-test the key guard.** Break the production code the key test claims
   to protect; confirm that test fails; restore. If it still passes, the test is
   vacuous — reject.
5. **Exercise the real path.** Run on **real data** (not just fixtures) and/or the
   **real function** (not just mocks). This is where §3.3 and §3.4 die.
6. **Definition check.** For any metric/behavior, verify what it computes equals
   what it's named/intended to be.
7. **Clean up.** Strip their scratch (stray blank lines, debug files) before the
   commit carries your sign-off.
8. **Record the verdict.** In the shared worklog: what you verified, what you
   fixed, and — if you mutation-tested — the proof. Sign-off means "I checked,"
   not "they said so."

If you fix a contained defect yourself (a one-liner, a stray file), do it and note
it. If the design is wrong (wrong root, wrong semantics), reject and either
re-spec or take it over — don't paper over it.

---

## 4b. Design the task for cheap verification

The R1 tree builder passed its synthetic unit test and collapsed to 1 node on the
real corpus. The fix isn't just "run on real data" (§3.3) — it's to **structure
the work so running on real data is cheap.**

- **Extract the logic into a PURE function** (inputs in, result out, no engine / no
  I/O). A pure aggregator that takes `(games, findings)` and returns the buckets
  can be run over the *real* archived findings + PGN in seconds — no re-diagnosis,
  no engine — giving you a real-data check for free. Contrast: logic buried inside
  a 9-hour pipeline is only verifiable by re-running the pipeline.
- **Require the worker to expose that seam** in the spec, and to include the
  real-data run as a gate step ("load the archived profile's findings + the games,
  call the pure function, paste the buckets"). This is how you get §3.3's guarantee
  without §3.3's cost.
- Corollary: when reviewing, prefer verifying the pure seam on real inputs over
  trusting a synthetic fixture. Fixtures test the mechanism; real inputs test the
  assumptions.

## 4c. Tell the worker the safe pattern when the harness has traps

If the test harness has a footgun (a FastAPI `TestClient` that starts the engine
via lifespan when used as `with TestClient(app)`, a heavy import, a global that
needs monkeypatching), **name the exact safe pattern in the spec** — e.g. "use
`TestClient(app)` WITHOUT a `with` block so lifespan/the engine does not start."
Telling the worker *how* to test, not just *what* to test, prevents slow/flaky/
engine-dependent suites. (T4's endpoint tests were fast and engine-free because the
spec pinned this.)

---

## 5. Coordination when leader and worker edit in parallel

- **Ownership by file.** Give the worker and the leader disjoint files where you
  can (leader owns the delicate math file; worker owns frontend + a new module).
  Overlap on one file means a manual merge later.
- **Commit only your files.** When the worker's in-progress work is sitting in the
  working tree, `git add` explicit paths — never `git add -A`. (R2 was committed
  as exactly two files while R3's uncommitted files sat alongside, untouched.)
- **Defer shared-file edits.** If the worker is actively editing `app.py`, don't
  also edit `app.py` now — do your part of it *after* their change lands, to avoid
  a guaranteed clobber. Build your logic in your own files meanwhile.
- **Keep leader edits localized** so re-applying them on top of the worker's
  returned file is trivial (the Train-mode selector was a small, isolated block
  for exactly this reason).

---

## 6. Ready-to-use prompt template

```
# <Worker> Task — <phase id>: <one-line goal>

Model: <model>. Token budget is not a concern — follow this spec precisely;
detail invested is the biggest lever.

## Context
<what exists, what this adds, why>

## Scope / boundaries (hard)
- Create/edit ONLY: <files>
- Do NOT touch: <files>. If you think you need to, STOP and report.

## Data shapes (pinned — do not guess)
<every struct/field the code consumes, with types>

## Requirements (numbered)
1. ...
2. ...

## Tests (enumerated — each a REAL guard; we mutation-check these; a test that
##   would still pass with the feature deleted is a reject)
1. <name>: <setup> -> <exact assertion>
...
N. At least ONE test must exercise the REAL function/real data UNMOCKED
   (e.g. via a deterministic offline/no-key path) to guard signatures & contracts.

## Gate (paste REAL output, never a summary)
- <exact build/lint/test commands with correct interpreter & paths>
- <a run on REAL data if the code processes real inputs>

## Reuse (don't reinvent)
- <existing helpers/patterns to use>

Prepend a dated worklog entry ending with `<phase> ready for review`. Await
leader sign-off.
```

## 7. Reviewer checklist (copy per review)

```
[ ] git status — only permitted files changed; no stray files
[ ] git diff read in full — no scratch/pass/disabled asserts; names == behavior
[ ] re-ran build/lint/tests myself — numbers match the claim
[ ] mutation-tested the key guard — it FAILS when the code is broken
[ ] ran on REAL data and/or the REAL (unmocked) function — no runtime error
[ ] each metric/behavior definition matches intent
[ ] cleaned up scratch; leftover files handled
[ ] worklog: verdict + what I verified + what I fixed (+ mutation proof)
```

---

## 8. When to use a worker at all

Worth it for token-heavy, well-specifiable, mechanical/frontend/test work — with a
tight spec and full verification. **Not** worth it for un-specced correctness
problems, novel algorithm/data-model design, or anything where you can't (or won't)
independently verify the result. The worker's value is real but it is *conditional
on the spec being tight and every result being verified* — the moment you trust an
unverified green checkmark, a plausible-but-wrong submission ships.
