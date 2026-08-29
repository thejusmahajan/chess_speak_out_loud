# BRIEF — put the completed IBM PyTorch certificate onto the two live CVs and the website

**Filed:** 2026-08-29 by the leader
**Worker:** Gemini 3.7 Flash (High), Antigravity IDE
**Workspaces:** `bioinformatics_project/job_search` (Part A) **and** `thejusmahajan.github.io` (Part B)
**Status:** ACTIVE

**Why this before the interview?** Because the submitted cover letter says *"I am in the final
module"* and the course is now **finished**. Every artefact a panel or a recruiter can reach —
the live ML CV that is the primary download on the website, and the website's own Certifications
section — still says otherwise. This is a credential that is already earned and already verified
sitting invisible. It is mechanical, it is small, and it makes a stated plan into a delivered one.

---

## 0. Read this before you type anything

### 0.1 The fact, and where it came from

The certificate is real, it is on disk, and the leader verified it **live against Coursera** on
2026-08-29 before writing this brief:

| field | value |
|---|---|
| course | **Deep Learning with PyTorch** |
| issuer | **IBM**, offered through **Coursera** |
| awarded to | Thejus Mahajan |
| completion date | **29 August 2026** |
| credential ID | **`DDDI9T0KHUJ4`** |
| verify URL | `https://coursera.org/verify/DDDI9T0KHUJ4` |
| file | `applications/hereon_aeon_up/certificates/IBM_Coursera_Deep_Learning_with_PyTorch.pdf` |

**Do not look any of this up. Do not "confirm" it. Do not enrich it.** Every string you insert is
given verbatim below. If you find yourself typing a fact that is not copied from this brief, you
have left the task — stop and report.

### 0.2 ⛔ The honesty boundary — the single most important constraint here

This course is **applied deep learning**: logistic/softmax regression, shallow networks, dropout
and batch normalisation, CNNs, transfer learning with ResNet18, and GPU/CUDA training patterns.

**It contains NO Bayesian methods, NO uncertainty quantification, NO calibration, NO Gaussian
processes, NO neural processes, NO probabilistic modelling of any kind.**

Thejus is interviewing for a project whose whole point is probabilistic. The syllabus is one click
from the credential ID you are about to publish. **Any wording that implies this course touches the
probabilistic side is a serious, career-damaging error** — worse now than before the certificate
existed, because the certificate makes the syllabus checkable.

So: **you may not write a single word of copy.** The exact LaTeX and the exact HTML are given.
Insert them character for character. If a step seems to need a sentence this brief does not
provide, **stop and ask.**

### 0.3 ⛔ Files you may not touch, and why

**`applications/hereon_aeon_up/cv_hereon_aeon_up.tex` and its PDF are FROZEN.** That application
was submitted on 27 August. Its CV says *"2026 — final module; certificate expected 09/2026"*,
which was true on the day it was sent. That file is now a **record of what was sent**, not a live
document. Editing it destroys the record and would leave the repo disagreeing with what Hereon
actually holds. **Do not open it.**

**The same applies to every other CV and cover letter under `applications/`** —
`erlangen_stem_cell_biology`, `helmholtz_munich`, `helmholtz_munich_staff_scientist`,
`fzj_fairagro_rdm`, `geomar_zoom_in`, `mdc_berlin_ludwig_lab`, `mpinat_scientific_it_specialist`,
`octapharma_molecular_design`, `robert_bosch_hospital`, `roche_biostatistician_penzberg`,
`clinical_data_science_general`, `mollman`, `hamburg_welcome_center`. Those are per-application
artefacts. **Leave all of them exactly as they are.** Do not "be helpful" and roll the update out
across them — a bulk edit here is the failure mode this brief is written to prevent.

**Exactly two `.tex` files change. They are named in §2.** One of them lives under `applications/`
and is the sole exception; it is there for historical reasons and it is the source of the live
website download.

### 0.4 The contract

`agents/README.md` applies in full: never invent a number, paste real command output, report every
deviation, and stop and ask for anything this brief does not cover.

**Do not commit. Do not push. In either repository.** Leave both trees dirty. The leader audits
the diff. Report to `agents/reports/2026-08-29_pytorch-certificate-rollout_REPORT.md` in the
`chess_speak_out_loud` repo, wherever your workspace is rooted.

---

## 1. Baseline FIRST — before you edit anything

Run this from the root of `bioinformatics_project/job_search` and **paste the full output** into
your report. You will compare against it in §4.

```bash
python -c "
from pypdf import PdfReader
for p in ['applications/ml_interpretability_general/cv_ml_interpretability.pdf',
          'cv_general_ml/cv_ml_general.pdf']:
    print(p, len(PdfReader(p).pages), 'pages')
"
md5sum applications/ml_interpretability_general/cv_ml_interpretability.pdf \
       cv_general_ml/cv_ml_general.pdf \
       ../../thejusmahajan.github.io/assets/Thejus_Mahajan_CV_ML.pdf
git status --porcelain
```

