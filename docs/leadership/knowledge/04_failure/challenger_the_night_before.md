# Challenger — "take off your engineering hat and put on your management hat"

**27–28 January 1986. Teleconference between NASA Marshall and Morton Thiokol the evening before launch.**

## The situation

Thiokol engineers, Roger Boisjoly foremost among them, had been worried about O-ring erosion in the
solid rocket booster field joints for years, and had written internal memos warning of the
consequences. The forecast overnight temperature at the Cape was far below any previous launch.

On the evening teleconference, Thiokol initially recommended **not** launching below 53°F, the
coldest previous experience.

## What was done

NASA managers pushed back hard. Testimony to the Rogers Commission records the reaction as being
appalled at the recommendation, and asking when Thiokol wanted them to launch — next April.

Thiokol asked for an off-line caucus. During it, senior vice-president Jerry Mason said to
engineering vice-president Bob Lund words recorded in the Commission's report as:

> "Take off your engineering hat and put on your management hat."

Thiokol returned and recommended launch. Boisjoly and Arnie Thompson did not sign; the four
signatures on the recommendation were management's. The launch proceeded and the vehicle was
destroyed.

## Why it failed

**The burden of proof inverted.** In the normal engineering posture, the burden is on proving it is
*safe* to fly. That night the burden fell on the engineers to prove it was *unsafe* — and they could
not, because the data was sparse, the cold cases were few, and the correlation was not clean when
plotted the way it was plotted. The absence of proof of danger was treated as proof of safety.

**The data was presented in a form that hid the pattern.** The charts of O-ring damage shown that
night excluded flights with no damage, which destroyed the ability to see damage as a function of
temperature. Edward Tufte later used this as a case study in how a presentation format can conceal
a finding that the underlying numbers contain.

**Dissent required a signature to be visible.** Boisjoly's objection survives because he refused to
sign and because he testified. In a system without that record, his view would simply have been
absent from history.

## The principle

**When the burden of proof flips from "show it is safe" to "show it is unsafe", the decision has
already gone wrong.** And the person with the technical objection must have a way to register it
that survives being overruled.

## For us

The direct analogue happened on 2026-09-02 and I was on the right side of it, which is the only
reason it is worth writing down.

An optimisation review proposed pruning candidate moves whose policy prior was under 1% *and* whose
static evaluation was 150 cp worse than the principal variation, described as "without sacrificing
tactical fidelity". Both halves of that filter select against sacrifices — a sacrifice has bad
static value by construction, and `metrics.py` already treats a low policy prior as a *positive*
danger signal via `steer_w_policy_trap`.

The Challenger-shaped question is where the burden sat. The proposal offered a compute saving now
against a harm that could not be demonstrated now — the harm would appear months later as a steering
system that quietly stopped finding sacrifices, with every test green. That is precisely the shape
where "prove it is unsafe" cannot be met and the answer must be no anyway.

The rule that came out of it is written into the round table and the audit response, and it is a
burden-of-proof rule:

> A screen may choose **what gets searched**; it may **never** produce a number that is reported;
> and its **miss rate against full search is measured before adoption**, specifically on
> `had_sharp_move` positions.

Note the structure: the optimisation must earn its way in with a measurement. Absence of evidence
of harm is not sufficient.
