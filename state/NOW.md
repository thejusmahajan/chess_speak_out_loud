# NOW — where the project stands

**Last updated:** 2026-09-03 by the leader (Opus 5) — **§9: Φ IS TRAINED, F1 FAILED at 0.6908**; §10 profile regeneration (think-time filter decided); §11 leadership corpus.
**Update this file at the end of every session.** If it is stale, the next restart pays for it.

---

## ⛔ 0. THIS REPOSITORY STAYS PUBLIC — so the career material has to leave it

**⚑ DECIDED BY THEJUS, 2026-08-29 (evening):** *"I keep the chess repo public and we will remove
all the other stuff from it as it is not part of chess repo."* **This reverses the standing
"set it private" instruction that headed this section all day.** Do not re-open it; the task is now
subtraction, not a visibility flip.

**Also decided the same evening:** *"Don't worry about the other applications. Only this hereon is
active as others were rejected."* The other ten are closed. `APPLICATION_LOG.md` still shows 4
Submitted and 7 "Draft prepared" — that log is now a historical record, not a work queue.

**Why it matters more than the signature scare that started this.** Publicly readable right now:
`trainer/content/ladders/hereon_aeon_up.json` (51 interview cards, **Karl named 22 times**,
including how to talk about his model and why the strongest question works on him);
`state/NOW.md` and `state/JOURNAL.md` (the publication-gap arithmetic, parental-leave dates,
salary framing, *"8 of 11 applications never left Draft prepared"*); the two `*honesty*` audit
reports; `CLAUDE.md` (permit expiry); `docs/career_strategy_conversation_aug2026.md`;
`trainer/state/answers.jsonl` (131 graded answers). Karl and Ramacher are findable people who
search their own model's name.

**⛔ Removing files in a new commit does not undo any of that — the history keeps them.** With the
repo staying public, **deleting the files changes nothing about what is already readable.** Anyone
can `git log` back to August and read all of it. This is the single most important fact on this
page and it must not be softened.

### The exposure, measured 2026-08-29

| fact | value |
|---|---|
| repo created | 2026-07-15; **300 commits** |
| `docs/career_strategy_conversation_aug2026.md` first appears | **2026-08-15** |
| `trainer/`, `agents/`, `discussions/` first appear | **2026-08-19** |
| `state/` first appears | **2026-08-27** |
| commits since 2026-08-15 (i.e. the rewrite blast radius) | **75 of 300** |
| stars / forks / watchers / subscribers | **0 / 0 / 0 / 0** |

**Everything before 2026-08-15 is pure chess.** The career material is confined to the last two
weeks of a six-week repository, in cleanly separable directories, and **nobody is watching it** —
no forks, no stars, no subscribers. That is about as good a position as this could be in.

**The full career footprint in the public tree** is wider than this section listed all day. Beyond
`agents/` (31 files), `trainer/` (112) and `state/`, it also includes **`research/aeon_up/`** — 11
files including `2_salary_and_conditions.md` and `1_karl_and_ufp.md` — plus `discussions/` (4),
`archive/superseded_tasks/` (3 AEON-UP worker tasks), `docs/SESSION_LOG_2026-08.md`,
`docs/leadership/COMMAND_BASE.md`, `docs/CV_AI_MODULE.md`, and `CLAUDE.md` itself, which carries the
permit expiry and the who-is-who.

### ⚑ The decision that is still open, and it is Thejus's

Deleting the files is easy. Making them *unreadable* means rewriting history and force-pushing.
Given 0 forks and 0 stars, a force-push breaks nobody, and 225 of 300 commits are untouched. The
residual is that GitHub keeps unreferenced commits reachable by SHA until it garbage-collects, so
the thorough version ends with a request to GitHub Support to purge cached views.

**⚠ A premise the leader had wrong and checked:** the submitted hereon CV does **not** link to
`github.com/thejusmahajan/chess_speak_out_loud`. It links the GitHub *profile*, the website, the
blog post, and `hepatitis-delta-pipeline`. So preserving this exact repository URL is **not**
load-bearing for the live application — which widens the options rather than narrowing them.

**So the question to answer before any `git mv`: delete-only, or delete plus history rewrite?**
Everything else in the separation plan (§0b) is mechanical once that is settled.

### ⚑ The IBM PyTorch certificate is EARNED — 2026-08-29
**Completed 29 August 2026. Credential `DDDI9T0KHUJ4`.** Verified live by the leader against
`coursera.org/verify/DDDI9T0KHUJ4`: name, course title, issuer and date all match the PDF.
Filed and pushed to the private repo as `2b8da1a` —
`job_search/applications/hereon_aeon_up/certificates/IBM_Coursera_Deep_Learning_with_PyTorch.pdf`.

**The interview line, and it is a good one.** The submitted cover letter says *"I am in the final
module of the IBM certificate course"*. It is now finished. Say it unprompted and early: *"One
update since I wrote to you — I finished the PyTorch certificate on 29 August."* One sentence,
verifiable on the spot, and it shows a stated plan delivered. **The boundary is unchanged:** the
course has no Bayesian methods, no uncertainty quantification, no neural processes. Overclaiming
is now *worse* than before, because the credential ID puts the syllabus one click away.
`study_room/12_pytorch_course.md` is updated with all of this.

