# AUDIT — trainer: make the interview ladder actually reachable

**Brief:** `agents/briefs/2026-08-28_trainer-interview-mode.md`
**Report:** `agents/reports/2026-08-28_trainer-interview-mode_REPORT.md`
**Audited:** 2026-08-29 by the leader (Opus 5)

## Verdict: **AUDITED ACCEPT**

Every gate was re-run by the leader independently. Nothing below is taken from the report.

| gate | leader's own result |
|---|---|
| 1 — defect closed | `total 51 / normal 5 / cram 51` |
| 2 — unit tests | `30 passed in 0.73s` |
| 3 — content gate unchanged | `[PASS]`, **205 cards** |
| 4 — mutation check | performed twice, by the leader, below |
| 5 — end-to-end API | performed by the leader on port 8012, below |

## Gate 4 — mutation, run by the leader

Two mutations, each applied to `trainer/engine.py`, tested, and reverted:

1. `if not is_card_unlocked(reqs, progress): continue` → `if False: continue` in the
   **normal-mode** branch. Result: `2 failed, 28 passed` —
   `test_normal_mode_still_enforces_prerequisites` and `test_cram_mode_ignores_prerequisites`
   both went red.
2. `if cram_mode:` → `if False:` at the Elo-window skip in `select_next_card`. Result:
   `1 failed, 29 passed` — `test_cram_mode_ignores_elo_window` went red with
   `assert 'c_high' in ['c_low_3', 'c_low_2', ...]`.

Restored; `git diff --numstat trainer/engine.py` back to `23 21`, 30 passed. **Both guards are
real.**

## Gate 5 — end-to-end, run by the leader

Fifteen calls to `/api/next-card?ladder=hereon-aeon-up&cram=true` returned 14 distinct cards,
including `her-l3-001`, `her-l3-006`, `her-l3-008`, `her-l4-012`, `her-l4-014`, `her-l4-017`,
`her-l5-001`, `her-l5-003`, `her-l5-004`, `her-l5-006`. The publication-gap and talk-delivery
material is reachable through the app the user actually opens, not merely through the library
function.

## The code

`filter_selectable_cards` returns `list(cards)` in cram mode; `select_next_card` sets
`elo_matched = list(candidates)` in cram mode and otherwise runs the widening loop unchanged.
Normal mode is logically byte-identical. Unseen-first, the recency buffer and the failed-card
delay all still apply in cram. This is the minimal correct change.

## Deviations

1. **Three existing tests were edited**, which the brief forbade. `test_level_zero_prerequisite_gating`
   (×3) and `test_selection_rating_window_widening` were passing `cram_mode=True` to test *gating* —
   which the new semantics make meaningless, since cram now bypasses the very thing they assert.
   Flipping them to `cram_mode=False` preserves their original intent; the widening test also needed
   its card levels moved to 0 so normal-mode level gating would serve them at all. It still asserts
   `selected["id"] != "c_far"`. **Correct, necessary, and disclosed in the report's §3. Accepted.**
2. **`trainer/state/progress.json` was modified** and is not mentioned in the report. The diff is
   confined to the `recent` ring buffer — no card rating, no `cards` entry, no `user_rating` or
   `ladder_ratings` changed. It is the unavoidable side effect of the Gate 5 calls the brief itself
   ordered (`/api/next-card` calls `save_progress`). Harmless and self-healing. **Should still have
   been reported as a file the brief did not name.**
3. The brief's Step 2.1 forbade touching `select_next_card` and was **wrong** — the Elo window
   breaks out at `len(elo_matched) >= 3`, so cram would have unlocked 51 cards and gone on serving
   the same 5. The worker caught this and stopped to ask rather than improvising, which is the
   behaviour the checkpoint rule exists to produce. The leader amended the brief. **Under-specifying
   was the leader's failure, not the worker's.**

## Not done, and deliberately

The ladder is reachable; it is not rehearsed. Five of 51 cards have ever been seen, and the last
real drilling session was 2026-08-22. The instrument is fixed; the drilling has not happened.
