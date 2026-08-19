```
Brief-ID:     2026-08-19_knowledge-trainer-build
Written:      2026-08-19
Target repo:  chess_speak_out_loud (this one)
Route:        Antigravity (full workspace)
Type:         implementation + content authoring
Status:       BLOCKED until 2026-08-19_knowledge-base-audit is delivered AND audited
Depends on:   2026-08-19_knowledge-base-audit
```

# Build the knowledge trainer

A spaced-repetition trainer, in the spirit of the Lichess puzzle trainer, that takes Thejus from
vocabulary up to a complete interview answer. It must **work**; it does not need to be pretty.

**Why it is blocked:** the content comes from this repository's documents, and those are being
audited right now because several are known stale or wrong. Drilling a wrong fact into someone
before an interview is worse than not training at all. If the audit is delayed, you may build
the engine (§3–§6) first and author content (§7) afterwards — but **never author a card from a
document the audit has flagged.**

---

## 1. The absolute rule

**Every card must be traceable to a source, and no card may teach something false.**

- Each card carries a non-empty `sources` list: a repo path (`docs/FILE.md#section`), a URL, or a
  paper citation. **No source, no card.**
- **Nothing may contradict**
  `C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\study_room\06_do_not_claim.md`.
  That file lists things Thejus must not claim (e.g. having implemented ConvCNP, having used
  EPISODE-CityChem). A trainer that rehearses him into an overclaim is the worst possible failure
  — he would say it to the people who would know.
- Where a fact is uncertain, the card says so. "This is disputed" is a legitimate answer.
- **Do not invent numbers, citations, or paper titles.** If you cannot source it, drop the card
  and note it in your report.

## 2. Stack and layout (pinned)

Python + FastAPI + one static HTML page. No build step, no npm, no framework, no CDN. Run with
`C:\Users\Admin\miniconda3\envs\cszero\python.exe`.

```
trainer/
  app.py                    FastAPI server (also serves the page)
  engine.py                 scheduling + rating, PURE functions, no I/O
  verify_cards.py           the content gate (§8)
  static/index.html         the whole UI, inline CSS/JS
  content/ladders/*.json    authored cards, one file per ladder
  state/progress.json       per-card SRS state + the user's rating
  state/answers.jsonl       append-only answer log
  state/comments.jsonl      append-only feedback  <-- THE LEADER READS THIS
  tests/test_engine.py
  README.md                 how to run it, in three lines
```

**All state is plain JSON/JSONL on disk.** No database, no browser-only storage — the leader must
be able to read progress and comments directly with `cat`.

**Do NOT touch** `backend/`, `frontend/`, `data/`, `docs/`, `agents/`, or any existing file. The
trainer is a new, self-contained directory. Do not commit.

## 3. The ladder — how content is structured

A **ladder** is a chain from vocabulary to one real interview answer. Five levels, bottom-up:

| level | what it tests | example |
|---|---|---|
| 1 | vocabulary / definition | "What is a Gaussian process, in one sentence?" |
| 2 | core concept | "What is the difference between aleatoric and epistemic uncertainty?" |
| 3 | mechanism — how it actually works | "How does a CNP encode a variable-size context set, and why must it be permutation-invariant?" |
| 4 | application / judgement / trade-off | "When would a ConvCNP beat a plain CNP for spatial downscaling, and what does it cost?" |
| 5 | **the full interview answer** | "Given three monitoring stations in a city, how would you produce a high-resolution NO₂ field with uncertainty?" |

**Method for authoring a ladder** (this is the design Thejus asked for):
1. Conceive a realistic interview question for the AEON-UP role — from the repo documents, the
   study room, and web search where needed.
2. Write the **complete, correct level-5 answer** first.
3. Decompose that answer downwards: what must someone already know for each sentence of it to
   make sense? Those become levels 1–4.
4. Every level-5 card lists, in `requires`, the level-4 cards it composes.

## 4. Card schema (pinned)

```json
{
  "id": "np-l3-002",
  "ladder": "neural-processes",
  "level": 3,
  "topic": "neural processes",
  "question": "…",
  "answer": "…",
  "explanation": "…why this is the answer, and the intuition",
  "trap": "…the common wrong answer, and why it is wrong (optional but valuable)",
  "sources": ["docs/…", "https://arxiv.org/abs/1807.01613"],
  "difficulty": 1400,
  "requires": ["np-l2-001", "np-l2-004"]
}
```

`difficulty` is an Elo-style number you author: **level 1 ≈ 1000, level 2 ≈ 1200, level 3 ≈ 1450,
level 4 ≈ 1700, level 5 ≈ 1950**, ±100 by your judgement.

## 5. Rating and scheduling (pinned — implement exactly, in `engine.py`, as pure functions)

**Grading is self-assessed**, three buttons: `got it` = 1.0, `partial` = 0.5, `missed` = 0.0.
The answers are prose; do not attempt automatic marking.

**Elo.** User rating `Ru` starts at **1200**. For a card of rating `Rc`:
```
expected = 1 / (1 + 10 ** ((Rc - Ru) / 400))
Ru += 24 * (score - expected)
Rc +=  8 * (expected - score)
```
Card ratings persist in `progress.json`, never overwriting the authored value in the content file.

**Spaced repetition (SM-2, simplified).** Per card: `ease` (default 2.5), `interval_days`, `reps`.
```
score 1.0 : reps += 1
            interval = 1 if reps == 1 else 6 if reps == 2 else round(interval * ease)
            ease += 0.10
score 0.5 : interval = max(1, round(interval * 0.6));  ease -= 0.15
score 0.0 : reps = 0; interval = 0;                    ease -= 0.20
ease clamped to [1.3, 2.8]
```
A card is **due** when `now >= last_seen + interval_days`. Interval 0 means due again this session.