**Where it is still invisible:** the live website CV
(`job_search/applications/ml_interpretability_general/cv_ml_interpretability.tex` — md5-confirmed
as the source of `assets/Thejus_Mahajan_CV_ML.pdf`, the primary download on the site) has **no
PyTorch course entry at all**, and neither does `cv_general_ml/cv_ml_general.tex`. The website's
Certifications & Training section lists four cards and not this one. **Brief filed:**
`agents/briefs/2026-08-29_pytorch-certificate-rollout.md` — two `.tex` files, `experience.html`,
one asset copy, ten gates, ending in a screenshot. *The hereon CV and every other application CV
are frozen records of what was sent and are explicitly off limits.*

⚠ **Open, found while doing this:** `assets/Thejus_Mahajan_CV.pdf` and `Thejus_Mahajan_CV_DE.pdf`
on the website have **no source `.tex` anywhere in `job_search`** — every PDF in the repo was
hashed and neither matched. Two of the three CVs a visitor can download cannot currently be
rebuilt. Needs a decision from Thejus, not a worker.

⚠ **The public surface contradicts itself, and this is the bigger finding.** `skills.html` has
**no ML content whatsoever** — no PyTorch, no deep learning, no machine learning. Its Python card
reads *"Data science, automation, and bioinformatics pipelines: Pandas, NumPy, scikit-learn,
matplotlib, seaborn, xarray"*. Meanwhile `index.html` headlines *"Modelling · Data Engineering ·
Machine Learning"* and offers the ML CV as the primary download. A technical reader who clicks
Skills finds a bioinformatician. **Folded into the same brief** (§3.3): an ML section, a rewritten
Python card, a rewritten page subtitle. ~~The CV's Machine Learning line also finally gets the CNP.~~
**⛔ REVERSED 2026-08-30 by Thejus** — *"Lets not put things that we still not finalized. So we
remove the claim from the website as well."* The clause
`, conditional neural processes (implemented from scratch), uncertainty calibration (NLL, CRPS, ECE)`
has been **removed from both `.tex` files**, both PDFs rebuilt at 2 pages, and the brief and ledger
amended so Part B cannot put it back. See §3.
*(The CNP itself was re-verified on disk when the line was written — `cnp_synthetic` at `063bc6e`,
`RESULTS.md` giving cnp CRPS 0.1677 vs gp_oracle 0.0379, ratio 4.4214, with `runs/` logs behind it.
**The evidence was never the problem; the decision is that an unfinalised thing is not a written
claim.**)*

---

## ⚑ 0b. SEPARATING THE REPOSITORIES — decided 2026-08-29, not yet started

**Thejus's instruction:** *"We will move the hereon stuff and then interview preparation to the job
search repo or another repo. Let's keep everything standalone and don't mix up."* Correct, and it
is the structural fix §0 already agreed.

**The leader's ruling on the target: the trainer goes into `job_search`, not into a repo of its
own.** Three pieces of evidence, all checked today:

1. **`trainer/verify_cards.py:33` already hardcodes an absolute path into `job_search`** —
   `...\applications\hereon_aeon_up\study_room\06_do_not_claim.md`. The content gate loads its five
   forbidden-claim boundaries from the study room. The trainer is *already* coupled to the career
   repo; moving it there **removes** a cross-repo dependency rather than adding one.
2. **The content is career content, not chess content.** 205 cards: `hereon_aeon_up` (51),
   `air_quality`, `own_work`, `neural_processes`, `uncertainty`, `pytorch`, `bridge`, three German
   ladders. None of it is about chess. It belongs beside the study room.
3. **A new GitHub repo needs Thejus** — no agent here holds a token, deliberately. `job_search`
   exists, is private, and is already the right neighbourhood. Choosing it means the work can start
   without waiting on anyone.

**What moves:** `trainer/` (112 files), `launch_knowledge_trainer.bat`, `stop_knowledge_trainer.bat`,
`docs/CV_AI_MODULE.md`, `docs/career_strategy_conversation_aug2026.md`, `docs/career/`, and the
career-facing audit reports in `agents/reports/`.

**✅ The citation question is now ANSWERED by the public-repo decision.** `verify_cards.py` checks
that every repo citation resolves on disk (line 309, `if not target_file.exists()`). The gate
reports **193 repo citations** — 84 into `docs/`, 22 into `backend/` — both of which stay in the
chess repo, so moving the trainer turns 106 of them red. Earlier today the obvious fix (rewrite
them as GitHub URLs) collided with the repo going private, which would have made them dead links.
**The repo stays public, so URLs are now the correct answer** — and they are strictly better than
local paths, because a citation the reader can click is evidence and a relative path is not.

That leaves one real design item for the brief: `verify_cards.py` must gain a URL-shaped citation
check (it already counts `url_sources_count` separately, so the machinery is half there) instead of
`exists()` for the 106 that move out of reach. **Mechanical, and specifiable.**

