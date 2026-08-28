# BRIEF — reorganise the repository without breaking either app

**Filed:** 2026-08-29 by the leader
**Worker:** Gemini 3.7 Flash (High), Antigravity IDE, workspace `chess_speak_out_loud`
**Status:** ACTIVE

**Why this before the interview?** Thejus asked for it directly, and the reason is attention, not
tidiness: the root carries **30 markdown files**, ten of which nothing references, and he has to
scan past all of them to find the four files a working session actually needs. This is a
mechanical, fully-specified move-and-relink job. It adds no new capability and must change no
behaviour whatsoever.

---

## 0. Read this before you move anything

### 0.1 The one rule that outranks every other instruction here

**Both apps must work identically after your change, and you must prove it by running them.**

If a step in this brief would break an app, **stop and report** — do not improvise a fix, do not
"repair" an import, do not adjust a test to pass. A tidy repository whose apps error on launch is
a total failure of this task, and Thejus said so explicitly: *"I don't want them to show an error."*

### 0.2 What you may and may not touch

**You may move only files matching `*.md`, plus the two junk files named in §4.**

**You may not move, rename, or edit — for any reason:**

```
backend/    frontend/    engine/    trainer/    data/    scripts/    colab/
kaggle_files/    profiles/    games_of_derdiedasdie/    downloads/    state/
applications/    agents/    archive/    docs/           (as directories — see §3 for what goes INTO them)
pyproject.toml    .gitignore    .gitattributes
*.bat  (all four launchers)
```

The `.bat` launchers resolve the project directory as `%~dp0` — the directory the `.bat` itself
sits in. **Moving one silently changes what `PROJECT_DIR` means and breaks both launchers.** They
stay at the root. This is not negotiable and is not a matter of taste.

**You may not edit the body of any file** except the four link-repair targets named in §5. Moving
a file is not editing it. Rewriting a paragraph inside it is, and is forbidden.

**You may not touch flashcard content.** `trainer/content/ladders/*.json` has exactly one
permitted edit, in §5.3, and it changes only `sources` path strings. Every other field in every
card — `question`, `answer`, `explanation`, `trap`, `difficulty`, `requires`, `level`, `id`,
`ladder`, `topic` — is off limits. Three fabricated deliveries on this project came from a worker
being asked for content. This is not that task.

### 0.3 Use `git mv`, always

Every move is `git mv <src> <dst>`. Never `mv`, never `Move-Item`, never delete-and-recreate.
`git mv` preserves history and makes the whole change reviewable as renames rather than as 30
deletions and 30 additions.

**Delete nothing.** Not one file. Files that have outlived their use go to `archive/`, which is
what `archive/` is for and what the 2026-07-25 cleanup pass already established as the convention.

### 0.4 The contract

`agents/README.md` applies in full. Specifically: never invent a number, paste real command
output, report every deviation, and stop and ask for anything this brief does not cover.

**Do not commit. Do not push.** Leave the tree dirty. The leader audits the diff.

---

## 1. Establish the baseline FIRST — before you move a single file

You cannot prove you broke nothing unless you know what "nothing broken" looked like. Run all
five, in order, and paste every output into your report as **Baseline**. If any of these is
already failing before you start, **stop and report that** — do not proceed.

```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests -q --deselect backend/tests/test_ts2_no_hang.py::test_ts2_orphan_future_cancellation_handled
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer\verify_cards.py
git status --short
git log --oneline -1
```

The expected shape, from the leader's own run on 2026-08-29: trainer tests **30 passed**,
`verify_cards.py` **[PASS] / 205 cards / 193 repo citations / 175 URL citations**, `git status`
clean except one untracked `applications/hereon_aeon_up/other_documents/` directory, HEAD at
`d32558d`. The backend suite's expected count is whatever your baseline run prints — record it,
do not guess it.

**Note the deselect.** `test_ts2_orphan_future_cancellation_handled` is a load-sensitive flake that
fails on clean HEAD too. Deselecting it is correct here; do not investigate it and do not "fix" it.

---

## 2. The load-bearing facts you need, already established

The leader measured these on 2026-08-29. You do not need to re-derive them, but everything in §3
depends on them being true, so a spot-check is welcome.

**Which root markdown files anything else refers to.** Counted over `*.md`, `*.py`, `*.json`,
`*.bat` and `*.toml`, excluding `.git`, `node_modules`, `archive`, `data` and `scratch`:

