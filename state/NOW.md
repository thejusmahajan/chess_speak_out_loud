# NOW — where the project stands

**Last updated:** 2026-08-27 by the leader (Opus 5)
**Update this file at the end of every session.** If it is stale, the next restart pays for it.

---

## ⚑ 1. The live item: the AEON-UP INTERVIEW

**The application was SENT.** Confirmed by Thejus on 2026-08-27. Q1 is closed; the 3 September
deadline no longer governs anything. Do not re-open it, do not re-audit the PDFs, do not
re-litigate the cover letter. Those are decided and out of his hands.

**Priority order, stated at the start of every session:**

| # | track | status |
|---|---|---|
| **1** | **AEON-UP interview preparation** | **TOP PRIORITY — everything below yields to it** |
| 2 | Other applications: throughput, logging, reminders | the real bottleneck (8 of 11 never left "Draft prepared") |
| 3 | The two apps — LC0 chess analysis/play, and the spaced-repetition trainer | portfolio *and* the interview's engineering evidence |
| 4 | CNP (`cnp_synthetic`) | BUILT; it exists **for this application** — close the loose ends, then it is CV/interview material |

**Rules while the interview is the live item:**
1. Its status is stated at the start of the session, before anything else.
2. At most **one** non-interview brief may be ACTIVE.
3. Every new brief carries a one-line *"why this before the interview?"*
4. **No new meta-process documents.** (`COMMAND_BASE.md`: "infrastructure that postpones
   exposure". A registry, a ledger, an audit protocol and three documents were all built while
   the application sat unsent.)

---

## 2. Interview preparation — what is actually missing

