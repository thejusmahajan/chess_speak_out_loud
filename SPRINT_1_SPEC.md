# SPRINT 1 SPEC — "Usual Suspects": recurring-weakness detection → review/approve → drill deck

Anchored in `GOAL_BOOK.md` (J6+J8, the user's #1). **Confirmed decisions:** manual-PGN
ingestion; recurrence = **frequency × severity, 2+ game floor**; his **exact game positions**;
**automated identification + human review/approve gate**; **severity-weighted blended** deck;
**mastery = OTB recognition** (metric: 90% on re-tests over 30 days); fast lean UI.

## Reuse map — what ALREADY exists (DO NOT rebuild)
- `backend/training/drills.py`: `generate_drill_set(count, profile, repertoire, engine, vision,
  steer_weight)` builds drills FROM findings (drill.origin.finding_id links back); `check_attempt`
  judges a move (Lichess rules).
- `backend/training/attempts.py`: working **SM-2-lite SRS** — `record_attempt(set_id, drill,
  correct)`, `due_drills()`, `load_srs()`, `escalate_regressions(profile)`; state in `srs.json`.
- API: `/api/training/drills/generate|attempt`, `/api/training/drills`, `/api/training/drills/{id}`,
  `/api/training/weakness-ranking`.
- Frontend: `DrillMode.tsx({setId,dueItems,onExit})` (drill runner, reveal, attempt), `WeaknessRanking.tsx`,
  `api/training.ts` (`generateDrills`, `getDrillsList`, `ProfileData` types incl. steer).
- `metrics.weakness_ranking_all(profile, n)` → rankings by {openings, phase, clock} (LEADER-owned).

## The GAP Sprint 1 fills
1. **Recurrence clustering by tactical THEME** → a ranked "usual suspects" list (metrics rank by
   opening/phase/clock only; nothing clusters recurring *themes* across games with member positions).
2. **Review/approve gate** (drills are currently auto-generated with no approval — Q4 wants approval).
3. **Deck from APPROVED suspects**, severity-weighted blend, feeding the existing SRS/DrillMode.
4. **Dashboard**: weakness / opening / tactical-theme-needing-attention (Q8.3).
Deferred to Sprint 1.5: the longitudinal "re-diagnose new games, prove mistakes drop" loop (Q5).

---

## LEADER-PINNED MATH — the "Usual Suspects" clustering (implement VERBATIM; do not invent)
This is the metric source of truth. Implement it exactly; if any input field is missing/ambiguous,
STOP and file in `QUESTIONS_FOR_LEADER.md` — do NOT guess.

**Inputs** — from `profile.findings[]`, each finding `f` has (verified schema):
`f["id"]` (e.g. `"g014-p026"` — the `g<NNN>` prefix is the GAME KEY), `f["motifs"]` (list),
`f["severity"]` (`"missed"`|`"blind"`), `f["confirmation"]["swing_cp"]` (int),
`f["confirmation"]["confirmed"]` (bool), `f["opening"]["eco"]`, `f["game"]`, `f["fen_before"]`.

**Step 1 — trainable theme tags.** Define a tunable constant
`GENERIC_MOTIFS = {"advantage", "veryLong", "quietMove"}` (ubiquitous context tags — they sit on
~all findings, so they are NOT trainable themes). A finding's **themes** = `set(f["motifs"]) −
GENERIC_MOTIFS`. Everything else in the motif vocabulary IS a trainable theme (sacrifice, fork,
discoveredAttack, exposedKing, clearance, castling, defensiveMove, rookEndgame, advancedPawn,
hangingPiece, doubleAttack, pin, skewer, …). A finding may belong to MULTIPLE theme-clusters.

**Step 2 — cluster by theme.** For each theme `T`, `F_T` = all findings whose themes contain `T`.

**Step 3 — per-cluster metrics.**
- `game_key(f)` = the `g<NNN>` prefix of `f["id"]`. `games(T)` = number of DISTINCT game_keys in `F_T`.
- `occ(T)` = `len(F_T)`.
- Per-finding severity: `sev(f) = min(f.confirmation.swing_cp, 800) * (1.0 if f.confirmation.confirmed else 0.5)`.
  (Cap at 800cp so one huge blunder can't dominate; unconfirmed count half.)
- `mean_severity(T)` = mean of `sev(f)` over `F_T`.
- **`rank_score(T) = games(T) * mean_severity(T)`**  (frequency × severity).

**Step 4 — floor + sort.** Keep only clusters with **`games(T) >= 2`** (the 2-game recurrence floor).
Sort surviving clusters by `rank_score` descending. That ordered list IS the "usual suspects."

**Output schema** (list of dicts):
```json
{ "theme": "fork", "games": 4, "occurrences": 6, "mean_severity": 512.0,
  "rank_score": 2048.0, "severity_label": "high|medium|low",
  "finding_ids": ["g003-p041", "g010-p033", ...] }
```
`severity_label`: high if mean_severity≥400, medium if ≥150, else low (tunable constants).
Also return, for the dashboard's BROAD view (Q8.1), the same computation grouped by **phase** and by
**concept** (reuse the existing `aggregates.by_phase`/`by_concept` — don't recompute; just surface
the top few). **Opening grouping is DEFERRED** (ECO is `'???'` until the ECO fix ships — do NOT
cluster by opening; leave a clearly-labeled TODO).

---

## PHASE A (dispatch now) — backend `usual_suspects.py` + route + tests
**Worker task.** Create `backend/training/usual_suspects.py`:
- `def usual_suspects(profile: dict) -> list[dict]` implementing the pinned math verbatim, returning
  the sorted list (empty list if no profile / no clusters clear the floor).
- Keep `GENERIC_MOTIFS`, the severity cap (800), the `>=2` floor, and the `severity_label` cutoffs as
  named module constants (so the leader can tune).
- Add API route `@app.get("/api/training/usual-suspects")` in `backend/app.py` → loads the profile
  via `store.load_profile()`, returns `{"suspects": [...], "by_phase": [...], "by_concept": [...]}`
  (404 if no profile, mirroring `get_profile`).
- **Tests** (`backend/tests/test_usual_suspects.py`): build a small synthetic profile fixture and assert:
  (1) a theme in 3 games clusters with `games==3`; (2) a theme in only 1 game is **excluded** by the
  floor; (3) `rank_score == games * mean_severity` on a hand-computed case; (4) `GENERIC_MOTIFS` never
  appear as a suspect theme; (5) unconfirmed findings weigh half; (6) sort order is by `rank_score` desc.
  **Mutation-check mindset:** each assertion must FAIL if the corresponding rule is broken.
- **Gates:** full suite stays **149 passed + your new tests** (`python -m pytest backend/tests`); do
  NOT touch `backend/training/metrics.py` (leader-owned) — the math lives in the new module.
- **Constraints:** match the finding schema field names EXACTLY (above); no engine calls needed (pure
  function over the profile dict); no push; STOP for leader review. Write `USUAL_SUSPECTS_REPORT.md`
  (what you built, the test results, any schema ambiguity you hit).

## PHASE B (spec after A lands + reviewed) — review/approve + deck
- Persist approved suspects (`store` json, e.g. `training/approved_suspects.json`): the user approves a
  subset of themes → their `finding_ids` become the deck source.
- Build the deck by reusing `drills.generate_drill_set` / the finding→drill path, restricted to approved
  findings, **blended and severity-weighted** (draw across approved themes proportional to `rank_score`),
  wired into the existing `attempts.py` SRS. Routes: `POST /api/training/usual-suspects/approve`,
  `POST /api/training/usual-suspects/deck`.

## PHASE C (spec after B) — frontend
- A "Usual Suspects" review screen: ranked themes (theme, games, occurrences, severity_label), each
  expandable to its positions, with approve/skip toggles → "Build my deck".
- Wire the approved deck into the existing `DrillMode.tsx` (reuse it; don't fork the runner).
- Minimal dashboard (Q8.3): top weakness (theme) / opening (placeholder until ECO fix) / theme needing
  attention, + drill progress from SRS `due_drills`.
- Gates: `npm test` green, `npm run build` clean, board/overlays unaffected.

## Sequencing note
Dispatch **Phase A only** now. Leader audits A (mutation-checks the floor + `rank_score`) before B is
specced. B before C. This keeps each piece pinned and reviewable — no big under-specified handoffs.