| inbound refs | files |
|---|---|
| 26–15 | `README.md`, `HOW_TO_RUN.md`, `LEADER_BIBLE.md`, `PLAN_SALIENCE_CNP.md`, `GM_CURRICULUM_PLAN.md` |
| 11–9 | `LEADER_GROUNDING.md`, `WORKER_AGENT_COOKBOOK.md`, `COMMAND_BASE.md`, `ARCHITECTURE.md`, `GOAL_BOOK.md` |
| 5–1 | `WORKLOG_TRAINING.md`, `KAGGLE_BEST_PRACTICES.md`, `POST_VALIDATION_BACKLOG.md`, `QUESTIONS_FOR_LEADER.md`, `GOALBOOK_REVIEW.md`, `CLAUDE.md`, `USING_YOUR_PROFILE.md`, `HOW_TO_USE.md`, `UI_PERFORMANCE_BEST_PRACTICES.md`, `GOAL_ELICITATION_QUESTIONS.md` |
| **0** | `USUAL_SUSPECTS_REPORT.md`, `UI_PERF_AUDIT.md`, `UI_ISSUES_TRIAGE.md`, `UI_BUGHUNT_REPORT.md`, `SRS_AWARE_DECK_REPORT.md`, `REPO_CLEANUP_PLAN.md`, `PROFILE_TRIAGE.md`, `HANDOVER.md`, `GEMINI_THEME_TAGGER_PHASE_C.md`, `CRITICAL_POINTS_DESIGN.md` |

**Two things that will bite you if you forget them:**

1. **`trainer/verify_cards.py:310` fails the content gate if a card cites a repo path that no
   longer exists on disk.** The cards carry **193** repo citations: 72 into `docs/`, 22 into
   `backend/`, and **12 to `PLAN_SALIENCE_CNP.md` at the root**. Move that file and twelve cards
   break the gate unless you also rewrite their `sources` strings. §5.3 tells you exactly how.
2. **`verify_cards.py` hardcodes `PROJECT_ROOT / "docs" / "CV_AI_MODULE.md"`** (line 35). `docs/`
   keeps its name and that file does not move.

**Markdown filenames appearing inside Python docstrings** (`backend/training/*.py` mentions
`GM_CURRICULUM_PLAN.md`, `WORKLOG_TRAINING.md` and others) are **prose, not file reads**. No Python
code in this repository opens a markdown file at runtime. You do **not** need to update docstrings,
and you must not, because that is editing file bodies. Several already name files archived long ago.

---

## 3. The target structure

The root keeps **four** markdown files and nothing else. These four are the cold-start spine — the
files a session reads before it does anything — and moving them costs more than it saves:

```
CLAUDE.md         auto-loaded by the harness on every cold start; it is the router
README.md         the GitHub landing page
LEADER_BIBLE.md   named by CLAUDE.md step 0
HOW_TO_RUN.md     the authoritative runbook, 19 inbound references
```

Every other root `*.md` moves to exactly one of four destinations. Create the three new
subdirectories under the existing `docs/` and `archive/`; do not invent any others.

### 3.1 → `docs/leadership/`

The operating system of the project — how the leader and worker work.

```
COMMAND_BASE.md
LEADER_GROUNDING.md
WORKER_AGENT_COOKBOOK.md
QUESTIONS_FOR_LEADER.md
```

### 3.2 → `docs/plans/`

Live design and planning documents that are still consulted.

```
PLAN_SALIENCE_CNP.md          ← ⚠ 12 card citations point here; see §5.3
GM_CURRICULUM_PLAN.md
GOAL_BOOK.md
GOALBOOK_REVIEW.md
GOAL_ELICITATION_QUESTIONS.md
POST_VALIDATION_BACKLOG.md
CRITICAL_POINTS_DESIGN.md
ARCHITECTURE.md
WORKLOG_TRAINING.md
```

### 3.3 → `docs/guides/`

How to use and operate things.

```
HOW_TO_USE.md
USING_YOUR_PROFILE.md
KAGGLE_BEST_PRACTICES.md
UI_PERFORMANCE_BEST_PRACTICES.md
```

### 3.4 → `archive/reports/`

Finished, superseded, or zero-reference documents. **Archived, never deleted.**

```
USUAL_SUSPECTS_REPORT.md
UI_PERF_AUDIT.md
UI_ISSUES_TRIAGE.md
UI_BUGHUNT_REPORT.md
SRS_AWARE_DECK_REPORT.md
REPO_CLEANUP_PLAN.md
PROFILE_TRIAGE.md
HANDOVER.md
GEMINI_THEME_TAGGER_PHASE_C.md
```

