# Error budgets and blameless postmortems

**Google Site Reliability Engineering, practices formalised in *Site Reliability Engineering* (O'Reilly, 2016).**

## The situation

Two groups with opposed incentives: developers want to ship, operators want stability. The usual
resolution is political — whoever is more senior, or whoever was most recently burned, wins. This
produces either paralysis or repeated outages, alternating.

## What was done

**The error budget.** Set an availability target — 99.9%, say — and note that this explicitly
permits 0.1% unavailability. That remainder is a **budget**, and it is spent by shipping. While
budget remains, the team ships freely. When it is exhausted, releases stop until reliability is
restored.

The move is to convert a political argument into an arithmetic one. Nobody debates whether to ship;
they read the number. And it makes explicit the thing everyone knew and nobody said: **100%
reliability is the wrong target**, because the marginal cost rises without limit and the user cannot
tell the difference.

**Blameless postmortems.** After an incident, the written analysis names systems and causes, not
culprits. The reasoning is not kindness; it is data quality. If the postmortem determines who is
punished, the people with the most information have the strongest incentive to shade it, and the
organisation loses the only account of what actually happened.

The counterpart, which is often dropped: blameless does **not** mean consequence-free. It means the
consequence attaches to the *system* — the fix is a guardrail, a test, an automated check — rather
than to the person.

**Toil budgets.** Cap the fraction of time spent on manual, repetitive work, on the grounds that
without a cap it expands to fill everything and no automation ever gets built.

## The principle

**Turn contested trade-offs into explicit budgets, and make the postmortem safe enough to be
accurate.** A number that everyone agreed to in advance settles arguments that seniority otherwise
settles badly.

## For us

**The error budget maps onto something we have and do not name.** Kaggle gives roughly 30 GPU-hours
a week. Colab Pro units are money Thejus borrowed. Those are budgets in the SRE sense — finite,
replenishing, and spendable on risk. The decision rule already reached ("if Kaggle's quota is too
small, cut the game count or the node budget, not spend borrowed money") is an error-budget
decision: when the budget is exhausted, reduce scope rather than borrow.

What we have *not* done is write the number down before the argument. The right form is: *this
week's Kaggle allowance is N hours; the profile regeneration may spend up to M of them; if M is
exceeded the scope is cut, not the budget raised.* Deciding that now, while nothing is at stake, is
Kranz's mission rule in a different costume.

**The blameless postmortem is a strength here and worth protecting.** The record is unusually honest:

- `LEADER_GROUNDING.md` is a catalogue of the leader's own failures, written by the leader.
- The 2026-09-01 post-mortem on the deleted round table names my error precisely and does not
  soften it.
- `PREFLIGHT_REVIEW.md` states that my own smoke test *deliberately does not exercise the riskiest
  code in the package*.
- Every audit of Gemini's work this week says plainly which failures were caused by my
  specification.

And the counterpart is being observed: consequences attach to systems. Each defect this week became
a guard — `test_phi_net_gate.py`, mutation-checked — rather than a resolution to be careful.

**Where the toil budget applies.** Four review passes to ship a notebook is toil. It caught real
defects, so it was worth it, and a process that needs four passes is one whose defects should be
made impossible instead of found. That is the direction Deming points too, and it is the same fix.
