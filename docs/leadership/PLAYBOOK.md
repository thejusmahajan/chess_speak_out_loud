# PLAYBOOK — what to do at the moment of decision

**This file is indexed by *situation*, not by theme.** It is the one to open when you are already
in the middle of something, which is when doctrine is hardest to recall and most needed.

It replaces nothing. The other three have different jobs:

| file | when you read it | what it is |
|---|---|---|
| `LEADER_BIBLE.md` | cold start, every session | doctrine, decided-do-not-relitigate, failure catalog, current state |
| `docs/leadership/LEADER_GROUNDING.md` | **before writing a brief** | my own failure catalogue, pre-flight/post-flight, the §7 seam checks |
| `docs/leadership/knowledge/` | when you want the evidence | 32 historical cases + `DISTILLATION.md` + `APPLICATION.md` |
| **this file** | **mid-task, at a decision** | situation → action |

Every entry ends with the case it comes from. If an entry ever seems wrong, the case is the appeal.

---

## ▸ You just changed something

**Do:** `grep -n "<identifier>"` across the tree. Open every call site. Name the file's sibling —
`train.py`/`evaluate.py`, README/how-to, notebook/how-to, source/`dist` copy — and check it too.

**Why:** four of eight defects on 2026-09-02 were a change made in one place and not in the place
that referenced it. *A change applied to some of the places it belongs is more dangerous than one
applied to none.* → `04_failure/knight_capital_seven_of_eight.md`

## ▸ You are about to write a command into a document

**Do:** execute it, exactly as written, before committing the document. Not a similar command.

**Why:** the launch line in `HOW_TO_KAGGLE.md` was plausible and died with
`ModuleNotFoundError` on the first cell. This is the most common way a README lies.
→ `03_verifying/feynman_oring_demonstration.md`

## ▸ You are about to argue about a number

**Do:** measure it instead. Ask what the smallest physical act is that would settle this, then do
that act rather than reasoning about it.

**Why:** "float32 rank sums lose precision" measured **4e-08**. "GradScaler risks parameter
corruption" measured **0.0**. "`roc_auc` looks fine" timed at **1.22 s per call**. Each took under
two minutes and settled what argument could not. → `03_verifying/feynman_oring_demonstration.md`,
`06_building/wright_brothers_cheap_iteration.md`

## ▸ A gate or alarm just fired

**Do:** stop. Do not tune the threshold. Report it, and treat the firing as the result.

**Why:** *a test whose failing result you will not act on is worse than no test* — it converts a
warning into a completed ritual. The Vasa's stability test was run, failed in front of witnesses,
and she sailed. Our A4 fired at 0.6637 and 301,116 rows were discarded instead.
→ `04_failure/vasa_the_kings_changes.md`, `03_verifying/kranz_mission_rules.md`

## ▸ You are about to write a threshold

**Do:** state which decision it governs, and at what altitude, in the same sentence.

**Why:** F1 (AUC > 0.70) is B2's gate on the *test* split. Applied to the B1 diagnostic rung it
would have aborted a Kaggle session on a **good** B1 of 0.66. A rule imported from another phase is
worse than none, because it carries pre-registered authority. → `03_verifying/kranz_mission_rules.md`

## ▸ An optimisation is being proposed and you cannot prove it is harmful

**Do:** say no until a measurement says otherwise. Watch specifically for the burden of proof having
flipped from *show it is safe* to *show it is unsafe*.

**Why:** pruning candidates on low policy prior and poor static evaluation was proposed as lossless.
Both halves select **against sacrifices** — a sacrifice has bad static value by construction, and
`steer_w_policy_trap` treats a low prior as a *danger signal*. The harm would have appeared months
later with every test green. → `04_failure/challenger_the_night_before.md`

## ▸ You are about to reuse something — a cache, a label, a benchmark, a component

**Do:** write down which environment made it valid, and store that record *with* the artefact.

**Why:** Ariane 5 was destroyed by proven Ariane 4 software whose range assumption was true of a
different rocket. Ours: the EPD cache is position-keyed and not budget-keyed; N1 negatives inherit
themes true only *before* the solution; motif outputs are positional against one manifest.
→ `04_failure/ariane5_reused_assumption.md`

## ▸ You are about to start a run that writes artefacts

**Do:** delete this run's target artefacts first.

**Why:** commit `33ff814` — a crashed 100-game run read a leftover 2-game `profile.json` and printed
`[DONE] games=2`. It looked like success. → `04_failure/columbia_normalization_of_deviance.md`

## ▸ A result surprises you

**Do:** re-derive the **frame** before re-running the measurement. Whose point of view, which units,
whose turn, which vehicle was the assumption true of.