Study room: `C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\study_room\`
(14 files, ~3,400 lines). **Coverage is broad; the holes are specific and were measured by grep
on 2026-08-26.** The problem is priority, not volume — do not add more reading.

| # | hole | why it matters |
|---|---|---|
| **H1** | **The publication gap has ZERO coverage.** The CV lists five publications, all 2018–2020 astrochemistry, and nothing from the 2021–2025 marine post-doc. Nothing anywhere prepares an answer. | A hiring PI checks output first. A four-year post-doc with no listed publication reads as failure rather than as timing. **This is the single most likely hard question.** **Decided 2026-08-27: Wirtz will NOT be emailed** — so the answer is built from what is already in hand (the CV's "manuscript in preparation" line, the Hereon guest stay that "prepared the simulation data for peer-reviewed publication", and the modelling actually done), not from a chased-down journal name. |
| **H2** | **No talk artefact.** No slides, no 10–15 min presentation anywhere. | Helmholtz interviews usually ask for one, often at short notice. |
| **H3** | **Salary / TVöD E13.** Appears only inside the doc that was found fabricated. His stated expectation is €75,000; AEON-UP is E13. | It will be asked, and an unconsidered answer is expensive. |
| **H4** | **Questions for the panel** barely exist — named in files 00 and 08, with no content. | The closing question of nearly every interview. |
| **H5** | **Karl's side is unaddressed.** The letter is addressed to both PIs but engages only Ramacher's Code4Earth work. **Ultrafine particles** — Karl's specific area, named in the advert — appear nowhere in it. | Half the panel was not written to. Prepare that half in the room instead. |
| **H6** | **"Batched GPU inference"** on the CV, and **"GPU/TPU execution"** — confirm the TPU claim is real, or be ready to drop it verbally. | Both are on the submitted CV; a probe on either is fair game. |

**Q2 and Q3 are CLOSED on the website — they were fixed on 2026-08-22 and this file was stale
for five days.** Commit `eb8ecdc` ("Remove unverified specifics from the blog; align M.Sc. date
with the CV") removed **five** names that appeared in first-person experience claims while
appearing in the CV zero times — **ICON-O, HAMOCC, EERIE, Levante, DKRZ** — across four pages,
and set the M.Sc. to `2012 – 2014`. Pushed; `origin/main` is level.

- **Q2 — HAMOCC.** Prose is clean. **One residual survived, in a code block, not prose:**
  `blog-ggplot2-timeseries.html:83` still loads `hamocc_plankton_output.csv`. One-line fix, in the
  brief below. *Lesson: a scrub of prose is not a scrub of the page — grep the code blocks too.*
- **Q3 — dates.** Settled and consistent: site `2012 – 2014` / CV `07/2012 - 12/2014` for the
  M.Sc., site `2009 – 2012` / CV `06/2009 - 04/2012` for the B.Sc. **Nothing to decide.**
- **⚠ LinkedIn has never been checked** and is the one public surface still unaudited. The same
  five names may sit on the profile. Thejus must paste his profile text into
  `job_search\linkedin_profile.txt` before anyone can audit it; **LinkedIn is edited by hand, by
  him.**

Working both of these: `agents/briefs/2026-08-27_public-surface-honesty-sweep.md` (ACTIVE).

**Decided 2026-08-27: no email to Kai Wirtz.** So H1 is answered from what is already in hand —
the manuscript status will not be chased. Prepare the publication-gap answer without it.

**The strongest asset, and it must be defended cold — see §3.**

---

## 3. The CNP is BUILT (this corrects the record)

`C:\Users\Admin\Documents\cnp_synthetic`, commit **`063bc6e` "feat: CNP on synthetic data, with
an honest uncertainty evaluation"**. Earlier notes — including the leader's own memory, dated
2026-08-26 — assert "the CNP was NEVER built". **That is stale. It exists**, with code
(`cnp/`, `train_1d.py`, `train_city.py`), `tests/`, five `runs/*.log`, four figures, `RESULTS.md`
and a `REFEREE_REPORT.md`.

This matters because the submitted cover letter says neural processes are *"current areas of
learning and **implementation**"*. That word now has something behind it. **It converts the
thinnest claim in the application into the strongest.**

Numbers a panel could ask for, all from `RESULTS.md`, all traceable to `runs/` (Task A, 1-D GP,
16000 steps / 639.5 s, 512 held-out tasks, eval seed 20260818):

| model | NLL | CRPS | ECE | mean sigma |
|---|---|---|---|---|
| cnp | 0.1532 | 0.1677 | 0.0214 | 0.2865 |
| gp_oracle | −1.8676 | 0.0379 | 0.0040 | 0.0716 |
| climatology | 1.1223 | 0.4442 | 0.0527 | 0.7387 |

The defensible story, if he can hold it in his own words: the CNP is **4.42× worse on CRPS than
the exact GP posterior, and that is the correct outcome** — beating the oracle would have meant a
context/target leak. Against climatology it wins on all four columns: **sharper *and* better
calibrated**, which is the pair that matters, since either alone is trivial. NLL flatters the CNP,
because NLL is its training objective and not the baselines'.

**Loose ends, small, worth closing before it is quoted in an interview:**
- The repo has **uncommitted changes** (`RESULTS.md`, `WORKER_REPORT.md`, `cnp_colab.ipynb`,
  `runs/pytest.log`, `tests/test_model.py`) and an **untracked `REFEREE_REPORT.md`**. Commit them
  — an unclean repo is a bad thing to screen-share.
- **The CV's Machine Learning skills line still contains nothing probabilistic.** The CNP is the
  highest-value addition to it. The submitted PDF is frozen, but every *future* application takes
  the improved line.

---

## 4. Track 2 — the other applications

**Throughput is the problem, not quality.** 8 of 11 applications never left "Draft prepared". The
materials are excellent; the pipeline is not. After the interview, this is where the effort goes.

He has asked for **application logging and reminders** — a running record of what went out, when,
to whom, and what is due back. Keep it as *one* tracked artefact in `job_search`, not a new
process framework here; see the no-new-meta-documents rule in §1.

Boards, not search results: HIDA board + Helmholtz Job Letter. Hereon was the warm lead.

---

## 5. Repo sync

| repo | branch | state at 2026-08-27 session close |
|---|---|---|
| `chess_speak_out_loud` | `windows-dev` | pushed and verified; see the session-close block in `CLAUDE.md` |
| `cnp_synthetic` | (own git) | **DIRTY — 5 modified + 1 untracked at `db3eb90`.** Commit them (§3) |
| `job_search` | `master` | clean at `aeeb6c9`. Real working copy: `Documents\bioinformatics_project\job_search\`; the `Documents\job_search` folder holds the hereon working dir + `study_room` |
| `thejusmahajan.github.io` | `main` | published 2026-08-22 (`c09496c`, `ac70a00`), verified live |

**GitHub's `main` on the chess repo is STALE by design.** The whole project is on `windows-dev`.

At the start of the 2026-08-27 session the chess repo was **35 commits ahead of origin and never
pushed**, with 11 uncommitted paths — the same failure that left the website repoint uncommitted
for three days after being audited ACCEPT. **Check the push state every session.**

**One deliberate exception, left untracked:** `applications/hereon_aeon_up/other_documents/
registration_confirmation_hlrs_email.pdf` sits in *this* repo but belongs in `job_search`, which
already holds `certificates/HLRS_Registration_Confirmation.pdf`. Not committed here and not
deleted — Thejus should move or drop it.

---

## 6. The live defect in the chess app: the LLM is reasoning about chess

**Status: CONFIRMED, unfixed.** A direct violation of the north star, in shipped code. The brief
is written and registered — `agents/briefs/2026-08-27_llm-seam-removal.md` — and it is the one
non-interview brief allowed ACTIVE under §1. *Why this before the interview: the chess app is
interview evidence, and this is a coach that talks without knowing anything.*

- `backend/app.py:658` calls `explanations.enrich_tree_explanations(tree)` **unconditionally** on
  the repertoire-tree endpoint.
- `backend/training/explanations.py` has **no `LLM_ENABLED` guard anywhere** and reaches
  `llm_client.generate_move_explanation` at line 63.
- The context handed over (`explanations.py:44-62`) is FEN, move UCI, `eval_cp`, `critical_reason`,
  `user_blind_rate`, opponent replies. **No LC0 search tree, no policy prior, no relational facts.**
- Three documents assert the path is dormant (`backend/app.py:42`, `ARCHITECTURE.md:30`,
  `HOW_TO_RUN.md:90`). `LLM_ENABLED = False` is a sign, not an interlock.

**It has already fired and cached its output.** `data/training/cache/explanations.jsonl`, 16
entries, 2026-07-26 19:37. *"Focus on maintaining sound piece activity and watch out for opponent
counter-play"* appears **verbatim on four different positions**. It comes from
`_build_fallback_explanation` (`llm_client.py:214-216`), which fires when `GEMINI_API_KEY` is
unset — so the served text is position-**independent** filler. Other entries truncate mid-word.
`llm_client.py` targets model id `gemini-3.5-flash`, which is not a real model.

---

## 7. Where the tracks stand

**The two apps.** (1) **LC0 chess analysis and play** — this repo. (2) **The spaced-repetition
trainer** — delivered and audited: 171 cards across 10 ladders (ML, German B2, plus `hereon-aeon-up`
and `bridge`), 84/84 external URLs resolving, repetition fixed, per-ladder ratings. Note the
`hereon-aeon-up` ladder *is* interview preparation, which puts the trainer on the critical path.

Two trainer questions still need a human, and both are minutes of work:
- **Q4 — do the equations render?** Open `http://127.0.0.1:8010`, reveal an `uncertainty` card,
  confirm typeset maths and not raw `$$`. KaTeX was audited ACCEPT but **nobody has ever seen the
  output.** *Standing lesson: three times, correct content was authored and left unreachable —
  every trainer brief must gate on a 400-draw distribution.*
- **Q5 — flag German that is correct but not idiomatic**, via the comment box category
  *"I think this is wrong"*. Invisible to every automated gate and to the leader.

**Chess / north star.** The extractor is built and audited (`backend/training/relational_facts.py`
— tactical, positional, plan-level). The frontier is **SALIENCE**: it emits many true facts and
only a few are the objective. The GM-annotation route measured **19 salient labels out of 2,284
facts, and 0 of 35 on the gold Capablanca tier** — the earlier "pilot validated the method" claim
was never measured and is false. Current plan: `PLAN_SALIENCE_CNP.md` (condition on the tiny gold
set rather than train on it; abstention is the motto in code). **Never hand-code salience.**

**Queued, blocked on the WIP limit:** `2026-08-19_attention-demo-page` (blocked on the regenerated
export), `2026-08-19_attention-export-with-history`, `2026-08-18_cnp-synthetic-build` (now
superseded — the build landed; close it).
