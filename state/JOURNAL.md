# JOURNAL — append-only session log

Newest first. One block per session. The purpose is that a restart never re-derives what a
previous session already established. Append; never rewrite a past entry — if it turns out to
be wrong, say so in the new entry and leave the old one visible.

Template:
```
## YYYY-MM-DD — <one-line title>
**Did:** ...
**Found:** ...
**Decided:** ...
**Open:** ...
**Repo:** commits, and whether they were PUSHED (verified, not assumed)
```

---

## 2026-08-31 — eight comments read; the `own_work` L0 cards teach a story, not a mechanism

**Did:** read the comment queue via the new `CLAUDE.md` Step 0 item 5 (42 entries, 8 unread since
the last triage). Wrote the Ramacher round-table document he asked for — **to the PRIVATE repo**,
`bioinformatics_project/job_search/.../study_room/18_ramacher_roundtable.md`, commit `14b8354`,
pushed. It is career material and §0 says that leaves this repo, not enters it.

**Found — and on the first point he is right and the cards are wrong:**
- **`own-l0-007` and `own-l0-008` assert claims their cited sources do not contain.** The head
  card says 24 heads "track 24 distinct concepts" and illustrates with *"Head 1 tracks diagonal
  bishop pin lines, Head 2 tracks open file control…"*; the layer card splits 1–4 local / 5–10
  tactical / 11–15 strategic. **Grepped `docs/writeup_attention_frame_bug.md`: neither claim is
  in it.** Invented illustrations wearing the word "Example:", in cards about his OWN work.
  **Fifth fabrication-class defect on record, and the first inside material he would say aloud
  about his own research.** Heads are known to be polysemantic; his own objection —
  *"isn't it just weights independently initialised and adjusted by gradient descent?"* — is more
  correct than the card.
- **What is real, and the cards withheld it:** `backend/neural_vision.py:302` is
  `stacked = torch.stack(attention_tensors)  # [15, N, 24, 64, 64]`. 15 layers, 24 heads,
  **64×64**. His question *"is this like a 64×64 matrix?"* has a one-line answer sitting in his
  own code, and `own-l0-005` hid it because it was authored "without mathematical matrices".
- **`own-l0-006` never says what the *self* in self-attention means** (Q, K and V from the same
  token set). He asked exactly that.
- **No card anywhere defines what a Gaussian Process IS.** `neural_processes` L0 has capacity,
  kernel, parametric-vs-non-parametric; the first GP card is **L1, "Gaussian Processes & kernel
  scaling"** — the properties before the object. He wrote *"I don't know what a Gaussian process
  is either."* That is the ladder's fault, not his.

**Why the GP gap is urgent and not cosmetic:** the abstract he supplied shows **Ramacher's own
method list is "XGBoost and Gaussian Processes"**. The interviewer uses the object the candidate
cannot picture, and the candidate has *built* its deep-learning cousin.

**Corrected a memory that could have cost the interview.** The `MEMORY.md` index line read
"4.42x CRPS vs the GP oracle", which compresses to something that sounds like a win. It is the
CNP being **4.42× worse** than the exact GP posterior, and `RESULTS.md` says that is the correct
outcome because beating it would indicate a context/target leak. Index line rewritten with the
direction and the warning explicit. The memory body was already right.

**Verified:** every number in the new document grepped against its source before commit —
11 figures against `cnp_synthetic/RESULTS.md`, the EPISODE-CityChem quote against GMD 12,
3357–3399, the ferryboat ranges against the Europe PMC record. The moved-road experiment I lean
on is committed at `db3eb90`, not just working-tree.

**Open:**
1. **The five `own_work` L0 cards are not yet rewritten** — the defect is diagnosed, not fixed.
2. **No L0 Gaussian-Process card yet.** Highest-value single gap in the trainer.
3. **`cnp_synthetic` has 5 modified files and an untracked `REFEREE_REPORT.md`**, unchanged for
   four days. That repo is screen-share material. The moved-road result is safely committed, but
   the referee report — which holds the mutation tests — is not in git at all.

**Repo:** this entry + memory correction. The round-table document is in the private repo.

---

## 2026-08-30 (night) — the LLM seam is closed; the brief understated its own defect three ways

**Did:** executed `agents/briefs/2026-08-27_llm-seam-removal.md` in full. Report:
`agents/reports/2026-08-27_llm-seam-removal_REPORT.md`.

Deleted `backend/training/explanations.py`, its 12 tests, and the 16-entry poisoned cache.
Removed the unused `generate_conversation` import and **both** `enrich_tree_explanations` call
sites from `backend/app.py`. Dropped the generated-prose branch from `RepertoirePanel.tsx` so the
Coach Explanation card renders only LC0-derived values. Corrected `HOW_TO_RUN.md:90` and
`docs/plans/ARCHITECTURE.md` (line 30 **and** the mermaid edge, which the brief did not name).
Created `backend/tests/test_llm_seam.py`: a static `ast` guard plus a behavioural test.

**Found — the brief's own evidence was understated three ways, all in the same direction:**
- **Two call sites, not one.** `app.py:659` *and* `app.py:745`. The second is the repertoire
  **drills** endpoint — generated text was being served into drill reveals and nobody had it
  written down.
- **The filler was on 9 of 16 cache entries, not four.** 8 distinct EPDs.
- **The other 7 entries are real Gemini output, truncated mid-word.** The fallback template always
  ends with its fixed sentence, so those did not come from it. **The app had genuinely called a
  language model and served its chess text.** That is a stronger violation than anything written
  down before tonight.

**Found and deliberately NOT fixed** (the brief asks for exactly this): `kaggle_files/` is a
complete 64-file clone of `backend/` frozen 2026-07-21, carrying both call sites and its own
`llm_client.py`. Gitignored, local-only, unreachable from the served app, and outside the
interlock's walk. Recommendation recorded: regenerate from HEAD rather than patch the snapshot.

**Verified:**
- Null test on HEAD before touching anything: `grep -c "sound piece activity" … = 9`.
- **`301 − 12 + 2 = 291`.** It balances. Frontend `vitest`: 9 files, 49 tests, all green,
  including `RepertoireTrainer.test.tsx` which mounts the edited panel.
- **Mutation test — and the first attempt failed usefully.** I inserted the import above a
  `from __future__` line, making a SyntaxError, and pytest died at *collection* instead of the
  guard going red. That exposed a real flaw in my own test: it imported fixtures at module scope,
  so a broken backend module took the guard down with it — exactly when you need it most. Moved
  those imports inside the behavioural test. Re-run correctly: guard goes **red naming
  `backend	raining\select_repertoire.py`**, revert is byte-identical, green again.

**⚠ Open, and stated plainly:**
1. **No independent audit.** The leader wrote this diff and the leader checked it. An audit brief
   for Gemini against it is cheap and legitimate.
2. **Nobody has looked at the Coach Explanation card in a browser.** Fourth instance of the
   standing failure in this repo's history. Vitest is not a pair of eyes.
3. `llm_client.py` targets `gemini-3.5-flash`, **not a real model**, on a deprecated SDK. Whoever
   builds the *translator* rewrites it; it is not usable scaffolding today.
4. Why the 7 cached generations truncate at 25–37 chars against `max_output_tokens=180` is
   unexplained, and the cache is deleted — the evidence now exists only in the report.

**Context:** this is the first code change to `backend/` since **2026-08-19** (`74724c3`); the
eleven days between were docs, archiving and the interview. The north-star frontier
(`docs/plans/PLAN_SALIENCE_CNP.md` Stage 0, repairing the label pipeline) is untouched and is the
next real piece of work.

**Repo:** one commit on `windows-dev`. PUSHED — verified.

---

