# CLAUDE OPUS 4.6 WORKER SPEC — Elite Training System (Phases C1–C3)

> **You are Claude Opus 4.6, the precision worker.** Your token budget is limited, so
> this spec is self-contained: everything you need is here plus the two files it tells
> you to read. **Read only:** `TRAINING_SYSTEM_PLAN.md` (§2–§6 especially) and
> `backend/training/metrics.py` (the normative math — import it, never re-derive).
> Skip Gemini's spec unless reviewing (C3). Branch `windows-dev`; python
> `C:\Users\Admin\miniconda3\envs\cszero\python.exe`; commit per phase
> (`[training] C<n>: …`); log each phase's verification output in `WORKLOG_TRAINING.md`.

**You own:** `backend/training/gems.py`, `backend/training/select_repertoire.py`,
`backend/tests/test_training_gems.py`, `test_training_select.py`.
**Never edit:** `metrics.py`, Gemini's files (`store.py`, `pipeline.py`, `puzzle_db.py`,
`openings.py`, `drills.py`, app.py, frontend) — in C3 you review them and report;
Gemini applies fixes (trivial one-liners excepted, noted in the worklog).

Oracle APIs (verified by the leader; signatures in plan §2): `engine.analyze`,
`engine.get_policy_distribution`, `vision.saliency_absolute(fen)` (absolute frame,
both colors), `MotifDetector.analyze_pv(fen, pv_san_list)`.

---

## C1 — Hidden-gem detector (`backend/training/gems.py`)

`async def scan_for_gems(fens: list[str], engine, vision, cfg=DEFAULT_CONFIG, max_bt3: int = 100) -> list[dict]`

Filter funnel, **cheapest test first**, so the BT3 budget (`max_bt3` forwards, ~1.5s
each) is spent only on survivors:
1. Dedupe by `chess.Board(fen).epd()`.
2. **Policy gate:** `get_policy_distribution(fen, nodes=1)`; require
   `policy[0]["p"] >= cfg.gem_top_prior`. Empty policy (mock mode) → skip fen.
3. **Quiet gate:** `analyze(fen, depth=None, multipv=1, time_limit=0.8)`;
   require `metrics.is_quiet(result["evaluation"], cfg)`.
4. **Attention gate (BT3, budgeted):** `vision.saliency_absolute(fen)` →
   `metrics.is_hidden_gem(evaluation, policy, saliency, cfg)`; keep if `["gem"]`.
5. For each gem, one confirmation search `analyze(fen, depth=None, multipv=2,
   time_limit=3.0)` and return:
   `{"fen", "side_to_move", "policy", "saliency", "gem_stats": <is_hidden_gem dict>,
     "solution_uci" (top policy move), "alt_solution_ucis" (metrics.alt_solutions),
     "solution_san", "pv_san": pv_lines[0].split(), "eval_cp": evaluation,
     "motifs": sorted(MotifDetector.analyze_pv(fen, pv_san))}`
