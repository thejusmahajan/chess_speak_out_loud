# BRIEF — bring the public surface up to date: both live CVs, and the website

**Filed:** 2026-08-29 by the leader. **Widened the same day** at Thejus's instruction from
"add the certificate" to "update all the CVs, and the text on the website."
**Worker:** Gemini 3.7 Flash (High), Antigravity IDE
**Workspaces:** `bioinformatics_project/job_search` (Part A) **then** `thejusmahajan.github.io` (Part B)
**Status:** ACTIVE

**Why this before the interview?** Three things are true today and none of them are visible to
anyone who looks him up. (1) The IBM PyTorch certificate is **earned** — the submitted cover letter
still says *"I am in the final module."* (2) The CNP is **built**, so the Machine Learning line on
the CV can finally carry something probabilistic, which is the single highest-value line on it for
an AEON-UP panel. (3) The website's skills page — the page a technical reader actually clicks —
**does not contain the words PyTorch, deep learning, or machine learning anywhere**, while the
front page headline says "Machine Learning" and the primary CV download is the ML one.

That last one is the real finding. The public surface currently contradicts itself.

---

## 0. Read this before you type anything

### 0.1 The facts, and where they came from

Everything you will insert was verified by the leader on 2026-08-29. **Do not look any of it up,
do not confirm it, do not enrich it.**

| fact | value | how the leader verified it |
|---|---|---|
| course | **Deep Learning with PyTorch**, IBM via Coursera | the certificate PDF |
| completion | **29 August 2026** | fetched `coursera.org/verify/DDDI9T0KHUJ4` — returns "Thejus Mahajan", "Deep Learning with PyTorch", IBM, "August 29, 2026" |
| credential ID | **`DDDI9T0KHUJ4`** | same fetch |
| CNP exists | `Documents/cnp_synthetic`, commit `063bc6e` | `RESULTS.md` on disk: cnp CRPS 0.1677, gp_oracle 0.0379, ratio 4.4214, with `runs/*.log` behind it |

**You write no copy on this task.** Every LaTeX string and every HTML block is given verbatim
below. If you find yourself composing a sentence, you have left the task — **stop and report**.

### 0.2 ⛔ The honesty boundary — the constraint that outranks everything else here

The IBM course is **applied deep learning**: logistic and softmax regression, shallow networks,
dropout and batch normalisation, CNNs, transfer learning with ResNet18, GPU/CUDA training patterns.

**It contains NO Bayesian methods, NO uncertainty quantification, NO calibration, NO Gaussian
processes, NO neural processes.**

He is interviewing for a project whose entire point is probabilistic, and the credential ID you are
about to publish puts the syllabus one click from the panel. **Any wording implying the course
covers the probabilistic side is a career-damaging error.**

The probabilistic material on the CV comes from a *different* source — the CNP he implemented
himself — and the strings below keep those two things in separate lines on purpose. **Do not merge
them, do not move them next to each other, do not add a connecting phrase.**

### 0.3 ⛔ Which CVs change, and which are evidence

**Exactly two `.tex` files change.** They are named in §2.

**Every CV under `applications/` is a frozen record of what was sent.** The hereon CV says
*"2026 --- final module; certificate expected 09/2026"*. That was true on 27 August, the day it was
sent. If Hereon asks *"is this the CV you sent us?"*, the repository has to be able to answer yes.
**Editing it destroys evidence.** Do not open any of these:

```
applications/hereon_aeon_up/            applications/mpinat_scientific_it_specialist/
applications/roche_biostatistician_penzberg/   applications/helmholtz_munich/
applications/erlangen_stem_cell_biology/       applications/fzj_fairagro_rdm/
applications/geomar_zoom_in/                   applications/mdc_berlin_ludwig_lab/
applications/octapharma_molecular_design/      applications/robert_bosch_hospital/
applications/helmholtz_munich_staff_scientist/ applications/clinical_data_science_general/
applications/hamburg_welcome_center/           applications/mollman/
```

**The one exception is `applications/ml_interpretability_general/`**, which despite its location is
not a submitted application — it is the source of the website's primary CV download. It changes.

*Thejus said "update all the CVs." The leader's ruling: that means every CV that is still live.
Sent applications are records, and the seven never-sent drafts are stale artefacts that will be
regenerated from the live CV when he actually applies to those posts — updating them now is
polishing documents that reach nobody. If he wants the drafts refreshed anyway, that is a separate
instruction and a separate brief.*

### 0.4 The contract

`agents/README.md` applies in full: never invent a number, paste real command output, report every
deviation, stop and ask for anything this brief does not cover.

