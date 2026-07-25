# Pre-Deploy Audit Report — Chess Speak Out Loud (Elite Training System)

**Audit Date:** 2026-07-22  
**Target:** Pre-deploy audit of diagnosis pipeline & node-limit changes prior to renting A100 GPU hours for a ~700-game corpus run.  
**Mode:** READ-ONLY audit (no code modifications made).

---

## Executive Summary & GO / NO-GO Recommendation

### Recommendation: ⛔ **NO-GO** (Must fix 3 high-severity blockers before spending rented GPU hours)

While recent fixes (F1 White-POV magnitude in `tactical_complexity` and F2 unweighted `by_opening` blind rates) have restored mathematical soundness to the core diagnostician, our audit of the newly landed node-limit search path (`ee9afda`) and full-corpus scalability revealed **3 high-severity blockers** that will either waste paid GPU execution hours or produce corrupted profiles over a 700-game run:

1. **No wall-clock safety cap on node-limited searches ([engine_manager.py:352-357](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/engine_manager.py#L352-L357)):** `_do_analyze` drops `time_limit` entirely when `nodes` is set. If LC0 hangs or hits a GPU driver hitch on any single position, python-chess will block indefinitely without a wall-clock deadline, freezing the multi-hour paid run.
2. **Incomplete node-limit migration in downstream cells ([select_repertoire.py:183, 226, 522](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/select_repertoire.py#L183) & [gems.py:75, 89](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/gems.py#L75)):** Node twins were added only for Stage B confirmation (`confirm_best_nodes` / `confirm_played_nodes`). Repertoire building, variation tree generation, and hidden gem scanning still use hardcoded time limits (`4.0s`, `1.6s`, `6.0s`), forcing the A100 GPU to evaluate ~670,000 nodes per position and wasting up to an hour of GPU time in cells 8–9.
3. **Tactical Steering (TS2) budget exhaustion silently truncates full-corpus analysis ([pipeline.py:396-398, 435-437](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/pipeline.py#L396-L437)):** The hardcoded `steer_search_budget=4000` exhausts after ~30-40 games out of 700. When hit, TS2 executes a `break` out of the decision loop, silently skipping tactical steering for the remaining ~660 games while saving `profile.json` as complete with distorted `steer_summary` move counts.

---

## Finding Summary Table

| ID | Sev | Title | Category | Status |
|---|---|---|---|---|
| F1.1 | **HIGH** | Node-limited engine searches drop `time` limit completely without a wall-clock safety net | `node-limit` / `run-wasting` | **CONFIRMED** |
| F1.2 | **HIGH** | Downstream searches (`select_repertoire.py`, `gems.py`) remain time-based, wasting GPU hours | `node-limit` / `run-wasting` | **CONFIRMED** |
| F1.3 | **HIGH** | Stage TS2 budget exhaustion (`steer_search_budget=4000`) silently truncates 95% of full corpus | `budget` / `profile-corrupting` | **CONFIRMED** |
| F1.4 | **HIGH** | Lack of incremental pipeline checkpointing loses all multi-hour GPU progress on mid-run failure | `run-wasting` / `edge-case` | **CONFIRMED** |
| F1.5 | **MEDIUM** | Progress bar `total` mismatch in `pipeline.py` & `diagnose_on_gpu.py` makes Stage B appear frozen | `aim-mismatch` / `edge-case` | **CONFIRMED** |
| F1.6 | **MEDIUM** | `EpdCache.put` uses raw non-atomic append without Windows permission retry backoff | `cache` / `run-wasting` | **CONFIRMED** |
| F1.7 | **MEDIUM** | Unbounded memory accumulation in `user_decision_nodes` and `uci_moves_so_far` over thousands of games | `edge-case` / `run-wasting` | **CONFIRMED** |
| F1.8 | **LOW** | `_walk_line` in `drills.py` truncates variation line when reaching opponent leaf node | `edge-case` | **CONFIRMED** |

**Totals:** 0 Critical, 4 High, 3 Medium, 1 Low (8 CONFIRMED, 0 SUSPECTED).

---

## Detailed Findings

### [SEV: high] Node-limited engine searches drop `time` limit completely without a wall-clock safety net (CONFIRMED)
- **category:** node-limit / run-wasting
- **location:** [backend/engine_manager.py:352-364](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/engine_manager.py#L352-L364)
- **evidence:**
```python
if nodes is not None:
    # Node-limited: deterministic search depth regardless of backend
    # speed. Ignores time/depth so quality is hardware-independent.
    limit_kwargs = {"nodes": nodes}
else:
    limit_kwargs = {"time": time_limit}
    if depth is not None:
        limit_kwargs["depth"] = depth
infos = await self.engine.analyse(
    board,
    chess.engine.Limit(**limit_kwargs),
    multipv=multipv,
)
```
- **failure scenario:** When `nodes` is passed (e.g. `confirm_best_nodes=120_000` in Cell 5b), `limit_kwargs` contains *only* `{"nodes": 120000}` and drops `time`. In `python-chess`, `Limit(nodes=N)` without `time` sets no wall-clock timeout on the subprocess read or `asyncio` call. If LC0 experiences a CUDA deadlock, driver glitch, or engine stall on a single position during a 4-hour run, the process will wait indefinitely.
- **blast radius on a full corpus run:** Wastes paid GPU execution time ($ and hours) by hanging the notebook execution indefinte on a single stalled search.
- **suggested fix:** In `_do_analyze`, include a wall-clock fallback safety net alongside `nodes`: `limit_kwargs = {"nodes": nodes, "time": max(time_limit or 30.0, 60.0)}`. UCI engines stop on whichever limit is reached first.

---

### [SEV: high] Downstream searches (`select_repertoire.py`, `gems.py`) remain time-based, wasting GPU hours (CONFIRMED)
- **category:** node-limit / run-wasting
- **location:** [backend/training/select_repertoire.py:183, 226, 522](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/select_repertoire.py#L183), [backend/training/gems.py:75, 89](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/gems.py#L75), [backend/training/metrics.py:86-87](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/metrics.py#L86-L87)
- **evidence:**
  In `metrics.py`: `confirm_best_nodes` and `confirm_played_nodes` are the only node-limit fields added to `TrainingConfig`.
  In `select_repertoire.py:183`: `analysis = await engine.analyze(tabiya_fen, depth=None, multipv=2, time_limit=cfg.repertoire_eval_seconds)`.
  In `select_repertoire.py:522`: `analysis = await engine.analyze(after.fen(), depth=None, multipv=2, time_limit=cfg.repertoire_eval_seconds)`.
  In `gems.py:75`: `quick = await engine.analyze(fen, depth=None, multipv=1, time_limit=cfg.gem_screen_seconds)`.
- **failure scenario:** `cfg.repertoire_eval_seconds` defaults to `4.0s` and `gem_confirm_seconds` defaults to `6.0s`. On a 168k-nps A100 GPU, a 4.0-second eval expands ~670,000 nodes per position (5x deeper than Stage B confirmation). When building repertoires and variation trees in cell 8 over dozens of candidate moves, cells 8 and 9 spend 30-60+ minutes evaluating positions to absurd search depths.
- **blast radius on a full corpus run:** Wastes rented GPU A100 time during post-diagnosis artifact generation (cells 8 & 9).
- **suggested fix:** Add `repertoire_eval_nodes`, `gem_screen_nodes`, and `gem_confirm_nodes` fields to `TrainingConfig` and configure node twins in Cell 5b of `colab/diagnose_on_gpu.py`.

---

### [SEV: high] Stage TS2 budget exhaustion (`steer_search_budget=4000`) silently truncates 95% of full corpus (CONFIRMED)
- **category:** budget / profile-corrupting
- **location:** [backend/training/pipeline.py:396-398, 435-437, 473-493](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/pipeline.py#L396-L437)
- **evidence:**
```python
if search_used >= metrics.DEFAULT_CONFIG.steer_search_budget:
    steer_budget_exhausted = True
    break
...
if steer_budget_exhausted:
    pbar_ts2.update(1)
    break
```
- **failure scenario:** Over ~700 games (~24,500 user decision nodes), evaluating candidate moves in Stage TS2 consumes 4 engine calls per uncached node. The default `steer_search_budget=4000` exhausts after ~30-40 games. Line 398 sets `steer_budget_exhausted = True` and line 437 `break`s out of the decision loop, silently skipping TS2 for the remaining ~660 games. Furthermore, `by_opening_steer` computes move counts (`st["moves"]`) using ONLY the processed games before budget exhaustion, producing false opening move counts in `steer_summary`. `profile.json` is saved as complete without surfacing that tactical steering skipped 95% of the games.
- **blast radius on a full corpus run:** Profile corruption (silent truncation of tactical steering and wrong `steer_summary` move counts for all openings across the player's profile).
- **suggested fix:** Scale `steer_search_budget` appropriately for GPU runs (or eliminate the search limit when GPU acceleration is active), compute total opening move counts across all user decision nodes regardless of TS2 budget exhaustion, and surface a prominent warning in `profile.json` when budget is exhausted.

---

### [SEV: high] Lack of incremental pipeline checkpointing loses all multi-hour GPU progress on mid-run failure (CONFIRMED)
- **category:** run-wasting / edge-case
- **location:** [backend/training/pipeline.py:130-132, 556-568](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/pipeline.py#L130-L568), [backend/training/store.py:121-134](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/store.py#L121-L134)
- **evidence:**
  `run_diagnosis` accumulates `findings`, `steer_findings`, and `aggregates` entirely in local Python lists during Stage A, Stage B, and Stage TS2. `store.save_profile(profile)` is invoked ONLY once at the very end of `run_diagnosis` (line 568).
- **failure scenario:** If a 4-hour Colab GPU run experiences a disconnect, preemption, container crash, or transient exception at game 650/700 in Stage B or Stage TS2, no `profile.json` checkpoint exists. The user must restart the entire multi-hour GPU run from game 0.
- **blast radius on a full corpus run:** Wastes paid GPU $ and hours upon any mid-run failure or network disconnect.
- **suggested fix:** Implement periodic incremental profile checkpointing in `pipeline.py` (e.g., after Stage B completion or after every N processed games).

---

### [SEV: medium] Progress bar `total` mismatch in `pipeline.py` & `diagnose_on_gpu.py` makes Stage B appear frozen (CONFIRMED)
- **category:** aim-mismatch / edge-case
- **location:** [backend/training/pipeline.py:180](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/pipeline.py#L180), [colab/diagnose_on_gpu.py:296-305, 328-337](file:///c:/Users/Admin/Documents/chess_speak_out_loud/colab/diagnose_on_gpu.py#L296-L337)
- **evidence:**
```python
_progress(job_id, total=user_moves_count, time_scramble_skipped=scramble_skipped)
```
In `colab/diagnose_on_gpu.py`:
```python
def custom_progress(job_id, total=None, stage_a_done=None, stage_b_done=None, stage_steer_done=None, **kwargs):
    ...
    if total is not None and pbar is None:
        pbar = tqdm(total=total, desc="Diagnosing Games", unit="move")
    if pbar is not None:
        current = stage_steer_done or stage_b_done or stage_a_done or 0
        pbar.n = min(current, pbar.total or current)
```
- **failure scenario:** `_progress` sets `total` to `user_moves_count` (e.g. 25,000 moves for 700 games). In Stage B, `stage_b_done` increments up to `len(flagged_moves)` (e.g. ~150 candidates). `pbar.n` sits at `150 / 25000` (0.6% progress) for the entire 20-30 minute duration of Stage B confirmation, appearing completely frozen.
- **blast radius on a full corpus run:** User confusion; risks the user prematurely cancelling a healthy paid GPU run under the false impression that it hung.
- **suggested fix:** Emit stage-specific totals in `_progress` (e.g. `stage_b_total=len(flagged_moves)`) and update `custom_progress` in `diagnose_on_gpu.py` to handle progress per stage.

---

### [SEV: medium] `EpdCache.put` uses raw non-atomic append without Windows permission retry backoff (CONFIRMED)
- **category:** cache / run-wasting
- **location:** [backend/training/store.py:45-50](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/store.py#L45-L50)
- **evidence:**
```python
def put(self, epd: str, payload: dict):
    record = payload.copy()
    record["epd"] = epd
    self._data[epd] = record
    with open(self.path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
```
- **failure scenario:** `store._write_json_atomic` contains explicit retry logic for `PermissionError` (lines 64-71) to survive transient file locks on Windows (e.g. antivirus scans or concurrent reads). `EpdCache.put` uses standard `open(..., "a")`. If an external reader or antivirus scans `policy.jsonl`, `stage_b.jsonl`, or `steer.jsonl` during a write, `open()` raises `PermissionError` and crashes `run_diagnosis`.
- **blast radius on a full corpus run:** Risk of mid-run crash on Windows development environments.
- **suggested fix:** Wrap `EpdCache.put` file opening with exponential backoff retry on `PermissionError`.

---

### [SEV: medium] Unbounded memory accumulation in `user_decision_nodes` and `uci_moves_so_far` over thousands of games (CONFIRMED)
- **category:** edge-case / run-wasting
- **location:** [backend/training/pipeline.py:239-247](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/pipeline.py#L239-L247)
- **evidence:**
```python
user_decision_nodes.append({
    "game_idx": game_idx,
    "game": game,
    "ply": ply,
    "user_color": user_color,
    "fen_before": board.fen(),
    "epd": epd,
    "uci_moves_so_far": list(uci_moves)
})
```
- **failure scenario:** For 4,000 games (`N_FULL = None` in Cell 7), `user_decision_nodes` stores 140,000+ dict objects in memory. Each dict retains a reference to the parsed `chess.pgn.Game` object and a newly copied list of up to 100 UCI move strings (`list(uci_moves)`). This creates over 10,000,000 string references and thousands of AST structures in RAM, triggering heavy GC thrashing by game 3,000.
- **blast radius on a full corpus run:** Memory bloat, performance degradation, and potential OOM crash on long runs.
- **suggested fix:** Store only essential primitive attributes (ECO code or current FEN) in `user_decision_nodes` instead of full `Game` references and cumulative move lists.

---

### [SEV: low] `_walk_line` in `drills.py` truncates variation line when reaching opponent leaf node (CONFIRMED)
- **category:** edge-case
- **location:** [backend/training/drills.py:298-299](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/drills.py#L298-L299)
- **evidence:**
```python
# end on a user move (odd length) so check_attempt completes cleanly
if len(line) % 2 == 0 and line:
    line = line[:-1]
```
- **failure scenario:** When walking a variation tree line where an opponent reply reaches a leaf node (no subsequent user move), line 298 pops the opponent's move to ensure odd line length. If the line was `[user_move, opp_reply]`, it is truncated to `[user_move]`, yielding a single-move drill.
- **blast radius on a full corpus run:** Minor UI/UX impact (single-move drill generated instead of multi-move sequence).
- **suggested fix:** Filter out 1-move lines when packaging repertoire drill sets or ensure tree generator extends leaf nodes by 1 ply.

---

## Must-Fix Blockers Before Launching Paid GPU Run

To ensure the multi-hour rented A100 GPU run is airtight, cost-effective, and produces a valid profile:

1. **Add `time` limit safety cap to `_do_analyze`:** In `backend/engine_manager.py:352-364`, pass `time` alongside `nodes` (`Limit(nodes=nodes, time=time_cap)`).
2. **Expose node limits for repertoire & gem calls:** In `backend/training/metrics.py`, add `repertoire_eval_nodes`, `gem_screen_nodes`, and `gem_confirm_nodes` to `TrainingConfig`. Set them in Cell 5b of `colab/diagnose_on_gpu.py`.
3. **Fix TS2 budget & summary math:** In `backend/training/pipeline.py:396-437`, scale `steer_search_budget` for GPU execution, and ensure `by_opening_steer` counts moves across all decision nodes regardless of budget exhaustion.
