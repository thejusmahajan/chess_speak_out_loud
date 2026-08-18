```
Brief-ID:     2026-08-19_salience-cnp-brainstorm
Written:      2026-08-19
Target repo:  chess_speak_out_loud (this one) — write only to agents/reports/
Route:        Antigravity (full workspace — you can and should read the files named below)
Type:         design/brainstorm
Status:       ACTIVE
Depends on:   none
```

# Brainstorm — is the CNP the right tool for our salience problem?

You are a research collaborator with **fresh eyes**. Your job is to BRAINSTORM and to
**CHALLENGE**, not to agree. The leader has formed a hypothesis and explicitly wants it
attacked by someone who did not build it. A well-argued disagreement is the most valuable
thing you can produce here. **Do not be agreeable.** If you only confirm, you have
produced nothing.

This is a **thinking** task. Write no production code. Your only output is one markdown
report (§ OUTPUT below).

---

## 0. Read these first (you have the workspace — actually open them)

| file | why |
|---|---|
| `PLAN_SALIENCE_CNP.md` | the hypothesis you are attacking, in full |
| `docs/SALIENCE_PROBLEM.md` | the problem statement, with worked examples and the four salience "shapes" |
| `docs/NORTH_STAR_decoding_lc0.md` | the project's aim and the "LLM is a translator, never a reasoner" constraint |
| `LEADER_BIBLE.md` §1, §4, §5, §6 | the vision, the decisions that must not be relitigated, and the failure catalog |
| `backend/training/relational_facts.py` | the fact extractor — what the machine can actually see |
| `backend/training/salience_matcher.py` | the prose→fact matcher, and `INFERENCE_PRIORS`, the hand-coded fallback |
| `backend/training/salience_dataset.py` | how the annotated corpus is built |

**Do not take the leader's numbers on trust — re-derive them.** Run the code yourself with
`C:\Users\Admin\miniconda3\envs\cszero\python.exe`. The leader claims: 288 records, 7 gold,
2,284 facts, **19** labelled salient (0.8%), and **0 of 35** on the gold tier. If your
measurement disagrees, **say so loudly and show your command** — that finding would be more
valuable than the rest of this brief combined.

---

## 1. The problem, so we share a definition

The extractor emits ~25 statements about a position. All are true. A strong annotator would
name only **1–3** as "the point"; the rest are true but incidental. Choosing that few is the
**salience problem**, and it is the bottleneck between "the machine sees true facts" and
"the machine understands the point".

The motto that governs everything: **a bad coach does more harm than no coach.** A confident
wrong explanation actively damages the student — they go away and train the wrong thing. So
precision matters far more than recall, and silence is an acceptable output.

`docs/SALIENCE_PROBLEM.md` documents four distinct **shapes** of salience — tactical,
positional/quiet, defensive, and prophylactic/move-order — and argues no single local rule
finds all four. Approaches already rejected there, with reasons: emit-everything; rank by
evaluation swing; tactics-only; and **hand-coding which fact kinds matter** (forbidden by
doctrine after the `had_tal` incident — see `LEADER_BIBLE.md` §5, "metric-mislabel family").

## 2. The measured state