**Expected baseline, recorded by the leader on 2026-08-29 — if yours disagrees, STOP and report:**

- both PDFs are **2 pages**
- `cv_ml_interpretability.pdf` md5 = `7f1f4987d03272e653172a6023e11d66`
- `assets/Thejus_Mahajan_CV_ML.pdf` md5 = `7f1f4987d03272e653172a6023e11d66` — **identical**, which
  is the fact that makes `cv_ml_interpretability.tex` the source of the website's primary download
- `cv_general_ml/cv_ml_general.pdf` md5 = `a1176876bdd171ae949ef006bae81fde`
- `git status --porcelain` is **empty except for `?? applications/mollman/`**, which is
  pre-existing and none of your business — leave it untracked and do not stage it. The certificate
  itself and the updated `study_room/12_pytorch_course.md` are already committed by the leader as
  `2b8da1a`. **Do not edit either.**

The Python is the `cszero` conda environment:
`C:\Users\Admin\miniconda3\envs\cszero\python.exe`. LaTeX is TeX Live 2019 `pdflatex`, already on
PATH; both CVs were last built with it.

---

## 2. Part A — the two CVs

### 2.1 The block to insert, verbatim

This is the entire text you are adding. **Copy it exactly**, including the `\\[0.3cm]` at the end:

```latex
\textbf{Deep Learning with PyTorch}\\
{\small IBM \textbar\ Coursera --- completed 08/2026\\
Credential DDDI9T0KHUJ4\\
CNNs, transfer learning, GPU/CUDA training patterns}\\[0.3cm]

```

Note what the third line does: it states the scope of the course. That is deliberate and it is the
§0.2 boundary made visible on the page. **Do not shorten it, do not reword it, do not drop it.**

### 2.2 Where it goes

In **both** files, the block becomes the **first** entry under `\cvsection{Further Training}` —
immediately after the `\cvsection{Further Training}` line and the blank line that follows it, and
**before** the existing `\textbf{Deployable Data Analysis \& AI Pipelines with HPC}` entry.
Newest first, which is the ordering both files already use.

**File 1 — `applications/ml_interpretability_general/cv_ml_interpretability.tex`**
(this is the live website CV; the section starts at line 182). It currently reads:

```latex
\cvsection{Further Training}

\textbf{Deployable Data Analysis \& AI Pipelines with HPC}\\
```

**File 2 — `cv_general_ml/cv_ml_general.tex`** — the same section, same structure, same insertion
point.

**Nothing else in either file changes.** Not the skills line, not the profile, not the summary,
not the publications block. One block, two files.

### 2.3 Build

For each of the two files, from the directory containing it:

```bash
pdflatex -interaction=nonstopmode <name>.tex
pdflatex -interaction=nonstopmode <name>.tex
```

Twice, because the class uses `paracol` and page geometry settles on the second pass.

**Paste the last 15 lines of each run.** Exit status must be 0 and there must be no `! LaTeX Error`
or `! Undefined control sequence` in the log.

### 2.4 Gates for Part A — run all four, paste all output

```bash
# G1 — the credential is actually on the page
pdftotext applications/ml_interpretability_general/cv_ml_interpretability.pdf - | grep -c "DDDI9T0KHUJ4"
pdftotext cv_general_ml/cv_ml_general.pdf - | grep -c "DDDI9T0KHUJ4"
# both must print 1

# G2 — the course title is on the page
pdftotext applications/ml_interpretability_general/cv_ml_interpretability.pdf - | grep -c "Deep Learning with PyTorch"
pdftotext cv_general_ml/cv_ml_general.pdf - | grep -c "Deep Learning with PyTorch"
# both must print 1

# G3 — page count UNCHANGED (a 3-page CV is a failure, not a detail)
python -c "
from pypdf import PdfReader
for p in ['applications/ml_interpretability_general/cv_ml_interpretability.pdf',
          'cv_general_ml/cv_ml_general.pdf']:
    print(p, len(PdfReader(p).pages))
"
# both must print 2

# G4 — THE HONESTY GATE. The diff must contain no probabilistic vocabulary.
git diff -U0 -- applications/ml_interpretability_general/cv_ml_interpretability.tex \
                cv_general_ml/cv_ml_general.tex \
  | grep -i -E "bayes|uncertain|neural process|calibrat|probabilist|gaussian process|CRPS"
# must return NOTHING (grep exit 1). Any hit = you wrote copy you were told not to write.

# G5 — nothing else was touched
git status --porcelain
# beyond the pre-existing `?? applications/mollman/` from §1, the ONLY paths listed may be:
#   the two .tex files, their two .pdf files, and their .aux/.log/.out build artefacts.
# If cv_hereon_aeon_up.tex or any other application CV appears here, you have broken §0.3.
```

