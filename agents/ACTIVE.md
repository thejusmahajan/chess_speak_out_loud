# ACTIVE — what the worker should do now

## ⚑ DEADLINE ITEMS — read this first, every session

| item | due | status |
|---|---|---|
| **AEON-UP application (Hereon, ref. 1056)** | **2026-09-03** | **NOT SENT** — materials corrected, verified, dated, on disk |

**Rules while any deadline item is `NOT SENT`:**
1. Its status is stated at the start of the session, before anything else. Not as a closing footnote.
2. **At most one non-deadline brief may be ACTIVE.**
3. Every new brief filed carries a one-line **"why this before the deadline item?"** — usually
   there is a good answer; the value is in having to write it.

*Why this block exists: a registry, a ledger, an audit protocol and three documents were built
while this item sat unsent. `COMMAND_BASE.md` warned about exactly that — "infrastructure that
postpones exposure" — and was read many times during it.*

---

**Worker: find the section below matching the folder you have open, then execute its topmost
brief marked `ACTIVE`.** Briefs target three different repositories, so which one you can do
depends on your workspace — do **not** simply take the first `ACTIVE` in the file.

Follow the chosen brief exactly, and follow the standing contract in `agents/README.md` (scope
limits, never invent a number, paste real output, report deviations, stop and ask when the brief
doesn't cover a decision).

Every brief and report path below is relative to
`C:\Users\Admin\Documents\chess_speak_out_loud\agents\`, wherever your workspace is rooted.
**All reports go there**, even for work done in another repo.

---

## Live now, by workspace

### If your workspace is `chess_speak_out_loud`

**1. `briefs/2026-08-19_knowledge-base-audit.md` — DONE, AUDITED, ACCEPTED.** Nothing to do.

**2. `briefs/2026-08-20_trainer-german-b2.md` — ACTIVE ← do this one**
German B2 (Goethe) ladders in the same trainer. **Part A first and blocking:** `user_rating` is a
single global scalar, so German mastery would inflate one number and start serving harder ML cards.
Per-ladder ratings, then the content. German content is the highest-fabrication-risk material this
trainer has carried — a learner cannot tell invented German from real German.

**3. TRAINER (ML side) — DELIVERED, AUDITED, ACCEPTED (both runs).** Level 0 is now served (400/400 draws
at rating 820) and the mathematics is restored and wired to render. **One open item needs Thejus,
not a worker:** open `http://127.0.0.1:8010`, reveal an `uncertainty` card, and confirm the
equations appear typeset rather than as raw `$$`. Nobody has seen the rendered output — the
worker's browser automation could not start.

**4. `briefs/2026-08-20_trainer-level-zero.md` — DELIVERED, AUDITED: content ACCEPTED, delivery blocked by the selector**

**3. `briefs/2026-08-19_trainer-content-repair.md` — DONE, AUDITED, ACCEPTED**
Repair the trainer's content. The engine passed audit; the content did not. A **fabricated DOI**
is cited 5 times (`gmd-12-4857-2019` does not exist; the real EPISODE-CityChem paper is
`gmd-12-3357-2019`, **by Matthias Karl — one of the hiring PIs**), and the do-not-claim gate
extracts **zero** patterns from the real file because it cannot parse a markdown table.

**3. `briefs/2026-08-19_knowledge-trainer-build.md` — DELIVERED, AUDITED: engine ACCEPTED,
content REJECTED.** Do not re-run; see brief 2.
The spaced-repetition interview trainer. **Unblocked**: the audit landed and its doctrine
corrections are applied. Read the brief's opening — three binding constraints (the real
do-not-claim file, the forbidden-source list, the corrected a8 frame). `job_search` is in the
workspace now, so the study room is readable and is preferred source material.

**3. `briefs/2026-08-19_attention-export-with-history.md` — QUEUED (WIP limit; the trainer is in flight)
Regenerate the attention JSON using **real move histories**. The previous export ran BT3 with
84 of its 112 input planes empty; the code was audited and accepted, only the data is wrong.
Three real master-game positions with full histories are pinned in the brief.

**4. `briefs/2026-08-19_attention-export-json.md` — SUPERSEDED (data) / AUDITED (code)**
Do not run. Its code is accepted and is reused by brief 3; only its output was rejected.

### If your workspace is `thejusmahajan.github.io`

**1. `briefs/2026-08-19_website-repoint-part2.md` — DONE, AUDITED, ACCEPTED.** Nothing to do.

**2. `briefs/2026-08-19_attention-demo-page.md` — BLOCKED**
The interactive attention page. Do **not** start until the regenerated export (chess-repo brief
1) is delivered **and the leader has audited it**.

### If your workspace is `cnp_synthetic`