**`CRITICAL_POINTS_DESIGN.md` is listed in §3.2, not here, despite having zero inbound
references** — it is a design document for a live feature, not a finished report. If you think
that is wrong, say so in the report; do not move it yourself.

---

## 4. The two junk files at the root

```
git mv texput.log archive/reports/texput.log
git mv gemini_stable_drill_ids_srs.txt archive/reports/gemini_stable_drill_ids_srs.txt
```

`texput.log` is LaTeX crash output from the 2026-08-27 deck build. `gemini_stable_drill_ids_srs.txt`
is a 2026-07-26 scratch list. Both are archived rather than deleted, per §0.3. Note that `*.log` is
in `.gitignore`, so `git mv texput.log` may report that the file is untracked — in that case use a
plain move for **that one file only** and say so in your report.

---

## 5. Link repair — the part that actually takes care

Moving files silently breaks every reference to them. You repair references in **exactly four
places** and nowhere else.

### 5.1 `CLAUDE.md`

It names `state/NOW.md`, `state/JOURNAL.md`, `LEADER_BIBLE.md`, `agents/ACTIVE.md`,
`state/MAP.md`, `HOW_TO_RUN.md` and `LEADER_GROUNDING.md`. Of those, **only
`LEADER_GROUNDING.md` moves** (to `docs/leadership/`). Update that one path. Change nothing else
in this file — not a word of prose, not a heading. It is the only file the harness loads
automatically, and a mistake in it degrades every future session.

### 5.2 `state/MAP.md`

This file exists to answer *"which file tells me X?"* and it names 26 markdown paths. **Every path
in it that you moved must be updated to the new location.** Update paths only; do not reword the
descriptions, do not add rows, do not remove rows.

### 5.3 `trainer/content/ladders/*.json` — the twelve `PLAN_SALIENCE_CNP.md` citations

**This is the only permitted edit to a card file, and it is a path string substitution only.**

Replace the exact string `PLAN_SALIENCE_CNP.md` with `docs/plans/PLAN_SALIENCE_CNP.md`, **only
where it appears inside a `sources` array**. Do it with a script that reads and writes UTF-8
explicitly:

```python
import io, json, glob
for p in glob.glob("trainer/content/ladders/*.json"):
    cards = json.load(io.open(p, encoding="utf-8"))
    changed = 0
    for c in cards:
        for i, s in enumerate(c.get("sources", [])):
            if s == "PLAN_SALIENCE_CNP.md":
                c["sources"][i] = "docs/plans/PLAN_SALIENCE_CNP.md"
                changed += 1
    if changed:
        io.open(p, "w", encoding="utf-8", newline="\n").write(
            json.dumps(cards, indent=2, ensure_ascii=False) + "\n")
        print(p, changed)
```

⚠ **`json.dumps` will reformat the whole file**, so the diff will be large even though the change
is twelve strings. That is expected. What is **not** expected is any change to a `question`,
`answer`, `explanation` or `trap`. **Gate 5 in §6 checks exactly this** and it is the gate most
likely to catch a mistake, so read it before you run the script.

⚠ **Never use PowerShell 5.1 `Get-Content`/`Set-Content` on these files.** 5.1 reads ANSI and
writes UTF-8, which turns every em dash into `â€"`. That corrupted `state/JOURNAL.md` on
2026-08-27 and 62 lines had to be reverted. Use the Python above.

### 5.4 Cross-references between the moved documents themselves

After moving, some of the moved files link to each other by bare filename. **Do not chase these.**
Fixing them means editing file bodies, which §0.2 forbids. Instead, **list them in your report**:
run the grep in Gate 6 and paste the result. The leader decides what to repair and whether it is
worth a second pass.

---

## 6. ✅ CHECKPOINT — six gates, all of them, output pasted verbatim

A report without all six pasted is not accepted.

**Gate 1 — the root is clean.**
```powershell
Get-ChildItem -File | Select-Object -ExpandProperty Name
```
Exactly four `.md` files must remain: `CLAUDE.md`, `README.md`, `LEADER_BIBLE.md`, `HOW_TO_RUN.md`.
No `.log`, no `.txt`. The four `.bat` launchers, `pyproject.toml`, `.gitignore` and `.gitattributes`
must still be there.

**Gate 2 — nothing was lost.**
```powershell
git status --short
```
Every line must be `R` (rename) or `M` (modified). **A single `D` without a matching `R` means a
file was deleted — stop and report.** The count of `R` lines must equal the number of files you
moved.

