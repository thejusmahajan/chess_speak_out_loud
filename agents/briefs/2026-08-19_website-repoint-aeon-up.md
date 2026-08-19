```
Brief-ID:     2026-08-19_website-repoint-aeon-up
Written:      2026-08-19
Target repo:  thejusmahajan.github.io  (C:\Users\Admin\Documents\thejusmahajan.github.io)
Route:        Antigravity (open THAT folder as the workspace, not the chess repo)
Type:         implementation (content application + mechanical sweep)
Status:       ACTIVE
Depends on:   none
```

# Repoint the personal site from clinical bioinformatics to environmental modelling + ML

## 0. THE ABSOLUTE RULE — read before anything else

**Every biographical and technical claim you write must already exist, in the site's own words,
somewhere in this repository.** All replacement copy in §3 was written by the leader from
`experience.html` and `index.html` and is sourced. Your job is to **apply** it, not to extend it.

- Do **not** invent a job, a date, a skill, a tool, a metric, a publication, or a claim.
- Do **not** "improve" the copy with extra detail. If a sentence feels thin, leave it thin.
- If something seems missing or wrong, **report it in your report** — do not fill it in.

This is a real person's professional record being read by a hiring panel. A single invented
detail is a firing offence for this task, and it is the failure mode that has cost this
project most.

## 1. Why

The site currently presents Thejus as a **clinical bioinformatician**. He is applying for a
postdoc in **probabilistic deep learning for urban air quality** at Helmholtz-Zentrum Hereon
(deadline 3 September 2026). The clinical applications are dormant; roles of the Hereon type
are now the focus.

As it stands the site tells that panel, twice and explicitly, that he wants a different job —
and frames his environmental modelling career, which is the exact fit for the role, as
something he deliberately left. The site and the application contradict each other.

It also buries the strongest single fact on it: **he was a Guest Scientist at Helmholtz-Zentrum
Hereon, Geesthacht (May–October 2025)** — the very institute he is applying to.

## 2. Scope and boundaries (hard)

**Edit ONLY these four files:**
```
index.html
projects.html
experience.html
skills.html      (only if §4's sweep finds positioning text there — see §4)
```

**Do NOT touch:**
- **Any `blog-*.html` file.** Sixteen posts mention "clinical" and they are legitimate technical
  content about clinical topics. They stay exactly as they are. We are changing *positioning*,
  not erasing history.
- `blog.html`, `dashboard.html`, `pca-demo.html`, `simulacrum-analysis.html`
- `css/`, `js/`, `assets/`, `images/` — no asset or stylesheet changes
- Anything in `C:\Users\Admin\Documents\chess_speak_out_loud`

**Do not commit and do not push.** Leave everything uncommitted for review. The remote needs
his credentials and pushing is his decision, not yours.

**Preserve the template conventions:** nav and footer blocks are duplicated verbatim in every
page — if you touch one, they must all still match byte-for-byte. Tailwind is via CDN; keep the
existing utility-class style. Do not introduce a build step, a framework, or new dependencies.

## 3. The copy to apply (exact — do not paraphrase)

Locate each item by its anchor text. HTML entities (`&mdash;`, `&amp;`, `&middot;`) may appear
in the source; match on the visible text and preserve the surrounding markup. **If you cannot
find an anchor, do not guess — report it.**

### 3.1 `index.html` — page title

**Anchor:** the `<title>` containing `Biostatistics` and `Clinical Data Engineering`
**Replace the title text with:**
```
Dr. Thejus Mahajan — Environmental Modelling & Machine Learning | Hamburg
```

### 3.2 `index.html` — hero tagline

**Anchor:** `Computational Scientist | Machine Learning · Clinical Data Pipelines · Biostatistics`
**Replace with:**
```
Computational Scientist | Spatio-Temporal Modelling · Machine Learning · Scientific HPC
```
Keep the existing `&middot;` separators and markup.

### 3.3 `index.html` — hero paragraph

