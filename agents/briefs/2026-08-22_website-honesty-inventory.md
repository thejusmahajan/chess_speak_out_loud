```
Brief-ID:     2026-08-22_website-honesty-inventory
Written:      2026-08-22
Target repo:  thejusmahajan.github.io (primary) + job_search + chess_speak_out_loud (evidence)
Route:        Antigravity (full workspace — all three folders must be open)
Type:         audit / evidence collection
Status:       ACTIVE
Depends on:   none
```

# Inventory every factual claim on the website and say which ones are backed by evidence

## INTENT

Thejus is about to rebuild his personal website as the front door of a Germany-wide job search.
His one hard rule is that **nothing on it may be invented, inflated, or claimed as known when it
is not known.** He would rather delete a true-but-unprovable line than defend it in an interview.

A correct result is a **claim-by-claim inventory** of all 23 pages: for every factual assertion,
the exact text, where it is, and whether a named piece of evidence supports it. Nothing more.

**You are not judging whether a claim is impressive. Only whether it is true and supported.**
Do not rewrite the site. Do not suggest better wording. Do not tell him what to emphasise. That
is the leader's job and his; yours is to establish what the evidence will bear.

**If any instruction below conflicts with this intent, the intent wins — stop and report.**

```
Blast-radius:   external   <- this feeds a public site read by employers
Reversibility:  costly     <- a wrong "SUPPORTED" verdict ships an overclaim
Failure-mode:   SILENT
```

> **Why this before the deadline item?** It serves it. The AEON-UP CV header links to
> `thejusmahajan.github.io`, so the hiring committee may well open it. Twenty-one pages of that
> site currently tell every visitor he is seeking clinical biostatistics roles and was "available
> from mid-April 2026". That is a live problem for the application, not a distraction from it.

---

## 0. The rule that makes this report worth anything

The failure mode of an audit like this is a report full of green ticks produced by reading the
site and finding it plausible. Plausible is what it was written to be.

> **THE RULE: a claim may only be marked SUPPORTED if you name the artefact, quote the supporting
> text from it, and give its path or URL. "Consistent with the CV" is not evidence. "I checked"
> is not evidence. The quote is the evidence.**

A SUPPORTED verdict with no quoted source is a defect and the report is rejected for it.

**UNSUPPORTED is the expected, useful, welcome answer for a large fraction of claims.** Most
websites contain unfalsifiable self-description. Saying so is the point of the exercise, not a
failure of it. **Never invent a number.**

Two mandatory, non-empty sections, both near the TOP of the report:

- **"What I could not reach or could not check."**
- **"If exactly one verdict in this report is wrong, which is it most likely to be, and why?"**

---

## 1. Where to write

One file, and nothing else:

```
agents/reports/2026-08-22_website-honesty-inventory_REPORT.md
```

(in `chess_speak_out_loud`, even though the subject is another repo)

**Change no HTML. Change no CV. Write no code. Commit nothing.**

---

## 2. What to audit

