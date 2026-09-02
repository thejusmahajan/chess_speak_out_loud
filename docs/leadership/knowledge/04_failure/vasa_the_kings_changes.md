# The Vasa — a ship built to a specification nobody could refuse

**Stockholm, 10 August 1628. The warship Vasa sank on her maiden voyage, roughly 1,300 metres from the quay, in light winds.**

## The situation

Vasa was built for Gustavus Adolphus during the Thirty Years' War. The king took a close personal
interest, was at war and impatient, and issued instructions from the field. Ship design at the time
was not calculated but carried in the master shipwright's experience and proportion rules.

## What happened

The requirements changed during construction, in the direction of more armament and a second gun
deck — a heavier, higher configuration than the hull had been laid down for. The master shipwright
who began the ship died partway through, and his successor completed a design he had not originated.
Ballast could not be increased enough to compensate without submerging the lower gun ports.

Before sailing, a **stability demonstration** was carried out: thirty men ran back and forth across
the deck to rock the ship. After a few runs the ship was heeling so badly the test was stopped for
fear of capsizing her at the quay. It was stopped — and the voyage proceeded anyway. The vice-admiral
present is recorded as wishing the king were home.

Vasa sailed, caught a gust, heeled, took water through her open gun ports and sank in minutes with
around thirty lives lost.

The inquiry found nobody guilty. The shipwrights had built to instruction; the instruction came from
the king.

## Why it failed

**Requirements churn from an authority who cannot be contradicted.** Each individual change was
plausible. Nobody held the integrating view of what the accumulated changes did to stability.

**The test was run and the result was discarded.** This is the sharpest detail in the whole case. It
was not that nobody knew; the demonstration produced an unambiguous negative result in front of
witnesses, and the schedule won.

**Accountability diffused upward until it evaporated.** When the specification comes from someone
unchallengeable, no one is responsible, which is Rickover's point in reverse.

## The principle

**A test whose failing result you will not act on is worse than no test** — it converts a real
warning into a completed ritual. And when requirements come from an authority who cannot be
questioned, someone must still hold the integrated consequence and say it out loud.

## For us

**The stopped test is the one to fear.** We have gates — F0, F1, F2, A1–A4 — and their entire value
is that we act on them. The record so far is good and I want it stated plainly so that any future
deviation is visible:

- **A4 fired at 0.6637** on the first dataset build. 301,116 rows were discarded and rebuilt to
  261,748. Nobody argued the threshold down.
- **The brief says it in terms:** *"a fired alarm is a stop, not a parameter"*, and *"if A3 ≥ 0.65,
  stop and report. Do not proceed and do not tune it away."*

The Vasa's thirty running men are what those sentences exist to prevent. The failure mode is not
ignoring a test; it is running one, watching it fail, and finding a reason.

**Requirements churn is a live risk here and the direction is unusual.** Thejus is both the
authority and the ground-truth oracle, which is a combination the Vasa lacked — his corrections have
been technically right, not merely authoritative. But the structural hazard remains: I have no
mechanism that says "these accumulated changes have made the plan incoherent."

Concretely, the configuration-steering plan has absorbed, in three days: the aim, a rebuild of the
dataset, a round table's seven agreements, three audit responses, and a leadership corpus. Each was
justified. **Nobody has asked whether the whole still floats**, and on this project that question has
a name — `CLAUDE.md` non-negotiable #6, *no new meta-process documents while a deadline item is
open*. The interview is still the open deadline item.

That is the integrating view, and saying it is the job.
