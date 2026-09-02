# The Wright brothers — the wind tunnel, not the big shot

**Dayton and Kitty Hawk, 1899–1903. First powered controlled flight 17 December 1903.**

## The situation

Two contemporaries pursued powered flight with very different methods.

**Samuel Langley**, Secretary of the Smithsonian, had roughly $50,000 of War Department funding and
substantial institutional support. His approach was to build a full-scale machine, the Aerodrome,
and launch it from a catapult over the Potomac. It failed twice, in October and December 1903, each
failure destroying the aircraft and nearly drowning the pilot.

**The Wrights** ran a bicycle shop and funded the work from it.

## What was done

**They identified the unsolved problem correctly.** Lift and propulsion were reasonably understood;
**control** was not. Most experimenters sought inherent stability. The Wrights, from watching birds
and from bicycles, concluded the machine should be unstable and controlled by the pilot — and
invented wing-warping for roll.

**They built a cheap test rig when the published data proved wrong.** Their 1900 and 1901 gliders
underperformed the predictions from Lilienthal's coefficient tables. Rather than trust the
literature or guess, they built a wind tunnel from a wooden box and a fan and tested on the order of
two hundred miniature airfoil shapes. They produced their own tables, and those tables were right.

**They flew gliders hundreds of times before adding an engine.** Each flight was seconds long and
cost nothing to repeat. Failures were survivable and informative.

**They built their own engine and propellers** when nothing suitable existed — deriving propeller
theory themselves, because a propeller is a rotating wing and nobody had treated it that way.

## Why it worked

Because they converted a single expensive question into thousands of cheap ones. Langley's method
allowed roughly one experiment per year, each fully coupled — a failure told you the machine did not
work, not why. The Wrights' wind tunnel gave many decoupled answers per day.

The deeper move: **when the published data conflicted with their observations, they built an
instrument to settle it** rather than deferring to authority or to their own intuition.

## The principle

**Decompose an expensive uncertain question into cheap decoupled ones, and build the instrument that
settles the disagreement.** A test you can run two hundred times teaches more than a demonstration
you can run twice.

## For us

This is the **ladder**, and it is written into `PLAN_CONFIGURATION_STEERING.md` §8b:

| rung | cost | question |
|---|---|---|
| B0 | seconds, CPU | is the dataset trivially separable? |
| B1 | minutes, free T4 | does Φ learn anything at all? |
| B2 | longer | does it hold at full scale — the real held-out number? |

The same shape appears in `LEADER_BIBLE.md` §4 for the GPU work: local (free) → T4 rehearsal (cheap)
→ one A100 shot. Gates before credits.

**The wind-tunnel move — building an instrument to settle a disagreement — has paid four times in
three days**, and it is the thing I am reliably good at:

- 1.22 s per `roc_auc` call, timed, not argued.
- float32 rank-sum error measured at 4e-08 against a claim that it would matter.
- `GradScaler` gradient difference measured at exactly 0.0 against a claim of "parameter corruption".
- The documented launch command executed, producing `ModuleNotFoundError`.

**Where we are still Langley.** The profile regeneration is a single expensive coupled experiment:
9,000 games, one profile, roughly 51 days of engine time on this hardware, and if the result is
disappointing we will not know which of a dozen choices caused it. The Wright answer is not more
compute. It is to decompose — does a 200-game profile answer the coaching question? does the bullet
corpus contain knowledge errors at all, or only reflex errors? Those are cheap and nobody has asked
them.
