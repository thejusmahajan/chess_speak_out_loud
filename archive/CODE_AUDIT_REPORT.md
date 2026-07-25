# CODE AUDIT REPORT — Elite Training System

> **Audit Date:** 2026-07-22  
> **Auditor:** Gemini 3.6 Flash (High)  
> **Mode:** READ-ONLY Audit & Aim-Alignment Verification  

---

## Executive Summary

A comprehensive, read-only audit of the Elite Training System backend (`backend/training/`, `backend/app.py`, `backend/engine_manager.py`) was performed across all six requested priority modules. 

The audit evaluated both **correctness bugs** (cross-module shape mismatches, mathematical errors, edge cases, error handling) and **aim alignment** against the authoritative specifications (`TRAINING_SYSTEM_PLAN.md`, `REPERTOIRE_TUTOR_EPOCH.md`, `TRAINING_ROADMAP.md`, `ARCHITECTURE.md`, and `metrics.py` docstrings).

A total of **8 findings** were identified and categorized by severity and status (**7 CONFIRMED**, **1 SUSPECTED**).

---

## Detailed Audit Findings (Ranked by Severity)

### 1. [SEV: critical] `tactical_complexity` computes response narrowness with inverted White-POV evals when Black is to move  (CONFIRMED)
- **category:** wrong-semantics / cross-module
- **location:** `backend/training/metrics.py:418-423` (consumer calls in `backend/training/pipeline.py:399` and `backend/training/select_repertoire.py:232`)
- **evidence:**  
  In `metrics.py`:
  ```python
  best_moves = analysis.get("best_moves") or []
  gap_cp = 0.0
  best_reply_uci = _move_uci(best_moves[0]) if best_moves else None
  if len(best_moves) >= 2:
      s0 = eval_cp_number(best_moves[0].get("score"))
      s1 = eval_cp_number(best_moves[1].get("score"))
      if s0 is not None and s1 is not None:
          gap_cp = max(0.0, s0 - s1)
  narrowness = min(gap_cp / cfg.steer_narrow_full_cp, 1.0) if cfg.steer_narrow_full_cp else 0.0
  ```
  `LC0Engine.analyze()` returns `score` in `best_moves` as centipawns from **WHITE's point of view** (`engine_manager.py:351`). `tactical_complexity` is evaluated on the position AFTER a candidate move $m$, where the side to move is the OPPONENT.  
  When Black is the side to move (e.g., after White plays a candidate move):
  - Black's 1st-best reply has a LOWER White-POV score $s_0$ (e.g. -200 cp).
  - Black's 2nd-best reply has a HIGHER White-POV score $s_1$ (e.g. +50 cp).
  - From Black's POV, the drop-off if Black fails to find $s_0$ is $(-s_0) - (-s_1) = s_1 - s_0 = 50 - (-200) = 250$ cp (a 250cp blunder/narrow defense).
  - However, `metrics.py` calculates `s0 - s1 = -200 - 50 = -250`, so `gap_cp = max(0.0, -250)` evaluates to `0.0`.
- **failure scenario:** For every White decision node evaluated during steering or repertoire tree construction, Black's candidate replies have White-POV scores where $s_0 < s_1$. `gap_cp` evaluates to `0.0`, forcing `narrowness = 0.0` and `policy_trap = (1 - p) * narrowness = 0.0`. Response narrowness and policy trap complexity components are silently zeroed out for all Black opponent reply evaluations.
- **why it matters:** Violates `TRAINING_ROADMAP.md` ("Epoch II — Tactical Steering") and `metrics.py` docstring ("How much tactical danger a position holds for the side to move... narrowness — eval gap between the best and 2nd-best reply").
- **suggested fix:** Pass mover POV / turn to `tactical_complexity` or compute `gap_cp = (s0 - s1) if mover_is_white else (s1 - s0)` so eval drop-off is measured from the side-to-move's perspective.

---

### 2. [SEV: high] `by_opening` aggregate computes weighted blind rate whereas `by_phase` and `by_clock` compute unweighted blind rate  (CONFIRMED)
- **category:** wrong-semantics / data-shape
- **location:** `backend/training/pipeline.py:493-516` vs `backend/training/pipeline.py:101-115`
- **evidence:**  
  In `pipeline.py` (lines 493-515):
  ```python
  for f in findings:
      weight = 2 if f["confirmation"].get("confirmed") else 1
      sev = f["severity"]
      ...
      eco = f["opening"]["eco"]
      by_opening[eco][sev] += weight

  for eco, st in by_opening.items():
      if st["moves"] > 0:
          st["blind_rate"] = st["blind"] / st["moves"]
  ```
  In `aggregate_phase_clock` (lines 102-114):
  ```python
  if key in blind_keys:
      by_phase[phase]["blind"] += 1
      by_clock[bucket]["blind"] += 1
  ...
  b_data["blind_rate"] = b_data["blind"] / moves if moves > 0 else 0.0
  ```
