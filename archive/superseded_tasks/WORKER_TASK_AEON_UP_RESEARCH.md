# WORKER TASK — Research report on the AEON-UP group's work

Produce a grounded research report on the two principal investigators of the
Hereon AEON-UP postdoc position, so that a job application can refer to their
actual work rather than to generalities.

**This is a research and citation task. Accuracy is the entire deliverable.**
The output feeds a job application; a confident wrong statement about someone's
research is worse than saying nothing. Every factual claim must carry a source
URL. Where you cannot find a source, write **"not found"** — that is a valid and
useful answer, and it is far better than an inference presented as fact.

**Do not speculate.** Do not write "they likely use..." or "their work probably
involves...". If it is not in a paper, an institutional page, or a project page,
it does not go in the report as fact. There is a clearly marked section at the
end for inference, and inference goes only there.

---

## The subjects

| | |
|---|---|
| **Position** | Postdoctoral Researcher — Probabilistic Deep Learning for Urban Air Quality (AEON-UP), ref. 1056 |
| **Institute** | Helmholtz-Zentrum Hereon, Institut für Umweltchemie des Küstenraumes (Institute of Coastal Environmental Chemistry), Geesthacht |
| **PIs** | **Dr. Martin Ramacher** and **Dr. Matthias Karl** |
| **Posting** | https://jobs2.hereon.de/default/job/Postdoctoral-Researcher-Probabilistic-Deep-Learning-for-Urban-Air-Quality-%28AEON-UP%29/1056-de_DE |

Known starting points (verify these, do not assume them):
- The institute runs a **Chemistry Transport Modelling** group whose publication
  list is at
  `https://www.hereon.de/institutes/coastal_environmental_chemistry/chemistry_transport_modelling/publications/`
- That group has used **CMAQ** (Community Multiscale Air Quality) over the North
  Sea and European domains.
- The advert names NO₂, particulate matter, **ultrafine particles**, and
  **neural processes**.

---

## Checkpoint 1 — Publication inventory

For **each** of Ramacher and Karl separately, list their publications from roughly
**2019 onward**, most recent first. For each entry give:

```
   Authors (as published) | Year | Title | Journal | DOI or URL
   One sentence: what the paper actually does.
   Tags: [urban air quality] [emissions] [UFP] [CTM/CMAQ] [machine learning]
         [health exposure] [shipping] [other: ...]
```

Use Google Scholar, ORCID, the Hereon publication pages, and journal sites.
**Prefer the institutional and DOI sources over aggregators.**

### ✅ Verification 1
State the number of publications found for each PI, the date range covered, and
which sources you searched. If the two PIs have very different publication
volumes or focus, say so plainly.

---

## Checkpoint 2 — What each PI actually works on

Two short profiles, 200–300 words each, **built only from Checkpoint 1**.

For each: their principal research themes; the models and tools they name in
their own papers (CMAQ, EPISODE, SMOKE, emission inventories, specific
frameworks); the spatial scales they work at (street / urban / regional /
European); and whether machine learning appears anywhere in their published
work — and if so, exactly what kind.

**That last point matters more than any other in this report.** The position is
"probabilistic deep learning". If the PIs' published work is mostly
physics-based chemistry transport with little or no ML, that tells the applicant
something important: they are hiring for a capability the group does not yet
have, which changes what the application should emphasise. If they already
publish ML work, that tells him something different. **Report what you find,
whichever way it goes.**

---

## Checkpoint 3 — The AEON-UP project itself

Find whatever is publicly documented about AEON-UP as a project, beyond the job
advert: funder, programme, partners, duration, stated objectives, any project
page or press release. Search the acronym with and without "Hereon", and check
Helmholtz and BMBF/BMFTR project databases.

If little or nothing exists publicly, **say so explicitly**. A short honest
section is worth more than a padded one.

Also record what the advert itself specifies, quoted exactly: pollutants,
methods named, required and desired qualifications, contract terms.

---

## Checkpoint 4 — Domain briefing

800–1200 words, written for someone with a strong modelling and HPC background
but no atmospheric chemistry, covering:

1. What a chemistry transport model does, and specifically what **CMAQ** is —
   inputs (emissions, meteorology, boundary conditions), what it solves, typical
   grid resolutions, and its known limitations at urban scale.
2. Why **urban** air quality is hard: the resolution gap between a CTM grid cell
   and a street canyon; why NO₂ has sharp gradients while PM is smoother; what
   makes **ultrafine particles** different (measured by number not mass,
   short-lived, sparsely monitored, and — verify this — whether they are covered
   by EU limit values).
3. How machine learning is currently used in this field. Cover bias correction,
   emulation of expensive models, statistical downscaling, data fusion, and
   **land-use regression** as the classical baseline. Cite real papers.
4. Where **probabilistic** methods and **neural processes** enter, and why
   uncertainty matters specifically for air quality — sensor placement,
   regulatory thresholds, health exposure estimates.

Every non-obvious claim gets a citation.

---

## Checkpoint 5 — Connections (clearly separated)

Two sections, and the boundary between them must be obvious.

**5a. Grounded overlaps.** Where the applicant's documented experience genuinely
touches the group's documented work. His background: gridded spatio-temporal
simulation (ERGOM, GOTM-FABM, NetCDF), Linux HPC, a Fortran-to-JAX port with
TPU/GPU parallelisation, PyTorch activation extraction from a 15-layer
transformer, production data-pipeline verification, and clinical biostatistics.
Only list overlaps you can point at on both sides.

**5b. Inference and open questions.** Clearly labelled as inference. What the
group plausibly needs, what a candidate might ask at interview, what gaps are
visible. **Nothing from this section may be stated as fact in an application.**

---

## Checkpoint 6 — Deliverable

Write `docs/career/AEON_UP_RESEARCH_REPORT.md` containing Checkpoints 1–5, plus:

- A **sources table**: every URL consulted, with what it supported.
- A **confidence line on every major claim**: `[verified]` with a source,
  `[single source]`, or `[not found]`.
- An explicit list of **anything you could not establish**.

**STOP. Do not write the application. Do not edit the cover letter or CV. Do not
push.**

---

## Anti-patterns that will fail review

- Any factual claim without a source URL.
- "Likely", "probably", "presumably" outside section 5b.
- Padding Checkpoint 3 when the project simply is not publicly documented.
- Reporting that the PIs work on machine learning because the job advert
  mentions it. The advert is what they want to *hire*; the publications are what
  they have *done*. Keep those separate — the difference is the most useful
  thing this report can establish.
- Inventing a DOI, a journal, or a title. Every reference must resolve.
