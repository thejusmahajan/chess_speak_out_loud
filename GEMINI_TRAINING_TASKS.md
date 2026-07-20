# GEMINI WORKER SPEC — Elite Training System (Phases G1–G5)

> **You are Gemini 3.1 Pro, acting as an implementation worker.** You have a large
> context window but you are prone to hallucinating APIs, file paths, and data formats.
> **Read `TRAINING_SYSTEM_PLAN.md` first** — it is the authoritative design and its
> §2 table lists the ONLY oracle APIs you may call (already verified by the leader).
> Follow this document exactly and **in order**. Where it says *verify*, run the
> command and paste the real output into `WORKLOG_TRAINING.md` before writing
> dependent code. Do not invent columns, endpoints, or library methods.

## Hard rules
1. Branch `windows-dev`. Python: `C:\Users\Admin\miniconda3\envs\cszero\python.exe`
   (conda env `cszero`). Windows/PowerShell syntax.
2. **You own:** `backend/training/store.py`, `pipeline.py`, `puzzle_db.py`,
   `openings.py`, `drills.py`; the marked endpoint section of `backend/app.py`;
   frontend Training tab; `scratch/` data scripts; `docs/api_contract.md`.
   **You must NOT edit:** `backend/training/metrics.py`, `gems.py`,
   `select_repertoire.py`, `backend/neural_vision.py`, `backend/tactics.py`,
   `backend/lichess_tagger/**`, `backend/concept_mapper.py`, `backend/engine_manager.py`.
3. All metric math comes from `backend.training.metrics` — import it, never re-derive.
   Saliency ONLY via `neural_vision.saliency_absolute(fen)`.
4. No LLM calls. No mock data in any output file (if `get_policy_distribution` returns
   `[]`, mark the job `error: "engine in mock mode"` and stop).
5. After each phase: run the acceptance gate, paste output + notes into
   `WORKLOG_TRAINING.md` (newest on top), commit with message `[training] G<n>: …`.
6. If blocked > 30 min on one issue, write the blocker into `WORKLOG_TRAINING.md`
   and move to the next phase that doesn't depend on it.

---

## PHASE G1 — Storage & job state (`backend/training/store.py`)

Build a small disk layer under `data/training/` (create dirs on demand; add a
`.gitignore` inside `data/` ignoring everything but itself):

- `EpdCache(name)` — append-only JSONL at `data/training/cache/<name>.jsonl`,
  records `{"epd": str, ...payload}`; loads into a dict on open; `get(epd)`,
  `put(epd, payload)` (write-through append). Two instances used: `policy`, `stage_b`.
- `Job` helpers — `create_job() -> job_id`, `update_job(job_id, **fields)`,
  `read_job(job_id)`; JSON files in `data/training/jobs/`. Fields per plan §4/§6.4.
- `save_profile(dict)` / `load_profile()`, `save_repertoire(dict)`,
  `save_drill_set(dict)` / `load_drill_set(set_id)` / `list_drill_sets()` per plan §5.

**Gate G1:** a pytest file you write at `backend/tests/test_training_store.py`
(temp dir via `tmp_path` monkeypatching the data root) passes:
`& C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests/test_training_store.py -q` → all green.

## PHASE G2 — Puzzle DB mining (`backend/training/puzzle_db.py` + `scratch/build_puzzle_db.py`)

1. *Verify first:* download `https://database.lichess.org/lichess_db_puzzle.csv.zst`
   to `data/puzzles/` (use `requests` streaming; ~250 MB). Decompress a sample with the
   `zstandard` package (add to `requirements.txt`) and **paste the real header row** into
   `WORKLOG_TRAINING.md`. Expected columns include
   `PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl,OpeningTags`
   — if they differ, adapt and record the difference.
2. `scratch/build_puzzle_db.py`: stream the CSV (never load it whole) into SQLite
   `data/puzzles/puzzles.sqlite`, table `puzzles(id TEXT PRIMARY KEY, fen TEXT,
   moves TEXT, rating INT, popularity INT, themes TEXT, opening_tags TEXT)`.
   Keep only rows with `Popularity >= 70`. Index on `rating`. Build a second table
   `opening_motifs(opening_tag TEXT, theme TEXT, n INT)` aggregating theme counts per
   OpeningTag token (tags are space-separated, e.g. `Sicilian_Defense Sicilian_Defense_Najdorf_Variation`).