All 23 pages in `C:\Users\Admin\Documents\thejusmahajan.github.io\`:

```
index.html  experience.html  projects.html  skills.html  blog.html
dashboard.html  pca-demo.html  simulacrum-analysis.html
blog-bash-ncbi  blog-blast-alignment  blog-clinical-data-wrangling  blog-deseq2
blog-ggplot2-timeseries  blog-hepatitis-delta-pipeline  blog-hpc-slurm
blog-lc0-attention-frame  blog-mixed-effects  blog-netcdf-xarray  blog-nextflow-dsl2
blog-r-packages  blog-shiny-dashboards  blog-sql-order  blog-survival-pca
```

**Audit the working tree as it stands on disk**, not the committed version. The working tree has
21 modified files that have never been committed; they are the current draft.

---

## 3. The evidence you may cite

Only these. If a claim is supported by nothing on this list, it is UNSUPPORTED.

| # | Artefact | What it settles |
|---|---|---|
| E1 | `job_search/applications/hereon_aeon_up/cv_hereon_aeon_up.tex` | Employment dates, roles, institutions, degrees, languages, training. **Corrected 2026-08-22; this is the authority.** |
| E2 | `thejusmahajan.github.io/github_thejusmahajan_projects/IBM/README.md` and `TECHNICAL_README.md` | The individual-based model: Lagrangian super-individuals, NPZD, trait evolution, Fortran/OpenMP, agent counts |
| E3 | `IBM/studies/*/` | Beckmann 2019 reproduction, Dolichospermum, Hense & Beckmann 2006 |
| E4 | `github.com/thejusmahajan` public repos | Whether a linked project exists, and what is actually in it |
| E5 | `chess_speak_out_loud/` code and `docs/CV_AI_MODULE.md` | The LC0 work: 15 layers, forward hooks, ONNX, the two bugs |
| E6 | `job_search/applications/hereon_aeon_up/study_room/06_do_not_claim.md` | The binding list of things he may not claim |
| E7 | The page itself, loaded | Whether a "live demo" actually runs |

**E6 deserves its own pass.** Any website text that violates a do-not-claim boundary is a HIGH
finding regardless of whether it is technically true, because he has already decided not to say
it.

---

## 4. The inventory

One row per factual claim. A page will produce many rows; `index.html` alone will produce dozens.

| page:line | claim, quoted exactly | verdict | evidence (artefact + quoted text) |
|---|---|---|---|

**Verdicts, and only these four:**

- **SUPPORTED** — an artefact says so. Quote it.
- **UNSUPPORTED** — may well be true; nothing on the E-list establishes it.
- **CONTRADICTED** — an artefact says otherwise. Quote both sides.
- **UNFALSIFIABLE** — not a checkable claim ("passionate about data"). Just label it; no evidence needed.

### Claim classes to be especially careful with

1. **Every number.** `26.5%`, `143,000+`, `~300 clinics`, `ten years`, `three years`,
   `terabytes`, `15-layer`, `257 rules`, agent counts, `10+`. For each: does an artefact state
   that number, or a number it was derived from? Derived is fine — show the derivation.
2. **Every date and duration.** Cross-check each against E1. **Known live discrepancy to resolve:
   `assets/Thejus_Mahajan_CV_ML.pdf` dates the independent research `05/2026 - present`, while
   E1 says `07/2026 - present`. Thejus has confirmed 07/2026 is correct. Find every place on the
   site carrying a start date for that work and report which value each one shows.**
3. **Every "available from" / availability statement.** The committed site says "available from
   mid-April 2026", a date now four months past.
4. **Every skill or tool named** on `skills.html`. For each, is there an artefact showing he used
   it — a repo, a blog post with real output, a CV line? A tool named with no trace anywhere is
   the single most common way a CV becomes indefensible.
5. **Every link.** Internal links that 404, external links that are dead, GitHub links to repos
   that do not exist or are empty.
6. **Every "live demo".** `dashboard.html`, `pca-demo.html`, `simulacrum-analysis.html`. Open
   them. Does the thing described actually run in a browser, or is it a screenshot or a stub?
   Report exactly what you observed.
7. **The 15 blog posts.** These are the largest surface area and the least reviewed. You are not
   fact-checking the technical content of the field. You are checking **claims about himself**:
   "in my work at X I did Y". Flag any that assert experience E1 does not support.

---

## 5. One thing to count, separately

He is broadening from a bioinformatics/ML specialist to a Germany-wide search across scientific
computing, data engineering and machine learning. So, as a plain count with page references, no
opinion attached:

- pages whose visible framing is **clinical / bioinformatics**
- pages whose visible framing is **machine learning / interpretability**
- pages whose visible framing is **environmental / physical modelling**
- pages that are **general** or framing-neutral

He needs to know the shape of what is there. He does not need you to tell him what it should be.

---

## 6. Report shape

```
1. What I could read, run, and could not                 <- FIRST, non-empty
2. The verdict I am most likely to have got wrong        <- a prediction
3. Summary counts: SUPPORTED / UNSUPPORTED / CONTRADICTED / UNFALSIFIABLE
4. CONTRADICTED claims          <- every one, in full. This is the section that matters most.
5. Do-not-claim violations (E6) <- HIGH severity, listed separately
6. UNSUPPORTED claims, grouped by page
7. Broken links and dead demos
8. The framing count from §5
9. Full inventory table
```

Sections 4 and 5 come before the bulk because they are what he must act on before the site goes
live. If the report is truncated by length, they must survive.

Length is not a virtue, but **completeness is** — a partial inventory that silently skips six
blog posts is worse than one that says "I audited 17 of 23 pages, here are the six I did not
reach". Say what you did not cover.
