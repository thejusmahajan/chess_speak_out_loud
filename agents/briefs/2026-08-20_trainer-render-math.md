```
Brief-ID:       2026-08-20_trainer-render-math
Written:        2026-08-20
Target repo:    chess_speak_out_loud
Route:          Antigravity (full workspace)
Type:           implementation + content restoration
Status:         ACTIVE
Depends on:     2026-08-20_trainer-level-progression (do that first — it is 30 minutes)
Blast-radius:   external
Reversibility:  costly     (equations deleted from cards must be recovered from git)
Failure-mode:   SILENT     (a card missing its equation still reads as a complete card)
Why before the deadline item: the application is unsent and outranks this. This is queued behind
the progression fix; together they make the trainer usable.
```

# Render the mathematics — do not remove it

## INTENT

The previous brief instructed that LaTeX be stripped from the cards because it was not rendering.
**That instruction was wrong.** "Unreadable" was a rendering failure, not a signal that the
equations were surplus. The equations are the substance of the uncertainty, neural-process and
PyTorch ladders — a card about the Law of Total Variance without the decomposition is a card about
nothing.

A correct result: **every equation is present and renders as typeset mathematics in the browser.**

**If any instruction below conflicts with that intent, the intent wins — stop and report.**

## 1. Vendor KaTeX locally

The no-CDN rule concerns **runtime fetches from external hosts**. Shipping a library inside the
repo and serving it ourselves satisfies it. `npm` is available at `C:\Program Files\nodejs\npm`.

```
npm pack katex
# extract the tarball's package/dist/ into:
trainer/static/vendor/katex/
    katex.min.css
    katex.min.js
    contrib/auto-render.min.js
    fonts/            <- REQUIRED; the CSS references these woff2 files
```

**The `fonts/` directory is not optional.** Without it KaTeX falls back to system fonts and the
output is visibly wrong. Verify the font files are present and that the CSS's relative paths
resolve as served.

If `npm pack` cannot reach the registry, **stop and report** — do not substitute a CDN link, and
do not fall back to stripping the maths again.

## 2. Serve and wire it

- Mount `trainer/static/vendor/` through the existing FastAPI static handling.
- In `index.html`, load `katex.min.css`, `katex.min.js`, then `contrib/auto-render.min.js`.
- After the card content is written into the DOM — **including after every reveal and every card
  change**, not once on page load — call:

```js
renderMathInElement(cardEl, {
  delimiters: [
    {left: "$$", right: "$$", display: true},
    {left: "$",  right: "$",  display: false}
  ],
  throwOnError: false
});
```

`throwOnError: false` so one malformed expression degrades to red source text rather than blanking
the card.

## 3. Restore the equations — merge, do not revert

The pre-strip content is in git: commit **`1560992`** still contains the LaTeX (68 math spans in
`uncertainty.json` alone).

```
git show 1560992:trainer/content/ladders/uncertainty.json
```

**Do not blanket-revert the ladder files.** Since that commit, Level 0 was added, the Deep
Ensembles card was re-levelled, and wording improved — a revert would destroy accepted work.

Instead, for each card that existed before the strip: diff its current text against the `1560992`
version and **restore the mathematics that was removed**, keeping every other improvement. Where
the plain-language rewrite is genuinely better prose, keep the prose *and* reinstate the equation
alongside it.

Report a table: card id → equation restored (yes/no) → the expression.

## 4. Level 0 keeps its equations too, with one rule

Level 0 is the ground floor, not a maths-free zone. Equations are welcome there, subject to:

> **Every symbol appearing in a Level-0 card is defined in words on that same card.**

`σ` is fine if the card says "the standard deviation, written σ". `∂L/∂θ` is fine if the card says
what L and θ are. This directly serves the user's stated need — start from basics — without
removing the mathematics he wants.

## 5. Reverse the gate

`verify_cards.py` currently **fails on `$`-LaTeX**. That check now enforces the wrong thing and
must go.

Replace it with two checks that enforce the right thing:
1. **Balanced delimiters** — `$` and `$$` counts must pair within each field. An unbalanced `$`
   is what breaks a renderer and is silent otherwise.
2. **No unsupported macros** — parse each expression and fail on any command KaTeX does not
   implement (`\label`, `\ref`, `\begin{align}` without the `amsmath` subset it supports, etc.).
   KaTeX's supported-function list is the reference.

Mutation-test both: introduce an unbalanced `$`, confirm non-zero exit; introduce `\ref{x}`,
confirm non-zero exit; restore.

## 6. Gate — paste REAL output, and this one needs a browser

```
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer/verify_cards.py
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn trainer.app:app --port 8010
git status
```

Then, in a real browser:
1. Open a card containing `$$` display maths and **describe exactly what you see** — typeset
   symbols, or dollar signs and backslashes. If you cannot open a browser, **say so plainly**;
   do not infer that it works from the code.
2. Confirm maths renders **after clicking reveal**, not only on first paint — this is the most
   likely thing to be wrong, because reveal injects new DOM.
3. Paste the browser console output. It must be free of 404s — a missing font file shows up here
   and nowhere else.
4. Confirm `trainer/static/vendor/katex/fonts/` contains the woff2 files and that they load.

## 7. Your report

`agents/reports/2026-08-20_trainer-render-math_REPORT.md`. Gate output, the restoration table, the
mutation proofs, what you saw in the browser, anything this brief got wrong, and — required —

> **"If exactly one thing in this delivery is still wrong, what is it most likely to be, and did I
> check it?"**
