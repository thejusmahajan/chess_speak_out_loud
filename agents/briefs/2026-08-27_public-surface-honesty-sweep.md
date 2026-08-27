# BRIEF — public-surface honesty sweep: kill the last HAMOCC, verify the dates, audit LinkedIn

**Filed:** 2026-08-27 by the leader
**Worker:** Gemini, in Antigravity
**Status:** ACTIVE

**Why this before the interview?** A panel reads the website and the LinkedIn profile. A
first-person claim to a model the CV never mentions is the kind of thing that gets probed in the
room, and it is cheaper to remove than to explain.

---

## 0. Read this before you touch anything

**Workspaces.** This brief spans two repositories. Both are already cloned.

| repo | path | branch |
|---|---|---|
| website | `C:\Users\Admin\Documents\thejusmahajan.github.io` | `main` |
| chess (this repo, for the report only) | `C:\Users\Admin\Documents\chess_speak_out_loud` | `windows-dev` |

**The standing contract in `agents/README.md` applies.** In particular:

- **Never invent a number, a line number, or a quotation.** A previous delivery on this exact
  website was audited and found **substantially fabricated** — it quoted a string that existed on
  no page and cited a line number that held different content. The standing rule that came out of
  it: **every quoted string must be reproduced by a `grep` whose output you paste.** If you cannot
  paste the grep, do not make the claim.
- **Scope is closed.** Touch only the files named in the steps below. If a step seems to require
  editing a file that is not named, **stop and ask** — do not improvise.
- **Do not commit and do not push.** Leave the working tree dirty. The leader audits the diff.
- Paste **real terminal output**, never a description of it or a reconstruction from memory.

**Terminal note.** The integrated terminal is now **PowerShell 5.1**. `&&` and `||` do not exist —
chain with `;` or `A; if ($?) { B }`. Do not use `Get-Content`/`Set-Content` to rewrite these
files: 5.1 reads as ANSI and writes UTF-8, which silently corrupts every `—` in them. Edit through
the IDE editor, or with Python using `io.open(..., encoding='utf-8')`.

**Background, so you know what "done" means.** On 2026-08-22 commit `eb8ecdc` removed five names
from the site — **ICON-O, HAMOCC, EERIE, Levante, DKRZ** — because each appeared in a first-person
experience claim while appearing in the CV **zero** times. The same commit aligned the M.Sc. date.
That work is done and is not to be repeated. **One residual survived it**, in a code block rather
than in prose, and that is Step 1.

---

## 1. Remove the last HAMOCC on the website

**File:** `blog-ggplot2-timeseries.html` — **one line only.**

