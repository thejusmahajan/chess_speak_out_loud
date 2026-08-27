# NOW — where the project stands

**Last updated:** 2026-08-27 by the leader (Opus 5)
**Update this file at the end of every session.** If it is stale, the next restart pays for it.

---

## ⚑ 1. Deadline items

| item | due | status |
|---|---|---|
| **AEON-UP application (Hereon, ref. 1056)** | **2026-09-03** (7 days) | **UNCONFIRMED — ask Thejus first thing** |

**Why UNCONFIRMED and not a status:** three sources disagree. `agents/ACTIVE.md` says NOT SENT.
The leader's auto-memory note from 2026-08-26 says materials are FINAL and "sending today". The
submission bundle exists on disk and is under version control —
`job_search/applications/hereon_aeon_up/Mahajan_CoverLetter_CV_1056.pdf` and
`Mahajan_Additional_Documents_1056.pdf`, repo clean at `aeeb6c9` on branch `master`. **None of
that is evidence of submission.** Asked on 2026-08-27; not yet answered.

**Rules while this row is not SENT:**
1. Its status is stated at the start of the session, before anything else.
2. At most **one** non-deadline brief may be ACTIVE.
3. Every new brief carries a one-line *"why this before the deadline item?"*
4. **No new meta-process documents.** (`COMMAND_BASE.md`: "infrastructure that postpones
   exposure" — a registry, a ledger, an audit protocol and three documents were all built
   while this item sat unsent.)

---

## 2. Open questions that only Thejus can answer

These block real work and have been open for days. Ask them; do not guess.

| # | question | blocks |
|---|---|---|
| Q1 | **Is the AEON-UP application actually sent?** | everything above |
| Q2 | **ICON-O/HAMOCC** — three blog posts claim first-person postdoc experience with it; the CV mentions it **zero** times. True and missing from the CV, or overstated and it comes off the site? | a live honesty risk on a public site during a job search |
| Q3 | **NIT Calicut M.Sc. end date** — live site says `2012 – 2015`, `cv_hereon_aeon_up.tex` says `07/2012 - 12/2014`. Which is right? (Completion and convocation commonly differ.) | site/CV consistency under interview questioning |
| Q4 | **Do the trainer equations render?** Open `http://127.0.0.1:8010`, reveal an `uncertainty` card, confirm typeset maths and not raw `$$`. KaTeX was audited ACCEPT but **nobody has ever seen the output.** | closing the trainer |
| Q5 | **Flag any German that is correct but not idiomatic**, via the comment box category *"I think this is wrong"*. Invisible to every automated gate and to the leader. | German B2 ladder quality |

---

## 3. Next three actions, in order

1. **Answer Q1.** If not sent: send it. Nothing below outranks this.
2. **Close the LLM seam** — see §4. Brief is written and registered:
   `agents/briefs/2026-08-27_llm-seam-removal.md`. Hand the path to Gemini in Antigravity.
3. **Answer Q4** (two minutes in a browser) — it closes the trainer track, which is otherwise
   finished and unverified.

Everything else stays QUEUED under the WIP limit.

---

## 4. The live defect: the LLM is reasoning about chess

**Status: CONFIRMED, unfixed, and worse than previously recorded.** This is a direct violation
of the north star, in shipped code.

- `backend/app.py:658` calls `explanations.enrich_tree_explanations(tree)` **unconditionally**
  on the repertoire-tree endpoint.
- `backend/training/explanations.py` has **no `LLM_ENABLED` guard anywhere** and reaches
  `llm_client.generate_move_explanation` at line 63.
- The context handed over (`explanations.py:44-62`) is FEN, move UCI, `eval_cp`,
  `critical_reason`, `user_blind_rate`, opponent replies. **No LC0 search tree, no policy
  prior, no relational facts.** The model is asked to coach from a position and a number.
- Three documents assert this path is dormant: `backend/app.py:42`, `ARCHITECTURE.md:30`,
  `HOW_TO_RUN.md:90`. `LLM_ENABLED = False` is a sign, not an interlock.

**New, found 2026-08-27 — it has already produced output and cached it.**
`data/training/cache/explanations.jsonl`, 16 entries, written 2026-07-26 19:37:

```
"Nf3 is the critical repertoire move here because you have historically been blind here
 100% of the time. Focus on maintaining sound piece activity and watch out for opponent
 counter-play."
```

That second sentence appears **verbatim on four different positions** with different pieces on
the board. It comes from `_build_fallback_explanation`, which fires when `GEMINI_API_KEY` is
unset (`llm_client.py:214-216`). So the served text is not merely ungrounded — it is
position-independent filler. Other entries are truncated mid-word ("Developing your knight to
f"). `llm_client.py` also targets model id `gemini-3.5-flash`, which is not a real model.

**The audit's open question — "does it fire in production?" — is now answered: yes, and the
evidence is on disk.**

---

## 5. Repo sync

| repo | branch | state at 2026-08-27 session close |
|---|---|---|
| `chess_speak_out_loud` | `windows-dev` | see `state/JOURNAL.md` latest entry |
| `job_search` | `master` | clean at `aeeb6c9` |
| `thejusmahajan.github.io` | `main` | published 2026-08-22 (`c09496c`, `ac70a00`), verified live |

**GitHub's `main` on the chess repo is STALE by design.** The whole project is on `windows-dev`.

At the start of this session the chess repo was **35 commits ahead of origin and never pushed**,
with 11 uncommitted paths. That is the same failure that left the website repoint sitting
uncommitted for three days after being audited ACCEPT. **Check the push state every session.**

---

## 6. Where the tracks stand

**Chess / north star.** The extractor is built and audited (`backend/training/relational_facts.py`
— tactical, positional, plan-level). The frontier is **SALIENCE**: it emits many true facts and
only a few are the objective. The GM-annotation route measured **19 salient labels out of 2,284
facts, and 0 of 35 on the gold Capablanca tier** — the earlier "pilot validated the method" claim
was never measured and is false. Current plan: `PLAN_SALIENCE_CNP.md` (condition on the tiny gold
set rather than train on it; abstention is the motto in code). **Never hand-code salience.**

**Trainer.** Delivered and audited. 171 cards across 10 ladders (ML, German B2, plus
`hereon-aeon-up` and `bridge`), 84/84 external URLs resolving, repetition fixed, per-ladder
ratings. Open only on Q4 and Q5 above. *Standing lesson: three times, correct content was
authored and left unreachable — every trainer brief must gate on a 400-draw distribution.*

**Job search.** Materials are excellent; **throughput is the problem** — 8 of 11 applications
never left "Draft prepared". AEON-UP is the best fit found. After it ships, the bottleneck to
attack is volume, not quality.

**Queued, blocked on the WIP limit:** `2026-08-19_attention-demo-page` (blocked on the
regenerated export), `2026-08-19_attention-export-with-history`, `2026-08-18_cnp-synthetic-build`.
