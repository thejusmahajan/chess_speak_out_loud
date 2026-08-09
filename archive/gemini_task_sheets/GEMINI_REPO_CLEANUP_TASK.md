# TASK FOR GEMINI (Instance 1) — Repo cleanup, archival & docs-consistency

Tidy the repo root and reconcile the docs. **NON-DESTRUCTIVE.** Your deliverables are two
reports plus SAFE, reversible archival via `git mv`. The leader (Claude) reviews before any
deletion. Scope is the **repo root docs/scratch clutter ONLY** — another Gemini instance is
editing `frontend/` concurrently, so **do not touch `frontend/`, `backend/`, `colab/`,
`docs/`, `data/`, or `scratch/`** (scratch holds live Kaggle logs).

## Hard rules
- **NEVER `rm` anything.** For clearly-dead files, `git mv` them into `archive/` (reversible).
  Anything you're not 100% sure about goes in the PLAN as a DELETE-CANDIDATE for approval — do
  not move it.
- **DO NOT touch (leave exactly where they are):** `LEADER_BIBLE.md`, `README.md`,
  `pyproject.toml`, `.gitignore`, `.gitattributes`, `HOW_TO_RUN.md`, `HOW_TO_USE.md`,
  `POST_VALIDATION_BACKLOG.md`, `ARCHITECTURE.md`, `WORKER_AGENT_COOKBOOK.md`,
  `QUESTIONS_FOR_LEADER.md`, and all ACTIVE Kaggle-campaign files:
  `colab/kaggle_diagnostic_run.py`, `KAGGLE_BEST_PRACTICES.md`, `GEMINI_LOG_TRIAGE_TEMPLATE.md`,
  `GEMINI_KAGGLE_REFERENCE_PROMPT.md`, `GEMINI_REPO_CLEANUP_TASK.md` (this file),
  `GEMINI_UI_BUGHUNT_TASK.md`, `GEMINI_UI_PERF_TASK.md`.
- Do not edit the CONTENT of any doc (except creating your two new reports). Consistency issues
  are REPORTED, not silently rewritten.
- Work on a branch or leave changes staged; **do not push.** STOP for leader review.

## Deliverable 1 — `REPO_CLEANUP_PLAN.md`
A table of EVERY root-level file that is a task-doc, report, scratch, or throwaway, classified:
`File | KEEP / ARCHIVE / DELETE-CANDIDATE | one-line reason (done? superseded? scratch?)`.
- The repo root has ~50 `.md` files, many one-off task specs (`*_TASKS.md`, `GEMINI_*_TASK.md`)
  and reports (`*_REPORT.md`) that are likely COMPLETED/OBSOLETE. Determine each via git history
  (`git log --oneline -- <file>`), references from other docs, and whether its subject shipped.
- **Known throwaway seeds (verify, then ARCHIVE via git mv):** `discovery.py`, `overnight.bat`,
  `scratch_analyze.json`, `tmp.json`, `test_api.py`, `test_fallback.py`, `test_policy.py`,
  `test_lc0_verbose.py`, `test_lc0_verbose2.py`, `frontend/discover*.mjs` (root-level dev
  scratch — EXCEPTION to the frontend rule: these specific `discover*.mjs` are throwaways, move
  only these, touch nothing else in frontend), `sample_games_to_analyze` (empty per project
  notes), `scratch_analyze.json`.
- For each ARCHIVE item, actually run the `git mv <f> archive/<f>` and list it under an
  "Archived this pass" section.

## Deliverable 2 — `DOCS_CONSISTENCY_REPORT.md`
Cross-check the surviving docs for contradictions and stale facts. For each: `claim | doc:line |
conflicting doc:line or current truth | recommended correction (describe, don't apply)`.
Seed checks (verify against current repo state, HEAD ~`7379c13` on `windows-dev`):
- **Host RAM**: several docs say Kaggle T4×2 has "~13 GB". Live readout showed ~30 GiB; the
  best-practices doc marks it NEEDS-VERIFY. Flag every doc that states 13 GB as fact.
- **".zip prevents .gz mangling"** (`KAGGLE_BEST_PRACTICES.md` §5): CONTRADICTED by our own
  experience (a `.pb.gz` inside our zip was still decompressed into a directory). Flag it.
- **Current baseline**: the first clean run is **213 findings / 263 steer_findings** (n=1,
  30 games, 2026-07-25). Flag any doc citing a different "baseline" (e.g. 28/22, 339/267) without
  noting it's a different/older set.
- **Net decisions** (LEADER_BIBLE §4): diagnosis net = BT3-768x15x24h; live app = 791556. Flag
  any doc that contradicts.
- Duplicate/overlapping guidance across `HOW_TO_RUN.md` / `HOW_TO_USE.md` / `USING_YOUR_PROFILE.md`.

## Constraints
- Non-destructive; reversible `git mv` only; deletions are proposals. Cite `git log`/refs as
  evidence for ARCHIVE calls. Report inconsistencies, don't rewrite docs. STOP when the two
  reports + safe archival are done.
