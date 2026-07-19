# TRAINING SYSTEM PLAN — The Elite Training System (Leader Master Plan)

> **Authoritative design document.** Written and owned by the leader agent (Claude Code).
> Worker specs: `GEMINI_TRAINING_TASKS.md` (Gemini 3.1 Pro) and `CLAUDE_TRAINING_TASKS.md`
> (Claude Opus 4.6). If a worker spec ever contradicts this file, THIS file wins.
> Branch: **windows-dev**. Python: **conda env `cszero`**
> (`C:\Users\Admin\miniconda3\envs\cszero\python.exe`). Runbook: `HOW_TO_RUN.md`.

---

## 1. Mission

Build three engines on top of the existing neural oracles:

1. **The Diagnostician** — analyze a user's PGN games against LC0's policy priors
   (intuitive blindness) and BT3 attention saliency (structural blindness), tag every
   significant divergence with tactical motifs and positional concepts, and emit a
   mathematical **Weakness Profile**.
2. **The Repertoire Architect** — select openings *backwards* from the Weakness
   Profile: lines whose resulting structures historically produce the motifs the
   player misses, that are sharp (low draw share), and objectively sound.
3. **The Drill Sergeant** — generate interactive training positions from (a) the
   user's own divergences, (b) a motif/opening-filtered corpus, (c) **hidden gems**:
   quiet positions (eval ≈ 0.00) with concentrated attention and a dominant policy
   prior. The reveal is visual: policy arrows + saliency heatmap + motif tags.

The visual layer is primary; text is secondary. **v1 has ZERO runtime LLM calls** —
all report text is deterministic templates. (LLM commentary is a v2 second pass.)

## 2. Verified ground truth (the leader checked these — do not re-derive, do not invent)

| Oracle | Call | Returns | Cost |
|---|---|---|---|
| Policy prior | `LC0Engine.get_policy_distribution(fen, nodes=1)` | `[{"uci","san","from","to","p",...}]` desc by `p` (fraction 0–1); `[]` in mock mode | fast (<0.5s) |
| Search eval / PV | `LC0Engine.analyze(fen, depth=None, multipv, time_limit)` | `{"evaluation"(white-POV cp or "M5"), "best_moves":[{move,san,score,wdl}], "pv_lines":[str], "wdl":[w,d,l] per-mille}` | ~time_limit |
| Attention saliency | `NeuralVision.saliency_absolute(fen)` | `{square: 0..1}` **absolute frame, correct for both colors** | ~1.5s/forward (CPU) |
| Motifs | `MotifDetector.analyze_pv(starting_fen, pv_san: list[str]) -> set[str]` | Lichess motif tags (`"discoveredAttack"`, …); `set()` on bad PV | cheap |
| Concepts | `analyze_position(fen, engine_analysis=None) -> {"summary", "observations":[{category,severity,text,squares}]}` | positional themes | cheap |

**Hard warnings:**
- `NeuralVision.saliency()` (public, older) is frame-correct ONLY for white-to-move.
  Training code must use **`saliency_absolute(fen)`** (added by the leader). Never call
  `_attention_saliency` directly.
- `analyze()`'s `pv_lines` is a list of **space-joined SAN strings** — `split()` before
  passing to `MotifDetector.analyze_pv`.
- The engine is a **single shared subprocess with a lock**. A batch job serializes with
  live board analysis; that's accepted for v1 (document it in the UI: "diagnosis running").
- Mock mode returns `[]` / mock dicts — pipeline must detect and **abort the job with a
  clear error**, never produce a profile from mock data.

## 3. Metric definitions — NORMATIVE CODE, already written & tested

`backend/training/metrics.py` (leader-owned, **workers must not edit**) defines:
`TrainingConfig` (all thresholds), `policy_divergence` (severity `"blind"`/`"missed"`),
`move_interaction_squares`, `attention_blindness`, `confirmation_swing`,
`is_quiet`, `saliency_concentration`, `is_hidden_gem`, `sharpness_from_wdl`,
`alt_solutions`. All pure functions. Read its docstrings; call them; do not reimplement
any formula anywhere else.

## 4. Compute budget → two-stage pipeline (this design is mandatory)

50 games ≈ 2,000 user moves. BT3 ≈ 1.5s/forward ⇒ naive full analysis ≈ hours. So:

- **Stage A (cheap, every user move):** `get_policy_distribution(fen_before, nodes=1)`
  → `policy_divergence(...)`. Flag moves with severity ≠ None. Expected flag rate 10–20%.