Stop scanning when `max_bt3` forwards are used. Pure orchestration — every judgment
comes from `metrics`. Also provide `gem_candidates_from_profile(profile) -> list[str]`
(fens of NON-flagged user moves are not stored, so use each finding's `fen_before`
neighbors is impossible — instead accept any fen list; Gemini's `drills.py` supplies
candidates from user games' quiet middlegame positions, ply 15–60).

**Verify:** `backend/tests/test_training_gems.py` with a fake engine/vision (stub
objects returning canned dicts) covering: funnel order (BT3 never called for a fen that
fails the policy gate — assert via call counting), `max_bt3` respected, mock-mode skip,
output schema. Run: `…python.exe -m pytest backend/tests/test_training_gems.py -q`.

## C2 — Repertoire backwards-selection (`backend/training/select_repertoire.py`)

*Depends on Gemini's G2 (`puzzle_db.py`) and G3a (`openings.py`) — check
`WORKLOG_TRAINING.md` that both gates passed; else do C1/C3 first.*

`async def build_repertoire(profile: dict, color: str, engine, top_n: int = 5) -> dict` (plan §6.2):
1. **Targets:** top 3 motifs from `profile["aggregates"]["by_motif"]` ranked by
   `2*blind + missed` (these weights, exactly).
2. **Candidates:** for each target motif, `puzzle_db.opening_tags_ranked(motif)`;
   union, keep tags mappable to an ECO line via `openings` (first-move color must match
   `color`). Score = Σ over targets of `weight_t × motif_profile(tag)[t]`.
3. **Sharpness+soundness gate** on the ~15 best candidates only (engine budget):
   `analyze(tabiya_fen, depth=None, multipv=1, time_limit=2.0)` → require
   `abs(metrics.eval_cp_number(evaluation)) <= cfg.sound_eval_cp` (white-POV sign
   flipped appropriately for black repertoires: the line must not be WORSE than
   −sound_eval_cp for the repertoire color) and `metrics.sharpness_from_wdl(wdl)["sharp"]`
   when wdl is present.
4. Emit top_n recommendations with the deterministic rationale template:
   `"Play the {name} ({line_pgn}). Structures from this opening produce {motif} in
   {pct}% of tagged master-game puzzles; LC0 holds the tabiya at {cp}cp with a
   {draw_pct}% draw share — sharp enough to force the patterns you miss."`

**Verify:** `test_training_select.py` with stubbed `puzzle_db`/`openings`/engine:
ranking weights, color filtering, soundness sign-handling for black, budget cap
(≤15 engine calls). Then one real run against the live puzzle DB if G2 is merged;
paste the top recommendation into `WORKLOG_TRAINING.md`.

## C3 — Review sweep of Gemini's work (after each Gemini gate, or batched)

For each of G1–G5, read the diff (`git log/diff` on `[training] G<n>` commits) and check
specifically — these are the historical Gemini failure modes:
1. **Metric re-derivation** — any inline thresholds or formulas duplicating `metrics.py`.
2. **Frame bugs** — any call to `vision.saliency()` or `_attention_saliency` instead of
   `saliency_absolute`; any white/black POV sign error in `confirmation_swing` usage.
3. **PV format** — `pv_lines[0]` must be `.split()` before `analyze_pv`.
4. **Lichess puzzle format** — `Moves[0]` must be treated as the opponent's setup move.
5. **Mock-mode leaks** — empty policy or mock analyze results reaching profile/drill files.
6. **Engine discipline** — no second LC0 spawned; batch work uses the app singletons;
   BT3 call counts bounded as specced.
7. **Hallucinated APIs** — every oracle call matches plan §2 signatures exactly.
Report findings as a checklist in `WORKLOG_TRAINING.md` (file:line, severity,
suggested fix). Gemini fixes; you re-verify. When all clear, run the end-to-end gate
(G4's HTTP transcript) yourself once and sign off: `C3 SIGN-OFF: <date>`.

---

# EPOCH II — Tactical Steering (Opus phases TS3, TS5)

> **Design is authoritative in `TRAINING_ROADMAP.md` → "Epoch II — Tactical
> Steering".** Read that section and `backend/training/metrics.py` (the
> normative math — import `tactical_complexity`, `steer_candidates`; never
> re-derive). If those symbols are absent, STOP: TS3 depends on TS1 (leader).
> **You own:** `backend/training/select_repertoire.py`, `test_training_select.py`.
> **Never edit:** `metrics.py`, `pipeline.py`, `drills.py`, `gems.py`, app.py,
> frontend. Branch `windows-dev`; commit `[training] TS<n>: …`; log gate
> output in `WORKLOG_TRAINING.md`.

## TS3 — Style-rooted tactical repertoire (`select_repertoire.py`)

Retire the `SACRIFICE_TARGETS` target-selection (the roadmap explains why —
it is the "random attacking openings" the user rejected). Keep the
soundness/sharpness gate (`sound_eval_cp`, `sharpness_from_wdl`) and the
`build_repertoire(profile, color, engine, style=...)` signature. New logic:

1. **Mine the ingrained repertoire.** From `profile["aggregates"]["by_opening"]`
   take ECOs the user actually reaches with `≥ cfg.repertoire_min_moves`
   played moves, of the requested `color`. These — not a canned list — are the
   candidate base openings.
2. **Classify each base opening:**
   - `leaky` if it has Track A `findings` (mistakes) in that ECO → mark as a
     **repair** target (the rec should point at the corrected line).
   - `dry` if its `steer_summary` complexity (from TS2, if present on the
     profile) is low → deprioritize or suggest a sharper sound sibling within
     the same opening family.
   - else `sound-keep`.
3. **Tactical tint.** For a base opening's tabiya (via `openings.tabiya_fen`),
   gather `multipv` for the top few moves and call `steer_candidates` to find
   the sound-but-sharper continuation within `cfg.steer_max_loss_cp`. That
   branch is the tint. Engine budget: reuse the existing `MAX_ENGINE_CALLS`
   cap; time via `cfg.repertoire_eval_seconds`.
4. **Recommendations** carry: base opening (theirs), `origin:
   kept|repaired|tinted`, the tint/repair move, `complexity`, `eval_cp`,
   `eval_loss_cp` (the bound proof), `draw_pct`, rationale assembled from JSON
   fields (NO LLM). Still drop anything failing sound+sharp.

If `steer_candidates`/`steer_summary` are unavailable (TS1/TS2 not merged),
build the kept/repaired classification only and note the missing tint in the
worklog — do NOT fall back to `SACRIFICE_TARGETS`.

**Gate TS3:** `test_training_select.py` covers: (a) a profile whose by_opening
has a leaky ECO → that ECO appears as `origin:"repaired"`; (b) a mocked
engine (like the existing test's `analyze` stub, now returning `wdl`) yields a
`tinted` rec whose `eval_loss_cp ≤ steer_max_loss_cp`; (c) no rec has
`eval_cp` below the loss bound. Paste pytest output. Then a live build over
HTTP for `weakness`+`sacrificial`/both colors on the real profile; paste the
recommendations (must be openings the user actually plays). Commit
`[training] TS3: style-rooted tactical repertoire`.

## TS5 — Interlock review (report + guardrail audit)

After Gemini's TS2/TS4 land, produce the reconciliation the roadmap names:
per opening, Track A error rate beside Track B steer-opportunity density, so
repair-vs-tint is legible. As the review sweep (like C3): read Gemini's TS2/
TS4 diffs and verify the two guardrails held on a REAL profile —
(1) no `steer_finding`/steer drill with `eval_cp < steer_min_eval_cp` (no
losing steers), (2) no sound opening sideline flagged as a Track A mistake
(spot-check `is_opening_mistake` behaviour on the user's pet lines). Report
findings in `WORKLOG_TRAINING.md`; Gemini applies non-trivial fixes, you may
apply one-liners. Leader signs off.
