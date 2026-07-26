# SPRINT 3 SPEC — Sacrifice / Tactical-Landmine Training (Jobs 1 + 7)

Anchored in `GOAL_BOOK.md` J1/J7 — the sacrificial/Tal training the user cares about most.
Core cure for the hesitation (Q7.1 "I can't foresee the advantage a sac produces"): **find the
sac in your own positions, and SEE that it's sound.** Runs on cached `steer_findings` (no engine,
no KB gate). Lean UI.

## Grounded data (verified)
- Profile `steer_findings`: **562 total, 176 with `had_tal_move == true`** (the Tal-style sacs LC0
  found in the user's positions). Each: `id` (e.g. `"s-000-p023"`), `fen_before`, `best`
  {san,eval_cp,complexity,components}, `steer` {san,uci,eval_cp,complexity,components} (=the
  **tal/sac move** when had_tal), `playable_candidates` [{uci,complexity,eval_cp}], `eval_loss_cp`,
  `opening`.
- **No tactical THEME** on steer_findings, and `lichess_tagger` is not a position→theme fn. So the
  J7 "pick the theme from a list" step is **DEFERRED** to the theme-KB (Sprint 5).
- Play-out-vs-LC0 (J1.2, the user's most-wanted piece) needs the **live engine** → **Phase C**.

## LEADER-PINNED — selection & scoring (implement VERBATIM; STOP + ask if a field is missing)
**Selection (the "landmines"):** from `steer_findings`, keep those with `had_tal_move == true`.
Rank by `steer.complexity` DESC (sharpest first). Dedupe by board EPD.
**Scoring a guess `g` (uci) against a steer_finding `sf`:**
- `sac_uci = sf["steer"]["uci"]`; `alt = { c["uci"] for c in sf["playable_candidates"] }`.
- **`correct = (g == sac_uci)`** (found LC0's sac). **`acceptable = (g in alt and not correct)`**
  (a sound alternative sharp move). Else a miss.
- **Soundness reveal** (the cure — show the sac is a good *practical* try): `safe = sf["best"]`
  (the timid move), `sac = sf["steer"]`, `eval_loss_cp` (how much objective eval the sac concedes —
  usually small), and the framing: *"You'd safely play {safe.san} ({safe.eval_cp}cp). The sac
  {sac.san} concedes only {eval_loss_cp}cp but goes into a far sharper position (complexity
  {sac.complexity}) where the opponent is likely to go wrong."* (Honest: the sac is often slightly
  worse objectively but far stronger practically — do NOT claim it "wins".)
- Session accuracy = (correct) / total; track `acceptable` separately as "sound-alt" rate.

## PHASE A (dispatch now) — backend `sac_drill.py` + routes + tests
1. `backend/training/sac_drill.py`:
   - `build_sac_session(count: int) -> list[dict]` → load profile, select per the pinned rule,
     sample `count`, return `[{"id", "fen"}]` ONLY (answer server-side; fen from `fen_before`).
   - `score_sac_guess(finding_id: str, uci: str) -> dict` → look up the steer_finding by `id`
     (build an index `{sf["id"]: sf}` from `profile["steer_findings"]`); compute per the pinned math;
     return `{"correct", "acceptable", "sac_move": {uci,san,eval_cp,complexity}, "safe_move":
     {san,eval_cp}, "eval_loss_cp", "playable_candidates": [...]}`; `{}` if id not found. Log the
     attempt to `training/sac_attempts.jsonl`.
   - `get_stats() -> {"total","correct","acceptable","accuracy","recent_accuracy"}` (last 50).
   - Constants: none needed beyond the reveal top-k of playable_candidates.
2. `backend/app.py` routes: `POST /api/training/sac/session {count}`, `POST /api/training/sac/guess
   {finding_id, uci}`, `GET /api/training/sac/stats`.
3. **Tests** (`backend/tests/test_sac_drill.py`), mutation-check mindset — each fails if its rule
   breaks: (1) selection includes ONLY had_tal_move=true; (2) `correct` iff guess==steer.uci;
   (3) `acceptable` iff guess in playable_candidates and not the sac; (4) session payload has NO
   answer (no steer/best/eval keys — only id+fen); (5) accuracy = correct/total over logged guesses;
   (6) unknown finding_id → `{}`. Synthetic profile fixture (monkeypatch `store.load_profile`).
- **Gates:** full suite green (171 + new); do NOT touch `metrics.py`; match the schema EXACTLY; no
  engine calls. No push. STOP for leader review. Report `SPRINT3_PHASE_A_REPORT.md`.

## PHASE B (spec after A) — frontend `SacDrill.tsx`
- Reuse `TrainingBoard` (interactive, `onMove` = the guess). Prompt: **"A strong sacrifice is
  available here — find it."** On move → `POST /sac/guess` → **soundness reveal panel**: the sac move
  vs the safe move with evals, `eval_loss_cp` framed as "the sac costs only Xcp of objective eval",
  complexity, and a clear HIT / sound-alternative / miss banner. Session score + lifetime stats from
  `/sac/stats`. New `'sacrifices'` view + "Train Sacrifices" tab in `TrainingTab` (mirror the pattern).
  Lean; reuse the board; `npm test` + build green.

## PHASE C (later — needs the LIVE engine) — play out the attack vs LC0
After the user finds the sac, let them **play the attacking side while LC0 defends** for 3–5 moves
(J1.2/Q7.2 — "feel the compensation"). Backend endpoint drives `lc0_engine` to reply; frontend
continues the line on the board. Specced separately once A+B land (heavier: live engine per move).

## Deferred (NOT this sprint) — noted for later
- "Pick the tactical theme from a list" (J7 step 4) — needs a theme source = **Sprint 5 theme-KB**.
- Master-DB example games (J1) — needs the master-DB source decision (Lichess Masters API vs local
  PGN; open question in GOAL_BOOK).
- Similarity-based testing with loss-scaled penalty (Q7.3) — needs config similarity (KB-adjacent).

## Sequencing
Dispatch **Phase A only** → leader audits (mutation-check selection=had_tal-only, scoring, and the
no-answer-leak) → Phase B → then Phase C (engine). Same pinned/phased/audited flow.
