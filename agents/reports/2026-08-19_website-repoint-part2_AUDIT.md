# AUDIT — `2026-08-19_website-repoint-part2`

**Auditor:** Leader (Claude Opus 5) · **Date:** 2026-08-19
**Verdict: ACCEPT.** All five gates pass on independent re-run, no article text was touched, and
the worker caught an error in the brief's own gate spec. The site repoint is complete.

---

## 1. Boundary check — PASS

21 files modified: the 20 carrying the clinical contact paragraph, plus `index.html` for the
meta description and title-entity fix. No `css/`, `js/`, `assets/`, `images/`. Nothing staged,
committed or pushed.

## 2. The main risk — article text — PASS, verified two ways

The danger was a bulk edit bleeding into the body of fifteen technical posts.

**Per-file changed-line count** (the brief required exactly 2 — one removed, one added):

```
blog-bash-ncbi 2 · blog-blast-alignment 2 · blog-clinical-data-wrangling 2 · blog-deseq2 2
blog-ggplot2-timeseries 2 · blog-hepatitis-delta-pipeline 2 · blog-hpc-slurm 2
blog-lc0-attention-frame 2 · blog-mixed-effects 2 · blog-netcdf-xarray 2 · blog-nextflow-dsl2 2
blog-r-packages 2 · blog-shiny-dashboards 2 · blog-sql-order 2 · blog-survival-pca 2
```

**Content of the changed lines:** every changed line across all fifteen posts belongs to the
contact paragraph — a grep for changed lines *not* matching the contact block returns **0**.
Not one word of article text moved.

## 3. Gates re-run independently — ALL PASS

| Gate | Expected | Observed |
|---|---|---|
| clinical contact paragraph remaining | 0 | **0** |
| pages carrying the new contact copy | 20 (brief) | **21** — see §4 |
| old meta description in `index.html` | none | **none** |
| `GOTM-FABM` + `validated against observational data` restored | both | **both present** |
| title entity | `&amp;` | `<title>Dr. Thejus Mahajan — Environmental Modelling &amp; Machine Learning \| Hamburg</title>` |
| internal links across all 22 pages | all resolve | **all resolve** |

New meta description in place:
> *Computational scientist (PhD): marine ecosystem modelling on HPC, neural-network
> interpretability in PyTorch, and large-scale scientific data engineering. Based in Hamburg.*

## 4. The worker corrected a leader error in the gate spec

Brief §6 gate 2 asserted the new contact text should appear on **20** pages. The true figure is
**21**: `index.html` already received that copy in part 1, so part 2 changed the remaining 20.

The worker reported the discrepancy explicitly with the reasoning, rather than editing a file to
force the number to 20 — which is the failure mode that gate spec could easily have induced.
Independently confirmed: `git diff index.html` contains exactly one occurrence of the new
sentence, and it is the part-1 addition.

## 5. Residual positioning — clean

Every remaining forward-looking statement on the site now reads:

```
I am currently seeking research positions combining environmental or physical modelling with machine learning.
I am seeking a research position combining environmental or physical modelling with machine learning.
```

(Two variants by design — the footer form and the About-section form.)

Remaining occurrences of "clinical" are factual history only: `index.html` 2, `projects.html` 2,
`experience.html` 2, `skills.html` 4 — the HealthTwiSt work and the CQ training, which are real
and stay. The clinical year is reframed as verification discipline, not deleted.

---

## 6. State of the site after parts 1 and 2

- Title, tagline, hero paragraph, About (three paragraphs), contact copy, page subtitles on
  `projects.html` and `experience.html`, and the meta description all repointed to environmental
  modelling + machine learning.
- The Hereon guest-scientist stint is now named in the About section rather than buried.
- A featured marine-modelling project card leads `projects.html`, carrying ERGOM, the CLC model,
  Fortran, NetCDF, HPC, GOTM-FABM and observational validation.
- All 22 pages carry consistent, non-contradictory positioning.

## 7. Still outstanding (leader-owned, not this brief's scope)

1. **The `experience.html` gap.** The most recent entry still ends April 2026, leaving four
   unexplained months and no entry for the LC0 interpretability research. Copy drafted; start
   date confirmed as **July 2026** from this repo's first commit (`2026-07-15`).
2. **The attention demo page**, blocked on the regenerated export.
3. **The positioning-switch mechanism** (marker comments + profile files), deferred until after
   3 September by design.
