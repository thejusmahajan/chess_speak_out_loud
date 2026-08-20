```
Brief-ID:       2026-08-20_trainer-german-b2
Written:        2026-08-20
Target repo:    chess_speak_out_loud
Route:          Antigravity (full workspace)
Type:           engine change (Part A) + content authoring (Part B)
Status:         ACTIVE
Depends on:     2026-08-20_trainer-render-math (AUDITED, ACCEPTED)
Blast-radius:   external   (he sits the Goethe B2 exam on this material)
Reversibility:  costly     (a wrong grammar rule drilled by spaced repetition is expensive to unlearn)
Failure-mode:   SILENT     (invented German reads as fluent German to a learner)
Why before the deadline item: the application is unsent and outranks this. German B2 is a
standing goal with its own exam date; this is queued behind the application, not ahead of it.
```

# German B2 (Goethe) ladders — and the rating fix they require first

## INTENT

Thejus is preparing for the **Goethe-Zertifikat B2**. The trainer's ladder + spaced-repetition
engine suits language work well, and reusing it keeps one system rather than two.

A correct result: he can train German in the same app, at the right level, **without German
progress corrupting his machine-learning progress or vice versa**, and every German fact in it is
correct — because a learner cannot tell invented German from real German.

**If any instruction below conflicts with that intent, the intent wins — stop and report.**

---

# PART A — per-ladder ratings (do this first; Part B is unsafe without it)

## A1. The defect

```derivation
$ grep -n user_rating trainer/engine.py trainer/app.py
engine.py:213:  user_rating = progress.get("user_rating", 1200.0)
$ python -c "json.load(open('trainer/state/progress.json'))['user_rating']"
911.48
```

**One global scalar rates the user across every ladder.** His German is roughly B2; his machine
learning is beginner. Adding German would push the single rating up as he masters German cards,
and the selector would then serve harder *ML* cards he is not ready for — and the reverse.

## A2. The change

In `trainer/engine.py` and `trainer/app.py`:

1. Replace the scalar with **`progress["ladder_ratings"]: Dict[str, float]`**, keyed by the
   `ladder` field already on every card.
2. **Migrate on load**: if `progress` has the old `user_rating` and no `ladder_ratings`, seed every
   existing ladder with that value. Do not discard his history. Keep the old key readable for one
   version, then ignore it.
3. Elo updates apply **only to the ladder of the card answered**. `calculate_elo` itself is audited
   — do not modify it; change only which rating is passed in and stored.
4. Selection uses the rating **of the ladder being drawn from**.
5. New ladders start at a stated default: **1200** for German (he is an advanced learner), **820**
   for any new ML-side ladder. Put these in one dict at the top of `engine.py`, not scattered.
6. The UI shows the rating **for the current card's ladder**, labelled with the ladder name.

## A3. Tests (Part A) — real guards

1. `test_ladder_ratings_are_independent` — answer a `pytorch` card at 1.0 and assert the
   `de-grammatik` rating is **unchanged**.
2. `test_migration_seeds_all_ladders_from_legacy_rating` — a progress file with only
   `user_rating: 911.48` yields every ladder seeded at 911.48, and no card history is lost.
3. `test_selection_uses_the_ladder_rating` — with `pytorch` at 820 and `de-grammatik` at 1400,
   cards drawn from each sit near that ladder's own rating.
4. `test_new_ladder_uses_its_configured_default` — a ladder absent from `ladder_ratings` starts at
   its configured default, not 1200 for everything.

**Mutation-check test 1**: revert to the global rating, confirm it fails, restore.

**Gate A — stop and report the result before starting Part B.** If Part A does not pass, Part B
must not be authored.

---

# PART B — the German content

## B1. The absolute rule for this ladder

**Do not invent German.** A learner cannot distinguish an invented collocation, a wrong case
governance, or an unidiomatic example sentence from a correct one. This is the highest-risk content
this trainer has carried.

- Every **example sentence** is either taken from a cited corpus/reference, or explicitly marked
  `"constructed": true` in the card and kept to a structure the cited grammar rule directly covers.
- Every claim about **what the exam tests** cites the Goethe official *Prüfungsziele,
  Testbeschreibung B2* or the published *Modellsatz*. Not a blog, not a language school.