## 2026-08-30 (evening, third) — his trainer comments went unread for ten hours; one was a real bug

**Found — and this is a leader failure, not a worker one:**
- `trainer/state/comments.jsonl` was **modified in the working tree when this session started**,
  and the leader committed it twice without reading a single line. The comment box in the app
  says feedback goes *"directly to the leader's audit queue"*. There was no queue. Six comments
  from 2026-08-30, the oldest sitting **ten hours**.
- **`CLAUDE.md` Step 0 now routes to it as item 5**, with the one-liner that prints the tail.
  Nothing else would have caught this: it is not in NOW.md, not in the JOURNAL, not in MAP.md.

**His comment [5] was a correct bug report — "I don't see the question here!" (her-l4-013):**
- He was right. The question he had to answer — *"have you worked with EPISODE-CityChem?"* — was
  in the small `topic` pill, and the `question` field held only a stage direction,
  *"Answer, in the exact register required."* Unanswerable on its own.
- **Five cards had drifted this way**, all in `hereon-aeon-up`: her-l3-010, her-l4-006, -009,
  -012, -013. All five rewritten so the question he will actually be asked is in the question
  field. 5 lines changed, 5 added — no reformat.
- **New gate in `verify_cards.py`:** if a topic quotes a question, that question must also appear
  in the question field. Mutation-checked (reverting her-l4-013 → gate goes red), and it earned
  its keep immediately by catching **her-l3-010, which the leader's own ad-hoc scan had missed**.
  That fifth card was borderline — its question paraphrased the quoted one in full — and the
  choice was made to conform the card rather than weaken the gate.
- Full gate: **206 cards, 87 URLs, 0 errors.** 75 tests pass.

**Two of his questions were folded back into the cards, not just answered in chat:**
- **[2] "why is it both Lagrangian and Eulerian? I am guessing it is Eulerian."** He is right about
  the flagship models, and the honest answer is better than that: **Karl's own model is a hybrid.**
  Fetched and quoted from the source the card already cites — *"EPISODE consists of a 3-D Eulerian
  grid CTM that interacts with a sub-grid Gaussian dispersion model for the dispersion of
  pollutants emitted from both line and point sources"* (Karl, Walker, Solberg **and Ramacher**,
  Geosci. Model Dev. 12, 3357–3399, 2019) — HIWAY-2 for line sources, SEGPLU for point sources,
  100 m over Hamburg. Added to `aq-l1-001`'s explanation. **Both his interviewers are on that
  paper.**
- **[1] the GOTM-FABM analogy** — yes, structurally. Same advection-diffusion-reaction equation
  with the biogeochemical source/sink term swapped out. Recorded on the same card **with the
  boundary attached**: the numerics transfer, the reaction term does not, and that is exactly
  what her-l4-012 forbids him to claim.
- **[4] "what is in this paper"** (the ferryboat study) — abstract fetched via Europe PMC and the
  numbers quoted into `her-l3-011`: *"1.5–3 × 10⁴ cm⁻³ at ferryboat piers and at the road traffic
  locations"* against an urban background of *"0.4–1.2 × 10⁴ cm⁻³"*, sub-50 nm dominated.
  MDPI returned 403; Europe PMC was the route that worked.

**Answered in chat, no card change needed:**
- **[3] "predicting a Gaussian instead of a number"** — right, and the `uncertainty` ladder already
  carries the refinement (8 cards mention aleatoric/epistemic; `unc-l0-002`, `unc-l1-001`,
  `unc-l3-003` are the spine). No gap to fill.
- **[6] he "almost forgot" `her-l5-003`** — that is the **slide-7 centrepiece**, the bug-admission
  slide. A level-5 card he half-forgot with the interview live is the one to re-drill first.

**Also:** ⚑ **Thejus confirmed the schedule bar renders** — *"The bar is running."* That closes the
open item from the two entries above, and the **fourth** instance of the standing failure
(correct work left unlooked-at). A person looked at the screen. That is still the only thing that
ever catches it.

**Repo:** one commit on `windows-dev`. PUSHED — verified.

---

## 2026-08-30 (evening, second) — "should I keep a tab open?" exposed a double-alarm, now fixed

**Did:**
- Answered the question: **no, the tab is optional.** Open the trainer when studying, close it
  after; the daemon owns the alarms.
- **Fixed the defect the question exposed.** With a tab open, the daemon and the page both fired
  at the same instant — every alert arrived doubled. The daemon's cursor file is rewritten every
  few seconds, so its freshness is a heartbeat; new endpoint **`/api/schedule/daemon`** exposes
  it, and the page now stays **silent while the daemon is alive**. The arm button reports which
  of the two is covering him (`🖥️ Desktop alarm active` / `🔔 Tab alarm armed` / `🔔 Enable alarm`).
  Re-checked every 15 s, and an unreachable server counts as *not covered* — it errs toward making
  a noise, never toward silence.
- **Hardened the daemon against this repo's own documented failure.** `write_cursor` did a bare
  `os.replace` once per second; on this machine AV/indexer holds intermittently deny that with
  **WinError 5**, which would have killed the 24/7 process outright. It now retries four times,
  and on final failure warns once and carries on. Log appends are wrapped the same way. Writes
  throttled 1 s → 3 s (~86k replaces a day → ~29k, each one fewer chance at the race).

**Verified:**
- **75 tests pass** (6 new, via `TestClient` with `STATE_DIR` monkeypatched to a tmp dir).
  Two more mutation checks, red then restored: treat a future heartbeat as alive → 1 red;
  a corrupt/missing heartbeat reads as alive → 2 red.
- **Live, both directions:** `{"alive":true,...,"age_seconds":0.2}` with the daemon running;
  33 s after killing it, `{"alive":false,...,"age_seconds":32.9}`.
- **The page's silence rule asserted in a node VM**, 6/6: daemon-alive → 0 plays for a work
  boundary and for the wake-up; daemon-gone → 1 play each; into-rest stays silent either way
  (it is a quiet kind, which has nothing to do with the daemon). The earlier 45/45 engine
  cross-check still passes after the edit.
- Daemon restarted on the hardened code — **PID 4820**, heartbeat carrying its pid.

**Open:** unchanged — **nobody has looked at the browser bar render.** Fourth instance of the
standing failure; the fix is one person, one glance.

**Repo:** one commit on `windows-dev`. PUSHED — verified.

---

## 2026-08-30 — the timetable is now part of the Knowledge Trainer, and it runs without a browser

