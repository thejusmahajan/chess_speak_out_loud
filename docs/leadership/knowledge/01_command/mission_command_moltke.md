# Auftragstaktik — Moltke and the order that says why, not how

**Prussian/German army, roughly 1860–1888. Helmuth von Moltke the Elder as Chief of the General Staff.**

## The situation

Moltke commanded armies larger and more dispersed than any before them, moved by railway and
directed by telegraph. A courier could take a day to reach a corps. By the time an order arrived,
the situation that produced it had changed. Detailed central control was not merely inefficient —
it was arithmetically impossible.

## What was done

Orders were written to convey **intent** and the commander's reasoning, and to leave method to the
subordinate. The doctrine that grew from this is *Auftragstaktik*, mission-type tactics: state the
task and its purpose, allocate the resources, and hold the subordinate accountable for the outcome
rather than for compliance with a method.

Moltke's most quoted line — usually rendered "no plan survives contact with the enemy" — is a
compression of his actual claim, which is more careful: no plan of operations extends with any
certainty beyond the first encounter with the enemy's main body. The point is not that planning is
futile. It is that the plan's *purpose* must survive even when its steps do not, and only the
subordinate on the ground can improvise toward a purpose he understands.

He also warned against the opposite error. An order should contain everything the subordinate
cannot determine for himself, **and nothing else**. Over-specification is as much a failure as
under-specification, because it substitutes the distant commander's stale picture for the local
commander's fresh one.

## Why it worked

Because it matched authority to information. The person with the freshest, richest picture of the
local situation was given the freedom to act on it, and the person with the widest view supplied the
thing the local commander could not see: what all of this is *for*.

It failed wherever the intent was not genuinely transmitted. A subordinate who does not understand
the purpose cannot improvise toward it; he can only guess, and guessing looks exactly like
initiative until it goes wrong.

## The principle

**Specify the intent and the constraints; leave the method to whoever holds the freshest
information. Include everything the executor cannot work out alone, and nothing more.**

The corollary is uncomfortable for the commander: if the subordinate misunderstands the intent, the
intent was badly written. Blame is upward-flowing by construction.

## For us

The brief format in `agents/briefs/` opens with an INTENT block that says *intent outranks
instructions; if any instruction conflicts with this paragraph, the intent wins — stop and report*.
That is Auftragstaktik, and it was arrived at the hard way: `LEADER_GROUNDING.md` records that
Gemini is "dangerous in exact proportion to how under-specified the task is", and that the
under-specification is the leader's failure.

The tension we have not resolved is Moltke's second warning. Our briefs are long and heavily pinned
— numbered steps, exact files, the command to run at each checkpoint. That is right where the worker
cannot determine the answer itself (which file, which threshold, which trap). It is wrong wherever
it substitutes my stale picture for its fresh one. The `data.py` episode of 2026-09-02 is exactly
this: Gemini reached the nested-directory problem before I did, patched it, and my job was to
correct the *determinism* of its patch — not to have specified the patch in advance.
