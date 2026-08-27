```
Brief-ID:     2026-08-27_llm-seam-removal
Written:      2026-08-27
Target repo:  chess_speak_out_loud
Route:        Antigravity (full workspace)
Type:         implementation
Status:       ACTIVE
Depends on:   2026-08-21_workflow-and-direction-review (found it); this session's audit (confirmed it fired)

Blast-radius:  repo
Reversibility: trivial (git preserves every deleted file)
Failure-mode:  SILENT  -> full protocol: diff + gate re-run + mutation test + null test
```

**Why this before the deadline item?** It is the only open item that puts *false chess coaching*
in front of the user, and the fix is bounded at roughly an hour. Everything else in the queue is
additive; this is subtractive and closes a live defect.

---

## INTENT

*(Intent outranks instructions. If any instruction below conflicts with this paragraph, the
intent wins — stop and report. Doing so is a success, never a boundary violation.)*

The aim of this project is that **the LLM is a translator of LC0's thoughts and never a chess
reasoner** — because a bad coach does more harm than no coach. A correct result is: after your
change, there is **no code path from any HTTP endpoint to a language model that is asked to say
something about a chess position**, and that fact is enforced by a test that goes red if anyone
re-introduces one — not by a comment, a flag, or a document. The user must lose nothing in the
UI: the panel that showed generated text must fall back to text derived from real computed
values. If you find a *second* such path that this brief does not name, that is the most
valuable thing you can report — report it, do not silently fix it.

---

## The defect, with the evidence

Do not re-derive this. It is verified. Read it so you know what you are removing.

1. `backend/app.py:658` calls `explanations.enrich_tree_explanations(tree)` **unconditionally**
   on the repertoire-tree endpoint.
2. `backend/training/explanations.py` contains **no `LLM_ENABLED` check anywhere**, and reaches
   `llm_client.generate_move_explanation` at line 63.
3. The context it hands the model (`explanations.py:44-62`) is: `fen`, `move_san`, `move_uci`,
   `critical_reason`, `eval_cp`, `user_blind_rate`, `opponent_replies`, `color`, `opening_name`.
   **No LC0 search tree. No policy distribution. No relational facts.** The model is asked to
   produce chess coaching from a position and a number. That is the violation.
4. Three documents assert this path is dormant and are therefore wrong:
   `backend/app.py:42`, `ARCHITECTURE.md:30`, `HOW_TO_RUN.md:90`.
5. **It has already run.** `data/training/cache/explanations.jsonl` holds 16 entries written
   2026-07-26 19:37. The sentence *"Focus on maintaining sound piece activity and watch out for
   opponent counter-play"* appears **verbatim on four different positions**. It comes from
   `_build_fallback_explanation` (`backend/llm_client.py:214-216`), which fires when
   `GEMINI_API_KEY` is unset. Other entries are truncated mid-word.

**Already checked, do not touch:** `generate_conversation` (the four-persona coach) is genuinely
dormant — its only call site, `backend/app.py:288`, is commented out. Its **import** at
`backend/app.py:35` is live but unused; remove the import only.

---

## Scope — the complete list of files you may touch

Touch nothing else. If you believe you must, **STOP and report**.

| file | action |
|---|---|
| `backend/app.py` | delete the unused import at line 35; delete the `enrich_tree_explanations` call and its local import at 657-659 |
| `backend/training/explanations.py` | **delete the file** |
| `backend/tests/test_explanations.py` | **delete the file** |
| `backend/tests/test_llm_seam.py` | **create** — the interlock (see Tests) |
| `frontend/src/components/Training/RepertoirePanel.tsx` | remove the `currentNode?.explanation` branch at 440-442; keep the `:` branch as the only content of the Coach Explanation card |
| `data/training/cache/explanations.jsonl` | **delete the file** — it is poisoned cache, and it will be re-served to the UI on the next request for those EPDs |
| `ARCHITECTURE.md` | correct line ~30 to describe what is now true |
| `HOW_TO_RUN.md` | correct line ~90 likewise |

