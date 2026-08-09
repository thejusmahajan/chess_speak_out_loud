# TASK FOR GEMINI — additions to *Inside LC0's Mind* (v2.1)

**Type:** additions to a finished document you built. Not a rebuild.
**Continue in the build session** — you have the figure sources, the coordinates and the
generator in context. (The study session that produced the input below is a *different*,
deliberately separate session; do not merge the two roles.)

---

## 0. Where this comes from, and why it is the best input we have

The reader has started studying the document and logged his questions in
`docs/design_session/visual_guide/STUDY_NOTES.md`. Read it first, in full.

That log is more valuable than any review, because it records **the things a strong reader
actually got wrong after reading the document carefully**. Every addition below traces to a
specific question in it. We are not adding material because it would be nice to have; we are
patching demonstrated failures of the document to convey something.

Two of his questions were not requests for more detail — they were **misconceptions the document
allowed**, and in one case the study session had to open with "Correction on Premise." That is
the document's fault, not the reader's.

**Standing rules are unchanged** — `GEMINI_VISUAL_GUIDE_TASK.md` §0 still governs: no chess
analysis, no invented numbers, figures generated from JSON by `tools/make_figures.py`, honesty
tiers enforced, `mctsviz.sty` for all drawing. Re-read that section before starting.

---

## 1. The gap, verified

I checked the built document rather than assuming. Across `parts/*.tex` and `figures/*.tex`:

| Term | Occurrences in the guide |
|---|---|
| `Q_FPU` as a node label | **30** |
| the FPU formula (`0.33`, `\sqrt`) | **0** |
| the PUCT formula (`c_puct`, `38739`) | **0** |
| the words Selection / Expansion / Backpropagation | **0** |

So the guide prints `Q_FPU = 0.97602`, then `Q_FPU = 0.75015` with a red "FPU drop" tag, and
**never tells the reader what FPU is or why it dropped**. It shows the consequences of two
formulas without ever showing the formulas. The reader noticed this himself and wrote it into
his notes: *"neural_mcts_visual_guide_v2 omits these explicit formulas."*

This is the root of three of his four questions.

---

## 2. The five additions

Numbering: use the new IDs given. **Do not renumber any existing figure** — the study notes,
`BUILD_REPORT.md` and the reader's own notes all cite the current IDs.

---

### ADD-A — FIG-1.4: "One value per position, not one per move"

**Origin:** Q2. He wrote *"Kd6, Kf6 are the two moves with almost equal P's and highest V's"* —
believing each move carries its own `V` from the root network call. It does not. The study
session had to correct the premise before it could answer.

**Why the document caused it:** FIG-1.2 (node anatomy) shows `P`, `n`, `Q`, `V`, `U`, `S` all on
one node. A reader reasonably concludes the network hands back that whole bundle per move. It
does not: one forward pass on a position returns **one `V` for that position** plus **one `P` per
legal move**. A move only acquires a `V` of its own later, when it is expanded into a child node
and that child is evaluated.

**Draw (2 frames, `pitfall` box):**
- **(a) The misreading** — four move-boxes each carrying its own `V`, struck through. Label:
  *"the network never says this."*
- **(b) What actually comes back** — one card holding `V(root) = +0.97602, d = 0.024` for the
  *position*, and beside it a single distribution over the four moves
  (45.13 / 44.23 / 5.38 / 5.26). One `V`, four `P`s.

**Do not overcorrect.** Add a third element to (b) or a caption line making clear that a move
*does* get a value once it is expanded — that is exactly what `V(leaf) = +0.96766` is in FIG-2.1,
and it belongs to the *child position*, not to the move. Cite FIG-2.1 so the reader can connect
them.

**Tier:** established, with the numbers from `engine_data.json` making it realdata where numbers
appear. **Place:** immediately after FIG-1.2, before FIG-1.3.

---

### ADD-B — FIG-1.5: What the policy actually predicts

**Origin:** Q2. The natural reading of "prior" is "how good this move is." That is wrong, and the
correct answer is sharper and more interesting.

**The claim, quotable verbatim from `ch12_two_heads.tex`** (`\begin{keyidea}`, around line 96) —
cite it, do not paraphrase it into something weaker:

