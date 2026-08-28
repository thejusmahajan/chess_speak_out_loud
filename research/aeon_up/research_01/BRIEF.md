# AEON-UP interview — verify seven external facts

> ⚠ **STALLED 2026-08-28 — SUPERSEDED. Do not paste this into Deep Research.**
> Gemini Deep Research takes a short *goal*, proposes a plan, browses, and returns a sourced
> report. This is a 335-line scope contract written for an agent that reads instructions, and
> the tool did not know what to do with it. The live route is **`../research_02/`** — four
> short self-contained prompts, nothing attached. The seven targets below are unchanged and
> still authoritative; only the machinery around them was wrong. Kept as the record of what
> was tried.

**Round:** research_01 · filed 2026-08-28
**Worker:** external web-based deep-research agent (no filesystem access)
**Companion:** four background files are attached alongside this prompt — see §0.4

> This is the web-upload version of `agents/briefs/2026-08-28_aeon-up-external-facts.md`, which is
> the registered brief in this repo's ledger. Same seven targets; the input and output sections
> differ because the worker here cannot read or write local files.

---

## 0. Read this before you search for anything

### 0.1 What this task is, and what it is emphatically not

**You are verifying seven specific external facts. You are not researching the job.**

The application for this position was **already submitted and confirmed sent on 2026-08-27**. The
CV and the cover letter are frozen PDFs in the employer's hands. A study room of 22 files and
roughly 3,400 lines already exists, covering the domain, the methods, the uncertainty theory, 20+
prepared interview answers, a talk script, and the honesty boundaries. Four of those files are
attached to this prompt.

Therefore the following are **out of scope and must not be attempted**:

- ❌ Extracting or summarising the job advert. It is already extracted.
- ❌ General research on Helmholtz-Zentrum Hereon, its locations, or its institutes. Already done.
- ❌ General research on "probabilistic deep learning for urban air quality" as a field. Already
  done — see the attached `4_domain.md`.
- ❌ **Any recommendation about the CV or the cover letter.** They are sent. They cannot change.
  Advice here is worse than useless: it invites re-litigating a closed decision.
- ❌ Writing interview questions. There are already 20+ prepared, and 51 flashcards in a trainer.
  You are not adding to them.
- ❌ Summarising the attached files back. They are context so that you do not re-research what is
  already known — they are not material to be digested and returned.

If you find yourself writing a paragraph that summarises something back, **stop** — you have
drifted out of scope.

### 0.2 The standing contract

Three rules, and they are not boilerplate:

- **Never invent a citation, a number, a date, or a quotation.** This project has **four
  fabricated deliveries on record**. Three occurred when a worker was asked for *content* rather
  than for *code*. One delivery on this very application carried **two fabricated citations** —
  Cabaneros (attributed to *Environmental Pollution* 254; the real paper is in *Environmental
  Modelling & Software* 119) and Andersson (given as arXiv:2305.15340; the real identifier is
  arXiv:2211.10381). Both survived into a study-room file and were caught months later by accident.
- **Every fact returns with a URL and a verbatim quotation.** Not a paraphrase. Not "according to".
  The exact sentence you read, in quotation marks, with the link it came from.
- **Report sources, never conclusions.** You are a retrieval instrument for this task. Do not
  synthesise, do not advise, do not judge whether a fact is good news.

### 0.3 ⚑ The UNVERIFIED rule — the single most important instruction here

For every one of the seven targets, exactly one of two things is true when you finish:

1. **VERIFIED** — you have a URL and a verbatim quotation, and you paste both.
2. **UNVERIFIED** — you could not find it, or the sources disagree, or the page you found is not
   authoritative. **You write the word UNVERIFIED and you stop.**

**An UNVERIFIED answer is a complete success.** It is exactly as valuable as a verified one,
because the person using this report will be saying these things out loud to the people who wrote
the underlying papers. A fact marked UNVERIFIED gets left out of the conversation, costing nothing.
A fact you guessed at, and got wrong, gets said to its own author.