3. `puzzle_db.py` query API:
   - `motif_profile(opening_tag) -> dict[theme, freq]` (freq = n / total for that tag)
   - `sample_puzzles(themes: list, opening_tags: list|None, rating_range, limit) -> rows`
   - `opening_tags_ranked(theme) -> [(tag, freq, n)]` (min n = 200)
   **Remember the format gotcha (plan §5): `Moves[0]` is the opponent's setup move.**

**Gate G2:**
`& …python.exe -c "from backend.training import puzzle_db; p=puzzle_db.motif_profile('Sicilian_Defense'); print(sorted(p.items(), key=lambda x:-x[1])[:5])"`
prints 5 plausible (theme, freq) pairs, and `sample_puzzles(['discoveredAttack'], None, (1500,2100), 5)` returns 5 rows. Paste both outputs.

## PHASE G3 — Openings matcher + Diagnostician pipeline

### G3a `backend/training/openings.py`
Vendor the five TSVs from `https://github.com/lichess-org/chess-openings` (raw files
`a.tsv`…`e.tsv`) into `data/openings/`. Parse (`eco, name, pgn`), convert each PGN line
to a UCI sequence with python-chess, and build:
- `classify(uci_moves: list[str]) -> {"eco","name"}|None` — longest-prefix match.
- `tabiya_fen(eco, name) -> str` — FEN after the line's last move.
- `to_opening_tag(name) -> str` — e.g. `"Sicilian Defense: Najdorf Variation"` →
  `Sicilian_Defense_Najdorf_Variation` (verify a few against real OpeningTags values
  from G2 and paste the comparison).

### G3b `backend/training/pipeline.py` — the Diagnostician
`async def run_diagnosis(job_id, pgn_text, player_name, engine, vision)`:
1. Split multi-game PGN with `chess.pgn.read_game` in a loop. Determine user color per
   game by matching `player_name` against White/Black headers (case-insensitive
   substring). Skip games where neither matches; count them in the job record.
2. **Stage A** — for every user move: EPD-cached `get_policy_distribution(fen_before, nodes=1)`,
   then `metrics.policy_divergence(policy, played_uci)`. Collect flagged moves.
   Update `job.progress` every 20 moves.
3. **Stage B** — for each flagged move, exactly the four steps in plan §4 (EPD-cached),
   using `metrics.attention_blindness`, `metrics.confirmation_swing` (mover POV!),
   `MotifDetector.analyze_pv(fen_before, pv_lines[0].split())`, `analyze_position`.
4. Classify opening per game via `openings.classify`; aggregate per plan §6.1
   (confirmed findings weigh 2); `save_profile(...)`; job → `done`.
Engine calls happen through the passed-in singletons from `app.py` — do not spawn a
second LC0. Wrap the whole run in try/except → job `error` with the message.

**Gate G3:** with the backend running per `HOW_TO_RUN.md`, POST 2–3 real PGNs of your
choosing (grab any from `scratch/` or lichess) through a temporary script hitting
`run_diagnosis` directly; show `data/training/profile.json` containing ≥1 finding with
non-empty `motifs` and a sensible `opening`. Paste the aggregates block.

## PHASE G4 — Endpoints + Drill assembly

### G4a `backend/app.py` — append a clearly marked section
`# --- Elite Training System endpoints (Gemini-owned) ---` implementing plan §6.4.
`diagnose` launches `run_diagnosis` via `asyncio.create_task` (one job at a time —
reject with 409 if a job is running). `attempt` returns the stored `reveal` and
`correct = move_uci in alt_solution_ucis`.

### G4b `backend/training/drills.py`
`generate_drill_set(count, profile, repertoire, engine, vision) -> dict` per plan §6.3:
- **own_game** (≈40%): top findings by `swing_cp` desc (confirmed first); reveal data
  is already in the finding + cached stage-B artifacts.
- **corpus** (≈40%): `sample_puzzles` filtered by profile's top motifs and, when a
  repertoire exists, its opening tags; rating window 1600–2300. Set `setup_move_uci=Moves[0]`,
  `solution_uci=Moves[1]`. Precompute reveal: policy + saliency_absolute of the
  post-setup position, motifs from the puzzle's own `themes`.