> The policy head predicts **which move a full search by this same engine would end up
> preferring**. It is a fast approximation of its own slow self. It is *not* a model of human
> choice, *not* a goodness score, and *not* calibrated to any rating band.

**Draw (1 frame):** the claim, plus **two measured proofs already in the corpus** that a prior is
not a goodness score — this is the part that makes it land, and both numbers are already in
`figure_data.json`:

- **P is not goodness, downward:** Kf5 and Kd5 together hold **10.64%** of the root policy and
  both **throw away a won game** (Stockfish d30: `0.00`).
- **P is not goodness, upward:** in the Morphy position `P(Qb8+) = 1.60%` — on a **forced mate in
  two**.

Point the reader at FIG-4.3 and FIG-5.3, which already show these; this figure's job is to name
the principle they are both instances of.

**Tier:** established for the claim (cite ch12), realdata for the two examples.
**Place:** after FIG-1.4.

---

### ADD-C — FIG-1.6: The four-phase loop, named and drawn

**Origin:** Q1. He asked *"then what happens?"* and had to be told the loop has four phases. The
guide animates the loop eight times and never names its parts.

**Draw (4 frames, one cycle diagram, one phase lit per frame):** a ring of four labelled boxes —
**Selection → Expansion → Evaluation → Backpropagation → (back to Selection)**. Each frame
highlights one box and annotates it with **what iteration 1 actually did**:

1. **Selection** — compute `S(a) = Q + U` for all four moves; all `Q` equal, so priors decide;
   Kd6 wins at `S = 1.76358`.
2. **Expansion** — step down the Kd6 edge, create the child node.
3. **Evaluation** — one forward pass on the new leaf.
4. **Backpropagation** — the value returns to the root, flipping sign at each ply; the root edge
   Kd6 receives `+0.96766`.

Nothing moves between frames; only the highlight and the annotation change.

**Then:** add a phase tag to every FIG-2.x caption — e.g. *"Selection → Expansion → Evaluation →
Backpropagation; the walk stopped at depth 1."* For FIG-2.3 onward the tag should make the
recursion visible: *"Selection recursed twice before expanding."* This is a caption edit, not a
redraw.

**Tier:** established. Cite `ch05_machines_to_trees.tex` ("One iteration, four phases").
**Place:** end of PART 1, as the bridge into PART 2.

---

### ADD-D — FIG-2.A: The two formulas, annotated onto the picture

**Origin:** Q4, where he flagged the omission explicitly.

This is the formula analogue of FIG-1.2's anatomy-of-a-node, and it must be **a picture of a
formula, not a maths dump**. Print both formulas large, and run a leader line from each symbol to
the thing it controls in a small inset S-bar:

```
  S(a)  =    Q(a)      +   c_puct(N) · P(a) · √max(N,1) / (1 + n_a)
             │                                              │
             └─→ the SOLID segment                          └─→ visiting a move puts
                 (measured, or the FPU guess)                    it in this denominator
                        ┌─────────────────────────────────────────┘
                        └─→ the PALE segment on top

  c_puct(N) = 1.745 + 3.894 · ln((N + 38740) / 38739)
  Q_FPU     = Q(parent) − 0.33 · √( Σ P over visited children )
```

Then one line, which is the whole point of the figure: **the tallest bar wins, and these two
formulas are what set the heights.**

Also annotate the `(1 + n_a)` denominator with a pointer to FIG-2.2 — that is where the reader
watches it halve.

**Tier:** established. Constants from `KNOWLEDGE_BASE.md` §2.2; they are LC0's real values and
must match `simulate_search.py` exactly.
**Place:** opening of PART 2, before FIG-2.0.

---

### ADD-E — FIG-2.B: Where the solid segment comes from *(the most important addition)*

**Origin:** Q3. He proposed: *"V is the initial hunch of the game outcome which doesn't have any
bearing on how MCTS sees the moves. MCTS searches only according to the P values. Correct?"*

The answer is **no**, and the fact that a careful reader concluded this after studying the
document is the strongest signal in the whole study log. The document shows solid bar segments
from frame one and never says where their height comes from — so the only visible driver of
search *appears* to be `P`.

**Draw (3 frames, reusing the FIG-2.0 canvas and its bar strip — no new coordinates):**

