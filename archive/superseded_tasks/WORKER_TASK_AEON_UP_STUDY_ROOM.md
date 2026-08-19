# WORKER TASK — Build the AEON-UP Study Room

Build a single, self-contained study and interview-preparation system for the
Hereon AEON-UP postdoctoral application. When it is finished, Thejus should be
able to prepare entirely from inside one directory and never need to search
elsewhere for background, method, or practice questions.

Everything you need to ground it is in §1. **Read all of §1 before writing a
word.** It is not context; it is the specification, and most of it was verified
against primary sources rather than assumed.

---

## 1. GROUND TRUTH — do not contradict any of this

### 1.1 The position

| | |
|---|---|
| Title | Postdoctoral Researcher — Probabilistic Deep Learning for Urban Air Quality (AEON-UP) |
| Institute | Helmholtz-Zentrum Hereon, Institut für Umweltchemie des Küstenraumes, Geesthacht |
| PIs | **Dr. Martin Ramacher** (named contact) and **Dr. Matthias Karl** |
| Reference | **Two different numbers are in circulation: `1056` (from the posting URL) and `030358` (from a research report). FLAG THIS as an open item for Thejus to confirm on the posting. Do not silently pick one.** |
| Deadline | 3 September 2026 |
| Term | Start 1 October 2026, two years to 30 September 2028, TVöD E13 |
| Goal | Fuse physics-based chemistry transport models with probabilistic deep learning — **neural processes** — to predict NO₂, PM and **ultrafine particles** across European cities, **with uncertainty estimates** |
| Required | PhD in ML, CS, Physics or Environmental Sciences; deep learning framework experience (e.g. PyTorch); strong Python |
| Desired | Probabilistic/Bayesian methods; spatio-temporal or geospatial data; HPC |

### 1.2 Verified findings about the group

These were checked against primary sources. Treat them as fact.

- **Dr. Matthias Karl** is in Hereon's Chemistry Transport Modelling department. He
  is associated with **EPISODE-CityChem** — the Hereon-developed urban-scale
  extension of the EPISODE dispersion model for reactive pollutants. He has
  published *City Scale Modeling of Ultrafine Particles in Urban Areas*. His
  interests are aerosol transformation and dispersion, urban-scale CTMs, and
  exposure/health effects. **No published machine learning was found.**
- **Dr. Martin Ramacher** publishes primarily deterministic, physics-based CTM
  work (CMAQ at regional scale, emission inventories, UrbEm). **One clear turn
  toward ML:** he mentored **"Urban Air Quality View"**, an ECMWF *Code for Earth*
  2024 project that downscales regional CAMS products to urban scale with a
  learned model instead of more expensive simulation — inputs are regional
  concentrations plus measurements and land use.
- **Strategic consequence, and the spine of the whole preparation:** the group is
  hiring a capability it does not yet have in depth. Thejus is not competing to
  out-publish ML researchers; he is offering to be the person who can build the
  learned half *inside* a physics-based modelling group.
- **CMAQ is the regional model; EPISODE-CityChem is the urban one.** AEON-UP is
  urban. Prefer EPISODE-CityChem when discussing the physics side.

### 1.3 The one conceptual trap — state it prominently and early

**"Neural processes" has nothing whatsoever to do with interpreting neural
networks, attention mechanisms, or mechanistic interpretability.** A Neural
Process is a probabilistic model that combines the uncertainty quantification of
a Gaussian Process with the scalability of a neural network. Any hint of
conflating the two in an interview would be disqualifying. The study room must
make this impossible to get wrong.

### 1.4 Thejus' actual background — ground every answer in this and nothing else

- PhD astrochemistry (Université Paris-Saclay): terabytes of particle-accelerator
  data, C++ optimisation of noise-suppression and signal-smoothing, molecular
  fragmentation model contributing to the KIDA database.
- Post-doc (Universität Hamburg): "Cyanobacteria Life Cycle" model inside the
  **ERGOM** framework; hindcast and projection runs for warming scenarios; daily
  work with gridded **NetCDF** on **Linux HPC**; translated a legacy **Fortran**
  engine to **Python/Google JAX** with TPU/GPU parallelisation.
- **Guest scientist at Hereon**, May–October 2025, ecosystem modelling.
- Weiterbildung in bioinformatics and biostatistics; HealthTwiSt Praxisphase —
  refactored a production R/tidyverse pipeline for a national medical registry
  (143,000+ records, ~300 clinics), verified byte-identical at every step,
  externalised 257 hard-coded rules into configuration, built an R package and a
  Shiny dashboard, found two pre-existing bugs and escalated rather than silently
  fixing them.
