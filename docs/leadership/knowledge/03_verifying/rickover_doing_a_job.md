# Rickover — "unless someone can be identified, no one has been responsible"

**Admiral Hyman G. Rickover, head of US Naval Reactors 1949–1982. Principles set out in his paper "Doing a Job" (1981).**

## The situation

Rickover built and ran the nuclear navy for over three decades. The programme's safety record is the
relevant fact: no reactor accident, across thousands of reactor-years, in a technology where a single
failure would have ended the programme and possibly the industry.

He was, by wide agreement, extremely difficult to work for.

## What was done

Several practices, all in tension with normal management instinct.

**Personal technical competence.** Rickover insisted the person in charge understand the technology
in detail, and he interviewed every officer entering the programme himself — thousands of them. His
position was that a manager who cannot evaluate the technical work cannot supervise it and is
reduced to trusting reports.

**Named individual responsibility.** From the paper:

> "Unless the individual truly responsible can be identified when something goes wrong, no one has
> really been responsible."

Committees, in his view, existed to diffuse accountability. He wanted a name attached to every
decision.

**Direct access to the deck plates.** He read technical correspondence himself, and cultivated
channels that bypassed the chain of command, so that a junior engineer's concern could reach him
without being filtered by everyone whose work it criticised.

**No shortcuts on the physical work.** The famous instruction that engineers must not accept
"approximately right" — a pipe is either to specification or it is not.

## Why it worked

Because he closed the gap between the report and the thing. Most large technical organisations
manage a *representation* of the work: schedules, status decks, summaries. Rickover treated that
representation as untrustworthy by default and built mechanisms to reach the object directly.

The cost was real. He was abrasive, made enemies, and the culture depended heavily on him
personally.

## The principle

**Verification requires technical competence and direct contact with the object. A leader who can
only read summaries is trusting, not supervising — and every decision needs a name on it.**

## For us

`LEADER_GROUNDING.md` §3c names the root error in almost the same words: *I substitute my
representation of a thing for the thing.* Intention for diff, fluency for fact, the role of auditor
for the act of auditing.

Where we do this well:

- Every worker number gets re-derived. Gemini reported A3 = 0.4870; I re-fitted it from the `.npz`
  and got 0.4884. It reported A4 = 0.5270; I got 0.5298. The point is not the agreement — it is that
  agreement was *established* rather than assumed.
- I read `diagnose_on_kaggle.py:434` rather than trusting a report that quoted it, and found that a
  fix described in the past tense had never been applied.
- `metrics.py` is leader-owned by explicit decision, because it is the mathematical source of truth.

Where Rickover would object:

- **"Doing a job" is not the same as reviewing one.** He would say I cannot audit a training run I
  have never been able to execute. The mixed-precision path in `phi_net` has been reviewed by two
  parties and run by neither. That is exactly the gap he built the programme to close, and I have no
  way to close it from this machine.
- **Names.** Our briefs are addressed to "the worker". When a delivery is wrong, the accountable
  party is always me — which is correct, and also means the mechanism has never been tested.
