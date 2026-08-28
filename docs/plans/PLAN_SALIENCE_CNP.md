# PLAN — Calibrated salience: the CNP toolkit applied to the north star

> Written 2026-08-18. Supersedes the assumption, recorded in memory and in
> `LEADER_BIBLE.md` §6, that the salience corpus is "gold tier seeded, 7 records."
> **It is measured below and it does not work.** Read §1 before anything else; the
> rest of the plan exists because of it.

---

## 1. CURRENT STATE — measured today, not recalled

Every number here came from running the code, not from reading a report.

### 1.1 What is built and works

`backend/training/relational_facts.py` — the machine's eyes. Emits **11 fact kinds**
across the corpus:

```
king_pressure 576 · pawn_weakness 436 · file_control 398 · pin_or_xray 228
bishop_quality 169 · color_complex 122 · tied_defender 103 · outpost 100
attack_on_valuable 81 · protected_passed_pawn 47 · rook_seventh 24
```

Signature is `relational_facts(fen, line_ucis, pov: chess.Color)`. **Static facts are
sparse** — 5 to 8 for a typical middlegame. The volume that the salience problem
describes comes from `per_move`, which requires a *line*. No line, no rich facts.

### 1.2 What is broken — the finding

| measurement | value |
|---|---|
| corpus records built | **288** |
| gold tier (Capablanca 1921) | **7** |
| bronze tier (unverified annotators) | **281** |
| facts across all records | **2,284** |
| facts labelled salient by `align_prose_to_facts` | **19** (0.8%) |
| **salient labels on the gold tier** | **0 out of 35 (zero)** |
| records with at least one label | 16 of 288 (6%) |

**There is no supervised signal.** Nineteen noisy labels, none of them from the only
source that clears the project's own quality bar.

### 1.3 Why gold yields exactly zero — three mechanical causes

Not bad luck. Each is guaranteed by construction.

**(i) The book parser emits sentence fragments.** The seven gold "GM comments" are:

```
"has the advantage of remaining with two Bishops while White has only one."
"therefore have a won ending."
"as his 28th move. The rest of his play was good, probably perfect."
"which he only lost through a blunder."
"P - B 3 is probably the best move in this position. I do not like the text"
"Black naturally did not want to make a second move with this Bishop."
"It would have been better for Black to play K - Q 1. The text move loses"
```

Four begin mid-sentence with no subject. At least three carry **no positional content
at all** — they are narrative about the game, not statements about the position. A
label extracted from "which he only lost through a blunder" would be noise even if the
matcher fired.

**(ii) Notation mismatch.** Capablanca 1921 is written in **descriptive** notation —
`P - B 3`, `K - Q 1`. `salience_matcher._SQUARE_RE` matches `[a-h][1-8]` only. The
matcher's hard grounding gate drops any fact whose square the annotator "did not name",
and the annotator can never name one the regex recognises. **The score is forced to
zero by construction.** `backend/training/descriptive_notation.py` exists but is not
wired into the matcher.

**(iii) Vocabulary gap.** Capablanca's headline concept in the first gold record is the
**two bishops**. The extractor has no bishop-pair fact — `bishop_quality` is about good
vs bad bishops, a different concept. The master's primary idea is invisible to the
machine, so no ranking over the machine's facts can ever recover it.

### 1.4 The uncomfortable part

`salience_matcher.INFERENCE_PRIORS` is a **hand-coded table** of how load-bearing each
fact kind is (`defender_removed: 1.00`, …). `LEADER_BIBLE.md` §6 states the rule
plainly: *"Do NOT hand-code salience — that repeats the `had_tal` mistake; emit true
facts, let the learned layer rank."* The learned layer was never built, so the
placeholder became the implementation.

This is the project's own **metric-mislabel family**, one level up. The failure is not
in a metric this time — it is in the *label generator*, which everyone (this leader's
memory included) recorded as an asset without measuring its yield.

---

## 2. TRAJECTORY — where this has to go

The north star: LC0's real thoughts → true facts → **the few that matter** → the LLM
translates, never reasons. Two organs are missing, and they are the same organ:

**Leg A — labels that exist.** Salience cannot be learned from 19 examples, and it must
not be hand-coded. Something has to produce labels at scale.

**Leg B — a ranker that knows when it doesn't know.** The motto is *a bad coach does
more harm than no coach*. Nothing in the system today can express confidence:
`INFERENCE_PRIORS` is a fixed table with no notion of "I am not sure about this
position." **A coach that cannot abstain cannot honour the motto.** Abstention is not
a nice-to-have; it is the motto expressed as code.

---

## 3. THE CNP TOOLKIT ON THE TABLE

Five separable tools, from `cnp_synthetic/`:

| # | tool | what it does |
|---|---|---|
| (a) | permutation-invariant set encoding (mean aggregation / DeepSets) | turn a variable-size **unordered set** into one fixed vector |
| (b) | conditioning on a small **context set** | adapt to a new task from a handful of examples, **no retraining** |
| (c) | heteroscedastic head | output **μ and σ** — the answer *and* the confidence |
| (d) | calibration machinery | coverage curves, ECE, PIT, CRPS — *is* the confidence honest? |
| (e) | leave-one-out under scarcity | the only sound validation when n is tiny |

---

## 4. THE LINK — and why it is genuine, not decorative

Taking each tool against the measured state of §1:

**(a) Facts are a set.** A position yields an unordered, variable-length collection of
facts. Mean aggregation is the *correct* architecture, not a stylistic preference — any
order-dependent encoder silently asserts that fact order carries meaning. It does not.

**(b) This is the load-bearing insight.** Gold annotations will *always* be scarce.
There is no future in which 100,000 Capablanca comments exist. Every plan that says
"train a salience model on GM annotations" is therefore already dead — including the
one currently written into `GM_CURRICULUM_PLAN.md`.

> A CNP does not **train on** the small set. It **conditions on** it.

Twenty repaired Capablanca records are useless as a training set and ideal as a
**context set**. Scarcity stops being the blocker and becomes the design assumption.
That is why the CNP is the right tool here and not an imported toy — the project's
worst data problem is precisely the problem this architecture was invented for.

It also buys something the product wants anyway: swap the context set, change whose
taste the coach has. Capablanca's context set → classical positional emphasis. The
user's own history → what *this* student keeps missing. Same weights, no retraining.

**(c) μ and σ.** "How salient" and "how sure" — two numbers where the system currently
has one hard-coded constant.

**(d) Calibration is the motto, mechanised.** *A bad coach is worse than no coach*
translates exactly into: **speak only above a confidence threshold.** The abstention
curve — precision of the named fact against the fraction of positions we speak on — is
the product specification, and it is the same curve as calibration-versus-sharpness.
A coach that is silent 70% of the time and right 95% of the time when it speaks is a
good coach. One that always speaks and is right 60% of the time is the thing the motto
forbids.

**(e) Leave-one-out.** With 7–30 gold records there is no test split. Leave-one-out is
the only honest protocol — the same one used on the 25 stations in the CNP work.

**The dual payoff.** The same artifact answers Hereon's interview question and advances
the north star. Both are literally: *few observations, predict everywhere, state the
uncertainty, validate by leave-one-out under scarcity.* One method, two payoffs — this
is a real structural identity, not a CV stretch.

---

## 5. THE CORPUS ANSWER — already on disk

`data/puzzles/puzzles.sqlite` — **5,527,851 puzzles**, 73 distinct themes. A theme is a
human-curated statement of *what the point of this position is*: `deflection`, `fork`,
`pin`, `discoveredAttack`, `attraction`, `hangingPiece`, `sacrifice`, `defensiveMove`,
`advancedPawn`, `promotion`, `exposedKing` … roughly 35 of the 73 are salience
statements; the rest are metadata (`short`, `master`, `middlegame`, `crushing`).

**Verified today, and it changes the build:** each row carries its own solution line in
`moves`. Feeding that line to `relational_facts` produced **9 static + 16 per-move = 25
facts** on a `deflection` puzzle — **with no engine call at all.**

So the label bottleneck is not real. It is 5.5M labelled positions sitting in the repo,
extractable on CPU.