**Selection.** From the due set, keep only cards whose `requires` are all satisfied (each required
card answered at 1.0 at least once — **this is what enforces bottom-up learning**). From those,
choose randomly among cards with `|Rc - Ru| <= 150`; if fewer than three qualify, widen by 50 and
repeat. If nothing is due, offer a **cram mode** that ignores due dates and uses the same
rating-window selection.

## 6. The interface

One page. Show: the question; a **reveal** button; then answer, explanation and trap; then the
three grading buttons. Also show the user's current rating, the card's rating and level, the
number due, and a session counter. That is enough.

**The comment box is not optional — it is the point.** On every card, always visible, a control
labelled **"Something wrong or unclear? Tell the leader."** Opening it asks:

1. A required category (radio):
   - `question unclear` — I didn't understand what was being asked
   - `missing prerequisite` — the answer assumed something I've never been taught
   - `answer unclear` — I couldn't follow the explanation
   - `I think this is wrong` — factual dispute
   - `too easy` / `too hard` for its level
   - `other`
2. A free-text box.

Submitting appends one line to `state/comments.jsonl` with: timestamp, `card_id`, `ladder`,
`level`, category, the text, the user's rating, and whether he had revealed the answer. **The
leader reads this file at every audit and rewrites the offending cards.** The structured category
is what makes that fast — say so in the UI so he knows it is read.

## 7. Seed content — five ladders, roughly 12 cards each (~60 total)

| ladder | spans | level-5 question (author the real one; these are the direction) |
|---|---|---|
| `pytorch` | tensors, dtype/device, broadcasting, autograd and define-by-run, `nn.Module`, the training loop, forward hooks, ONNX conversion, `no_grad`, batching | "Walk me through how you extracted attention from a 15-layer transformer." |
| `uncertainty` | aleatoric vs epistemic, proper scoring rules, CRPS, reliability/coverage, ECE, sharpness-vs-calibration, leave-one-out | "How would you convince a city agency that your uncertainty estimates are meaningful?" |
| `neural-processes` | GP intuition, kernels, meta-learning, CNP encoder/decoder, permutation invariance, ANP, ConvCNP | "You have three monitoring stations. Produce a high-resolution field with uncertainty." |
| `air-quality` | chemistry transport models, CMAQ, EPISODE-CityChem, emissions inventories, downscaling, land-use regression, ultrafine particles | "How would you couple a physics-based CTM with a learned model?" |
| `own-work` | his LC0 interpretability project: attention extraction, the coordinate-frame bug, the history-planes bug, verification discipline | "Tell me about a time you found a serious error in your own work." |

**PyTorch gets the philosophy as well as the terms** — define-by-run versus static graphs, why
autograd builds the graph as it executes, what `nn.Module` is really for, why `no_grad` matters.
Level-1 PyTorch cards should be genuinely elementary; **everything is bottom-up.**

The `own-work` ladder must be sourced from this repo and from
`docs/writeup_attention_frame_bug.md` — it is about *his* work, so accuracy is non-negotiable and
every card needs a repo citation.

## 8. `verify_cards.py` — the content gate

A script that fails loudly on:
1. any card with an empty `sources` list;
2. any `sources` entry that is a repo path which does not exist on disk;
3. any duplicate `id`;
4. any `requires` pointing at a non-existent card, or at a card of level ≥ its own (a cycle or an
   inversion);
5. any ladder with no level-5 card;
6. any card whose text matches a phrase from `06_do_not_claim.md` (load that file, extract the
   forbidden claims, substring-match case-insensitively, report every hit for human review).

Run it in the gate. It must exit non-zero on failure.

## 9. Tests — real guards, mutation-checked

`trainer/tests/test_engine.py`, pure-function tests on `engine.py`:
1. Elo: a user rated 1200 beating a 1600 card gains **more** than beating a 1000 card; assert the
   exact deltas from the §5 formula.
2. Elo is zero-sum in the pinned proportion: the card moves by exactly 8/24 of the user's change,
   in the opposite direction.
3. SM-2: intervals follow 1 → 6 → 6·ease on three consecutive `got it`s; assert the numbers.
4. `missed` resets `reps` to 0 and makes the card due immediately.
5. Ease is clamped at both ends after repeated extreme grades.
6. **Prerequisite gating**: a level-3 card whose `requires` are unmet is never selected, and
   becomes selectable the moment they are all answered at 1.0.
7. Selection stays inside the rating window when enough candidates exist, and widens when not.
8. `verify_cards.py` fails on a card with no source, and on a `requires` cycle (build both
   fixtures).

## 10. Gate — paste REAL output

```
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -v
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer/verify_cards.py
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn trainer.app:app --port 8010
```
Then, in a browser: answer at least five cards at different levels, submit **one comment**, and
paste the resulting `state/comments.jsonl` line and the changed lines of `state/progress.json`.
State plainly which browser you used and what you saw.

Also report: total cards authored per ladder, and the count of cards whose source is a repo file
versus a URL.

## 11. Your report

`agents/reports/2026-08-19_knowledge-trainer-build_REPORT.md`. Include every gate result; the
card counts; **any card you dropped for lack of a source** (this list is valuable, not
embarrassing); anything this brief got wrong; and anything not done.

**The leader will audit the card content itself** — every claim, against its cited source. Author
accordingly.
