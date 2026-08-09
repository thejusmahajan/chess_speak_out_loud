# TASK FOR GEMINI — Theme-Tagger Phase C: re-tag the stored profile, then wire the real sacrifice surface

Phase A (`977edaa`) fixed the tagger; Phase B (uncommitted) split *sharpness* from *sacrifice* and built
`select_missed_sacrifices` — but it's **dormant** because the stored `data/training/profile.json` still
holds the OLD bogus motifs (645/646 phantom `advantage`, 69 phantom `sacrifice`). Phase C makes the stored
profile correct **without a Kaggle re-run**, then wires the (now-real) sacrifices into a drill the user can
actually solve.

Read `docs/THEME_DEFINITIONS.md`, `docs/LICHESS_DEVIATIONS_REPORT.md`, and `THEME_TAGGER_FIX_SPEC.md`
FIRST. **Cite `file:line` for every change.** Reuse existing patterns — never re-derive material or ECO
logic. No push. **STOP at the CHECKPOINT for leader+user review before doing Phase C-B.**

---

## Two HARD facts (verified on the real profile — pin your logic to these, do not "fix" around them)

1. **Findings carry NO absolute evaluation.** `finding["best"] = {uci, san, p}` (`p` = policy prob, not
   eval); `finding["confirmation"] = {swing_cp, confirmed}` (`swing_cp` = the eval *swing* of the played
   move, NOT the position eval). So `analyze_pv`'s `cp` is **unrecoverable offline**. Therefore the
   eval-tier tags Lichess `cook()` always appends (`crushing`/`advantage`/`equality`, `cook.py:55-60`)
   **cannot be honestly reproduced — you MUST strip them from the re-tagged motifs, never fake them.**
   (Restoring correct eval-tier tags would need an engine re-run; out of scope. Stripping them is what
   finally removes the bogus 645× "advantage".)
2. **The sacrifice move is `pv_san[0]`, NOT `finding["best"]["uci"]`.** `best` is the *policy*-best move;
   `pv_san` is the *search* best-play line, and they differ (real example `g000-p023`: `best.san=Nxe5`,
   `pv_san=['e4',...]`). `cook()` flags a sacrifice from the **line** (`[setup_uci] + pv_san`), so the sac
   the user missed is the first move of that line = `pv_san[0]`. The drill solution in C-B is `pv_san[0]`
   (reconstructed to UCI from `fen_before`), NOT `best.uci`. Guessing `best.uci` here is WRONG.

---

# PHASE C-A — re-tag the stored profile (offline) + produce a human-validation dump

### C-A1. Backfill `pre_fen` + `setup_uci` per finding (reuse `eco_backfill.py`'s alignment)
Findings lack `pre_fen`/`setup_uci` (they predate Phase A). Rebuild them from the corpus:
- Reuse `eco_backfill.parse_game_idx_from_id` + the `game_map[idx] = {game, user_color, uci_moves, ...}`
  construction and the header cross-check / `find_game_by_headers` fallback (same alignment as
  `backfill_ecos`). Corpus PGN: the same path `backfill_ecos` is called with (confirm it; it's the
  `games_of_derdiedasdie/...pgn` used for the 100-game run).
- **Derive robustly, do NOT trust a fixed ply convention.** For each finding find the integer `k` such
  that replaying `uci_moves[:k]` yields a board whose FEN equals the stored `finding["fen_before"]`. Then
  `setup_uci = uci_moves[k-1]` and `pre_fen` = FEN after `uci_moves[:k-1]`. If no `k` matches (or `k==0`,
  a move-1 finding), set `setup_uci=None`, `pre_fen=None` and **log+count it as unresolved** (that finding
  re-tags to `set()` — acceptable). This replay==fen_before check is your ground-truth guard against
  off-by-one; report how many findings resolved vs unresolved.

