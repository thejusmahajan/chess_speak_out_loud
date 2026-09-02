# Gene Kranz — mission rules written before the mission

**NASA Mission Control, 1960s–70s. The "Tough and Competent" address to the Flight Control Branch, 30 January 1967, three days after the Apollo 1 fire.**

## The situation

Apollo 1 killed Grissom, White and Chaffee in a pad fire during a plugs-out test. The vehicle had a
pure-oxygen cabin at above-ambient pressure, flammable materials, and an inward-opening hatch that
could not be released quickly. None of these facts was secret; all had been noted; the test was
classified as non-hazardous because there was no fuel in the rocket.

## What was done

Kranz assembled his branch and told them, in substance, that they were at fault: that they had known
things were wrong and had not stopped, that they had trusted contractors' schedules over their own
judgement, and that from that day forward Flight Control would be known by two words — **Tough** and
**Competent**. Tough meaning permanently accountable for what they do or fail to do; Competent
meaning never taking anything for granted, never stopping learning. He asked them to write the two
words on their blackboards and never erase them.

The other, older practice matters as much: **mission rules**. Before a flight, controllers wrote
down the conditions under which they would abort, continue, or switch to a backup — in advance, in
writing, with the reasoning. During the mission, with adrenaline and hierarchy and a countdown
clock, the rule had already been decided by people who had time to think.

## Why it worked

Mission rules solve a specific problem: **the moment when a decision is needed is the worst moment
to make it.** Under time pressure, with sunk cost visible and the whole programme watching, every
force pushes toward "continue". A rule written in a quiet room three months earlier is the only
representative of the calm judgement in the room.

The rules were not a bureaucratic constraint on the flight director's authority. They were his
authority, borrowed from his own earlier self.

## A note on the famous line

**"Failure is not an option" was written for the 1995 film** *Apollo 13*, by screenwriters drawing
on interviews. Kranz did not say it during the mission; he later adopted it as the title of his
memoir. The genuine slogan from the period is "Tough and Competent". This corpus flags it because
repeating a screenwriter's line as a primary source is the same error class as citing a fabricated
quote from a file.

## The principle

**Write the abort criteria before the run, when nothing is at stake. In the moment, the rule is the
only thing arguing for the calm decision.**

## For us

This is the design of `PLAN_CONFIGURATION_STEERING.md` §8, and it was written before the dataset
existed:

| gate | rule | decided |
|---|---|---|
| F0 | material-only AUC < 0.65 | before the build |
| F1 | Φ held-out AUC > 0.70 | before the build |
| F2 | Φ AUC − material ≥ 0.03 | before the build |

Two things that follow, both already tested:

**The rule fired and we obeyed it.** A4 caught the first dataset build at 0.6637 and it was rebuilt
rather than argued with — 301,116 rows discarded for 261,748 honest ones.

**Writing the rule at the wrong altitude is itself a failure.** I applied the *full* gate set to the
B1 rung, which would have aborted the Kaggle session on a B1 of 0.66 — a good result. Mission rules
must be written for the specific decision they govern; a rule imported from a different phase is
worse than none, because it carries the authority of having been pre-registered.

**And the ethos.** Kranz's charge — you knew things were wrong and did not stop — is the one to keep
in view. `sac_drill` returned `0` for five weeks. Nothing crashed. Nobody stopped.