- **(a) `V` arrives.** `V(root) = +0.97602` sits at the root. The four bars are empty outlines.
- **(b) `V` becomes every solid segment.** Four arrows carry that same value down into all four
  children as their `Q_FPU`. All four solid segments are **exactly the same height**, and that
  height **is** `V(root)`. Only the pale `U` caps differ — and those come from `P`. Caption:
  *before a single measurement, `V` sets the floor for every move and `P` sets what is stacked on
  top.*
- **(c) The penalty appears.** After Kd6 is measured, its solid segment becomes its own measured
  `Q = 0.96766`; the other three drop to `0.75015`. Show the subtraction explicitly as a slice
  removed from the top of those three bars:
  `0.97184 − 0.33·√0.4513 = 0.97184 − 0.22169 = 0.75015`.

**Add a small table** beneath, tracking `Q_FPU` against the visited prior mass across all eight
iterations — the data is already in `simulate_search.py`'s output:

| It. | visited prior mass | `Q_FPU` |
|---:|---:|---:|
| 1 | 0.0000 | 0.97602 |
| 2 | 0.4513 | 0.75015 |
| 3 | 0.8936 | 0.66460 |
| 4–8 | 0.8936 | 0.658–0.668 |

and make the observation the table exists to support: **the penalty stops growing after iteration
3, because only Kd6 and Kf6 are ever visited, so no new prior mass is ever added.** After that
`Q_FPU` only drifts with the root's own `Q`. (`ch07` exercise `ch7:fpudrop` asks exactly this —
cross-reference it.)

**Tier:** realdata. Every number from `simulate_search.py` / `engine_data.json`.
**Place:** immediately after FIG-2.A, before FIG-2.0.

---

## 3. Constraints

- **Existing figure IDs are frozen.** Add only; renumber nothing.
- **Frozen canvas still holds.** FIG-2.B reuses FIG-2.0's coordinates exactly
  (`LATEX_SPEC.md` §4, as-built values). Run the coordinate-drift check across all Part 2 figure
  sources before you report done.
- **Every number generated**, from JSON or `simulate()`, recorded in `figure_data.json` with its
  source path. No literals in `make_figures.py` outside layout constants.
- **`\vglane` for any backprop path** that would cross a node row. Never a curved `\vgbackup`
  for those — see `LATEX_SPEC.md` §3.4 for why.
- **No new colours.** Everything must already be in `\vglegend`. If ADD-E needs to show a
  "removed slice," derive it from the existing palette (e.g. `PitfallRed` at low opacity) and add
  it to the legend rather than inventing a colour silently.
- **Page discipline:** a tier box and the figure it introduces stay on the same page. The
  document is currently 19 pages and free of overfull hboxes; keep it that way.

---

## 4. Verification

Same bar as last time, plus the two columns you added:

- `python tools/make_figures.py` exits 0, engine self-check passes.
- `pdflatex` twice, exit 0, zero overfull hboxes.
- Every new page **rendered to PNG and inspected at 300 dpi**, not at page scale. The last three
  defects were only visible zoomed in.
- Per new figure in `BUILD_REPORT.md` §4: gold bar/ring match (N/A where no selection), caption
  numbers appear in the figure, no element overlaps another — with the **x-extent arithmetic**
  written out for any frame where two things come within a centimetre.
- Coordinate-drift check across `figures/fig_2_*.tex` reports zero drift.

---

## 5. Deliverables

1. The five new figures and their generator code.
2. The FIG-2.x caption phase-tags from ADD-C.
3. Rebuilt PDF.
4. `BUILD_REPORT.md` updated: new rows, and a new §5 **"Additions traceable to reader
   questions"** mapping each addition to the question in `STUDY_NOTES.md` that motivated it.
   That mapping is worth keeping — it is how we will judge future additions too.
5. Your running uncertainty log, extended. In particular: **say so if you think an addition is
   in the wrong place, or if drawing one of these would be clearer as two figures.** Layout
   judgement is yours; content is not.

---

## 6. One thing to be careful about

ADD-A and ADD-B correct misconceptions, and there is a temptation to write them as a lecture on
what the reader got wrong. Don't. He got them wrong because the document let him. Frame both as
*"here is a thing that is easy to misread, and here is the picture that makes it unmistakable"* —
the `pitfall` box exists for exactly this and is titled "Where people go wrong," not "where you
went wrong."
