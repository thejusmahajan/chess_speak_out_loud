# Report: PyTorch Certificate Rollout

**Brief:** `agents/briefs/2026-08-29_pytorch-certificate-rollout.md`  
**Date:** 2026-08-29  
**Auditor / Worker:** Gemini 3.7 Flash (High) (Antigravity IDE)  
**Status:** HALTED AT G3 (cv_ml_general.pdf is 3 pages) — STOP AND REPORT PER §2.5 & §3

---

## 1. Baseline Output (§1)

Run from `bioinformatics_project/job_search`:

```
applications/ml_interpretability_general/cv_ml_interpretability.pdf 2 pages
cv_general_ml/cv_ml_general.pdf 2 pages
7f1f4987d03272e653172a6023e11d66 *applications/ml_interpretability_general/cv_ml_interpretability.pdf
a1176876bdd171ae949ef006bae81fde *cv_general_ml/cv_ml_general.pdf
7f1f4987d03272e653172a6023e11d66 *../../thejusmahajan.github.io/assets/Thejus_Mahajan_CV_ML.pdf
?? applications/mollman/
```

---

## 2. Git Diff

### `bioinformatics_project/job_search` (`.tex` files)

```diff
warning: in the working copy of 'cv_general_ml/cv_ml_general.tex', LF will be replaced by CRLF the next time Git touches it
diff --git a/applications/ml_interpretability_general/cv_ml_interpretability.tex b/applications/ml_interpretability_general/cv_ml_interpretability.tex
index 2bbaa6d..db14a83 100644
--- a/applications/ml_interpretability_general/cv_ml_interpretability.tex
+++ b/applications/ml_interpretability_general/cv_ml_interpretability.tex
@@ -155,7 +155,7 @@ Relocation from India to Germany and active job search.
          {Python (PyTorch, ONNX, JAX, NumPy, Pandas, FastAPI), R (tidyverse, Shiny, tidymodels, Bioconductor), SQL, TypeScript, Fortran, C++, BASH}
 
 \cvskills{Machine Learning}
-         {Transformers, attention/activation capture (forward hooks), mechanistic interpretability, ONNX$\rightarrow$PyTorch conversion, batched GPU inference, policy/value head analysis, tidymodels}
+         {Transformers, attention/activation capture (forward hooks), mechanistic interpretability, ONNX$\rightarrow$PyTorch conversion, batched GPU inference, policy/value head analysis, conditional neural processes (implemented from scratch), uncertainty calibration (NLL, CRPS, ECE), tidymodels}
 
 \cvskills{Clinical Data \& Biostatistics}
          {Medical registry pipelines, GDPR/DSGVO compliance, multivariate analysis, PCA, ANOVA, survival analysis concepts, clinical endpoints}
@@ -181,6 +181,11 @@ Relocation from India to Germany and active job search.
 
 \cvsection{Further Training}
 
+\textbf{Deep Learning with PyTorch}\\
+{\small IBM \textbar\ Coursera --- completed 08/2026\\
+Credential DDDI9T0KHUJ4\\
+CNNs, transfer learning, GPU/CUDA training patterns}\\[0.3cm]
+
 \textbf{Deployable Data Analysis \& AI Pipelines with HPC}\\
 {\small Supercomputing-Akademie, HLRS\\
 Universit\"at Stuttgart \textbar\ 09--10/2026 (enrolled)}\\[0.3cm]
diff --git a/cv_general_ml/cv_ml_general.tex b/cv_general_ml/cv_ml_general.tex
index 5693f16..fc5bde2 100644
--- a/cv_general_ml/cv_ml_general.tex
+++ b/cv_general_ml/cv_ml_general.tex
@@ -155,7 +155,7 @@ Relocation from India to Germany and active job search.
          {Python (PyTorch, ONNX, JAX, NumPy, Pandas, FastAPI), R (tidyverse, Shiny, tidymodels, Bioconductor), SQL, TypeScript, Fortran, C++, BASH}
 
 \cvskills{Machine Learning}
-         {Transformers, attention/activation capture (forward hooks), representation extraction, ONNX$\rightarrow$PyTorch conversion, batched GPU inference, policy/value head analysis, tidymodels}
+         {Transformers, attention/activation capture (forward hooks), representation extraction, ONNX$\rightarrow$PyTorch conversion, batched GPU inference, policy/value head analysis, conditional neural processes (implemented from scratch), uncertainty calibration (NLL, CRPS, ECE), tidymodels}
 
 \cvskills{Clinical Data \& Biostatistics}
          {Medical registry pipelines, GDPR/DSGVO compliance, multivariate analysis, PCA, ANOVA, survival analysis concepts, clinical endpoints}
@@ -184,6 +184,11 @@ Relocation from India to Germany and active job search.
 
 \cvsection{Further Training}
 
+\textbf{Deep Learning with PyTorch}\\
+{\small IBM \textbar\ Coursera --- completed 08/2026\\
+Credential DDDI9T0KHUJ4\\
+CNNs, transfer learning, GPU/CUDA training patterns}\\[0.3cm]
+
 \textbf{Deployable Data Analysis \& AI Pipelines with HPC}\\
 {\small Supercomputing-Akademie, HLRS\\
 Universit\"at Stuttgart \textbar\ 09--10/2026 (place confirmed)}\\[0.3cm]
```

