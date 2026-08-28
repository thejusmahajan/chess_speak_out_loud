# research/

Briefs and returned reports for **external web-based research agents** — tools that run outside
this workspace, cannot read the filesystem, and are driven by hand.

Not to be confused with `agents/`, which is the Gemini-in-Antigravity loop. That worker reads the
repo directly; these do not, so a round here carries **copies** of everything it needs.

```
research/<subject>/research_NN/
    BRIEF.md      the prompt to paste
    inputs/       files to attach alongside it
    report/       the returned report, dropped in by hand
```

One directory per round. A follow-up round gets `research_02`, not an edit to `research_01` — the
brief that produced a report has to stay readable next to it.

Rounds that matter are registered in `agents/ACTIVE.md`, which remains the single ledger for all
delegated work regardless of which worker did it.
