# SPRINT 2 SPEC — LC0 Intuition Speed-Drill (Jobs 4 + 5)

Anchored in `GOAL_BOOK.md` J4/J5. **The loop:** show a position → user guesses **LC0's top
policy move** within ~10 s → reveal LC0's ranked policy (+ probabilities) → score → next.
~10-min daily session; track top-1 accuracy over time (the "policy-blindness ↓" metric, Q5.3).
Predictive, not passive (Q4.2). Lean, fast UI (user's bar).

## Grounded data (verified) — the drill runs on the cache, NO engine
- `store.EpdCache("policy")`: **2,234 positions**, each record `{"epd": str, "policy": [ {"uci",
  "san","from","to","p","q","n","wdl"}, ... up to 20 ] }`, **policy sorted DESC by `p`** (e.g.
  `d4 0.1274 > Nf3 0.1246`). This is LC0's move ranking with probabilities — exactly the guess target.
- **No eval** in this cache (`q=0.0`, `wdl=None`). So the reveal shows POLICY (the core); eval is
  optional/best-effort later. **Attention-hotspot prediction is DEFERRED** (a later enhancement; keep
  the MVP to move-prediction).
- `EpdCache` currently exposes only `.get(epd)` (backed by `._data` dict) — **no enumeration**.

## LEADER-PINNED MATH — scoring & sampling (implement VERBATIM; STOP + ask if a field is missing)
Given a position's `policy` (list, sorted desc by `p`) and a guessed UCI `g`:
- `top = policy[0]`; `top_uci = top["uci"]`.
- **`correct = (g == top_uci)`** (top-1 match — "the top policy choice", Q5.2).
- **`rank`** = 1-based index of the first policy entry whose `uci == g`, else `null` (guess not in
  LC0's top-20).
- `your_p` = that entry's `p` if found, else `0.0`. `top_p = top["p"]`.
- **Session accuracy = correct_count / total_guesses.** (Headline metric; lower policy-blindness = higher.)

**Sampling a session of `count` positions:**
- Eligible EPDs = cache records with `len(policy) >= 2` AND `policy[0]["p"] < 0.9` (skip near-forced
  positions — guessing a lone obvious move doesn't train intuition). `0.9` is a tunable constant.
- Uniform-random sample `count` eligible EPDs (no repeats within a session). If fewer than `count`
  eligible, return what's available.

## PHASE A (dispatch now) — backend `intuition.py` + `EpdCache.keys()` + routes + tests
**Worker task.**
1. `store.py`: add `EpdCache.keys() -> list[str]` returning `list(self._data.keys())` (tiny, non-metrics).
2. `backend/training/intuition.py`:
   - `build_session(count: int) -> list[dict]` → sample per the pinned rule; return `[{"epd", "fen"}]`
     ONLY (NO policy — the answer stays server-side; reconstruct fen from epd via a `chess.Board`,
     `board.set_epd(epd)` then `board.fen()`).
   - `score_guess(epd: str, uci: str) -> dict` → load `EpdCache("policy").get(epd)`; compute per the
     pinned math; return `{"correct", "rank", "your_move": {"uci","san","p"} | null, "top_move":
     {"uci","san","p"}, "top_policy": policy[:5]}` (reveal top-5 for the UI). 404-style `{}` if the
     epd isn't cached.
   - Stats: append each guess to `training/intuition_attempts.jsonl` (`{epd, uci, correct, rank, ts}`
     via `store._write_json_atomic`-style append) and `get_stats() -> {"total", "correct",
     "accuracy", "recent_accuracy"(last 50)}`.
   - Keep the `0.9` near-forced threshold + `top_k=5` reveal as named module constants.
3. `backend/app.py` routes: `POST /api/training/intuition/session {count:int}` → `build_session`;
   `POST /api/training/intuition/guess {epd:str, uci:str}` → `score_guess` (also logs the attempt);
   `GET /api/training/intuition/stats` → `get_stats`.
4. **Tests** (`backend/tests/test_intuition.py`), mutation-check mindset — each fails if its rule breaks:
   (1) `score_guess` correct=True only when guess == policy[0].uci; (2) `rank` is the right 1-based
   index, `null` for an off-list move; (3) sampling excludes `policy[0].p >= 0.9` and `len(policy)<2`;
   (4) `build_session` returns fen-only (no `policy` leaked); (5) accuracy = correct/total over a
   sequence of logged guesses; (6) `EpdCache.keys()` returns the loaded epds. Use a small synthetic
   `EpdCache` fixture (monkeypatch `store.TRAINING_DIR` to a tmp dir, or construct records directly).
- **Gates:** full suite green (165 + new); do NOT touch `metrics.py`; match the cache schema EXACTLY.
  No engine calls. No push. STOP for leader review. Report `SPRINT2_PHASE_A_REPORT.md`.

## PHASE B (spec after A lands + reviewed) — frontend `IntuitionDrill.tsx`
- Board (reuse the existing chessground/TrainingBoard) + a ~10 s countdown per position. User makes a
  move = their guess of LC0's top move; on move OR timeout → `POST /guess` → reveal LC0's top-5 policy
  as a labelled bar/list (san + p%), highlight hit/miss + the user's rank, brief "next" flow.
- Session of N positions with a running score + an end-of-session accuracy summary; a small
  accuracy-trend readout from `/stats`. New `'intuition'` view + tab in `TrainingTab` (mirror the
  existing view-switch pattern). Lean, no bloat; `npm test` + build green.

## Deferred (NOT this sprint) — note for later
- Attention-hotspot prediction (predict LC0's attended squares — uses the stage_b saliency cache).
- Eval display in the reveal (pull from stage_b where present).
- SRS on positions the user repeatedly misses (right now sessions are fresh random draws).

## Sequencing
Dispatch **Phase A only** now → leader audits (mutation-check the scoring + the answer-not-leaked
guarantee + sampling filter) → then Phase B. Same pinned/phased/audited flow as Sprint 1.