### `thejusmahajan.github.io` (`.html` files)

*None — Part B was not started per §3: "Part A must be finished and its gates green first — Part B copies Part A's build output."*

---

## 3. LaTeX Builds (§2.4) — Last 15 Lines of All 4 Runs

### Run 1: `applications/ml_interpretability_general/cv_ml_interpretability.tex` (Pass 1)

```
live/2019/texmf-dist/fonts/enc/dvips/fontawesome5/fa5free3.enc}{c:/texlive/2019
/texmf-dist/fonts/enc/dvips/fontawesome5/fa5free0.enc}{c:/texlive/2019/texmf-di
st/fonts/enc/dvips/fontawesome5/fa5free2.enc}<c:/texlive/2019/texmf-dist/fonts/
type1/public/fontawesome5/FontAwesome5Brands-Regular.pfb><c:/texlive/2019/texmf
-dist/fonts/type1/public/fontawesome5/FontAwesome5Free-Solid.pfb><c:/texlive/20
19/texmf-dist/fonts/type1/public/amsfonts/cm/cmmi6.pfb><c:/texlive/2019/texmf-d
ist/fonts/type1/public/amsfonts/cm/cmr6.pfb><c:/texlive/2019/texmf-dist/fonts/t
ype1/public/amsfonts/cm/cmsy10.pfb><c:/texlive/2019/texmf-dist/fonts/type1/publ
ic/amsfonts/cm/cmsy8.pfb><c:/texlive/2019/texmf-dist/fonts/type1/public/amsfont
s/cm/cmsy9.pfb><c:/texlive/2019/texmf-dist/fonts/type1/public/tex-gyre/qhvb.pfb
><c:/texlive/2019/texmf-dist/fonts/type1/public/tex-gyre/qhvr.pfb><c:/texlive/2
019/texmf-dist/fonts/type1/public/tex-gyre/qhvri.pfb><c:/texlive/2019/texmf-dis
t/fonts/type1/public/cm-super/sftt0800.pfb>
Output written on cv_ml_interpretability.pdf (2 pages, 242123 bytes).
Transcript written on cv_ml_interpretability.log.
```

### Run 2: `applications/ml_interpretability_general/cv_ml_interpretability.tex` (Pass 2)

```
live/2019/texmf-dist/fonts/enc/dvips/fontawesome5/fa5free3.enc}{c:/texlive/2019
/texmf-dist/fonts/enc/dvips/fontawesome5/fa5free0.enc}{c:/texlive/2019/texmf-di
st/fonts/enc/dvips/fontawesome5/fa5free2.enc}<c:/texlive/2019/texmf-dist/fonts/
type1/public/fontawesome5/FontAwesome5Brands-Regular.pfb><c:/texlive/2019/texmf
-dist/fonts/type1/public/fontawesome5/FontAwesome5Free-Solid.pfb><c:/texlive/20
19/texmf-dist/fonts/type1/public/amsfonts/cm/cmmi6.pfb><c:/texlive/2019/texmf-d
ist/fonts/type1/public/amsfonts/cm/cmr6.pfb><c:/texlive/2019/texmf-dist/fonts/t
ype1/public/amsfonts/cm/cmsy10.pfb><c:/texlive/2019/texmf-dist/fonts/type1/publ
ic/amsfonts/cm/cmsy8.pfb><c:/texlive/2019/texmf-dist/fonts/type1/public/amsfont
s/cm/cmsy9.pfb><c:/texlive/2019/texmf-dist/fonts/type1/public/tex-gyre/qhvb.pfb
><c:/texlive/2019/texmf-dist/fonts/type1/public/tex-gyre/qhvr.pfb><c:/texlive/2
019/texmf-dist/fonts/type1/public/tex-gyre/qhvri.pfb><c:/texlive/2019/texmf-dis
t/fonts/type1/public/cm-super/sftt0800.pfb>
Output written on cv_ml_interpretability.pdf (2 pages, 242123 bytes).
Transcript written on cv_ml_interpretability.log.
```