- **Stage B (expensive, flagged moves only):**
  1. `analyze(fen_before, depth=None, multipv=2, time_limit=3.0)` → best PV + eval.
  2. Eval the played move's continuation: `analyze(fen_after_played, depth=None, multipv=1, time_limit=1.5)`
     → `confirmation_swing(...)` (mover POV).
  3. `saliency_absolute(fen_before)` → `attention_blindness(...)` (ONE BT3 forward).
  4. `MotifDetector.analyze_pv(fen_before, pv_san_list)` + `analyze_position(fen_before, engine_analysis)`.
- **Cache everything on disk keyed by `board.epd()`** (JSONL): `policy`, `stage_b`.
  Jobs are resumable; transpositions and re-runs are free.
- Runs as a **background asyncio task** in FastAPI with a job-state file
  (`queued → stage_a → stage_b → aggregating → done | error`) and progress counters.

Budget check: 2,000 × 0.3s (A) + ~300 × ~6s (B) ≈ 40 min for 50 games. Acceptable.

## 5. Data & corpus strategy (leader decision — big token/compute saver)

**Do NOT mine motif frequencies by running engines over master games.** Use the
**Lichess puzzle database** (`https://database.lichess.org/lichess_db_puzzle.csv.zst`,
~4M puzzles, CSV columns include `FEN, Moves, Rating, Themes, OpeningTags`): it is
already motif-tagged AND opening-tagged by the same tagger family we use. Aggregating
it gives the `opening → motif frequency` table for free, plus a verified drill corpus.

**Lichess puzzle format gotcha (critical):** the CSV `FEN` is the position BEFORE the
opponent's last move; `Moves[0]` (UCI) is the opponent's setup move; the solver answers
from `Moves[1]`. Drills from this corpus must apply `Moves[0]` as `setup_move_uci`.

**Openings:** vendor `lichess-org/chess-openings` TSVs (`a.tsv`–`e.tsv`: `eco, name, pgn`)
into `data/openings/`; build a longest-prefix matcher (UCI sequence → eco/name) for
classifying user games and derive each line's final FEN as its **tabiya** for soundness
checks. Prefer PGN header ECO/Opening when present; matcher is the fallback.

**Storage:** `data/training/` — `cache/*.jsonl`, `jobs/*.json`, `profile.json`,
`repertoire.json`, `drills/*.json`, plus `data/puzzles/puzzles.sqlite` (indexed by
theme, opening tag, rating). All gitignored except directory placeholders.

## 6. JSON contracts (frozen — frontend and backend build against these in parallel)

### 6.1 Weakness Profile (`data/training/profile.json`)
```json
{"version":1,"created":"ISO","games_analyzed":47,"moves_analyzed":1882,
 "findings":[{"id":"g012-p034","game":{"white":"…","black":"…","date":"…","result":"…"},
   "user_color":"white","ply":34,"move_number":17,"fen_before":"…",
   "played":{"uci":"a2a3","san":"a3","p":0.01},"best":{"uci":"f3g5","san":"Ng5","p":0.44},
   "divergence":0.43,"severity":"blind",
   "attention":{"engagement_played":0.1,"engagement_best":0.82,"hot_squares":["f7","h7"],"blind":true},
   "confirmation":{"swing_cp":160,"confirmed":true},
   "motifs":["discoveredAttack"],"concepts":["king_safety"],
   "opening":{"eco":"B90","name":"Sicilian Najdorf"},"pv_san":["Ng5","h6","Nxf7"]}],
 "aggregates":{
   "by_motif":{"discoveredAttack":{"missed":12,"blind":7,"confirmed":9}},
   "by_opening":{"B90":{"moves":140,"missed":9,"blind":4,"blind_rate":0.029}},
   "by_concept":{"king_safety":{"missed":11}},
   "intuitive_blindness_rate":0.05,"attention_blindness_rate":0.03}}
```
Only findings with `severity != None` are stored; `confirmed` findings weigh double in
aggregates used by Engine 2 (weight = 2 for confirmed, 1 otherwise).

### 6.2 Repertoire (`data/training/repertoire.json`)
```json
{"version":1,"color":"white","targets":["discoveredAttack","king_safety"],
 "recommendations":[{"eco":"C45","name":"Scotch Game","line_pgn":"1. e4 e5 2. Nf3 Nc6 3. d4",
   "line_uci":["e2e4","e7e5","g1f3","b8c6","d2d4"],"tabiya_fen":"…",
   "motif_profile":{"discoveredAttack":0.34,"fork":0.21},"puzzle_count":1240,
   "sharpness":{"draw_pct":31.2,"sharp":true},"soundness_cp":18,
   "rationale":"deterministic template text"}]}
```

