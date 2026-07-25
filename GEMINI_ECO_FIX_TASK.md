# TASK FOR GEMINI — Root-cause & fix `ECO='???'` (opening classification broken on Kaggle)

The last Kaggle 2×T4 diagnosis produced a healthy profile EXCEPT every opening is unclassified:
**100% of `findings[]`, `steer_findings[]`, `aggregates.by_opening`, and `steer_summary` have
`opening.eco == "???"`** (verified: 0 of 213 findings have a real ECO). It works LOCALLY
(LEADER_BIBLE §6 lists "openings fix" as done+verified), so something about the Kaggle run
breaks it. Find the true cause and fix it. Report + fix; run the local tests; **do not push.**
STOP for leader review.

## Known facts (grounded)
- The classifier is `backend/training/openings.py` — "ECO/opening prefix matcher (Gemini-owned)".
- On Kaggle the backend is imported FROM THE DATASET (`/kaggle/input/.../backend/`), and the run
  parses PGNs itself (the diagnostic splits the PGN text). Findings DO carry real game headers
  (white/black/date) and moves (`pv_san`), so PGN parsing itself worked — only ECO lookup failed.
- **Leading hypothesis (check FIRST):** `openings.py` loads an external ECO/opening DATA FILE
  (e.g. a `.tsv`/`.json`/`.pgn` ECO table) by a path. If that file is **gitignored or otherwise
  not included in the Kaggle dataset**, or loaded by a path that resolves differently on Kaggle
  (relative to `__file__`/cwd), the matcher silently falls back to `'???'`. This is the SAME
  class as the missing-`.pb.gz` weights bug — a data dependency that never shipped to the dataset.

## Investigate (report each with file:line)
1. **Data dependency:** Does `openings.py` read a file? What path? Is that file tracked in git or
   gitignored? Would it be present under `/kaggle/input/.../backend/` given how the dataset was
   built? (Check `.gitignore` and whether the file sits inside `backend/`.)
2. **Path resolution:** If it loads a file, is the path relative to `__file__` (survives the
   dataset import) or to cwd/repo-root (breaks when run from `/kaggle/working`)?
3. **Silent fallback:** Does the matcher swallow an exception (missing file / parse error) and
   return `'???'` instead of failing loudly? (Like the chmod bug — a silent `except` hid the real
   cause.)
4. **Call path:** Trace how `pipeline.py` invokes the opening classifier — is it passed the moves
   it needs? Could the diagnostic's custom PGN split drop a header the matcher relies on?

## Fix (make ECO work on Kaggle without breaking local)
- If it's a missing/mis-pathed data file: make the load robust (resolve relative to `__file__`),
  and if the file is gitignored, state EXACTLY which file must be added to the Kaggle dataset and
  where (so the leader/user can ship it) — OR, if the ECO table is small, consider committing it
  inside `backend/` so it ships with the dataset automatically. Recommend the safest option.
- Make any silent `except` LOUD (log the real error) so a future failure can't hide.
- Do NOT change the classification LOGIC/output for the local (working) case — behavior-preserving
  except that Kaggle now resolves ECOs too.

## Gates & constraints
- Run the local backend tests (the suite is 149 passed / 5 skipped) — stay green; add/adjust a
  targeted test for the file-resolution fix if useful (don't delete assertions).
- Do NOT touch `backend/training/metrics.py` (leader-owned) — file any concern in
  `QUESTIONS_FOR_LEADER.md`.
- Deliverable: `ECO_FIX_REPORT.md` (root cause with file:line + evidence; the fix; whether a file
  must be shipped to the dataset and which; test results) + the code fix. Don't push. STOP for review.
