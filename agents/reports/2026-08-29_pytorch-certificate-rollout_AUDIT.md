# AUDIT — 2026-08-29 PyTorch certificate rollout, Part A

**Auditor:** the leader (Opus 5), 2026-08-29
**Delivery:** `agents/reports/2026-08-29_pytorch-certificate-rollout_REPORT.md`
**Verdict: ✅ AUDITED ACCEPT for Part A, with an honest halt at G3 that the leader then resolved.
Part B is unblocked and handed back.**

---

## 1. The diff is ground truth, and the diff is exactly to spec

Eleven added lines across two files, and every one of them was specified verbatim in the brief:

- `cv_ml_interpretability.tex` — Machine Learning line extended with `conditional neural processes
  (implemented from scratch), uncertainty calibration (NLL, CRPS, ECE)`; the four-line Further
  Training block inserted first under `\cvsection{Further Training}`.
- `cv_ml_general.tex` — the same two edits, and **correctly using the different FROM string**
  (`representation extraction`, not `mechanistic interpretability`). This was the trap in the brief
  and the worker did not fall into it.

**No file outside the two named `.tex` files was touched.** `git status` in `job_search` lists only
those two, their PDFs and their build artefacts, plus the pre-existing untracked
`applications/mollman/`. **No frozen application CV was opened** — the §0.3 rail held.

## 2. Gates re-run by the leader, not read from the report

| gate | result |
|---|---|
| G1 credential on the page | `1` and `1` — both PDFs |
| G2 course title | `1` and `1` |
| G2 CNP present | `1` and `1` |
| G3 page count | **`cv_ml_interpretability` 2 ✅ / `cv_ml_general` 3 ❌** — the halt |
| G4 honesty gate | **clean** on added lines |
| G5 scope | clean |

**On G4 — a caveat worth recording.** Run as written, `git diff -U0 \| grep -i ... publicat`
returns a hit. It is a **hunk-header context line** (`@@ ... Five peer-reviewed publications ...`),
not added text. Re-run against added lines only (`grep "^+" | grep -v "^+++"`) it is clean. *The
gate as I wrote it is capable of a false positive; that is a defect in my brief, not in the
delivery.* Filtering to `^+` is the correct form and future briefs should use it.

## 3. The halt was correct behaviour

`cv_ml_general.pdf` compiled to 3 pages. The brief said: *"If G3 returns 3 pages, STOP and report.
Do not delete something else to make room. What a CV says is a leader decision."*

The worker stopped, reported it as a failure with the real `pdflatex` output showing
`(3 pages, 242383 bytes)`, did not start Part B, and did not invent a fix. **It did not claim
success it had not earned.** That is the second consecutive delivery where a checkpoint caught a
problem instead of a fabrication reaching the leader — the 2026-08-29 trainer brief was the first,
where the worker stopped rather than improvise around a wrong instruction in Step 2.1.

## 4. What the leader did about it

Page 3 contained **44 characters** — `Hamburg, 19 August 2026 / Dr. Thejus Mahajan`, the signature
block and nothing else. A marginal spill, not a content problem.

Fix, in `cv_ml_general.tex` only:
1. `\vspace{0.3cm}` before the signature minipage → `\vspace{0.05cm}`.
2. The credential moved onto the issuer line: `IBM | Coursera --- completed 08/2026 (DDDI9T0KHUJ4)`.

**No content was cut.** Rebuilt twice, re-gated — G1/G2 still `1` across the board, **G3 now 2 and
2** — and page 2 rendered at 90 dpi and looked at: the signature sits normally above the bottom
margin, and the Further Training block reads correctly.

*Step 2 alone did not fix it; step 1 did. Recorded because the obvious remedy — compress the text —
was the one that failed, and 0.25 cm of whitespace was the one that worked.*

## 5. Open, and not fixed here

- **`cv_ml_general.tex` is dated "Hamburg, 19 August 2026".** Stale. The convention is to update the
  date every time the CV is sent; it is not a build problem and it is not the worker's to guess.
- **Part B was never started.** Handed back with the brief amended at §3.
- The two site CVs with no source, unchanged from this morning.
