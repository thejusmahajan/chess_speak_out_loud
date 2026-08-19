# ACTIVE — what the worker should do now

**Worker: execute the topmost brief marked `ACTIVE`.** Follow it exactly, and follow the
standing contract in `agents/README.md` (scope limits, never invent a number, paste real
output, report deviations, stop and ask when the brief doesn't cover a decision).

---

## Live now

### 1. `briefs/2026-08-19_website-repoint-aeon-up.md` — **ACTIVE** ← start here
Repoint the personal site from clinical bioinformatics to environmental modelling + ML,
ahead of the AEON-UP deadline (3 Sept). **Open the `thejusmahajan.github.io` folder as the
workspace, not this repo.** All copy is written by the leader — the worker applies it and
must invent no biographical detail. Blog posts are out of scope entirely.

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
| `2026-08-19_website-repoint-aeon-up` | thejusmahajan.github.io | implementation | **ACTIVE** | — | — |
| `2026-08-19_salience-temporal-frame-fix` | chess_speak_out_loud | implementation | **AUDITED** | `reports/…_REPORT.md` | **ACCEPT** — boundaries clean; suite 297p/5s reproduced independently (290 baseline + 7 new); **2 mutations each killed 2 guards** so the tests are real; witness fixed on the real path; §6 obeyed (grep: zero scoring changes); SAN prefix does **not** contaminate prose alignment. See `…_AUDIT.md` |
| `2026-08-19_salience-cnp-brainstorm` | chess_speak_out_loud | design | **AUDITED** | `reports/…_REPORT.md` | **ACCEPT WITH CORRECTIONS** — Part 0 re-derivation exact; §1.1/1.2/1.3/5.2/5.4 confirmed; **§5.3 confirmed = real bug** (move delta discarded in `rank_salient_facts`). **§1.4 FALSE** (235,511 `quietMove` puzzles; 27.3% of band `quiet_first`). **§5.5 right number, wrong cause** — do NOT relax the provenance invariant. Part 4 metric not measurable as specified. See `…_AUDIT.md` |
| `2026-08-18_cnp-synthetic-build` | cnp_synthetic | implementation | **ACTIVE** (queued) | — | — |

Status values: `ACTIVE` · `DELIVERED` (worker returned, not yet checked) · `AUDITED` (leader
verified — record the verdict) · `SUPERSEDED by <id>` · `ABANDONED`.

**`DELIVERED` never means done.** Nothing is believed until the leader has run the audit:
boundaries via `git status`, the **diff rather than the report**, the gate re-run
independently, the key guard mutation-tested, and the real path exercised on real data.
