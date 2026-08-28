# NOW — where the project stands

**Last updated:** 2026-08-29 by the leader (Opus 5)
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

**⚠ THE STUDY ROOM MOVED 2026-08-28. The canonical path is now:**
`C:\Users\Admin\Documents\bioinformatics_project\job_search\applications\hereon_aeon_up\study_room\`
— see §5. **`Documents\job_search` is RETIRED**; an edit made there is invisible to GitHub.

**18 files.** H1–H5 are all now written; **the deck is BUILT** (`../talk/aeon_up_talk.pdf`).
**Nothing here is rehearsed.** The remaining work is his voice, out loud, with a timer — not more
documents. *The problem was always priority, not volume; do not add more reading.*

**⚑ H1–H5 are now DRILLABLE, 2026-08-28.** The `hereon-aeon-up` ladder in the trainer went
**17 → 51 cards**. The old 17 were written 2026-08-22 and stopped at "the pitch"; the five holes
were written 27–28 August and had **zero** coverage. Now: L2 the four UFP facts, L3 the UFP bridge
and the CNP numbers, **L4 fourteen cards** on the publication gap / TVöD / facing Karl / the panel
questions, L5 nine on delivering the talk. `verify_cards.py` passes at 205 cards and was
mutation-checked — an injected "hands-on experience with EPISODE-CityChem" turns it red.
*This is recall drill, not more reading; it does not substitute for saying the talk aloud against
a clock.* Levels are capped 0–5 by the schema, so the new material sits inside the existing bands.

**⛑ THE LADDER WAS UNREACHABLE UNTIL 2026-08-29.** The app could serve **5 of the 51 cards**.
Level gating pinned the ladder to Level 0, and cram mode still applied `is_card_unlocked`, whose
chains run five deep — so the L4 publication-gap cards and the L5 talk cards could not be reached
by any route. Fixed and **AUDITED ACCEPT** (`agents/reports/2026-08-28_trainer-interview-mode_AUDIT.md`):
every gate re-run by the leader, both guards mutation-checked, 15 live API calls returning L3–L5
material. *The instrument now works. It has still never been drilled — 5 of 51 cards seen, last
real session 2026-08-22.*

**The external-facts research came back PARTIALLY, 2026-08-29** — two Deep Research PDFs in
`applications/hereon_aeon_up/research/`, against `agents/briefs/2026-08-28_aeon-up-external-facts.md`.

| target | outcome |
|---|---|
| **R1** Karl's UFP paper | **RESOLVED by the leader** (the report missed it). Lauenburg, M.; **Karl, M.**; Matthias, V.; Quante, M.; **Ramacher, M.O.P.**, *"City Scale Modeling of Ultrafine Particles in Urban Areas with Special Focus on Passenger Ferryboat Emission Impact"*, **Toxics 10(1), 3**, doi:10.3390/toxics10010003. **Karl is second author, Ramacher last.** The ⚠ on H5 is lifted — but call it *the ferryboat paper*, never "your paper". |
| **R2** TVöD | **DROPPED by Thejus**, 2026-08-29. Do not re-open it. |
| **R3** PI publications | **One claim was FALSE.** The report announced Karl now has an ML record; its cited source is a Copernicus *related-articles* page, and the quoted sentence belongs to Vartiainen et al. (AMT). **Karl has no ML record.** The true finding is the mirror: **Ramacher first-authored EGU25-9157**, *"Machine Learning Downscaling of CAMS Regional Air Quality Reanalyses"*, with Paul Keil — AEON-UP's problem statement, by one of its PIs. Cards corrected. |
| **R4** AEON-UP as an entity | **LEADS ONLY, not facts.** Oct 2026–Sep 2028; partners Helmholtz Munich (Bayesian DL / neural processes) and RIFS Potsdam; benchmarks vs XGBoost and Gaussian Processes. All from job-board mirrors; jobtensor 403'd the leader. **Do not state as known.** The acronym expansion is unknown — do not guess it. |
| **R5** interview format | **NEVER CAME BACK.** Panel composition and whether a presentation is standard are still unsourced, and `14_talk_script.md` assumes both. **Ask the panel by email.** |
| **R6** the landscape | **Not card material.** Five of eight rows carry "Title Unavailable" or an UNVERIFIED DOI. One solid takeaway: leave-one-station-out reads as rigorous, not eccentric — supports `her-l3-008`. |
| **R7** UFP regulation | **CONFIRMED and sharpened by the leader.** Directive **(EU) 2024/2881**, adopted 23 Oct 2024, in force since Dec 2024, transposition due **Dec 2026 — inside the project period**. UFP mandatory at supersites with black carbon and ammonia, **no numerical limit value**, ≥1 supersite per 5 million inhabitants. |

**New lead worth a question: ACT-AQ**, a Helmholtz Forum consortium formed in response to the
revised AAQD — kickoff 8–9 July 2026 in Hamburg, **Ramacher a PI**, partners including Helmholtz
Munich and RIFS, the same two AEON-UP partners.

**Cards not yet written:** the ferryboat citation, the Ramacher EGU abstract (as a question *to*
him, never a claim *about* him), and ACT-AQ.

| # | hole | why it matters |
|---|---|---|
| ~~**H1**~~ | **DRAFTED 2026-08-27 — `study_room/05_interview_questions.md`, Band G, Question 20.** The gap had zero coverage in 3,400 lines; Q15 answers *"no **ML** publications"*, a different question whose answer **invites** this one. Q20 gives the arithmetic (3.5 years on paper − 12 months parental leave − a change of field ⇒ ~2.5 years of research), what exists (Lagrangian IBM, GOTM-FABM, the Fortran/OpenMP→JAX port, manuscript in final preparation), and the strongest fact: **six months back at Hereon as a guest scientist, unpaid, to finish the framework.** The lesson is *publish incrementally* — the JAX port was a model-description paper he did not split out. The **follow-ups** are prepared too, since that is where it fails. **Hard rules: never criticise a former supervisor; never invent a submission date.** ⚠ **Still needs him:** confirm the manuscript is genuinely still in final preparation, and that the JAX port really was publishable standalone — the reflection only works if it is his. **REHEARSE ALOUD; it is drafted, not rehearsed.** |
| ~~**H2**~~ | **SCRIPTED 2026-08-27 — `study_room/14_talk_script.md`.** Thirteen slides + seven backups, ~14:00, with a marked 10-minute cut. Thesis: *“I build environmental models, I have moved into machine learning, and what I am actually good at is finding the errors that do not announce themselves.”* Centrepiece is slide 7 — the two silent bugs, with the mirrored/corrected attention figures side by side and the admission that one was already published. Slide 9 is the CNP evidence; slide 11 volunteers what he does not know, which is what makes the rest credible. **Deck build delegated:** `agents/briefs/2026-08-27_aeon-up-talk-deck.md` (content copied verbatim; Gemini does LaTeX only). ⚠ **Ask the panel the format first** — length and emphasis — and rehearse aloud with a timer standing up. |
| ~~**H3**~~ | **WRITTEN 2026-08-28 — `study_room/17_salary_and_conditions.md`.** The reframe: **TVöD E13 is not negotiable; the *Stufe* within it is**, and that is the entire conversation. **No figures are quoted anywhere** — he checks the current TVöD Bund table himself, in advance. ⚠ **The €75,000 expectation probably needs recalibrating before the interview**, not during it. Step case tabulated from the CV; two things to ask HR rather than assert (how the 65% Teilzeit counts, whether the unpaid Hereon guest period counts). Flags the missing **Arbeitszeugnis** from Universität Hamburg — step assignment runs on documents, and that is the one major CV entry with none. |
| ~~**H4**~~ | **WRITTEN 2026-08-28 — `study_room/16_questions_for_the_panel.md`.** Eight to choose from, **bring four on paper**, at least one addressed to **Karl by name** — that is the correction for the letter engaging only Ramacher. Strongest is *"where do you expect EPISODE-CityChem to be weakest?"* — it invites the model's author to discuss his own model's limits and frames the ML as serving the physics. Includes what **not** to ask (salary first, permanency, anything answerable from the advert, a disguised statement about himself). |
| ~~**H5**~~ | **WRITTEN 2026-08-28 — `study_room/15_karl_and_ufp.md`.** ⚑ **Contains the argument the cover letter should have made.** UFP has **no binding limit value** (revised AAQD 2024 mandates monitoring only) and almost **no monitoring** — so an AEON-UP model produces exposure estimates *nobody can check*, which is exactly where a confidently wrong model does real damage. That makes UFP the strongest possible case for his own uncertainty thesis. **The honest technical bridge:** the CNP's Task B — smooth regional background **plus a sharp road ridge**, leave-one-station-out — is the UFP geometry exactly. He must say unprompted that it is synthetic and has no microphysics. Also: coagulation is second-order in N, so **UFP is not a passive tracer** — raise that limitation on his own approach before Karl does. ⚠ **Verify the exact title of Karl's UFP paper before naming it to its author.** |
| **H6** | **"Batched GPU inference"** on the CV, and **"GPU/TPU execution"** — confirm the TPU claim is real, or be ready to drop it verbally. | **Handled in the deck** (it says GPU only) but **not** on the submitted CV. Still open. |

**Q2 and Q3 are CLOSED on the website — they were fixed on 2026-08-22 and this file was stale
for five days.** Commit `eb8ecdc` ("Remove unverified specifics from the blog; align M.Sc. date
with the CV") removed **five** names that appeared in first-person experience claims while
appearing in the CV zero times — **ICON-O, HAMOCC, EERIE, Levante, DKRZ** — across four pages,
and set the M.Sc. to `2012 – 2014`. Pushed; `origin/main` is level.

- **Q2 — HAMOCC. CLOSED and SHIPPED.** The one residual — `hamocc_plankton_output.csv` inside a
  code block in `blog-ggplot2-timeseries.html` — is gone, pushed as `909237a`.
  *Lesson: a scrub of prose is not a scrub of the page — grep the code blocks too.*
- **Q3 — dates.** Settled and consistent: site `2012 – 2014` / CV `07/2012 - 12/2014` for the
  M.Sc., site `2009 – 2012` / CV `06/2009 - 04/2012` for the B.Sc. **Nothing to decide.**
- **LinkedIn: AUDITED 2026-08-27** (leader; brief `…_public-surface-honesty-sweep.md` is DELIVERED,
  AUDITED, ACCEPTED). **The five names are NOT on LinkedIn — nothing to remove for honesty.** What
  the audit found is a profile that stops in Oct 2025: **L1** CQ shown as *Present* though it ended
  02/2026, **L5** PhD field given as *Astrophysics* not Astrochemistry, plus the B.Sc., the
  HealthTwiSt Praxisphase and the current LC0 work all missing, no ML in the headline, and **L13**
  a Languages section that contradicts the CV in four of six entries (German claims *professional
  working proficiency* against a B1 certificate). Twelve items, L1–L13, in
  `agents/reports/2026-08-27_public-surface-honesty-sweep_AUDIT.md`.
  **Headline and About drafted** from the CV: `job_search\linkedin_rewrite_2026-08-27.md`.
  **LinkedIn is edited by hand, by him** — nothing here is automated.

**Decided 2026-08-27: no email to Kai Wirtz.** So H1 is answered from what is already in hand —
the manuscript status will not be chased.

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
| `chess_speak_out_loud` | `windows-dev` | pushed and verified at the 2026-08-28 close (6 commits: cards, brief, research package, launchers, ideas, trainer state) |
| `cnp_synthetic` | (own git) | **DIRTY — 5 modified + 1 untracked at `db3eb90`.** Commit them (§3) |
| `job_search` | `master` | **FIXED AND PUSHED 2026-08-28**, at `7619193`, `0 0` against `github.com/thejusmahajan/job_search` (private). **Canonical clone: `Documents\bioinformatics_project\job_search\`.** See the note below — this was not a missing remote but a fork. |
| `thejusmahajan.github.io` | `main` | published 2026-08-22 (`c09496c`, `ac70a00`), verified live |

**⚠ The `job_search` fork, and what it cost — worth remembering.** There were **two clones with
unrelated root commits**: `Documents\job_search` (2 commits, no remote, but holding the whole study
room) and `bioinformatics_project\job_search` (15 commits, the real remote, **no study room**). A
plain push would have been rejected; forcing it would have destroyed twelve commits of AEON-UP
history that the remote already had. Resolved by fast-forwarding to origin and laying the newer
files on top, after verifying the incoming copy was a superset and deleted nothing.

**A silent regression was caught doing it.** The orphan's `09_operational_script.md` still carried
**two fabricated citations that the remote had already corrected** in `9de009a` — Cabaneros (the
real paper is in *Environmental Modelling & Software* 119, not *Environmental Pollution* 254) and
Andersson (arXiv:**2211.10381**, not 2305.15340). Overlaying blindly would have reintroduced both.
Restored from the remote before committing. **Lesson: when reconciling two copies, diff the content,
never assume the copy with more files is newer in every line.**
`Documents\job_search\RETIRED_READ_THIS_FIRST.md` marks the dead copy; a full backup including its
`.git` is in the session scratchpad.

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
- ~~**Q4 — do the equations render?**~~ **CLOSED 2026-08-28** — Thejus confirmed directly:
  *"Equations are fine now."* KaTeX had been audited ACCEPT on 2026-08-20 with the honest caveat
  that Playwright 404'd and **nobody had ever seen the output**; a human has now seen it. That
  closes the third instance of the standing failure. *The lesson stands anyway: correct content
  authored and left unreachable happened three times, and only a person looking at the screen
  ever caught it.*
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
