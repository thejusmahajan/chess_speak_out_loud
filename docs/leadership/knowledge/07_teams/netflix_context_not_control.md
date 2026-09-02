# "Context, not control"

**Netflix culture deck, published publicly by Reed Hastings and Patty McCord in 2009; expanded in *No Rules Rules* (2020).**

## The situation

The conventional way to make a large organisation reliable is process: approvals, rules,
standardised procedures. This works, and it has a cost — it optimises for preventing error at the
expense of speed and judgement, and it drives out the people who most dislike being managed.

Netflix's argument was that for creative and technical work, this trade is bad, and the alternative
is to hire people who do not need the process and then give them the *context* to decide well.

## What was done

**"Context, not control."** A manager's job is to supply strategy, objectives, role clarity,
transparency about the business, and the reasoning behind decisions — and then let the person
decide. If someone does the wrong thing, the first question is what context was missing.

**"Highly aligned, loosely coupled."** Alignment on strategy and goals is expensive and deliberate;
coordination on tactics is minimised. Teams should not need meetings to stay consistent, because
they share the objective.

**Judgement over policy.** The expenses policy famously reduces to "act in Netflix's best
interests".

**The honest counterpart.** The same deck contained the "keeper test" and generous severance for
people who were merely adequate. Freedom was paired with a low tolerance for underperformance, and
the model does not transplant if only the pleasant half is copied.

## The limits

It is a claim about a specific kind of work — high-judgement, non-safety-critical, expensive to
specify and cheap to correct. Nobody proposes running a nuclear reactor on context rather than
control; Rickover's programme is the opposite pole and is right in its domain. The skill is knowing
which regime you are in, and most organisations contain both.

## The principle

**Where errors are cheap and reversible, supply context and get out of the way. Where they are
irreversible or silent, supply control.** Applying either universally is the mistake.

## For us

This is the tension running through every brief we write, and the resolution is not "pick one".

**The briefs are heavy on control**, and correctly so: numbered steps, exact files, the command to
run at each checkpoint, the output to paste back. `CLAUDE.md` says why — *Gemini is dangerous in
exact proportion to how under-specified the task is*. In a regime where the failure mode is silent
(a dataset separable on mobility, a metric that measures the wrong thing), control is the right
setting.

**But the briefs also carry context, and that is what has made the good ones work.** Every one opens
with an INTENT paragraph that outranks the instructions, quotes Thejus's aim in his own words, and
names the trap in plain language with the reasoning attached — *the puzzle `fen` is one ply before
the tactic; here is the proof; if you find yourself pushing `moves[0]` to build a positive, you have
built the wrong dataset.* That is context, and it is why the worker can stop correctly rather than
following a rule off a cliff.

**Where insufficient context cost us directly:** the sacrifice-pruning proposal. A locally excellent
optimisation that contradicted the entire aim, produced by a reviewer who had the code and not the
purpose. Nobody had told it that low static value *is the signal*. That is a missing-context failure,
and by Netflix's rule the first question is what I failed to supply.

**Where control is non-negotiable here**, and no amount of context substitutes: the gates. F0, F1,
F2, A1–A4, `b1_verdict`. Those are irreversible-and-silent territory. *A fired alarm is a stop, not a
parameter* is a control statement, deliberately.
