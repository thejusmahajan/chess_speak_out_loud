# Brooks — conceptual integrity, the surgical team, and the second system

**Fred Brooks, *The Mythical Man-Month* (1975; anniversary edition 1995), drawn from managing IBM OS/360.**

## The situation

OS/360 was one of the largest software projects of its era and was late, expensive, and complex.
Brooks, who had managed it, wrote up why — and produced the observations that most of software
engineering has been rediscovering since.

## The claims that matter here

**Brooks's Law.** Adding manpower to a late software project makes it later. The reason is
communication overhead — pairwise coordination grows quadratically — plus the training cost paid by
the people who already understand the system.

**Conceptual integrity is the most important consideration.** He argues it is better to have a
system reflect **one set of design ideas** than many good but uncoordinated ones. A coherent design
with omissions beats an incoherent design with more features, because a user can learn one mind and
cannot learn twelve.

**The surgical team.** From Harlan Mills: rather than a democratic team of equal programmers, one
chief programmer does the design and the critical code, supported by specialists — a copilot, an
administrator, a toolsmith, a tester. The point is to preserve conceptual integrity by *not*
dividing the design.

**The second-system effect.** The most dangerous system an architect designs is the second one,
because it accumulates all the embellishments he prudently left out of the first. The first is lean
from inexperience; the second is bloated from confidence.

**Plan to throw one away; you will, anyhow.** Brooks himself **retracted this** in the 1995 edition,
calling it too simple — the incremental/iterative model, where the system is grown rather than
discarded, is better than build-one-to-throw-away. The retraction is worth as much as the original.

## The principle

**Protect the coherence of the design by keeping it in few enough heads to stay coherent, and be
most suspicious of your second version.**

## For us

**The surgical team is exactly the structure we run**, and it was arrived at by economics rather
than by reading Brooks. `CLAUDE.md`: *your pool is small; spend it on reasoning, on the exact wording
of a spec, and on verification — never on bulk typing. Gemini does the heavy lifting.* Leader as
chief programmer, worker as the hands, and `metrics.py` explicitly leader-owned as the mathematical
source of truth.

The evidence that conceptual integrity is doing real work: on 2026-09-02 Gemini improved the
notebook and I took its streaming fix while rejecting its discovery rewrite — not because the rewrite
was badly made, but because it silently picked among candidates, which contradicts a principle
running through the whole codebase. Holding that line is what "one set of design ideas" means in
practice.

**The second-system warning applies to `phi_net` right now.** The first configuration-steering
dataset was lean. The second has: a mobility-bucketed matching key, four alarms, per-row `source`,
manifest identity carried in checkpoints, a three-shape mount resolver, stale-output clearing, and a
notebook that discovers its own inputs. Every addition was justified by a real defect — and that is
exactly how a second system bloats. Each embellishment has a name and a reason, and there are now
eleven of them.

**And Brooks's Law in our terms.** We cannot add people, but we can add *work* — corpora, briefs,
round tables, audits of audits. The equivalent of adding manpower to a late project is adding
process to an unfinished one, which `CLAUDE.md` non-negotiable #6 already forbids. I am writing this
paragraph inside a corpus that tests that rule.
