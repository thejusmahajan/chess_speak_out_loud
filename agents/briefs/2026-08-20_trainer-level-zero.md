```
Brief-ID:       2026-08-20_trainer-level-zero
Written:        2026-08-19
Target repo:    chess_speak_out_loud
Route:          Antigravity (full workspace)
Type:           content authoring + one UI fix
Status:         ACTIVE
Depends on:     2026-08-19_trainer-content-repair (AUDITED, ACCEPTED)
Blast-radius:   external   (he will repeat these to the people who wrote the papers)
Reversibility:  costly     (a wrong or confusing card is drilled in by spaced repetition)
Failure-mode:   SILENT     (a card pitched too high looks exactly like a card pitched right)
Why before the deadline item: the application is still unsent and outranks this. But the trainer
is currently unusable — the user's rating fell 1269 → 1186 and he flagged eight Level-1 cards as
incomprehensible — so it is either fixed or not used.
```

# Add Level 0, and stop the maths being unreadable

## INTENT

Thejus used the trainer and left nine comments. **Eight of nine are Level 1 — the lowest tier —
and every one says he does not know the vocabulary the answer is written in.** His rating fell
through the session because the ladder has no bottom: Level 1 already assumes graduate ML fluency.

The goal is a **genuine ground floor**: cards a competent physicist who has never trained a neural
network can answer, in plain English, with no notation he has not been taught first. He is not
weak; the ladder is mis-levelled by roughly two tiers.

**If any instruction below conflicts with that intent, the intent wins — stop and report.**

## 1. The evidence — his own words, verbatim from `trainer/state/comments.jsonl`

**This is the specification. Do not paraphrase it away.**

| card | level | his comment |
|---|---|---|
| `pyt-l1-003` | 1 | *"I don't know what is meant by B,D. Are they numbers or some representation of dimensions? What is broadcasting? I haven't heard of it in a programming context."* |
| `own-l1-003` | 1 | *"What do you mean by 'logits mapping ..'? What are logits? Aren't they probabilities in percent?"* |
| `np-l1-003` | 1 | *"What do you mean by model capacity? What are kernel matrices?"* |
| `unc-l1-003` | 1 | *"I don't know what is ep deep ensemble, epistemic variance etc."* |
| `unc-l1-003` | 1 | *"I don't understand the terminology. I think these terminologies must be studied and trained first. For example aleatoric variance. **And the Latex is not rendering.**"* |
| `pyt-l1-002` | 1 | *"So either the Tensors live in the GPU ram or on the CPU ram?"* |
| `pyt-l2-003` | 2 | *"What is the significance of 'zero' here in `optimizer.zero_grad()`?"* — **asked twice** |
| `own-l5-001` | 5 | *"The distinction between side-to-move vertical reflection a8 vs 180-deg rotation h8 is crystal clear and verified against neural_vision.py."* — this one **works**; it is the model to imitate |

Note the last row. A Level-5 card is his clearest card. The problem is not difficulty — it is
**unexplained vocabulary**.

## 2. THE LATEX BUG — fix this first, it makes everything else unreadable

Cards contain raw LaTeX (`$\theta$`, `$\sigma_m^2(x)$`, `$P(a|s)$`). The page does not render it,
so he is reading source.

**Do not add MathJax or KaTeX** — the no-CDN, no-build constraint stands and a maths renderer is not
worth it here.

**Instead: remove LaTeX from card text entirely.** Rewrite every affected card using plain words
and Unicode:
- `$\sigma_m^2(x)$` → `the variance of model m at x`, or `σ²`
- `$\theta$` → `θ`, introduced as "the model's parameters (written θ)"
- `$P(a|s)$` → `P(move | position)` — spell the meaning out
- `$N$` → `N`, and say what N counts

Add a check to `verify_cards.py`: **fail if any card field contains `$` followed by a letter or
backslash.** Mutation-test it.

## 3. Build Level 0

