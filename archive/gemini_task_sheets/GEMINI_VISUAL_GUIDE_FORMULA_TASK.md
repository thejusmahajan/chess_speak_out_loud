# TASK FOR GEMINI — build the formula before you use it (v2.2)

**Type:** restructure + additions to PART 1. Continue in the build session.
**Standing rules unchanged:** `GEMINI_VISUAL_GUIDE_TASK.md` §0 governs. Generated figures,
provenance for every digit, honesty tiers, `mctsviz.sty` for drawing, `\vglane` for backprop.

---

## 0. The problem

`S(a)`, `Q(a)` and `U(a)` first appear in **§1.2** (FIG-1.2, node anatomy). They are not defined
until **FIG-2.A**, in Part 2. The reader meets the three most important symbols in the document
several sections before anything tells him what they are — and even FIG-2.A only says what they
*are*, never why they exist or why they are combined the way they are.

The reader's own words:

> These are the most important variables appearing in the equation. Therefore they must be
> expounded in detail. The logic behind each of the terms and their combination should be given.
> The "Why" question is very important for me. I want to have a logical feel of this equation and
> its terms so that it would be very clear for me to follow the subsequent text without any blocks.

He is right, and the fix is not to move FIG-2.A earlier. It is to **derive the formula**, so that
by the time he sees it he already knows why every piece of it has to be there.

**The good news: you do not have to invent any of this.** `ch06_building_puct.tex` already does
exactly this derivation, in prose, with real numbers. Your job is to turn it into pictures and
put it before first use. Read `ch06` §"Five attempts" (around line 66) and §"First-play urgency"
(around line 273) in full before you draw anything.

---

## 1. New structure for PART 1

Insert three new sections. Everything after them shifts down; **no existing figure changes its
content**, and only one changes its ID (§4).

| § | Content | Status |
|---|---|---|
| 1.1 | The handshake — what the network hands over | unchanged |
| **1.2** | **NEW — The problem the search has to solve** | FIG-1.7 |
| **1.3** | **NEW — Building the rule: five attempts** | FIG-1.8a–e |
| **1.4** | **NEW — Reading the finished formula, term by term** | FIG-1.9 (was FIG-2.A) + FIG-1.10a–d |
| 1.5 | Node anatomy | was §1.2, unchanged content |
| 1.6 | The initial network evaluation | was §1.3 |
| 1.7 | One value per position / what the policy predicts | FIG-1.4, FIG-1.5 |
| 1.8 | The four-phase loop | FIG-1.6 |

Node anatomy now lands *after* the formula, which is the right order: a node stores those fields
**because** the selection rule needs them. Say that in one line when you get there.

---

## 2. §1.2 — FIG-1.7: The problem the search has to solve

Before any formula, draw the constraints. `ch06` states three requirements (it calls them R1–R3);
use them verbatim as the spine:

- **R1** — most moves may get **zero** visits. (A 46-move position on a small budget cannot
  afford one visit each.)
- **R2** — any move must still be **reachable later**. (Nothing may be permanently excluded.)
- **R3** — with enough visits, **measurement must be able to overrule the prior**.

**Draw (1 frame):** the three requirements as three labelled constraints, each with the concrete
failure it prevents, and — this is what makes it bite — **the Morphy position as the witness**:
`P(Qb8+) = 1.60%` on a **forced mate in two**. Any rule that decides in advance which moves are
worth looking at fails this position. Cite `ch06` lines ~55–64 and FIG-5.3.

State plainly: these three requirements are what the rest of the section is trying to satisfy
simultaneously, and that they pull against each other is the whole difficulty.

**Tier:** established, with the Morphy numbers as realdata.

---

## 3. §1.3 — FIG-1.8a–e: Five attempts

Five frames. Each shows **one candidate rule and the picture of it breaking.** This is the heart
of the "why" — the reader should finish it feeling that PUCT is not an arbitrary formula someone
chose, but the only thing left standing.