- Every **word-level claim** (case, gender, plural, governance, collocation) cites **DWDS** or
  **Duden** for that specific word, with a resolving URL.
- If you cannot source it, **drop the card and list it in your report.** That list is a success.

## B2. Three ladders

Same five-level shape as the existing ladders. Roughly 15 cards each; do not pad to a number.

### `de-konnektoren` — connectors and Redemittel *(highest yield: serves both Schreiben and Sprechen)*
- **L0** meaning of individual connectors — *obwohl, dennoch, trotzdem, zwar…aber, allerdings,
  hingegen, folglich, zumal, sofern, indem*
- **L1** the syntax each forces — subordinating (verb final), coordinating, or adverbial
  (position 1 → inversion). This is where B2 candidates lose marks.
- **L2** choosing between near-synonyms in a given context
- **L3** join two given sentences using a specified connector
- **L4** build a concession + counter-argument pair
- **L5** produce the full argumentative skeleton of a *Schreiben Teil 1* forum post — Einleitung,
  eigene Position, Argument + Beispiel, Gegenargument, Schluss

### `de-grammatik` — the structures B2 actually tests
Konjunktiv II (Höflichkeit, irreale Bedingung, indirekte Rede) · Passiv and its
Ersatzformen (`sich lassen`, `sein + zu + Infinitiv`, `-bar`) · Partizipialattribute ·
n-Deklination · Präpositionen mit Genitiv · Verben mit festen Präpositionen and the
Präpositionaladverbien (`darauf`, `damit`, `worüber`) · Nominalisierung ↔ Verbalisierung.

### `de-wortschatz` — structures, not word lists
Nomen-Verb-Verbindungen (`eine Entscheidung treffen`, `in Betracht ziehen`, `zur Verfügung
stellen`) · Präfixverben as families (`stehen → bestehen / entstehen / gestehen / verstehen`) ·
Wortbildung (`-ung, -keit, -heit`; `ver-, ent-, zer-`) · near-synonyms separated by register ·
typical interference errors for an English/Malayalam speaker, **only where you can source the
correct form**.

## B3. Card conventions specific to German

1. **Language of the card.** L0–L1 questions may be in English. **L2 and above are entirely in
   German** — this models the exam and is the point.
2. **UTF-8 correctness.** Umlauts and ß must be correct characters, never `ae/oe/ue/ss`
   transliterations. **Add a gate**: fail if any German-ladder card contains ` ue `, `ae`, `oe` or
   `ss` where the cited source shows `ü/ä/ö/ß`. Mutation-test it.
3. **Production cards carry a self-grade rubric.** For any L3–L5 card where the answer is produced
   rather than recalled, the card includes a `rubric` field with explicit, checkable criteria, e.g.

   > Score 1.0 only if: (a) the verb is in final position, (b) you used the specified connector,
   > (c) under 30 words. Otherwise 0.5.

   Self-grading without a rubric is guesswork, and guesswork corrupts the scheduling.
4. **No audio.** Hörverstehen cannot be trained by text cards. Do not fake it; note it as a gap.

## B4. Sourcing

Expected sources — all must resolve under `--check-urls`:
- `goethe.de` — Prüfungsziele Testbeschreibung B2, Modellsatz, Wortlisten
- `dwds.de` — word entries and corpus examples
- `duden.de` — grammar and governance

## B5. Gate

```
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer/verify_cards.py
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer/verify_cards.py --check-urls
git status
```

Plus:
- **Part A result pasted before Part B was begun**, including the mutation proof;
- a 400-draw distribution per ladder showing German draws near the German rating and ML draws near
  the ML rating — the proof that A2 works end to end;
- the count of German cards per ladder and per level;
- **every card dropped for lack of a source**, listed;
- the umlaut gate mutation proof.

## B6. Your report

`agents/reports/2026-08-20_trainer-german-b2_REPORT.md`. All gate output, the dropped-card list,
anything this brief got wrong, and — required —

> **"If exactly one thing in this delivery is still wrong, what is it most likely to be, and did I
> check it?"**

For this brief the honest candidate is a **German usage claim that is plausible but not idiomatic**.
Say which cards you are least confident about and why. Naming them is worth more than asserting
they are all fine.