The surrounding prose was already made generic ("simulated phytoplankton abundance data from
biogeochemical model output"). The code example below it still loads a file named after the model.

Change the filename in the `read_csv(...)` call from `hamocc_plankton_output.csv` to
**`plankton_output.csv`**.

**Constraints:**
- Change **only** the filename string. Do not touch the `mutate`, `filter`, or any `ggplot` line.
- Do not reflow, re-indent, or reformat the `<pre>` block. The diff for this step must be
  **exactly one line changed**.
- Do not rename the variable `plankton_df`.

### ✅ CHECKPOINT 1 — paste all three of these

```powershell
cd C:\Users\Admin\Documents\thejusmahajan.github.io
git diff --numstat blog-ggplot2-timeseries.html
git diff blog-ggplot2-timeseries.html
Select-String -Path *.html -Pattern "hamocc" -CaseSensitive:$false
```

**Pass condition:** `--numstat` reads exactly `1	1	blog-ggplot2-timeseries.html`, and the third
command returns **no matches at all**.
**If `--numstat` shows any other number, you changed more than the filename — revert with
`git checkout -- blog-ggplot2-timeseries.html` and redo it.**

---

## 2. Prove the other four names are gone

Run this exactly, and paste the whole output including the empty results:

```powershell
cd C:\Users\Admin\Documents\thejusmahajan.github.io
Get-ChildItem -Recurse -Include *.html,*.md,*.js,*.css |
  Where-Object { $_.FullName -notmatch '\\\.git\\' } |
  Select-String -Pattern 'hamocc','icon-o','eerie','levante','dkrz' -CaseSensitive:$false
```

### ✅ CHECKPOINT 2

**Pass condition:** **zero matches.** If anything matches, do **not** edit it. **Stop and report
the match with its file and line** — whether it is a real claim or an innocent coincidence is the
leader's call, not yours.

---

## 3. Verify the dates agree — read only, change nothing

Three places state the same two degrees. They must agree. **This step edits nothing.**

```powershell
Select-String -Path C:\Users\Admin\Documents\thejusmahajan.github.io\experience.html -Pattern '2012','2009','Calicut' -Context 1,1
Select-String -Path C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\cv_hereon_aeon_up.tex -Pattern '2012','2009'
```

**Expected, from the leader's own check on 2026-08-27:**

| degree | website `experience.html` | CV `cv_hereon_aeon_up.tex` |
|---|---|---|
| M.Sc. Physics, NIT Calicut | `2012 – 2014` | `07/2012 - 12/2014` |
| B.Sc., University of Calicut | `2009 – 2012` | `06/2009 - 04/2012` |

### ✅ CHECKPOINT 3

**Pass condition:** the pasted output matches the table — the site's year range is the year range
of the CV's month/year range, for **both** degrees.
**If either row disagrees, STOP.** Do not edit either file. Report the exact strings you found.
Which one is right is a question only Thejus can answer, and he has already answered it once.

---

## 4. LinkedIn — audit only, and only if the input exists

The same five names may appear on the LinkedIn profile, which nobody has checked. **You cannot
reach LinkedIn and you must not try.** The input is a file Thejus pastes himself.

**First, check whether it exists:**

```powershell
Test-Path C:\Users\Admin\Documents\job_search\linkedin_profile.txt
```

### ✅ CHECKPOINT 4a — the gate

- **If it returns `False`: STOP HERE.** Do not create the file, do not guess its contents, do not
  proceed to 4b. Report: *"LinkedIn audit blocked — `linkedin_profile.txt` not present. Thejus
  needs to paste his profile text into it: headline, About section, and every Experience and
  Education entry."* Then go to Step 5 and report everything else.
- **If it returns `True`**, continue.

**4b — the audit.** Compare the profile text against `cv_hereon_aeon_up.tex`. Report, as a table,
every item in **one** of these three categories:

1. **Names the CV does not contain** — run the Step 2 pattern over the file, plus any *other*
   named model, cluster, project or tool in the profile that does not appear in the CV.
2. **Date disagreements** with the table in Step 3, or with any employment date in the CV.
3. **First-person claims of experience** that the CV does not support.

**Rules for this step:**
- **Quote exactly, and paste the `Select-String` that produced each quote.** Same anti-fabrication
  rule as Step 0.
- **Report only. Edit nothing, and do not write a suggested replacement profile.** LinkedIn is
  edited by hand, by Thejus. Your output is the change list he works from.
- **Absence of a name from the CV is a flag, not a verdict.** Some entries will be legitimate
  things the CV simply had no room for. Say what you found; do not judge whether it is dishonest.

---

## 5. Report

Write to `C:\Users\Admin\Documents\chess_speak_out_loud\agents\reports\2026-08-27_public-surface-honesty-sweep_REPORT.md`.

Structure it exactly like this, and keep the two apart:

```
## What I changed
(the one-line diff from Step 1, pasted)

## Checkpoint output
(Checkpoints 1, 2, 3, 4a verbatim — real terminal output, nothing retyped)

## LinkedIn findings
(the Step 4b table, or the blocked message from 4a)

## Deviations
(anything you did differently from this brief, and why. "None" if none.)

## Opinions
(anything you think is wrong or worth doing that this brief did not ask for.
 Keep it out of the sections above.)
```

**Leave both repositories uncommitted.** The leader re-runs every checkpoint before accepting.