**Also leader work, not worker work:** `state/NOW.md` and `state/JOURNAL.md` are roughly half
career war-room and half chess project state. Splitting them is authorship, and three of this
project's five fabricated deliveries came from handing a worker content.

### Done overnight, 2026-08-29
- **`applications/` is out of this repo.** The three PDFs were copied to
  `bioinformatics_project/job_search/applications/hereon_aeon_up/{research,other_documents}/`,
  md5-verified identical, committed as `0088b9f` and **pushed to the private repo**. Then removed
  here and `applications/` added to `.gitignore`.
- **The trainer split was NOT done.** It needs a GitHub repo to exist first, and creating one
  needs `gh` (not installed) or a token (deliberately not held). ⚠ Note before doing it:
  `trainer/verify_cards.py` hardcodes `PROJECT_ROOT / "docs" / "CV_AI_MODULE.md"` and the cards
  carry 193 repo citations, 72 into `docs/` and 22 into `backend/` — a standalone trainer repo
  breaks the content gate until those are re-rooted. It is a real task, not a `git subtree` one-liner.

### He drilled tonight — first real session since 2026-08-22
21 answers and 6 comments, all on `air-quality`, at L3/L4 — **levels that were unreachable until
today's fix**. Several scored 0.0. His own comments name the gaps:
- *"I have no idea what neural surrogate is."* (`aq-l4-002`)
- *"I don't know what their abbrevation mean."* (`aq-l3-001`)
- *"covariance is something that varies along with another … I am forgetting things like ANOVA
  which is very fundamental. This is scary."* (`aq-l4-002`)
- *"May be give me some examples?"* (`aq-l2-001`)

Two ideas of his worth keeping: linking AQI in Chennai / Mumbai / Delhi against Hamburg
(`aq-l1-003`), and the morning-pollution and jogging angle as a ready answer to *"which is the
latest paper you read?"* (`aq-l3-003`).

**These are content gaps, not bugs. Write the cards with him, awake — do not delegate them.**

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
material. *The instrument now works.*

**⚑ Be precise about this — the loose version of it misled the leader on 2026-08-29.** The app is
**in active use and saving correctly**; what is undrilled is **this ladder specifically**. From
`trainer/state/answers.jsonl`, read directly on 2026-08-29:

| | |
|---|---|
| total answers, all ladders | **127** across 19, 20, 21, 22, 26 and 28 August |
| most recent session | **2026-08-28**, 22 answers + 6 comments, ending 23:26 UTC (01:26 local on the 29th), **all on `air-quality`** |
| **`hereon-aeon-up` answers, ever** | **5** |
| distinct hereon cards ever seen | **5 of 52** |
| last hereon answer | **2026-08-22T19:42 UTC** |

So: *"he has not drilled since 22 August"* is **false** — he drilled on the 28th. *"He has not
drilled the hereon ladder since 22 August"* is true. **The 47 unseen cards include all 17 Level-4
cards on the publication gap and facing Karl, and all 9 Level-5 cards on delivering the talk** —
which is exactly the material that only became reachable on 2026-08-29.

**The app is one source of truth and nothing is being lost.** Desktop shortcut
`Knowledge Trainer.lnk` → `launch_knowledge_trainer.bat` (`%~dp0`) → uvicorn on port 8010 serving
`trainer.app:app` **from this repo**, reading and writing `trainer/state/`. There is no second copy
of the state anywhere on the machine — checked. `load_all_cards()` runs **per request**
(`trainer/app.py:111,152,184`), so newly authored cards appear without restarting the server.

**⛔ Constraint this puts on the separation (§0b):** the launcher resolves `%~dp0`, so moving
`trainer/` out of this repo **breaks the desktop shortcut he uses daily**. The brief must move the
`.bat` files with it and rebuild the shortcut, and prove the app still launches and serves.

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

**Cards status, updated 2026-08-29 (night):**
- ✅ **The ferryboat citation is WRITTEN** — `her-l3-011`, ladder now **52 cards** (206 total).
  **Re-verified against the Crossref API before writing**, not taken from the earlier note:
  Lauenburg, Marvin; **Karl, Matthias**; Matthias, Volker; Quante, Markus; **Ramacher, Martin**,
  *"City Scale Modeling of Ultrafine Particles in Urban Areas with Special Focus on Passenger
  Ferryboat Emission Impact"*, Toxics 10(1), doi:10.3390/toxics10010003. Karl is **second of five**,
  Ramacher **last**; first author is Marvin Lauenburg. The card's whole point is *never say "your
  paper"*. Gate passes at 206, **mutation-checked** (an injected "hands-on experience with
  EPISODE-CityChem" turns it red, restore turns it green), and **reachability confirmed by a
  400-draw cram distribution: all 52 served, the new card 7 times.**
- ✅ **The Ramacher EGU abstract** is already covered — `EGU25` appears in 3 cards after this
  morning's corrections. Nothing to write.