### Run 3: `cv_general_ml/cv_ml_general.tex` (Pass 1)

```
live/2019/texmf-dist/fonts/enc/dvips/fontawesome5/fa5free3.enc}{c:/texlive/2019
/texmf-dist/fonts/enc/dvips/fontawesome5/fa5free0.enc}{c:/texlive/2019/texmf-di
st/fonts/enc/dvips/fontawesome5/fa5free2.enc}<c:/texlive/2019/texmf-dist/fonts/
type1/public/fontawesome5/FontAwesome5Brands-Regular.pfb><c:/texlive/2019/texmf
-dist/fonts/type1/public/fontawesome5/FontAwesome5Free-Solid.pfb><c:/texlive/20
19/texmf-dist/fonts/type1/public/amsfonts/cm/cmmi6.pfb><c:/texlive/2019/texmf-d
ist/fonts/type1/public/amsfonts/cm/cmr6.pfb><c:/texlive/2019/texmf-dist/fonts/t
ype1/public/amsfonts/cm/cmsy10.pfb><c:/texlive/2019/texmf-dist/fonts/type1/publ
ic/amsfonts/cm/cmsy8.pfb><c:/texlive/2019/texmf-dist/fonts/type1/public/amsfont
s/cm/cmsy9.pfb><c:/texlive/2019/texmf-dist/fonts/type1/public/tex-gyre/qhvb.pfb
><c:/texlive/2019/texmf-dist/fonts/type1/public/tex-gyre/qhvr.pfb><c:/texlive/2
019/texmf-dist/fonts/type1/public/tex-gyre/qhvri.pfb><c:/texlive/2019/texmf-dis
t/fonts/type1/public/cm-super/sftt0800.pfb>
Output written on cv_ml_general.pdf (3 pages, 242383 bytes).
Transcript written on cv_ml_general.log.
```

### Run 4: `cv_general_ml/cv_ml_general.tex` (Pass 2)

```
live/2019/texmf-dist/fonts/enc/dvips/fontawesome5/fa5free3.enc}{c:/texlive/2019
/texmf-dist/fonts/enc/dvips/fontawesome5/fa5free0.enc}{c:/texlive/2019/texmf-di
st/fonts/enc/dvips/fontawesome5/fa5free2.enc}<c:/texlive/2019/texmf-dist/fonts/
type1/public/fontawesome5/FontAwesome5Brands-Regular.pfb><c:/texlive/2019/texmf
-dist/fonts/type1/public/fontawesome5/FontAwesome5Free-Solid.pfb><c:/texlive/20
19/texmf-dist/fonts/type1/public/amsfonts/cm/cmmi6.pfb><c:/texlive/2019/texmf-d
ist/fonts/type1/public/amsfonts/cm/cmr6.pfb><c:/texlive/2019/texmf-dist/fonts/t
ype1/public/amsfonts/cm/cmsy10.pfb><c:/texlive/2019/texmf-dist/fonts/type1/publ
ic/amsfonts/cm/cmsy8.pfb><c:/texlive/2019/texmf-dist/fonts/type1/public/amsfont
s/cm/cmsy9.pfb><c:/texlive/2019/texmf-dist/fonts/type1/public/tex-gyre/qhvb.pfb
><c:/texlive/2019/texmf-dist/fonts/type1/public/tex-gyre/qhvr.pfb><c:/texlive/2
019/texmf-dist/fonts/type1/public/tex-gyre/qhvri.pfb><c:/texlive/2019/texmf-dis
t/fonts/type1/public/cm-super/sftt0800.pfb>
Output written on cv_ml_general.pdf (3 pages, 242383 bytes).
Transcript written on cv_ml_general.log.
```

---

## 4. Gates (G1–G12)

### G1 — Credential reached the page
**Command:**
```bash
pdftotext applications/ml_interpretability_general/cv_ml_interpretability.pdf - | grep -c "DDDI9T0KHUJ4"
pdftotext cv_general_ml/cv_ml_general.pdf - | grep -c "DDDI9T0KHUJ4"
```
**Output:**
```
1
1
```
**Status:** PASS

