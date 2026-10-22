# Gemini Work Order — Diagnose one failing frontend test

**Role:** You are the worker. Claude (orchestrator) ported this repo from Windows to Debian.
Everything is green except **one** frontend test. Find out why. This is a **diagnosis-first**
task: understand before you touch anything.

**Repo:** `/scratch/local1/chess_speak_out_loud` (branch `windows-dev`, already checked out)

---

## The failure

```bash
cd /scratch/local1/chess_speak_out_loud/frontend
npx vitest run src/components/Training/__tests__/RepertoireTrainer.test.tsx
```

→ `1 failed | 10 passed`. The failing case is **test 6**, around line 289:

```js
fireEvent.click(trainBtn);
await waitFor(
  () => { expect(screen.getByText(/Ply 1 \/ Depth 6/i)).toBeInTheDocument(); },
  { timeout: 4000 }
);
```

The click lands, the component re-renders, but the text `Ply 1 / Depth 6` never appears.
It fails **consistently** — it is not flaky. I re-ran it; same result both times.

## Context you need and should not re-derive

- The component under test is `frontend/src/components/Training/RepertoirePanel.tsx`.
- This is a **jsdom** test. There is no browser, no network, no filesystem in play.
- The other 10 tests in this same file pass, including ones that render the same panel.
- The repo was just moved Windows → Linux. **I do not believe this is a platform issue** —
  jsdom component tests have essentially no platform surface. Treat "it's because of Linux"
  as a hypothesis you must *prove*, not assume. My prior is that this test was already
  failing on the Windows box.

---

## What I want from you

**Phase 1 — Diagnose (do this before editing anything).**

Answer these three questions, with evidence:

1. What exact UI state *does* the panel reach after the click? (The vitest output dumps the
   rendered DOM — read it. Also add a temporary `screen.debug()` if useful.)
2. Where does the string `Ply N / Depth M` get rendered in `RepertoirePanel.tsx`, and what
   conditions must hold for that branch to render?
3. Which of those conditions is false, and why — trace it back to the mock data the test sets
   up at the top of test 6.

**Phase 2 — Classify.** State which one of these it is:

- **(a) Bad test** — the mock data is incomplete/wrong and the component is behaving correctly.
- **(b) Real component bug** — the component mishandles this input shape.
- **(c) Platform** — something genuinely Linux-specific. If you claim this, you must show the
  specific mechanism, not just "it works on Windows."

**Phase 3 — Fix, but only under this constraint.**

- If **(b)**, fix `RepertoirePanel.tsx`. Minimal diff.
- If **(a)**, fix the test's mock data so it exercises the intended path. You may **not** delete
  the test, weaken the assertion, add `skip`/`xfail`, or extend the timeout to mask it.
- If you cannot decide between (a) and (b) with confidence, **do not edit anything** — report
  your evidence and stop. A clear "here's what I found, here's what I'm unsure about" is worth
  more to me than a confident wrong fix.

**Phase 4 — Verify.** Whole frontend suite must be green, with no test lost:

```bash
cd /scratch/local1/chess_speak_out_loud/frontend && npm test 2>&1 | tail -15
```

Baseline before your change: **44 passed, 1 failed (45 total)**.
Target: **45 passed (45 total)**. If the total is not 45, you deleted or skipped something — undo it.

---

## Rules

1. **Do not touch anything outside `frontend/src/components/Training/`.** Not the backend,
   not the build config, not `package.json`, not git.
2. **Do not commit, branch, stash, or revert.** Working tree edits only.
3. **Do not `npm install` anything.** Deps are already correct.
4. **Do not refactor, rename, or reformat.** Minimal diff only.
5. **No `sudo`, no writes outside the repo.**
6. If you are about to spend effort on something not named in this document — stop and report
   instead.

---

## Report

Write your findings to `GEMINI_REPERTOIRE_REPORT.md` in the repo root. Be terse, no filler:

```
## What state the panel actually reaches
<evidence — the relevant slice of the rendered DOM>

## Where "Ply N / Depth M" renders and its conditions
<file:line, and the guarding condition>

## The condition that fails, and why
<trace to the test's mock data>

## Classification
(a) bad test / (b) component bug / (c) platform — pick ONE, justify in 2 sentences

## What I changed
<file:line diffs, or "nothing — insufficient confidence, see above">

## Suite result
<verbatim final line of `npm test`>

## What I am unsure about
<be honest here; this section is the most useful one to me>
```

Then stop.