### 6.3 Drill set (`data/training/drills/<set_id>.json`)
```json
{"id":"set-2026-07-19-a","created":"ISO","drills":[{"id":"d001",
  "source":"own_game|corpus|hidden_gem","fen":"…","setup_move_uci":null,
  "solution_uci":"f3g5","alt_solution_ucis":["f3g5"],"solution_san":"Ng5",
  "tags":["discoveredAttack"],"difficulty":1800,
  "origin":{"finding_id":"g012-p034","puzzle_id":null,"eco":"B90"},
  "reveal":{"policy":[…policy dist…],"saliency":{…},"motifs":[…],
            "concepts":{…},"pv_san":[…],"eval_cp":160}}]}
```
`reveal` is precomputed at generation time (no engine call during drilling).
Correctness check: attempted UCI ∈ `alt_solution_ucis` (computed via `metrics.alt_solutions`
for `own_game`/`hidden_gem`; for `corpus`, exactly `Moves[1]`).

### 6.4 API endpoints (append to `backend/app.py`, section-marked)
```
POST /api/training/diagnose      {pgn: str (multi-game), player_name: str} -> {job_id}
GET  /api/training/jobs/{job_id} -> {status, progress:{total,stage_a_done,flagged,stage_b_done}, error}
GET  /api/training/profile       -> profile.json | 404
POST /api/training/repertoire    {color:"white"|"black"} -> repertoire.json
POST /api/training/drills/generate {count:int=20} -> drill set JSON (balanced across 3 sources)
GET  /api/training/drills        -> [{id, created, size, sources}]
GET  /api/training/drills/{set_id} -> drill set JSON (with reveals stripped)
POST /api/training/drills/attempt {set_id, drill_id, move_uci} -> {correct, reveal}
```
Update `docs/api_contract.md` with these (Gemini task).

## 7. Division of labor & ownership (no file is edited by two agents)

| Owner | Files | Why |
|---|---|---|
| **Leader (done)** | `backend/training/metrics.py`, `backend/training/__init__.py`, `neural_vision.saliency_absolute` | normative math, frame-correctness |
| **Claude Opus 4.6** | `backend/training/gems.py`, `backend/training/select_repertoire.py`, `backend/tests/test_training_*.py` (review tests), code review of every Gemini phase | subtle algorithms; low token budget → small precise files |
| **Gemini 3.1 Pro** | `backend/training/store.py`, `pipeline.py`, `puzzle_db.py`, `openings.py`, `drills.py`, app.py endpoint section, `frontend/` Training tab, `scratch/` data scripts, `docs/api_contract.md` | bulk plumbing, data wrangling, UI boilerplate → big context budget |

**Order:** G1 (store) ∥ C1 (gems) → G2 (puzzle DB) ∥ G3 (pipeline) → C2 (repertoire
select, needs G2 output) → G4 (endpoints+drills) → G5 (frontend) → C3 (review sweep) →
leader final verify. Gemini never edits Claude-owned files and vice versa. Both append
progress to **`WORKLOG_TRAINING.md`** (create it; newest entry on top: date, agent,
phase, what was done, verification output pasted, open questions).

## 8. Hard rules (both workers)

1. Branch `windows-dev` only. Commit per phase with `[training]` prefix.
2. Use conda env `cszero` python for everything; never `pip install` into system python.
3. No runtime LLM calls anywhere in v1. `LLM_ENABLED` stays as-is.
4. Never reimplement motif detection or metric math. `lichess_tagger` and
   `backend/training/metrics.py` are the only sources of truth.
5. Mock-mode data must never enter a profile, repertoire, or drill file.
6. Every phase ends with its **acceptance gate** (a command + expected output) pasted
   into `WORKLOG_TRAINING.md`. A failed gate = STOP and report, don't continue.
7. New Python deps go into `requirements.txt` (`zstandard` will be needed).

## 9. Standard of success (from the brief — the leader's final verification)

Upload 50 games → precise diagnostic report (by motif and opening) → personalized
repertoire targeting the diagnosed blindnesses → 20 interactive drills mixing own-game
positions, corpus puzzles, and hidden gems — with the neural reveal (arrows + heatmap)
shown only after each attempt, sufficient to teach with no generated text at all.
