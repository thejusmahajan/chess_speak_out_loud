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

---

**When all gates pass**, write a final `WORKLOG_TRAINING.md` entry summarizing files
touched and known gaps, and hand over to Claude for the C3 review sweep
(`CLAUDE_TRAINING_TASKS.md`). Do not merge or push without the review.