Each frame carries: the candidate formula, a small diagram of the failure, and a red tag naming
the requirement it violates. Keep the same layout in all five so only the formula and the failure
change.

| Frame | Candidate | Fails | The picture |
|---|---|---|---|
| **a** | search only the top *k* priors | **R2** | Morphy with *k*=3: Qb7, Qb5, Qc3 searched — **mate in two is not in the list**, not at 800 nodes, not at eight billion. Draw the excluded move greyed out and unreachable. |
| **b** | `Q + c·P` — add the prior | **R3** (and R1) | the prior never decays: a permanent thumb on the scale. Show a bar where the prior slab stays the same height forever while measurement piles up beneath it and still cannot outweigh it. |
| **c** | `Q + c·P·√(ln N / n)` — UCB1's bonus, prior-scaled | **R1** | at `n = 0` the bonus is **infinite**. Draw the bar going off the top of the frame. Every legal move gets a mandatory first visit. |
| **d** | `Q + c·P·√(ln N)/(1+n)` — finite at zero | **R2** in practice | finite now, but the numerator grows like `√ln N`: from `N=100` to `N=10,000` it grows only **41%**, while a neglected move needs roughly **10×** to become competitive. Draw the two growth curves side by side — the gap is the point. |
| **e** | `Q + c_puct·P·√N/(1+n)` — **the survivor** | — | same range now grows **tenfold**. A move passed over early is not passed over forever. |

Then the final form, boxed, with the book's own two labels under the braces — use this wording,
it is better than "exploitation/exploration":

```
        Q(s,a)                 c_puct · P(a|s) · √N(s) / (1 + N(s,a))
   └─ what I measured ─┘      └────── what I haven't checked ──────┘
```

**Tier:** established throughout; the Morphy figures are realdata. Every number in frames (a),
(b), (d) is in `ch06` — take them from there, and put them in `figure_data.json` with `ch06` as
the source since they are not all in the JSON.

---

## 4. §1.4 — Reading the finished formula, term by term

**FIG-1.9 = the current FIG-2.A, moved here.** Its content is good; do not redraw it. This is the
**only** ID change allowed in this task — record the rename `FIG-2.A → FIG-1.9` in
`BUILD_REPORT.md`, and carry a parenthetical "(formerly FIG-2.A)" in the caption for this one
revision so the reader's existing notes still resolve. Part 2 keeps **one line** of recall where
FIG-2.A used to sit — a pointer back to FIG-1.9, not a duplicate figure.

Then **FIG-1.10a–d**: four small panels, one per question. These are the "why" panels the reader
asked for. Each is a picture plus at most three sentences.

**(a) Why `Q` is an average, and why it starts as a guess.**
`Q` is the running mean of everything that came back through this edge — so it is *evidence*, and
like all evidence it can be young. An unvisited move has no average at all, so it is given
`Q_FPU`: the parent's own value, minus a penalty. The reasoning behind the penalty, from `ch06`:

> if you have already examined moves covering 80% of the prior mass and none of them beat what
> you have, the remaining 20% is probably not hiding a better move — so discount it.

Show why the two obvious alternatives fail: `Q = 0` is "a pessimistic slander of every unexamined
move" in a won position and wild optimism in a lost one; `Q = parent` with no penalty makes
unvisited moves tie with measured ones and get pulled in too eagerly. Cross-reference FIG-2.B,
which already shows the penalty arithmetic.

**(b) Why `U` is built the way it is** — three sub-parts, each one line, each pointing at the
frame where the reader can watch it happen:
- `P` in the numerator → a move nobody rates starts with a small claim on the budget.
- `√N` in the numerator → the claim of a neglected move **grows** as the search spends elsewhere.
  This is what eventually forces the one visit to Kf5 and Kd5 (FIG-3.1) and finds Qb8+ (FIG-4.1).
- `(1 + n_a)` in the denominator → visiting a move **halves** its own claim immediately. Not `n`,
  because `1/n` is infinite at zero. Point at FIG-2.2, where the halving decides the iteration.

