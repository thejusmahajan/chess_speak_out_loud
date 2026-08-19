# AUDIT — `2026-08-19_website-repoint-aeon-up`

**Auditor:** Leader (Claude Opus 5) · **Date:** 2026-08-19
**Verdict: ACCEPT the work delivered. The TASK is incomplete — because the brief was wrong,
not because the worker was.** A follow-up brief (`…_website-repoint-part2`) closes the gaps.

---

## 1. Boundary check — PASS

Three files modified in `thejusmahajan.github.io` (`index.html`, `projects.html`,
`experience.html`); `skills.html` correctly swept but not edited. No `blog-*.html` touched.
No `css/`, `js/`, `assets/`, `images/`. Nothing staged, committed or pushed. The report landed
in the chess repo as instructed.

## 2. Copy applied verbatim — PASS

Every §3 replacement matches the leader-written copy exactly. **No biographical or technical
claim was invented anywhere in the diff.** This was the primary risk of the task and it did not
materialise.

## 3. Gates re-run independently — PASS

| Gate | Result |
|---|---|
| `grep "mid-April 2026" *.html` | no hits — stale date gone |
| `grep "February 2026 — April 2026" experience.html` | **still present** — the real internship date was not corrupted |
| `grep "seeking a position in clinical" *.html` | no hits |
| nav / footer blocks in the diff | untouched |
| internal links in the three edited pages | all resolve |

(Nav-block hashes differ *between* pages, but they differ on unedited pages too — that is
pre-existing active-link styling, not a regression.)

## 4. Worker behaviour — exemplary on the two things that matter

1. **It reported a leader spec error instead of hiding it.** §5 of the brief claimed
   `projects.html` had no card for the environmental modelling work. **That was false** — a
   `<!-- Project 3 -->` "Cyanobacteria Life Cycle Model" card already existed further down the
   page. The leader had read only the top of the file. The worker stated the discrepancy
   plainly, then removed the now-redundant card rather than shipping duplicates. Defensible
   action, correctly disclosed.
2. **It refused to write copy it was not given.** The sweep found the clinical contact paragraph
   in `projects.html:246`, `experience.html:253` and `skills.html:221` — outside the copy the
   brief supplied. It classified them as "(b) positioning to review" and **stopped**, exactly as
   instructed, instead of improvising replacements for a real person's professional record.

---

## 5. What is still wrong — all four are LEADER errors

### 5.1 The clinical-seeking footer is on **20 pages**, not four — CRITICAL

```
grep -l "expertise in clinical biostatistics" *.html | wc -l   ->  20
```

Every blog post, plus `blog.html`, `dashboard.html`, `experience.html`, `projects.html`,
`skills.html`, all still end with *"I am currently seeking opportunities to apply my expertise
in clinical biostatistics and bioinformatics."*

**The worst instance:** `blog-lc0-attention-frame.html:260` — the flagship neural-network
interpretability post, the single page a technical reviewer is most likely to read, closes by
saying he wants a clinical job.

**Root cause is the brief.** It said *"Do not rewrite any blog post. Not one word."* That is
correct for **article text** and wrong for the **shared footer boilerplate**, which is site
chrome duplicated verbatim across every page (as `website-and-blog-cadence` memory records).
The worker obeyed the instruction it was given.

### 5.2 The `<meta name="description">` still sells clinical work

`index.html:8` is unchanged:
> *"Computational scientist (PhD) with recent experience refactoring clinical data pipelines at
> scale (143,000+ patient records, German DeGIR registry). Available in Hamburg / Berlin /
> remote."*

**This is the snippet Google prints under the search result** — arguably more visible than the
`<title>` that was fixed. The worker filed it under "(a) factual history" and left it, which
was the safe call given no replacement copy was supplied. The classification is arguable; the
omission is the leader's.

### 5.3 Real content was lost in the card swap

The deleted `Project 3` card carried two things the new featured card does not:

- the **`GOTM-FABM`** tag — sourced independently at `skills.html:139` ("ERGOM biogeochemical
  model, GOTM-FABM framework, HPC applications"), and a meaningful credential to exactly the
  ocean/atmosphere modelling community Hereon sits in;
- the phrase **"validated against observational data"** — model-to-observation validation is
  precisely what an AEON-UP panel cares about.

Net effect: the swap added Hereon and ERGOM detail but dropped two genuinely relevant facts.
Caused by the leader not knowing the card existed.

### 5.4 Minor — malformed entity in the new `<title>`

`index.html:7` now contains a bare `&`:
```html
<title>Dr. Thejus Mahajan — Environmental Modelling & Machine Learning | Hamburg</title>
```
The rest of the file uses `&amp;`. Browsers recover, but validators flag it and this is the most
visible line on the site. The leader supplied the raw string; the worker applied it faithfully.

---

## 6. Lesson for future briefs

**"Don't touch these files" and "don't touch this content" are different instructions.** On a
site where nav and footer are duplicated into every page, a file-level exclusion silently
exempts site-wide chrome from a site-wide change. Scope by *element*, not only by *file* — and
run the positioning grep across **all** pages before deciding which files are in scope, rather
than after.
