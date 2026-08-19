# WORKER TASK — CP-1: Critical Points backend (selector + lazy cached multipv lines + endpoints)

**Worker:** Opus 4.6 (fallback: Gemini). **Token discipline:** every codebase fact you need is INLINED
below — do NOT re-Read/Grep to rediscover signatures, schemas, or "how-to"s; spend tokens on the actual
code. If you run low, STOP at a phase boundary (CP-1a / CP-1b / CP-1c), write a `## HANDOFF` note (done +
exact next step + any file:line), and a fresh worker/Gemini continues. Partial-but-clean is fine.

Design context: `CRITICAL_POINTS_DESIGN.md`. This builds the **backend only** (no UI = CP-2). A
"Critical Point" = a finding where the user gave up ≥2 pawns (`swing_cp >= 200`); the training value is the
missed **continuation**, shown as the critical line + alternatives + the user's own line, with evals. The
SET is free (stored `swing_cp`); the engine only ever computes the **lines**, lazily, cached by position.

Ground rules: do NOT touch `backend/training/metrics.py` (leader-owned). Suite stays green. No push. STOP
for leader review. Cite `file:line` for edits.

---

## INLINED FACTS (this is your reconnaissance — do not re-derive)

**Finding shape** (`profile["findings"][i]`, from `data/training/profile.json`):
```
{ "id": "g000-p023", "ply": 23, "user_color": "white"|"black",
  "fen_before": "<FEN, user to move>",
  "played": {"uci": "...", "san": "...", "p": 0.27},
  "best":   {"uci": "...", "san": "...", "p": 0.13},
  "move_number": 12, "opening": {"eco": "...", "name": "..."},
  "confirmation": {"swing_cp": 320, "confirmed": true},   # <-- swing_cp lives HERE
  "pv_san": ["e4","d4",...], "motifs": [...], "severity": "blind"|"missed" }
```
Profile load: `from backend.training import store; profile = store.load_profile()` (returns the dict or None).

**EpdCache** (`backend/training/store.py`): persistent EPD→record jsonl cache.
```
from backend.training import store
cache = store.EpdCache("critical_lines")   # file: data/training/cache/critical_lines.jsonl
rec = cache.get(epd)          # -> dict or None
cache.put(epd, payload)       # appends {**payload, "epd": epd}; on reload last-write-wins
```
EPD from a FEN: `import chess; epd = chess.Board(fen).epd()`.

**Engine** — `lc0_engine` is a module-global in `backend/app.py`; endpoints pass it in (see pattern below).
`await lc0_engine.analyze(fen, multipv=3, nodes=None, time_limit=2.0)` returns:
```
{ "evaluation": <int cp | "M5"/"M-3">,        # WHITE-POV, from the top line
  "best_moves": [ {"move": uci, "san": san, "score": <int cp | "Mn">, "nodes": int, "wdl": [...]}, ... ],
  "pv_lines":  [ "<SAN SAN SAN ...>", ... ],   # ALIGNED with best_moves BY INDEX (line i = best_moves[i] + pv_lines[i])
  "nodes": int }
```
So line `i`: first move = `best_moves[i]["move"]`/`["san"]`, per-line WHITE-POV eval = `best_moves[i]["score"]`,
full continuation SAN = `pv_lines[i]`. In **mock/dev** mode `analyze` returns `best_moves: [], pv_lines: []`
(check `lc0_engine.is_available()` is False) — handle it (see CP-1b).

**Eval normalization** (`backend/training/metrics.py`, READ-only use):
`metrics.eval_cp_number(evaluation) -> Optional[int]` — WHITE-POV cp; mate `"M5"`→`+10000`, `"M-3"`→`-10000`.
To convert WHITE-POV → the mover's POV: `mover_cp = white_cp if user_color=="white" else -white_cp`.

**Endpoint pattern** (`backend/app.py`, ~line 821+; Pydantic request models are defined near the other
`*Request` classes — grep `class SacSessionRequest` region and add yours alongside):
```
@app.post("/api/training/sac/playout/start")
async def sac_playout_start(req: SacPlayoutStartRequest):
    res = await sac_drill.start_sac_playout(req.finding_id, lc0_engine)   # <-- lc0_engine passed in
    ...
```

**Reuse:** `build_drill_from_finding(f, source=...)` exists in `backend/training/drills.py` if you want the
standard drill shape — but for CP-1 a thin item list is enough (UI is CP-2).

---

## CP-1a — selector (pure, NO engine). Do this first; trivial.
New file `backend/training/critical_points.py`:
```
def select_critical_points(profile: dict | None, min_swing: int = 200) -> list[dict]:
    # findings where confirmation.swing_cp >= min_swing, sorted by swing_cp DESC.
    # profile None -> store.load_profile(); guard missing/empty -> [].
```
Return the raw finding dicts (caller shapes them). Sort stable by `-swing_cp`.

