# Columbia — the normalisation of deviance

**STS-107, lost on re-entry 1 February 2003. Concept from Diane Vaughan, *The Challenger Launch Decision* (1996); applied by the Columbia Accident Investigation Board (2003).**

## The situation

Foam shedding from the External Tank was not supposed to happen. It was outside specification. It
happened on most flights.

Because it happened repeatedly and no orbiter was lost, the event was reclassified over time —
first as an anomaly, then as a maintenance turnaround issue, then as effectively normal. By 2003 a
foam strike was, institutionally, not a safety-of-flight concern. On STS-107 a briefcase-sized piece
struck the left wing leading edge at several hundred miles per hour and breached the thermal
protection. The orbiter broke up on re-entry.

## What Vaughan named

Her analysis of Challenger produced the phrase **normalisation of deviance**: a signal that is
outside specification recurs without visible consequence, and the organisation's definition of
acceptable expands to include it. Nobody decides to accept a danger. Each individual step is
reasonable given the previous step. The standard drifts.

The CAIB found the same mechanism operating seventeen years later in the same organisation, and
concluded that the causes were as much organisational as technical — that NASA's culture had been "a
contributing cause" of both losses.

The other CAIB finding worth carrying: **engineers requesting imagery of the wing were turned down**,
and the requests never reached the level where they could be granted. The information existed inside
the organisation and did not travel.

## Why it happens

Because the feedback is asymmetric. Every flight that survives a deviation is evidence that the
deviation is survivable, and the one flight that does not is not available as evidence in advance.
The organisation is running an experiment whose only decisive result is a catastrophe.

## The principle

**Track the specification, not the outcome.** A recurring out-of-spec event that has not yet hurt
you is a fact about your luck, not about your margin. And an anomaly that has been reclassified
should be re-derived from first principles, not inherited.

## For us

Ours is not a safety-critical system, so the stakes are honest work rather than lives. The mechanism
is identical.

**The clearest instance is `sac_drill` returning `0`.** It returned an empty list. Nothing crashed.
Twenty-nine tests passed — against a synthetic profile in the new format, so nothing tested the
selector against the data on disk. The empty result was indistinguishable from a legitimate "no
findings", and it stayed that way for five weeks. That is deviance normalised by silence rather than
by decision.

**The second instance is subtler and is about tests.** `LEADER_BIBLE.md` §5 names the
vacuous-verification family: parity tests that assert tautologies, a "full suite" that ran a subset,
batch-of-1 self-references. A green suite that does not exercise the real path is exactly the
survived deviation — every run is evidence that everything is fine.

This is why mutation-checking is doctrine and not decoration. On 2026-09-02 I broke `encode.py:39`
deliberately to prove the colour-flip guard turns red, and broke `b1_verdict` to prove its test
bites. Without that, a passing suite is only evidence that nothing has crashed yet.

**Where deviance is currently normalising and I should say so:**

- `test_ts2_no_hang.py::test_ts2_orphan_future_cancellation_handled` is routinely deselected as a
  "load-sensitive flake". That was established once, correctly, by stashing to clean HEAD. It has
  been inherited ever since without re-derivation. It is exactly the shape of an anomaly that has
  been reclassified.
- `data/` is gitignored in full, so the dataset every result depends on exists on one laptop and is
  in no backup. That has been true for weeks and has not yet cost anything.