- **hidden_gem** (≈20%): call `gems.scan_for_gems(...)` (Claude-owned; if not yet
  merged, emit fewer drills and note it — do NOT stub your own gem logic).
Cap engine work: ≤ 60 BT3 forwards per generation call.

**Gate G4:** full loop over HTTP with the server running: diagnose (small PGN) → poll
job → profile → generate drills (count=6) → GET the set (reveals stripped) → attempt a
wrong move (`correct:false` + reveal present) and the right move (`correct:true`).
Paste the curl/Invoke-RestMethod transcript.

## PHASE G5 — Frontend Training tab

Read `frontend/src` yourself (you have the context budget) and reuse the existing
board + policy-arrow + saliency-heatmap components. Add a **Training** view:
1. **Diagnose panel** — textarea/file for PGN, player-name input, start button,
   progress bar polling the job endpoint.
2. **Profile report** — aggregate tables (by motif / by opening / by concept, rates),
   findings list; clicking a finding loads `fen_before` on the board and overlays the
   stored policy arrows + `hot_squares`.
3. **Drill mode** — load a set; for each drill: show position (play `setup_move_uci`
   with a short animation if present), let the user move on the board, POST attempt,
   then reveal: correct/incorrect flash (reuse the existing feedback flash), policy
   arrows, saliency heatmap, motif chips, PV. Next/previous navigation and a
   score summary at the end.
No text generation anywhere; labels come from the JSON. Update `docs/api_contract.md`.

**Gate G5:** `npm run build` succeeds; manual walkthrough of diagnose → report →
6-drill session works against the live backend; screenshot or DOM-dump evidence in
`WORKLOG_TRAINING.md`.

## PHASE G5.1 — Diagnose zero-match fix + screenshots (leader-directed, 2026-07-19)

**Context (verified by leader — do not re-litigate):** the user's "Diagnose does
nothing" report is NOT normal behavior. Job files at `data/training/jobs/` from
19:04–19:10 all show `"total": 0` and `status: done`: the `player_name` filter in
`pipeline.run_diagnosis` matched **zero games** (the UI default is `'?'`), so the job
finished instantly, showed nothing, AND `save_profile(...)` **overwrote the previous
good profile with an empty one**. Fix all three:

1. **`backend/training/pipeline.py`** — after building `games_to_process`, if it is
   empty: set the job to `error` with a message that lists the White/Black names
   actually found in the PGN, e.g.
   `No games matched player 'X'. Players in this PGN: Carlsen, Nakamura, …` — and
   `return` WITHOUT calling `save_profile`. (Never save a profile when
   `games_analyzed == 0`.)
2. **`frontend/src/components/Training/DiagnosePanel.tsx`** — default `playerName`
   to `''` (not `'?'`); placeholder "Your name exactly as it appears in the PGN
   headers"; disable Start until both PGN and name are non-empty; the job-error
   message from (1) already flows into the existing `error-msg` div — verify it renders.
3. **Screenshots** — the user has placed 3 screenshots at
   `docs/screenshots/chrome_2026-07-19_*.png`. Note: the Training Mode one currently
   shows the bug (profile with "Games analyzed: 0"). After Gate G5.1(b) below
   produces a populated profile, ask the user to retake that one screenshot (you
   cannot drive a browser on this box — Playwright driver download is broken), then
   reference all screenshots from `WORKLOG_TRAINING.md`.

**Gate G5.1:** re-run diagnose over HTTP twice: (a) with a wrong player name → job
errors with the helpful message and `data/training/profile.json` is untouched;
(b) with a correct name → profile regenerates with ≥1 finding. Paste both job JSONs.
Then commit everything as `[training] G5: Frontend training UI` (screenshots + fix
included; one commit is fine).

## PHASE G5.2 — Leader review fixes (2026-07-19, blocks C3 handoff)

The leader review of commit `f363b08` found the Gate G5 claims do not hold. Work
through these **in order**, in your owned files only. The leader has separately
committed a castling-UCI normalization to `metrics.py`/`pipeline.py`/`drills.py`
(LC0 encodes castling as `e1h1`, python-chess as `e1g1`; every user castling move
was becoming a false "blind" finding). **Do not touch that code** — but note the
consequences for you below.

