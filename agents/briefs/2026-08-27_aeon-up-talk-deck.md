# BRIEF — build the AEON-UP interview deck (Beamer) from the written script

**Filed:** 2026-08-27 by the leader
**Worker:** Gemini, in Antigravity
**Status:** ACTIVE

**Why this before the interview?** It *is* the interview. Helmholtz panels ask for a talk, often at
short notice, and no deck exists.

---

## 0. The one rule that governs this brief

**You are building a deck, not writing one.** All content is already written and is not yours to
change.

**Source of truth:**
`C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\study_room\14_talk_script.md`

- **Copy the slide text from §3 of that file verbatim.** Do not rewrite, condense, "improve",
  reorder, or add a slide. Do not invent a bullet because a slide looks thin.
- The `**Say:**` lines in the script are **spoken words, not slide text.** They go in the Beamer
  **`\note{}`** for that frame, never on the slide.
- The `**Do not**` / `❌` lines are instructions to the author. They appear **nowhere** in output.
- **Every number** on a slide must match `14_talk_script.md` character for character. Three
  documents have been rejected on this project for numbers that were not traceable. Check the
  table on slide 9 twice.
- If the script is ambiguous, **stop and ask.** Do not resolve it yourself.

This split is deliberate: the content is the leader's, the LaTeX is yours.

---

## 1. Environment

- TeX Live 2019 is on PATH at `/c/texlive/2019/bin/win32`. `pdflatex` works; the CV and the
  certificate bundle were both built with it.
- The terminal is **PowerShell 5.1** — `&&` and `||` do not exist. Chain with `;` or
  `A; if ($?) { B }`.
- Build in a **new** directory:
  `C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\talk\`
- Main file: `talk\aeon_up_talk.tex`. Output: `talk\aeon_up_talk.pdf`.
- **Do not modify anything outside `talk\`.** `14_talk_script.md` is read-only to you.

---

## 2. Figures — use these exact files, and no others

Copy them into `talk\figures\`; do not edit the originals, and do not generate new plots.

| slide | file | source |
|---|---|---|
| 7 (side by side) | `bt3_attention_mirrored.svg` **and** `bt3_attention_corrected.svg` | `C:\Users\Admin\Documents\chess_speak_out_loud\docs\figures\` |
| 9 | `fig2_calibration.png` | `C:\Users\Admin\Documents\cnp_synthetic\figures\` |
| B1 | `fig4_loso.png` | same |
| B2 | `fig3_city_field.png` | same |
| B3 | `fig1_1d_fit.png` | same |

**The two SVGs need converting** — `pdflatex` cannot include SVG. Convert to PDF (Inkscape, or
`cairosvg`, or `rsvg-convert`; `cairosvg` installs into the `cszero` env if nothing else is
available). Keep the vector form — **do not rasterise to PNG.** State in your report which tool you
used.

**If a figure will not convert or render, STOP and report it.** Do not substitute a different
figure, and do not leave a slide with a missing-image box.

---

## 3. Build it

1. **`beamer`, 16:9** (`\documentclass[aspectratio=169]{beamer}`).
2. A **clean, plain theme** — `metropolis` if available, otherwise `default` with
   `\setbeamertemplate{navigation symbols}{}`. **No institutional logos, no Hereon branding**: this
   is his talk, not theirs, and using their logo uninvited looks presumptuous.
3. **Slide numbers** in the footer (`\insertframenumber`). Panels refer to slides by number.
4. **13 content frames**, in the script's order, titled as in §3. Then a `\appendix` and the
   **7 backup frames** from §4 of the script.
5. Body text **no smaller than 18pt at 16:9**. If a slide does not fit, **stop and ask** — do not
   shrink the font and do not cut text.
6. `\note{}` on every content frame, carrying that slide's `**Say:**` line and its timing budget.
   Also produce a **second PDF with notes shown**: `aeon_up_talk_notes.pdf`
   (`\setbeameroption{show notes}`). Two PDFs, one source file.
7. Slide 9's table: use `booktabs`. Right-align the numbers. Bold nothing — the script bolds
   nothing there.
8. Slide 7 places the two SVGs **side by side, mirrored on the left, corrected on the right**, each
   captioned only `before` / `after`.

---

## ✅ CHECKPOINT A — after the build

Paste all of it:

```powershell
cd C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\talk
pdflatex -interaction=nonstopmode aeon_up_talk.tex | Select-String -Pattern "Output written","Error","Warning" -Context 0,1
Get-ChildItem *.pdf | Select-Object Name, Length
```

**Pass:** both PDFs exist, `aeon_up_talk.pdf` reports **20 pages** (13 content + 7 backup), and the
log contains **no** `Error` and no missing-file warning.
**If the page count is not 20, do not adjust the count to match — report the discrepancy.**

---

## ✅ CHECKPOINT B — the numbers gate

The single most likely failure on this deck is a transcription error in the slide-9 table.

Extract the text of the built PDF and prove each number survives:

```powershell
cd C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\talk
& "C:\Users\Admin\miniconda3\envs\cszero\python.exe" -c "import sys;sys.exit(0)"
```

Then, with any PDF-text tool available in `cszero` (`pypdf`, `pdfminer.six` — install into `cszero`
if absent, and say so in the report), dump the text of the slide-9 page and paste it, followed by:

```powershell
Select-String -Path C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\study_room\14_talk_script.md -Pattern "0.1532","0.1677","0.0214","0.2865","-1.8676","0.0379","0.0040","0.0716","1.1223","0.4442","0.0527","0.7387"
```

**Pass:** all twelve numbers appear in the PDF text dump **and** in the script, identically.
**Any mismatch: fix the deck to match the script, never the script to match the deck.**

---

## ✅ CHECKPOINT C — the boundary gate

§5 of the script lists what must never appear. Prove none of it did:

```powershell
cd C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\talk
Select-String -Path aeon_up_talk.tex -Pattern 'CMAQ','EPISODE','WRF','mechanistic','circuit','activation patching','causal interven','TPU','sacrifice','Tal metric','ICON-O','HAMOCC','EERIE','Levante','DKRZ','visa' -CaseSensitive:$false
```

**Pass: zero matches.** A hit means a boundary breach reached the deck — **stop, report it, and do
not fix it silently.** The leader needs to know it happened.

---

## 4. Report

Write to
`C:\Users\Admin\Documents\chess_speak_out_loud\agents\reports\2026-08-27_aeon-up-talk-deck_REPORT.md`,
in this structure:

```
## What I built
(file list with sizes, page counts, the SVG conversion tool used)

## Checkpoint output
(A, B, C verbatim — real terminal output, nothing retyped)

## Where I had to make a judgement call
(every place the script did not fully determine the LaTeX: figure sizing,
 line breaks, table column widths. Say what you chose. If you had to stop
 and ask instead, say that.)

## Deviations
(anything done differently from this brief, and why. "None" if none.)

## Opinions
(design or content suggestions. Keep them OUT of the deck itself.)
```

**Do not commit and do not push. Do not open the PDF and describe how it looks** — the leader and
Thejus judge that. Report what the commands returned.
