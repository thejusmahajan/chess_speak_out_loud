# Ariane 5 Flight 501 — reused code, retired assumption

**4 June 1996. Maiden flight of Ariane 5, destroyed about 37 seconds after lift-off. Inquiry board chaired by Jacques-Louis Lions.**

## The situation

The Inertial Reference System software was inherited, largely unchanged, from Ariane 4 — where it had
flown successfully many times. Reusing proven flight software is normally the *safe* choice.

## What happened

A conversion of a 64-bit floating-point value representing horizontal bias into a 16-bit signed
integer overflowed, because Ariane 5's trajectory produced horizontal velocities far larger than
anything Ariane 4 could generate. The operand error was unprotected — the conversion had been left
unguarded on the grounds that the physical value could not exceed the range, which was true for
Ariane 4.

The exception propagated. The active inertial reference unit shut down. The backup unit, running
identical software, had already failed the same way milliseconds earlier for the same reason.
Diagnostic data was then interpreted by the on-board computer as flight data, the nozzles swivelled
hard, the vehicle broke up and was destroyed by the range safety system.

The offending computation was **not even needed after lift-off**. It was part of an alignment
function that served only a pre-launch purpose, left running for a few seconds into flight for
operational convenience inherited from Ariane 4.

## Why it failed

**The assumption was valid and undocumented.** "Horizontal bias cannot exceed 16-bit range" was a
true statement about a *different vehicle*. Nothing in the code recorded which vehicle it was true
of.

**Redundancy did not help, because both channels shared the assumption.** Identical backups protect
against random hardware failure and give nothing against a design fault.

**The component was reused without re-deriving its preconditions in the new environment.**

## The principle

**Reuse imports the assumptions of the original environment along with the code.** Every reused
component must have its preconditions re-derived against the new context, and identical redundancy
protects against nothing systematic.

## For us

Three live instances, one of which I created today.

**The EPD cache.** `LEADER_BIBLE.md` §5 names the cache-key family: `data/training/cache/*.jsonl` is
keyed by position, **not** by node budget or network. Eight thousand eight hundred and forty-five
entries were computed at `confirm_best_seconds: 6.0` / `confirm_played_seconds: 3.0`. The moment we
switch to node budgets those entries are a different measurement wearing the same key — a valid
assumption from a retired environment. This is exactly Ariane 5, and it is the reason the node-budget
decision is deferred until after the T4 rehearsal rather than taken now.

**The motif labels.** The N1 "spent tactic" negatives *inherit their puzzle's themes* — 3.96 motif
bits per row against 3.90 for positives. Those labels were true of the position the puzzle started
from; they are false of the position after the solution has been played. Reused label, retired
context. Caught while writing the loss, and handled by masking the motif head to positives only.

**The theme vocabulary.** The 20 motif outputs are positional against a frozen list in
`manifest.json`, and our two dataset builds already order it differently. A checkpoint trained on one
build and evaluated against another would have meant something different with no shape change and no
error. Fixed by writing the manifest into every checkpoint and refusing across builds — the
precondition is now carried *with* the artefact instead of assumed.

**The general rule adopted:** when reusing anything — a cache, a label, a component, a benchmark
number — write down what environment made it valid, and put that record where the reuser will trip
over it.