**(c) Why `S = Q + U` is a sum — and what kind of number `S` is.**
This is the panel most likely to unblock him, so give it room. A sum, because the two terms
answer different questions and neither may veto the other: `Q` says *how good this looked when I
checked*, `U` says *how much I still don't know*. Multiplying would let either one zero out the
other; ranking by one and tie-breaking by the other would make the loser irrelevant. Adding lets
a well-measured mediocre move and an unexamined promising move compete on one scale.

Then state plainly what `S` is **not**: it is **not** an evaluation, **not** a probability, and
**not** comparable between positions or between moments. It is a **priority score** — the answer
to "where should the next visit go, right now, at this node." That is all.

**This panel must include the trap**, because the document currently invites it: across
FIG-2.0 → FIG-2.8 the leading `S` **falls** from `1.764` to `1.40`. That is not the position
getting worse. `Q` barely moves; `U` decays as visits accumulate. Draw the two components
separating over the eight iterations so the reader sees the fall is entirely in the pale segment.

**(d) Why `c_puct` grows with `N`.**
`c_puct(N) = 1.745 + 3.894·ln((N + 38740)/38739)`. Nearly constant at small `N` — over our eight
iterations it moves only from `1.7451` to `1.7458`, which the reader can verify in the FIG-2.x
frames — and it opens up over long searches so that deep searches keep some appetite for the
unexamined instead of hardening around an early favourite. Say explicitly that at our scale it is
effectively a constant, so he should not look for it doing anything in Part 2.

**Tier:** established; the `c_puct` values and the `S` decay are realdata from
`simulate_search.py`.

---

## 5. Constraints

- **Existing figure content is frozen.** Only FIG-2.A moves and is renamed. Nothing else
  renumbers, and no Part 2 figure changes.
- **Symbols must not be used before FIG-1.9.** After restructuring, check §1.1 for any stray
  `Q`/`U`/`S`. If the handshake section needs to gesture at them, it may name them in words
  ("what it measured", "what it hasn't checked") but not as symbols.
- **No new colours** outside `\vglegend`. FIG-1.8's "this rule fails" tag should reuse
  `PitfallRed`.
- Every digit in `figure_data.json` with a source — including the `ch06` ones, cited as
  `ch06_building_puct.tex:<line>` where they are not in the JSON.
- Page discipline as before: tier box and its figure on the same page; zero overfull hboxes.

---

## 6. Verification

As last round, plus the check you added:

- `make_figures.py` exits 0, engine self-check passes.
- Every printed digit has a `figure_data.json` entry — **including the new derivation figures.**
  No numeric literals in the generator outside layout constants. (This is the check that caught
  FIG-1.4a; it applies with full force to five new frames of formulas.)
- All new pages rendered and inspected **at 300 dpi**.
- Coordinate-drift check across `figures/fig_2_*.tex` still reports zero.
- Confirm by grep that no `Q(a)`, `U(a)` or `S(a)` appears in a part file before FIG-1.9.

---

## 7. Deliverables

1. FIG-1.7, FIG-1.8a–e, FIG-1.9 (relocated), FIG-1.10a–d, and the restructured PART 1.
2. Rebuilt PDF.
3. `BUILD_REPORT.md`: new rows, the FIG-2.A → FIG-1.9 rename recorded, and the §5 mapping
   extended — this task traces to the reader's request for the logic behind the terms.
4. Uncertainty log extended. In particular, **tell me if you think five attempt-frames is too
   many for one section** and it reads better as three. Layout judgement is yours.

---

## 8. The standard to hit

The reader has said the "why" matters more to him than the "what". When he finishes §1.4 he
should be able to answer, without looking anything up:

- why a move nobody rates still eventually gets looked at;
- why visiting a move makes the search *less* likely to visit it again;
- why the two terms are added rather than combined some other way;
- and why a falling `S` does not mean a worsening position.

If a frame does not move him toward one of those four, it is decoration. Cut it.
