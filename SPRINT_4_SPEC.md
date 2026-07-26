# SPRINT 4 SPEC — Sharp Openings (Job 2): analyze his repertoire + steer him toward dynamic lines

Anchored in `GOAL_BOOK.md` J2. TWO sides: (a) understand his ACTUAL repertoire from the corpus and
surface where it can go SHARP; (b) actively RECOMMEND new dynamic openings (1.e4 gambits) since he's
ready to leave the dry London. **Key realization:** a repertoire system ALREADY exists
(`select_repertoire.py`: `build_repertoire`, `build_repertoire_tree`, `_leaky_ecos`, `_classify_eco`;
routes `/api/training/repertoire[s]`, `/repertoire/top-openings`, `/repertoire/drills`;
`RepertoirePanel.tsx`) — but it's **crippled because the profile's ECOs are all `'???'`**. So Sprint 4
starts by UN-crippling it.

## Grounded facts
- `openings.classify(ucis)` works LOCALLY now (returns e.g. `D02 London System`) — the ECO fix landed.
- The current 100-game `profile.json` has `aggregates.by_opening = {"???": {...}}` and every
  finding/steer_finding `opening.eco == "???"` (it ran on Kaggle's stale backend).
- The corpus PGN (`games_of_derdiedasdie_*.pgn`) has his games; the diagnostic selected them as
  `[g for g in games if "derdiedasdie" in g.lower()][:MAX_GAMES]`; findings carry `id` = `g<NNN>-p...`
  (NNN = index into that selected list) and `game` {white,black,date}.
- steer_findings (562, 176 had_tal) already carry the sharp/sac data per position.

## PHASE 0 (dispatch now) — ECO backfill (LOCAL, no Kaggle re-run) — unblocks everything
**Worker task.** `backend/training/eco_backfill.py`:
- `backfill_ecos(profile: dict, pgn_path: str) -> dict`:
  1. Parse the corpus PGN; replicate the diagnostic's selection EXACTLY (filter games containing
     "derdiedasdie", take the first `games_analyzed` of them) so index N aligns with `g<NNN>`.
  2. For each selected game, extract its opening move UCIs (first ~20 plies) and `openings.classify(...)`
     → `{eco, name}`. Build `game_index -> {eco,name}`.
  3. For every finding AND steer_finding: parse `g<NNN>` from `id`, set `opening = {eco, name}` from the
     map. **VERIFY alignment**: assert the mapped game's White/Black matches the finding's `game`
     white/black for a sample; if they don't match, fall back to matching by `game` {white,black,date}
     and report the discrepancy — do NOT silently mis-assign openings.
  4. Recompute `aggregates.by_opening` grouped by the real ECO (mirror the existing by_opening shape:
     moves/moves_white/moves_black/missed/blind/blind_rate per ECO).
  5. Return the enriched profile (do not save inside the fn).
- Route `POST /api/training/openings/backfill-ecos` → loads profile, backfills using the corpus PGN
  path (reuse whatever `_corpus_pgn()` / config the repertoire routes already use), `store.save_profile`,
  returns `{openings: [{eco,name,count}...], unresolved: n}`.
- **Tests** (`test_eco_backfill.py`): synthetic profile + a tiny PGN fixture → assert findings get real
  ECOs, by_opening regroups, alignment-mismatch is reported not silently wrong, a game whose opening
  can't be classified stays `'???'` (graceful). Mutation-check mindset.
- **Gates:** suite green; do NOT touch `metrics.py`; reuse `openings.classify`. No push. STOP for review.
- **Leader will run it on the real 100-game profile and verify openings resolve (London/etc.) before
  Phase A.** Once done, the EXISTING repertoire system (`top-openings`, `build_repertoire`) comes alive.

## PHASE A (spec after Phase 0 verified) — sharpness-by-opening + new-opening recommendations
- **Sharpness analysis:** group steer_findings (esp. `had_tal_move`) + findings by real ECO → per
  opening: `mean_complexity`, `#sacs`, `#findings`, and the top sharp/sac positions (feed them straight
  into the existing SacDrill/UsualSuspects by opening). Reuse `_classify_eco`/`by_opening`. Route
  `GET /api/training/openings/sharpness`.
- **New-opening recommendations (the "direct me to new lines" side):** a curated data file of dynamic
  1.e4 lines (Fried Liver, Evans Gambit, Giuoco Piano Nc3, King's Gambit, …) with ECO + the sac/tactical
  themes each produces; a route that returns them framed as "you want sharp play — explore these",
  optionally matched to his color. (Curated content + light logic; NOT engine analysis.)

## PHASE B (spec after A) — frontend
- Extend/reuse `RepertoirePanel.tsx`: a "Sharp Openings" view — his openings ranked by sharpness (from
  `/openings/sharpness`), drill into an opening's sharp positions, + a "Dynamic openings to explore"
  card list from the recommendations. Reuse the board / existing repertoire tree view. Lean; tests + build green.

## Sequencing
Dispatch **Phase 0 only** now (+ the parallel SRS-aware-deck task, `GEMINI_SRS_AWARE_DECK_TASK.md` —
different files, no conflict). Leader runs the backfill on the real profile, verifies ECOs resolve,
then specs Phase A. Phase 0 alone is high-value: it revives the whole existing repertoire feature.