**Do not commit. Do not push. In either repository.** Leave both trees dirty; the leader audits the
diff. Report to `agents/reports/2026-08-29_pytorch-certificate-rollout_REPORT.md` in the
`chess_speak_out_loud` repo, wherever your workspace is rooted.

---

## 1. Baseline FIRST — before you edit anything

From the root of `bioinformatics_project/job_search`. **Paste the full output** into your report;
you compare against it in §2.5.

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

**Expected baseline, recorded by the leader — if yours disagrees, STOP and report:**

- both PDFs are **2 pages**
- `cv_ml_interpretability.pdf` md5 = `7f1f4987d03272e653172a6023e11d66`
- `assets/Thejus_Mahajan_CV_ML.pdf` md5 = `7f1f4987d03272e653172a6023e11d66` — **identical**. This
  is the fact that makes `cv_ml_interpretability.tex` the source of the site's primary download,
  and it is not the file the directory names would lead you to guess. Do not second-guess it.
- `cv_general_ml/cv_ml_general.pdf` md5 = `a1176876bdd171ae949ef006bae81fde`
- `git status --porcelain` is **empty except `?? applications/mollman/`** — pre-existing, leave it
  untracked. The certificate and the updated `study_room/12_pytorch_course.md` are already
  committed by the leader as `2b8da1a`.

Python is the `cszero` env: `C:\Users\Admin\miniconda3\envs\cszero\python.exe`.
LaTeX is TeX Live 2019 `pdflatex`, on PATH; both CVs were last built with it.

---

## 2. Part A — the two live CVs

Two edits per file. Both files get the same Further Training block; the Machine Learning line
differs slightly between them, so **each has its own FROM string — match them exactly.**

### 2.1 Edit 1 — the Further Training entry (identical in both files)

Insert this block as the **first** entry under `\cvsection{Further Training}`, immediately after
that line and the blank line following it, and **before** the existing
`\textbf{Deployable Data Analysis \& AI Pipelines with HPC}` entry. Newest first — the ordering
both files already use. Verbatim, including the trailing `\\[0.3cm]`:

```latex
\textbf{Deep Learning with PyTorch}\\
{\small IBM \textbar\ Coursera --- completed 08/2026\\
Credential DDDI9T0KHUJ4\\
CNNs, transfer learning, GPU/CUDA training patterns}\\[0.3cm]

```

The third line states the scope of the course. That is deliberate: it is §0.2 made visible on the
page, so the boundary is stated by him before a panel has to ask. **Do not shorten it, reword it,
or drop it.**

### 2.2 Edit 2 — the Machine Learning skills line

**File 1 — `applications/ml_interpretability_general/cv_ml_interpretability.tex`.**

FROM (one line, under `\cvskills{Machine Learning}`):
```latex
         {Transformers, attention/activation capture (forward hooks), mechanistic interpretability, ONNX$\rightarrow$PyTorch conversion, batched GPU inference, policy/value head analysis, tidymodels}
```
TO:
```latex
         {Transformers, attention/activation capture (forward hooks), mechanistic interpretability, ONNX$\rightarrow$PyTorch conversion, batched GPU inference, policy/value head analysis, conditional neural processes (implemented from scratch), uncertainty calibration (NLL, CRPS, ECE), tidymodels}
```

**File 2 — `cv_general_ml/cv_ml_general.tex`.** ⚠ **This one says "representation extraction"
where the other says "mechanistic interpretability".** Do not copy File 1's line into it.

FROM:
```latex
         {Transformers, attention/activation capture (forward hooks), representation extraction, ONNX$\rightarrow$PyTorch conversion, batched GPU inference, policy/value head analysis, tidymodels}
```
TO:
```latex
         {Transformers, attention/activation capture (forward hooks), representation extraction, ONNX$\rightarrow$PyTorch conversion, batched GPU inference, policy/value head analysis, conditional neural processes (implemented from scratch), uncertainty calibration (NLL, CRPS, ECE), tidymodels}
```

*Why these words and no others:* he implemented a CNP from scratch in PyTorch and evaluated it with
NLL, CRPS and ECE against a GP oracle and a climatology baseline — all three metrics are computed
in `cnp_synthetic/RESULTS.md` from logged runs. "Implemented from scratch" is the honest claim.
**There is no "Bayesian" and no "publication" in that line, and you may not add one.**

### 2.3 Nothing else in either file changes

Not the profile, not the summary, not the experience bullets, not the publications block, not the
languages. **Two edits per file, four edits total.**

