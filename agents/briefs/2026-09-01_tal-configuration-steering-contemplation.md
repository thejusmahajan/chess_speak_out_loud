```
Brief-ID:     2026-09-01_tal-configuration-steering-contemplation
Written:      2026-09-01
Target repo:  chess_speak_out_loud
Route:        Antigravity (full workspace)
Type:         contemplation / design exploration  -- NOT implementation
Blast-radius:  one new document
Reversibility: trivial
Failure-mode:  SILENT -- a confident design built on a misread of the idea wastes a training run
```

**Why this before the deadline item?** The interview is the live item and remains so. This is the
chess project's north-star direction and Thejus asked for it explicitly today. It costs one
document and no compute.

---

## 1. INTENT

*(Intent outranks instructions. If any instruction below conflicts with this paragraph, the intent
wins — stop and report. Doing so is a success, never a boundary violation.)*

Thejus has an idea about steering a quiet chess position toward the kind of position from which a
tactic exists. **Your task is to understand it and contemplate how it could be achieved.**

**Do not implement anything. Do not write code. Do not train anything.** Produce one document of
analysis and proposed approaches.

**The leader has deliberately withheld his own view of how to do this.** A previous leader-written
discussion of this idea was rejected by Thejus and deleted, because it argued from a premise he
does not hold. You are being asked precisely because your thinking should be independent. **Do not
search the git history for the deleted document. If you encounter it, stop reading it and say so
in your report.**

**Do not agree by default.** A proposal you cannot see a serious objection to is a proposal you
have not thought about hard enough.

---

## 2. The idea, in his words

**Read `ideas/2026-09-01_steering_to_tal_configurations.md` in full before anything else.** It
contains his statement verbatim in sections 1 and 2, and a measured inventory of what is on disk
in section 3. Quote from it exactly if you quote at all.

The essentials, so you do not misread the aim:

1. **The target is the CONFIGURATION, not the move.** In his words: *"For a player, making that
   moves once the position is reached is easy, but getting that position is what needs carefully
   study."* The interesting problem is arriving at a position of a certain shape, not choosing
   well once you are there.
2. **The Lichess puzzle starting positions are the thing to learn from.** *"we first learn from
   the configuration of the lichess puzzles. This confuguration are what we aim for."*
3. **Then work backwards.** *"If there are pieces and pawn positions that could possibly lead to
   the starting positions in the puzzle we will find moves that will steer our quiet position or
   position in hand towards it."*
4. **Rolling back a few plies from a tactical position is explicitly retained** as a useful device.
5. **A binding constraint from him, and take it seriously:** *"LC0 evaluating a position good
   doesn't mean it is a tactical position."* A high engine evaluation is not a tactic detector. Do
   not build anything that quietly assumes it is.
6. He suggests PyTorch, and Kaggle or Colab for training, and regards the build as a learning
   exercise in its own right. Weigh that as a real requirement, not a footnote.

---

## 3. What you may use

Everything in section 3 of the ideas document is on disk now, in this repository:

- `data/puzzles/puzzles.sqlite` — 5,527,851 puzzles with `fen`, `moves` (the solution line in
  UCI), `rating`, `themes`, `opening_tags`; plus `puzzle_flags` with `quiet_first`.
- `backend/training/relational_facts.py` — an existing extractor that turns a position into
  grounded true statements about piece relationships.
- `backend/neural_vision.py` — forward hooks capturing LC0 BT3 attention, `[15, N, 24, 64, 64]`,
  and policy-prior extraction.
- `backend/training/metrics.py`, `backend/engine_pool.py`, `data/training/cache/steer.jsonl`.

**Verify anything you cite.** Open the file, run the query, paste the output. Do not describe a
schema or a function signature from memory.

---

## 4. What to produce

Write `agents/reports/2026-09-01_tal-configuration-steering-contemplation_REPORT.md`.
**Create no other file. Modify no existing file. Do not commit.**

Structure it as you think best, but it must answer these, which come from his own text:

1. **Representation.** He wants to learn from "the configuration" of puzzle positions. What IS a
   configuration, computationally? What are the candidate representations, and what does each one
   make easy or impossible? Consider at least: raw board planes, piece-square occupancy
   statistics, relational/graph features, and learned embeddings.
2. **Learning target.** What exactly would a model be trained to output, such that it is useful
   for his aim? Note that his aim is not "is there a tactic here" but "is this position on the way
   to one". Be explicit about what the label is and where it comes from.
3. **The backward step.** He wants positions that *lead to* puzzle starting positions. How would
   you obtain or construct them at scale from what is on disk? What are the options, and what does
   each cost?
4. **The negative class.** Whatever you propose to train, say what it is trained *against*, and
   why that choice does not make the problem trivially easy in a way that would produce a useless
   model.
5. **The five-to-seven list.** He wants a short list of candidate target arrangements for a given
   position. How would such a list be produced, and how would each candidate be scored for whether
   it is actually reachable?
6. **Combining with LC0.** Given a target configuration, how do you find moves toward it without
   blundering or losing evaluation? Name the concrete mechanisms available in an
   AlphaZero-style engine and what each would require of us.
7. **The falsification test.** State, in advance, what measurable result would show this direction
   does not work. Be specific enough that we could run it.
8. **The strongest objection.** Argue the best case *against* the whole approach — not a token
   caveat, the argument you would make if you were trying to stop us spending a month on it.

---

## 5. Constraints on your answer

- **Cheapest informative experiment first.** For every approach you propose, say what the smallest
  experiment is that would tell us whether it is worth continuing, and what it costs in compute.
- **Do not invent numbers.** If you state a dataset size, a runtime or an accuracy, it must come
  from a query you ran or a paper you name. An estimate must be labelled as an estimate.
- **Name papers precisely** if you draw on literature — title, authors, year, arXiv id — and only
  ones you are confident exist. A fabricated citation is worse than no citation.
- **Distinguish clearly** between what is already built in this repository, what is standard and
  available off the shelf, and what would have to be invented.
- **Say what you do not know.** A non-empty "could not check" section is required.

---

## 6. Stop and ask

Not covered by this brief: writing code, modifying any existing file, training anything, running
LC0 over the puzzle corpus, committing, or reading the deleted round-table document from git
history. If the task appears to require any of these, **stop and report**.

**Do not commit. The leader audits the document, and Thejus decides.**