- ⛔ **ACT-AQ is NOT written, deliberately.** It came from the Deep Research batch and the leader
  **could not verify it** — the Helmholtz page 404s and a web search returns nothing matching.
  *The same batch produced the false "Karl has an ML record" claim.* **An unverified fact does not
  go on a card that will be recited to the people it is about.** If Thejus wants it, it needs a
  primary source first.

⚠ **Found while writing the card: 63 of the ladder citations point at the RETIRED `job_search`
clone.** They use `../job_search/...`, which resolves from the repo root to
`Documents\job_search` — the dead copy — while the newer L5 cards correctly use
`../bioinformatics_project/job_search/...`. The gate checks only that the path *exists*, and the
retired directory still does, so **it is green against a stale tree**. Re-rooting those 63 is bulk
work and belongs in the separation brief, not in a one-card edit.

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
- **⛔ The CNP is deliberately NOT on any CV — decided by Thejus, 2026-08-30.** *"Lets not put
  things that we still not finalized."* It was added to both live ML CVs on 2026-08-29 and
  **removed again on 2026-08-30**; the brief and `agents/ACTIVE.md` are amended so Part B cannot
  reintroduce it. **Do not re-litigate this and do not helpfully add it back.**
  *The reasoning, which is sound:* the submitted hereon CV claims nothing probabilistic — verified
  by grepping the sent PDF, not a note — and the cover letter's only mention frames neural
  processes as *"current areas of learning and implementation"*. Every public surface now agrees
  with the one document the panel is actually holding.
  *What this does NOT change:* the CNP is built, real, and the strongest thing he has for a
  probabilistic-DL post. It is **spoken** material — slide 9 of the deck — not written-claim
  material. And because nothing in the application mentions it, **nobody will ask; he must raise it.**

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

## 6. ~~The live defect: the LLM is reasoning about chess~~ — CLOSED 2026-08-30

**The seam is removed.** `agents/briefs/2026-08-27_llm-seam-removal.md` was executed on
2026-08-30 (21:45–22:05) and its report is `agents/reports/2026-08-27_llm-seam-removal_REPORT.md`.
No non-test module under `backend/` imports `llm_client`; neither repertoire endpoint calls the
enricher; the poisoned cache is deleted; the UI now shows text derived from LC0's own computed
values. `backend/tests/test_llm_seam.py` is the interlock — a static `ast` guard that fails
naming the offending file, mutation-verified red then green.

`301 − 12 + 2 = 291` backend tests; 49 frontend tests; the arithmetic balances.

### ⚠ Three things this left behind — do not lose them

1. **It was executed by the LEADER, so it was never independently audited.** The person who wrote
   the diff checked it. That is weaker than this repo's normal loop. **An audit brief for Gemini
   against this diff is a legitimate and cheap next item.**
2. **Nobody has looked at the Coach Explanation card in a running browser.** Vitest passes and
   the panel mounts, but this project's most-repeated failure is correct work nobody looked at —
   now four times over. Start the app, open a repertoire tree, look at that card.
3. **`kaggle_files/` holds a complete July clone of `backend/`** with both call sites and its own
   `llm_client.py`. Gitignored, local-only, not reachable from the served app, and NOT covered by
   the interlock. Found and deliberately not fixed. **Do not re-serve that snapshot** — regenerate
   it from HEAD when Kaggle is next used.

### What the brief had wrong, all understated

| brief said | actually measured 2026-08-30 |
|---|---|
| one call site, `app.py:658` | **two** — `app.py:659` and `app.py:745` (the drills endpoint) |
| filler on "four different positions" | **9 of 16** entries, 8 distinct EPDs |
| — | the other **7 entries are real Gemini output, truncated mid-word** |

That last row is the one that matters: the fallback template always ends with its fixed sentence,
so those 7 did not come from it. **The app had genuinely called a language model and served its
chess text.** Why they truncate at 25–37 characters, when `max_output_tokens=180`, is unexplained
and the evidence is now deleted — it survives only in the report.

Also worth knowing before anyone builds the *translator*: `llm_client.py` targets model id
`gemini-3.5-flash`, **which is not a real model**, and `google.generativeai` is deprecated
(`FutureWarning` in the suite). It is not usable scaffolding as it stands.

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

---

## 8. The timetable is live in the Knowledge Trainer — 2026-08-30

Thejus dictated a full day plan and asked for it to run 24/7 alongside the trainer. Built and
verified this session. **`trainer/content/timetable.json` is the single source of truth** — edit
that file, and the daemon, the API and the browser bar all follow it.

**The rule, once, so nobody re-derives it:** one reminder per block boundary, five minutes
before. It is simultaneously *"this session is ending"* and *"the next one starts"*, so nothing
is announced twice. **It sounds only when the block starting at that boundary is not rest or
sleep** — silent when a session ends (he is concentrating), alarm when a break ends. The 03:00
wake-up alarm fires *at* 03:00, not 02:55.

Two gaps in the dictated plan were filled rather than left silent: **04:15–04:30 = Rest** (he did
not specify it) and **22:00–03:00 = Sleep**. Both are one-line edits if he wants them different.

### Answered 2026-08-30: the tab is optional

