# AUDIT — `2026-08-20_trainer-level-progression` + `2026-08-20_trainer-render-math`

**Auditor:** Leader (Claude Opus 5) · **Date:** 2026-08-20
**Verdict: ACCEPT BOTH.** One thing remains unverified and it needs a human with a browser.

---

## Run 1 — level progression: ACCEPT

Re-ran the measurement myself against the real `trainer/state/progress.json`:

```
stored user rating:                 820.0   (was 1055.6)
levels served over 400 draws:       {0: 400}
ladders touched:  pytorch 135 · uncertainty 89 · neural-processes 73 · own-work 53 · air-quality 50
```

Before the change this was `{1: 400}`. The ground floor is now reachable, and the draw spreads
across all five ladders rather than fixating on one. Suite: **17 passed** (was 11).

## Run 2 — render the mathematics: ACCEPT

### Vendoring
KaTeX 0.18.4 in `trainer/static/vendor/katex/` — `katex.min.css`, `katex.min.js` (272 KB),
`contrib/auto-render.min.js`, and **60 font files** including the woff2 set. Served locally; no
runtime external fetch.

### Restoration — nothing was lost
Compared every card against pre-strip commit `1560992`:

| | pre-strip | now |
|---|---|---|
| cards | 60 | **78** (Level 0 preserved) |
| `$` delimiters | 234 | **382** |
| **cards that had maths then and have none now** | — | **0** |
| cards absent now | — | 1 — `unc-l1-003`, renamed to `unc-l3-003` on re-levelling |

More mathematics than before the strip, and no card lost its equations. The merge was done per
card rather than by reverting, so the Level-0 work, the re-levelling and the improved prose all
survive.

Spot-checked the cards that mattered:
- `unc-l3-003` carries the full Law of Total Variance decomposition in display math.
- `pyt-l0-007` **kept the plain-English correction of the user's misconception** — *"do NOT sum to
  1 or 100%"* — **and** gained the softmax expression. That is exactly the intended outcome:
  equations restored without losing the pedagogy.
- `unc-l0-002` uses `σ²` with the words "stochastic noise" / "model ignorance" alongside, meeting
  the Level-0 rule that every symbol is defined in words on the same card.

### Gates — both new checks mutation-verified

| mutation | result |
|---|---|
| unbalanced `$` injected | exit **1** |
| `\label{x}` injected | exit **1**, message names the macro and the card |
| clean content | exit **0**, 78 cards |
| file restored byte-identical after each | confirmed |

The unsupported-macro regex covers `label|ref|eqref|cite|pageref|nameref|autoref|input|include`.

*(Measurement note: my first `\ref` mutation returned exit 0 and looked like a broken gate. The
injection was mangled by shell escaping — `\r` became a carriage return, so no literal backslash
ever reached the file. Re-injected from Python and the gate fires correctly. Second faulty
measurement of mine this session; both were caught by checking the artefact before filing the
finding, which is the only reason they were not reported as defects.)*

### Render wiring — verified by reading the call sites
`renderMath()` is defined at `index.html:590` and called at **679** (after a card loads) and
**691** (inside `revealAnswer`). Reveal was the case most likely to be missed, since it injects new
DOM. It is covered. `throwOnError: false` is set, so a malformed expression degrades to visible
source rather than blanking the card.

---

## The one thing not verified

**Nobody has seen typeset output.** The report states plainly that the browser automation could not
start — Playwright's driver download returned 404 — and substitutes HTTP asset checks (all assets
200 OK). That is the correct disclosure rather than an inference, and it is also the limit of what
can be established without a browser. I cannot close it either.

**If exactly one thing here is still wrong, I predict it is font path resolution in the served
CSS.** `katex.min.css` references its woff2 files by relative path; if the static mount serves the
CSS from a path that does not resolve `fonts/` the same way, KaTeX falls back to system fonts and
renders *almost* correctly — wrong glyph shapes, wrong spacing, no error anywhere. It is the
classic KaTeX deployment failure, it is silent, and it is invisible to every check performed so
far. I checked that the font files exist and that the CSS and JS return 200; I could not check
that the browser resolves the font URLs.

**Ten seconds closes it:** open `http://127.0.0.1:8010`, reveal a card in the `uncertainty` ladder,
and look at whether `Var(y|x) = …` appears as typeset mathematics or as raw `$$`. If the symbols
look subtly wrong rather than absent, that is the font-path failure above.

---

## State

The trainer is now usable pending that visual check: Level 0 is served, the equations are present,
the maths should render, and the comment box writes to `state/comments.jsonl` where the last round
of feedback came from.
