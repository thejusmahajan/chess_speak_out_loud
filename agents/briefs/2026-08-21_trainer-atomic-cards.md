```
Brief-ID:       2026-08-21_trainer-atomic-cards
Written:        2026-08-21
Target repo:    chess_speak_out_loud
Route:          Antigravity (full workspace)
Type:           engine fix (Part A) + content authoring (Part B)
Status:         ACTIVE
Depends on:     2026-08-20_trainer-german-b2 (AUDITED, ACCEPTED)
Blast-radius:   external
Reversibility:  costly
Failure-mode:   SILENT
Why before the deadline item: the application is unsent and outranks this. The trainer is in
daily use and currently recycles the same handful of cards, so it is either fixed or abandoned.
```

# Atomic cards, with examples — and stop repeating the same ones

## INTENT

Thejus reports the trainer showing the same cards repeatedly instead of moving to fresh ones, and
asks for **short sections progressing from low difficulty upward**. Both are correct diagnoses.
A correct result: he meets new material steadily, each card teaches **one** thing, and every
foundational card carries a **concrete example**.

**If any instruction conflicts with that intent, the intent wins — stop and report.**

---

# PART A — the repetition (engine)

## A1. The measurement

```derivation
$ python -c "engine.filter_selectable_cards(...) against the live progress.json"
answers logged:                52     distinct cards seen: 34 of 123
score distribution:            {1.0: 25, 0.5: 5, 0.0: 22}   <- 42% missed
SELECTABLE right now:          16 of 123
  locked by prerequisites:     82
  not due:                     17
  unseen among the selectable:  7
```

Three causes compound:
1. A missed card gets `interval_days = 0`, so it is due again **immediately** and can be served
   next. With a 42% miss rate the same cards cycle.
2. 82 cards are locked behind prerequisites that are not being mastered, so the pool stays small.
3. `select_next_card` has **no recency memory and no preference for unseen cards** — verified: it
   filters by unlock + due, then picks within the Elo window. Nothing prevents an immediate repeat.

## A2. The changes — selection only

Do **not** touch `calculate_elo`, `update_sm2`, `is_card_due`, `is_card_unlocked`, or
`migrate_progress`. All are audited.

1. **Recency buffer.** Track the last **8** card ids served (persist in `progress["recent"]`, a
   capped list). Exclude them from candidates. If that empties the pool, relax to the last 3; if
   still empty, allow anything — never return `None` while any card is selectable.
2. **Prefer unseen.** If any candidate has no entry in `progress["cards"]`, choose only among
   those. New material outranks review while new material exists.
3. **Failed cards return later, not next.** A card scored 0.0 becomes eligible again after **at
   least 5 other cards** have been served, not immediately. Keep `interval_days = 0` — this is a
   selection rule, not an SM-2 change.

## A3. Tests (Part A)

1. `test_no_card_repeats_within_recency_window` — serve 20 cards from a pool of 30; assert no id
   appears twice within any window of 8.
2. `test_unseen_cards_are_preferred` — a pool with 5 unseen and 5 reviewed; the next 5 served are
   all unseen.
3. `test_failed_card_returns_after_five_others` — score a card 0.0; assert it is not among the
   next 5 served, and does reappear afterwards.
4. `test_selector_never_starves` — with only 2 selectable cards and a recency window of 8, the
   selector still returns a card rather than `None`.

**Mutation-check test 1**: remove the recency filter, confirm it fails, restore.

---

# PART B — atomic cards with examples

## B1. His comments are the specification

Verbatim from `trainer/state/comments.jsonl`. **These name real gaps — do not paraphrase them away.**