A new tier below Level 1. `level: 0`, `difficulty: 800` (range 750–850). Existing Level-1 cards
gain `requires` entries pointing at the Level-0 cards that teach their vocabulary — so the engine
will not serve `unc-l1-003` until the epistemic/aleatoric groundwork is answered.

**Rules for a Level-0 card:**
1. **One idea per card.** If the answer needs two new terms, it is two cards.
2. **No symbol appears without being named in words first.**
3. **Answer in 2–4 plain sentences.** No LaTeX, no citation-style jargon.
4. **Every card carries a concrete example** — a number, a shape, a line of code he could run.
5. Assume: strong physics, strong Fortran/Python/R, HPC, NetCDF. Assume **no** deep-learning
   vocabulary whatsoever.

### The Level-0 cards to write (from his questions — do not invent a different list)

**`pytorch` ladder**
- What is a tensor, and how is it different from a NumPy array?
- What do the letters in a shape like `(B, 1, D)` mean? *(that they are named dimensions, not
  values; B = batch, D = feature dimension; show a real shape from this repo)*
- What is broadcasting? *(he explicitly says he has never met the term — use a concrete
  `(3,1) + (1,4)` example and show the result)*
- Where does a tensor live — CPU or GPU memory? *(his own phrasing; confirm his reasoning, then
  explain `.to('cuda')` and why mixing devices errors)*
- What is a gradient here, in one sentence?
- What does `optimizer.zero_grad()` zero, and why is it needed? *(**he asked twice — this card
  matters most**; explain that PyTorch accumulates gradients by default, so stale ones must be
  cleared each step)*
- What are logits? **Explicitly correct the misconception**: they are raw unbounded scores before
  softmax, they can be negative, they are *not* percentages. He asked exactly this.

**`uncertainty` ladder**
- What is variance, in plain words, for a prediction?
- Aleatoric vs epistemic uncertainty — with a physical example, no formulas. *(noise in a sensor
  vs never having measured that neighbourhood)*
- What is an ensemble, and why would several models disagree?
- What is calibration, in one sentence?

**`neural_processes` ladder**
- What does "model capacity" mean? *(his question)*
- What is a kernel, and what is a kernel matrix? *(his question — use a concrete "how similar are
  these two points" framing)*
- What does it mean for a model to be parametric or non-parametric?

**`own_work` ladder**
- What is a policy, and what is a value, for a game-playing network? *(plain, before the
  head-architecture card)*
- What is a probability distribution over win/draw/loss?

That is roughly 17 cards. **Do not pad to a round number.** If a card on the list turns out to
duplicate an existing Level-1 card that is already clear, say so and skip it.

## 4. Re-level what exists

`unc-l1-003` ("How do Deep Ensembles estimate epistemic uncertainty?", answer invoking the Law of
Total Variance) is **not** a Level-1 card. Promote it to Level 3 and adjust its difficulty. Sweep
the other Level-1 cards: any card whose answer uses a term not taught at Level 0 or earlier in
Level 1 is either re-levelled or given a `requires` link. **Report every card you move.**

## 5. Sourcing rules stand

Everything from the previous brief still applies: every card needs a real source; a session log is
never a sole source; no forbidden claim; every external URL must resolve. For Level 0, PyTorch's
own documentation is the right source for PyTorch terms — cite the specific page, not the root.

## 6. Gate — paste REAL output

```
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer/verify_cards.py
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer/verify_cards.py --check-urls
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
git status
```

Plus:
- the count of Level-0 cards per ladder;
- **proof the LaTeX check works**: add `$\theta$` to a card, show the gate exits non-zero, restore;
- **proof prerequisite gating works**: show that a Level-1 card with unmet Level-0 `requires` is
  not served by the selector (a test, not an assertion);
- every card you re-levelled, with old and new level;
- confirmation that **no `$`-LaTeX remains in any card field**.

## 7. Your report

`agents/reports/2026-08-20_trainer-level-zero_REPORT.md`. Every gate result, the re-levelling
table, anything this brief got wrong, and — required —

> **"If exactly one thing in this delivery is still wrong, what is it most likely to be, and did I
> check it?"**

"I could not test the browser" does not answer that question.