**Never fill a gap with a plausible reconstruction.** If the exact title of a paper eludes you, do
not assemble one from the words you saw. If a pay figure is not on an authoritative table, do not
compute one from a news article. **Do not soften an unknown with "likely", "appears to be",
"approximately", or "around"** — those are the words that turn a gap into a false fact.

### 0.4 The four attached files, and why you get exactly these

| file | why you get it |
|---|---|
| `1_karl_and_ufp.md` | carries the ⚠ on R1; tells you what is already known about Dr. Karl |
| `2_salary_and_conditions.md` | the TVöD framing R2 must not contradict |
| `3_do_not_claim.md` | five honesty boundaries; nothing you return may tempt him across one |
| `4_domain.md` | the physics is already covered — do not re-research it |

**You are deliberately not given the other 18 study-room files.** If you read them you will
summarise them back, which is the failure this brief is written to avoid.

### 0.5 Output

Return **one markdown document** as your response, in the format given in §8 below. Nothing else —
no cover note, no summary of what you did, no offer of further work.

The document will be saved by hand into this round's `report/` directory and audited line by line.

### 0.6 Stop-and-ask

Anything this brief does not cover, say so in the report rather than improvising scope.

---

## The seven targets

Each gives you: what is already known, what is missing, and precisely what to return.

---

### R1 — the exact citation of Dr. Matthias Karl's ultrafine-particle paper

**⚑ This is the highest-value target in the brief. Do it first.**

**Known.** The attached `1_karl_and_ufp.md` records the title as *"City Scale Modeling of Ultrafine
Particles in Urban Areas"* and flags it explicitly as unverified. It also records one
**already-verified** citation, which you may use as a cross-check that you have the right person:

> Karl et al. (2019), *Geoscientific Model Development* **12**, 3357–3389,
> doi:10.5194/gmd-12-3357-2019 — the EPISODE-CityChem Part 2 Hamburg application.

Dr. Matthias Karl is at Helmholtz-Zentrum Hereon, Institute of Coastal Environmental Chemistry.

**Missing.** The exact title, the year, the venue, the DOI, and the author position.

**Why it matters.** He may name this paper to its own author in the interview. The instruction in
the study room is blunt: *"naming a paper wrongly to its author is worse than not naming it."*

**Return:**
1. The full citation as it appears on an authoritative source — the publisher's page, the DOI
   resolver, or Hereon's own publication listing. Not Google Scholar's rendering, not ResearchGate.
2. The URL.
3. A verbatim quotation of the title line as displayed on that page.
4. Whether Karl is first author, and the full author list.
5. **If several UFP papers by Karl exist, list them all** rather than choosing one. Choosing is not
   your job.
6. If no paper matching that title exists — say so plainly. **That is a valuable finding, not a
   failure.** It would mean the title currently in the study room is wrong and must be struck.

---

### R2 — the TVöD Bund pay table in force for 2026, entry group E13

**Known.** The post is advertised at **E13**. The attached `2_salary_and_conditions.md` establishes
the frame: the group is fixed and not negotiable; the *Stufe* (step) within it is what gets
assigned, from recognised *einschlägige Berufserfahrung*. Helmholtz centres pay **TVöD Bund**.

**Missing — and deliberately so.** That file quotes **no figures anywhere**, on purpose, because
none had been verified. This target supplies them.

**Return:**
1. The **monthly gross** for **E13, steps 1 through 6**, under the TVöD **Bund** table in force in
   2026. Not TVöD VKA, not TV-L — those are different tables, and using the wrong one produces a
   wrong number that sounds authoritative.
2. The **effective date** of that table and the collective agreement (*Tarifvertrag*) it comes
   from. If a new table takes effect partway through 2026, give both and say which applies when.
3. The **Jahressonderzahlung** rate applicable to E13 at Bund level, as a percentage, with source.
4. The URL for each, preferring an official or union source (BMI, ver.di, or the published
   *Tarifvertrag* text) over a salary-calculator site.