- **failure scenario:** `by_opening[eco]["blind"]` contains the weighted finding sum (`weight = 2` for confirmed findings), so `st["blind"] / st["moves"]` is a weighted severity density that can exceed `1.0` (e.g. `1.20` or 120%), whereas `by_phase` and `by_clock` compute unweighted move fractions (`blind / moves` in `[0.0, 1.0]`).
- **why it matters:** Contradicts `TRAINING_SYSTEM_PLAN.md` § 6.1 example (`"blind":4, "blind_rate":0.029` where $4/140 = 0.02857$) and creates mathematical inconsistency when `rank_dimension` compares openings against phase or clock dimensions.
- **suggested fix:** Compute `st["blind_rate"]` in `by_opening` using unweighted blind finding counts (`unweighted_blind / moves`), or store `weighted_blind` separately.

---

### 3. [SEV: high] Unhandled `JSONDecodeError` / `OSError` in `start_diagnose` can crash diagnosis endpoint with HTTP 500  (CONFIRMED)
- **category:** edge-case / error-handling
- **location:** `backend/app.py:465-468` vs `backend/app.py:452-456`
- **evidence:**  
  In `backend/app.py`:
  ```python
  @app.post("/api/training/diagnose")
  async def start_diagnose(req: DiagnoseRequest):
      jobs_dir = Path(store.TRAINING_DIR) / "jobs"
      if jobs_dir.exists():
          for job_file in jobs_dir.glob("*.json"):
              with open(job_file, "r") as f:
                  j = json.load(f)
                  if j.get("status") == "running":
                      raise HTTPException(status_code=409, detail="A diagnosis job is already running")
  ```
  Unlike `_sweep_orphaned_training_jobs()` which safely wraps `json.load(f)` in a `try...except (json.JSONDecodeError, OSError): continue`, `start_diagnose` opens and parses all job files in `data/training/jobs/` without any error handling.
- **failure scenario:** If an existing job file in `data/training/jobs/` is corrupted, empty, or currently locked/being written by another handle, `json.load(f)` raises `json.JSONDecodeError` or `OSError`. `POST /api/training/diagnose` fails with an uncaught HTTP 500 error instead of skipping the invalid file or returning HTTP 409.
- **suggested fix:** Wrap `json.load(f)` in `start_diagnose` with `try...except (json.JSONDecodeError, OSError): continue`.

---

### 4. [SEV: high] Hardcoded corpus PGN path and username in `repertoire_top_openings` and `get_repertoire_tree` endpoints  (CONFIRMED)
- **category:** data-shape / aim-mismatch
- **location:** `backend/app.py:526-527` and `backend/app.py:575-576`
- **evidence:**  
  In `backend/app.py`:
  ```python
  pgn_path = PROJECT_DIR / "games_of_derdiedasdie" / "lichess_derdiedasdie_2026-07-19.pgn"
  player_name = "derdiedasdie"
  ```
- **failure scenario:** In a clean environment, when running for a different player username, or when `games_of_derdiedasdie/lichess_derdiedasdie_2026-07-19.pgn` is absent, requesting top openings or building an un-cached repertoire tree fails with HTTP 404 ("Corpus PGN not found") or builds trees for `derdiedasdie` rather than the active user's games.
- **why it matters:** Violates multi-user / generic user diagnosis goals in `TRAINING_SYSTEM_PLAN.md` § 1 & § 6.4.
- **suggested fix:** Parameterize PGN path and player_name from active profile metadata or request body instead of hardcoding developer-specific paths.

---

### 5. [SEV: medium] `build_repertoire_tree` `user_blind_rate` counts profile-wide findings against ECO-specific game count  (CONFIRMED)
- **category:** wrong-semantics
- **location:** `backend/training/select_repertoire.py:435-446` & `backend/training/select_repertoire.py:541-543`
- **evidence:**  
  In `select_repertoire.py`:
  ```python
  blind_by_epd = defaultdict(int)
  if profile:
      for f in profile.get("findings", []):
          ...
          if f.get("severity") in ("blind", "missed"):
              blind_by_epd[fepd] += 1
  ...
  n_here = node["n_games"]
  blind_rate = min(1.0, blind_by_epd.get(epd, 0) / n_here) if n_here else 0.0
  ```
- **failure scenario:** `blind_by_epd` accumulates findings from ALL games in the profile regardless of ECO, while `n_here` (`node["n_games"]`) counts only games in `valid_games` (games reaching this specific ECO). If a transposition EPD occurred in multiple openings, `blind_by_epd.get(epd, 0)` includes findings from other openings, causing `blind_by_epd.get(epd, 0) / n_here` to artificially inflate or hit the 1.0 cap.
- **suggested fix:** Filter `profile.get("findings", [])` to findings matching `f.get("opening", {}).get("eco") == eco` when building `blind_by_epd` for a specific tree.

---