### 2.4 Build

For each file, from the directory containing it:

```bash
pdflatex -interaction=nonstopmode <name>.tex
pdflatex -interaction=nonstopmode <name>.tex
```

Twice — the class uses `paracol` and geometry settles on the second pass. **Paste the last 15 lines
of each of the four runs.** Exit 0, and no `! LaTeX Error` or `! Undefined control sequence`.

### 2.5 Gates for Part A — run all five, paste all output

```bash
# G1 — the credential reached the page
pdftotext applications/ml_interpretability_general/cv_ml_interpretability.pdf - | grep -c "DDDI9T0KHUJ4"
pdftotext cv_general_ml/cv_ml_general.pdf - | grep -c "DDDI9T0KHUJ4"
# both must print 1

# G2 — the course title and the CNP both reached the page
for f in applications/ml_interpretability_general/cv_ml_interpretability.pdf cv_general_ml/cv_ml_general.pdf; do
  echo "== $f"
  pdftotext "$f" - | grep -c "Deep Learning with PyTorch"
  pdftotext "$f" - | grep -c "conditional neural processes"
done
# all four must print 1

# G3 — page count UNCHANGED. A 3-page CV is a failure, not a detail.
python -c "
from pypdf import PdfReader
for p in ['applications/ml_interpretability_general/cv_ml_interpretability.pdf',
          'cv_general_ml/cv_ml_general.pdf']:
    print(p, len(PdfReader(p).pages))
"
# both must print 2

# G4 — THE HONESTY GATE. The diff must contain no overclaim vocabulary.
git diff -U0 -- applications/ml_interpretability_general/cv_ml_interpretability.tex \
                cv_general_ml/cv_ml_general.tex \
  | grep -i -E "bayes|gaussian process|variational|posterior|publicat|expert|advanced|proficient"
# must return NOTHING (grep exit 1). Any hit means you wrote copy you were told not to write.

# G5 — scope
git status --porcelain
# beyond the pre-existing `?? applications/mollman/`, the ONLY paths listed may be:
#   the two .tex files, their two .pdf files, and their .aux/.log/.out build artefacts.
# If ANY file under applications/ other than ml_interpretability_general appears, you have
# broken §0.3 — revert it and report.
```

**If G3 returns 3 pages, STOP and report.** Do not delete something else to make room. What a CV
says is a leader decision.

---

## 3. Part B — the website

Workspace `C:\Users\Admin\Documents\thejusmahajan.github.io`, branch `main`.

> ### ⚑ AMENDED 2026-08-29 by the leader — PART A IS DONE. START HERE.
>
> **You already delivered Part A, and it was correct.** The diff matched the spec exactly in both
> files, G1, G2, G4 and G5 were re-run by the leader and are green, and **you were right to halt at
> G3** — `cv_ml_general.pdf` really did come out at 3 pages. Stopping instead of improvising a fix
> was the correct call and it is the second time in two days a checkpoint has caught something.
> Do not redo Part A.
>
> **The leader fixed the overflow.** Page 3 held nothing but the signature block, so it was a
> marginal spill: the pre-signature `\vspace{0.3cm}` became `\vspace{0.05cm}`, and the credential
> moved onto the issuer line in *that file only*. **No content was cut.** Rebuilt, re-gated, and
> visually checked at 90 dpi — `cv_ml_general.pdf` is now 2 pages with the signature block sitting
> normally. Both CVs are green.
>
> **The sequencing rule in this section is lifted.** It was written before the leader knew the
> failure would be isolated to `cv_general_ml`, which Part B never touches. Part B depends only on
> `cv_ml_interpretability.pdf`, which has been 2 pages and green throughout.
>
> **Do §3.1 through §3.4 now.** Everything below is unchanged. Do not touch either `.tex` file
> again — `git status` in `job_search` is expected to show both CVs modified; that is the leader's
> and your work, already audited. Leave it dirty and do not stage or commit it.

### 3.1 Refresh the downloadable CV

```bash
cp ../bioinformatics_project/job_search/applications/ml_interpretability_general/cv_ml_interpretability.pdf \
   assets/Thejus_Mahajan_CV_ML.pdf
md5sum assets/Thejus_Mahajan_CV_ML.pdf \
       ../bioinformatics_project/job_search/applications/ml_interpretability_general/cv_ml_interpretability.pdf
```

**G6: the two md5s must be identical to each other and must DIFFER from
`7f1f4987d03272e653172a6023e11d66`.** The baseline hash means you copied the stale file.