**Gate 3 — the content gate still passes, with the same numbers.**
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer\verify_cards.py
```
Must print `[PASS]`, **205 cards**, **193 repo citations**, **175 URL citations** — identical to
your baseline. If the repo-citation count dropped, a citation now points at a moved file and §5.3
was incomplete. **Do not fix that by deleting a citation.**

**Gate 4 — both test suites, unchanged from baseline.**
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests -q --deselect backend/tests/test_ts2_no_hang.py::test_ts2_orphan_future_cancellation_handled
```
Trainer: **30 passed**. Backend: the same count as your baseline.

**Gate 5 — no card content changed. Run this, it is the one that matters.**
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -c "import io,json,glob,subprocess; bad=[]; [bad.append((p,c['id'],k)) for p in glob.glob('trainer/content/ladders/*.json') for c,o in zip(json.load(io.open(p,encoding='utf-8')), json.loads(subprocess.run(['git','show','HEAD:'+p.replace('\\','/')],capture_output=True,text=True,encoding='utf-8').stdout)) for k in ('id','question','answer','explanation','trap','level','difficulty','requires','ladder','topic') if c.get(k)!=o.get(k)]; print('DIFFERENCES:',len(bad)); [print(b) for b in bad[:20]]"
```
It compares every card field except `sources` against `HEAD`. It must print **`DIFFERENCES: 0`**.
Anything else means you altered content — revert `trainer/content/` entirely and redo §5.3.

**Gate 6 — both apps launch and serve, and you must actually do this.**

This is the gate Thejus cares about. Static checks do not satisfy it.

*The knowledge trainer:*
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn trainer.app:app --port 8010
```
In a second shell:
```powershell
curl.exe "http://127.0.0.1:8010/api/next-card?ladder=hereon-aeon-up&cram=true"
curl.exe "http://127.0.0.1:8010/api/state"
```
Paste both responses. Paste **the server's full console output**, including any traceback or
warning. Then stop the server.

*The chess backend:* follow `HOW_TO_RUN.md` — it is authoritative and you follow it exactly as
written. Start the backend, confirm it comes up, paste the startup log, hit its health or root
endpoint, paste the response, then stop it. **If `HOW_TO_RUN.md` conflicts with anything in this
brief, `HOW_TO_RUN.md` wins for how to launch — stop and report the conflict.**

*Then the dangling-link inventory for §5.4:*
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -c "import glob,os,re; [print(f'{p}: {m}') for p in glob.glob('docs/**/*.md',recursive=True)+glob.glob('*.md') for m in re.findall(r'\]\(([^)]+\.md)\)', open(p,encoding='utf-8',errors='replace').read()) if not m.startswith('http') and not os.path.exists(os.path.join(os.path.dirname(p),m))]"
```
Paste the full list. **Do not fix any of it.** It is an inventory for the leader.

---

## 7. Report

Write `agents/reports/2026-08-29_repo-reorganisation_REPORT.md`:

1. The **Baseline** block from §1, verbatim.
2. `git status --short` in full — every rename, so the leader can read the whole move as one list.
3. All six gate outputs, verbatim, including the two app launches.
4. The dangling-link inventory.
5. **Deviations.** Any file you moved that this brief did not name; any file this brief named that
   you did not move, and why; anything you edited beyond the four §5 targets. The correct answer to
   the last is "nothing".
6. One line confirming you deleted no file, and one line confirming no card field other than
   `sources` changed.

Then stop. Do not commit, do not push, do not start another brief.

---

## 8. What is explicitly NOT in scope

Say no to all of these if you find yourself drifting toward them:

- ❌ **Reorganising `backend/`, `frontend/`, `trainer/`, `docs/` internals, or `archive/`.** Only
  the root's markdown moves, into the destinations §3 names.
- ❌ **Writing a new plan, index, README, structure document or convention guide.** `state/MAP.md`
  already exists and §5.2 tells you to update it. Creating another is the project's documented
  failure mode — infrastructure that postpones the real work. `REPO_CLEANUP_PLAN.md` from
  2026-07-25 is being archived in this very brief for exactly that reason.
- ❌ **Deleting anything.**
- ❌ **Touching `applications/`.** It holds the AEON-UP material and it is already where Thejus
  wants it.
- ❌ **"Improving" any document you move** — no rewording, no reformatting, no fixing a typo, no
  updating a stale docstring.
- ❌ **Renaming any file.** Every file keeps its exact name; only its directory changes.