---

### G2 — Course title and CNP reached the page
**Command:**
```bash
for f in applications/ml_interpretability_general/cv_ml_interpretability.pdf cv_general_ml/cv_ml_general.pdf; do
  echo "== $f"
  pdftotext "$f" - | grep -c "Deep Learning with PyTorch"
  pdftotext "$f" - | grep -c "conditional neural processes"
done
```
**Output:**
```
== applications/ml_interpretability_general/cv_ml_interpretability.pdf
1
1
== cv_general_ml/cv_ml_general.pdf
1
1
```
**Status:** PASS

---

### G3 — Page count UNCHANGED (Must both be 2 pages)
**Command:**
```bash
python -c "
from pypdf import PdfReader
for p in ['applications/ml_interpretability_general/cv_ml_interpretability.pdf',
          'cv_general_ml/cv_ml_general.pdf']:
    print(p, len(PdfReader(p).pages))
"
```
**Output:**
```
applications/ml_interpretability_general/cv_ml_interpretability.pdf 2
cv_general_ml/cv_ml_general.pdf 3
```
**Status:** ❌ **FAILED — STOP AND REPORT TRIGGERED**

*Explanation:* In `cv_general_ml/cv_ml_general.tex`, adding the 4-line `Deep Learning with PyTorch` Further Training block alongside the expanded Machine Learning skills line caused the content of page 2 to overflow, pushing the signature block onto a 3rd page (`cv_ml_general.pdf` is 3 pages). Per §2.5: *"If G3 returns 3 pages, STOP and report. Do not delete something else to make room. What a CV says is a leader decision."*

---

### G4 — The Honesty Gate (No overclaim vocabulary in diff)
**Command:**
```bash
git diff -U0 -- applications/ml_interpretability_general/cv_ml_interpretability.tex \
                cv_general_ml/cv_ml_general.tex \
  | grep -i -E "bayes|gaussian process|variational|posterior|publicat|expert|advanced|proficient"
```
**Output:**
```
(no output, grep exited with code 1)
```
**Status:** PASS

---

### G5 — Scope
**Command:**
```bash
git status --porcelain
```
**Output:**
```
 M applications/ml_interpretability_general/cv_ml_interpretability.aux
 M applications/ml_interpretability_general/cv_ml_interpretability.log
 M applications/ml_interpretability_general/cv_ml_interpretability.pdf
 M applications/ml_interpretability_general/cv_ml_interpretability.tex
 M cv_general_ml/cv_ml_general.pdf
 M cv_general_ml/cv_ml_general.tex
?? applications/mollman/
```
**Status:** PASS (Only target directories touched; untracked `applications/mollman/` is pre-existing).

---

### G6 to G12 — Part B Gates
**Status:** **NOT RUN**  
Per §3 of the brief: *"Part A must be finished and its gates green first — Part B copies Part A's build output."* Because Gate G3 failed with a 3-page compilation for `cv_ml_general.pdf`, Part B was halted as instructed.

---

## 5. Deviations & Stop Points

1. **Gate G3 Failure (Page Count Overflow on `cv_ml_general.pdf`):**
   - After inserting the verbatim Further Training block and the verbatim Machine Learning skills line into `cv_general_ml/cv_ml_general.tex`, compiling with `pdflatex` produced a 3-page document (page 3 contains the trailing signature block).
   - In accordance with the explicit brief instruction (§2.5: *"If G3 returns 3 pages, STOP and report. Do not delete something else to make room. What a CV says is a leader decision."*) and the workspace contract (§0.4 / `agents/README.md`), execution was stopped immediately.
   - No copy was altered or removed to force the layout onto 2 pages.
   - Part B was not initiated because Part A gates did not pass green.

---

## 6. Final `git status --porcelain` for Both Repositories

### Repository 1: `bioinformatics_project/job_search`

```
 M applications/ml_interpretability_general/cv_ml_interpretability.aux
 M applications/ml_interpretability_general/cv_ml_interpretability.log
 M applications/ml_interpretability_general/cv_ml_interpretability.pdf
 M applications/ml_interpretability_general/cv_ml_interpretability.tex
 M cv_general_ml/cv_ml_general.pdf
 M cv_general_ml/cv_ml_general.tex
?? applications/mollman/
```

### Repository 2: `thejusmahajan.github.io`

```
(clean - no modifications)
```
