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
