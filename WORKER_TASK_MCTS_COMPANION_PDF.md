# WORKER TASK — Typeset the MCTS Companion Study Guide as a PDF

Typeset `docs/study/MCTS_COMPANION_STUDY_GUIDE.md` as a PDF that sits beside
`docs/study/guide/neural_mcts_visual_guide_v2.pdf` and looks like it belongs to
the same series, adding illustrative diagrams throughout.

**You are typesetting and illustrating. You are NOT rewriting.** The prose has
been checked line by line against the visual guide's own figure sources and every
number agrees to five decimal places. Do not reword explanations, do not
"improve" the pedagogy, and above all **do not change a single number**. If you
believe something is wrong, STOP and report it rather than fixing it.

Work checkpoint by checkpoint. Each has a verification whose real output you
paste into your report before moving on. If a checkpoint fails, STOP and report.

---

## 0. Read first

| File | Why |
|---|---|
| `docs/study/MCTS_COMPANION_STUDY_GUIDE.md` | **The source content.** Your job is to render this. |
| `docs/study/guide/preamble_visual.tex` | The styling you must match. |
| `docs/study/book/preamble.tex` | The base: colours, boxes, fonts, geometry. |
| `docs/study/guide/tikz/mctsviz.sty` | **The diagram macro library. Reuse it; do not reinvent it.** |
| `docs/study/guide/figures/fig_2_0.tex` … `fig_2_3.tex` | Worked examples of the exact diagrams you need. Read these carefully. |
| `docs/study/guide/parts/part2_growing_tree.tex` | How a chapter is structured and how figures are captioned. |

### Environment

TeX Live 2019 is installed. Build with `pdflatex` (run it **twice** so the table
of contents resolves). `pdftoppm` is available for rendering pages to PNG so you
can check your own work visually — **use it**.

### Do NOT touch

`docs/study/guide/**` — the existing guide, its parts, figures, and `mctsviz.sty`
are finished work. You may *read* and `\usepackage` them. You may not edit them.
Your output is a new, self-contained directory.

---

## Checkpoint 1 — Skeleton that compiles

Create `docs/study/companion/`:

```
docs/study/companion/
    mcts_companion_guide.tex     main file
    preamble_companion.tex       inherits the guide styling
    parts/                       one .tex per Part of the markdown
    figures/                     your new TikZ figures, one per file
```

`preamble_companion.tex` must start by pulling in the existing look:

```latex
\input{../guide/preamble_visual.tex}
```

so colours (`NavyBlue`, `BuildBlue`, `DataTeal`, `HypPurple`, `PitfallRed`,
`WorkGrey`), the `tier` / `keyidea` / `pitfall` / `notationbox` boxes, and the
`realdata` / `established` / `bridge` environments are all available, along with
`mctsviz.sty`. Add nothing that duplicates what is already there.

Title block:

```
Neural MCTS: A Companion Study Guide
Working Through the Search One Number at a Time
Chess Speak Out Loud Project
```

Use `\documentclass[11pt,a4paper]{report}` and `\chapter` per Part, matching the
main guide.

### ✅ Verification 1

```bash
cd docs/study/companion && pdflatex -interaction=nonstopmode mcts_companion_guide.tex && pdflatex -interaction=nonstopmode mcts_companion_guide.tex
grep -c "^!" mcts_companion_guide.log
```

Paste the page count and the error count. **Error count must be 0.**

---

## Checkpoint 2 — Content transferred faithfully

Convert each Part of the markdown into `parts/partN_*.tex`.

**Rendering rules, and these are the point of the whole document:**

1. **The student explicitly rejected unrendered LaTeX.** Every formula that
   appears as plain text in the markdown must appear as **clean typeset
   arithmetic** in the PDF — real numbers, real operators, readable at a glance.
   Use display math for the formulas; never leave raw markup visible.
2. **The fenced code blocks that contain ASCII tables or trace arithmetic** (for
   example the iteration tables in Part 7) should become **proper tabulars** with
   `booktabs` rules — `\toprule`, `\midrule`, `\bottomrule` — right-aligned
   numeric columns, and monospace only where a literal calculation is being
   shown.
3. **The block quotes of the student's own questions** get their own visual
   treatment. Define one environment for them, e.g.

   ```latex
   \newtcolorbox{studentq}[1][]{colback=PaleGrey, colframe=WorkGrey,
     fonttitle=\bfseries, title={The question this answers}, #1}
   ```

   so the reader can see at a glance which passages answer which question.
4. Use `established` for mechanism statements and `realdata` for anything quoting
   engine output, exactly as `part2_growing_tree.tex` does.
5. Keep every section heading and every number **verbatim**.

### ✅ Verification 2

Paste a diff-style list of every numeric value appearing in your `.tex` files
that does **not** appear in the markdown source. That list should be empty.
Command that will do it:

```bash
grep -ohE "[0-9]+\.[0-9]{4,5}" docs/study/companion/parts/*.tex | sort -u > /tmp/tex.txt
grep -ohE "[0-9]+\.[0-9]{4,5}" docs/study/MCTS_COMPANION_STUDY_GUIDE.md | sort -u > /tmp/md.txt
comm -23 /tmp/tex.txt /tmp/md.txt
```

---

## Checkpoint 3 — The diagrams

