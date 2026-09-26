# A file bus between the leader and the worker — Thejus's idea

**Origin:** Thejus, 2026-09-26, in session.
**Status:** PARKED by Thejus ("keep it for the future; we have other important things to finish").
Nothing built. No brief filed. Next step, when un-parked, is the pilot in §4 — not a build.

> **Section 1 is his words, unedited.** Everything after it is the leader's view and can be argued
> with. Section 1 cannot be edited.

---

## 1. The idea — 2026-09-26, verbatim

> We have worker agents in antigravity. But it is not possible to communicate with them as we don't
> have the api access. But I am thinking of an idea. We create a communication file that is
> accessible to both. The script for the worker agent is put into it. Beforehand I instruct the
> worker agent to execute whatever is in the execution file and it must wait and not close the
> session. The Claude agent, that is you, check the work and write another file. Gemini is
> beforehand instructed to execute this file when it reaches the disk. So when the waiting agent,
> gemini worker agent sees this it executes. This can be errors or checkpoints in the first brief and
> so on. So we have a consecutive execution policy defined. The worker agent is beforehand instructed
> to only stop its work when the a sentence like "everything is checked and write the final report"
> or something like that. For this to work, we need first to make the agent aware of the rules by a
> brief. Then when I say start to the agent, it will wail for the brief to reach the disk, executes it
> and produce what ever is taked to do. The claude agent, that is you, waits till the gemini work is
> on disk, verifies it and write another file which follows the gemini's policy. If gemini sees it it
> executes. By this way we can overcome the api deficiency.

In one line: Thejus stops being the hand-carried transport for every checkpoint; he carries one
protocol brief, says "start", and the spec → implement → audit loop runs through the disk.

---

## 2. Leader's verdict (2026-09-26): viable in principle, unproven in practice

**Mechanism.**
- **Gemini cannot "idle".** An agent's turn ends when it stops calling tools, so waiting must be a
  *blocking terminal command* — e.g. `python agents/bus/wait.py 0003` — that polls every few
  seconds, prints the file when it appears, and exits after a bounded time (~20 min) with
  `TIMEOUT — re-run me`. Bounded so an Antigravity command timeout cannot kill the loop silently.
- **The leader waits for free.** Same script in a Claude Code background Bash; its exit re-invokes
  the leader. No tokens spent while Gemini works.
- **Torn reads.** Write `.tmp`, then rename; every message ends with an end marker; the reader
  ignores anything without it. (Windows: rename can hit the AV `WinError 5` — retry, as in
  `store._write_json_atomic`.)
- **Ordering and record.** Monotonic numbered files (`0001_claude.md`, `0002_gemini.md`, …), never
  overwritten. The folder is the transcript Thejus reads afterwards.

**Two unknowns that decide it — neither verified:**
1. **Antigravity's terminal auto-run policy.** If every command needs Thejus's click, each wait
   needs him and nothing is gained. The wait command must be allowed to auto-run.
2. **Whether Gemini actually re-arms the wait** instead of ending its turn. Models end turns despite
   instructions. Failure mode is benign: Thejus types "continue" and we are back to today's workflow.

---

## 3. Guardrails required before any real use

- **Files are instructions, not scripts.** Gemini acts within the original brief's scope (listed
  files, listed commands). It never pipes bus content into a shell. Otherwise a leader mistake, or
  any stray write to the folder, can do anything in the repo.
- **Kill switch:** if `agents/bus/STOP` exists, both sides halt at once.
- **Round cap ~6**, then a fresh Gemini session: context growth degrades the worker, and an
  unattended loop spends leader tokens (borrowed money — see auto-memory) without Thejus seeing it.
- **Only the leader commits.** Gemini touches the working tree, never git.
- **Audit unchanged.** Automated transport does not make a worker report more trustworthy; the diff
  is still ground truth (CLAUDE.md non-negotiables 1, 4).
- **Cost of the idea:** Thejus no longer sees each hand-off, and he is the ground-truth oracle.
  The numbered log is the compensation — he skims it at the end of every run.

---

## 4. The pilot, when this is un-parked (~15 min)

Three rounds on a throwaway task under `temp/`: Gemini writes a file → leader returns a planted
"fix this error" → Gemini fixes → leader sends the stop sentence → final report.

**Pass:** zero human keystrokes between "start" and the final report, and no permission prompt.
**First action before the pilot:** Thejus checks Antigravity's terminal auto-execution setting.
Build order if it passes: protocol brief → `wait.py` → pilot brief.