1. **Build is broken — `npm run build` FAILS with 6 errors.** Your gate claim was
   false; never report a gate as passed without pasting the real output. Fix all
   TS6133 (unused declarations):
   - `DrillMode.tsx(17)` `revealFen`, `DrillMode.tsx(51)` `san`
   - `ProfileReport.tsx(1)` `useState`, `ProfileReport.tsx(16)` `concepts`
     (don't delete `concepts` — see item 3)
   - `TrainingBoard.tsx(9)` `makeUci`, `TrainingBoard.tsx(64)` `currentPos`
2. **Corpus drills are unplayable.** `DrillMode.tsx` mounts `drill.fen` directly,
   but for corpus drills that is the position BEFORE `setup_move_uci`: wrong side
   to move, orientation computed for the opponent, `movable.color` = opponent,
   every answer judged wrong, reveal overlays drawn on the wrong position. Your
   "we didn't inject chessops" note is wrong — `TrainingBoard.tsx` already imports
   chessops. Fix: when `drill.setup_move_uci` is set, apply it with chessops to
   get the effective FEN; show the pre-setup position first and animate the setup
   move via chessground's `move()` (spec item 3 of G5), then enable input on the
   post-setup position. Orientation = side to move AFTER setup.
3. **Render the by-concept table** in `ProfileReport.tsx` (spec required all
   three tables; `concepts` is computed but unused). Also fix
   `{f.confirmation?.swing_cp && (...)}` which renders a literal `0` — use an
   explicit `!= null` check.
4. **`reveal.eval_cp` is mislabeled.** For own_game drills it holds `swing_cp`;
   for corpus it is always 0. Rename the field to `swing_cp` in `drills.py`'s
   reveal dicts (coordinate: leader already edited nearby lines — rebase/pull
   first), label it "Eval swing" in `DrillMode.tsx`, hide it when 0, and update
   `docs/api_contract.md`.
5. **Surface drill-generation failures.** `TrainingTab.handleGenerateDrills`
   only `console.error`s — same silent-failure class as the G5.1 bug. Show the
   error in the UI.
6. **Commit `docs/screenshots/`** — you referenced the images in the worklog but
   never `git add`ed them; the directory is untracked.
7. **Regenerate tainted data**: after pulling the leader's castling commit,
   re-run a real diagnosis (policy/stage-B caches stay valid, only
   `profile.json` findings were tainted) and regenerate a drill set.

**Gate G5.2 (paste REAL outputs for every step):** (a) `npm run build` exits 0 —
paste full output; (b) HTTP walkthrough: diagnose → profile without castling
false-positives → generate drills → play one corpus drill to `correct: true`
(paste the attempt request/response and state which drill id); (c) `git status`
shows `docs/screenshots/` committed. Commit as `[training] G5.2: review fixes`.
Then hand over to Claude for C3.

---

**When all gates pass**, write a final `WORKLOG_TRAINING.md` entry summarizing files
touched and known gaps, and hand over to Claude for the C3 review sweep
(`CLAUDE_TRAINING_TASKS.md`). Do not merge or push without the review.

---

# EPOCH II — Tactical Steering (Gemini phases TS2, TS4)

> **Design is authoritative in `TRAINING_ROADMAP.md` → "Epoch II — Tactical
> Steering".** Read it first. The metric math (`tactical_complexity`,
> `steer_candidates`, `is_opening_mistake`) is **leader-owned in
> `backend/training/metrics.py`** — import and call it, NEVER re-derive or
> inline the formula. If `metrics.tactical_complexity` is not yet present,
> STOP and write a blocker in `WORKLOG_TRAINING.md`: TS2/TS4 depend on TS1
> (leader). Ownership and hard rules from the top of this file still apply:
> you own `pipeline.py`, `drills.py`, the marked `app.py` section, frontend;
> you must NOT edit `metrics.py`, `select_repertoire.py`, `gems.py`,
> `neural_vision.py`. Saliency ONLY via `neural_vision.saliency_absolute(fen)`.
> No mock data. Per-phase: acceptance gate output pasted into the worklog,
> commit `[training] TS<n>: …`.

## PHASE TS2 — Steering pass over own games (`backend/training/pipeline.py`)

Add a **budgeted second pass**, reusing the positions Track A already visited
(do not re-split the PGN; extend the existing Stage-A/Stage-B loop or add a
pass right after, using the SAME `games_to_process` and the policy/stage_b
EPD caches). For each user decision point (the position BEFORE the user's
move, `fen_before`):

