# TASK FOR GEMINI — foundations chapter + two carry-overs (v2.3)

**Type:** one mechanical sweep, one structural addition. Continue in the build session.
**Standing rules unchanged:** `GEMINI_VISUAL_GUIDE_TASK.md` §0 governs — generated figures,
provenance for every digit, honesty tiers, `mctsviz.sty` for drawing, `\vglane` for backprop.

Do the two carry-overs **first**. They are mechanical, and if you build the new chapter before
fixing them it will inherit both problems.

---

# PART A — Carry-overs from the last round

## A1. Finish the legibility sweep — 46 of 67 figures are still unreadable

The last round fixed only the twelve figures you touched. Across the whole directory:

> **46 of 67 figures still use `\tiny` inside a `scale=0.72–0.85` tikzpicture** — about 4.3pt.

That includes the spine of the document: `fig_2_0` … `fig_2_8` (all eight iteration frames),
`fig_1_1a–d`, `fig_1_2`, `fig_1_6a–d`, `fig_2_10b/c`.

The document now carries **two typographic standards** — §1.2–1.6 are crisp and everything else
is half-legible. That is worse than being uniformly small, because the contrast makes the older
pages read as a mistake.

Apply the same treatment to all 46: **remove the scale factor, raise `\tiny` to `\scriptsize`**,
and let each figure occupy the space it needs. Page count is not a constraint.

**Care needed on Part 2.** Those frames carry the frozen canvas. **Do not change node
coordinates to make room.** Either scale the whole `tikzpicture` up as a unit, or raise
`\vgNodeW` / `\vgNodeH` in `mctsviz.sty` so every frame grows together. Re-run the
coordinate-drift check afterwards — it must still report **0**.

**Acceptance:** the check `for f in figures/*.tex` finds **zero** files combining a `scale<1`
with `\tiny`, and you have read pages at 110 dpi without zooming.

## A2. Fix the figure-ID drift and the file/label mismatch

Splitting FIG-1.8 inserted an ID and shifted everything after it:

```
figures/fig_1_9.tex       now renders as   "FIG-1.10"   (and its caption still says
                                                         "formerly FIG-2.A")
figures/fig_1_10a-d.tex   now render as    "FIG-1.11(a)-(d)"
```

So "fix FIG-1.10" is now ambiguous — file or label? And that figure has been renamed twice in two
rounds (FIG-2.A → FIG-1.9 → FIG-1.10).

**Rename the files to match the displayed IDs**, not the reverse — the labels are what the reader
sees and cites:

```
fig_1_9.tex      ->  fig_1_10.tex
fig_1_10a-d.tex  ->  fig_1_11a-d.tex
```

Update `\input` paths and `\label{}` keys, and record the **full mapping including the
FIG-2.A → FIG-1.9 → FIG-1.10 trail** in `BUILD_REPORT.md`, so the reader's existing notes still
resolve.

**Then adopt a standing rule:** file name and displayed ID must always agree; if a change inserts
a figure, renumber the files in the same pass. Add it to your checklist.

---

# PART B — The foundations chapter

## B0. What the reader asked for, and who he is now

> *"We need to equip the reader with the essential tools and knowledge before he embarks into the
> content. This means building the equation step by step, all the terms, notation and why they are
> used. The target reader is a graduate in Physics, so he has the necessary math. But the theory
> must be grounded first so that the reader is equipped with the necessary toolset to understand
> the terms. The central equations must be carefully enumerated, to the extent of explaining why
> such an equation is used."*

**This changes the assumed background — upward.** Until now the guide assumed a strong chess
player with no maths. The foundations chapter assumes **a physics graduate**: comfortable with
calculus, probability, expectation and variance, sampling, and tail bounds. You may use that
machinery directly. You may not use it *sloppily* — a physicist will notice.

**This does not license you to lower the standard anywhere else.** Parts 1–6 keep their current
voice. The new chapter is the on-ramp, not a new register for the whole document.

## B1. The good news: you are not inventing any of this

The book already contains the entire arc, rigorously, with the derivations the reader is asking
for. Your job is to distil it into visual form and put it **before** everything else. Read these
four chapters in full before drawing:

| Chapter | What it gives you |
|---|---|
| `ch02_currency_of_evaluation.tex` | expected score; centipawns → probability (logistic); why search needs probabilities; sharpness |
| `ch03_one_machine.tex` | why a value must be **sampled**; the running average `W/N`; the **1/√n law**; "from typical error to a guarantee"; the optimism principle |
| `ch04_many_machines.tex` | the bandit setup and the honest definition of waste; why greedy and ε-greedy fail; **"Choosing δ: how the ln N appears"**; UCB1 by hand; the exploration constant |
| `ch05_machines_to_trees.tex` | bandits all the way down; the four phases; **backpropagation and the sign flip**; UCT; why UCT alone cannot play chess |

`ch04`'s §"Choosing δ" is the most important section in the whole task — it is where `ln N` comes
from, and it is exactly the "why is the equation this shape" question the reader is asking.

