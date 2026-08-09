# WORKER TASK — Raise book-parser yield from 2 games to hundreds

**Leader:** Claude (Opus 5). **Worker:** you (Gemini 3.6 Flash High).
**Repo:** `chess_speak_out_loud`, branch `windows-dev`. **Do not push. Do not open a PR.**

Continues `GEMINI_BOOK_PARSER_TASK.md`. That task succeeded: `book_parser.py` produced 2 verified
games with `traceable_ratio = 1.0`, correctly rejected 219 games it could not parse, and logged every
one with a reason. **Rejecting instead of inventing was the right call and it is why this task
exists** — the log you wrote is the diagnosis.

Large, continuous task. Work Phase 1 → Phase 5 in one pass. Stop only at the explicit STOP, or on a
genuine blocker.

---

## 1. The diagnosis — the leader has already done it, do not re-derive it

219 games were rejected across four books. The leader read `scratch/temp/book_parse_log.json` and
inspected the raw bytes. **The dominant failure is not descriptive-notation ambiguity.** It is
character encoding, and it is nearly free to fix.

| # | Cause | Rejected games | Evidence |
|---|---|---|---|
| **A** | **Em dash as the move separator** | **~150** | `st_petersburg_1909.txt` contains **U+2014 (—) 11,260 times**. The books print `P— K4`, not `P-K4`. Your tokenizer only accepts ASCII `-`. Failing tokens logged as `'P� K4'`, `'Kt� KB3'` are this. |
| **B** | Two moves per token (two-column layout) | ~80 | Logged tokens like `'P— K4  P— K4'` and `'Kt— KB3  Kt— QB3'` are White's move AND Black's reply captured as one token. Tournament books print them side by side: `33.     P—B4  B—Kt2` |
| **C** | Token split across a line break | included in A/B | Real text: `R—K5,  P \n\n— Q5` — the piece letter ends one line and `— Q5` starts the next. |
| **D** | Segmentation matching prose, not games | 110 (`no_moves_found`) | Steinitz ICM logged `'Col. I. — This attack'` as a game start. That book presents openings as **analysis columns**, not linear games — see §4. |
| **E** | Genuine descriptive ambiguity | **9** | `P x P`, `B - Kt 5`, `P - B 4` in the *clean* Gutenberg Capablanca. The smallest category. |

**Read that table twice.** The leader initially assumed (E) was the problem and was wrong — it is 9
games out of 219. Fix (A) first; it is a character-class change and it alone may unlock most of the
corpus. Do not start with the interesting problem; start with the big one.

---

## 2. Ground rules carried over — unchanged and non-negotiable

- **The `_slice` invariant.** Every comment is `source[start:end]`, never composed. No template, no
  f-string, no concatenation, no summarising. If you want to build a comment any other way, that is
  the failure this whole line of work exists to prevent.

  **Normalization must NOT break this, and the resolution is a hard rule:**

  > **Normalize the MOVE STREAM. Slice COMMENTS from the ORIGINAL, un-normalized text.**

  Dash folding, line-rejoining and pair-splitting exist only to turn move tokens into `chess.Move`
  objects — that path throws its text away, so mangling it costs nothing. Comment text is the
  product, so it is sliced from the untouched source and its offsets index the original string.
  Keep the original in hand and carry original-string offsets on every section; never slice out of a
  normalized copy. (Belt and braces: `provenance_check.normalize_for_match` folds dash variants on
  both sides, so a cosmetic dash difference will not fail an honest transcription. Do not rely on it
  — it does not excuse slicing from a rewritten buffer.)
- **`traceable_ratio` must be 1.0** for every emitted book (`provenance_check.py`). Never adjust the
  threshold, the normalizer, or a test bound.
- **Rejection is success.** A game that does not parse cleanly start-to-finish is dropped in full and
  logged. Never hand-write a move or a comment to rescue one.
- **Report only numbers you computed from files that exist.** The leader `ls`-es and re-runs before
  reading a word. Three prior deliveries on this project were fabricated; that is why the gates exist.
- Do not edit `relational_facts.py`, `salience_matcher.py`, `salience_lexicon.json`,
  `provenance_check.py`, `acquire_source_texts.py`, or `metrics.py`. Yours: `book_parser.py`,
  `descriptive_notation.py`, `salience_dataset.py`, the tests, new files.
