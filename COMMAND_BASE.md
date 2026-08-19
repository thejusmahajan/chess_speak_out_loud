# Command Base

This repository is the command base. Three tracks run from it, and they share one
spine. Nothing here moves existing work — the structure is additive, so the
current workflow is untouched.

---

## The spine

The three tracks look unrelated on a CV. They are the same question asked at
three levels of maturity:

| Track | The question | Evidence already produced |
|---|---|---|
| **Weiterbildung** (clinical data) | *Did the model's output survive verification?* | 143k-record pipeline refactored with byte-identical output verified at every step; two pre-existing bugs found and escalated rather than silently fixed |
| **This project** (interpretability) | *Can I trust what the model computes internally?* | Two silent correctness bugs found in my own analysis pipeline — one after publication — and publicly corrected |
| **AEON-UP** (the application) | *Can the model state what it does not know?* | — the job |

**Verify → interpret → quantify.** That is the whole narrative, and it is already
the argument the cover letter makes. It does not need to be invented; it needs to
be made legible.

---

## The three tracks

### 1. BUILD — `backend/`, `frontend/`
Unchanged. The engine, the interpretability toolchain, the training system, the
puzzle trainer. This is where code lives and where results come from.

### 2. LEARN — `docs/study/`
The teaching loop: ask Gemini with `START_HERE_PROMPT.md`, work through a concept
until it is genuinely understood, log the exchange, and fold it into a companion
guide. This has already produced `MCTS_COMPANION_STUDY_GUIDE.md` and its PDF.

The loop is documented in `docs/study/STUDY_PROTOCOL.md` so it repeats cleanly
for the next topic rather than being reinvented each time.

### 3. APPLY — `docs/career/`
Thin by design. The application artefacts themselves live in the `job_search`
repo; what lives here is only the material that depends on *this* project:
- The bridge and the question bank were **not** built here. They live in the application repo:
  `job_search/applications/hereon_aeon_up/study_room/` (files `00`–`11`), with
  `06_do_not_claim.md` as the binding constraint on anything he says or writes.

---

## The bridge that actually works

The instinct to connect the study topic (neural processes) to real project work is
right. But the connection should not be forced through an unrelated toy. There is
a genuine one already sitting in this repository.

**AEON-UP's problem shape:** sparse, irregularly placed sensors; interpolate a
field everywhere; state the uncertainty; prove the uncertainty is honest with
calibration and CRPS.

**The same shape, here:** LC0's value head outputs `w, d, l` — a probability
distribution over outcomes. There are 693 of Thejus' own games with known results.

> **Is BT3's WDL head calibrated?** When it says `w = 0.60`, does the side to move
> actually win about 60% of the time?

That single question exercises AEON-UP's entire evaluation toolkit — reliability
diagrams, Brier score, CRPS, calibration-versus-sharpness — on data that already
exists, with code that already works. It produces a figure and a number, and it is
a real finding either way: a calibrated network is a clean result, a miscalibrated
one is a more interesting one.

It also depends on the history-planes fix. Before that, `evaluate_batch` returned
`wdl = [0,0,1]` on every midgame position, and this experiment was impossible.
Fixing the bug is what unlocked it.

**Sequence:** implement a conditional neural process on synthetic data first (an
afternoon, from the study book) so the vocabulary is real, then run the calibration
analysis. The first makes "I have implemented one" true; the second makes "I have
applied the evaluation methodology to my own model" true.

---

## Sequencing, and one warning

The deadline is **3 September 2026**. (Do not write a day-count here; it rots. Subtract.)

**Before 3 September — only these:**
1. Send the AEON-UP application. Materials are finished.
2. Conditional neural process on synthetic data — half a day, turns reading into
   doing.
3. The Ramacher/Karl research report — so the letter's final paragraph is specific.

**After the application is sent:**
4. WDL calibration analysis — the bridge experiment above.
5. Interview preparation, built from 1–4.
6. Weiterbildung refresh (clinical statistics, tidymodels, the radioDB work).

**The warning, stated plainly.** Building a unified learning system is the kind of
work that feels productive and defers the task that actually matters. This project
already carries forty-odd markdown files at its root; the job search already
carries eight finished applications that were never sent. The failure mode is not
laziness — it is infrastructure that postpones exposure.

So: the spine above is real and worth writing down once. It is now written down.
Everything past that waits until the application is out.

---

## Division of labour

| Who | What |
|---|---|
| **Thejus** | Studying, understanding, asking; sending applications; the decisions |
| **Gemini** | Labour with a detailed brief and checkpoints: research reports, typesetting, data extraction, log processing |
| **Leader (Claude)** | Architecture, briefs, auditing Gemini's output, anything where a wrong answer is expensive |

The standing rule from experience: **delegate code and labour, never content or
judgement.** Every worker deliverable gets spot-checked against its raw output, not
against its own report — the last two both claimed checks they had not performed.

Every brief lives in **`agents/`** (added 2026-08-19) — `agents/ACTIVE.md` says what is
live, `agents/briefs/` is the immutable archive, `agents/reports/` holds deliveries and
audit verdicts. `ACTIVE.md` is grouped **by workspace** — a worker can only act on the repo it has open — so the
instruction is: *read `agents/ACTIVE.md`, find the section for the folder you have open, and
execute its topmost ACTIVE brief.*