The plan was to learn salience from grandmaster book annotations: the master's comment IS
the salience label. **Measured today, that pipeline yields almost nothing** — see the numbers
in §0 that you are re-deriving. Three mechanical causes are claimed in `PLAN_SALIENCE_CNP.md`
§1.3: book-parser sentence fragments; descriptive notation (`P - B 3`) versus an
algebraic-only square regex with a hard grounding gate; and a vocabulary gap (no bishop-pair
fact, which is Capablanca's headline concept). **Verify each of these three independently.**

## 3. The resource that does exist

`data/puzzles/puzzles.sqlite` — **5,527,851** puzzles with position, solution moves, rating
and **human-curated theme tags** (73 themes; roughly 35 are genuine "what is the point here"
statements, the rest metadata like `short`, `master`, `middlegame`). Verified: each row
carries its own solution line, so `relational_facts` runs on it **with no engine call**.
Obvious limitation: the themes are overwhelmingly tactical.

## 4. The hypothesis you are attacking

That a **Conditional Neural Process** is the right tool, because:

1. A position's facts are an unordered, variable-size **set** → a permutation-invariant mean
   aggregator is structurally correct; an order-dependent model would be wrong.
2. **The load-bearing claim:** GM annotations will always be scarce — there will never be
   100,000 Capablanca comments — so "train a ranker on GM annotations" is a dead plan. But a
   CNP does not *train on* the small set, it *conditions on* it. Twenty good annotated
   positions are useless as a training set and ideal as a **context set**. Scarcity becomes
   the design assumption rather than the blocker, and swapping the context set swaps whose
   taste the coach imitates.
3. A mean/σ output lets the coach **abstain** when unsure — the motto, in code.
4. Pretrain the representation on the millions of tactical puzzles; condition on the few good
   master annotations for the quiet and prophylactic shapes.

(If you are unfamiliar: a CNP encodes a set of observations by encoding each element and
**averaging**; it is trained across many tasks so that at test time a small labelled
"context set" adapts it instantly with no retraining; it outputs a mean and a standard
deviation; and it comes with calibration machinery — reliability curves, expected calibration
error, proper scoring rules — plus leave-one-out validation for tiny datasets.)

---

## 5. YOUR TASK — structure the report exactly like this

### PART 0 — VERIFICATION
The numbers you re-derived, with the exact commands and their real output. State plainly
whether each of the three claimed causes in §2 holds. Contradict the leader where warranted.

### PART 1 — ATTACK THE HYPOTHESIS
The strongest reasons the CNP framing may be wrong, oversold, or a poor fit. Be specific
about mechanism. Address at minimum:
- Is a "task" well-defined here for the purposes of conditioning? What *is* one task?
- The problem statement says salience is **LINKAGE** — 4 facts chaining into one idea. Does
  a mean-aggregating encoder destroy exactly that structure?
- Would a much simpler method match it? Say which, and be concrete.
- Would the predicted uncertainty be *meaningful*, or just noise dressed as confidence?
- Does pretraining on tactical puzzles poison the model toward tactics, given that the
  hardest shapes (quiet, prophylactic) are absent from that corpus?

### PART 2 — THE STRONGEST VERSION
If it survives, state the sharpest possible version. Be precise: what is one task, what is in
the context set, what does a single training example look like, what exactly is predicted,
and what is the loss?

### PART 3 — RIVAL APPROACHES
3–5 genuinely different attacks on the salience problem given these resources (millions of
theme-tagged puzzles, a handful of master annotations, a true-fact extractor, a strong engine
available at inference). For each: mechanism, data needed, main failure mode, and how it
handles all four salience shapes. **At least one must not be a neural network.** Rank them
against the CNP proposal and say which you would build first, and why.

### PART 4 — THE CHEAPEST KILLER EXPERIMENT
Doctrine: *the cheap thing that can invalidate the expensive thing runs first.* Design the
single cheapest experiment that reveals whether this direction works **before** anything
large is built. Give the exact measurement, the number that means **proceed**, and the number
that means **stop**. It must run in hours on a laptop CPU.

### PART 5 — WHAT THE LEADER MISSED
Hidden assumptions, problems with the evaluation plan, a resource in the repo being
underused, or a risk not named. Include anything you found while reading the code that
contradicts the documents.

---

## OUTPUT

Write **one file**: `agents/reports/2026-08-19_salience-cnp-brainstorm_REPORT.md`.
Create or modify nothing else.

Be specific, not generic. Do not restate this brief back. Where you are uncertain, say so
explicitly rather than inventing detail — an honest "I don't know" is worth more than a
confident guess, and inventing detail here is the failure mode that has cost this project
most. If you think a claim above is simply false, say so plainly and show why.