**Did:**
- Built the day timetable Thejus dictated into the Knowledge Trainer as a first-class feature,
  in four pieces:
  - **`trainer/content/timetable.json`** — the 24 blocks as editable data, not code. Validated
    at load: the blocks must tile the full 24 h, one block may wrap midnight, a gap is a hard
    error naming both sides of it.
  - **`trainer/schedule.py`** — the pure engine. No clock of its own; every function takes `now`,
    so all of it is deterministic under test.
  - **`trainer/schedule_daemon.py`** — the 24/7 process. Always-on-top Tk banner +
    `winsound.Beep` alarm. **This is the reliable half; the browser is the convenience.**
  - **`trainer/static/index.html`** — a live bar under the header (current block, progress track,
    countdown, what's next) that fires the same reminders as an overlay + system notification.
- Endpoints `/api/schedule`, `/api/schedule/now`, `/api/schedule/reminders`.
- `launch_schedule.bat` / `stop_schedule.bat`; the daemon also starts from
  `launch_knowledge_trainer.bat`, so one double-click gives him cards *and* the clock.

**Decided (the reminder doctrine — this is the whole design):**
- **One reminder per boundary, five minutes before it.** The "session ending" notice and the
  "next session starting" notice are the *same event*; announcing both would double every alert
  in his day. He asked for both and gets both, in one message.
- **It sounds only when the block STARTING at that boundary is not rest/sleep.** That is exactly
  his rule — silence when a session ends because he is concentrating, alarm when a break ends
  because that is when he needs pulling back — and it falls out of one line of code rather than
  a table of special cases.
- **The 03:00 wake-up alarm fires at 03:00, not 02:55.** A five-minute lead on a wake-up wakes
  him five minutes early; `start_alarm` suppresses the lead for that block.
- Two gaps in the dictated timetable were filled rather than left silent: **04:15–04:30 as Rest**
  (unstated in the original) and **22:00–03:00 as Sleep**. Both are one-line edits in the JSON.

**Verified (not reported — run):**
- **69 tests pass** (`trainer/tests`, 37 of them new). **Five mutation checks**, each confirmed
  red then restored green: invert the quiet-kind sound rule → 5 red; drop the contiguity check
  → 2 red; wake-up gets a lead instead of a start alarm → 1 red; make the firing window
  inclusive at both ends → 1 red; block containment half-open → closed → 2 red.
  A sixth mutation appeared to survive and did not: I had written it at the wrong indentation,
  so it patched nothing. Re-applied correctly, it went red.
- **The live daemon fired all three reminder shapes** against synthetic timetables whose
  boundaries landed in the next two minutes: `19:14 ALARM (wake, at-start)`,
  `19:15 silent (into rest)`, `19:16 ALARM (out of rest, into work)` — with the matching
  `state/schedule_log.jsonl` lines. This is the path that matters and it was not assumed.
- **All three endpoints answered a live uvicorn**, and `/api/state` still answers unchanged.
- **The browser JS was cross-checked against the Python engine** — the page recomputes the
  schedule from the device clock rather than trusting the server, so the two implementations
  could drift. Ran the page's own script in a node VM against the real timetable:
  **45/45 assertions matched** (current + next block at 10 probe minutes, all 24 boundaries,
  and the sound decision at each).

**Open:**
- **The browser bar has not been looked at.** Its logic is verified and its markup parses, but
  nobody has seen it render. Load `http://127.0.0.1:8010/` and click **🔔 Enable alarm** once —
  browsers refuse audio until a user gesture, so until that click the overlay is silent.
- **For the 03:00 alarm to exist, something must have started the daemon before 03:00.** Nothing
  does that yet: put a shortcut to `launch_schedule.bat` in `shell:startup`.
- **⚠ This adds to the public footprint §0 is trying to shrink.** `timetable.json` publishes his
  daily routine — wake time, "Interview prep" twice a day, German, the mech-interp slot — in a
  repo that stays public. It is far milder than what §0 already lists, and `trainer/` is already
  on the §0b removal list, so the timetable rides out with it. Flagging it, not blocking on it.

**Repo:** one commit on `windows-dev`. PUSHED — verified with `git status` reporting nothing ahead.

---

## 2026-08-28 (third session) — the "Claude keeps crashing" triage: it was the machine, not the tool

**Did:**
- Triaged repeated Claude Code crashes. Four hypotheses were on the table — cmd environment /
  PATH overflow, overlapping plugins, the Bun-compiled native binary, and cmd-vs-PowerShell.
  Measured all four instead of guessing.
- Switched the Antigravity IDE default terminal profile to PowerShell and set
  `terminal.integrated.gpuAcceleration: "off"`
  (`~/AppData/Roaming/Antigravity IDE/User/settings.json`, backup `.bak-20260828`).
- Set `DISABLE_AUTOUPDATER=1` and `cleanupPeriodDays: 20` in `~/.claude/settings.json`
  (backup `.bak-20260828`).
- Corrected the **The terminal** section of `CLAUDE.md` and added a crash-triage note to it.

**Found:**
- **Three of the four suspects are false, with numbers.** Machine PATH 764 + User PATH 635 =
  **1400 chars** against an 8191 limit, whole environment block 5.2 KB of 32 KB — no overflow.
  **Zero plugins enabled**; `~/.claude.json` has no `enabledPlugins` key, only the official
  marketplace catalog cached on disk. And there is **no `claude.exe` crash dump, no WER report,
  and no Application-event-log entry** for claude, bun or node — so nothing supports the Bun
  theory either. The `/cmd` seen in PATH is `C:\Program Files\Git\cmd`.
- **The machine was crashing, not Claude Code.** System log for the day: `Kernel-Power`
  **Event 41** at 11:12:50 — *"the system has rebooted without cleanly shutting down"*;
  `Display` **Event 4101** at 18:39:08 — *"Display driver igfx stopped responding and has
  successfully recovered"*; a `dwm.exe` AppCrash at 17:48; archived `Kernel_139` and `Kernel_1e`
  reports. When dwm or the Intel iGPU resets, the IDE window and its integrated terminal go with
  it, and that presents as the agent dying.
- **The native updater hot-swapped the binary mid-session**, 2.1.250 → 2.1.251 at 18:05:30,
  leaving `claude.exe.old.1787940330363` (226 MB) beside the new 217 MB exe while sessions were
  open.
- **`CLAUDE.md` asserted a state that was never true.** It has claimed since 2026-08-27 that the
  integrated terminal was switched from `cmd` to PowerShell. The IDE setting was still
  `"Command Prompt"` today, so every session since has run the TUI in legacy conhost. Same
  failure class as the 2026-08-27 finding that `LEADER_BIBLE.md` §6 claimed "everything pushed"
  while 35 commits sat unpushed: **a document asserting a state nobody verified on disk.**
- 78 MB of session transcripts for this project alone, one file at 23.5 MB. Disk C is down to
  20.4 GB free of 218.6 GB.

**Decided:**
- **Do not migrate to the Node/npm build.** It was the obvious "bypass Bun" move and it is
  staged (`npm i -g @anthropic-ai/claude-code`; Node v24.13.1 and npm 11.8.0 are both present),
  but no evidence implicates the native build, and it would additionally need
  `~/.local/bin/claude.exe` renamed so it stops shadowing the npm shim on PATH. Holding it as
  the fallback if crashes survive the driver update — changing the toolchain on a hunch is how
  an afternoon disappears.
- Left the one stray empty entry (`;;`) in the User PATH alone. It is cosmetic, and rewriting a
  persistent PATH for no measured gain is not worth the risk.

**Open:**
- **Thejus must update the Intel graphics driver.** This is the top item and cannot be done from
  here. The igfx TDR is the leading suspect and is untreated.
- The PowerShell + GPU-acceleration change **needs an IDE restart** to take effect.
- Needs admin: Defender realtime is on with no exclusions for `C:\Users\Admin\.local\bin` or
  `C:\Users\Admin\.claude`. Given the recorded `WinError 5` history on atomic writes
  (`store._write_json_atomic`), these are worth adding.

**Repo:** `CLAUDE.md` and this file. Not yet committed at time of writing.

---

## 2026-08-28 — the job_search fork resolved; H1–H5 written; the deck is built

**Did:**
- **Reconciled the two `job_search` repos and pushed.** Fast-forwarded the remote-backed clone to
  `origin/master`, laid the newer working copy on top, verified superset and zero deletions, and
  pushed. Canonical clone is now `Documents\bioinformatics_project\job_search\`;
  `Documents\job_search` carries a `RETIRED_READ_THIS_FIRST.md`.
- **Wrote H5, H4, H3** as study room files 15, 16, 17, and **built the interview deck** —
  `talk/aeon_up_talk.pdf` (20 pages) plus `aeon_up_talk_notes.pdf`, from `14_talk_script.md`.

**Found:**
- **It was never a missing remote — it was a fork.** Two clones with **unrelated root commits**:
  the one holding the entire study room had no remote and 2 commits; the one with the remote had
  15 commits and **no study room at all**. A plain push was rejected; forcing would have destroyed
  twelve commits of AEON-UP history the remote already had.
- **⚠ A silent regression, caught only by diffing content.** The orphan's
  `09_operational_script.md` still contained **two fabricated citations the remote had already
  corrected** in `9de009a`: Cabaneros (the real paper is *Environmental Modelling & Software* 119,
  285–304 — not *Environmental Pollution* 254) and Andersson (arXiv:**2211.10381**, not
  2305.15340). The orphan had *more files*, so it looked newer; on those two lines it was older.
  Both restored from the remote before committing. Files 10 and 11 were checked the same way and
  differ only in maths notation.
- **The strongest thing found for H5** was already on disk and unused: UFP has **no binding limit
  value** and almost **no monitoring**, so an AEON-UP model produces exposure estimates nobody can
  check. That makes ultrafine particles the best possible case for his own uncertainty thesis —
  and the CNP's Task B (smooth background + sharp road ridge, leave-one-station-out) is that
  geometry exactly. Honest, provided he volunteers that it is synthetic.

**Decided:**
- **The deck was built by the leader, not delegated.** `2026-08-27_aeon-up-talk-deck.md` is marked
  SUPERSEDED. All three of its gates were still run — build, the twelve-number check, and the
  boundary grep — because the gates were the point, not who typed the LaTeX.
- **No figures quoted for TVöD.** File 17 refuses to name a salary number and sends him to the
  current table instead. Never invent a number applies to his pay as much as to a benchmark.
- Content stays leader-authored; only mechanics are delegable. Reaffirmed by the citation
  regression above.

**Open:**
- **Nothing is rehearsed.** Five files and a deck exist; not one has been said out loud.
- **H6** — the "GPU/TPU" claim on the *submitted* CV. The deck says GPU only; the CV still says both.
- Verify the exact title of Karl's UFP paper before naming it to its author.
- Confirm the manuscript is still "in final preparation" (Band G) and that the JAX port was
  publishable standalone.
- `cnp_synthetic` is still dirty; the LinkedIn edits are still his to make by hand.

**Repo:** `job_search` at `7619193`, pushed, `0 0`. Chess repo pushed and verified.

---

## 2026-08-27b — AEON-UP is SENT; the interview is now the live item; the CNP exists

**Did:**
- Re-pointed the whole state spine at the interview. `state/NOW.md` rewritten: §1 is the priority
  order Thejus gave (1 interview, 2 other applications + logging/reminders, 3 the two apps —
  LC0 chess and the spaced-repetition trainer, 4 the CNP), §2 is the measured interview gaps,
  §3 the CNP. `agents/ACTIVE.md` deadline block replaced accordingly.
- Recorded the terminal change and the worker economics in `CLAUDE.md`.

**Found:**
- **Q1 is answered: the application was SENT.** Three sources had disagreed for two days
  (`ACTIVE.md` said NOT SENT, the 08-26 memory said "sending today", the PDFs sat on disk).
  Thejus confirmed it directly. The 3 September deadline no longer governs.
- **The CNP was built, and no state file knew.** `cnp_synthetic` is at `db3eb90` with commit
  `063bc6e` "feat: CNP on synthetic data, with an honest uncertainty evaluation" — `cnp/`,
  `train_1d.py`, `train_city.py`, `tests/`, five `runs/*.log`, four figures, `RESULTS.md`,
  `REFEREE_REPORT.md`. The leader's own memory dated 2026-08-26 asserts "⚠⚠ THE CNP WAS NEVER
  BUILT (verified)". **That note was true when written and is now false** — left visible per the
  append-only rule, corrected in `state/NOW.md` §3 and in the memory file.
  This is what puts something behind the word *implementation* in the submitted cover letter.
  The repo is **dirty**: 5 modified + 1 untracked. Commit before it is ever screen-shared.
- **The largest interview hole is the publication gap, and it has zero coverage** across 14
  study-room files / ~3,400 lines. Five publications, all 2018–2020 astrochemistry, nothing from
  the 2021–2025 marine post-doc. Also thin: TVöD E13 vs the stated €75k, questions *for* the
  panel, no talk artefact, Karl's ultrafine-particle side never addressed in the letter.
- **The terminal is now PowerShell** (Antigravity integrated terminal, switched from `cmd`), and
  it is **Windows PowerShell 5.1** — no `&&`, no ternary. Both shells verified working; `cszero`
  resolves (Python 3.11.15, torch 2.13.0+cpu). Cause of the crash not determined.
- **A bash heredoc failed** writing a long markdown file — "unexpected EOF while looking for
  matching quote". Use the Write tool for file content; Bash for reading, grep and git.

**Decided:**
- The interview inherits the deadline discipline verbatim: status stated first, one non-interview
  brief at a time, every brief justifying itself against it, no new meta-process documents.
- The LLM-seam brief keeps its ACTIVE slot as that one exception — the chess app is interview
  evidence, and it currently ships a coach that talks without knowing anything.
- Application logging and reminders belong in `job_search` as one artefact, not as new process
  machinery in this repo.

**Open:**
- H1–H6 in `state/NOW.md` §2, H1 (the publication gap) first.
- Q2 (ICON-O/HAMOCC) and Q3 (NIT Calicut date) are now interview risks, not just website risks.
- Q4 (do the trainer equations render?) and Q5 (idiomatic German) still need two minutes each.
- `cnp_synthetic` working tree is dirty.

**Repo:** committed and pushed to `origin/windows-dev`; verified with `git status` reporting
nothing ahead.

---

## 2026-08-28 (second session) — the interview holes became drillable; research delegated outward

**Did:**
- **Carded H1–H5. The `hereon-aeon-up` ladder went 17 → 51 cards.** The existing 17 were written
  2026-08-22 and topped out at "the pitch"; H1–H5 were written 27–28 August, so the five
  highest-value pieces of interview material had **zero** coverage. Added 34: four UFP facts at L2,
  the UFP bridge and the CNP numbers at L3, **fourteen** at L4 (publication gap, TVöD, facing Karl,
  the panel questions), nine at L5 on delivering the talk. Every card sourced from the study room;
  no figure or quotation invented.
- **Filed `agents/briefs/2026-08-28_aeon-up-external-facts.md`** — seven external facts, R1–R7 —
  and built the upload package at `research/aeon_up/research_01/` for an external web-based
  research app. New `research/` tree, one directory per round, with copies of the four background
  files because that worker has no filesystem access.
- Committed the desktop launchers, `ideas/tactical_kernels.md`, and the real training state.

**Found:**
- **The trainer schema caps levels at 0–5.** The plan had been to add levels 6–8; `verify_cards.py`
  rejects them, and it also requires every `requires` edge to point **strictly downward**. It
  caught 25 same-level prerequisite edges on the first run. The new material was redistributed
  inside the existing bands, with `difficulty` carrying intra-band ordering — which is how the
  original ladder already worked.
- **`verify_cards.py` was reading its do-not-claim gate from the RETIRED `Documents\job_search`
  clone.** Contents are currently identical to the canonical copy, so nothing had gone wrong yet,
  but the gate raises `FileNotFoundError` by design when that file is missing and the directory it
  points at is dead. Repointed to `bioinformatics_project`.
- **The gate is real.** Mutation-checked rather than trusted: injecting "hands-on experience with
  EPISODE-CityChem" and "published papers in Neural Processes" into `her-l4-013` turned it red on
  both boundaries. Restored.
- **Q4 is closed.** Thejus confirmed the equations render — *"Equations are fine now."* KaTeX was
  audited ACCEPT on 08-20 with the honest caveat that Playwright 404'd and nobody had ever seen the
  output. A human has now seen it.

**Decided:**
- **The proposed research plan was rewritten, not accepted.** As drafted it had six steps: extract
  the advert, research Hereon, research the field, identify required skills, **tailor the CV and
  cover letter**, and generate interview questions. That is a plan for an application that has not
  been sent. It was sent 2026-08-27; four of the six steps rebuild the existing 22-file study room
  and one re-litigates frozen PDFs. Replaced with seven targets that share one property: **none can
  be settled from any file on disk.**
- **The brief is scoped by exclusion.** It forbids the four out-of-scope steps by name and hands
  the worker **four** study-room files out of 22 — a research agent given all of them summarises
  them back instead of going out to find what is missing.
- **UNVERIFIED is defined as success**, in its own section with the reasoning attached: these facts
  get said aloud to the people who wrote the underlying papers, so a gap left open costs nothing
  and a confident reconstruction is a disaster. The brief also forbids "likely" / "appears to be" /
  "approximately" — the words a model reaches for when it half-knows something. The Cabaneros and
  Andersson fabrications are quoted back at it with both the wrong and the right citation.
- **Flashcards are recall drill, not reading.** Recorded in `NOW.md` and in the commit: the cards
  do not substitute for standing up and delivering the talk against a clock. Adding 34 documents
  would have been this project's documented failure mode; adding 34 recall prompts is not, but only
  if the rehearsal actually happens.

**Open:**
- **Nothing is rehearsed.** Unchanged from the last session and now the only thing left on H1–H5.
- **The seven external facts are out and not back.** R1 (Karl's UFP paper title) and R2 (the TVöD
  Bund 2026 E13 table) each gate something he must not say until verified. The €75,000 expectation
  is still unrecalibrated.
- **H6** — the CV's "GPU/TPU execution". Now carded as `her-l5-009` (say GPU, correct the CV line
  if asked), but the underlying claim is still unconfirmed.
- H1's two questions for Thejus, and H5's ⚠ on Karl's paper title, all still need him.
- `cnp_synthetic` working tree is still dirty. Q5 (idiomatic German) still needs a human.
- `applications/hereon_aeon_up/other_documents/registration_confirmation_hlrs_email.pdf` remains
  untracked **on purpose** — it belongs in `job_search`, which already holds the same certificate.
  Deliberately not committed this session despite committing everything around it.

**Repo:** six commits — cards, brief, research package, launchers, ideas note, trainer state.
Pushed to `origin/windows-dev` and verified with `git status` reporting nothing ahead.

---

## 2026-08-27 — built the restart spine; confirmed the LLM defect is live and cached

**Did:**
- Created the missing entry point. `CLAUDE.md` at the repo root is auto-loaded by Claude Code on
  every cold start; it is a thin router, not content. It points at `state/NOW.md`,
  `state/JOURNAL.md`, `LEADER_BIBLE.md`, `agents/ACTIVE.md`, and carries the session-close
  routine. Added `state/NOW.md` (live state), `state/JOURNAL.md` (this file), `state/MAP.md`
  (question → file index).
- Wrote and registered `agents/briefs/2026-08-27_llm-seam-removal.md` for Gemini.
- Committed and pushed the backlog described below.

**Found:**
- **The chess repo was 35 commits ahead of origin, unpushed**, with 11 uncommitted paths —
  including two audit reports and two trainer ladders. `LEADER_BIBLE.md` §6 asserts "everything
  pushed to origin". It was not. Same failure class as the website repoint that sat uncommitted
  for three days after being audited ACCEPT.
- **The LLM seam has already fired and cached its output.**
  `data/training/cache/explanations.jsonl` holds 16 entries written 2026-07-26. The sentence
  *"Focus on maintaining sound piece activity and watch out for opponent counter-play"* appears
  verbatim across four different positions. It comes from `_build_fallback_explanation`
  (`backend/llm_client.py:214-216`), which fires when `GEMINI_API_KEY` is unset. Other entries
  are truncated mid-word. `llm_client.py` targets model id `gemini-3.5-flash`, which is not a
  real model. This answers the 2026-08-22 audit's first "could not check" item — *does it fire
  in production?* — with **yes**, from evidence on disk.

**Decided:**
- The problem was never a shortage of documentation — it was that none of it was on the path a
  cold start actually takes. `CLAUDE.md` is the fix because the harness loads it whether or not
  anyone remembers to. Everything else hangs off it.
- `state/` holds cross-cutting live state; `agents/ACTIVE.md` remains the sole source of truth
  for worker brief status. No fact is duplicated between them — `NOW.md` points at the ledger
  rather than restating it.

**Open:**
- Q1–Q5 in `state/NOW.md` §2. **Q1 (is AEON-UP sent?) is unanswered and outranks everything.**
  Asked this session; no response.

**Repo:** see the commit below this entry's date in `git log`. Pushed to `origin/windows-dev`
and verified with `git status` reporting nothing ahead.

---

## 2026-08-29 — the interview ladder was unreachable; two research claims did not survive audit

**Did:**
- **Fixed the trainer's core defect.** The `hereon-aeon-up` ladder holds 51 cards and the app
  could serve **5**. Level gating pinned the ladder to Level 0, and cram mode — the intended
  escape hatch — still applied `is_card_unlocked`, whose chains run five deep. So the 17 Level-4
  cards on the publication gap and facing Karl, and the 9 Level-5 cards on delivering the talk,
  were unreachable by any route. Brief `agents/briefs/2026-08-28_trainer-interview-mode.md`,
  delivered by Gemini, **AUDITED ACCEPT** — every gate re-run by the leader, both guards
  mutation-checked, 15 live API calls returning L3–L5 material.
- **Audited the two Deep Research PDFs** in `applications/hereon_aeon_up/research/` against the
  seven targets in `agents/briefs/2026-08-28_aeon-up-external-facts.md`. R1, R3, R4 and part of R6
  came back. **R5 and R7 did not come back at all**; R2 was dropped by Thejus.
- **Corrected three cards** from verified facts: `her-l0-003`, `her-l1-003`, `her-l2-007`.
  `verify_cards.py` still passes at 205 cards; `git diff --numstat` was `12 9`, no encoding damage.

**Found:**
- **A fabricated-class claim in the PI report.** It announces *"Contrary to the assumption that
  Dr. Karl has no published record involving artificial intelligence, a definitive linkage to
  machine learning exists."* The leader fetched its cited source, `gmd-9-451-2016-relations.html`.
  The quoted sentence belongs to **Vartiainen et al., "Machine learning-based downscaling of
  aerosol size distributions from a global climate model"** (AMT). Karl is not an author. A
  *related-articles* listing was read as a bibliography. **Karl still has no ML record.** Fifth
  fabricated delivery on record, and the third to arrive when a worker was asked for content.
- **The real finding is the mirror image, and it is verified.** Ramacher **first-authored
  EGU25-9157**, *"Machine Learning Downscaling of CAMS Regional Air Quality Reanalyses:
  High-Resolution Urban Concentrations of PM2.5 and NO2 Across Europe"*, with Paul Keil. That is
  AEON-UP's problem statement, written by one of its PIs. Card `her-l1-003` had said *"Both PIs
  … no substantial machine-learning publication record"* — which, said to Ramacher, is a bad
  moment. Corrected.
- **R1 is resolved and the report missed it entirely.** The paper the study room flagged
  ⚠ UNVERIFIED exists; the title was merely truncated: Lauenburg, M.; **Karl, M.**; Matthias, V.;
  Quante, M.; **Ramacher, M.O.P.**, *"City Scale Modeling of Ultrafine Particles in Urban Areas
  with Special Focus on Passenger Ferryboat Emission Impact"*, **Toxics 10(1), 3**,
  doi:10.3390/toxics10010003. **Karl is second author, Ramacher last** — so it is not "your
  paper" to either of them, and it is one paper joining both PIs, EPISODE-CityChem, UFP and
  Hamburg.
- **R7 confirmed and sharpened.** The revised AAQD is **Directive (EU) 2024/2881**, adopted
  23 October 2024, in force since December 2024, transposition due December 2026 — inside the
  AEON-UP project period. UFP mandatory at supersites alongside black carbon and ammonia,
  **no numerical limit value**, at ≥1 UFP supersite per 5 million inhabitants.
- **New lead: ACT-AQ**, a Helmholtz Forum consortium formed in response to the revised AAQD,
  kickoff 8–9 July 2026 in Hamburg, **Ramacher a PI**, partners including Helmholtz Munich and
  RIFS — the same two AEON-UP partners. Strong question material for Ramacher.
- **The brief's Step 2.1 was wrong.** It forbade touching `select_next_card`, but the Elo window
  breaks out at `len(elo_matched) >= 3`, so cram would have unlocked 51 cards and gone on serving
  the same 5. The worker stopped and asked instead of improvising. **Under-specifying was the
  leader's failure**; the checkpoint rule is what caught it.

**Decided:**
- **Delegate code, not content — again, and this time with a fifth data point.** The two research
  PDFs were a content delegation and produced one false headline claim and one missed paper the
  brief explicitly asked for. The trainer fix was a code delegation with five pinned gates and
  came back clean. The engine fix went to Gemini; the card corrections were written by the leader.
- **AEON-UP facts sourced only from job-board mirrors are leads, not facts.** Project period
  Oct 2026–Sep 2028, partners Helmholtz Munich (Bayesian DL / neural processes) and RIFS Potsdam,
  benchmarks against XGBoost and Gaussian Processes — jobtensor returned 403 to the leader, so
  none of this is independently confirmed. **Do not state them as known.** The acronym expansion
  is genuinely unknown; do not guess it.
- **The R6 air-quality PDF is not card material.** Five of eight rows carry "Title Unavailable" or
  an UNVERIFIED DOI. Its one solid contribution: leave-one-station-out reads as rigorous rather
  than eccentric in the spatial-modelling community, which supports `her-l3-008`.

**Open:**
- **The ladder is reachable; it is not rehearsed.** 5 of 51 hereon cards have ever been seen and
  the last real drilling session was 2026-08-22. The instrument is fixed. The drilling has not
  happened, and no document substitutes for saying the talk aloud against a clock.
- **R5 never came back** — panel composition and whether a presentation is standard at a Helmholtz
  centre are still unsourced, and `14_talk_script.md` assumes both.
- **New cards not yet written:** the ferryboat citation, the Ramacher EGU abstract (as a question
  to him, never as a claim about him), and ACT-AQ.
- **Repo tidy-up requested by Thejus this session.** The root carries 30 markdown files and the
  directory now holds `applications/` alongside the two apps. Brief to follow.

**Repo:** committed and pushed to `origin/windows-dev` this session.

---

## 2026-08-29 (evening) — the PyTorch certificate is earned; the public surface has not caught up

**Did:**
- **Verified the credential before filing it.** The certificate PDF landed in `Downloads` claiming
  completion of "Deep Learning with PyTorch", IBM via Coursera, 29 August 2026, credential
  `DDDI9T0KHUJ4`. Rather than trust the file, the leader fetched
  `coursera.org/verify/DDDI9T0KHUJ4`: it returns "Thejus Mahajan", "Deep Learning with PyTorch",
  IBM, "August 29, 2026". Name, title, issuer and date all match the PDF. *A credential ID is the
  one CV line an interviewer can check in ten seconds; checking it first costs nothing.*
- **Filed it** as
  `job_search/applications/hereon_aeon_up/certificates/IBM_Coursera_Deep_Learning_with_PyTorch.pdf`
  — one canonical copy, in the private tracked repo, alongside every other credential, md5-verified
  against the original. Committed and pushed as `2b8da1a`; `git status` reports level.
- **Updated `study_room/12_pytorch_course.md`** — content, written by the leader, not delegated.
  The status line said "in Module 6" as of 26 Aug; it now records completion, the credential ID and
  the live verification, and it restates the section-2 boundary deliberately. `git diff --numstat`
  was `17 1` — a clean insert, no encoding damage.
- **Filed `agents/briefs/2026-08-29_pytorch-certificate-rollout.md`** and registered it in
  `agents/ACTIVE.md` under a new combined `job_search` / website workspace heading.

**Found:**
- **The live website CV does not mention the course at all.** Hashing every PDF in `job_search`
  against the website's assets established that `assets/Thejus_Mahajan_CV_ML.pdf` — the primary
  download on `index.html` — is a byte-identical copy of
  `applications/ml_interpretability_general/cv_ml_interpretability.pdf`, **not** of
  `cv_general_ml/cv_ml_general.pdf` as the directory name would suggest. Its Further Training
  section lists only HLRS and JSC. A worker told to "update the CV" would almost certainly have
  edited the wrong file; the brief pins the right one and says why.
- **Two of the three downloadable CVs cannot be rebuilt.** `Thejus_Mahajan_CV.pdf` and
  `Thejus_Mahajan_CV_DE.pdf` match **no** PDF in `job_search`, and no corresponding `.tex` exists
  there or in `Documents/cv`. They are orphaned build outputs. Open item for Thejus.
- **The repository is still public.** Re-checked against the GitHub API this session:
  `"private": false`. §0 of `NOW.md` has said this is the first action of the next session since
  01:30 today and it has not happened.

**Decided:**
- **Every CV under `applications/` is a frozen record of what was sent, and the brief says so by
  name.** The hereon CV reads "final module; certificate expected 09/2026" — true on 27 August,
  when it was sent. Editing it now would make the repo disagree with the document Hereon actually
  holds. Exactly two `.tex` files change; the other thirteen application directories are named
  individually in the brief as off limits, because "roll it out everywhere" is precisely the
  helpful improvisation this workflow keeps getting bitten by.
- **The worker writes no copy on this task.** Every LaTeX and HTML string is given verbatim,
  because the one wrong sentence here — anything implying the course covers Bayesian methods or
  uncertainty — is worse now than it would have been last week: the credential ID publishes the
  syllabus. Gate G4 greps the diff itself for probabilistic vocabulary and must come back empty.
- **Completion is an interview asset, not a CV line.** The letter said "final module"; it is done.
  One unprompted sentence early in the interview converts a stated plan into a delivered one.

**Open:**
- The brief is ACTIVE and unexecuted. It spans two repositories; Part A must run before Part B.
- The two orphaned website CVs.
- **The repository is still public.**
- Unchanged from this morning: the ladder is reachable but only 5 of 51 hereon cards have been
  seen, and nothing has been rehearsed aloud against a clock.

**Repo:** committed and pushed to `origin/windows-dev` this session; `job_search` pushed at
`2b8da1a`.

---

## 2026-08-29 (late) — the brief widened; the public surface turns out to contradict itself

**Did:**
- **Widened `2026-08-29_pytorch-certificate-rollout.md`** from "add the certificate" to the whole
  public surface, at Thejus's instruction ("update all the CVs, and the text on the website"). It
  was filed narrow two hours earlier; handing it over and following with a second overlapping brief
  would have put two worker passes on the same four files and produced a conflict of the leader's
  own making. One brief, twelve gates, two screenshots.
- **Marked `2026-08-29_repo-reorganisation.md` DELIVERED in `agents/ACTIVE.md`.** It had been
  sitting as ACTIVE while `3e2d403` had already landed the work and the root was down to four spine
  files. The ledger was stale — the same failure class the catalog is full of, in the file whose
  entire job is to be current.

**Found:**
- **`skills.html` has no machine-learning content at all.** No PyTorch, no deep learning, no ML.
  The Python card reads "Data science, automation, and bioinformatics pipelines: Pandas, NumPy,
  scikit-learn, matplotlib, seaborn, xarray". The front page headlines "Machine Learning" and
  serves the ML CV as the primary download. **A technical reader who clicks Skills finds a
  bioinformatician.** This is worse than the missing certificate and nobody had noticed it.
- **`verify_cards.py:33` hardcodes an absolute path into the `job_search` repo** —
  `study_room/06_do_not_claim.md`, from which the gate loads its five forbidden-claim boundaries.
  The trainer is already coupled to the career repo. That single fact decides the separation target.
- **The gate checks that citations resolve on disk** (line 309). Run directly, it reports **193
  repo citations** across 205 cards — 84 into `docs/`, 22 into `backend/`. Ground truth from the
  tool itself rather than from `NOW.md`, which had said "193 / 72 / 22"; the docs/ figure was low.
- **Application statuses, from `APPLICATION_LOG.md`:** 4 Submitted (MPINAT, Roche, Helmholtz Munich
  IDM, and Hereon), 7 "Draft prepared", never sent.
- **The CNP was re-verified on disk before it was written onto a CV** — `cnp_synthetic` at
  `063bc6e`, `RESULTS.md` giving cnp CRPS 0.1677 against gp_oracle 0.0379, ratio 4.4214, backed by
  `runs/*.log`. Still dirty: 5 modified, 1 untracked.

**Decided:**
- **"Update all the CVs" resolves to two files, and the ruling is written into the brief.** The 4
  submitted applications are evidence — if Hereon asks "is this the CV you sent us?", the repo has
  to answer yes, so the hereon CV keeps saying "final module; certificate expected 09/2026". The 7
  never-sent drafts are stale artefacts that get regenerated from the live CV when he actually
  applies; polishing them now is documents that reach nobody, which is the documented failure mode.
  All fourteen application directories are named individually in the brief as off limits, because
  "roll it out everywhere" is exactly the helpful improvisation this workflow keeps losing to.
- **The trainer goes into `job_search`, not into a repo of its own.** Its gate already reaches into
  `job_search`; its 205 cards are career content, not chess content; and a new GitHub repo needs
  Thejus, while `job_search` exists and is private today.
- **No separation brief is filed yet, deliberately.** Moving the trainer turns 106 on-disk citations
  red, and the natural fix — rewrite them as GitHub URLs — collides with the chess repo going
  private, which would make them dead links. *The citation question and the visibility question are
  the same question.* Answer it before the move, not halfway through a `git mv`. Splitting
  `NOW.md`/`JOURNAL.md` into chess state and career state is authorship and stays with the leader.
- **The CV's ML line finally carries the probabilistic work** — `conditional neural processes
  (implemented from scratch), uncertainty calibration (NLL, CRPS, ECE)` — closing the §3 open item.
  Kept in a separate line from the IBM entry on purpose: the course teaches none of it, and the
  credential ID now publishes the syllabus.

**Open:**
- The brief is ACTIVE and unexecuted; it is the one thing waiting to be handed to the worker.
- The separation, blocked on the citations-vs-visibility decision above.
- Two website CVs with no source.
- **The repository is still public.**
- Still nothing rehearsed aloud against a clock; 5 of 51 hereon cards ever seen.

**Repo:** committed and pushed to `origin/windows-dev` this session.

---

## 2026-08-29 (night) — Part A audited accept; the repo stays public, so the material has to move

**Did:**
- **Audited the worker's Part A delivery. ACCEPT.** The diff matched the brief verbatim in both
  `.tex` files, including the deliberately different FROM string in `cv_ml_general.tex` — the trap
  in the brief, and it was not tripped. No frozen application CV was opened. G1, G2, G4 and G5
  re-run by the leader from the files themselves, not read from the report.
- **The worker halted at G3 and was right to.** `cv_ml_general.pdf` compiled to 3 pages. It
  reported the failure with real `pdflatex` output, did not improvise a fix, and did not start
  Part B. Second consecutive delivery where a checkpoint caught a problem instead of a fabrication
  reaching the leader. Audit filed at
  `agents/reports/2026-08-29_pytorch-certificate-rollout_AUDIT.md`.
- **Fixed the overflow myself** — what a CV says is a leader decision, and the brief said so. Page 3
  contained 44 characters: the signature block alone. `\vspace{0.3cm}` before it became
  `\vspace{0.05cm}`, and the credential moved onto the issuer line in that file only. **No content
  cut.** Rebuilt, re-gated green at 2 and 2, and page 2 rendered at 90 dpi and looked at.
  *Worth recording: compressing the text did not fix it; 0.25 cm of whitespace did.*
- **Amended the brief and handed Part B back.** The "Part A green first" rule was mine and was
  written before I knew the failure would land in a file Part B never touches.

**Found:**
- **A defect in my own G4 gate.** As written it greps the whole `git diff -U0`, so a hunk-header
  context line containing "publications" reads as a hit. Filtered to added lines
  (`grep "^+" | grep -v "^+++"`) it is clean. The gate can false-positive; future briefs use the
  filtered form. *My brief, my defect — not the worker's.*
- **The career footprint in the public repo is wider than `state/NOW.md` §0 had listed all day.**
  Beyond `agents/`, `trainer/` and `state/`, it includes **`research/aeon_up/`** (11 files, among
  them `2_salary_and_conditions.md` and `1_karl_and_ufp.md`), `discussions/` (4),
  `archive/superseded_tasks/` (3 AEON-UP worker tasks), `docs/SESSION_LOG_2026-08.md`,
  `docs/leadership/COMMAND_BASE.md` and `CLAUDE.md` itself.
- **The exposure is bounded and nobody is watching.** 300 commits from 2026-07-15; the career
  material first appears 08-15 (`career_strategy_conversation`), 08-19 (`trainer/`, `agents/`,
  `discussions/`) and 08-27 (`state/`). 75 of 300 commits sit in that window. **0 stars, 0 forks,
  0 watchers, 0 subscribers.** Everything before 08-15 is pure chess.
- **⚠ A premise of mine that was wrong, checked before I built on it.** I was about to argue that
  this repository's URL must be preserved because the submitted hereon CV links it. It does not:
  it links the GitHub *profile*, the website, the blog post and `hepatitis-delta-pipeline`. The
  repo URL is not load-bearing for the live application.

**Decided (by Thejus):**
- **The chess repo stays PUBLIC.** This reverses the "set it private" instruction that headed
  `NOW.md` §0 all day. The fix is subtraction: everything that is not chess leaves.
- **Only Hereon is live.** The other ten applications were rejected. `APPLICATION_LOG.md` is now a
  historical record, not a work queue — which retrospectively confirms the ruling that the seven
  never-sent drafts were not worth updating.

**Decided (by the leader):**
- **The citation question is answered by the public decision.** 106 of the 193 card citations point
  into `docs/` and `backend/`, which stay here. With the repo public, rewriting them as GitHub URLs
  is correct *and better than what exists* — a citation the reader can click is evidence; a relative
  path is not. `verify_cards.py` needs a URL check in place of `exists()` for those, and it already
  counts URL citations separately, so the machinery is half built.

**Open:**
- **Delete-only, or delete plus history rewrite?** Deleting the files changes nothing about what is
  already readable back to 15 August. With 0 forks and 0 stars a force-push breaks nobody and
  leaves 225 of 300 commits untouched; the thorough version ends with asking GitHub Support to
  purge cached views. **This is Thejus's call and it gates the separation brief.**
- Part B of the rollout, handed back to the worker.
- `cv_ml_general.tex` is still dated "Hamburg, 19 August 2026".
- Two website CVs with no source.
- Still nothing rehearsed aloud against a clock.

**Repo:** committed and pushed to `origin/windows-dev` this session.

---

## 2026-08-29 (night, cont.) — history question closed; the ferryboat card written and verified

**Decided (by Thejus):** *"Doesn't matter with the history."* **No history rewrite.** Delete-only
when the separation happens. Closed — do not re-open it. *"We prepare for the interview."*

**Did:**
- **Wrote `her-l3-011`, the ferryboat card** — the one paper joining Karl, Ramacher, ultrafine
  particles and Hamburg. Leader-authored; card content is never delegated.
- **Verified the citation against the Crossref API before writing it**, rather than trusting this
  repo's own earlier note: `Lauenburg, Marvin; Karl, Matthias; Matthias, Volker; Quante, Markus;
  Ramacher, Martin`, *"City Scale Modeling of Ultrafine Particles in Urban Areas with Special Focus
  on Passenger Ferryboat Emission Impact"*, Toxics 10(1), doi:10.3390/toxics10010003, issued
  2021-12-21. Karl second of five, Ramacher last. The card exists to stop him saying *"your paper"*
  to either of them.
- **Gated it properly.** `verify_cards.py` passes at 206 cards; **mutation-checked** by injecting
  "hands-on experience with EPISODE-CityChem" into the new card and watching it go red on the
  forbidden-claim regex, then restoring to green. `git diff --numstat` was `18 0` — a clean insert
  that did not reformat the other 51 cards.
- **Confirmed the card is actually reachable**, which is the lesson this project keeps paying for:
  a 400-draw cram-mode distribution served **all 52 cards**, the new one 7 times.

**Found:**
- **ACT-AQ could not be verified and therefore was not written.** The Helmholtz URL 404s and a web
  search returns nothing matching. It came from the same Deep Research batch that produced the false
  "Karl has an ML record" claim. **An unverified fact does not go on a card that will be recited to
  the people it is about.**
- **63 ladder citations point at the RETIRED `job_search` clone.** They use `../job_search/...`,
  which resolves from the repo root to `Documents\job_search` — the dead copy — while the newer L5
  cards correctly use `../bioinformatics_project/job_search/...`. The gate only checks that the path
  exists, and the retired directory still does, **so it has been green against a stale tree.**
  Re-rooting them is bulk work for the separation brief.
- **Part B still has not been run** — the website repo is clean, so the brief has not been handed
  back to the worker yet.

**Open:**
- Part B of the rollout.
- The separation itself: delete-only, target `job_search`, plus the 63 stale citations and the URL
  check in `verify_cards.py`. Brief not yet written.
- **The real interview gap is unchanged and no card fixes it:** 5 of 52 hereon cards have ever been
  seen, last real drilling session 2026-08-22, and the talk has never been said aloud against a
  clock.

**Repo:** committed and pushed to `origin/windows-dev` this session.

---

## 2026-08-30 — the CNP claim comes off every CV; the ReLU consultation audited

**Decided (by Thejus):** *"Lets not put things that we still not finalized. So we remove the claim
from the website as well."* **The CNP is not a written claim on any public surface.** It stays what
it always was — spoken material, slide 9 of the deck. Do not re-litigate; do not helpfully add it back.

**Did:**
- **Answered the question he actually asked** — does the CV mention the CNP — by grepping the
  **sent PDF**, `Mahajan_CoverLetter_CV_1056.pdf`, not a note about it. **The CV pages contain zero
  hits** for *neural process*, *CNP*, *CRPS*, *probabilistic*, *uncertainty*, *calibration* or
  *Bayes*. The only two hits in the whole bundle are in the **cover letter**, and both are
  disclaimers: *"I come to the probabilistic side as a builder rather than as someone with a
  publication record in it, and Bayesian methods and neural processes are current areas of learning
  and implementation."*
- **Removed the clause** `, conditional neural processes (implemented from scratch), uncertainty
  calibration (NLL, CRPS, ECE)` from `cv_ml_interpretability.tex` and `cv_general_ml/cv_ml_general.tex`.
  Both Machine Learning lines are now **byte-identical to their pre-Part-A state** — which is the
  proof the revert was exact, since the line stopped appearing in `git diff` at all.
- **Rebuilt both PDFs: 2 pages each** — the page-count gate Part A originally failed on still
  passes — **0 CNP/CRPS hits**, and **credential `DDDI9T0KHUJ4` still present** in both. The PyTorch
  certificate was not touched; that one is finalised.
- **Amended the brief and the ledger so Part B cannot put it back.** This was the real risk:
  `2026-08-29_pytorch-certificate-rollout.md` §3.3 would have inserted *Conditional Neural
  Processes* and *Uncertainty Calibration (NLL, CRPS, ECE)* as chips on `skills.html`, and **gate G9
  checked that they were there**. Both chips struck; G9 inverted to *must be 0*; G2's CNP half
  withdrawn; the two historical `TO` blocks in §2.2 prefixed with a do-not-apply marker, because a
  live-looking instruction inside a brief is exactly this project's failure class.
- **Audited the ReLU consultation** (`agents/consultations/2026-08-29_01_...`). ACCEPT on substance.
  `audit_consultation.py` passes — 6 claims, 3 VERIFIED all grepping, 2 EXTERNAL with URL and date.
- Committed and pushed both repos. `job_search` at `80e2d89`, this repo below.

**Found:**
- **The live website never carried the CNP claim at all.** Grepped the whole site — HTML, MD, JS,
  CSS and `assets/Thejus_Mahajan_CV_ML.pdf`: **zero hits**. Part A edited the `.tex` sources; Part B
  never ran, so nothing was ever published. The removal was pre-emptive, not a retraction.
- **⛔ A wrong complexity bound in the consultation, and it would have been said to a panel.** The
  follow-up answer quotes the growth of linear regions as $\mathcal{O}((N/L)^{L \cdot d})$. Against
  Montúfar et al. (2014) that is wrong three ways: the ratio is width over **input dimension**, the
  exponent is **$(L-1)n_0$**, and it is a **lower bound on the maximum**, not a big-O on what a
  trained network has. Replaced with the qualitative form, which is what the argument needs:
  *exponential in depth, polynomial in width, at fixed parameter budget.*
- **A limit of the mechanical auditor, worth knowing:** it greps `VERIFIED` quotes against local
  files and **cannot check an `EXTERNAL` quote's wording**. Claim 4's quoted abstract line says
  regions grow exponentially "with the number of hidden units"; the result that paper is known for
  is exponential in **depth**. The claim stands; the quotation is unconfirmed.
- **The interview consequence of all this, and it is the part that matters.** Nothing in the
  application — CV or letter — tells the panel the CNP exists. **So nobody will ask about it.** It
  is the strongest asset he has for a probabilistic-DL post and it enters the room only if he
  raises it himself. That is now slide 9's whole job.

**Open (unchanged, and still the only thing that matters):**
- **5 of 52 hereon cards have ever been seen; last hereon drill 2026-08-22.** He drilled twice this
  morning at 05:32 UTC — both `air-quality`, both 0.5.
- **The talk has still never been said aloud against a clock.**
- **R5 never came back:** ask the panel by email what the format is. `14_talk_script.md` assumes
  both the length and that a presentation is standard.
- **H6:** is the "GPU/TPU" claim on the submitted CV real? The deck says GPU only.
- Part B of the rollout, now safe to hand back.
- The separation brief, still unwritten.

**Repo:** `chess_speak_out_loud` and `job_search`, both committed and pushed and verified level.
