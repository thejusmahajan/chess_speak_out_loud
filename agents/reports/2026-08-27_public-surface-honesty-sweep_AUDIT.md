# AUDIT — 2026-08-27 public-surface honesty sweep

**Brief:** `agents/briefs/2026-08-27_public-surface-honesty-sweep.md`
**Report:** `agents/reports/2026-08-27_public-surface-honesty-sweep_REPORT.md`
**Auditor:** the leader (Opus 5), 2026-08-27
**Verdict: ACCEPT.** Steps 1–3 delivered and independently reproduced. Step 4 correctly refused.

---

## 1. Worker delivery — ACCEPTED

Every checkpoint was re-run by the leader, not read from the report.

| checkpoint | pass condition | independent result |
|---|---|---|
| **1** | diff is exactly one line | `git diff --numstat` → `1	1	blog-ggplot2-timeseries.html`. The diff changes only the string `hamocc_plankton_output.csv` → `plankton_output.csv`. `mutate`, `filter`, `ggplot` and indentation untouched. **PASS** |
| **2** | zero matches for the five names | independent `grep -rniE "hamocc\|icon-o\|eerie\|levante\|dkrz"` across `*.html *.md *.js *.css`, `.git` excluded → **no output. PASS** |
| **3** | site dates match CV | `experience.html:242` `2012 – 2014`, `:247` `2009 – 2012`; `cv_hereon_aeon_up.tex:237` `07/2012 - 12/2014`, `:245` `06/2009 - 04/2012`. **PASS** |
| **4a** | stop if the input file is absent | `Test-Path` returned `False`; the worker stopped and reported it as blocked. **PASS — this is the behaviour the gate existed to produce.** |

`git status` in the website repo shows **one** modified file. No scope creep, no reformatting, no
commit, no push. Deviations "None" and Opinions "None" are both consistent with the diff.

**No fabrication.** Every quoted string in the report reproduces. This is the first delivery
against this website that survives the grep rule that was written after the 2026-08-22 §6
fabrication.

**One cosmetic artifact, not a defect:** the report's Checkpoint 3 paste renders the en dashes in
`experience.html` as hyphens (`2012 - 2014`). That is PowerShell console encoding in the paste,
not a change to the file — `git status` shows `experience.html` unmodified and the leader's own
grep returns the en dash. Worth knowing before someone reads it as a diff.

**Still uncommitted, deliberately.** The website fix is a one-line change sitting in the working
tree. *It is not shipped until it is committed and pushed.* Standing failure mode: audited
ACCEPT is not shipped.

---

## 2. LinkedIn audit — done by the leader, since the worker was correctly blocked

The input arrived at `agents/briefs/linkedin_profile.txt` (104 lines), not the path in the brief,
which is why Step 4a gated. Audited by the leader rather than re-briefed.

**The question that was asked is answered: the five names are NOT on LinkedIn.** No HAMOCC, no
ICON-O, no EERIE, no Levante, no DKRZ. The postdoc entry describes cyanobacteria and marine
ecosystem modelling, all of which the CV supports. **Nothing on LinkedIn needs removing for
honesty.**

**But the profile is badly out of date, and two entries misstate fact.** Compared line by line
against `cv_hereon_aeon_up.tex`:

| # | LinkedIn | CV | severity |
|---|---|---|---|
| **L1** | CQ Beratung+Bildung — *"Aug 2025 – **Present** · 1 yr 1 mo"* | `08/2025 - 02/2026` | **Factual error, top of the profile.** The programme ended in February 2026; the profile shows it as current. |
| **L2** | Postdoc *"Aug 2021 – **Feb 2025**"* | `08/2021 - 01/2025` | One-month mismatch with the submitted CV. |
| **L3** | **HealthTwiSt Praxisphase absent** | `02/2026 - 04/2026`, Clinical Data Engineering | Missing. He specifically asked that the bioinformatics training not be buried in the certificate bundle; on LinkedIn it is not there at all. |
| **L4** | **Current role absent** | `07/2026 - present`, *Independent Research — Deep Learning Pipeline Engineering* | Missing. LinkedIn shows **no activity after Oct 2025** — the LC0 interpretability work, the whole ML case, is invisible. |
| **L5** | Education: *"PhD **Astrophysics**"* | `Ph.D. in Astrochemistry` | Field mismatch — and LinkedIn contradicts *itself*: its own About says "experimental atomic and molecular collision". |
| **L6** | **B.Sc. absent** from Education | `University of Calicut`, 06/2009 - 04/2012 | Missing; it is on both the CV and the website. |
| **L7** | About section is entirely PhD-era, in the **present tense** — *"I use Fortran to run my simulations and C++ for data reduction"* | — | Reads as current work. Nothing from 2021 onward: no marine modelling, no ML, no interpretability. |
| **L8** | Headline: *"Computational Scientist \| Bioinformatics & Data Science \| HPC, Python, R, Fortran \| Big Data Optimization"* | — | **No ML or AI anywhere**, while he applies for probabilistic deep learning posts. |
| **L9** | Postdoc description in present tense — *"The question I am trying to answer…"* | ended 01/2025 | Reads as an ongoing role. |
| **L10** | Languages: German *"Professional working proficiency"* | only **Goethe B1** in the certificate bundle | Judgement call, his to make. B1 does not normally read as professional working proficiency, and he is currently working a B2 ladder. In Germany this is checkable. |
| **L11** | 3 publications listed | CV says five (2018–2020) | Undersells; also makes the 2021–2025 publication gap (H1) visible to anyone comparing. |
| **L12** | M.Sc. 2012–2014; PhD 2015–2018 | matches CV and site | ✅ **correct, change nothing** |

**Reading of the whole:** the honesty problem the sweep went looking for is not on LinkedIn. What
is there instead is a **positioning** problem — the profile still presents a Fortran/C++
astrochemist and stops in October 2025. L1 and L5 are the two that are simply wrong; L4 and L8 are
the two that cost him the most.

**LinkedIn is edited by hand, by Thejus.** Nothing here was or should be automated.

---

## 3. Follow-ups

1. **Ship the website fix** — one line, uncommitted in `thejusmahajan.github.io`.
2. **L1 and L5 are factual corrections** and should go first; the rest is rewriting.
3. `agents/briefs/linkedin_profile.txt` is an *input*, not a brief, and `agents/briefs/` is the
   immutable brief store. Move it or drop it once LinkedIn is updated. (Its contents are the
   public profile, so there is no disclosure concern in this repo.)