⛔ **`assets/Thejus_Mahajan_CV.pdf` and `assets/Thejus_Mahajan_CV_DE.pdf` have no source `.tex`
anywhere** — the leader hashed every PDF in `job_search` and searched `Documents/cv`; neither
matches and no source exists. **Do not touch them, do not attempt to regenerate them, do not
delete their download buttons.** It is an open question for Thejus, recorded in `state/NOW.md`.

### 3.2 `experience.html` — the Certifications card

Section 4, *"Certifications & Training"* (the `<h2>` is near line 254). Two exact changes.

**(a)** The grid holds four cards and is about to hold five. Change the class so they lay out
three-then-two instead of stranding one:

```
FROM:  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
TO:    <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
```

There is exactly one such `<div>` inside this section. **Change no other grid on the site.**

**(b)** Insert as the **first** card in that grid — immediately after the opening `<div>` above,
before the existing *"Goethe-Zertifikat B1"* card:

```html
                <div class="bg-white border border-gray-100 shadow-sm rounded-lg p-5 text-center hover:shadow-md hover:border-sky-100 transition-all">
                    <h4 class="font-bold text-gray-800 text-sm mb-1">Deep Learning with PyTorch</h4>
                    <p class="text-xs text-gray-600">IBM on Coursera, August 2026 &middot; <a href="https://coursera.org/verify/DDDI9T0KHUJ4" target="_blank" rel="noopener noreferrer" class="text-sky-700 hover:underline">verify</a></p>
                </div>
```

### 3.3 `skills.html` — the real gap

**The skills page contains no ML content at all.** No PyTorch, no deep learning, no machine
learning. The Python card says "Data science, automation, and bioinformatics pipelines". Meanwhile
`index.html` headlines "Machine Learning" and offers the ML CV as the primary download. Three
changes, all verbatim.

**(a) The page subtitle**, line ~55.

FROM:
```html
            <p class="text-xl text-gray-600 max-w-2xl mx-auto">Tools and methods for clinical bioinformatics, biostatistics, and computational research</p>
```
TO:
```html
            <p class="text-xl text-gray-600 max-w-2xl mx-auto">Tools and methods for machine learning, computational modelling, clinical bioinformatics and biostatistics</p>
```

**(b) The Python card**, in Section 4 *Programming Languages*.

FROM:
```html
                    <p class="text-sm text-gray-600 mb-4 italic">Data science, automation, and bioinformatics pipelines</p>
                    <div class="text-sm text-gray-900 font-semibold mb-1">Tools & Packages:</div>
                    <p class="text-sm text-gray-600">Pandas, NumPy, scikit-learn, matplotlib, seaborn, xarray</p>
```
TO:
```html
                    <p class="text-sm text-gray-600 mb-4 italic">Deep learning, scientific computing, data science and bioinformatics pipelines</p>
                    <div class="text-sm text-gray-900 font-semibold mb-1">Tools & Packages:</div>
                    <p class="text-sm text-gray-600">PyTorch, ONNX, JAX, NumPy, Pandas, scikit-learn, xarray, FastAPI, matplotlib, seaborn</p>
```

**(c) A new section**, inserted **immediately before** the `<!-- Section 3: Bioinformatics -->`
comment, so it sits between Biostatistics and Bioinformatics. It copies the structure of the
Biostatistics section exactly, including the `border-l-4 border-sky-600` accent:

```html
        <!-- Section 2b: Machine Learning & Deep Learning -->
        <section class="mb-12">
            <div class="bg-white rounded-xl shadow-sm border-l-4 border-sky-600 p-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-6">Machine Learning & Deep Learning</h2>
                <div class="flex flex-wrap gap-3">
                    <span class="bg-sky-50 text-sky-700 px-4 py-2 rounded-full font-medium text-sm border border-sky-100">PyTorch</span>
                    <span class="bg-sky-50 text-sky-700 px-4 py-2 rounded-full font-medium text-sm border border-sky-100">Transformers &amp; Attention</span>
                    <span class="bg-sky-50 text-sky-700 px-4 py-2 rounded-full font-medium text-sm border border-sky-100">Mechanistic Interpretability</span>
                    <span class="bg-sky-50 text-sky-700 px-4 py-2 rounded-full font-medium text-sm border border-sky-100">Forward Hooks &amp; Activation Capture</span>
                    <span class="bg-sky-50 text-sky-700 px-4 py-2 rounded-full font-medium text-sm border border-sky-100">ONNX &rarr; PyTorch Conversion</span>
                    <span class="bg-sky-50 text-sky-700 px-4 py-2 rounded-full font-medium text-sm border border-sky-100">CNNs &amp; Transfer Learning</span>
                    <span class="bg-sky-50 text-sky-700 px-4 py-2 rounded-full font-medium text-sm border border-sky-100">Conditional Neural Processes</span>
                    <span class="bg-sky-50 text-sky-700 px-4 py-2 rounded-full font-medium text-sm border border-sky-100">Uncertainty Calibration (NLL, CRPS, ECE)</span>
                    <span class="bg-sky-50 text-sky-700 px-4 py-2 rounded-full font-medium text-sm border border-sky-100">Batched GPU Inference</span>
                    <span class="bg-sky-50 text-sky-700 px-4 py-2 rounded-full font-medium text-sm border border-sky-100">Tidymodels &amp; scikit-learn</span>
                </div>
            </div>
        </section>

```

