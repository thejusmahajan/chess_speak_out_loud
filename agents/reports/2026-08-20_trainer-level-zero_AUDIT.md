# AUDIT — `2026-08-20_trainer-level-zero`

**Auditor:** Leader (Claude Opus 5) · **Date:** 2026-08-19
**Verdict: ACCEPT THE CONTENT. THE FEATURE DOES NOT REACH THE USER.**
The Level-0 cards are well written and do exactly what was asked. **The selector will never serve
them**: at his current rating the Elo band sits entirely above the Level-0 difficulty range. 400
of 400 simulated draws returned Level 1. Content authored, intent unmet.

---

## 1. Boundaries — PASS, with two benign out-of-scope edits

`trainer/` plus the report, as declared. Two small edits outside the brief's list, both harmless
and disclosed in the report: one CSS line in `index.html` for a level-0 badge, and a status update
to `agents/ACTIVE.md` marking its own brief DELIVERED. The ledger is the leader's file; marking
delivery is acceptable bookkeeping, but the **audit verdict column stays mine**.

## 2. The user's actual complaint — FIXED

He wrote: *"the Latex is not rendering."* He had been reading raw `$\sigma_m^2(x)$`.

**Zero cards now contain `$` or any LaTeX command** — checked across all 78 cards and every field.
A gate was added to `verify_cards.py` and, per the report, mutation-tested.

## 3. Content — PASS, and genuinely at the right level

18 Level-0 cards, difficulty 780–840. Sampled against his verbatim comments:

| his question | card | verdict |
|---|---|---|
| *"What are logits? Aren't they probabilities in percent?"* | `pyt-l0-007` | **Excellent** — the question literally asks "and are they probabilities in percent?"; the answer states they "do NOT sum to 1 or 100%" |
| *"What is the significance of 'zero' in `optimizer.zero_grad()`?"* (asked twice) | `pyt-l0-006` | Correct — explains PyTorch accumulates gradients by default |
| *"What is broadcasting? I haven't heard of it in a programming context."* | `pyt-l0-003` | Concrete: (3,1)+(1,4) → (3,4), as specified |
| *"What do you mean by model capacity?"* | `np-l0-001` | Plain, straight-line vs deep-net example |
| *"What are kernel matrices?"* | `np-l0-002` | Plain: similarity function, N-by-N table |

No LaTeX, one idea per card, concrete examples. These are answerable by a physicist with no
deep-learning background, which was the whole requirement.

## 4. Re-levelling — PASS

`unc-l1-003` — *"How do Deep Ensembles estimate epistemic uncertainty?"*, answered via the Law of
Total Variance, authored at **Level 1** — is now `unc-l3-003` at **Level 3, difficulty 1480**. A
plain "what is an ensemble and why do models disagree" card sits at Level 0 (810).

Every card he flagged now carries a `requires` link to its Level-0 prerequisite.

## 5. Prerequisite gating — PASS, verified behaviourally

Not read — executed:

```
new user:                            pyt-l1-003 locked            -> True
after mastering pyt-l0-003 (1.0):    pyt-l1-003 unlocked          -> True
after only a PARTIAL (0.5):          pyt-l1-003 still locked      -> True
```

The partial case was my own addition and also passes: a half-remembered prerequisite does not
unlock the card above it.

*(One correction against myself: my first gating test reported a failure. My test was wrong — the
progress dict nests under a `"cards"` key and I passed a flat one. I nearly filed a defect that
was my own measurement error. Checked the function before claiming; this is why.)*

---

## 6. THE BLOCKING DEFECT — the cards exist and cannot be reached

Measured on his real `progress.json`:

```
stored user rating:                      1055.6
selection window (±150):                 905 – 1205
Level-0 card difficulty range:           780 – 840     <-- entirely BELOW the window
Level-1 card difficulty range:          1020 – 1060    <-- squarely inside it

level served over 400 simulated draws:  {1: 400}
```

**He would never see a single Level-0 card.**

The Elo band assumes a user's rating reflects their knowledge. His 1200 starting rating was an
assumption, and in this material he is genuinely below the Level-0 band. The rating decays at
K=24, so it would take dozens more failures to fall to 840 — and every one of those failures would
be on a Level-1 card he has already told us he cannot parse.

**This is the failure class this project keeps producing**: every gate passes, the artefact is
correct in isolation, and the intent is not served. The brief asked for a ground floor; a ground
floor was built; the staircase does not descend to it.

**Root cause is mine.** I specified Elo-band selection in the original trainer brief and never
reconciled it with level-based progression. Elo across the whole card pool competes with the
ladder; it should choose *within* a level, not across levels.

### The fix, and why this one

Serve the **lowest level that still has unmastered cards**, and use Elo only to order *within*
that level. This matches how the Lichess trainer actually behaves — a rating within a pool, not a
rating that selects the pool — and it matches what he asked for in plain words: *"I need to start
from the very basic concepts."* Per-card `requires` is not sufficient, because many Level-1 cards
have no prerequisites and so remain reachable.

His rating should also be reset to the Level-0 band, since 1055 was inherited from an assumption
that has now been falsified by evidence.

## 7. What I could not check, and the one thing most likely still wrong

I did not run the app in a browser or exercise the comment box end to end; I read the state files
it wrote, which is weaker evidence. I verified 5 of 18 Level-0 cards deeply and the rest only for
LaTeX and structure.

**If exactly one thing in this delivery is still wrong, I predict it is a Level-0 card in the
`air_quality` or `uncertainty` ladder that still assumes a term it has not introduced** — those two
have the least of his direct feedback pointing at them (his comments were concentrated on PyTorch
and neural processes), so they had the weakest specification and I have the least independent
signal about whether they land. That is the opposite of where I looked, which is why it is written
down.
