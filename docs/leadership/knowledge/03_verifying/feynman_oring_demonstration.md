# Feynman, the ice water, and Appendix F

**Rogers Commission on the Challenger accident, 1986.**

## The situation

Challenger broke up 73 seconds after launch on 28 January 1986. The proximate cause was a failure of
the O-ring seals in a solid rocket booster field joint, which had lost resilience in the coldest
launch temperatures the programme had ever attempted.

The Commission was a formal body with a large staff and a schedule. Its natural output was a
document.

## What was done

At a televised hearing, Feynman took a sample of O-ring material, compressed it with a small clamp,
dropped it into a glass of ice water, and after a few minutes showed that when released it did not
spring back — the material had lost resilience at low temperature. The whole demonstration took
minutes and used a clamp, a glass, and ice.

He also insisted on going to the engineers directly rather than working through management
briefings, and found that engineers' estimates of catastrophic failure probability differed from
management's by about three orders of magnitude — roughly 1 in 100 versus 1 in 100,000.

His personal appendix to the report (Appendix F) ends:

> "For a successful technology, reality must take precedence over public relations, for Nature
> cannot be fooled."

## Why it worked

Because it converted an argument into an **observation anyone could make**. The technical case was
already in the record — Thiokol engineers had raised the temperature concern the night before the
launch — and it had failed to persuade because it lived in charts, caveats and probability. The ice
water was irrefutable, immediate, and required no expertise to evaluate.

The second reason: he **sampled the population that had the information**, not the population that
had the authority. The three-orders-of-magnitude gap is the whole accident in one number, and it is
invisible from the top of the organisation because management's estimate is the one that travels
upward.

## The principle

**The cheapest decisive demonstration beats the most thorough argument.** And: when you want to know
what an organisation knows, ask the people doing the work, not the people reporting on it.

## For us

The pattern of the last two days has been exactly this, and it is the thing I am best at.

- Gemini argued that float32 rank sums would lose precision on 200k rows. Plausible, well-reasoned,
  and it assumed naive summation. **Measured: 4e-08 to 8e-08.** Torch sums pairwise.
- It argued that a live `GradScaler` under `--no-amp` risks "parameter corruption". **Measured: 0.0
  gradient difference**, because scale-then-unscale by a power of two is exact in fp32.
- It documented a launch command in the how-to. **Executed it: `ModuleNotFoundError`.**
- My own `roc_auc` tie-handling looked correct. **Timed it: 1.22 s per call**, three calls an epoch,
  one device synchronisation per element on CUDA.

Each took under two minutes and settled a question that argument could not. `LEADER_GROUNDING.md`
§3d.1 states the rule — *perturb before you claim; re-reading is not verification, because my model
of the artefact does the reading and cannot trip on an error.*

**The ice-water test to keep asking:** what is the smallest physical thing I could do, right now,
that would be decisive? Usually it is running the code rather than reading it, and usually I think
of it only after I have written a paragraph of reasoning.

**And the honest limit.** The three-orders-of-magnitude gap has an analogue here: the mixed-precision
path in `phi_net` has now been reviewed by two parties and executed by neither. Everything anyone
has said about it — mine included — is management's estimate.