He asked whether to keep a browser tab open all day. **No — open the trainer when he studies and
close it after.** The daemon owns the alarms. That question exposed a real defect and it is fixed:
with a tab open, the daemon and the page fired at the same instant and every alert arrived
doubled. The page now reads the daemon's heartbeat (`/api/schedule/daemon`, freshness of the
cursor file) and **stays silent while the daemon is alive**, taking the sound back within 15
seconds if the daemon dies. The button says which one is covering him.

Hardened at the same time: the cursor write is a `os.replace` that ran once per second, and this
machine has a documented WinError 5 denial from AV holding the target. It now retries and, if it
still fails, warns once and carries on — **a heartbeat write must never take the alarm clock
down.** Writes are throttled to once every 3 s.

### ⚑ CLOSED 2026-08-30 — Thejus confirmed the bar renders

*"The bar is running."* That was the fourth instance of the standing failure and it is shut.
Nothing about the timetable is now waiting on anyone.

### The trainer comment queue — READ IT EVERY SESSION

**`trainer/state/comments.jsonl` is the only channel he has to the leader from inside the app**,
and on 2026-08-30 the leader committed six of his comments twice without reading one of them.
One was a correct bug report that had been sitting ten hours. `CLAUDE.md` Step 0 item 5 now
routes to it. Anything newer than the last JOURNAL entry is unread.

Outcome of that triage, in full:
- **5 cards fixed** (her-l3-010, her-l4-006/-009/-012/-013): the question he had to answer was in
  the `topic` pill while the `question` field held a stage direction. All five now state the
  question outright.
- **New gate in `verify_cards.py`** — a question quoted in a topic must also appear in the
  question field. Mutation-checked, and it caught a fifth card the leader's own scan had missed.
  206 cards, 87 URLs, 0 errors.
- **Two of his questions folded back into the cards**, so they return in the drill rather than
  living in a chat log: the Eulerian/Lagrangian answer on `aq-l1-001` (**Karl's own model is a
  hybrid** — 3-D Eulerian grid CTM plus sub-grid Gaussian dispersion, HIWAY-2 for line sources and
  SEGPLU for point sources, GMD 12, 3357–3399, 2019, **Ramacher a co-author**), and the ferryboat
  paper's headline numbers on `her-l3-011`.

### ⚑ Two things worth his attention next

1. **Re-drill `her-l5-003` first.** He wrote *"I have to understand the problem and solution more
   clearly as I almost forgot."* That is **slide 7, the centrepiece** — the bug-admission slide the
   whole talk turns on. A half-forgotten level-5 card there, with the interview live, is the
   highest-value thing in the queue.
2. **His GOTM-FABM instinct is a genuine asset and should be rehearsed as a line.** A CTM is the
   same advection-diffusion-reaction equation he already solves, with the biogeochemical
   source/sink term swapped for chemistry. *"The numerics transfer, the chemistry does not"* is
   both true and exactly the register her-l4-012/-013 demand. It converts a gap into a bridge.

### ⚑ One thing still needs Thejus

1. ~~**Put `launch_schedule.bat` in the Startup folder.**~~ **DONE 2026-08-30** — the leader
   created `Startup\Knowledge Trainer Timetable.lnk` pointing at `launch_schedule.bat`
   (minimised), and started the daemon in this session (PID confirmed running, cursor file
   ticking). **So the 03:00 alarm exists tomorrow.** To undo it, delete that shortcut.
2. **Open `http://127.0.0.1:8010/` and click "🔔 Enable alarm" once.** Browsers refuse audio
   until a user gesture. *This is also the fourth instance of the standing failure* — the bar's
   logic is verified against the Python engine 45/45 and its markup parses, but **nobody has
   looked at the screen.** Same class as the KaTeX equations. Look at it.

### What was verified, and how

69 tests pass (37 new, `trainer/tests/test_schedule.py`). Five mutation checks, each red then
restored green. The **live daemon** fired all three reminder shapes against synthetic timetables
with boundaries two minutes out — at-start alarm, silent-into-rest, alarm-out-of-rest — with
matching `schedule_log.jsonl` lines. All three endpoints answered a live uvicorn and `/api/state`
is unchanged. The page's own JS was run in a node VM against the Python reference: 45/45.

`state/schedule_log.jsonl` (gitignored) records every reminder fired or missed. That is the
adherence record — the only honest answer to *"did I actually keep the schedule this week?"*

### ⚠ It adds to the footprint §0 is shrinking

`timetable.json` publishes his daily routine — wake time, two "Interview prep" blocks, German,
the mech-interp slot — in a repo that stays public. Much milder than what §0 already lists, and
`trainer/` is on the §0b removal list already, so the timetable leaves with it. Noted, not a
blocker on the feature.

---

## ⛑ 9. Configuration steering — Thejus's idea, taken forward 2026-09-01

**The aim is his and is not to be paraphrased away:**
`ideas/2026-09-01_steering_to_tal_configurations.md` holds his words and nothing else.
**Spec:** `docs/plans/PLAN_CONFIGURATION_STEERING.md`. **Worker brief (ACTIVE):**
`agents/briefs/2026-09-01_configuration-dataset-build.md`.