This is the part that earns the PDF its existence. **Reuse `mctsviz.sty` macros**
— `\vgboardnode`, `\vgsbar`, `\vgsbarS`, `\vgsbaraxis`, `\vgheat`,
`\vgedgewidth`, `\vgselectmark`, `\vgnewmark`, `\vgbackup`, `\vglegend` — and the
node styles `vgroot`, `vgnew`, `vgunvisited`. Study `figures/fig_2_1.tex` before
writing anything; it shows the intended idiom.

Each figure goes in its own file under `figures/` and is pulled in with
`\input{figures/....tex}`, matching the main guide's convention.

**Required figures, one per row:**

| Figure | Part | What it must show |
|---|---|---|
| `fig_c_wdl.tex` | 1 | A horizontal stacked bar for w/d/l summing to 1, with `E` and `V` marked on two aligned axes underneath, showing `V = 2E - 1` geometrically |
| `fig_c_sharp.tex` | 1 | Two stacked bars side by side, both with `E = 0.60`, one sharp (d small) and one drawn (d large) — the point being that one number hides the difference |
| `fig_c_circles_arrows.tex` | 2 | **The most important diagram.** A root *circle* labelled as a position, four *arrows* labelled as moves, four child *circles*. Circles and arrows visually distinct. Annotate: `V` lives on circles, `P/n/W/Q` live on arrows |
| `fig_c_board.tex` | 0 | The King+Pawn position drawn as a real chessboard. **Use `xskak`, already loaded in the base preamble**, with FEN `4k3/8/4K3/4P3/8/8/8/8 w - - 0 1`, and arrows for the four legal moves — two green (winning), two red (throw the win away) |
| `fig_c_qmean.tex` | 4 | Running-mean convergence: samples `x_1..x_n` as points, the running average `Q` as a line settling down |
| `fig_c_signflip.tex` | 4 | Three stacked levels alternating White/Black to move, with `V` values alternating sign as they back up |
| `fig_c_ushrink.tex` | 5 | `U` against visit count `n` for a high-`P` and a low-`P` move, showing the `1/(1+n)` decay and the halving at the first visit |
| `fig_c_fpu.tex` | 6 | **The transition moment.** Two panels: before first visit (borrowed placeholder, drawn dashed/hollow) and after (real measurement, solid). Make it obvious the placeholder is *replaced*, not blended |
| `fig_c_iter0.tex` … `fig_c_iter3.tex` | 7 | Four S-bar strips, one per iteration, in the exact style of `fig_2_0..3` — `Q` as the solid segment, `U` as the pale cap, tallest bar gold-highlighted as selected |
| `fig_c_visits.tex` | 8.1 | Visit distribution after four iterations (Kd6 1, Kf6 2, Kf5 0, Kd5 0) beside a sketch of what it looks like at 10,000 nodes — the answer to "won't blunders drag the average down" |
| `fig_c_depth.tex` | 8.2 | Two panels: visit 1 to `Kf6` stopping at the child; visit 2 passing *through* it to a grandchild. The answer to "why revisit a move" |

**Numbers in figures must come from the markdown.** The iteration S-bars in
particular have exact `Q` and `U` values already computed there — use them, do
not recompute and do not round differently.

### ✅ Verification 3

Render every page to PNG and **look at them**:

```bash
cd docs/study/companion && pdftoppm -r 100 -png mcts_companion_guide.pdf page
```

For each of the 15 figures, state in your report: figure name, which page it
landed on, and whether it renders correctly (no overlapping labels, nothing
running off the page, all text legible at 100 dpi). **A figure you have not
looked at does not count as done.**

---

## Checkpoint 4 — Final build

- `pdflatex` twice, zero errors.
- Table of contents resolves, all `\ref`/`\label` resolve (no `??` in the PDF).
- No figure overruns the text block; no `Overfull \hbox` above 20pt.
- The document reads as part of the same series as the visual guide.

### ✅ Verification 4

```bash
cd docs/study/companion
pdflatex -interaction=nonstopmode mcts_companion_guide.tex >/dev/null
pdflatex -interaction=nonstopmode mcts_companion_guide.tex >/dev/null
echo "errors: $(grep -c '^!' mcts_companion_guide.log)"
echo "undefined refs: $(grep -c 'undefined' mcts_companion_guide.log)"
grep -c "Overfull" mcts_companion_guide.log
grep -o "Output written on .*" mcts_companion_guide.log
```

Paste all of it.

---

## Checkpoint 5 — Report

Write `MCTS_COMPANION_PDF_REPORT.md` at repo root:

1. Files created, with the page count and final PDF size.
2. Pasted output of **all four verifications**.
3. The figure table from Checkpoint 3 with your rendering assessment per figure.
4. Anything you could not do, or where you deviated — **state it plainly**.
5. Any place you were tempted to change wording or a number, and what you did
   instead.

**STOP. Do not push. Do not edit the markdown source. Do not touch `guide/`.**

---

## Anti-patterns that will fail review

- Changing, rounding, or recomputing any number. The markdown is the authority.
- Rewriting explanations because you would have phrased them differently.
- Writing new TikZ from scratch when a `mctsviz.sty` macro already does it.
- Editing anything under `docs/study/guide/`.
- Leaving raw LaTeX visible in the output — the entire reason this document
  exists is that the student could not read unrendered markup.
- Reporting a figure as fine without having rendered and looked at it.
- Claiming a checkpoint passed without pasting its real command output.
