# AUDIT — `2026-08-21_trainer-atomic-cards`

**Auditor:** Leader (Claude Opus 5) · **Date:** 2026-08-21
**Verdict: ACCEPT.** The repetition is fixed, the named gaps are filled, and the content is
better than specified. No leader fix required — the first trainer delivery in this sequence where
that is true.

---

## 1. Boundaries and gates — PASS

`trainer/` plus the report (and a status line in `ACTIVE.md` — worker bookkeeping, as before).
137 cards, up from 123. `verify_cards.py` exits 0. Suite **26 passed** (was 22).

## 2. The repetition — FIXED, verified behaviourally

```
30-draw sequence, engine managing its own recency state:
   repeats within any window of 8:  0
simulating the app's real loop (select -> grade -> persist):
   distinct cards in 30 draws:      27 / 30
400-draw standing gate:             all level 0 (correct — he is at L0 across ladders)
```

Before this delivery the same handful cycled. The recency buffer, the unseen-preference and the
failed-card delay all work.

**Two of my own measurements were wrong before I got this right, and the pattern is worth
recording.** First I managed `progress["recent"]` myself in the harness — the engine maintains it
internally, so I was corrupting its bookkeeping and saw 11 false "repeats". Then I simulated
`select_next_card` in a loop **without grading**, so no card ever became "seen", the
unseen-preference correctly kept returning the same 12 unseen cards, and I read that as a pool
starvation bug. Both times I read the implementation before filing a defect, which is the only
reason neither was reported.

**Lesson for future trainer audits: simulate the app's actual loop — select, grade, persist — not
the selector in isolation.** A selector measured without its state transitions will lie.

## 3. Content — PASS, and it exceeds the brief

His comments were used as the specification. Checked against them directly:

| his comment | result |
|---|---|
| *"Is the stretched part be all zeros?"* | **`pyt-l0-003` now asks "does it pad missing dimensions with zeros?" and answers "it NEVER pads with zeros"**, with the reason (zero-padding would corrupt the arithmetic) and a `trap` naming the misconception. His exact question, corrected head-on. |
| *"I would like some examples to practice"* (German) | Example sentences present — `des Lehrers`, `der Frau`, `aufgrund des Wetters`, `Trotzdem arbeitete er`. They live in the `trap` fields as wrong/right pairs, which is stronger than a bare example. |
| *"splitting this into manageable questions"* | The four-preposition card is split into `de-gra-l0-001a/b/c/d`, one preposition each. |
| *"I feel like I forgot what genitive is"* | **`de-gra-l0-gen`** added *beneath* the preposition cards — "Wessen?", the article table, and a trap correcting `*der Fraus*`. |
| *"I need this built step by step conceptually"* (transformers) | A genuine sub-ladder: `own-l0-003` token → `004` embedding → `005` attention in one plain sentence, no matrices → `006` Query/Key/Value in plain words → `007` head, and why 24 → `008` what 15 stacked layers do. Difficulty 785 → 825. |
| *"What is a softmax function?"* · *"Why is variance sigma sq?"* · *"what quality of numpy array prohibits GPU"* | All addressed at L0. |

The `trap` field is doing real work here. `de-kon-l0-001` distinguishes `obwohl` from `trotzdem`
and then shows the concrete error: *"\*Trotzdem er müde war, arbeitete er\*"* is wrong, it must be
*"Trotzdem arbeitete er"*. That is the B2 marking criterion, taught as a contrast rather than a rule.

## 4. Not defects, but worth knowing

**82 of 137 cards remain locked** behind prerequisites, so roughly 29 are reachable at any time.
That is the bottom-up design working, not a fault — the pool opens as Level 0 is mastered. It does
mean progress is gated on actually mastering the foundations, which is the point.

## 5. What I could not check, and the one thing most likely still wrong

I did not run the app in a browser, did not resolve all external URLs this round, and read roughly
10 of the 41 Level-0 cards in full.

**Prediction made, then tested, and it was WRONG — recorded because a prediction only counts if
it is scored.**

I predicted German Level 0 would fall out of the selection window before being mastered: the
ladder rating is 1200 and those cards sit at 1080–1145, inside the ±150 window by only 20–30
points, so a run of correct answers should evict them. I simulated 40 consecutive correct answers
in `de-grammatik`:

```
after  1 correct: rating 1153, L0 still selectable: 6
after 10 correct: rating 1255, L0 still selectable: 6
after 20 correct: rating 1381, L0 still selectable: 6
after 40 correct: rating 1604, L0 still selectable: 6
```

The rating climbs 400 points and Level 0 stays reachable throughout. **The level gate protects
it**: the ladder holds at its lowest unmastered level and the Elo window only orders *within* that
level — which is precisely the fix applied two briefs ago. The mechanism I was worried about was
already immunised by an earlier repair, and I did not connect the two until I ran it.

**Revised prediction:** the most likely remaining error is now a content one — a Level-0 card whose
answer still introduces a second unexplained term, in `de-wortschatz` or `air-quality`, the two
ladders his comments have never touched and which therefore had the weakest specification.
