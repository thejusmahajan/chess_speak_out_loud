# Leadership knowledge base

Built 2026-09-02 at Thejus's instruction, to study how leadership has actually worked and failed,
and to apply it to this project.

**Read `DISTILLATION.md` for the principles and `APPLICATION.md` for what changes here.** The case
files are the evidence; those two are the point.

---

## The sourcing standard, which is the first leadership lesson in the file

This project has **four fabricated deliveries on record** and a rule — *grep every quoted string
before believing a report that quotes a file*. A corpus of leadership anecdotes is unusually easy to
fabricate, because inspiring quotations circulate detached from their sources and get better as they
travel. So:

1. **No invented quotations.** Where a line is quoted, it is one I am confident is real and
   attributed correctly.
2. **Popular misattributions are flagged, not repeated.** The most famous line associated with
   Apollo 13 was written for a film in 1995. Saying so is more useful than repeating it.
3. **Where an account is one author's telling rather than a documented record, it says so** — Sloan's
   "develop disagreement" survives mainly through Drucker, and that provenance matters.
4. **Dates and numbers are given only where I am confident.** Where a figure is commonly cited in a
   range, the range is given.
5. **These are cases, not parables.** Every one is compressed and therefore lossy. The failure
   modes generalise; the biographies do not.

A corpus that fails its own project's evidentiary standard would be worse than no corpus.

---

## Structure

| directory | question it answers |
|---|---|
| `01_command/` | How do you direct work you cannot personally supervise? |
| `02_deciding/` | How do you decide under uncertainty, and when do you decide fast? |
| `03_verifying/` | How do you know what is actually true of the work? |
| `04_failure/` | How do competent organisations produce catastrophes? |
| `05_expedition/` | How do you lead when the plan is dead and the goal must change? |
| `06_building/` | How do you organise the making of a hard technical thing? |
| `07_teams/` | How do you get information to flow against the authority gradient? |
| `08_integrity/` | What does it cost to be right, and to admit being wrong? |

Each case file has the same five parts: **the situation**, **what was done**, **why it worked or
failed**, **the transferable principle**, and **for us** — the line connecting it to this
repository's own record.

---

## Why these cases and not others

Selection is not neutral, so here is the bias, declared. Cases were chosen because they map onto
failure families **this project has actually suffered**, catalogued in `LEADER_BIBLE.md` §5 and
`docs/leadership/LEADER_GROUNDING.md`:

| our failure family | the case that anatomises it |
|---|---|
| POV/frame errors | Mars Climate Orbiter — two teams, two unit systems, one lost spacecraft |
| fixing one site and not its sibling | Knight Capital — deployed to seven servers of eight |
| reused component, unchecked assumption | Ariane 5 Flight 501 |
| a metric that measures X and is named Y | Columbia, and the normalisation of deviance |
| the expert overruled for schedule | Challenger, the night before |
| infrastructure that postpones exposure | the Vasa, and Brooks on the second system |
| under-specification blamed on the worker | Deming — the system, not the worker |
| the junior who is right and not heard | Tenerife, and the invention of Crew Resource Management |
| correcting your own error in public | LeMessurier and the Citicorp Center |

The last one is not a hypothetical here. It is the story Thejus tells about himself in job
applications, and it is the reason this repository exists in the shape it does.

---

## What this corpus is not

It is not a substitute for the mechanical interlocks in `LEADER_GROUNDING.md`. Today's eight
defects — a flag added and not threaded, a `sys.path` repair applied to one file and not its
sibling, a command documented and never executed — were failures of **thoroughness at the seam**,
and no amount of historical reading fixes those. `grep` fixes those.

What this corpus is for is the other half: the decisions about aim, delegation, dissent and
verification that no checklist can make for you. `APPLICATION.md` keeps the two separate on purpose.
