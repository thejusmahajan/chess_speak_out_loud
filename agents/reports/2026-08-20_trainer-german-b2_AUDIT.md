# AUDIT — `2026-08-20_trainer-german-b2`

**Auditor:** Leader (Claude Opus 5) · **Date:** 2026-08-21
**Verdict: ACCEPT the content and Part A's design. One blocking defect found and FIXED by the
leader** — the migration made every German card unreachable, exactly as Level 0 had been.

---

## 1. Boundaries and gates — PASS

Only `trainer/` and the report. `verify_cards.py` exits 0 on 123 cards. Suite **22 passed**
(was 17). Three new ladders: `de-konnektoren`, `de-grammatik`, `de-wortschatz`, 15 cards each,
levels 0–5.

## 2. The German content — PASS, and it is good

This was the highest-fabrication-risk material the trainer has carried. It holds up.

| check | result |
|---|---|
| sources | **dwds.de ×65, goethe.de ×3** — all external, no logs, no repo-only citations |
| rubrics on production cards | **18 of 18** L3+ cards have one |
| language convention (German from L2) | **0** cards at L2+ with an English question |
| umlaut / ß integrity | clean — my two "transliteration" flags were false positives of my own crude heuristic, matching *"d**ue** to"* and *"ne**ue** Synergien"* |

Spot-checks of the German itself:
- **Genitivpräpositionen** — `aufgrund, trotz, während, wegen`, correctly scoped to formal register.
- **Pronominaladverbien** — `da(r)-` / `wo(r)-` formation, with the human vs non-human distinction,
  which is precisely the B2 discriminator.
- **Konsekutive Konnektoren** — `folglich, demnach, infolgedessen`, correctly noting they trigger
  inversion in position 1.
- `de-kon-l4-002` asks for a Gegenargument using *"Zwar lässt sich einwenden, dass … allerdings
  sollte man bedenken, dass …"* — idiomatic B2 Redemittel, with a model answer in correct German
  and a rubric that is actually checkable: *"1.0 only if (a) both Redemittel correctly integrated,
  (b) verb positions correct (final in the dass-clause, position 2 in the main clause)."*

The rubric design works. Self-grading on production cards is no longer guesswork.

## 3. THE BLOCKING DEFECT — German was unreachable

```
AS DELIVERED, 400 draws:  {pytorch 186, own-work 90, uncertainty 47, air-quality 40, neural-processes 37}
                          German: 0 / 400
```

**Root cause**, `engine.py:69` — the migration seeded **every ladder in `DEFAULT_LADDER_RATINGS`**
from the legacy global `user_rating` (911.48), including the German ladders that had never
existed. The defaults dict was configured correctly (`de-*` → 1200); the migration overwrote it.

German cards are rated **1100–1650**. The ±150 window around 911 tops out at 1061, so no German
card qualified — and the window stops widening the moment ML cards satisfy it.

Confirmed causally rather than by inspection:

```
with German seeded at 911.48 (as shipped):  0 / 400 German draws
with German at the specified default 1200:  164 / 400 German draws
```

**This is the third time in this trainer that correct content was authored and left unreachable**
(Level 0, then German). The pattern is the same: every gate passes, the artefact is right in
isolation, and the delivery path is not exercised. The 400-draw measurement is the only check that
has ever caught it, and it now belongs in every trainer brief.

**The specification was self-contradictory and that is on me.** §A2.2 said "seed every existing
ladder with that value"; §A2.5 said new ladders take their configured default. The worker
implemented the first and wrote a test asserting it. Given a contradictory brief, that is a
defensible reading.

## 4. Fixed by the leader

Three changes, all verified:

1. **`engine.py`** — added `LEGACY_GLOBAL_RATING_LADDERS` (the five ML ladders that existed while
   the global rating was the only rating). The migration now seeds those from the legacy value and
   everything else from `get_default_ladder_rating()`. Comment explains why, since the reason is
   historical rather than derivable.
2. **`test_engine.py`** — the test asserted the wrong contract. Rewritten to require that legacy
   ladders keep 911.48 **and** German ladders take 1200, with the failure it prevents recorded in
   the docstring. **Mutation-tested**: forcing the old behaviour turns it red; restoring turns it
   green.
3. **`state/progress.json`** — the three German ladders reset from 911.48/919.07 to their
   configured 1200. Card history untouched.

Final state, measured:

```
verify_cards exit 0 · 22 tests passed
400 draws: pytorch 125 · de-wortschatz 84 · de-konnektoren 56 · own-work 51 · air-quality 30 ·
           neural-processes 29 · uncertainty 25    ->  German 140 / ML 260
ladder ratings: de-* 1200 (de-grammatik 1190 after answers) · ML ladders 911.5
```

Per-ladder independence works: German progress no longer moves the ML rating, which was Part A's
whole purpose.

## 5. Open, minor

The legacy `user_rating` key is still written on every grade (919.07). It is now dead — nothing
reads it for selection. Harmless today, misleading later. Should be removed once one more session
confirms the migration path is not needed again.

## 6. What I could not check, and the one thing most likely still wrong

I verified sources by host and count, not by resolving all 68 URLs, and I spot-checked 5 German
cards of 45 in depth.

**If exactly one thing here is still wrong, I predict it is a German usage claim in
`de-wortschatz` that is grammatically correct but not idiomatic** — a collocation that a native
speaker would not choose. Prefix-verb families and Nomen-Verb-Verbindungen are exactly where a
fluent-but-non-native generator drifts, DWDS confirms that a word exists without confirming that a
*combination* is natural, and it is the one class of error neither the gates nor I can detect.
**Thejus is the only available check on this**, and the comment box category *"I think this is
wrong"* is the right channel.