**The design decision, in one line:** the position we steer toward is the puzzle's `fen` column —
**`s_err`, where the opponent is to move and is about to go wrong** — not the position after their
error. You cannot steer into a position that requires their blunder to have already happened. 5.5M
recorded human failures, each stamped with the rating of the player who failed.

**Measured on disk 2026-09-01, both new:**
1. The puzzle `fen` is **one ply before the tactic** — proof: 0 of 5,527,851 solution lines are of
   odd length. `puzzle_regime.puzzle_position()` already does this correctly; a naive dataset build
   would have been off by one ply on every sample.
2. `data/puzzles/lichess_db_puzzle.csv.zst` (289 MB, local) carries **`GameUrl`** with game id and
   ply, so parent games cost a targeted API fetch, not the 500 GB archive download the worker
   report assumed. v2 only — Thejus demoted the roll-back idea himself.

**Division of labour, and it is a requirement not a preference:** Gemini builds the dataset;
**Thejus writes the PyTorch model and the Kaggle training loop himself** (*"this will also be a
great learning experience"*); the leader specs and audits. The previous session deleted that part
of his idea and was corrected for it.

**Gate before anything is trained:** alarm A3 in the brief — a logistic regression on the ten piece
counts alone must score **AUC < 0.65** on the built dataset. If piece counts separate the classes,
the CNN would score well and mean nothing. Hard stop, not a tuning knob. The leader re-runs A3
independently.

**Still open, unchanged:** `build_sac_session()` returns **0** — `data/training/profile.json` was
generated 2026-07-26 and carries the dead key `had_tal_move`; `sac_drill._get_sharp_findings`
selects on `had_sharp_move`. Needs Thejus's decision on corpus scope for regeneration.

---

**⛑ Φ IS TRAINED. F1 DID NOT PASS. The number is 0.6908 and it is not rounded up.**

```
TEST AUC      0.6908        material-only baseline  0.5017
F1 threshold  > 0.70        shortfall               0.0092
gates_passed  false         (phi_net/runs/phi_b2_test.json)
```

**F1 is recorded as FAILED.** The threshold was pre-registered in
`PLAN_CONFIGURATION_STEERING.md` §8 before the dataset existed, and 0.6908 is the single most
tempting number in this project's history to round. It is not being rounded, and the threshold is
not being moved. *A fired alarm is a stop, not a parameter* (`LEADER_BIBLE.md` §3.9).

**Two things in the result are genuinely good, and they are the more informative half:**

- **+0.19 over material.** Φ learned something real — not chance, not piece-counting.
- **Per-source AUC is balanced:** N1 spent-tactic **0.6955**, N2 quiet-play **0.6841**. Had Φ
  latched onto an artefact these would diverge. **The rebuilt dataset is honest** — the A4 rebuild
  paid off.

**The shortfall is NOT undertraining — it is a representation ceiling.**

| rung | rows | epochs | wall | best val AUC |
|---|---|---|---|---|
| B1 | 100,000 | 15 | 48.6 s | 0.6888 |
| B2 | 209,036 | 40 | 245.1 s | **0.6908** |

**Four times the data and 2.7× the epochs bought +0.002.** That is a plateau. The plan
pre-registered what an F1 failure means and the answer is not more compute:

> *F1 fails → configurations are not recoverable at 18 planes with this network. That is a real
> finding, not a failure of nerve. The response is to change the representation (relational
> features, or BT3 activations) — **not** to tune hyper-parameters until the number moves.*

**Calibration — fixed 2026-09-03.** Φ's raw sigmoid was over-spread, and worst exactly where
steering uses it (test bin 0.7–0.8 predicted 0.749 against an actual 0.654). Isotonic regression
fitted on **val**, reported on **test**:

```
expected calibration error   0.0522 -> 0.0050      (10x better)
worst decile error          +0.095  -> +0.007
test AUC                     0.6908 -> 0.6905
```

The AUC moves by 0.0003 because isotonic creates flat blocks and therefore ties, which changes
tie-averaging — **not** a loss of ranking information. Curve saved to
`phi_net/runs/phi_b2_calibration.json`. **Rank on raw Φ, display the calibrated number.**

**The UI — ⛑ CORRECTED 2026-09-03 after audit.** I previously wrote here that `app.py` sorts only
the *playable* set and that **LC0 keeps an absolute veto on blunders**. **That was wrong.**
`compute_steering_analysis()` never calls `steer_candidates()`, and `grep -c "steer_max_loss_cp|"`
`steer_min_eval_cp" backend/app.py` returns **0**. It uses its own tiers — 80 cp, then 150 cp, then a
**fallback with no eval constraint at all**. `steer_min_eval_cp = -60` is applied nowhere in the live
path.

**This is the cause of Thejus's field report** that opening steering produces *"spurious piece sacs
that can be easily refuted"*: in the opening the engine's top moves cluster, the tiers hold fewer
than two members, the fallback fires, and the highest-Φ move is surfaced regardless of eval.

Calibration and the experimental label are now wired (2026-09-03). **The missing floor is not fixed
— which floor to apply is a design decision and is Thejus's.** See
`agents/reports/2026-09-03_think-time-filter-and-phi-calibration-wiring_AUDIT.md` §2.

---

~~**STATUS 2026-09-02 (late): Φ IS READY TO TRAIN…**~~ — **DONE 2026-09-03.** Trained on Kaggle, evaluated, and wired into the UI. The result is the block above.

**What to do next, in order:**
1. Upload `dist/config_steering_dataset.zip` as a private Kaggle dataset (this is also the
   only backup of the dataset — see the warning below).
2. Upload `dist/phi_net_code.zip` as a second dataset.
3. Kaggle → New Notebook → **File → Import Notebook** → `dist/kaggle_phi_net.ipynb`.
4. Attach both datasets, choose a **single GPU** (P100 preferred — Φ trains on `cuda:0` with
   no DDP, so a second card idles), Run All.
5. **F0 should print ≈ 0.488.** If it does not, the mounted dataset is not the audited one —
   stop and check the version.

`phi_net/` — model, trainer, gates, evaluation, Kaggle notebook. Smoke-tested end to end on
CPU; **18 tests pass** across `test_phi_net_gate.py` and `test_config_steering.py`, and the
guards are **mutation-checked** (breaking `encode.py:39` reddens the frame test; restoring the
old B1 gate reddens `test_b1_proceeds_when_signal_is_present_but_below_f1`).

**Eighteen defects were found and fixed before upload** — twelve by self-review
(`phi_net/PREFLIGHT_REVIEW.md`) and six by an independent Gemini audit
(`agents/reports/2026-09-02_phi-net-kaggle-training_AUDIT_RESPONSE.md`), plus two more from the
historical-bugs report. The worst were: `roc_auc` doing one host-device sync per element;
the B1 gate trap that would have aborted the session on a good result; a stale `phi_b2.pt`
being scored as this run's result; and a Φ frame error in the README and the plan.

**⚠ Nobody has executed the mixed-precision path.** Reviewed twice, run zero times.
`--no-amp` bypasses all of it and reproduces the tested path exactly.

---

**✅ The dataset itself: BUILT, AUDITED, CLEAN.**
`data/training/config_steering/` — 261,748 rows (train 209,036 / val 26,222 / test 26,490),
34.7 MB train split; arrays `bb` (18 uint64), `y`, `motif` (20), `source`.
Leader's independent re-runs: **A3 = 0.4884**, **A4 = 0.5298** (thresholds 0.65 / 0.60). The
in-check/mobility leak that killed the first build is gone — 1.97% vs 2.01% in check, 30.20 vs
30.23 legal moves. Colour-flip guard mutation-checked: breaking `encode.py:39` reddens two tests.

**Next is Thejus's:** the PyTorch model and the Kaggle loop — B1 (50k+50k) then B2 (full,
held-out AUC = F1), per `PLAN_CONFIGURATION_STEERING.md` §8b. Nothing needs a GPU until he starts.