## B2. Where it goes

**Extend the existing PART 0.** It currently holds only the legend (FIG-0.1). That is the right
home for the toolkit, and it means **Parts 1–6 do not renumber.**

New sections, ending exactly where the current §1.2 ("The Problem the Search Has to Solve")
begins — so the foundations hand off into the five attempts with no seam:

| § | Title | Equations introduced |
|---|---|---|
| 0.1 | How to read these pictures *(existing legend)* | — |
| **0.2** | **Notation and conventions** | the symbol table |
| **0.3** | **What the numbers mean: score, expectation, WDL** | E1, E2, E3 |
| **0.4** | **Why a move's value must be sampled** | E4 |
| **0.5** | **How wrong is a sample mean?** | E5, E6 |
| **0.6** | **Optimism under uncertainty — and where `ln N` comes from** | E7 |
| **0.7** | **From one node to a tree: nested bandits and the sign flip** | E8, E9 |
| **0.8** | **Why this is not enough for chess** | — (hands off to §1.2) |
| **0.9** | **The equation register** | recap card, E1–E12 |

## B3. §0.2 — The notation table (FIG-0.2)

A single reference card the reader keeps open. Every symbol used anywhere in the document, with
**four columns: symbol, name, type/range, whose frame it is in.** The frame column matters more
than anything else here — sign errors are the most common failure mode in this material, and the
document already devotes FIG-2.10 to one.

Cover at minimum: `s`, `a`, `V(s)`, `w`/`d`/`l`, `P(a|s)`, `N(s)`, `n_a` (= `N(s,a)`), `W(s,a)`,
`Q(s,a)`, `U(s,a)`, `S(a)`, `c_puct`, `Q_FPU`, and the visited-prior-mass `Σ_visited P`.

Mark explicitly which quantities are **side-to-move relative** (`V`, `Q`, and every backed-up
value) and which are absolute (`N`, `n_a`, `P`).

> The book's own notation appendix (`appA_notation.tex`) is an empty 73-byte stub. Build this
> table well and it can be lifted into the book later — but **build it here, do not edit the
> book.**

## B4. §0.3–0.7 — The derivation

One idea per figure. Each figure answers a single "why". The physics reader should be able to
reconstruct each equation from its picture.

**§0.3 — What the numbers mean.**
- **E1** expected score `E[score] = P(win) + ½·P(draw)` — the observable being estimated.
- **E2** LC0's value `V = w − l ∈ [−1, +1]`, with `d = 1 − w − l`. Draw the WDL simplex and show
  where our root sits: `V = +0.97602, d = 0.024`. Say why an engine reports a *distribution* and
  not a single number, and what the `d` component tells you that `V` cannot.
