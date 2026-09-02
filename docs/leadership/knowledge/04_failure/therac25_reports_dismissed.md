# Therac-25 — the reports that were explained away

**Atomic Energy of Canada Limited radiation therapy machine, accidents 1985–1987; six known massive overdoses, at least three deaths. Definitive analysis: Nancy Leveson and Clark Turner, *IEEE Computer*, 1993.**

## The situation

The Therac-25 delivered radiation therapy in two modes: a low-energy electron beam applied directly,
and a high-energy beam that required a thick tungsten target to be rotated into the path to attenuate
it. Firing the high-energy beam **without** the target in place delivers an enormous overdose.

Earlier models had **hardware interlocks** that made this physically impossible. The Therac-25
removed them and relied on software.

## What happened

A race condition in the operator-interface code meant that if a technician typed the treatment
parameters quickly and used the edit keys within a narrow window, the machine's internal state could
disagree with the displayed state and the beam could fire in high-energy mode with the target
retracted. Fast, experienced operators were the ones who triggered it.

The machine displayed "MALFUNCTION 54" — an undocumented code — and appeared to have delivered no
dose, so operators sometimes repeated the treatment.

**The response to the reports is the leadership failure.** Hospitals reported injuries. AECL
investigated and could not reproduce the fault, and reported that an overdose was not possible. A
lawsuit was settled. Machines stayed in service. It took a hospital physicist reproducing the bug
himself — after an accident at his own site — to establish the mechanism.

## Why it failed

**Inability to reproduce was treated as evidence of absence.** The bug depended on operator typing
speed; it could not be reproduced by an investigator typing carefully. "We could not make it happen"
became "it cannot happen."

**Software was assumed reliable in a way hardware never was.** Removing the physical interlock was a
decision to trust code that had never been analysed to the standard the interlock represented.

**There was no channel through which field reports could stop the product.** Each report was handled
as a support incident.

## The principle

**A defect you cannot reproduce is not a defect that does not exist — especially when the reporter
was there and you were not.** And: never remove a physical guarantee and replace it with a claim.

## For us

**The reproduce-it-yourself rule.** Thejus is the ground-truth oracle and his reports have repeatedly
been right against my analysis: *"that's not a sacrifice"*, *"the bar is stuck"*, and the comment
sitting in `trainer/state/comments.jsonl` for ten hours saying *"I don't see the question here!"* —
which was a correct bug report from someone looking at the running app while I was reading the code.
`CLAUDE.md` now mandates reading that queue at session start, and it exists because a leader
committed six of his comments without reading one.

The Therac lesson sharpens it: when the person who was there says something is wrong and I cannot
reproduce it, **the default hypothesis is that my reproduction is wrong**, not that they are.

**The interlock-versus-claim rule** is the harder one, and it bites now.

- `steer_candidates()` is a real interlock: LC0's evaluation floors mean a blundering move cannot be
  recommended regardless of what Φ says. Φ re-ranks only what has already been declared sound. That
  guarantee is structural.
- The screen-then-search proposal would have **replaced that structure with a claim** — that pruning
  on prior and static value costs nothing. The rule adopted (a screen may choose what is searched,
  never produce a reported number, miss rate measured first) keeps the interlock and makes the claim
  earn its way in.
- The mixed-precision path is currently a claim. Two reviews, zero executions.

**And the undocumented error code.** "MALFUNCTION 54" is the ancestor of every empty list served as
an answer. `build_sac_session()` returning `0` told the user nothing was wrong. A failure that
presents as a normal result is worse than a crash, which is why the rigour formula in
`LEADER_GROUNDING.md` §3b multiplies by SILENCE.