5. A verbatim quotation of the E13 row, or a clear statement of how you read the table.

**Failure mode to avoid:** salary-comparison and calculator websites carry stale or regionally
mixed tables and present them confidently. If your only source is such a site, mark it
**UNVERIFIED** and name the site.

---

### R3 — what both principal investigators have published since January 2024

**Known.** Dr. Matthias Karl — EPISODE-CityChem, aerosol dynamics, chemistry, dispersion, exposure;
**no published machine-learning track record**. Dr. Martin Ramacher — regional and urban emission
inventories (UrbEm, CMAQ), exposure modelling; mentored ECMWF Code4Earth **Challenge 34** with
**Johannes Bieser**, using the **CAMS European Air Quality Reanalysis**, producing *Urban Air
Quality View*. Both at Helmholtz-Zentrum Hereon, Institute of Coastal Environmental Chemistry.

**Missing.** Everything after roughly the start of 2024.

**Return, for each of the two separately:**
1. Publications and preprints from **2024-01-01 to today**, with title, venue, year and DOI, from
   an authoritative listing (Hereon's publication database, ORCID, or the publisher).
2. For each, **one verbatim sentence from the abstract** — enough to tell what it is about.
3. ⚑ **Flag explicitly any paper involving machine learning, statistical emulation, data
   assimilation, or uncertainty quantification.** If Karl has now published something using ML,
   that materially changes how one talks to him, and it is the single most useful thing you could
   return under this target.
4. Any **new** project, consortium, or software release either is publicly associated with.

**Do not** characterise their research direction, speculate about their interests, or infer what
they want in a candidate. List what they published.

---

### R4 — AEON-UP as a funded entity

**Known.** Almost nothing beyond the advert. The description in circulation — probabilistic deep
learning for calibrated high-resolution urban air-quality fields — is inferred from the job posting
itself, not from any project documentation.

**Missing.** Whether AEON-UP exists publicly as a named, funded project at all.

**Return:**
1. Is there a public project page, grant record, or funding-database entry for AEON-UP? URL if so.
2. The **funder** and **programme**, if identifiable (BMBF, DFG, Helmholtz internal, EU/Horizon).
3. The **partners or consortium members**, if any.
4. The **project period**, and whether the advertised two-year post sits inside it.
5. What the acronym expands to, **if and only if a source states it.** Do not construct an
   expansion from the letters. A guessed expansion said aloud in the interview is difficult to
   recover from.
6. If nothing public exists — **say so in one line.** That is a genuine and useful finding: it
   means the project is internal, which makes *"how much of this starts from Code4Earth?"* a better
   question than it already was.

---

### R5 — what a first-round interview at a Helmholtz centre actually looks like

**Known.** The talk script assumes a presentation is likely and instructs him to establish the
format by email in advance. That assumption is currently unsourced.

**Return, each with a source:**
1. Is a candidate presentation standard for a postdoc-level scientific post at a Helmholtz centre,
   and if so what length is typical?
2. **Who normally sits on the panel** for a German public-sector research post. Specifically: does
   HR attend; is a **Betriebsrat / Personalrat** representative present; is a
   *Gleichstellungsbeauftragte* (equal opportunity officer) or *Schwerbehindertenvertretung*
   representative normally present? This is standard practice in the German public sector and is
   worth knowing before walking into a room with more people in it than expected.
3. Is a **second round** typical before an offer?
4. At what stage is the **Stufe** normally settled — with the panel, or with HR after an offer?
   The attached `2_salary_and_conditions.md` asserts the latter. **Verify or contradict it.** If it
   is wrong, that is a correction needed before the interview, not after.
5. Anything Hereon publishes specifically about its own hiring process.

Prefer official sources — Helmholtz or Hereon careers pages, public-sector guidance — over
candidate forums. Where you use a forum, label it as such.

---

### R6 — who else is doing probabilistic deep learning for urban air quality

**Known.** The attached `4_domain.md` covers the methods. **Do not re-cover them.**

**Missing.** The current landscape — named groups and recent papers, so that *"what do you see as
the state of the art?"* does not land cold.

**Return, and keep it tight — 6 to 10 items, not a literature review:**
1. Recent work (**2023 onward**) combining chemistry-transport-model output with learned models to
   produce **calibrated, uncertainty-aware** urban air-quality fields. Title, authors, venue, year,
   DOI.
2. Specifically: any application of **neural processes, deep kernel learning, Gaussian-process
   hybrids or deep ensembles** to air quality, or to spatial environmental fields with sparse
   sensors.
3. Any work using **leave-one-station-out** validation for air-quality models — he intends to
   propose exactly this, and knowing whether it is standard or unusual in this community changes
   how he pitches it.
4. Any European operational effort at high-resolution urban air quality with uncertainty.

For each: **one verbatim sentence from the abstract**, and the DOI. No commentary.

---

### R7 — the current regulatory status of ultrafine particles

**Known**, from the attached `1_karl_and_ufp.md`. Each item needs confirming or correcting:

- Directive **2008/50/EC** sets limits for PM10 (40 µg/m³ annual) and PM2.5.
- The **revised AAQD, agreed in 2024**, mandates UFP **monitoring at supersites** but sets **no
  numerical limit value**.
- **WHO 2021** guidelines give UFP **"Good Practice Statements"**, not a guideline value.

**Return:**
1. The **formal identifier of the revised AAQD** — directive number and date of adoption or entry
   into force. Confirm it is adopted rather than merely agreed, and give the transposition
   deadline.
2. A **verbatim quotation** of the provision covering ultrafine particles / particle number
   concentration at monitoring supersites.
3. **Confirm or correct** that no binding numerical limit value for UFP exists in it.
4. A **verbatim quotation** of the WHO 2021 Good Practice Statement wording for UFP.
5. Any change since 2024 to any of the above.

**This is the factual base of his strongest argument** — that with no limit and almost no
monitoring, the model's own uncertainty does the work a monitoring station would otherwise do. If
any of it is wrong, the argument has to be rebuilt before the interview rather than discovered
mid-sentence.

---

## 8. Output format

Use exactly this structure, once per target, R1 through R7:

```markdown
## R1 — Karl's UFP paper

**Status:** VERIFIED | UNVERIFIED | PARTIALLY VERIFIED

**Finding:**
<the fact, stated flatly, in as few lines as it takes>

**Source:** <URL>
**Verbatim:** "<the exact sentence from that page>"

**Notes:** <only genuine caveats — conflicting sources, ambiguity, an
authoritative page that was unreachable. Not commentary.>
```

Then close with:

```markdown
## Summary table

| target | status | one-line finding |
|---|---|---|
| R1 | VERIFIED | ... |
| R2 | UNVERIFIED | ... |
```

---

## 9. ✅ Checkpoint — answer these seven in the report itself, in a final section

1. Did you write **any** recommendation about the CV or cover letter? **If yes, delete it.**
2. Does **every** VERIFIED finding carry both a URL and a verbatim quotation in quotation marks?
3. Is every fact you could not confirm marked **UNVERIFIED** — rather than softened with "likely",
   "appears to be", or "approximately"?
4. For R2: is your table **TVöD Bund**, and did you state its effective date?
5. For R1: if multiple candidate papers exist, did you list **all** of them rather than choosing?
6. Did you summarise any attached file back instead of using it as context?
7. Which targets did you run out of budget on, if any? Say so plainly rather than thinning the
   evidence to cover all seven.

---

## 10. What happens to this report

Every citation is audited independently — each DOI resolved, each quotation re-fetched against its
source. Two fabricated citations reached a study-room file on this exact application once already
and were caught months later.

Whatever survives that audit becomes flashcards in a spaced-repetition trainer, which is at 51
cards on this interview and is the thing actually being rehearsed.
