# JOURNAL — append-only session log

Newest first. One block per session. The purpose is that a restart never re-derives what a
previous session already established. Append; never rewrite a past entry — if it turns out to
be wrong, say so in the new entry and leave the old one visible.

Template:
```
## YYYY-MM-DD — <one-line title>
**Did:** ...
**Found:** ...
**Decided:** ...
**Open:** ...
**Repo:** commits, and whether they were PUSHED (verified, not assumed)
```

---

## 2026-08-27b — AEON-UP is SENT; the interview is now the live item; the CNP exists

**Did:**
- Re-pointed the whole state spine at the interview. `state/NOW.md` rewritten: §1 is the priority
  order Thejus gave (1 interview, 2 other applications + logging/reminders, 3 the two apps —
  LC0 chess and the spaced-repetition trainer, 4 the CNP), §2 is the measured interview gaps,
  §3 the CNP. `agents/ACTIVE.md` deadline block replaced accordingly.
- Recorded the terminal change and the worker economics in `CLAUDE.md`.

**Found:**
- **Q1 is answered: the application was SENT.** Three sources had disagreed for two days
  (`ACTIVE.md` said NOT SENT, the 08-26 memory said "sending today", the PDFs sat on disk).
  Thejus confirmed it directly. The 3 September deadline no longer governs.
- **The CNP was built, and no state file knew.** `cnp_synthetic` is at `db3eb90` with commit
  `063bc6e` "feat: CNP on synthetic data, with an honest uncertainty evaluation" — `cnp/`,
  `train_1d.py`, `train_city.py`, `tests/`, five `runs/*.log`, four figures, `RESULTS.md`,
  `REFEREE_REPORT.md`. The leader's own memory dated 2026-08-26 asserts "⚠⚠ THE CNP WAS NEVER
  BUILT (verified)". **That note was true when written and is now false** — left visible per the
  append-only rule, corrected in `state/NOW.md` §3 and in the memory file.
  This is what puts something behind the word *implementation* in the submitted cover letter.
  The repo is **dirty**: 5 modified + 1 untracked. Commit before it is ever screen-shared.
- **The largest interview hole is the publication gap, and it has zero coverage** across 14
  study-room files / ~3,400 lines. Five publications, all 2018–2020 astrochemistry, nothing from
  the 2021–2025 marine post-doc. Also thin: TVöD E13 vs the stated €75k, questions *for* the
  panel, no talk artefact, Karl's ultrafine-particle side never addressed in the letter.
- **The terminal is now PowerShell** (Antigravity integrated terminal, switched from `cmd`), and
  it is **Windows PowerShell 5.1** — no `&&`, no ternary. Both shells verified working; `cszero`
  resolves (Python 3.11.15, torch 2.13.0+cpu). Cause of the crash not determined.
- **A bash heredoc failed** writing a long markdown file — "unexpected EOF while looking for
  matching quote". Use the Write tool for file content; Bash for reading, grep and git.

**Decided:**
- The interview inherits the deadline discipline verbatim: status stated first, one non-interview
  brief at a time, every brief justifying itself against it, no new meta-process documents.
- The LLM-seam brief keeps its ACTIVE slot as that one exception — the chess app is interview
  evidence, and it currently ships a coach that talks without knowing anything.
- Application logging and reminders belong in `job_search` as one artefact, not as new process
  machinery in this repo.

**Open:**
- H1–H6 in `state/NOW.md` §2, H1 (the publication gap) first.
- Q2 (ICON-O/HAMOCC) and Q3 (NIT Calicut date) are now interview risks, not just website risks.
- Q4 (do the trainer equations render?) and Q5 (idiomatic German) still need two minutes each.
- `cnp_synthetic` working tree is dirty.

**Repo:** committed and pushed to `origin/windows-dev`; verified with `git status` reporting
nothing ahead.

---

## 2026-08-27 — built the restart spine; confirmed the LLM defect is live and cached

**Did:**
- Created the missing entry point. `CLAUDE.md` at the repo root is auto-loaded by Claude Code on
  every cold start; it is a thin router, not content. It points at `state/NOW.md`,
  `state/JOURNAL.md`, `LEADER_BIBLE.md`, `agents/ACTIVE.md`, and carries the session-close
  routine. Added `state/NOW.md` (live state), `state/JOURNAL.md` (this file), `state/MAP.md`
  (question → file index).
- Wrote and registered `agents/briefs/2026-08-27_llm-seam-removal.md` for Gemini.
- Committed and pushed the backlog described below.

**Found:**
- **The chess repo was 35 commits ahead of origin, unpushed**, with 11 uncommitted paths —
  including two audit reports and two trainer ladders. `LEADER_BIBLE.md` §6 asserts "everything
  pushed to origin". It was not. Same failure class as the website repoint that sat uncommitted
  for three days after being audited ACCEPT.
- **The LLM seam has already fired and cached its output.**
  `data/training/cache/explanations.jsonl` holds 16 entries written 2026-07-26. The sentence
  *"Focus on maintaining sound piece activity and watch out for opponent counter-play"* appears
  verbatim across four different positions. It comes from `_build_fallback_explanation`
  (`backend/llm_client.py:214-216`), which fires when `GEMINI_API_KEY` is unset. Other entries
  are truncated mid-word. `llm_client.py` targets model id `gemini-3.5-flash`, which is not a
  real model. This answers the 2026-08-22 audit's first "could not check" item — *does it fire
  in production?* — with **yes**, from evidence on disk.

**Decided:**
- The problem was never a shortage of documentation — it was that none of it was on the path a
  cold start actually takes. `CLAUDE.md` is the fix because the harness loads it whether or not
  anyone remembers to. Everything else hangs off it.
- `state/` holds cross-cutting live state; `agents/ACTIVE.md` remains the sole source of truth
  for worker brief status. No fact is duplicated between them — `NOW.md` points at the ledger
  rather than restating it.

**Open:**
- Q1–Q5 in `state/NOW.md` §2. **Q1 (is AEON-UP sent?) is unanswered and outranks everything.**
  Asked this session; no response.

**Repo:** see the commit below this entry's date in `git log`. Pushed to `origin/windows-dev`
and verified with `git status` reporting nothing ahead.