**Anchor:** the paragraph beginning `PhD-level researcher with 10+ years in computational modeling`
**Replace the whole paragraph with:**
```
Physicist with over ten years in computational modelling — including three years developing
biogeochemical models of marine ecosystems on HPC clusters, and current independent research in
neural network interpretability, extracting and correcting internal representations from a
15-layer transformer in PyTorch.
```

### 3.4 `index.html` — the availability line (STALE DATE)

**Anchor:** `I am available from mid-April 2026.`
**Action:** delete this sentence entirely. That date passed four months ago.

⚠ **Precision required.** `experience.html` also contains "April 2026" as the genuine end date
of the HealthTwiSt internship (`February 2026 — April 2026`). **That is correct and must not be
touched.** Only the availability sentence in `index.html` is stale.

### 3.5 `index.html` — About, first paragraph

**Anchor:** the paragraph beginning `I am a computational scientist with a Ph.D. in Astrochemistry`
**Replace the whole paragraph with:**
```
I am a computational scientist with a Ph.D. in Astrochemistry (Université Paris-Saclay) and more
than three years as a postdoctoral scientist in marine ecosystem modelling at the University of
Hamburg (with parental leave in 2024). There I developed the Cyanobacteria Life Cycle model
within the ERGOM biogeochemical framework, engineered simulations in Fortran, analysed large
NetCDF datasets in Python, and managed multi-year hindcast and projection experiments on HPC
clusters. In 2025 I continued this work as a guest scientist at Helmholtz-Zentrum Hereon in
Geesthacht.
```

### 3.6 `index.html` — About, second paragraph

**Anchor:** the paragraph beginning `I recently completed intensive training in bioinformatics`
**Replace the whole paragraph with:**
```
I then spent a year in clinical data engineering, which sharpened a different discipline:
verification. Refactoring a production R pipeline that processes 143,000+ patient records
annually from ~300 German clinics, I reduced it by 26.5% while proving byte-identical output at
every step, and escalated two pre-existing bugs for supervisor review rather than silently
fixing them. I also built an interactive Shiny dashboard for clinical quality metrics, available
as a live demo.
```
Keep the existing hyperlink on "live demo" pointing wherever it currently points.

### 3.7 `index.html` — About, closing paragraph (THE HARMFUL ONE)

**Anchor:** `I am seeking a position in clinical data science, biostatistics, or bioinformatics`
**Replace the whole paragraph with:**
```
My current independent research is in neural network interpretability, where I found and
publicly corrected two silent errors in my own analysis pipeline. The same question runs through
all of this work: what is the model actually computing, and how far can its output be trusted? I
am seeking a research position combining environmental or physical modelling with machine
learning.
```

### 3.8 `index.html` — Contact section

**Anchor:** `I am currently seeking opportunities to apply my expertise in clinical biostatistics and bioinformatics.`
**Replace the whole sentence pair with:**
```
I am currently seeking research positions combining environmental or physical modelling with
machine learning. I would be glad to connect and discuss how my work might contribute to your
group.
```

### 3.9 `index.html` — the "R + Python" statistics tile

**Anchor:** the tile body `Proficient in Bioconductor, Tidymodels, scikit-learn, Pandas, ggplot2`
**Replace the tile body with:**
```
PyTorch, xarray/NetCDF, scikit-learn, Pandas, Fortran, ggplot2
```
If the tile's heading reads `R + Python`, change it to `Python + R`. Leave the other three
statistic tiles (5 Publications, ~300 Clinics, 10+ Years) untouched.

### 3.10 `projects.html` — page subtitle

**Anchor:** `Applied work in clinical data analysis, biostatistics, and computational modeling`
**Replace with:**
```
Applied work in environmental modelling, machine learning, and scientific data engineering
```

### 3.11 `experience.html` — page subtitle (THE HARMFUL ONE)

**Anchor:** `A deliberate career transition from computational physics to clinical bioinformatics`
**Replace with:**
```
Computational modelling across physics, marine ecosystems, and machine learning
```

## 4. Add a project card for the marine modelling work

`projects.html` has cards for the DeGIR pipeline and the Simulacrum analysis but **none for the
three-and-a-half years of environmental modelling** — the most relevant work he has for the
roles he is now targeting.

