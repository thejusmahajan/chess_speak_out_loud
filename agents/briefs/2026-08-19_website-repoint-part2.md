```
Brief-ID:     2026-08-19_website-repoint-part2
Written:      2026-08-19
Target repo:  thejusmahajan.github.io  (C:\Users\Admin\Documents\thejusmahajan.github.io)
Route:        Antigravity (open THAT folder as the workspace)
Type:         implementation (site-wide chrome sweep + three fixes)
Status:       ACTIVE
Depends on:   2026-08-19_website-repoint-aeon-up (delivered and audited; do not redo its work)
```

# Website repoint, part 2 — the shared footer, the meta description, and two content fixes

Part 1 was applied correctly. **Four things remain, and all four are errors in the part-1
brief, not in the previous worker's execution.** Do not revisit anything part 1 already changed.

**The absolute rule from part 1 still stands: invent no biographical or technical claim.** All
copy below is leader-written and sourced from this repository. Apply it; do not extend it. If
an anchor does not match, report it — do not improvise.

## 1. Scope

This task edits **site chrome that is duplicated into every page**, plus three single-line fixes.

**In scope: all 20 `.html` files at the repository root** — but only the specific strings named
below.

**Still hard out of scope: the body/article text of every `blog-*.html` file.** You are changing
the shared contact paragraph in their footers and nothing else. Not one word of any article.

Do not touch `css/`, `js/`, `assets/`, `images/`. **Do not stage, commit, or push.**

## 2. Fix A — the clinical-seeking footer (20 files)

`grep -l "expertise in clinical biostatistics" *.html` currently returns **20 files**, including
`blog-lc0-attention-frame.html`, the machine-learning interpretability post. Every one of them
tells a reader he is seeking clinical work.

There are **two variants**. Replace both, everywhere they occur.

**Variant 1 — the two-sentence version** (on `blog.html`, `dashboard.html`, `experience.html`,
`projects.html`, `skills.html`):

find:
```
I am currently seeking opportunities to apply my expertise in clinical biostatistics and bioinformatics. I would love to connect and discuss how my skills can contribute to your team.
```
replace with:
```
I am currently seeking research positions combining environmental or physical modelling with machine learning. I would be glad to connect and discuss how my work might contribute to your group.
```

**Variant 2 — the one-sentence version** (on the 15 `blog-*.html` posts):

find:
```
I am currently seeking opportunities to apply my expertise in clinical biostatistics and bioinformatics.
```
replace with:
```
I am currently seeking research positions combining environmental or physical modelling with machine learning.
```

Apply variant 1 first, then variant 2, so the longer string is not partially consumed. Preserve
all surrounding markup and whitespace exactly.

`index.html` already carries the new copy from part 1 — leave it alone.

## 3. Fix B — the meta description (`index.html`)

**Anchor:** the `<meta name="description" …>` tag whose content begins `Computational scientist
(PhD) with recent experience refactoring clinical data pipelines`.

This string is what Google prints beneath the search result. Replace the whole `content`
attribute value with:
```
Computational scientist (PhD): marine ecosystem modelling on HPC, neural-network interpretability in PyTorch, and large-scale scientific data engineering. Based in Hamburg.
```
Change nothing else in the tag.

## 4. Fix C — restore two facts lost in the card swap (`projects.html`)

Part 1 replaced an older "Cyanobacteria Life Cycle Model" card with the new featured card, and
two sourced facts were dropped in the process. Restore both to the **new featured card**:

1. **Add `validated against observational data`** to the body. The sentence
   ```
   ...and managed multi-year hindcast and projection experiments on HPC clusters.
   ```
   becomes
   ```
   ...and managed multi-year hindcast and projection experiments on HPC clusters, validated against observational data.
   ```
2. **Add a `GOTM-FABM` tag pill**, matching the existing pill markup exactly, placed
   immediately after the `Fortran` pill.

Both are sourced: the validation phrasing from the deleted card (recoverable with
`git show HEAD:projects.html`), and GOTM-FABM from `skills.html:139` — *"ERGOM biogeochemical
model, GOTM-FABM framework, HPC applications"*.

## 5. Fix D — malformed entity in the title (`index.html`)

The `<title>` currently contains a bare `&`:
```html
<title>Dr. Thejus Mahajan — Environmental Modelling & Machine Learning | Hamburg</title>
```
Change that single `&` to `&amp;`. Change nothing else on the line — the em dash stays as the
literal `—` character.

## 6. Gates — paste REAL output

1. `grep -c "expertise in clinical biostatistics" *.html` → **zero hits in every file.**
2. `grep -l "seeking research positions combining environmental" *.html | wc -l` → must be
   **20**.
3. `grep -n "refactoring clinical data pipelines" index.html` → **no hits.**
4. `grep -n "GOTM-FABM\|validated against observational data" projects.html` → both present.
5. `grep -n "Machine Learning | Hamburg" index.html` → shows `&amp;`, no bare `&`.
6. **Proof no article text changed:** for every `blog-*.html`, show that the diff touches only
   the contact paragraph — e.g. `git diff --stat` plus `git diff -U0 blog-*.html | grep -c "^[+-]"`
   and confirm the count equals 2 changed lines per file (one removed, one added). Paste it.
7. `git status` — 20 modified files, nothing staged or committed.
8. Open `index.html` and one blog post in a browser and confirm the footer renders correctly.
   State which post you checked.

## 7. Your report

`agents/reports/2026-08-19_website-repoint-part2_REPORT.md` in the **chess repo**. Cover: each
fix (applied / anchor-not-found), every gate with real output, anything the brief got wrong
about the files, and anything you did not do.
