# One-way and two-way doors — matching rigour to reversibility

**Amazon, articulated by Jeff Bezos in the 2015 and 2016 shareholder letters.**

## The situation

A large organisation that applies uniform decision rigour will apply it wrongly in both directions.
Heavyweight process on reversible decisions makes it slow; lightweight process on irreversible ones
makes it reckless. The characteristic disease of a maturing company is applying the *irreversible*
process to everything, because that is what the process was built for.

## What was done

Bezos distinguished two classes:

**Type 1 — one-way doors.** Consequential and effectively irreversible. If you walk through and
dislike what you find, you cannot get back. These deserve slow, deliberate, heavily consulted
decisions.

**Type 2 — two-way doors.** Changeable. You can walk back through. These should be made quickly by
individuals or small groups with good judgement.

His warning was asymmetric and specific: organisations drift toward treating Type 2 decisions as
Type 1, which produces slowness, risk-aversion, and a failure to experiment. He did not warn much
about the reverse, because it is rarer in large organisations — though it is common in small ones.

The related Amazon practice is the **six-page narrative memo**, read in silence at the start of the
meeting. Its purpose is to force the author to think in complete sentences and to expose the gaps
that bullet points hide.

## The principle

**Classify the decision by reversibility before choosing how much rigour to spend on it.** Speed on
reversible decisions is not carelessness; it is the thing that pays for care on irreversible ones.

## For us

This is already in the repository, arrived at independently. Every brief header carries
`Blast-radius` and `Reversibility` fields, and `LEADER_GROUNDING.md` §3b states the rule directly:

> *Rigour is proportional to blast radius × irreversibility × SILENCE.*

The third factor is the local addition and it is the important one. Amazon's model has two axes; ours
has three, because our characteristic failure is not an irreversible mistake but a **silent** one —
a metric that measures the wrong thing, an empty list served as an answer, a dataset separable on
mobility. A cheap, reversible, silent error can sit in the record for months and poison everything
built on it. `sac_drill` returning `0` was reversible and free to fix, and it was wrong for five
weeks because nothing complained.

**Where the classification has been useful today:**

- *Two-way:* the phi_net code, the notebook, the archives. All rebuildable in minutes. I moved fast
  and let the audits catch things, which is correct.
- *One-way:* the node budgets for the profile regeneration. The EPD cache is keyed by position and
  not by budget, so changing the budget silently invalidates 8,845 cached entries. That decision is
  deliberately deferred until the T4 rehearsal produces a real number, and that deferral is the
  model working.
- *One-way and not yet treated as such:* the dataset's rating window, seed and stride are frozen in
  `manifest.json`. Every result we ever quote is conditioned on them, and they were chosen in a
  single pass from one memory note about the 1500–2000 band.
