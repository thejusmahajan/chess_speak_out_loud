# Knight Capital — deployed to seven servers of eight

**1 August 2012. Knight Capital Group, New York. Roughly $440–460 million lost in about 45 minutes; the firm did not survive independently.**

## The situation

Knight was deploying new code to support a NYSE retail liquidity programme. The deployment reused a
flag that had previously activated an old, dormant order-routing function called Power Peg — code
that had been left in the system for years, unused, and which lacked the safety behaviour of the
current path.

## What happened

A technician deployed the new code to **seven of the eight** production servers. The eighth kept the
old code. When the flag was set, the seven updated servers behaved as intended; the eighth
interpreted the same flag as "run Power Peg" and began sending child orders without the counter that
would have stopped them.

At market open the eighth server started emitting orders at enormous rate. Alerts fired, but they
were not routed to anyone able to interpret them as a deployment problem. Staff, reasoning that the
new code was the change, **removed the new code from the seven correct servers** — which put all
eight into the broken configuration and made the situation dramatically worse.

Roughly 45 minutes and about four million executions later, the firm had a loss larger than its
capital.

## Why it failed

**The deployment was partial and nothing detected that it was partial.** No automated check compared
what was running across the fleet.

**A dormant code path was reachable.** Power Peg had not been used in years and had not been removed;
it stayed live enough to be triggered by a repurposed flag.

**The diagnosis under pressure was backwards.** The reasonable hypothesis — the new code is the
problem — was wrong, and acting on it converted a partial failure into a total one. There was no
established procedure for "stop everything and work out what is different between the servers".

## The principle

**A change applied to some of the places it belongs is more dangerous than a change applied to
none**, because the system is now inconsistent in a way nobody has modelled. Enumerate every site
mechanically, verify the fleet matches, and delete dead paths rather than leaving them reachable.

## For us

This is my characteristic failure, at a scale where it costs nothing and with exactly the same shape.

On 2026-09-02, in a single session:

- I added `--no-amp` to `train.py` and did **not** thread it into `predict()`, so the documented
  mitigation silently did nothing during validation and test.
- I added the `sys.path` repair to `run_kaggle.py` and **not** to its sibling `evaluate.py`.
- I fixed the launch command in `HOW_TO_KAGGLE.md` and then wrote the notebook using a *different*
  mechanism — `subprocess.call` — reintroducing the invisible-output problem I had just fixed.
- I added `--no-amp` to `train.py` and never exposed it on `run_kaggle.py`, the only entry point
  where it matters on Kaggle.

Four instances of seven-of-eight, in one day, all found by an independent reviewer rather than by me.

**The dead-path half applies too.** `data/training/profile.json` carried `had_tal_move` after the
rename to `had_sharp_move` landed — a dormant key that no longer matched any selector, producing an
empty list rather than an error. The old path was reachable and silent.

**The interlock**, now written into `LEADER_GROUNDING.md`: *change one thing, grep the identifier
across the tree, and check every call site.* Not "be careful" — `grep -n`. The Knight technician was
being careful too.