**1. `briefs/2026-08-18_cnp-synthetic-build.md` — QUEUED (WIP limit)**
Build a conditional neural process on synthetic data with an honest uncertainty evaluation.
Self-contained; the canonical copy sits in that repo. Handed over 2026-08-18 but never run —
the worker was unavailable.

---

**Leader's priority, if asked:** the **trainer** is the single ACTIVE task; everything else is
QUEUED under the WIP limit until the deadline item ships or the trainer completes. The website
repoint is done; its remaining items are leader-owned copy, not worker briefs.

---

## Ledger

Every brief, its outcome, and the audit verdict. This is the forensic trail: when something
breaks later, the brief that specified it, the report that delivered it and the audit that
passed it are all findable from here.

| Brief | Target | Type | Status | Delivered | Audit verdict |
|---|---|---|---|---|---|
| `2026-08-19_attention-demo-page` | thejusmahajan.github.io | implementation | **BLOCKED** | — | — |
| `2026-08-19_knowledge-base-audit` | chess_speak_out_loud | design/audit | **AUDITED** | `reports/…_REPORT.md` | **ACCEPT** — best worker design deliverable to date. Every spot-check held: **CV_AI_MODULE said black-to-move index 0 = h8, actually a8** (code does `^56`, rank-flip only) in the *lead-with-this* interview story; `INFERENCE_PRIORS` violates the Bible's own no-hand-coded-salience rule; "pilot validated the method" is false (measured 0/35); `HOW_TO_RUN` claims requirements.txt is empty (36 lines); Bible states 200 AND 239 tests (actual 302). Honestly declared it could not reach `job_search` — **that gap hid a live do-not-claim violation in the submittable CV ("mechanistic interpretability"), found and fixed by the leader.** See `…_AUDIT.md` |
| `2026-08-20_trainer-german-b2` | chess_speak_out_loud | engine + content | **ACTIVE** | — | — |
| `2026-08-20_trainer-render-math` | chess_speak_out_loud | implementation | **AUDITED** | `reports/…_REPORT.md` | **ACCEPT.** KaTeX 0.18.4 vendored locally (60 font files incl. woff2), served with no runtime external fetch. Restoration verified against `1560992`: **382 `$` delimiters vs 234 pre-strip, and ZERO cards that had maths then have none now** — merged per card, so Level 0 and the re-levelling survive. `unc-l3-003` carries the full Law of Total Variance; `pyt-l0-007` kept the plain-English misconception fix **and** gained the softmax formula. Both new gates mutation-verified (unbalanced `$` → exit 1; `\label` → exit 1). `renderMath()` fires on card load **and inside `revealAnswer`**. **NOT verified: actual typeset output** — Playwright 404'd; honestly disclosed. See `…_AUDIT.md` |
| `2026-08-20_trainer-level-progression` | chess_speak_out_loud | implementation | **AUDITED** | `reports/…_REPORT.md` | **ACCEPT.** Re-measured independently against the real `progress.json`: rating 1055.6 → **820**, and **400/400 draws now serve Level 0** (was `{1: 400}`), spread across all five ladders. Suite 11 → **17 passed**. |
| `2026-08-20_trainer-level-zero` | chess_speak_out_loud | content | **AUDITED** | `reports/…_REPORT.md` | **CONTENT ACCEPT / FEATURE UNREACHABLE.** 18 Level-0 cards (780–840), genuinely elementary and matched to his verbatim comments — the logits card literally answers "are they probabilities in percent?" with "they do NOT sum to 1 or 100%". **All LaTeX gone** (0 of 78 cards contain `$`), which was his actual complaint. Deep-Ensembles card correctly promoted L1→L3. Prerequisite gating verified **behaviourally**: locked for a new user, unlocked after a 1.0, still locked after only a 0.5. **BLOCKING: the selector never serves Level 0** — his rating 1055.6 gives a 905–1205 window, Level 0 is 780–840, and 400/400 simulated draws returned Level 1. Leader spec error (Elo band across the pool competes with the ladder). Fixed by `…_level-progression`. See `…_AUDIT.md` |
| `2026-08-19_trainer-content-repair` | chess_speak_out_loud | content repair | **AUDITED** | `reports/…_REPORT.md` | **ACCEPT.** Both CRITICALs fixed and verified independently: the fabricated DOI `gmd-12-4857` is gone (0 occurrences) and the do-not-claim loader now parses the real file's markdown table — **5 patterns from the real file**, hardcoded fallback deleted, and mutation-tested to raise `FileNotFoundError` on a missing path. No card has a sole non-external source. **MEDIUM concern:** `gmd-12-3357` now appears on 9 of 12 air-quality cards, close to the blanket substitution the brief forbade — plausible for dispersion/street-canyon claims, thin for 'what is an emission inventory'. Not fabricated; weakly apposite. See `…_AUDIT.md` |
| `2026-08-19_knowledge-trainer-build` | chess_speak_out_loud | implementation | **AUDITED** | `reports/…_REPORT.md` | **ENGINE ACCEPT / CONTENT REJECT.** Engine sound: 9 tests pass, gate mutation-tested twice (exit 1 on unsourced card and on dead path), boundaries clean, 60 cards as specced. Constraint (c) handled well — all `h8` mentions sit in `trap` fields as the wrong answer. Constraint (b) clean. **CRITICAL 1: `10.5194/gmd-12-4857-2019` does not exist** (404 via doi.org AND via GMD) yet is cited on 5 of 12 air-quality cards, sole external source on 4 — the real paper is `gmd-12-3357-2019` **by Matthias Karl, a hiring PI**. **CRITICAL 2: the do-not-claim gate extracts ZERO patterns from the real file** (it parses `- ❌` lines; the real file uses a `| ❌` table) — all 4 came from in-repo `CV_AI_MODULE.md`, i.e. the paraphrase the brief forbade, with a silent fallback. **HIGH: `SESSION_LOG_2026-08.md` is the most-cited source (24/125); 18/60 cards have no external source.** See `…_AUDIT.md` |
| `2026-08-19_attention-export-with-history` | chess_speak_out_loud | implementation | **QUEUED** (WIP limit) | — | — |
| `2026-08-19_attention-export-json` | chess_speak_out_loud | implementation | **AUDITED** (code) / **SUPERSEDED** (data) | `reports/…_REPORT.md` | **ACCEPT CODE, REJECT DATA** — frame verified independently against a live `saliency_absolute` call to 0.0005 (quantisation error) incl. black-to-move; row sums 0.994–1.005 so axes are not transposed; suite 302p/5s reproduced; model presence honestly reported. **But the brief pinned `history_ucis=None`**, running BT3 with 84 of 112 planes empty — measured max diff **0.48**, correlation 0.85, top squares change. Leader error. Data regenerated by `…_with-history`. See `…_AUDIT.md` |
| `2026-08-19_website-repoint-part2` | thejusmahajan.github.io | implementation | **AUDITED** | `reports/…_REPORT.md` | **ACCEPT** — all 5 gates pass on independent re-run; clinical contact paragraph now on **0** pages; **every one of the 15 blog posts changed exactly 2 lines, all in the contact block** (grep for non-footer changed lines returns 0), so no article text moved; meta description replaced; GOTM-FABM + observational validation restored; `&amp;` fixed; all internal links resolve. Worker **corrected a leader error in the gate spec** (21 pages, not 20 — index.html was already done in part 1) instead of forcing the number. See `…_AUDIT.md` |
| `2026-08-19_website-repoint-aeon-up` | thejusmahajan.github.io | implementation | **AUDITED** | `reports/…_REPORT.md` | **ACCEPT (task incomplete — leader spec errors)** — copy applied verbatim, nothing invented, gates pass, real internship date preserved. Worker correctly reported a leader spec error and refused to write copy it wasn't given. Gaps, all leader's: clinical footer on **20** pages not 4; meta description untouched; GOTM-FABM + "validated against observational data" lost in the card swap; bare `&` in title. Closed by `…_part2`. See `…_AUDIT.md` |
| `2026-08-19_salience-temporal-frame-fix` | chess_speak_out_loud | implementation | **AUDITED** | `reports/…_REPORT.md` | **ACCEPT** — boundaries clean; suite 297p/5s reproduced independently (290 baseline + 7 new); **2 mutations each killed 2 guards** so the tests are real; witness fixed on the real path; §6 obeyed (grep: zero scoring changes); SAN prefix does **not** contaminate prose alignment. See `…_AUDIT.md` |
| `2026-08-19_salience-cnp-brainstorm` | chess_speak_out_loud | design | **AUDITED** | `reports/…_REPORT.md` | **ACCEPT WITH CORRECTIONS** — Part 0 re-derivation exact; §1.1/1.2/1.3/5.2/5.4 confirmed; **§5.3 confirmed = real bug** (move delta discarded in `rank_salient_facts`). **§1.4 FALSE** (235,511 `quietMove` puzzles; 27.3% of band `quiet_first`). **§5.5 right number, wrong cause** — do NOT relax the provenance invariant. Part 4 metric not measurable as specified. See `…_AUDIT.md` |
| `2026-08-18_cnp-synthetic-build` | cnp_synthetic | implementation | **QUEUED** (WIP limit) | — | — |

Status values: `ACTIVE` · `DELIVERED` (worker returned, not yet checked) · `AUDITED` (leader
verified — record the verdict) · `SUPERSEDED by <id>` · `ABANDONED`.

**`DELIVERED` never means done.** Nothing is believed until the leader has run the audit:
boundaries via `git status`, the **diff rather than the report**, the gate re-run
independently, the key guard mutation-tested, and the real path exercised on real data.
