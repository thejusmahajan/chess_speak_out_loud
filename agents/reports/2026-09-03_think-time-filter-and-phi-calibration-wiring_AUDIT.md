# AUDIT — `2026-09-03_think-time-filter-and-phi-calibration-wiring`

**Auditor:** leader (Opus 5), 2026-09-03.
**Verdict on the delivery: ACCEPT**, with two defects to fix (D2, D3).
**Verdict on what the audit uncovered: ⚑ D1 is a live, user-facing false claim, it pre-dates this
brief, and it is mine.**

---

## 1. The delivery did what the brief asked — verified against the diff

| requirement | verdict |
|---|---|
| think-time tracked from the previous clock **of the same player** | ✅ `prev_user_clock` only updates inside `if board.turn == user_color` |
| `prev_user_clock` reset per game | ✅ reset at the top of every game loop, all four sites |
| increment parsed per game from `TimeControl` | ✅ `metrics.parse_increment(game.headers.get("TimeControl"))` |
| unknown think time → analysed, not discarded | ✅ inherited from `is_reflex_move`, which returns False on `None` |
| all three named call sites | ✅ **four** — it also found the opening-aggregation site at ~line 683 |
| `is_time_scramble` and `time_scramble_skipped` kept | ✅ retained; the counter reports 0 as instructed |
| new `decisions` / `reflex_skipped` counters | ✅ in `_progress` and in the profile |
| scorer splits raw from display | ✅ `phi_raw`, `phi_display`, `phi` kept as raw for compatibility |
| ranking uses **raw**, never calibrated | ✅ all three sort sites use `phi_raw` |
| calibration loaded with a warning fallback | ✅ |
| UI renders the display value | ✅ `phi_display ?? phi` at both render sites |
| experimental label present | ✅ verbatim from the brief |
| suite green | ✅ **339 passed, 5 skipped, 1 deselected** |

No invented numbers. No scope violations. Fourth clean delivery.

---

## 2. ⚑ D1 — the UI states a safety property that does not exist, and I wrote the sentence

`SteeringLinesPanel.tsx:115` renders, to the user:

> **Experimental.** Φ ranks positions by how often a human of similar rating went wrong from them
> (held-out AUC 0.69). It is not an evaluation, **and LC0 still vetoes any unsound move.**

**The last clause is false.** Measured:

```
grep -c "steer_max_loss_cp\|steer_min_eval_cp" backend/app.py   ->  0
```

`compute_steering_analysis()` never calls `metrics.steer_candidates()`. It implements its own
selection:

- **Tier 1:** candidates within **80 cp** of best — a *relative* bound, and looser than the decided
  `steer_max_loss_cp = 60`.
- **Tier 2:** within **150 cp**.
- **Fallback:** `others.sort(key=phi_raw); tactical = others[:3]` — **no eval constraint whatsoever.**

And **`steer_min_eval_cp = -60`, the absolute "never objectively lost" floor, is applied nowhere in
the live path.** Even Tier 1 only bounds the *loss relative to best*; if the best move is −200, a
move at −280 passes.

**This explains Thejus's field report exactly.** He reported: *"the tactical steer in the opening
isn't working well and making spurious piece sacs that can be easily refuted."* In the opening the
engine's top moves cluster tightly, so Tier 1 and Tier 2 frequently hold fewer than two members, the
fallback fires, and **the highest-Φ move is surfaced regardless of how badly it evaluates.**

**Provenance — this is not Gemini's regression.** The 80/150/fallback structure is in the `-` lines
of the diff; it arrived with the 2026-09-02 steering-integration delivery, **which I never audited**.
Gemini's change here was only `phi` → `phi_raw` in the sort keys, which is correct.

**It is mine in the way that matters.** I asserted the veto three times in the record —
`state/NOW.md` §9, `LEADER_BIBLE.md` §6a, and the 2026-09-03 journal entry — each time as *"`app.py`
sorts only the playable set, so LC0 keeps an absolute veto on blunders and the harm is bounded."* I
had grepped a line number and inferred a guarantee from a variable named `playable`, without
following it back to `steer_candidates()`. Then I **dictated that false claim into the brief as
required UI wording**, and it is now on screen.

Root error: `LEADER_GROUNDING.md` §3c — *I substitute my representation of a thing for the thing.*
A variable name is not a guarantee.

**Immediate action taken:** the false clause is removed from the label. The fix to the *code* — which
floor, and whether it should be the narrowness-scaled "gamble floor" discussed with Thejus — is a
design decision and is his, not something to slip into an audit.

---

## 3. D2 — the aggregates use a stricter population than the analysis

`pipeline.py`, `aggregate_phase_clock`:

```python
if not reflex and not is_time_scramble(node.comment, cfg):
```

The old clock-remaining filter is **ANDed** with the new one, so `by_phase` and `by_clock` are
computed over a *different, smaller* population than `findings`. A move deliberated for eight
seconds with 15 s left — the exact case the whole change exists to rescue — appears in the findings
and is missing from the aggregates.

The brief said to keep `is_time_scramble` **in the file** (tests and old profiles reference it), not
to keep **applying** it. **Fix:** drop the second condition, leaving `if not reflex:`.

## 4. D3 — Stage A's cost is paid and its result discarded

`div = metrics.policy_divergence(...)` is computed **before** the `if not reflex:` gate, so the
policy call runs on every user move, reflex or not — the intended cheap full coverage at 0.13 s/node.
But the result is only recorded inside the gate, so for reflex moves it is computed and thrown away.

The brief's reasoning was *"a move blundered in one second is still evidence about blindness."* As
implemented we pay the cost and keep no evidence. **Fix:** either record a Stage-A-only blindness
tally for reflex moves, or skip the policy call for them and save the ~8 hours over the corpus.
Either is defensible; doing neither is not.

## 5. D4 — minor

`PhiScorer.calibrate_phi()` logs a warning on **every call** when uncalibrated. That is one log line
per candidate move per position. Warn once at load.

---

## 6. What changes in the record

The veto claim is corrected in `state/NOW.md` §9, `LEADER_BIBLE.md` §6a and the journal, in the same
commit as this audit. The corrected statement is:

> Φ re-ranks candidates selected by a **relative** 80/150 cp bound in `app.py`, with a fallback that
> applies **no eval constraint at all**. `steer_candidates()` and `steer_min_eval_cp` are **not** in
> the live path. There is currently **no absolute floor on how bad a surfaced move may be.**
