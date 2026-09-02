# Distillation — what thirty-two cases actually agree on

Read the cases for evidence; read this for the pattern. `APPLICATION.md` is what changes here.

---

## The single strongest finding

**Almost none of these failures were caused by a lack of information. In nearly every one, someone
in the organisation already knew.**

Thiokol engineers knew about O-rings in cold weather and said so the night before. NASA engineers
requested imagery of Columbia's wing and were refused. The Vasa was rocked by thirty running men and
the test was stopped for fear of capsizing her *at the quay* — and she sailed. Therac-25 hospitals
filed reports. Mars Climate Orbiter navigators noticed the trajectory anomalies during cruise. The
KLM flight engineer asked whether the Pan Am aircraft was clear.

The knowledge was present and the *mechanism to act on it* was absent. That reframes what leadership
mostly is: not being the smartest source of judgement, but **building channels that carry
inconvenient information to a place where it can stop things.**

Corollary, uncomfortable and consistent: when something goes wrong, the useful question is rarely
"who was wrong" and almost always "what prevented what was already known from arriving".

---

## Six principles, ranked by how much damage they prevent

### 1. Decide the rule before the moment, and obey it when it fires

*Kranz's mission rules; Eisenhower's failure note; Sloan's adjournment; the Vasa's abandoned
stability test.*

The moment a decision is needed is the worst moment to make it — sunk cost is visible, the schedule
is loud, and everyone senior is watching. A rule written in a quiet room is the only representative
of calm judgement in the room.

But the Vasa supplies the sharper half: **a test whose failing result you will not act on is worse
than no test.** It converts a warning into a completed ritual. The rule earns its authority entirely
from being obeyed the first time it is inconvenient.

And Challenger supplies the failure mode: watch for the burden of proof inverting. The moment the
question shifts from *show it is safe* to *show it is unsafe*, the decision has already gone wrong.

### 2. Go to the object; the report is a lossy encoding

*Ohno's chalk circle; Rickover reading the correspondence; Feynman's ice water; the Wrights' wind
tunnel.*

Every organisation manages a representation — status, summaries, dashboards, reports — and the
representation is always more comfortable than the thing. Feynman found engineers and managers
differing on catastrophic failure probability by three orders of magnitude, and the *management*
number was the one that travelled upward.

The transferable technique is the ice water: **the cheapest decisive demonstration beats the most
thorough argument.** Ask constantly what the smallest physical act is that would settle this, and
then do it instead of reasoning about it.

### 3. State the frame at every boundary

*Mars Climate Orbiter; Ariane 5; Boyd on orientation.*

Units, coordinate systems, points of view, whose turn it is, which vehicle the assumption was true
of — these are unstated contracts, and unstated contracts are where two correct components produce
one wrong system. Both spacecraft were destroyed by software that worked perfectly.

Boyd generalises it: when results stop making sense, the fault is usually in the *frame*, not in the
data or the speed. A faster loop around a wrong orientation just produces confident errors sooner.

Defences, in order of strength: canonicalise at the boundary so the frame exists in one place; test
the boundary end-to-end with real values rather than testing each side; put the frame in the name.

### 4. Apply the change everywhere it belongs, and delete what is dead

*Knight Capital; Ariane 5's unnecessary alignment function; the `had_tal_move` key.*

A change applied to seven servers of eight is **more dangerous than a change applied to none**,
because the system is now inconsistent in a way nobody has modelled. Reachable dead code is the same
hazard waiting for a flag.

This is the one principle on this list that is purely mechanical. It is not solved by judgement,
seniority or care. It is solved by enumerating the sites with a tool.

### 5. Separate the aim from the plan, and say out loud when the plan is dead

*Shackleton; Grove's "what would our successors do"; Brooks's own retraction.*

Persistence toward a dead goal is not tenacity. Shackleton substituted the objective on the day the
ship was lost, announced it, and cut sunk cost visibly starting with his own possessions.

Grove supplies the debiasing tool for when identity is entangled: ask what a competent stranger with
no history would do, then do that. The information is usually already present; what is missing is
permission.

Brooks supplies the honest ending — he publicly retracted "plan to throw one away" twenty years
later. Retracting your own most-quoted line is the same act as Shackleton's cigarette case.

### 6. Blame the system, then remove the inspection

*Deming; blameless postmortems; CRM.*

Deming's inversion — interrogate the system before the person — is now widely accepted and half
applied. The half that gets dropped is the second: **cease dependence on inspection.** A defect
caught at review is a defect the process was built to allow, and an organisation that needs four
review passes is one whose defect rate the reviews are barely outrunning.

The direction of travel is from *caught* to *impossible*: a function that raises on ambiguity instead
of a reviewer noticing; a refusal across dataset builds instead of a reminder to check.

---

## Three tensions the cases do not resolve

**Control versus context.** Rickover ran the safest technical programme in history on obsessive
central verification. Netflix argues that for creative work the same instinct destroys judgement and
speed. Both are right *in their regime*, and the regime is set by whether errors are cheap and
reversible or silent and irreversible. Most projects contain both regimes and apply one policy.

**Margin versus tempo.** Amundsen's flag lines and surplus depots look like timidity right up until
Scott dies. But margin is paid for in speed, and Grove's inflection point kills companies that were
being prudent. Neither "have margins" nor "move fast" is a decision rule; the question is always
*margin against which specific error you will certainly make.*

**Pinned specification versus mission command.** Moltke says include everything the executor cannot
determine and nothing more. Our experience says an under-specified brief is dangerous in exact
proportion to its under-specification. Both are true, and the boundary between them is not stable —
it moves as the executor's judgement is demonstrated.

---

## The compressed version

1. Someone already knows. Build the channel.
2. Write the rule before the moment; obey it the first time it hurts.
3. Go and look at the object.
4. Name the frame at every boundary.
5. Grep every site; delete the dead path.
6. Kill plans, never the aim.
7. Move checks from review into the code.
8. Faith in the outcome, brutal facts about the present, and never a date attached to the faith.