- **Independent ML research (2026–present):** built and debugged a PyTorch
  pipeline around a 15-layer transformer — ONNX→PyTorch conversion, forward
  hooks capturing internal representations, batched GPU/CPU inference, async
  engine orchestration. **Found two systematic errors in his own analysis
  pipeline**, both producing smooth plausible output that raised no exception and
  failed no test; one had already reached a published write-up, and he corrected
  it publicly.
- HPC training at the **Jülich Supercomputing Centre**; confirmed place on
  *Deployable Data Analysis & AI Pipelines with HPC*, **Supercomputing-Akademie,
  HLRS**, 6 Sept – 7 Oct 2026.
- German B1 (Goethe), B2 in preparation. English C1. Work authorisation for
  Germany. Lives in Hamburg.

### 1.5 What he must NOT claim — reproduce this as a card in the study room

- ❌ Published work in Bayesian deep learning or neural processes. He has reading
  and (soon) his own implementation. That is what he may say.
- ❌ Causal interventions, activation patching, or circuit discovery. He captures
  and reads activations; he has not ablated or patched.
- ❌ Experience with CMAQ, EPISODE-CityChem, or any atmospheric chemistry model.
- ❌ Air quality domain experience. He has *environmental* modelling.
- ❌ Anything resting on the "sacrifice/Tal" metric from his chess project — it is
  documented in that repository as unsound.

### 1.6 Existing material to build on, not duplicate

`STUDY_BOOK.md` already exists in this application folder and covers the
GP→CNP→NP→ANP lineage, aleatoric vs epistemic uncertainty, CRPS and calibration,
and a first domain briefing. **Extend and reorganise it into the study room;
do not rewrite what is already correct there.**

### 1.7 How he learns — this determines the format

From an extended documented study dialogue: he wants **first principles, small
chunks, plain readable text, concrete worked examples, and no unrendered LaTeX**.
He rejected LaTeX-in-chat explicitly. He learns by asking follow-up questions
until a mechanism is fully grounded, then wants it written down. Formulas must
be plain-text and hand-checkable. Diagrams should be ASCII/Unicode where they
help.

---

## 2. WHAT TO BUILD

Everything goes in `applications/hereon_aeon_up/study_room/` in the `job_search`
repository. Markdown throughout.

```
study_room/
    00_START_HERE.md          the door: what to read, in what order, with time budget
    01_domain.md              air quality, CTMs, EPISODE-CityChem, UFP
    02_methods.md             GP -> CNP -> NP -> ANP -> ConvCNP
    03_uncertainty.md         aleatoric/epistemic, CRPS, calibration, evaluation
    04_the_bridge.md          his background mapped to their needs, claim by claim
    05_interview_questions.md the question bank (see §3)
    06_do_not_claim.md        the card from §1.5
    07_flashcards.md          spaced-repetition items, question on one line, answer on the next
    08_study_plan.md          a dated plan from today to the interview
```

### Content requirements per file

**00_START_HERE.md** — a genuine index. What each file is for, the order to read
them, and an honest time estimate per file. Must open with the §1.3 trap.

**01_domain.md** — enough atmospheric science to hold a conversation, not a
textbook. What a CTM does; what **EPISODE-CityChem** is and why it exists;
why NO₂ has sharp gradients and PM is smoother; what makes **ultrafine particles**
distinctive (number not mass, short-lived, sparsely monitored — and check whether
they are covered by EU limit values); boundary-layer height and inversions; the
resolution gap between a CTM cell and a street canyon. Cite sources.

**02_methods.md** — the lineage, building on `STUDY_BOOK.md`. Why a GP is the
classical answer and why O(n³) and kernel choice defeat it here. CNP, NP, ANP —
including the underfitting argument that motivated attention. **ConvCNP in
detail**, because it is the closest published analogue to this job:
*Convolutional conditional neural processes for local climate downscaling*,
arXiv 2101.07950 — read it, summarise it properly, and explain why translation
equivariance matters for gridded data. Include a **plain-text walkthrough of the
CNP forward pass**: encoder, aggregation, decoder, and the context/target split
that makes training meta-learning.

