# Eisenhower's "In Case of Failure" note

**Supreme Headquarters Allied Expeditionary Force, written 5 June 1944, the eve of the Normandy landings.**

## The situation

Eisenhower held the decision on whether to launch Overlord into a marginal weather window. The
alternatives were to go on 6 June with a forecast break in the storm, or to postpone — which meant
weeks, a loss of tidal and moonlight conditions, and the near-certainty that the secret would leak.

He decided to go.

## What was done

Having given the order, he wrote a short note by hand and put it in his wallet, to be released if the
landings failed. It read, in part:

> "Our landings in the Cherbourg-Havre area have failed to gain a satisfactory foothold and I have
> withdrawn the troops. My decision to attack at this time and place was based upon the best
> information available. The troops, the air and the Navy did all that Bravery and devotion to duty
> could do. If any blame or fault attaches to the attempt it is mine alone."

He mis-dated it "July 5". It was never issued.

## Why it matters

Three things, in ascending order of usefulness.

The obvious one: he took sole responsibility in advance, and gave the credit away in the same
sentence.

The less obvious one: the note is **written before the outcome is known**. It therefore cannot be
contaminated by hindsight. Whatever he says about his reasoning is what he actually believed at the
moment of decision, not a reconstruction assembled after seeing the result.

The most useful one: writing it forced him to inhabit the failure concretely, while he could still
change his mind. A leader who cannot draft the failure announcement has not finished thinking about
the decision.

## The principle

**Before an irreversible commitment, write the account you would have to give if it fails — in
advance, and in detail.** It disciplines the decision, and it is the only version of your reasoning
that hindsight cannot rewrite.

## For us

This is the **pre-registered prediction**, and we already do a weak form of it. Every brief ends
with the mandatory audit field, borrowed from Perez via `LEADER_GROUNDING.md` §3d.3:

> *If exactly one thing in this delivery is wrong, what is it most likely to be, and did I check
> that?*

That is Eisenhower's note in miniature, and its whole value is that it is scoreable later — a
disclaimer is not.

Two places we have done it properly and one where we have not:

- **Done:** the falsification gates F0/F1/F2 were written into `PLAN_CONFIGURATION_STEERING.md` §8
  *before* the dataset was built. When B1 fails, we cannot relitigate what "success" meant.
- **Done:** `PREFLIGHT_REVIEW.md` §3 states, before the Kaggle run, exactly which code has never
  executed. If the run breaks in the mixed-precision path, that was predicted, not excused.
- **Not done:** nothing was written in advance about what we would conclude if F1 *passes*. Success
  has no pre-registered interpretation, which is precisely where a project talks itself into
  overclaiming. Φ passing F1 means *configurations are learnable from 18 planes*. It does not mean
  the steering works, and it will be tempting to say it does.
