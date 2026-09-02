# Deming — the fault is in the system

**W. Edwards Deming, statistician; work in Japan from 1950, *Out of the Crisis* (1982).**

## The situation

Deming came from statistical process control, and the central distinction is between **common-cause**
variation — inherent in the system — and **special-cause** variation, attributable to something
specific and identifiable.

His empirical claim, stated in *Out of the Crisis*: the great majority of problems belong to the
system rather than to the worker. He gave the figure as roughly **94% common causes, 6% special
causes**.

## What follows from it

**Blaming the worker for common-cause variation makes things worse.** It adds fear, suppresses
reporting, and produces tampering — adjusting a stable process in response to noise, which increases
variation.

**The red bead experiment.** Deming would have volunteers draw beads from a container mixed with red
and white ones, using a paddle, and then praise, rank and fire them by their proportion of red
beads. Nobody could affect the outcome; the proportion was a property of the container. The point is
that a manager who ranks people on outcomes largely determined by the system is measuring noise and
calling it merit.

**"Drive out fear"** is one of his fourteen points, on the reasoning that a frightened organisation
produces distorted information, and that management then makes decisions on the distortion.

**"Cease dependence on inspection to achieve quality."** Inspection at the end is too late and too
expensive; quality must be built into the process. Inspection finds defects, it does not prevent
them.

## The principle

**When output is bad, interrogate the system that produced it before interrogating the person.** And
inspection is a fallback, not a strategy: a defect caught at review is a defect the process was
built to allow.

## For us

This project got Deming's first point right early and has the record to prove it.
`docs/leadership/LEADER_GROUNDING.md` opens with the leader's own failure catalogue and states:

> **The standard I enforce on output must apply to my input.**

and

> *I specify from memory and partial reads, scope by convenience, and verify the least where the
> consequences are quietest.*

`CLAUDE.md` says it directly: *Gemini is dangerous in exact proportion to how under-specified the
task is — under-specifying is your failure, not the worker's.*

That is Deming's inversion applied correctly, and the evidence that it works is visible in the last
three days. Every Gemini delivery this week was honest: it followed the brief, invented no numbers,
and where the result was unusable — the first `config_steering` build, separable at AUC 0.6637 on
mobility and check — **the fault was in my specification**. I wrote three alarms that all
interrogated material and none that interrogated anything else. The worker passed every gate it was
given. The gates were mine.

**Where Deming's second point convicts us, and it is the more useful half.**

*Cease dependence on inspection.* Our quality currently comes overwhelmingly from inspection: audits,
audits of audits, mutation checks, independent reviews. Eight defects were found by review on
2026-09-02, and reviewing found them — but a process that requires four review passes to ship a
notebook is a process that produces defects at a rate the reviews are barely keeping up with.

The Deming answer is to move the checks into the system so the defect cannot be created:

- `resolve_data_dir` **raising** on ambiguity rather than a reviewer noticing `nested[0]`.
- `evaluate.py` **refusing** across dataset builds rather than a reviewer remembering to check.
- `clear_stale_outputs()` **deleting** the artefact rather than a reviewer spotting a stale one.
- `b1_verdict` extracted as a **testable function** rather than reviewed prose.

Each of those converts an inspection into a property. That is the direction to keep pushing: fewer
things caught, more things impossible.