### 6. [SEV: medium] Steer cache misses re-calculate saliency without persisting saliency to disk  (CONFIRMED)
- **category:** silent-degeneracy / performance
- **location:** `backend/training/pipeline.py:375-398`
- **evidence:**  
  In `pipeline.py`:
  ```python
  s_data = steer_cache.get(epd_after_m)
  if not s_data:
      ...
      s_data = {"analysis": analysis, "policy": pol_after}
      steer_cache.put(epd_after_m, s_data)
      search_used += 1

  analysis_after = s_data["analysis"]
  policy_after = s_data["policy"]

  if bt3_budget_remaining > 0:
      saliency = vision.saliency_absolute(fen_after_m)
      bt3_budget_remaining -= 1
  else:
      saliency = None
  ```
- **failure scenario:** `steer_cache.put` saves only `{"analysis": analysis, "policy": pol_after}`. On a cached re-run of diagnosis or when reading from disk, `steer_cache.get` returns `s_data` without `saliency`. `saliency` is re-computed with `vision.saliency_absolute` (spending CPU time and decrementing `bt3_budget_remaining`), instead of leveraging cached attention maps.
- **suggested fix:** Include `"saliency": saliency` in `s_data` payload saved to `steer_cache`.

---

### 7. [SEV: low] `TRAINING_SYSTEM_PLAN.md` § 8 Rule 3 ("No runtime LLM calls in v1") vs R3 `enrich_tree_explanations` LLM generation  (CONFIRMED)
- **category:** aim-mismatch
- **location:** `backend/app.py:535` and `backend/training/explanations.py:63` vs `TRAINING_SYSTEM_PLAN.md:27,183`
- **evidence:**  
  In `TRAINING_SYSTEM_PLAN.md`: "v1 has ZERO runtime LLM calls — all report text is deterministic templates... No runtime LLM calls anywhere in v1. LLM_ENABLED stays as-is."  
  In `explanations.py`: `explanation_text = await llm_client.generate_move_explanation(context, model)` is called directly when serving `POST /api/training/repertoire/tree` in `app.py`.
- **failure scenario:** If `GEMINI_API_KEY` is present in `.env`, calling `POST /api/training/repertoire/tree` makes external network calls to Gemini API during tree enrichment. (If `GEMINI_API_KEY` is absent, it falls back to plain-text templates).
- **why it matters:** This reflects an intentional specification evolution from `TRAINING_SYSTEM_PLAN.md` (v1 zero LLM) to `REPERTOIRE_TUTOR_EPOCH.md` (Epoch III Track R / R3 LLM explanations), but represents a formal doc contradiction.
- **suggested fix:** Update `TRAINING_SYSTEM_PLAN.md` to document R3 LLM explanations as an approved Epoch III addition.

---

### 8. [SEV: low] `_walk_line` in `drills.py` line truncation logic when reaching leaf node  (SUSPECTED)
- **category:** edge-case
- **location:** `backend/training/drills.py:276-300`
- **evidence:**  
  In `drills.py`:
  ```python
  while len(line) < max_len:
      ...
      line.append(um["uci"])
      ...
      if not replies:
          break
      top = replies[0]
      ...
      line.append(top["uci"])
      node = child
  if len(line) % 2 == 0 and line:
      line = line[:-1]
  ```
- **failure scenario:** If a line terminates because `replies` is empty after `line.append(um["uci"])`, `len(line)` is odd (e.g. 1, 3, 5). `len(line) % 2 == 0` is False, so `line` remains odd. If `line.append(top["uci"])` is reached when `len(line) == max_len` (even), `len(line) % 2 == 0` truncates `line` to odd length `line[:-1]`. A edge case might occur if `max_len` is configured as an even integer, which could return an even-length line.
- **suggested fix:** Add `assert len(line) % 2 != 0` before returning from `_walk_line` to strictly enforce odd-length line invariant.

---

## Aim-Alignment Verdict

**Verdict: HIGHLY ALIGNED with minor mathematical & hardcoding gaps.**

The core architecture of the Elite Training System successfully fulfills the mission outlined in `TRAINING_SYSTEM_PLAN.md` and `REPERTOIRE_TUTOR_EPOCH.md`:
1. **The Diagnostician** correctly integrates policy divergence, absolute attention blindness, tactical complexity, and phase/clock aggregations.
2. **The Repertoire Architect** selects ingrained openings from user PGN games and constructs engine-vetted variation trees.
3. **The Drill Sergeant** generates line drills from critical nodes with SRS scheduling, alt-solution acceptance, and cached LLM coach explanations.

### Top Gaps to Address
1. Inverted White-POV score evaluation in `tactical_complexity` for Black response narrowness (Finding 1).
2. Weight mismatch between `by_opening` vs `by_phase`/`by_clock` blind rates (Finding 2).
3. Hardcoded user PGN path and username in repertoire tree endpoints (Finding 4).

---

## Summary of Findings

| Severity | CONFIRMED | SUSPECTED | Total |
|---|---|---|---|
| **Critical** | 1 | 0 | **1** |
| **High** | 3 | 0 | **3** |
| **Medium** | 2 | 0 | **2** |
| **Low** | 1 | 1 | **2** |
| **Total** | **7** | **1** | **8** |