## CP-1b — the lazy + cached multipv verdict (the meat)
In `critical_points.py`:
```
async def critical_lines(fen_before: str, played_uci: str, user_color: str,
                         lc0_engine, multipv: int = 4, nodes: int = 4000,
                         force: bool = False) -> dict
```
Logic:
1. `epd = chess.Board(fen_before).epd()`. `cache = store.EpdCache("critical_lines")`.
2. If `not force`: `hit = cache.get(epd)`; if `hit`, return `hit` (INSTANT — no engine).
3. Else run the engine (2 calls):
   - `a = await lc0_engine.analyze(fen_before, multipv=multipv, nodes=nodes)`.
     If `not a.get("best_moves")` → engine is mock/unavailable → **return `{"error": "engine_unavailable"}`
     and do NOT cache** (so a real engine later can fill it).
     Build `lines` from aligned `best_moves`/`pv_lines`: for each i →
     `{"rank": i, "first_uci": best_moves[i]["move"], "first_san": best_moves[i]["san"],
       "eval_cp": mover_cp(best_moves[i]["score"], user_color), "pv_san": pv_lines[i].split()}`.
   - user's line: `b = chess.Board(fen_before); b.push_uci(played_uci); fen_after = b.fen();`
     `pa = await lc0_engine.analyze(fen_after, multipv=1, nodes=nodes)`.
     `played = {"uci": played_uci, "san": <san of played on fen_before>,
                "eval_cp": mover_cp(pa["evaluation"], user_color),   # note: after user's move it's OPPONENT to move;
                                                                     # keep eval in the USER's POV (same flip) so it compares to lines
                "pv_san": (pa["pv_lines"][0].split() if pa.get("pv_lines") else [])}`.
   - `diverge_ply`: 0 if `played_uci != lines[0]["first_uci"]` (the fork is the move itself); else compare
     `played["pv_san"]` vs `lines[0]["pv_san"]` and set the first index they differ.
4. `verdict = {"epd": epd, "computed_at": <utc iso>, "nodes": nodes, "multipv": multipv,
              "lines": lines, "played": played, "diverge_ply": diverge_ply}`.
   `cache.put(epd, verdict)`; return it.
Where `mover_cp(white_eval, color) = (lambda w: w if color=="white" else -w)(metrics.eval_cp_number(white_eval) or 0)`.

## CP-1c — endpoints (`backend/app.py`)
- `POST /api/training/critical/points` body `{min_swing?: int}` → `select_critical_points(store.load_profile(),
  min_swing or 200)` → return a thin list `[{"id","fen_before","swing_cp","played","best","move_number",
  "user_color","opening"}]`.
- `POST /api/training/critical/lines` body `{finding_id: str, force?: bool}` → look up the finding by id in
  the profile; if not found → 404. Else `await critical_points.critical_lines(f["fen_before"],
  f["played"]["uci"], f["user_color"], lc0_engine, force=req.force or False)`. If result has `error` →
  return it (200 with the error field, like the sac endpoints do).
  Add Pydantic request models next to the existing `*Request` classes.

---

## Tests (`backend/tests/test_critical_points.py`) — mutation-checked, NO real engine
1. **Selector**: profile with swing 150/250/900 → `select_critical_points(p, 200)` returns the 250 & 900
   findings, sorted 900 then 250; the 150 excluded. (Mutation: fails if the threshold or sort is wrong.)
2. **Cache proof** (the key gate): a **fake engine** stub with an `async analyze` that increments a
   call-counter and returns canned `best_moves`/`pv_lines`. Call `critical_lines(...)` TWICE for the same
   fen → assert the verdict matches AND **the stub was invoked only on the FIRST call** (2nd is a cache
   hit). Use a `tmp_path` `CSZERO_DATA_DIR` so the cache file is isolated (see how `test_suspects_deck.py`
   sets `store.DATA_DIR`/`TRAINING_DIR`). (Mutation: fails if the cache is bypassed.)
3. **Eval POV**: `user_color="black"`, stub returns white-POV `score=+300` → assert the line's `eval_cp`
   is `-300` (mover POV). (Mutation: fails if the color flip is dropped.)
4. **Mock-safe**: stub returns empty `best_moves` → `critical_lines` returns `{"error":"engine_unavailable"}`
   and writes NOTHING to the cache (assert `EpdCache("critical_lines").get(epd) is None`).

Leader will run the real-engine smoke separately; your stub tests are the gate.

## Gates
Backend suite green (`... -m pytest backend/tests`), add the 4 tests, no `metrics.py` edits, no push.
Report: `file:line` for each change, the 4 tests + why each fails on the wrong behavior, and confirm the
cache-hit test proves the 2nd visit skips the engine. STOP for leader review.