**If G3 comes back 3 pages**, stop and report it. Do not fix it by deleting something else to make
room. That is a judgement call about what a CV says, and it belongs to the leader.

---

## 3. Part B — the website

Workspace: `C:\Users\Admin\Documents\thejusmahajan.github.io`, branch `main`.

### 3.1 Refresh the downloadable CV

```bash
cp ../bioinformatics_project/job_search/applications/ml_interpretability_general/cv_ml_interpretability.pdf \
   assets/Thejus_Mahajan_CV_ML.pdf
md5sum assets/Thejus_Mahajan_CV_ML.pdf \
       ../bioinformatics_project/job_search/applications/ml_interpretability_general/cv_ml_interpretability.pdf
```

**Gate G6: the two md5 values must be identical, and both must differ from
`7f1f4987d03272e653172a6023e11d66`.** Same hash as the baseline means you copied the stale file.

`assets/Thejus_Mahajan_CV.pdf` and `assets/Thejus_Mahajan_CV_DE.pdf` have **no source `.tex` in
`job_search`** — the leader checked, by hashing every PDF in the repo. **Do not touch either of
them and do not attempt to regenerate them.** That is a separate open question for Thejus.

### 3.2 The Certifications card

In `experience.html`, section 4 *"Certifications & Training"* (the `<h2>` is around line 254).
Two changes, both exact:

**(a)** Change the grid class so five cards lay out evenly (three then two) instead of leaving one
card stranded on its own row:

```
FROM:  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
TO:    <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
```

There is exactly one such `<div>` inside this section. **Do not change any other grid on the site.**

**(b)** Insert this as the **first** card in that grid, immediately after the opening `<div>` above
and before the existing *"Goethe-Zertifikat B1"* card. Verbatim:

```html
                <div class="bg-white border border-gray-100 shadow-sm rounded-lg p-5 text-center hover:shadow-md hover:border-sky-100 transition-all">
                    <h4 class="font-bold text-gray-800 text-sm mb-1">Deep Learning with PyTorch</h4>
                    <p class="text-xs text-gray-600">IBM on Coursera, August 2026 &middot; <a href="https://coursera.org/verify/DDDI9T0KHUJ4" target="_blank" rel="noopener noreferrer" class="text-sky-700 hover:underline">verify</a></p>
                </div>
```

**No other page changes.** Not `index.html`, not `skills.html`, not the blog, not the meta
descriptions. If you think another page needs it, say so in the report — do not do it.

### 3.3 Gates for Part B

```bash
# G7 — the card is present exactly once, and the verify link with it
grep -c "DDDI9T0KHUJ4" experience.html          # must be 1
grep -c "Deep Learning with PyTorch" experience.html   # must be 1

# G8 — the grid change is confined to that one section
grep -n "md:grid-cols-4" experience.html
grep -n "md:grid-cols-3" experience.html
# report both; the Certifications grid must be the ONLY one that moved from 4 to 3

# G9 — scope
git status --porcelain
# ONLY experience.html and assets/Thejus_Mahajan_CV_ML.pdf may be listed
```

**G10 — look at it.** Open `experience.html` in a browser. **Screenshot the Certifications &
Training section** and attach it to the report. Confirm in your own words: five cards, laid out
3 + 2, no overflow, no card wider or taller than its neighbours, the *verify* link visible and
clickable. *This project has three recorded cases of correct content shipped somewhere nobody
could see it. A grep is not a pair of eyes.*

---

## 4. What to report

`agents/reports/2026-08-29_pytorch-certificate-rollout_REPORT.md`, in the `chess_speak_out_loud`
repo. It must contain:

1. The §1 baseline output, pasted.
2. The `git diff` of both `.tex` files, in full. They should be small — one block each.
3. The last 15 lines of all four `pdflatex` runs.
4. **G1 through G10, each with its command and its real output.** A gate reported without its
   output counts as not run.
5. The G10 screenshot.
6. Every deviation, and every point where you stopped and asked.
7. Final `git status --porcelain` for **both** repositories.

**Do not commit and do not push. Neither repo.**

---

## 5. Out of scope — say so if you notice, do not act

These are real and the leader already knows about them. Listing them so you do not "fix" one:

- `Thejus_Mahajan_CV.pdf` / `_DE.pdf` on the website have no tracked source. Open question.
- The German CV has not been updated in some time. Separate task.
- LinkedIn is edited by hand, by Thejus. **Nothing on LinkedIn is automated, ever.**
- The `hereon_aeon_up` trainer ladder may deserve a card about the completed certificate. **Card
  content is written by the leader, never by a worker.** Three fabricated deliveries on this
  project came from asking a worker for content.
