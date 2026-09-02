# Boyd's OODA loop — and the part everyone drops

**John Boyd, USAF, 1960s–1990s. Developed from fighter combat analysis into a general theory of conflict.**

## The situation

Boyd began with a puzzle from Korea: the F-86 Sabre consistently beat the MiG-15 despite the MiG
being superior in several measurable respects — it could climb faster and turn tighter. Boyd's
answer was that the Sabre could *transition between manoeuvres* faster, because of its hydraulic
controls and its bubble canopy. It could change state, and see, quicker than its opponent.

## What was done

He generalised this into the cycle usually written **Observe – Orient – Decide – Act**, and usually
misunderstood as "go round it faster than the other guy."

The vulgarised version is a footrace. Boyd's actual claim is more interesting and is mostly about
**Orient**, which he drew as by far the largest element, fed by cultural traditions, genetic
heritage, previous experience, and new information, with feedback loops running back into Observe
and forward into Act. Orientation is the *interpretive frame* — the model through which observations
become meaning. Two people can observe identical data and orient to opposite conclusions.

His stronger claim: the way you defeat an opponent is not merely to cycle faster but to **operate
inside their orientation** — to generate situations their model cannot interpret, so their
observations stop producing usable decisions. Speed matters because it denies them time to re-orient,
not because velocity is itself a virtue.

## Why the popular version is dangerous

"Decide faster" is exactly the wrong lesson for anyone whose orientation is wrong. A fast loop
around a bad model produces confident wrong actions at high tempo. Boyd's own emphasis was on
destroying and rebuilding your mental models — he wrote about analysis and synthesis, taking
frameworks apart and reassembling the pieces differently.

## The principle

**Tempo is worth having only after orientation is right. When results stop making sense, the fault
is usually in the frame, not in the data or the speed.**

## For us

The frame is where nearly all of our real damage has been done, and none of it was a speed problem.

- `had_tal_move` measured complexity and was *oriented* as sacrifice. The observations were fine.
- The Lichess puzzle `fen` is one ply before the tactic. Reading it as the tactic position is a
  pure orientation error, and it would have corrupted every sample in the dataset while every
  number looked healthy.
- Φ's meaning flips with the side to move. I wrote `Φ(after) − Φ(before)` into a README and into the
  plan, subtracting two different questions, and it would never have surfaced as a wrong answer.
- The screen-then-search proposal was oriented as "prune low-value candidates" when in this project's
  frame low static value *is the signal*.

Each of these is a case where more data and faster iteration would have made things worse, because
they would have produced more confident output from a wrong model.

**The practical form:** when a result is surprising, re-derive the frame before re-running the
measurement. And the interlock that catches frame errors is not speed but **perturbation** —
`LEADER_GROUNDING.md` §3d.1: predict what would be different if you were wrong, then go and make
that difference. Mutation-checking the colour-flip guard on 2026-09-02 is exactly that, and it is
the only reason we know the frame guard is real rather than decorative.