Add a new card as the **first** card on the page, matching the existing card markup exactly
(same classes, same structure, same tag-pill style). Content, all of it sourced verbatim from
`experience.html`:

- **Title:** `Marine Ecosystem Modelling — the Cyanobacteria Life Cycle model in ERGOM`
- **Subtitle:** `University of Hamburg, Institute of Marine Ecosystem and Fisheries Sciences · Helmholtz-Zentrum Hereon`
- **Body:**
  ```
  Developed the Cyanobacteria Life Cycle (CLC) model within the ERGOM biogeochemical framework.
  Engineered simulation models in Fortran and analysed large NetCDF datasets in Python. Performed
  statistical analysis and visualisation of ecological time-series data in R and ggplot2, and
  managed multi-year hindcast and projection experiments on HPC clusters. Continued as a guest
  scientist at Helmholtz-Zentrum Hereon, Geesthacht, in 2025.
  ```
- **Tag pills:** `Fortran` `Python` `NetCDF` `xarray` `R` `ggplot2` `HPC` `ERGOM`
- **No statistics block and no buttons** unless you can source real numbers and a real URL from
  this repository. If you cannot, omit them — an empty stat is worse than none.

## 5. The mechanical sweep — REPORT, do not guess

After making the changes above, sweep the four in-scope files for anything still positioning him
as seeking clinical work, and for any other stale date:

```
grep -n -i "clinical\|biostatist\|bioinformatic\|seeking\|available from" index.html projects.html experience.html skills.html
```

**Classify every hit into one of two lists in your report:**

- **(a) Factual history** — descriptions of what he actually did (the HealthTwiSt internship, the
  CQ training, skills he genuinely has). **Leave these alone.** They are true and they are not
  the problem.
- **(b) Forward-looking positioning** — anything stating what kind of role he wants, or framing a
  domain as his target. **List these with file, line number and exact text, and STOP.** Do not
  rewrite them yourself; the leader writes all copy.

The distinction matters: we are not hiding his clinical year, we are removing statements that
say he wants a clinical job.

## 6. Gates — paste REAL output

1. `grep -n "mid-April 2026" *.html` → must return **nothing**.
2. `grep -n "February 2026 — April 2026" experience.html` → must **still be present** (proof you
   did not corrupt the real internship date).
3. `grep -n "seeking a position in clinical" *.html` → must return **nothing**.
4. **Nav/footer consistency:** show that the nav block is still byte-identical across all edited
   pages (e.g. extract the `<nav>`…`</nav>` block from each and compare hashes).
5. **Internal link check:** every `href` to a local file in the four edited pages resolves to a
   file that exists. Paste the check and its result.
6. `git status` and `git diff --stat` — only the permitted files, nothing committed.
7. Open `index.html` and `projects.html` in a browser (or render them) and confirm the layout is
   not broken. Say plainly which you checked and how.

## 7. What NOT to do

- **Do not rewrite any blog post.** Not one word.
- **Do not delete the clinical work** from projects or experience. It is real, recent, and the
  verification discipline it demonstrates is an asset. We are re-framing, not erasing.
- **Do not touch the CV files or their links.** The primary "Download CV" button already points
  at `assets/Thejus_Mahajan_CV_ML.pdf`, which is correct.
- **Do not write new copy of your own.** Every sentence in §3 was written by the leader. If a
  gap needs filling, report it.
- **Do not commit or push.**

## 8. Your report

Write `agents/reports/2026-08-19_website-repoint-aeon-up_REPORT.md` **into the chess repo**
(`C:\Users\Admin\Documents\chess_speak_out_loud\agents\reports\`), covering:

1. Each §3 item: applied, or anchor-not-found (with what you searched for).
2. The §5 sweep, split into the two lists (a) factual history and (b) positioning-to-review.
3. Every gate command and its real output.
4. Anything in this brief that was wrong about the actual files — **reporting a spec error is a
   good outcome**, working around it silently is not.
5. Anything you did not do, explicitly listed.