**Why:** a faster loop around a wrong orientation produces confident errors sooner. Five frame
instances in six weeks here: white-POV vs mover-POV, black-to-move saliency, the value-screen sign,
the puzzle `fen` being one ply early, and Φ's meaning flipping with the side to move.
→ `04_failure/mars_climate_orbiter_frames.md`, `02_deciding/boyd_ooda_and_orientation.md`

## ▸ Thejus contradicts you

**Do:** assume your reproduction is wrong before assuming his report is. He is the ground-truth
oracle and has been right repeatedly against confident analysis.

**Why:** AECL could not reproduce the Therac-25 fault by typing carefully, and concluded an overdose
was impossible. The bug depended on operators typing *fast*. "We could not make it happen" is not
"it cannot happen". → `04_failure/therac25_reports_dismissed.md`, `01_command/marshall_dissent_upward.md`

## ▸ You are about to downgrade or reject a worker's finding

**Do:** measure it, put the measurement in the reply, and if you downgrade the same finding twice,
say so explicitly to Thejus so he can adjudicate over your head.

**Why:** the senior person is sometimes wrong and confident, and there is currently no path by which
a second challenge from Gemini reaches Thejus except through me. CRM's two-challenge rule exists for
exactly this. → `07_teams/crm_after_tenerife.md`

## ▸ You are briefing the worker

**Do:** supply the intent and the aim in Thejus's own words, name the traps with reasoning attached,
pin what it cannot determine for itself — **and nothing more**. Ask it to *enumerate every caller of
X*, never *what do you think of X*.

**Why:** Moltke — include everything the executor cannot work out alone and nothing else; over-
specification substitutes your stale picture for its fresh one. And three audits' evidence: it is
better than you at exhaustive local inspection, worse at determinism under ambiguity and at judging
severity. → `01_command/mission_command_moltke.md`, `06_building/manhattan_parallel_paths.md`

## ▸ The worker delivered something unusable

**Do:** read your own specification first. Under-specification is the leader's failure.

**Why:** the first `config_steering` build passed every gate it was given and was still separable at
AUC 0.6637 on mobility and check. The worker followed the brief exactly. I had written three alarms
that all interrogated material. → `07_teams/deming_system_not_worker.md`

## ▸ You are about to spend an irreversible or rationed resource

**Do:** classify it. Reversible → move fast and let review catch things. Irreversible **or silent** →
slow down, and write the failure account in advance.

**Why:** rigour is proportional to *blast radius × irreversibility × SILENCE*, and the third factor
is ours: a cheap reversible silent error sat in `sac_drill` for five weeks.
→ `02_deciding/one_way_and_two_way_doors.md`, `01_command/eisenhower_in_case_of_failure.md`

## ▸ You are about to report a result

**Do:** state the honest limit in the same breath. Separate *measured* from *projected* explicitly.

**Why:** Φ learns what a human in the 1500–2200 band gets wrong, not objective attacking potential.
The CNP is **4.42× worse** than the exact GP posterior and that is the correct outcome. The career
story — *found two silent bugs in my own published work and corrected them publicly* — stops being
true the moment that discipline lapses. → `08_integrity/lemessurier_citicorp.md`

## ▸ You reached a conclusion easily and nobody has argued against it

**Do:** construct the opposing case yourself, or postpone. If nobody can build one, that is
information about the process, not about the decision.

**Why:** Sloan adjourned meetings for lack of disagreement. *"The steering target is `s_err`"* was
reached in one pass and has been settled ever since; nobody has argued for `s_tac`.
→ `02_deciding/sloan_manufacture_dissent.md`

## ▸ The plan is not working

**Do:** ask what a competent stranger with no history here would do. Then separate the **aim** (never
negotiable) from the **plan** (always) and say out loud which one is dead.

**Why:** Shackleton substituted the objective on the day the ship was lost and announced it. Grove
and Moore walked out of the door and came back in. *Steer/Tal is a core aim — hone, never fold*; the
plans beneath it have already been replaced four times.
→ `05_expedition/shackleton_aim_substitution.md`, `02_deciding/grove_inflection_point.md`

## ▸ You are about to add a document, a process, or a checklist

**Do:** ask whether it can be a test, an assertion or a refusal in code instead. If it cannot, ask
whether the deadline item is open.

**Why:** *cease dependence on inspection* — a defect caught at review is one the process allowed.
And `CLAUDE.md` non-negotiable #6 exists because a registry, a ledger, an audit protocol and three
documents were built while an application sat unsent. This playbook is itself subject to the rule.
→ `07_teams/deming_system_not_worker.md`, `06_building/brooks_conceptual_integrity.md`

---

## The five-line version, for when there is no time for any of this

1. `grep` it. Run it. Time it.
2. The rule was written for a reason — obey it the first time it hurts.
3. Go and look at the object.
4. Kill the plan, never the aim.
5. Say the honest limit in the same breath as the result.