### C-A2. Re-tag: run the corrected tagger, strip the un-recoverable eval tier
For each finding with `pre_fen`/`setup_uci`/`pv_san`: call
`MotifDetector.analyze_pv(pre_fen, setup_uci, pv_san, cp=0)` (Phase A's corrected signature), then
**remove `{"crushing","advantage","equality"}`** from the result. Overwrite `finding["motifs"]` with the
cleaned set (keep it a list, stable order). Recompute `aggregates["by_motif"]` from the new motifs
(same shape it currently has: `{motif: {blind, missed, ...}}` — match the existing structure exactly;
inspect it first, don't invent fields).

### C-A3. Migrate the renamed keys in the stored profile
The stored `steer_findings` + `aggregates` still use the OLD keys. Migrate in place:
`had_tal_move`→`had_sharp_move`, `tal_move`→`sharp_move` (inside each steer finding), and
`tal_moves`→`sharp_moves` in `aggregates`/`by_opening_steer`. (This is what lets the Phase-B-renamed
consumers read the stored profile. After this, the transitional `tal_moves` fallbacks become dead — leave
them; leader removes them at commit.)

### C-A4. SAFETY — never clobber the live profile
Implement re-tag as a **pure function** `retag_profile(profile: dict, pgn_path: str) -> (dict, report)`
(input dict in, new dict out, no I/O inside). The driver script must: (a) back up the current
`data/training/profile.json` to `profiles/profile_pre_retag_<YYYY-MM-DD>.json` FIRST; (b) write the result
to a **NEW** file `data/training/profile_retagged.json`; (c) **NOT overwrite the live profile** — the
leader does the swap after reviewing the dump. (Per project memory, `profile.json` is fragile and the real
one is archived in `profiles/` — respect that.)

### C-A5. THE VALIDATION DUMP (this is the gate — the user personally checks it)
Write `data/training/retag_report.md` containing:
- **Before→after motif distribution**: the top ~12 motif counts before (bogus) and after (corrected),
  so the 645×`advantage` / 69×`sacrifice` collapse is visible.
- **Every "sacrifice you missed"** (findings whose corrected motifs include `"sacrifice"`), as a readable
  table: game (`white` vs `black`, `date`), move number, **the sac move in SAN (= `pv_san[0]`)**, the full
  `pv_san` line, and `fen_before`. Count them.
- Resolved/unresolved backfill counts from C-A1.
This dump is what proves (or disproves) that the corrected detector finds REAL sacrifices in the user's
games. Do not editorialize — just present the positions.

### C-A6. Tests (`test_retag.py`) — synthetic fixtures, mutation-checked
1. A synthetic finding whose reconstructed line is a real material sac (e.g. a Greek-gift `pv_san`) →
   after `retag_profile`, its motifs include `"sacrifice"` and exclude `advantage/equality/crushing`.
2. A finding whose line WINS material → motifs do NOT include `"sacrifice"`.
3. Eval-tier strip: assert no re-tagged finding carries `crushing/advantage/equality`.
4. Key migration: a profile with `had_tal_move`/`tal_moves` → after retag has `had_sharp_move`/`sharp_moves`
   and NOT the old keys.
Real-data run = executing the driver on the real profile and producing C-A5's dump (paste its head).

## ⛔ CHECKPOINT — STOP HERE for leader + user review
Do NOT proceed to C-B. The leader reviews `retag_report.md` with the user to confirm the re-tagged
sacrifices are real. Wiring a surface onto unvalidated tags would repeat the original mistake. Only after
the user validates does the leader swap in `profile_retagged.json` and release C-B.

---

# PHASE C-B — wire the real sacrifice surface (ONLY after the checkpoint passes)

### C-B1. Sac-drill builder (solution = `pv_san[0]`, per HARD fact #2)
Add a builder that turns a missed-sacrifice finding into a solvable drill where `solution_uci`/
`solution_san`/`line_uci` come from the **first move of `pv_san`**, reconstructed to UCI by walking the
SAN line from `chess.Board(fen_before)` (same SAN→move conversion `analyze_pv` uses). Reuse
`build_drill_from_finding`'s reveal shape (policy/saliency/pv_san/motifs) but override the solution to the
sac move. Tags must include `"sacrifice"`.

### C-B2. Endpoint
`GET /api/training/missed_sacrifices` (optional `eco`) → `sac_drill.select_missed_sacrifices(eco=...)` →
map through the C-B1 builder → return the drill list (solutions server-side, same privacy contract as
`build_sac_session`). Wire in `app.py` next to the existing `sac_drill` endpoints (`app.py:821-855`).

### C-B3. Frontend surface — "Sacrifices You Missed"
Add an entry point that fetches the endpoint and presents the positions in the **existing** drill-solving
UI (reuse `DrillMode`/the board component — do NOT build a new solver). The reveal must show the "why":
"this is a real material sacrifice (Lichess `cook`) — the line: <pv_san>", distinguishing it clearly from
the *sharp* surfaces. Keep it lean.

### C-B4. Tests + real-data check
Unit: the C-B1 builder sets `solution_uci == uci(pv_san[0])` for a fixture finding (mutation: fails if it
uses `best.uci`). Endpoint test (fast, no engine). Frontend: a vitest that renders the fetched deck. Real
run: hit the endpoint against the swapped-in profile; confirm it returns the validated sacrifices.

---

## Constraints & gates
- Do NOT touch `backend/training/metrics.py` (leader-owned). Reuse `lichess_tagger` (never re-derive
  material), `eco_backfill` alignment, `build_drill_from_finding`. Ground themes in `THEME_DEFINITIONS.md`.
- Never overwrite the live `profile.json`; the leader swaps after the checkpoint.
- Backend + frontend suites green; add the C-A6/C-B4 tests; `npm run build` clean. No push.
- Report: `file:line` for every change, resolved/unresolved counts, the 3+ mutation tests + why each fails
  on the wrong behavior, confirmation `metrics.py` untouched, and — for C-A — the head of `retag_report.md`.
  **STOP at the CHECKPOINT; do not start C-B until released.**