**Do not delete `backend/llm_client.py`.** It is the scaffolding for the eventual *translator*
role, which is a decided aim. It must simply become unreachable from any request path.

**Commit nothing.** Leave the work uncommitted so the diff can be audited.

---

## Tests — these are the deliverable, not decoration

Create `backend/tests/test_llm_seam.py` with exactly two tests.

### `test_no_module_reachable_from_app_imports_llm_client`

A **static** test. Walk every `.py` file under `backend/` **excluding `backend/tests/` and
`backend/llm_client.py` itself**, parse each with `ast`, and collect every module that imports
`llm_client` in any form (`import backend.llm_client`, `from backend import llm_client`,
`from backend.llm_client import X`). Assert the resulting set is **empty**.

Write the assertion so the failure message **names the offending files**. A test that says
`assert False` teaches the next person nothing.

Do not implement this with a regex over file text. Use `ast`, so a reference inside a string or a
comment does not trip it and a real import cannot hide from it.

### `test_repertoire_tree_response_carries_no_generated_explanation`

A **behavioural** test. Build or stub a repertoire tree the way the existing repertoire tests do
(read `backend/tests/` first and reuse their fixtures — do not invent a new engine stub if one
already exists), exercise the path that `app.py:658` sat on, and assert **no node in the result
carries an `explanation` key**.

If reaching that endpoint requires the live LC0 engine, say so plainly in your report and test
the tree-construction function directly instead. **"Could not run it" is a valid and welcome
answer. Inventing a passing test is not.**

---

## Gate — run these, paste the real terminal output for each

Not a summary. Not "all tests passed". The actual output.

```
1.  <python> -m pytest backend/tests -q --deselect backend/tests/test_ts2_no_hang.py::test_ts2_orphan_future_cancellation_handled
2.  grep -rn "llm_client" backend --include=*.py | grep -v __pycache__
3.  grep -rn "enrich_tree_explanations" . --include=*.py --include=*.tsx --include=*.ts | grep -v __pycache__
4.  ls data/training/cache/
5.  cd frontend && npm test        (or the project's real frontend test command — check package.json)
6.  git status --short
```

Expected: (2) returns only `backend/tests/test_llm_seam.py`. (3) returns nothing. (4) shows no
`explanations.jsonl`. (6) shows only the files listed in Scope.

`<python>` is `C:\Users\Admin\miniconda3\envs\cszero\python.exe`.

**The suite count before your change is what it is — measure it first and report both numbers.**
Do not copy a count from any document in this repo; several of them are stale. Deleting
`test_explanations.py` will *reduce* the total, and that is expected and correct — state the
arithmetic explicitly: `before − deleted + added = after`. If it does not balance, that is a
finding, not a rounding error.

---

## Mutation test — you run this yourself and paste it

The leader will repeat it, but a submission without it is incomplete.

1. Add `from backend import llm_client` to any module under `backend/training/`.
2. Run gate command 1. Confirm `test_no_module_reachable_from_app_imports_llm_client` **fails**,
   and that its message names the file you just edited.
3. Revert. Confirm the file is byte-identical (`git diff` on it is empty) and the test passes.

Paste all three steps. A guard that has not been seen to go red is not a guard.

---

## Null test

Before you change anything, confirm the defect exists on the current HEAD, so we know the fix is
causal rather than coincidental:

```
grep -c "sound piece activity" data/training/cache/explanations.jsonl
```

Report the number. Then proceed.

---

## Report

Write `agents/reports/2026-08-27_llm-seam-removal_REPORT.md`. Include:

- the suite arithmetic, before and after, with both raw outputs
- every gate command's real output
- the mutation test, all three steps
- the null test count
- **any second LLM path you found that this brief did not name** — this is the highest-value
  section, and "none found, here is where I looked" is a complete answer
- **what you could not check.** This section must be non-empty. Twice in this project's history
  the worker's own "could not verify" section contained the most important finding.

The standing contract in `agents/README.md` applies in full and is not restated here.
