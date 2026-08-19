```
Brief-ID:       2026-08-20_trainer-level-progression
Written:        2026-08-19
Target repo:    chess_speak_out_loud
Route:          Antigravity (full workspace)
Type:           implementation (selector logic) — small and surgical
Status:         ACTIVE
Depends on:     2026-08-20_trainer-level-zero (content ACCEPTED — do not touch the cards)
Blast-radius:   external
Reversibility:  trivial    (one function; revert is easy)
Failure-mode:   SILENT     (a mis-ordered curriculum looks exactly like a correct one)
Why before the deadline item: ~30 minutes, and without it the Level-0 work already done is
unreachable — the trainer stays unusable.
```

# Make the ladder actually descend to Level 0

## INTENT

Eighteen Level-0 cards were written and are good. **The selector never serves them.** The user
must be able to start at the bottom and climb; today he is pinned at Level 1, which he has already
told us he cannot parse.

A correct result: with his current state, the next card he is shown is a **Level 0** card, and he
does not reach Level 1 in a ladder until Level 0 in that ladder is largely mastered.

**If any instruction below conflicts with that intent, the intent wins — stop and report.**

## 1. The measurement

```derivation
$ python -c "engine.select_next_card over 400 draws against trainer/state/progress.json"
stored user rating:                      1055.6
selection window (+/-150):               905 - 1205
Level-0 difficulty range:                780 - 840     <- entirely BELOW the window
Level-1 difficulty range:               1020 - 1060    <- squarely inside it
levels served over 400 draws:            {1: 400}
```

Elo-band selection across the whole pool competes with the ladder. Per-card `requires` does not
save it, because many Level-1 cards have no prerequisites and stay reachable.

**This is a leader specification error**, not a defect in the previous delivery. The original
trainer brief specified Elo-band selection and never reconciled it with level progression.

## 2. The change

In `trainer/engine.py`, modify **only** the selection stage. Do not touch `calculate_elo`,
`update_sm2`, `is_card_due`, or `is_card_unlocked` — all four are audited and correct.

**New rule: level gates the pool; Elo orders within it.**

1. Compute, **per ladder**, the lowest level `L` that still has unmastered cards. A card counts as
   *mastered* when it has been answered at 1.0 at least once (the same definition
   `is_card_unlocked` already uses — reuse it, do not write a second one).
2. A ladder is **eligible at level L** only. Cards above `L` in that ladder are not served, even if
   unlocked and due.
3. Advance the ladder to `L+1` when **at least 80%** of its level-`L` cards are mastered — not
   100%, so one stubborn card cannot block progress forever.
4. Within the eligible pool, keep the existing behaviour exactly: due-first, then the ±150 rating
   window widening by 50 until at least three candidates.
5. **Cram mode keeps ignoring all of this** — it is the escape hatch and stays as it is.

Different ladders progress independently: he may be at Level 2 in `pytorch` and Level 0 in
`air_quality`.

## 3. Reset the inherited rating

`trainer/state/progress.json` has `user_rating: 1055.6`, descended from an assumed 1200 start. That
assumption is now falsified by evidence — he flagged eight of nine Level-1 cards as incomprehensible.

Set `user_rating` to **820**, the middle of the Level-0 band. Preserve all per-card progress and
history; change only the user rating. Say in your report what it was before.

## 4. Tests — real guards, mutation-checked

Add to `trainer/tests/test_engine.py`:

1. `test_new_user_is_served_level_zero` — empty progress, 200 draws, **every card served is level
   0**. Assert the set of levels drawn equals `{0}`.
2. `test_level_one_unreachable_until_level_zero_mastered` — master 50% of a ladder's level-0 cards;
   assert no level-1 card from that ladder is served. Then master 80%; assert level-1 cards appear.
3. `test_ladders_advance_independently` — master all of `pytorch` level 0 and none of
   `air_quality` level 0; assert `pytorch` level-1 cards are served and `air_quality` level-1 cards
   are not.
4. `test_elo_still_orders_within_a_level` — with several level-0 cards of differing difficulty and
   a fixed user rating, the selector prefers those nearest the rating. This guards that the Elo
   logic was *scoped*, not deleted.
5. `test_cram_mode_ignores_level_gating` — cram still reaches any unlocked card.

**Mutation-check test 1 yourself**: revert the level gate, confirm the test fails, restore.

## 5. Gate — paste REAL output

```
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer/verify_cards.py
git status
```

Plus, and this is the one that matters — **re-run the measurement from §1 against his real
`progress.json` after the change** and paste it:

```
levels served over 400 draws:  <must be {0: 400}>
```

Also paste the mutation proof for test 1.

## 6. Your report

`agents/reports/2026-08-20_trainer-level-progression_REPORT.md`. Gate output, the before/after
rating, the 400-draw distribution, the mutation proof, anything this brief got wrong, and —
required —

> **"If exactly one thing in this delivery is still wrong, what is it most likely to be, and did I
> check it?"**
