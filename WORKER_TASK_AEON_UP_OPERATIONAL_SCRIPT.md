# WORKER TASK — The AEON-UP Operational Script (depth and breadth)

Build the document that lets Thejus walk into an interview and describe **the job
itself** — what the work would actually consist of, in what order, with what
decisions, in the field's own vocabulary — and answer "how would you go about
this?" without hesitating.

The study room already covers *what the methods are*. This covers *what the work
is*. Do not repeat the study room; extend past it.

---

## 0. ORIENTATION — read before anything else

### Where things live

The study room was written into the wrong repository and has been **moved**. It
now lives at:

```
job_search/applications/hereon_aeon_up/study_room/
    00_START_HERE.md  01_domain.md  02_methods.md  03_uncertainty.md
    04_the_bridge.md  05_interview_questions.md  06_do_not_claim.md
    07_flashcards.md  08_study_plan.md
```

Your output goes in the **same folder**, as `09_operational_script.md` plus the
supporting files named in §3. Write into `job_search`, not the chess repository.

### Corrections already applied — do not reintroduce them

The study room's model answers were edited because they asserted knowledge that
does not exist. These specific claims were **removed and must not return**:

- Any claim to have implemented CNP or **ConvCNP**. He has read; he has not yet
  trained one.
- Specific parameterisations attributed to Dr. Karl (coagulation kernels, SOA
  volatility basis sets). Unverified, and he would be saying them *to Karl*.
- "basic NOx photochemistry" — not in his background.
- Understanding **EPISODE-CityChem** output "from day one" — never used it.
- **Helmholtz Munich** as a project partner — unverified.
- "HLRS fellowship" (it is a paid course place) and "publicly retracted" (he
  corrected a write-up; retraction is a term of art).

**The rule this establishes:** a vague honest answer beats a specific invented
one, because every specific invites a follow-up. Read
`study_room/06_do_not_claim.md` before writing a single answer.

### Ground truth

`WORKER_TASK_AEON_UP_STUDY_ROOM.md` §1 in the chess repository holds the verified
position facts, the findings about Ramacher and Karl, and Thejus' exact
background. **Treat it as the specification.** Corrections since: the reference
is **`1056 - 2026/KU 2`**, and the posting **names no contact** — it lists
Ramacher (machine learning focus) and Karl (urban air quality modelling).

---

## 1. THE LITERATURE FOUNDATION

Read these properly — not abstracts. For each produce a structured card:

```
Paper | Authors, year, venue, DOI/arXiv
Problem:      what was actually broken before this paper
Method:       what they did, in plain terms
Result:       what it achieved, with the numbers they report
Limitation:   what the authors themselves admit it cannot do
For AEON-UP:  what this implies for the project - one paragraph
Terms introduced: the vocabulary this paper puts in play
```

**Required core (read fully):**
1. Vaughan et al., *Convolutional conditional neural processes for local climate downscaling* — arXiv 2101.07950. **This is the closest published analogue to the job. Give it the longest card.**
2. Garnelo et al. 2018, *Conditional Neural Processes*.
3. Garnelo et al. 2018, *Neural Processes*.
4. Kim et al. 2019, *Attentive Neural Processes* — cover the underfitting argument.
5. Gordon et al. 2020, *Convolutional Conditional Neural Processes*.
6. Kendall & Gal 2017, *What Uncertainties Do We Need in Bayesian Deep Learning?*
7. Lakshminarayanan et al. 2017, *Deep Ensembles*.
8. Gneiting & Raftery 2007, *Strictly Proper Scoring Rules* — CRPS and propriety.

**Required domain (read fully):**
9. The **EPISODE-CityChem** model description paper (Karl et al., Geoscientific
   Model Development). Find it and cite it exactly.
10. Karl et al., *City Scale Modeling of Ultrafine Particles in Urban Areas*.
11. One Ramacher paper on urban emissions or downscaling (**UrbEm** is a good
    candidate).
12. One review of machine learning for air quality — and one paper on
    **land-use regression**, which is the classical baseline any ML method is
    measured against.

**Then find, yourself, 3–5 more** that matter and say why you chose them. Good
territory: physics-informed ML for atmospheric transport, emulation of CTMs,
spatial cross-validation methodology, uncertainty calibration for geospatial
prediction.

**Every reference must resolve.** Check each DOI or arXiv ID. A fabricated
citation in interview preparation is worse than no citation, because he will
repeat it aloud.

---

## 2. THE BOTTLENECKS

The most valuable section. What actually blocks progress in high-resolution
urban air quality prediction? For each: what the obstacle is, why it is hard,
what has been tried, what remains open, and **how AEON-UP appears to be
attacking it** (marking that last part as inference where it is inference).

Cover at least:

- **Spatial sparsity.** Monitoring stations are few and non-randomly placed —
  they sit where regulators expect exceedances. What does that do to a model
  trained on them?
