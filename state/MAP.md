# MAP — which file answers which question

262 non-vendor markdown files live here. This is the index so you never grep for orientation.
If a question below has no answer on disk, that is a gap worth filing, not worth re-deriving.

---

## Orientation (a cold restart reads only these)

| question | file |
|---|---|
| What do I read first? | **`CLAUDE.md`** (auto-loaded) |
| Where is the project *today*? | **`state/NOW.md`** |
| What happened recently, and why? | **`state/JOURNAL.md`** |
| What are the rules I operate under? | **`LEADER_BIBLE.md`** (§4 decided, §5 failure catalog) |
| What is the worker doing? | **`agents/ACTIVE.md`** |
| How do I brief a worker without hurting us? | `agents/README.md`, `docs/leadership/WORKER_AGENT_COOKBOOK.md` |
| How do I *ask Gemini a question* about the project? | **`agents/CONSULT_GEMINI.md`** — paste it, add the question at the bottom |
| Where do its answers land, and how are they checked? | `agents/consultations/`, audited by `python agents/audit_consultation.py` |
| What mistakes do *I* make? | `docs/leadership/LEADER_GROUNDING.md` — read before writing any brief |

## The aim

| question | file |
|---|---|
| What is the north star, in full? | `docs/NORTH_STAR_decoding_lc0.md` |
| What is the product meant to become? | `docs/plans/GOAL_BOOK.md` |
| What is the open research frontier? | `docs/SALIENCE_PROBLEM.md` |
| What is the current plan against it? | `docs/plans/PLAN_SALIENCE_CNP.md` |
| Why do we think LC0 has plans to decode? | `docs/research_learned_lookahead.md` |
| How do the three tracks (build / learn / apply) connect? | `docs/leadership/COMMAND_BASE.md` |

## Definitions — the ground truth for any chess claim

| question | file |
|---|---|
| What counts as a tactical theme? | `docs/THEME_DEFINITIONS.md` |
| What counts as a positional fact? | `docs/POSITIONAL_DEFINITIONS.md` |
| What is a "sacrifice"? | `docs/THEME_DEFINITIONS.md` — material over a forced line via Lichess `cook()`, **never** complexity |
| Which annotation sources are allowed? | `docs/public_domain_chess_library.md` — GM / world-class trainers / public-domain books only |

## Running it

| question | file |
|---|---|
| How do I run the app? | **`HOW_TO_RUN.md`** (authoritative) |
| How is it put together? | `docs/plans/ARCHITECTURE.md` |
| How does a user use it? | `docs/guides/HOW_TO_USE.md`, `docs/guides/USING_YOUR_PROFILE.md` |
| How do I deploy? | `DEPLOY_DEBIAN.md` if present; otherwise `HOW_TO_RUN.md` |

## Code that matters

| thing | path |
|---|---|
| Fact extractor (the machine's "eyes") | `backend/training/relational_facts.py` |
| Plan-level facts (runs LC0 on a position) | `backend/training/critical_points.py::position_plan_facts` |
| Metrics — **leader-owned**, workers file questions instead | `backend/training/metrics.py` |
| The live LLM seam (defect — see `state/NOW.md` §4) | `backend/app.py:658` → `backend/training/explanations.py` → `backend/llm_client.py` |
| Flashcard trainer | `trainer/` (engine, `content/ladders/*.json`, `state/`) |

## The other two repos

| repo | path | what it holds |
|---|---|---|
| `job_search` | `../job_search` (branch **master**) | CVs, cover letters, `applications/hereon_aeon_up/` incl. the study room and `06_do_not_claim.md` — **the binding constraint on anything he says or writes** |
| personal site | `../thejusmahajan.github.io` (branch **main**) | the public site and blog |

## History — pull on demand, do not read cold

`archive/` (108 files), `docs/guides/KAGGLE_BEST_PRACTICES.md`, `discussions/`, `docs/discussion_*.md`,
`docs/SESSION_LOG_2026-08.md`, and the full brief/report archive in `agents/briefs/` +
`agents/reports/`.

**A file with `> **STATUS: SUPERSEDED` at the top is history, not instruction.** Convention is
in `docs/leadership/LEADER_GROUNDING.md`; only one root file currently carries it, which means most stale
documents are not marked. Treat an undated claim with suspicion and re-check it against code.