Two minor open items from the audit §4: zero the en-passant plane before the final run (set in
2.4% of negatives vs 0.1% of positives), and 182 boards (0.695% of val) recur in train with 5
carrying contradictory labels — irreducible, and a reminder that Φ's ceiling is below 1.0 by
construction.

---

## ⛑ 10. Profile regeneration — decided by Thejus, blocked on hardware, moving to Kaggle

**⛑ DECIDED 2026-09-03: filter by THINK TIME, not by time control.** Approved by Thejus.

Measured over his own moves in the 9,000-game corpus, from consecutive `[%clk]` values:

| time control | games | his moves | median think | ≥ 5s |
|---|---|---|---|---|
| **120+1 bullet** | 8,617 | 252,365 | **2.0 s** | **25.5%** |
| 300+3 blitz | 210 | 6,623 | 4.0 s | 48.2% |
| 60+0 | 148 | 3,995 | 1.0 s | 4.5% |
| 300+0 | 22 | 698 | 4.0 s | 41.1% |

**Do not drop bullet.** 25.5% of 252,365 is roughly **64,000 moves he thought about for five seconds
or more** — by far the largest pool of genuine decisions he owns. The 210 blitz games yield ~3,200.

**`min_clock_seconds = 20` gated on the wrong variable** — clock *remaining*, not time *spent*. A
move played in one second with 60s left was kept; a move deliberated for eight seconds with 15s left
was discarded. The code's own comment says the intent was to exclude flag-fall panic; think time is
the correct expression of that intent.

**Implemented 2026-09-03 in `backend/training/metrics.py`** (leader-owned): `min_think_seconds = 5.0`,
`parse_increment()`, `think_seconds()`, `is_reflex_move()`. Eleven tests in
`backend/tests/test_think_time_filter.py`, **mutation-checked** against three mutations — treating
unknown think time as a reflex, dropping the increment, and an off-by-one threshold — each of which
reddens a test.

**Effect:** ~68,000 nodes instead of 228,020. **70% less engine work, on better data** — a strict
improvement on both axes, and it attacks the ~51-day projection directly.

