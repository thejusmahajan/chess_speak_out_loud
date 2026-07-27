# Critical Points — training-surface design (thinking doc, pre-spec)

**Status:** leader design for user review. NOT a Gemini prompt yet. Per the "study/think before
delegating" principle, we settle the model here, then pin a spec.

Origin: the user's reframe (2026-07-27). We stopped trying to make a brittle *material* heuristic call
things "sacrifices." The real training unit is a **Critical Point** — a position where the user's move
gave up a **sizable advantage**, and the value is the missed **continuation** (a series of events), not a
single move or a theme tag. Grounded in **eval swing** (robust, already computed), which dissolves the
theme-tagging brittleness. Sacrifices become a small **sub-container**, not the frame.

---

## 1. What a Critical Point IS
A finding where `confirmation.swing_cp >= 200` (~≥2 pawns) — the search-confirmed amount of advantage the
user left on the table vs the objective-best continuation. Default threshold ≥200, user-adjustable.

**The set is free** (no engine needed to FIND them — `swing_cp` is stored). From the current 100-game
profile:
- ≥2p: **272** (~2.7/game) · ≥3p: 221 · ≥5p: 159 · ≥8p: 122 — all confirmed.
- **176 "blind"** (best move not even considered — richest) + 96 "missed."
- Two natural flavors: **surrendered edge** (200–499, 113) vs **missed decisive win** (≥800, 122).

## 2. The training unit — a continuation, not a move
For each Critical Point we show:
- the **critical line** (objective-best continuation) with its eval,
- **2–3 alternative lines** with evals (so the fork is visible),
- **the user's own move/line** highlighted, with its eval and the **divergence point** ("your `Nf3`
  (−0.4) left the critical `Bxh7` (+2.6); the paths fork here").
The line may or may not contain sacs / forced moves — irrelevant. The point is *where and why* the game's
fate turned.

## 3. The engine model — LAZY + CACHED + explicit re-run (user's design)
We do NOT batch-compute lines for all 272 upfront. Instead:
1. **On attempt/reveal:** when the user opens a Critical Point and submits a move, the backend checks the
   cache for this position (EPD). If absent, it runs **LC0 multipv** on `fen_before` (N≈3–4 lines) and a
   quick eval of the user's played move, assembles the verdict, and **stores it keyed by EPD**.
2. **Second visit = instant:** the stored verdict is served; the engine does not repeat the work.
3. **Explicit "investigate deeper":** a manual control re-runs with more nodes / more lines and updates
   the cache. Only then does the engine spend more time.
This matches the user's stated tolerance: *UI speed matters, analysis latency is fine.* "Prebuilt for
tactics" falls out for free — a warmup pass can pre-populate the cache for a chosen deck; the default
stays lazy-and-remembered.

## 4. Data & cache contract (reuse existing infra)
- Reuse `store.EpdCache` (already EPD-keyed, used for `"policy"` / `"stage_b"`). New namespace
  `"critical_lines"`.
- Verdict schema (pinned in the spec):
  ```
  { "epd": str, "computed_at": iso, "nodes": int, "multipv": int,
    "lines": [ {"rank": int, "first_uci": str, "first_san": str, "eval_cp": int, "pv_san": [str]} ],
    "played": {"uci": str, "san": str, "eval_cp": int, "diverge_ply": int} }
  ```
- Engine: LC0 `analyze` already emits multiple `pv_lines`; wrap a `critical_lines(fen, nodes, multipv)`
  around it. Nodes tuned for a few-second reveal (start ~ the playout budget, `PLAYOUT_NODES`≈4000).

## 5. Sacrifice as a SUB-container (not the frame)
Within Critical Points, flag the small subset whose critical line involves a genuine **material give-up**
(the validated ~4, or a strict live check on the computed multipv line: `pv[0]` is the give-up, committed
early, stays ≥2 down). It's a **badge/filter** for sac-vision training, never the primary label. This is
where the earlier sacrifice work lands — small and honest.

## 6. Reuse, don't rebuild
Critical Points is a **re-frame of the findings deck by swing**, so it plugs into what exists:
- Deck/drill machinery: `build_drill_from_finding`, the SRS-aware deck ordering (just fixed), the
  drill-solving UI (`DrillMode`). The drill's "reveal" gains the multipv lines + divergence.
- Ranking: swing × recurrence (usual-suspects clustering can group Critical Points by theme/opening as a
  secondary lens).
The genuinely NEW code is: the swing filter as a first-class surface, the on-attempt `critical_lines`
call + cache, and the "why" (divergence) display.

## 7. What this SUPERSEDES / drops
- **Phase C-B (wire the sacrifice surface): dropped** — replaced by Critical Points + sacrifice sub-badge.
- **Phase C-A motif re-tag: value shrinks to near-zero** for this surface (Critical Points need no motif
  tags). Keep `profile_retagged.json` + backup archived; do NOT swap it in on this account. (Removing the
  bogus 645× `advantage` is minor hygiene we can decide separately.)

## 8. Open decisions to pin BEFORE the spec
1. **multipv N**: 3 or 4 lines on top of the critical line?
2. **Reveal nodes**: latency vs quality for the on-attempt run (≈4000? higher?). Explicit "deeper" uses
   more.
3. **Divergence display**: show the user's full line (needs an extra engine PV from the played move's
   position) or just the played move's eval + the ply where it leaves the critical line?
4. **Flavor filter**: expose "surrendered edge" vs "missed decisive win" (≥800) as a toggle?
5. **Threshold default**: ≥200 confirmed; is that the right floor, or start stricter (≥300)?

## 9. Sequenced build (after decisions pinned)
- **CP-1 (backend, no UI):** `critical_points(profile, min_swing)` selector (pure, free) +
  `critical_lines(fen)` engine wrapper + `EpdCache("critical_lines")` + endpoint. Real-data gate: run on a
  few positions, confirm cache hit on 2nd call.
- **CP-2 (drill UX):** reveal shows critical line + 2–3 alts + your move + divergence; "investigate deeper"
  control. Reuse `DrillMode`.
- **CP-3:** sacrifice sub-badge + flavor filter. Then retire the old sacrifice-centric surfaces.