- **The resolution gap.** A CTM cell is kilometres; exposure varies over metres.
  Downscaling, emulation, and fusion as the three responses.
- **Non-stationarity.** The relationship between predictors and concentration is
  not constant across a city — roadside is not background. What breaks when a
  model assumes stationarity, and how do attention or convolutional structure
  help?
- **Computational cost.** Why running a CTM at street resolution across European
  cities is infeasible, and what a learned surrogate buys.
- **Transferability.** A model trained on one city applied to another — what
  fails, and why meta-learning over tasks is the natural framing.
- **Evaluation.** Why random cross-validation is misleading under spatial
  correlation, and what leave-one-station-out and blocked CV do about it.
- **Ultrafine particles specifically.** Sparse monitoring, no mass-based
  regulatory anchor, short atmospheric lifetime.

---

## 3. THE OPERATIONAL SCRIPT — the core deliverable

`09_operational_script.md`. A phased walkthrough of the actual job, written so he
can talk through it fluently.

Structure it as **five phases** covering roughly the first year:

For **each** phase give:
- **The objective** in one sentence.
- **What you would actually do** — concrete steps, named tools, data formats.
- **The decisions you would face**, each with the options and the trade-off. Not
  a single recommended answer: the interviewer wants to hear him reason.
- **The technical terms in play**, each defined in one line, plain language.
- **What could go wrong** and how it would show up.
- **What he would need to ask the group**, because it genuinely depends on
  choices they have already made.

Suggested phases, adjust if the literature suggests better:
1. Data assembly and audit — CTM output, station observations, covariates
   (land use, road density, population, meteorology, satellite NO₂); alignment,
   projection, resolution, gaps.
2. Baselines before anything clever — land-use regression, interpolation,
   raw CTM. What you must beat and why you establish it first.
3. First model — a CNP or ConvCNP on this data; context/target construction;
   what a "task" is when the data is a city-day.
4. Uncertainty and calibration — separating aleatoric from epistemic; reliability
   diagrams; CRPS; leave-one-station-out.
5. Coupling to the physics and transferring across cities — CTM as prior, as
   covariate, or as training target; what changes when the model moves to an
   unseen city.

**Tone:** he is describing how he would approach it, not asserting how it will
be done. Phrases like "I would start by…", "the trade-off there is…", "that
depends on whether you are…" are correct. Confident assertions about their
project are not.

---

## 4. THE "HOW WOULD YOU" BANK

`10_how_would_you.md`. **At least 12 scenario questions**, distinct from the
existing question bank in `05_interview_questions.md` — those test knowledge,
these test approach.

Format for each:

```
The question
What they are really probing
How to open (the first sentence out of his mouth)
The reasoning, step by step
The trade-off he should name explicitly
What he should ask back before committing
How this could go wrong if he over-commits
```

Territory to cover:
- A city has three monitoring stations. How would you proceed?
- Your model is well calibrated overall but overconfident near roads. Diagnose it.
- How would you decide between a CTM emulator and a bias-correction model?
- The CTM and the observations disagree systematically. What do you do?
- How would you validate that this transfers to a city not in training?
- You have one month of GPU budget. What do you run first?
- How would you show a municipal agency that the uncertainty means something?
- Your NP underfits and the predictions are too smooth. What do you try?
- How would you incorporate meteorology?
- How would you handle a station that goes offline for three months?
- The reviewer says a simpler model does just as well. How do you respond?
- How would you use the uncertainty to recommend where to put a new sensor?

---

## 5. THE GLOSSARY

`11_glossary.md`. Every technical term appearing anywhere in the study room or
your new files, defined in **one or two plain sentences**, grouped by area
(atmospheric, statistical, ML, HPC). He should be able to skim it the morning of
the interview and have nothing land unfamiliar.

Mark terms he should be able to *use* differently from terms he only needs to
*recognise*.

---

## 6. DELIVERABLE

`OPERATIONAL_SCRIPT_REPORT.md` in the application folder:

1. Files created, with word counts.
2. The full reference list, each with a resolved link **and confirmation you
   checked it resolves**.
3. The list of "how would you" questions, questions only, for review at a glance.
4. Every place you had to infer rather than cite, listed explicitly.
5. Anything in the ground truth you believe is wrong, with evidence.

**STOP. Do not edit the CV, the cover letter, or files 00–08 of the study room.
Do not push.**

---

## Anti-patterns that will fail review

- **Any claim that he has done something he has not.** This is the failure that
  was already corrected once. It will not be tolerated twice.
- Technical specifics invented to sound expert — the coagulation-kernel failure.
  If you do not have a source, write the honest general version.
- A citation that does not resolve.
- Answering "how would you" with a single confident plan and no trade-off. The
  interviewers are researchers; they want reasoning, and a candidate who sees
  only one option looks junior.
- Repeating the study room's method explanations instead of building past them.
- Naming a tool, model, or partner not established in the ground truth.