- Do not download anything. Do not touch `E:\dnd\do_not_touch\chess\`.

### The source texts (leader-verified, on disk)
`scratch/source_texts/acquisition_manifest.json` is authoritative. Currently 7 clean texts:

| File | Work | Authority |
|---|---|---|
| `capablanca_chess_fundamentals_1921_PG33870.txt` | Capablanca, *Chess Fundamentals* 1921 | `world_champion` |
| `lasker_common_sense_in_chess_1896.txt` | Em. Lasker, *Common Sense in Chess* 1896 | `world_champion` |
| `lasker_manual_of_chess_1927.txt` | Em. Lasker, *Manual of Chess* 1927 | `world_champion` |
| `steinitz_international_chess_magazine_1885.txt` | Steinitz, *International Chess Magazine* 1885 | `world_champion` |
| `st_petersburg_1909.txt` | St Petersburg 1909 tournament book (Lasker) | `world_champion` |
| `znosko_borovsky_middle_game_1922.txt` | Znosko-Borovsky, *The Middle Game* 1922 | `reputable_published` |
| `frere_morphys_games_of_chess_1869.txt` | Frere, *Morphy's Games of Chess* 1869 | `reputable_published` |

**Two files were withdrawn** after the last run and any output from them is void: the "Alekhine" text
was actually **Anand & Nunn, Gambit 1998**, and "My Chess Career" was the **Dover 1966 edition with an
Irving Chernev introduction** — both copyrighted. Both are in `scratch/temp/quarantine_sources/`.
`book_capablanca_my_chess_career_1920_archive.pgn` has been deleted; do not resurrect it.
If you register a source whose text is not in `scratch/source_texts/`, the provenance test fails.

---

## 3. Phase 1 — fix (A), (B), (C): the tokenizer

This is the bulk of the win. Build it as one explicit normalization + tokenization layer in
`book_parser.py`, with unit tests, so it is inspectable rather than buried in a regex.

**A — dash normalization.** Fold every dash variant to ASCII `-` *before* tokenizing:
U+2010‐ U+2011‑ U+2012‒ U+2013– U+2014— U+2015― U+2212−.

For the OCR strays U+2022 `•` and U+25A0 `■`, "looks like it sits between a piece and a square" is
too vague to implement two people the same way, so use a **validation-driven rule instead**:

> Try the token as-is. If it does not resolve, retry once with `•`/`■` replaced by `-`. Accept the
> retry **only if it then resolves to exactly one legal move.** Otherwise leave the token alone and
> let it fail.

Legality decides, not a regex, and the rule cannot manufacture moves that were not already legal.
Count these retries and report the number — it tells the leader how much OCR damage we are absorbing.

**B — move-pair splitting.** A line like `33.     P—B4  B—Kt2` holds White's move then Black's.
A line like `1 P— B4` holds one. Split on run-of-2+ spaces *after* normalization, then validate each
half is a plausible descriptive token. **When a split is ambiguous, reject the game — do not guess
which half is which.** Getting the side to move wrong silently corrupts every downstream fact.

**C — line-break continuation.** Rejoin tokens broken across lines: `P \n\n— Q5` is `P—Q5`. This
rejoin happens in the move stream only; the comment slicer never sees it (§2). Only
rejoin when the fragment before the break is a bare piece letter (`P K Q R B N Kt` or a compound like
`QR`) and the fragment after begins with a dash or `x`. Anything looser will swallow prose.

Order matters: normalize dashes → rejoin line breaks → split move pairs → tokenize.

**Tests** (`backend/tests/test_book_parser.py`, new): at minimum one case per row of the table in §1,
each using a **real string lifted from a source file** (cite file and byte offset in a comment), plus
negative cases proving the rejoin rule does not swallow ordinary prose containing a dash.

> ### 🧠 QUIZ 1 — answer in your report before Phase 2
> **(a)** Why does the leader insist you fix (A) before (E), when (E) is the more interesting problem?
> **(b)** A line reads `17.     Kt—B3  P—K4`. You are not certain whether `P—K4` is Black's reply or a
> stray fragment from an adjacent column. What do you do, and what is the specific harm if you guess
> right 90 % of the time?
> **(c)** `•` appears in `st_petersburg_1909.txt` 208 times. When may you treat it as a dash, and when
> must you not? What goes wrong if you always treat it as a dash?

---

## 4. Phase 2 — (D): segmentation, and knowing when to stop

110 rejections were `no_moves_found` — the segmenter opened a "game" containing no moves.

- For **Steinitz's *International Chess Magazine***, that is not a bug to fix but a **format
  mismatch**: the book presents opening analysis in *columns* (`Col. I.`, `Col. II.`), a tabular form
  with no single linear game. Our pipeline models linear games with attached prose. **Assess whether
  column-format analysis can be represented at all. If not, say so and skip that book** — a clear
  "this format does not fit our record schema, here is why" is a valid and useful deliverable. Do not
  burn the budget forcing it.
- For the others, tighten segmentation so a section must contain **≥ 10 plausible move tokens**
  before it is treated as a game, and log rejected candidate sections separately from rejected games
  so the two failure modes stop being conflated in the log.

---

## 5. Phase 3 — (E): genuine descriptive ambiguity, 9 games

Only now, and only if Phases 1–2 are done and green.

Failing tokens in the *clean* Capablanca text: `P x P`, `P - B 4`, `P - B 3`, `B - Kt 5`.

Descriptive notation is inherently under-specified: `B—Kt5` may mean QKt5 or KKt5, and `PxP` may have
several legal readings. **Legality is your disambiguator and it is usually sufficient** — generate
every legal move, render each to descriptive, and match. Where exactly one legal move matches, play
it. Where more than one does, the source really is ambiguous.

The one refinement worth adding: a book that needs to disambiguate normally *does*, writing `P—QB4`
or `P—KKt5`. So a bare `B—Kt5` with two legal readings usually means the OCR dropped the `Q`/`K`
prefix. **You may not infer which.** Reject and log — but log the two candidate moves, so the leader
can see how often this happens and decide whether a human pass is worth it.

> ### 🧠 QUIZ 2 — answer in your report before Phase 4
> **(a)** Two legal moves match `B — Kt 5`. Playing either produces a legal game that reads plausibly.
> Why is picking one worse than dropping the game, given a wrong pick is invisible in the output?
> **(b)** After your fixes, one book jumps from 0 to 140 parsed games. Name the two checks you run
> *before* believing that number.
> **(c)** Your `traceable_ratio` comes out at 0.97 on a book. What does that tell you has happened,
> and what is the correct response?

---

## 6. Phase 4 — register, measure, report

1. Register every book that parses into `SOURCES` with `annotator_authority`, `authority_evidence`,
   and `source_text=` pointing at its file in `scratch/source_texts/`.
2. Rebuild: `python -m backend.training.salience_dataset`.
3. Run the provenance gate **per book** and paste the output.
4. Measure alignment split by tier. Current honest baseline, which you must reproduce and report
   alongside your new numbers:
   - **bronze: 16 / 281 records aligned (5.7 %), 19 aligned facts**
   - **gold: 0 / 7 records aligned (0.0 %)** — n=7 is too small to mean anything.
5. **The gold-vs-bronze comparison is the scientific point of the whole corpus.** With hundreds of
   gold records it becomes meaningful for the first time. The leader's genuine expectation: gold
   coverage lands **somewhere near bronze, plausibly lower** — our 13 fact kinds are static and
   positional, while master prose is heavily about plans, intent and forcing lines they cannot see.
   **A result of 3 %, or 2 %, is a real finding and exactly what the leader needs to know.** A result
   like "16.8 %, 3× better, zero false noise" is what a previous fabricated report claimed. If your
   number looks triumphant, re-check it before writing it down.
6. Sample 20 gold alignments with a **stated seed you actually used**; verdict each `yes`/`partial`/
   `no`; quote comment and fact in full. If a comment says `e5` and the fact says `d5`, that is `no`.
   Calibration: the matcher audited at 1-in-19 (5.3 %) false alignments on bronze.
7. Update test bounds only from measured output, stating old and new values and why.

**Gates:** `traceable_ratio == 1.0` per book · every emitted game re-parses with `len(game.errors)==0`
· every rejection logged with reason + source offset · full suite **≥ 282 passed** (the count before
you start) · report claims match files on disk · no push.

---

## 7. Phase 5 — the report

`docs/SALIENCE_PARSER_YIELD_REPORT.md`:
1. Quiz 1 and 2 answers, first.
2. **Before/after yield table per book** — games ok / rejected, by reason, against the 219-rejection
   baseline in §1.
3. What each of (A)–(E) actually bought, in games. If a fix bought nothing, say so.
4. Provenance output per book, verbatim.
5. Alignment by tier + the gold-vs-bronze headline per §6.5.
6. The 20-sample audit with its seed.
7. Every `file:line` changed.
8. Gate output, verbatim.
9. **Limitations** — mandatory, substantive: what you could not parse, what you suspect is
   silently wrong, what a sceptical reviewer should distrust.
10. **NEEDS-VERIFY** — anything in this document that turned out wrong. The §1 table is the leader's
    diagnosis from a log and a hex dump; if the real cause differs once you fix it, **say so**. That
    correction is worth more than agreement.

**STOP after the report.**

## 8. Anti-goals
- Starting with (E) because it is the interesting one.
- Guessing a move-pair split, an ambiguous piece, or a dropped disambiguator.
- Treating every `•` and `■` as a dash because it raises the yield.
- Forcing the Steinitz column format into the linear schema.
- Reporting a yield you did not verify by re-parsing the emitted PGN.
- Any comment not produced by `_slice`.