**The honest limitation, which must be stated everywhere this corpus is used:** puzzle
themes cover the **tactical** shape of salience. `docs/SALIENCE_PROBLEM.md` names four
shapes — tactical, positional/quiet, defensive, prophylactic/move-order. Puzzles largely
solve one, touch a second (`defensiveMove`), and miss the quiet and prophylactic shapes
entirely. Those remain GM-annotation territory, which is exactly what the context-set
mechanism of (b) is for. **Puzzles pretrain the representation; gold conditions the
taste.** Do not let the puzzle corpus quietly redefine salience as "tactics".

---

## 6. THE BUILD — staged, each stage gated

Sequenced so that the cheap thing that can invalidate the expensive thing runs first.

### Stage 0 — repair the label pipeline (local, CPU, no GPU, no Kaggle)

1. Fix book-parser segmentation: comments must be whole sentences.
2. Wire `descriptive_notation.py` into `salience_matcher` so 1921 text can ground.
3. Add the missing master vocabulary, **starting with `bishop_pair`** — Capablanca's
   literal first concept.

**GATE 0 (blocking):** gold label yield rises from **0/35** to a measured non-zero
number, *and* the user reads 10 sampled (comment → chosen fact) pairs and answers the
one load-bearing question: **would a master say that?** No later stage starts until
this passes. If the gold corpus cannot be repaired, we learn that for a day of CPU
rather than after a Kaggle campaign.

### Stage 1 — the puzzle corpus (local first)

Extract facts for puzzles using each row's own `moves` as the line. Label = the row's
themes, restricted to the ~35 salience-bearing ones. Start at **2,000 puzzles locally**
to prove the pipeline end to end.

**GATE 1:** a fact-set + theme-label dataset on 2k puzzles, with a per-theme count
table and the extraction rate. Spot-check 10 by eye.

### Stage 2 — scale (this is the only place Kaggle is even a question)

Extraction is **CPU-bound and embarrassingly parallel**, with no engine in the loop.
Kaggle is therefore a *convenience*, not a necessity — and given the Kaggle failure
family in `LEADER_BIBLE.md` §5b, convenience is not worth the infrastructure fight.

**Decision rule, to be answered with a measurement at Gate 1, not now:** time the local
extraction rate on 2k puzzles. If 100k positions extract locally in under one overnight
run, **stay local**. Move to Kaggle only if that measurement says otherwise.

### Stage 3 — the model

CNP over fact sets. Encode each fact → mean-aggregate → position representation `r` →
decode each fact conditioned on `r` → `(μ, σ)` for its salience. Context set selects
whose taste. Abstain when `σ` is high or `μ` is low.

### Stage 4 — the evaluation that *is* the product question

- **The abstention curve** — precision of the top-1 named fact vs. coverage (fraction of
  positions spoken on). The headline result.
- **Calibration** — reliability diagram and ECE over fact-level salience, with mean σ
  always reported beside it.
- **Leave-one-out** on the repaired gold records.
- **The baseline that gives the numbers meaning: the existing hand-coded
  `INFERENCE_PRIORS` table.** The learned ranker must beat it. If it does not, that is
  the finding and it gets reported as such — it would mean the hand-coded prior already
  captures what the facts can express, which is worth knowing.

---

## 7. DIVISION OF LABOUR

| who | what |
|---|---|
| **Leader (Claude)** | the featurizer contract, label semantics, metric definitions, stage gates, every audit |
| **Gemini** | parser repair, the descriptive-notation bridge, bulk extraction script, training-loop boilerplate, plots — always against a pinned spec |
| **Thejus** | Gate 0's *would a master say this?*, and the user's-eye pass on the prototype |

Standing rule unchanged: **delegate code and labour, never content or judgement**, and
audit the diff rather than the report.

---

## 8. WHAT THIS PLAN DELIBERATELY DOES NOT DO

- It does not build a unified learning system, a new UI, or more detectors.
- It does not touch the AEON-UP application, whose deadline is **3 September** and which
  is still unsent.
- It adds exactly one document — this one. `COMMAND_BASE.md` warns that infrastructure
  which feels productive is how exposure gets postponed. Stage 0 is one day of CPU work
  against a measurable gate, and it is the whole of the next step.