**03_uncertainty.md** — extend what `STUDY_BOOK.md` has. Aleatoric vs epistemic
with the *operational* consequence (one argues for placing a sensor, the other
does not). How each is obtained: deep ensembles, MC dropout, Bayesian NNs,
heteroscedastic regression. Evaluation: CRPS, proper scoring rules, reliability
diagrams, **sharpness subject to calibration**, and **leave-one-station-out
rather than random cross-validation** — explain the spatial-leakage trap.

**04_the_bridge.md** — the most important file. A table mapping each element of
his background (§1.4) to a specific demand of the role, with a one-sentence
statement he could actually say aloud. Every row must be defensible from §1.4.
**No row may overstate.** Include the AEON-UP framing that his own project
mirrors: sparse observations → interpolate a field → state the uncertainty →
prove it with calibration.

**08_study_plan.md** — a dated plan. Note that the HLRS course runs 6 Sept –
7 Oct and is 80% online, so it overlaps the likely interview window.

---

## 3. THE INTERVIEW QUESTION BANK — `05_interview_questions.md`

**At least 15 questions**, arranged from basic to complex, in five bands. For
each: the question, what the interviewer is really testing, a **model answer in
his voice grounded strictly in §1.4**, and a note on what would make the answer
fail.

**Band A — Foundational (3+)**
Example territory: what is a neural process and how does it differ from a
Gaussian process; what do the value/policy of "uncertainty" mean here; what is a
chemistry transport model.

**Band B — Method (4+)**
Why an NP rather than a GP, a CNN, or plain kriging; what the context/target
split is and why training is meta-learning; why ConvCNP suits gridded data;
aleatoric versus epistemic and why the distinction has operational consequences.

**Band C — Applied and design (4+)**
How would you couple a CTM with a learned model — bias correction, emulation, or
fusion, and which you would try first and why; how would you evaluate whether
the uncertainty is trustworthy; how would you cross-validate spatially; what
would you do about a city with only three monitoring stations; how would you
handle the fact that NO₂ is sharp and PM is smooth in the same model.

**Band D — Behavioural (2+)**
Tell me about a difficult bug — the two silent errors, told properly, including
that he corrected a published result. Why you are moving from ecosystem
modelling to this.

**Band E — The hard ones (2+)**
These decide the interview and must be answered without flinching:
- *"You have no publications in machine learning. Why should we take you over
  someone who does?"*
- *"Your German is B1."*
- *"Your PhD is in astrochemistry and your postdoc in marine ecosystems. This is
  atmospheric chemistry and deep learning. Why you?"*
- *"What do you not know that you would need to learn?"* — the answer must be
  honest and specific, not a disguised strength.

Also include a short list of **questions he should ask them**, which should
reveal that he understands the project: whether the NP is being trained on CTM
output, observations, or both; what the target resolution is; whether uncertainty
is expected to inform sensor placement; how EPISODE-CityChem output would feed
the learned model.

---

## 4. RULES

1. **Never invent experience.** Every model answer draws only on §1.4. If a
   question cannot be answered honestly from his background, say so in the
   answer note and give him an honest deflection instead of a fabrication.
2. **Cite sources** for factual claims about the domain, the group, or the
   methods. Mark anything uncertain as `[unverified]`.
3. **Plain text formulas.** No unrendered LaTeX. He rejected it explicitly.
4. **Do not contradict §1.** If you find evidence that something in §1 is wrong,
   **STOP and report it** rather than quietly writing something different.
5. Keep the reference-number discrepancy visible as an open item.

---

## 5. DELIVERABLE

Write `STUDY_ROOM_REPORT.md` in the same folder:

1. Every file created, with word count and the reading time you claim for it.
2. A list of every source cited, with URL.
3. The full question list — just the questions — so it can be reviewed at a
   glance.
4. Every point where you could not ground an answer in §1.4, and what you did.
5. Anything in §1 you believe is wrong, with evidence.

**STOP. Do not edit the CV or the cover letter. Do not push.**

---

## Anti-patterns that will fail review

- A model answer claiming experience he does not have. This is the one failure
  that could cost him the job in the room.
- Treating "neural processes" as related to interpretability anywhere.
- Rewriting `STUDY_BOOK.md` content instead of building on it.
- Fewer than 15 questions, or a bank that avoids Band E because it is
  uncomfortable.
- Padding the domain file into a textbook. It should be readable in one sitting.
- Any factual claim about Ramacher or Karl beyond §1.2 without a source.
