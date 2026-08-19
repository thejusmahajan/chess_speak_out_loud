```
Brief-ID:       2026-08-19_trainer-content-repair
Written:        2026-08-19
Target repo:    chess_speak_out_loud
Route:          Antigravity (full workspace; job_search IS readable)
Type:           content repair + gate fix
Status:         ACTIVE
Depends on:     2026-08-19_knowledge-trainer-build (engine ACCEPTED — do not rewrite it)
Blast-radius:   external   (this teaches a person facts he will state in an interview)
Reversibility:  costly     (a wrong fact learned is expensive to unlearn)
Failure-mode:   SILENT     (a plausible wrong card looks exactly like a right one)
Why before the deadline item: the application is unsent and takes priority; this is queued behind
it, but the trainer must not be used until repaired — a fabricated citation drilled by spaced
repetition is worse than no trainer.
```

# Repair the trainer's content and its do-not-claim gate

## INTENT

A person will study these cards and repeat their contents to the two scientists who wrote the
source papers. **A card that is plausible and wrong is worse than no card**, because spaced
repetition will drill it in. The goal is not sixty cards; it is sixty cards each of which survives
being checked by the person who would know.

**If any instruction below conflicts with that intent, the intent wins — stop and report.**

## 1. What was accepted, and must not be rewritten

The engine passed audit: `engine.py`, `app.py`, `static/index.html`, `tests/test_engine.py`,
9 tests green, `verify_cards.py` mutation-tested twice and correctly exiting 1 on failure. **Leave
all of it alone** except the one function named in §3.

The `own_work`, `pytorch`, `uncertainty` and `neural_processes` ladders were spot-checked and are
broadly sound. Do not rewrite them wholesale; §4 applies to them.

## 2. CRITICAL — a fabricated citation, used five times

`https://doi.org/10.5194/gmd-12-4857-2019` **does not exist.** Verified 404 by two routes
(`doi.org`, and `gmd.copernicus.org/articles/12/4857/2019/`).

It appears on `aq-l2-002`, `aq-l3-001`, `aq-l3-002`, `aq-l4-001`, `aq-l5-001` — and is the only
external source on four of them.

The real paper is:

```derivation
$ curl -sIL https://doi.org/10.5194/gmd-12-3357-2019   # resolves
  -> https://gmd.copernicus.org/articles/12/3357/2019/
  "The Eulerian urban dispersion model EPISODE - Part 2: Extensions to the source dispersion
   and photochemistry for EPISODE-CityChem v1.2 and its application to the city of Hamburg"
   first author: Matthias Karl
```

**Matthias Karl is one of the two PIs for the job this trainer prepares him for.**

**Do NOT blanket-substitute `3357` for `4857`.** For each of the five cards, decide whether the
claim is actually supported by that paper. If yes, cite it. If not, find a real source or **delete
the card** and say so. A wrong citation replaced by a differently-wrong citation is not a fix.

## 3. CRITICAL — the do-not-claim gate enforces a paraphrase

`verify_cards.py :: load_do_not_claim_patterns` extracts **zero** patterns from the real file:

```derivation
$ python -c "lines starting with '- ❌' or '❌'"
  C:\Users\Admin\Documents\job_search\...\study_room\06_do_not_claim.md  ->  0
  docs\CV_AI_MODULE.md                                                   ->  6
$ python -c "from verify_cards import *; len(load_do_not_claim_patterns()) - len(FORBIDDEN_CLAIM_PATTERNS)"
  4     # all four sourced from docs/CV_AI_MODULE.md, none from the real file
```

The real file states its forbidden claims in a **markdown table** (`| ❌ NEVER CLAIM | … |`); the
parser matches only lines *beginning* with `❌`.

Required changes:
1. **Parse the table form** — extract the first cell of every row whose first cell contains `❌`.
2. **Fail loudly** if the real file is missing or unreadable: raise, exit non-zero, print the path.
   No silent fallback. A missing constraint file must stop the build, not degrade it.
3. **Delete `except Exception: pass`.** A parse failure must surface.
4. Keep `docs/CV_AI_MODULE.md` as an *additional* source, never a substitute.
5. **Prove it works**: print the number of patterns loaded from the real file, and assert it is
   `>= 5`. Paste that output.

## 4. HIGH — re-source, with the session log demoted

`docs/SESSION_LOG_2026-08.md` is currently the most-cited source in the trainer (24 of 125
references). It is a record of our own prior conversation, not an authority.

- **A session log may corroborate a card. It may never be a card's only source.**
- **18 of 60 cards currently have no external source at all.** Every card needs at least one source
  that is either an external publication or a repository *code/analysis* file — not a log, not a
  planning document, not a conversation transcript.
- The `air-quality` ladder needs the most work. **The intended material is now readable** at
  `C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\study_room\` (files `00`–`11`)
  and `STUDY_BOOK.md` in the same folder. Use it.

## 5. Verify every external citation by resolution

There are 18 external URLs in the content. **Resolve every one** and confirm the title matches the
claim it supports. Report a table: URL → resolved title → the card that cites it → OK / WRONG /
DEAD.

A DOI that redirects to a paywall (403) still counts as resolving. A 404 does not.

**Add this as a gate**, not a one-off: `verify_cards.py --check-urls` that resolves every external
source and fails on any that 404s. Network-dependent, so keep it a separate flag from the default
run.

## 6. Gate — paste REAL output

```
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer/verify_cards.py
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer/verify_cards.py --check-urls
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
git status
```

Plus:
- the count of do-not-claim patterns loaded **from the real file** (must be ≥ 5);
- the citation table from §5;
- a list of any card you **deleted** for lack of a real source — this list is a success, not an
  embarrassment;
- the exit code of `verify_cards.py` when you temporarily point a card at a dead URL (must be
  non-zero), then restore.

## 7. Your report

`agents/reports/2026-08-19_trainer-content-repair_REPORT.md`. Include every gate result, the
citation table, deleted cards, anything this brief got wrong, and — required —

> **"If exactly one thing in this delivery is still wrong, what is it most likely to be, and did
> I check it?"**

Answer that specifically. "I could not test the browser" is not an answer to it.