| card | his comment |
|---|---|
| `pyt-l0-007` | *"What is a softmax function? I have heard of it but how is it used here?"* |
| `pyt-l0-005` | *"So this a gradient on the loss curve indicating its direction of maximum increase?"* |
| `pyt-l0-003` | *"Is the stretched part be all zeros?"* ← **a misconception; broadcasting repeats values, it does not zero-fill. Correct it explicitly.** |
| `pyt-l0-001` | *"It is interesting to know what quality of numpy array prohibits it to use the GPU. Basically they are just numbers."* |
| `unc-l0-001` | *"Why is the variance sigma sq and not just sigma?"* |
| `np-l0-003` | *"What do you mean by 'retaining in its formulation'? Does it keep on holding data or what is going on?"* |
| `np-l0-002` | *"What is meant by 'share high kernel covariance'? I don't understand this usage of the term covariance."* |
| `own-l1-001` | *"I am still grappling with the idea of a transformer… what exactly are these transformers and how do they work? I think I need this built step by step conceptually."* |
| `de-kon-l0-003` | *"I would really like some examples here and I am seeing these words for the first time and I am B1."* |
| `de-gra-l0-001` | *"I would like some examples to practice."* |
| `de-gra-l0-003` | *"Some example sentences and splitting this into manageable or palatable questions would be nice."* |

## B2. The rule this establishes

**One card, one idea, one example.**

- A card whose answer introduces **two** unexplained terms must become **two cards**.
- `de-gra-l0-001` asks for four Genitive prepositions at once. **Split it into four**, each with a
  real example sentence.
- Every Level-0 card must contain a **concrete example** — a number, a shape, a sentence, a line of
  code. He has asked for examples three times.
- Keep answers to **2–4 sentences**. If it needs more, it is more than one card.

## B3. New cards to author

**`pytorch` L0** — softmax (what it does to logits, with a worked 3-number example) · gradient as
direction of steepest increase and why we step *against* it · why a NumPy array cannot run on a GPU
(it is not "just numbers": no device pointer, no CUDA kernels, no autograd tape) · **broadcasting
repeats values, it does not pad with zeros** — show `(3,1)+(1,4)` element by element.

**`uncertainty` L0** — why variance is σ² and not σ (units, additivity), and what σ gives you back.

**`neural-processes` L0** — what "retaining data in its formulation" means, concretely (a GP keeps
the training points; an MLP does not) · what covariance means before "kernel covariance" is used.

**`own-work`** — a genuine **step-by-step transformer sub-ladder at L0**: what a token is here (one
square) · what an embedding is · what "attention" means in one sentence, no matrices · query/key/value
in plain words · what a head is · what stacking 15 layers does. Six or so cards, each with an
example. He asked for this explicitly and it currently jumps straight to attention extraction.

**`de-grammatik` L0** — a **Genitiv refresher before** any Genitive-preposition card (what the case
marks, `der/des/dem/den`, with examples) · then `aufgrund`, `trotz`, `während`, `wegen` as **four
separate cards**, each with one example sentence from DWDS.

**`de-konnektoren` L0** — every connector card gains a **German example sentence** showing the word
position it forces. He is B1 working toward B2: introduce the word, then its syntax, as separate
cards.

## B4. Pitch the German at B1 → B2

He states plainly that he is B1 and meeting these connectors for the first time. Level 0 in the
German ladders is the **bridge from B1**, not a B2 warm-up. Where a card assumes B2 vocabulary to
explain a B2 point, insert the B1 step beneath it.

## B5. Rules that still stand

Sources on every card (DWDS/Duden/Goethe for German; PyTorch docs or a real paper for ML). No
invented German. Rubrics on production cards. Equations stay and must render — **do not strip
LaTeX**. Umlauts intact.

## B6. Gate — paste REAL output

```
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer/verify_cards.py
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer/verify_cards.py --check-urls
git status
```

Plus, and these are the ones that matter:
- **the 400-draw distribution** against the live `progress.json`, per ladder and per level —
  standing gate for every trainer brief now, because three times running, correct content has been
  authored and left unreachable;
- **a 30-draw sequence printed as a list of card ids**, showing no repeat within any window of 8;
- the count of new cards per ladder, and every card you **split**, with old id → new ids;
- the mutation proof for the recency filter.

## B7. Your report

`agents/reports/2026-08-21_trainer-atomic-cards_REPORT.md`. All gate output, the split table,
anything this brief got wrong, and — required —

> **"If exactly one thing in this delivery is still wrong, what is it most likely to be, and did I
> check it?"**
