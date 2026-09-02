# Apollo 13 — work the problem, and do not make it worse by guessing

**11–17 April 1970. Oxygen tank 2 ruptured about 56 hours into the flight; the crew returned alive.**

## The situation

An explosion in the Service Module destroyed the spacecraft's oxygen supply and, with it, the fuel
cells that made electrical power and water. The Command Module had limited battery power that had to
be preserved for re-entry. The crew were about 320,000 km from Earth in a vehicle that could no
longer support them.

## What was done

**The Lunar Module became a lifeboat.** It had its own oxygen, power and propulsion, and was
designed for two men for two days; it had to keep three alive for four. This use was not in the
mission plan, though lifeboat scenarios had been discussed in earlier simulations.

**Consumables were budgeted to the return, not to comfort.** Power was cut to a fraction of normal.
The Command Module was powered down entirely and a novel power-up sequence had to be written from
scratch, tested in the simulator, and read up to a cold, exhausted crew.

**The CO₂ problem was solved with the inventory actually aboard.** The LM's lithium hydroxide
canisters were round; the CM's spares were square. Ground teams assembled a filter adapter from
items known to be on the spacecraft — flight plan covers, tape, a sock, hose from a suit — and
talked the crew through building it.

**Nothing irreversible was done in a hurry.** Burns were computed, checked, and rehearsed. The
temptation to attempt a direct abort was resisted in favour of the free-return trajectory around the
Moon, which was slower and did not require the damaged Service Module engine.

## A note on the famous line

**"Failure is not an option" is a 1995 screenplay line**, not something said in Mission Control in
1970. The genuine ethos is better captured by Kranz's actual instruction to his team to stop guessing
and work the problem, and by the standing rule that a controller does not act on a hypothesis he has
not verified. Repeating the film line as history is the same error class this project calls
fabrication.

## The principle

**In a crisis, inventory what you actually have, budget it to the objective, and change nothing
irreversibly until you have verified the change.** Panic shows up as unverified action, not as
visible fear.

## For us

The Knight Capital counter-example is the reason this matters: under pressure, staff removed the new
code from the seven correct servers and made a partial failure total. Apollo 13 is what the opposite
discipline looks like.

**Where we already do this:**

- On 2026-09-01, facing a profile regeneration that projected to ~51 days, I did not start it. I
  measured the throughput, backed up `profile.json` first, and stopped the job when the number was
  in hand. State was restored to exactly what it had been.
- The Kaggle plan is a free-return trajectory: warming sessions bank cache and are discarded, one
  assembly pass produces the profile. Slower, and it does not require the damaged engine.
- `clear_stale_outputs()` is the powered-down Command Module — nothing left running that could later
  be mistaken for a live result.

**The inventory habit is the transferable one.** Both real advances this week came from asking what
is already aboard rather than what should be built:

- The puzzle `moves` column already contains the solution line, so precursor positions were free.
- `GameUrl` already sits in the local `.csv.zst`, so parent games cost an API call rather than a
  500 GB download.
- `confirm_best_nodes` and `confirm_played_nodes` already exist in the config, unset, so the
  node-limited path needs no code change at all.

Three times in three days, the answer was in the spacecraft.