1. From the cached policy distribution, take the top `cfg.steer_top_k` legal
   candidate moves (leader will expose `steer_top_k`; until then default 4).
2. For each candidate `m`: push it, and call
   `engine.analyze(fen_after_m, depth=None, multipv=2,
   time_limit=metrics.DEFAULT_CONFIG.confirm_played_seconds)`. EPD-cache the
   result in a NEW cache `store.EpdCache("steer")` keyed by the post-move EPD.
   Empty/mock engine output → mark job `error: "engine in mock mode"`, stop.
3. Compute complexity per candidate with
   `metrics.tactical_complexity(analysis_after_m, policy_after_m, saliency, cfg)`
   — get `policy_after_m` via `engine.get_policy_distribution(fen_after_m,
   nodes=1)` (cached), `saliency` via `vision.saliency_absolute(fen_after_m)`
   (this is the BT3 budget — cap at `cfg.steer_bt3_budget` forwards per run;
   when exhausted, skip complexity's attention term, do not stop).
4. Call `metrics.steer_candidates(...)` to rank and to decide whether a
   bounded Tal move exists at this node.

Emit a `steer_findings` list on the profile (SEPARATE from `findings`), each:
`{id, game ref, ply, fen_before, best: {uci,san,eval_cp},
  steer: {uci,san,eval_cp,complexity,components}, eval_loss_cp,
  had_tal_move: bool}`. Only keep nodes where `had_tal_move` is true OR the
best move itself is highly complex (record both — the contrast is the point).
Add `profile["steer_summary"]` = counts + mean complexity, per opening ECO
(reuse `openings.classify`). Respect the time-scramble filter
(`is_time_scramble`) exactly as Stage A does. Wrap in the existing try/except.

**Gate TS2:** over HTTP, diagnose a small real PGN (5–10 games), then show
`data/training/profile.json` contains a non-empty `steer_findings` with at
least one `had_tal_move: true` whose `eval_loss_cp` is within
`cfg.steer_max_loss_cp` and `steer.complexity > best`'s. Paste the finding +
the `steer_summary` block. Confirm no `steer_finding` has
`steer.eval_cp < cfg.steer_min_eval_cp` (no losing steers leaked).

## PHASE TS4 — Steering drills + minefield visualization

### TS4a `backend/training/drills.py` — `"steer"` drill source
Add a fourth source alongside own_game/corpus/hidden_gem. Draw from the
profile's `steer_findings` (had_tal_move). Each steer drill:
`{source:"steer", fen: fen_before, setup_move_uci: null,
  solution_uci: steer.uci, line_uci: [steer.uci],
  alt_solution_ucis: <all steer_candidates within bound, via the finding>,
  solution_san, tags: ["steer"] + motifs, difficulty: 1700,
  reveal: {policy, saliency, complexity_components, best_uci (contrast),
           eval_loss_cp, ...}}`. **Judging rule (coordinate with the existing
`check_attempt`):** a steer drill is correct if the move is in
`alt_solution_ucis` (any bounded sharp move), NOT if it equals the objective
best. Do not break existing own_game/corpus judging — steer drills carry
their own accepted set. Add a share knob so a generated set can be
steer-weighted; keep old sets working (no `line_uci`/steer fields → unchanged).

### TS4b Frontend — minefield view
Reuse `TrainingBoard`'s SVG overlay. Given a position + its per-candidate
complexity (new endpoint or embedded in the drill reveal), render each
candidate move as an arrow whose weight/colour encodes complexity, and paint
the `saliency_absolute` map underneath as the "how LC0 sees the fire" heat.
Add a small legend: "sharpness = danger to the opponent, not objective eval."
In steer-drill reveal, show `best` (objective) vs `steer` (what you were
asked for) side by side with their evals and complexity. No text generation;
all labels from JSON.

**Gate TS4:** `npm run build` exits 0 (paste output). Over HTTP: generate a
set with steer drills, GET it (reveals stripped), attempt (a) the objective
best move on a steer drill → judged per the accepted-set rule, (b) a bounded
sharp move → `correct: true`. Paste both attempt transcripts and a DOM/
screenshot of the minefield overlay. Commit `[training] TS4: steer drills + minefield`.

**When TS2 + TS4 gates pass:** worklog summary + known gaps, hand to Opus for
TS3/TS5 review. Do not push without the review.