**No other page changes.** Not `index.html`, not `projects.html`, not the blog, not the meta
descriptions. If you think another page needs it, **say so in the report and do not do it.**

### 3.4 Gates for Part B — run all, paste all output

```bash
# G7 — the certification card is present exactly once
grep -c "DDDI9T0KHUJ4" experience.html                  # must be 1
grep -c "Deep Learning with PyTorch" experience.html    # must be 1

# G8 — the grid change is confined to the Certifications section
grep -n "md:grid-cols-4" skills.html experience.html
grep -n "md:grid-cols-3" experience.html
# report all; the Certifications grid must be the ONLY one that went 4 -> 3.
# skills.html still has a md:grid-cols-4 (Tools & Platforms) and it must STAY 4.

# G9 — the skills page now has ML content
grep -c "Machine Learning &amp; Deep Learning" skills.html   # must be 1
grep -c "PyTorch" skills.html                                # must be >= 2
grep -c "Conditional Neural Processes" skills.html           # must be 1

# G10 — no stray HTML. Every opened tag in the inserted blocks is closed.
python -c "
import html.parser, sys
class P(html.parser.HTMLParser):
    def __init__(s): super().__init__(); s.stack=[]; s.void={'br','img','meta','link','input','hr'}
    def handle_starttag(s,t,a):
        if t not in s.void: s.stack.append(t)
    def handle_endtag(s,t):
        if s.stack and s.stack[-1]==t: s.stack.pop()
        elif t in s.stack: print('MISMATCH', t, s.stack[-5:]); s.stack.remove(t)
for f in ['skills.html','experience.html']:
    p=P(); p.feed(open(f,encoding='utf-8').read())
    print(f, 'unclosed:', p.stack)
"
# 'unclosed: []' for both, or report exactly what it prints

# G11 — scope
git status --porcelain
# ONLY experience.html, skills.html and assets/Thejus_Mahajan_CV_ML.pdf may be listed
```

**G12 — LOOK AT IT.** Open `skills.html` and `experience.html` in a browser. **Screenshot both**:
the new Machine Learning section, and the Certifications & Training row. Confirm in your own words —
five certification cards laid out 3 + 2, no card overflowing; the ML section matching the
Biostatistics section's styling; the *verify* link visible and clickable; nothing overlapping at a
narrow window width.

*This project has three recorded cases of correct content shipped where nobody could see it. A grep
is not a pair of eyes.*

---

## 4. What to report

`agents/reports/2026-08-29_pytorch-certificate-rollout_REPORT.md`, in `chess_speak_out_loud`:

1. The §1 baseline output, pasted.
2. The full `git diff` of both `.tex` files and both `.html` files.
3. The last 15 lines of all four `pdflatex` runs.
4. **G1–G12, each with its command and its real output.** A gate reported without output counts as
   not run.
5. The two G12 screenshots.
6. Every deviation, and every point where you stopped and asked.
7. Final `git status --porcelain` for **both** repositories.

**Do not commit and do not push. Neither repo.**

---

## 5. Out of scope — report if you notice, do not act

- `Thejus_Mahajan_CV.pdf` / `_DE.pdf` have no source. Open question for Thejus.
- The German CV has not been updated and must **not** be machine-translated — he is B1 and would
  have to defend the wording in an interview. It needs a native pass.
- LinkedIn is edited by hand, by Thejus. **Nothing on LinkedIn is ever automated.**
- The `hereon-aeon-up` trainer ladder may deserve a card about the completed certificate. **Card
  content is written by the leader, never by a worker** — five fabricated deliveries on this
  project came from asking a worker for content.
- `cnp_synthetic` has 5 modified files and 1 untracked at `db3eb90`. Different repo, different task.