- **E3** the logistic map between a centipawn score and a probability (`ch02` §"Building the
  logistic function"). Plot it. This is the figure that explains why "+1.4" is not a linear
  quantity and why the search works in probabilities.

**§0.4 — Why a value must be sampled (E4).**
The exact value of a move is a minimax over a tree too large to enumerate, so it is **estimated**.
`Q = W/N` is a sample mean — a Monte-Carlo estimator. Give the incremental update
`Q_{n+1} = Q_n + (x_{n+1} − Q_n)/(n+1)` and say why an engine stores `W` and `N` rather than a
list of samples. Draw the estimator converging.

**§0.5 — How wrong is a sample mean (E5, E6).**
- **E5** the `1/√n` law — the standard error. A physicist owns this; state it crisply and move on.
- **E6** the step from a *typical* error to a **guarantee**: a concentration bound gives a radius
  that holds with probability `1 − δ`. Draw the confidence interval shrinking as `1/√n` and label
  the radius. This is the object that becomes `U`.

**§0.6 — Optimism, and where `ln N` comes from (E7).** ***The centrepiece of this chapter.***
- The optimism principle: act as if each option is as good as its confidence interval allows —
  "optimism in the face of uncertainty" — and show why that self-corrects (an over-optimistic arm
  gets sampled, and sampling shrinks its interval).
- Then **derive the `ln N`**, following `ch04` §"Choosing δ". The reader must see that the
  logarithm is not decoration: it is what you get when you demand the confidence bound hold
  simultaneously across all arms and all `N` rounds, and choose `δ` shrinking like a power of
  `1/N`. Draw the union-bound argument.
- **E7** UCB1: `Q + c·√(ln N / n)`.

This section is where a physics graduate stops feeling handed a formula and starts feeling he
could have derived it. Give it the most room in the chapter.

**§0.7 — Nested bandits and the sign flip (E8, E9).**
- Every node is its own bandit problem; a tree is bandits all the way down.
- **E8** the negamax backup `V_parent = −V_child` — the two-player structure. Connect it forward
  to FIG-2.10, which walks the exact sign flip on real numbers (`+0.95129 → −0.95129 → +0.95129`).
- **E9** UCT = UCB1 applied at every node.

**§0.8 — Why this is not enough for chess.**
Short. UCT gives every legal move a mandatory first visit (`1/√n` is infinite at `n = 0`), which
is unaffordable at 46 legal moves — and it has no way to use the fact that a network can *look*
at a position and rank moves. That is the gap the prior fills, which is precisely where §1.2's
three requirements pick up. **End the chapter pointing at §1.2 by name.**

## B5. §0.9 — The equation register (FIG-0.N)

A single recap card listing **E1–E12** with, for each: the equation, a one-line statement of what
it is for, and the section where it is used. E10–E12 already exist in Part 1 — **do not re-derive
them**, just enter them in the register:

| # | Equation | Where |
|---|---|---|
| E1 | expected score | §0.3 |
| E2 | `V = w − l` | §0.3 |
| E3 | logistic centipawn ↔ probability | §0.3 |
| E4 | `Q = W/N`, incremental form | §0.4 |
| E5 | `1/√n` standard error | §0.5 |
| E6 | concentration radius | §0.5 |
| E7 | UCB1 | §0.6 |
| E8 | negamax sign flip | §0.7 |
| E9 | UCT | §0.7 |
| E10 | **PUCT** | §1.4 *(existing)* |
| E11 | `Q_FPU` | §1.4 *(existing)* |
| E12 | `c_puct(N)` | §1.4 *(existing)* |

**Then number these equations in the LaTeX** (`\begin{equation}` with labels `eq:E1` …) and make
Parts 1–6 **cite them by number** rather than restating. When FIG-2.2 says `U` halved, it should
be able to point at (E10).

## B6. Physics bridges — allowed, but fenced

You may connect a construct to something the reader already owns — a sample mean is a
Monte-Carlo estimator; a confidence radius is a tail bound; a softmax is a Boltzmann distribution
with a temperature; a value backup is a Bellman-style recursion.

**Two hard conditions:**

1. **Only where the corpus supports the underlying claim.** The bridge may be your phrasing; the
   fact must be `ch02`–`ch06`'s. If you want a bridge the corpus does not support, leave it out.
2. **Fence them visually.** Put every analogy in a distinct box — add one `tcolorbox` style,
   e.g. `\begin{bridge}` titled *"If you know this from physics"* — so an analogy can never be
   mistaken for a measured or established statement about LC0. Register the style in
   `mctsviz.sty` or `preamble_visual.tex` and add it to `\vglegend`.

An analogy that flatters the reader but misstates the mechanism is worse here than no analogy.

---

## B7. Constraints

- **Parts 1–6 do not renumber.** New material is PART 0 only. New figure IDs run FIG-0.2 upward.
- **No Part 2 figure changes**, beyond the A1 legibility sweep.
- Legibility floor from A1 applies to every new figure from the start: **no `\tiny`, no
  `scale<1`.**
- Every digit in `figure_data.json` with a source. Numbers taken from `ch02`–`ch05` are cited as
  `ch0N_<name>.tex:<line>`.
- No new colours outside `\vglegend` — except the `bridge` box, which you add to the legend.
- Tier boxes: this chapter is `established` throughout. It is textbook material, not this
  project's findings. Where our own measured numbers illustrate a point (the root `V`, the
  WDL simplex position), those parts are `realdata`.

## B8. Verification

- `make_figures.py` exits 0; engine self-check passes; provenance check passes.
- `pdflatex` twice, exit 0, zero overfull hboxes.
- **Zero** figures in the whole directory combining `scale<1` with `\tiny` (A1).
- Coordinate drift across `figures/fig_2_*.tex` still **0**.
- Every figure legible at 110 dpi without zooming — including the 46 you sweep.
- File names match displayed IDs everywhere (A2).
- Every equation E1–E12 has a LaTeX label and appears in the register.

## B9. Deliverables

1. The A1 sweep and the A2 rename, with the mapping recorded.
2. PART 0 §0.2–0.9 and all its figures.
3. Rebuilt PDF.
4. `BUILD_REPORT.md`: new rows, the ID mapping, the equation register, and §5 extended — this
   task traces to the reader's request for a grounded toolset before the content.
5. Uncertainty log extended. **Specifically: say where you had to stretch to make a derivation
   visual, and where you think a figure is carrying more than one idea.** Those are the places
   this chapter will fail, and I would rather hear about them from you than find them.

## B10. The standard to hit

After PART 0, a physics graduate who has never seen a chess engine should be able to say, without
looking anything up:

- what quantity the engine is actually estimating, and why it is a probability rather than a score;
- why that quantity has to be **sampled** rather than computed;
- how the error of a sample mean behaves, and how a *typical* error becomes a *guarantee*;
- **why a logarithm appears in the exploration term** — not that it does, but why it must;
- why the value flips sign on the way up the tree;
- and what is still missing at the end of it, such that a prior is needed at all.

The last one matters most: PART 0 must end with the reader feeling a **gap**, not a summary — the
gap that §1.2 and the five attempts then fill.
