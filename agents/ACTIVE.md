# ACTIVE — what the worker should do now

**Worker: execute the topmost brief marked `ACTIVE`.** Follow it exactly, and follow the
standing contract in `agents/README.md` (scope limits, never invent a number, paste real
output, report deviations, stop and ask when the brief doesn't cover a decision).

---

## Live now

### 1. `briefs/2026-08-19_salience-cnp-brainstorm.md` — **ACTIVE** ← start here
Design/brainstorm. Attack the leader's hypothesis that a conditional neural process is the
right tool for the salience problem. Re-derive the leader's measurements first and
contradict them if they don't hold. Output: one report into `agents/reports/`.
**No production code.** Route: Antigravity — read the repo files it names.

### 2. `briefs/2026-08-18_cnp-synthetic-build.md` — **ACTIVE** (queued)
Implementation, in the **separate** `cnp_synthetic` repo. Build a conditional neural process
on synthetic data with an honest uncertainty evaluation. Self-contained; the canonical copy
sits in that repo. Handed over 2026-08-18 but never run — the worker was unavailable.

---

## Ledger

Every brief, its outcome, and the audit verdict. This is the forensic trail: when something
breaks later, the brief that specified it, the report that delivered it and the audit that
passed it are all findable from here.

| Brief | Target | Type | Status | Delivered | Audit verdict |
|---|---|---|---|---|---|
| `2026-08-19_salience-cnp-brainstorm` | chess_speak_out_loud | design | **ACTIVE** | — | — |
| `2026-08-18_cnp-synthetic-build` | cnp_synthetic | implementation | **ACTIVE** (queued) | — | — |

Status values: `ACTIVE` · `DELIVERED` (worker returned, not yet checked) · `AUDITED` (leader
verified — record the verdict) · `SUPERSEDED by <id>` · `ABANDONED`.

**`DELIVERED` never means done.** Nothing is believed until the leader has run the audit:
boundaries via `git status`, the **diff rather than the report**, the gate re-run
independently, the key guard mutation-tested, and the real path exercised on real data.
