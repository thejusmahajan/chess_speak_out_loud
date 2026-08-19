# AUDIT — `2026-08-19_knowledge-trainer-build`

**Auditor:** Leader (Claude Opus 5) · **Date:** 2026-08-19
**Verdict: ACCEPT THE ENGINE. REJECT THE `air-quality` LADDER. FIX THE CONTENT GATE.**
The machinery is sound and mutation-tested. Two CRITICAL content findings — one a **non-existent
citation used five times**, one the **do-not-claim gate silently enforcing a paraphrase instead of
the real file**, which is precisely the failure the brief was written to prevent.

---

## 1. Boundary check — PASS

Only `trainer/` created. No existing file touched. Nothing committed. 60 cards, 5 ladders × 12, as
specified.

## 2. Engine — PASS, mutation-tested

| check | result |
|---|---|
| `pytest trainer/tests -q` | **9 passed** |
| `verify_cards.py` on clean content | exit **0** |
| mutation: strip a card's `sources` | detected, exit **1** |
| mutation: point a source at a nonexistent file | detected, exit **1** |
| file restored byte-identical after each | confirmed |

The gate is real, not decorative.

## 3. Constraint (c) — the a8/h8 frame — PASS, and handled well

All three `h8` occurrences are in **`trap` fields** — the common wrong answer — with the correct
reason attached:

> *"Stating that internal index 0 for Black is h8 (which would be a 180-degree rotation flipping
> both rank and file, placing White's king on d8)."*

The level-3 answer states the transform correctly: `i ⊕ 56`, vertical reflection, rank flipped,
file preserved. This drills the error **out**, which is what was asked.

## 4. Constraint (b) — forbidden sources — PASS

No card cites `SALIENCE_PROBLEM.md`, `GM_CURRICULUM_PLAN.md`, anything under `archive/`, or the
stub `CONCEPT_INDEX` chapters. Verified by grep across all five ladder files.

## 5. Random spot-check — PASS (5 cards, seeded random, not chosen by me)

Per the rule that I audit where I am comfortable and errors are elsewhere, the sample was drawn
with a fixed seed rather than selected. `own-l3-002`, `own-l2-001`, `own-l4-002`, `unc-l5-001`,
`pyt-l2-001`.

Content accurate in all five. The hook path `module.encoder{i}/mha/QK/softmax` matches
`neural_vision.py`. The Gneiting & Raftery DOI is correct. **`arxiv.org/abs/1910.13556` verified as
Gordon et al., *Convolutional Conditional Neural Processes*** — which also means the earlier
`salience-cnp-brainstorm` report, which cited `1910.13551`, was wrong and **I did not check its
citations during that audit.** Recorded as my own miss.

---

## 6. CRITICAL — a non-existent citation, used five times

`https://doi.org/10.5194/gmd-12-4857-2019` **does not resolve.** Checked by two independent routes:

- `doi.org/10.5194/gmd-12-4857-2019` → **HTTP 404**
- `gmd.copernicus.org/articles/12/4857/2019/` → **HTTP 404**

The real paper is **`10.5194/gmd-12-3357-2019`** — verified live:

> *"The Eulerian urban dispersion model EPISODE – Part 2: Extensions to the source dispersion and
> photochemistry for EPISODE–CityChem v1.2 and its application to the city of Hamburg"* —
> **first author Matthias Karl.**

`4857` versus `3357`: a near-miss of a real DOI, which is the classic fabrication signature —
structurally valid, plausible, wrong.

**Where it lands makes it worse.** It is on **5 of the 12 `air-quality` cards**, and is the *only*
external source on four of them. That is the ladder closest to the actual job, and the paper it
gestures at was **written by the man who would be interviewing him.** Citing Karl's own paper with
a fabricated DOI is a worse outcome than not citing it.

## 7. CRITICAL — the do-not-claim gate enforces a paraphrase, not the real file

Brief §0(a) was explicit: load the real
`job_search/.../study_room/06_do_not_claim.md`, *not* an in-repo paraphrase, because that exact
substitution is what let "mechanistic interpretability" survive into the submittable CV.

`verify_cards.py` names the right path. It still fails the constraint:

```
lines matching the parser ('- ❌' / '❌' at line start):
   real 06_do_not_claim.md   ->  0
   docs/CV_AI_MODULE.md      ->  6
```

The real file states its forbidden claims in a **markdown table** (`| ❌ NEVER CLAIM |`). The
parser matches only lines *beginning* with `❌`. Measured directly:

```
hardcoded fallback patterns:      7
total after "loading" real file: 11
extracted from the real file:     4   <-- all four came from docs/CV_AI_MODULE.md
```

**Zero patterns come from the real file.** The gate passes on a hardcoded fallback plus an in-repo
document — the paraphrase the brief forbade.

Two aggravating details: the loader falls back **silently** if the file is missing, and wraps the
parse in `except Exception: pass`. So a moved file, a renamed file, or a reformatted table all
degrade to "gate still green."

**Consequence:** if a new forbidden claim is added to the real file, the trainer will never see it,
and nothing will say so.

This finding is also a clean instance of the pattern from this session: **reading the code suggests
it works; running it shows it extracts nothing.** I found it only by executing the loader and
diffing against the hardcoded set.

## 8. HIGH — the most-cited source is our own session log

| source | refs |
|---|---|
| **`docs/SESSION_LOG_2026-08.md`** | **24** |
| `docs/writeup_attention_frame_bug.md` | 12 |
| `backend/neural_vision.py` | 12 |
| `arxiv.org/abs/1807.01613` | 10 |

125 source references total; 45 external, 80 repo files. **18 of 60 cards have no external source
at all.**

A session log is a record of our own prior conversation. Citing it as authority for CRPS,
calibration or dispersion modelling is the "own prior output laundered into evidence" failure, one
level up — the trainer would teach him from our conversation while presenting it as sourced.

Cards where the *only* sources are a session log and a non-existent DOI are not sourced in any
meaningful sense.

---

## 9. What I could not check, and the one thing most likely still wrong

*(Required field. The honest prediction, not a safe disclaimer.)*

I verified 18 external URLs by resolution, 5 cards deeply, and the three binding constraints. I did
**not** trace all 60 cards to their cited text, and I did not run the app in a browser or exercise
the comment box end to end.

**If exactly one thing in this delivery is still wrong, I predict it is a factual claim inside an
`air-quality` level-3 or level-4 card** — because that ladder has the weakest sourcing (session log
plus a fabricated DOI), it is the domain furthest from anything in this repository, and it is the
one area where I have the least independent knowledge to notice an error by reading. That is the
opposite of where I would instinctively look, which is why it is written down.

## 10. Required before this trainer is used

1. **Remove `10.5194/gmd-12-4857-2019` everywhere.** Replace with `10.5194/gmd-12-3357-2019`
   (Karl et al.) *only where the claim is actually supported by that paper* — not as a blanket
   substitution.
2. **Re-source the `air-quality` ladder.** Every card needs a real external source. The study room
   in `job_search` is the intended material and is now readable.
3. **Fix `load_do_not_claim_patterns`:** parse the table form (`| ❌ …`), **fail loudly** if the
   real file is unreadable rather than falling back, and drop `except Exception: pass`.
4. **Demote the session log.** It may corroborate; it may not be a card's only source.
5. **Re-verify every external citation by resolution** — the 18 present, and any added.