**Refinement to carry into the run:** Stage A (policy blindness) measured at **0.13 s/node**, so all
228,020 cost about 8 hours. **Run Stage A on everything; spend Stage B confirmations and TS2 only on
the ≥5 s population.** Full coverage of blindness, expensive confirmation only where it means
something.

**Honest caveat:** a blunder played in one second may still be real blindness — arguably that *is*
policy-blindness. The fast moves are not deleted, only left unconfirmed, and it is a filter
parameter, so it is recoverable.

**Still pending:** wiring the filter into `pipeline.py` (brief filed — `metrics.py` is done).

---


**He decided 2026-09-01: regenerate the profile.** Regeneration is confirmed to be the correct fix
— a real 25-game run produced `had_sharp_move` (not the dead `had_tal_move`) **and** real ECO keys
in `steer_summary` (`A40`, `A46`, `A48`, `C20`, not `"???"`). Both journal-recorded bugs die on
regeneration.

**⚠ Two premises corrected, both measured:**
1. **The corpus is 9,000 games, not 693.** `games_of_derdiedasdie/lichess_derdiedasdie_2026-07-21.pgn`
   — 8,617 of them 2+1 **bullet**, 210 at 5+3, 148 at 1+0. The 693 figure came from a stale memory of
   `...2026-07-19.pgn`, which is no longer on disk. **228,020** decision nodes survive the 20 s clock
   filter, of 272,974 user moves.
2. **It cannot be run on this laptop.** LC0 here is **BLAS/DNNL on 2 cores ≈ 100 nodes/s**
   (measured: 400 nodes → 3.64 s/position). Stage B costs **10.2 s per flagged move**; cold cost
   ≈ **8.2 min/game**. 100 games ≈ 14 h. 693 games ≈ 4 days. **9,000 games ≈ 51 days.**

**The lever, and it is already decided doctrine.** The budgets are *time*-limited
(`confirm_best_seconds: 6.0`, `confirm_played_seconds: 3.0`), and a GPU does not make a 6-second
search finish sooner — it makes it deeper. Only **node**-limited search converts GPU speed into
wall-clock savings (`LEADER_BIBLE.md` §4). `analyze(..., nodes=N)` and
`confirm_best_nodes`/`confirm_played_nodes` already exist; the node fields are `None`.

**⚠ The EPD cache is keyed by position only, not by budget** (§5 cache-key family). The 8,845
cached entries were computed at 6 s/3 s; switching to node budgets makes them a different
measurement under the same key. **Clear the cache when the budget changes** — leader's call, after
the T4 numbers land.

**Next:** `agents/briefs/2026-09-01_kaggle-gpu-profile-regeneration.md` — rehearsal + throughput
measurement, QUEUED behind the config-steering dataset build. Thejus runs the notebook; Gemini
prepares it; the leader sets the node budgets from the measured T4 throughput and only then specs
the full run.

**State right now:** `data/training/profile.json` is **unchanged** — the original 100-game profile
(646 findings, 562 steer, dead `had_tal_move` key). Backup of it at
`data/training/profiles/profile_pre_regen_20260901.json`. The backend is stopped.

---

## ⛑ 11. Leadership corpus, playbook, and the Bible — 2026-09-02

Built at Thejus's instruction: study historical leadership, distil it, apply it here.

- **`docs/leadership/knowledge/`** — 32 case files across 8 themes, plus `DISTILLATION.md` and
  `APPLICATION.md`. 2,565 lines. Cases chosen because they anatomise failure families this project
  has *actually suffered*. **Sourcing standard in the README:** no invented quotations, popular
  misattributions flagged (“failure is not an option” was written for a 1995 film), single-author
  accounts marked as such.
- **`docs/leadership/PLAYBOOK.md`** — the same doctrine indexed by **situation** rather than theme,
  for use mid-task. Sixteen entries, each ending in the case it came from.
- **`LEADER_BIBLE.md`** — five new doctrine rules (§3.8–12), six do-not-relitigate rows (§4), four
  new failure families (§5), and a new **§6a CURRENT STATE** because the July §6 was five weeks
  stale and the header still announced the compute campaign as live. **Read §6a, not §6.**
- **`LEADER_GROUNDING.md` §7** — the six mechanical seam checks. These prevent more damage than
  anything else written today.

**The honest yield, stated in `APPLICATION.md` §0:** of the eight defects an independent audit found
in the leader's work, **seven were mechanical** — fixed by `grep`, by executing the documented
command, and by timing the function. Two were genuine leadership failures. The corpus is worth what
its Part A (interlocks) and Part C (three unasked questions) are worth.

**The three unasked questions in `APPLICATION.md` Part C, carried here so they are not lost:**
1. There is no path by which a second Gemini challenge reaches Thejus over the leader's head.
2. **Nobody has asked whether the profile regeneration should happen at all** — 9,000 games of which
   8,617 are 2+1 bullet is a corpus of *reflex* errors. Cheap decompositions exist and none has been
   run.
3. The dataset exists in exactly one place.
