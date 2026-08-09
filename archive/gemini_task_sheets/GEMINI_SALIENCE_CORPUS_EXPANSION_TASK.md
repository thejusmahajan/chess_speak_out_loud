> ## ⛔ SUPERSEDED — do not execute this document
> Leader decision, 2026-07-29: **Track A (lichess GM studies) is cut**; the whole budget goes to
> Track B. The live task is **`GEMINI_TRACK_B_MASTER_BOOKS_TASK.md`**. This file is retained only as
> the record of the Track A design, in case we revive it later.

# WORKER TASK — Build the GOLD salience corpus: annotations by verified top GMs only

**Leader:** Claude (Opus 5). **Worker:** you (Gemini 3.6 Flash High).
**Repo:** `chess_speak_out_loud`, branch `windows-dev`. **Do not push. Do not open a PR.**
Work locally, run the gates, write the report, STOP for leader review.

You have a large token budget. This task is deliberately large and continuous — **do not stop after
each sub-step to ask "shall I continue?"**. Work through Phase 0 → Phase 4 in one sustained pass.
Stop only at the four explicit **STOP** points, or if a **QUIZ** reveals you have misunderstood the
principle, or if you hit a genuine blocker (network dead, licence ambiguity, a rule below that
contradicts what you find on disk).

---

## 0. Why this task exists — read this before touching anything

The product goal (`docs/NORTH_STAR_decoding_lc0.md`) is to decode what LC0 is actually thinking and
say it back to the user as position-specific coaching. The blocker is the **salience problem**
(`docs/SALIENCE_PROBLEM.md`): our extractor emits ~8 TRUE facts per position, but only 1–3 of them
are *the point*. Picking wrong makes a **bad coach, which is worse than no coach** — that is the
project's motto and the reason every rule below is precision-first.

We cannot hand-label salience at scale. So: **a strong annotator's comment IS a salience label.**
When Alekhine writes "the e6 pawn is now a permanent weakness", he has told us which of the many
true facts carried the position. That is the training signal. The whole corpus exists to harvest it.

**Therefore the authority of the person who wrote the prose is the entire value of the record.**
A brilliant amateur annotation is a confidently-stated wrong label, and a wrong label is worse than
no label — it actively teaches the machine to foreground the wrong thing.

### What the previous corpus got wrong (learn from this — it is the reason for this task)

The first corpus shipped 281 records tiered `gold`/`silver`/`bronze`. The `gold` tier was labelled
*"Public Domain Master Classics: Capablanca, Steinitz, Alekhine"*. On audit, every one of those names
was a **player**, not an annotator. The actual `[Annotator]` headers were seven club-level hobbyists
annotating famous games, and the second source was a philosophy professor. **Zero of 281 records
were annotated by a titled player.** The whole corpus is now correctly retiered to `bronze`.

The failure was a single conflated idea: *world-class game* ≠ *world-class annotation*.

> ### 🧠 QUIZ 1 — answer in your report before doing anything else
> You find a PGN file: 60 games of Kasparov, Karpov and Fischer, beautifully annotated with deep
> positional prose. The `[Annotator]` header on every game reads `"ChessFan1987"`.
> **(a)** What `quality_tier` does this source get, and why?
> **(b)** The prose is genuinely excellent — better than some GM notes. Does that change your answer?
> **(c)** State in one sentence the rule that decides it.
> *If your answer to (b) is "yes" or "it depends on quality", you have misunderstood the task —
> re-read this section before continuing.*

---

## 1. Mission

Add records to the salience corpus whose annotator is a **verified top grandmaster or world-class
coach**, so that the `gold` tier stops being empty. Two independent tracks, both required.

- **Track A — Lichess studies by API-verified GMs.** Mechanically verifiable authorship, moderate
  volume, modern positions.
- **Track B — public-domain master books → annotated PGN.** World champions annotating their own
  games. This is the highest-authority material in existence and it is legally free. It is not yet
  in PGN form; converting it is the largest and most valuable part of this task.

Both tracks feed the same schema and the same code path. Nothing about the extractor or the matcher
changes.

---

## 2. Ground rules (violating any of these invalidates the whole delivery)

### 2.1 NEVER INVENT PROSE — the cardinal rule
You are a transcriber and a verifier here, **not an annotator**. You must never:
- write your own comment on a position, however obvious;
- paraphrase, summarise, modernise, clarify, or "improve" a master's wording;
- fill a gap where the OCR is garbled or the text is missing;
- merge two comments, or split one and re-word the halves;
- add a comment because a position "clearly deserves one".

Every character of `gm_comment` must be traceable to the source text. If you cannot read it, **drop
the record**. A dropped record costs us nothing. An invented record poisons the training signal and
we may not catch it.

The one permitted transformation: **translation of a public-domain non-English original** (Nimzowitsch
and Tarrasch wrote in German, Réti in German). Never use somebody else's in-copyright English
translation — the translation carries its own separate copyright.

Translation mechanics, so there is no ambiguity: **do the translation yourself, with your own model
capability** — no external translation service, no third-party translated edition. Store BOTH strings
on the record: `gm_comment` = your English translation, `gm_comment_original` = the verbatim source
text, `"translated": true`, `"source_language": "de"`. The original is what makes the translation
auditable; without it the record is unverifiable and therefore worthless. Translate faithfully and
literally — a chess term must survive as a chess term (`Freibauer` → "passed pawn", not "free pawn").
All files UTF-8, no exceptions; German umlauts and the like must round-trip intact.

### 2.2 Authority must be EVIDENCED, not asserted
Every source you add declares an `annotator_authority` from this fixed set, and an
`authority_evidence` string that a sceptical reviewer could check:

| `annotator_authority` | tier | Bar |
|---|---|---|
| `world_champion` | gold | Undisputed world champion annotating (usually their own games) |
| `grandmaster` | gold | Holds/held the GM title. Machine-verified, or a citation to FIDE/a reference work |
| `world_class_coach` | gold | Trainer of world-top players (e.g. FIDE Senior Trainer). Needs a real citation |
| `titled_verified` | silver | IM/WGM/FM, verified. Informs, never overrides gold |
| `reputable_published` | silver | Untitled but a recognised published annotator, with citation |
| `unverified` | bronze | Anything else. **The default when in doubt.** |
| `none` | bronze | No annotator at all |

`authority_evidence` must be specific: `"lichess /api/user/<name> returns title=GM (checked
2026-07-30)"` is evidence. `"well known strong player"` is not. **When you cannot evidence it, it is
`unverified`.** There is no shame in bronze; there is real damage in a false gold.

### 2.3 Licensing — no exceptions, no "but it's on the internet"
- **US public domain = published 1930 or earlier** (as of 2026). 1931 is NOT public domain yet.
- **The 1930 rule already accounts for foreign works.** You may worry about URAA copyright
  restoration for the German titles (Nimzowitsch 1925, Tarrasch 1912, Réti 1922). Restored works get
  the same 95-years-from-publication term, so 1925 + 95 = expired at the end of 2020. A work
  published ≤1930 is PD in the US in 2026 whether or not it was restored. Do not spend time on this;
  it is settled. If you find a work you believe is an exception, flag it and exclude it.
- `docs/public_domain_chess_library.md` is the leader-approved shelf. **Read it. It already lists
  what is confirmed PD and what is explicitly excluded.** Do not re-litigate it.
- Explicitly **EXCLUDED regardless of availability**: Chernev (all), Bronstein *Zurich 1953*,
  Lipnitsky, Dvoretsky, Yusupov, Kotov, New in Chess, ChessBase products, Nunn, Watson, any post-1930
  book. Finding a PGN of one of these online does **not** make it ingestible. Do not ingest it. Do not
  suggest ingesting it.
- Never scrape a paywalled or login-walled resource.

### 2.4 Files you must NOT modify
- `backend/training/metrics.py` — leader-owned.
- `backend/training/relational_facts.py` — audited primitive.
- `backend/training/salience_matcher.py` — leader-owned. If you believe the lexicon needs new
  phrases, write them to **`scratch/temp/lexicon_proposals.json`** with, for each phrase, the corpus
  line that motivated it. The leader audits and merges. Do not edit `salience_lexicon.json`.

You MAY modify: `backend/training/salience_dataset.py` (to register new sources — the `SOURCES` list
is designed for exactly this), and you may add new files under `backend/training/`, `scratch/`, and
`docs/`.

> ### 🧠 QUIZ 2 — answer in your report
> **(a)** You find `logical_chess_move_by_move.pgn` on a public GitHub repo — Chernev's complete book,
> free to download, superb instructive prose. Ingest it? One sentence why or why not.
> **(b)** You are transcribing Tarrasch's German notes and hit a sentence whose OCR reads
> `"Der Sprnger auf d5 ist ###unleserlich### stark"`. What do you do with that comment?
> **(c)** You find an excellent English edition of Nimzowitsch's *My System* translated in 1991.
> The 1925 German original is public domain. Can you use the 1991 English text? What is the correct
> route to an English `gm_comment` here?

---

## 3. Phase 0 — orient yourself in the repo (do this first, ~10 minutes)

Read, in this order:
1. `docs/SALIENCE_PROBLEM.md` — what salience is and why no local rule finds it.
2. `GM_CURRICULUM_PLAN.md` — the corpus paradigm and the modular knowledge architecture.
3. `docs/public_domain_chess_library.md` — the approved PD shelf and the exclusion list.
4. `docs/SALIENCE_PIPELINE_REPORT.md` — what already exists, and its honest limitations.
5. `backend/training/salience_dataset.py` — **the code you will extend.** Note `SourceSpec`,
   `AUTHORITY_TIER`, `SOURCES`, `clean_comment`, `is_substantive_comment`, `iter_source_records`.
6. `backend/tests/test_salience_pipeline.py` — the gates you must keep green.

Then run the existing pipeline once so you know it works before you change anything:

```bash
python -m backend.training.salience_dataset
python -m pytest backend/tests/test_salience_pipeline.py -o pythonpath=. -q
```

Expected today: 281 records, all `bronze`, 13 tests pass. If that is not what you see, **STOP and
report** — something changed under you and the rest of this task is built on it.

**Environment note:** this repo is developed on Windows, and the backend runs from the conda env
`cszero`. On the leader's machine that interpreter is
`C:\Users\Admin\miniconda3\envs\cszero\python.exe` — **if you are on a different machine or OS,
locate the `cszero` env yourself (`conda env list`) rather than assuming that path.** The salience
pipeline itself needs only `python-chess`, so plain `python` is fine for Phases 1–3; the FULL test
suite needs `cszero` (it imports `torch`).

**STOP POINT 1** is at the end of Phase 1. Everything before it is preparation.

---

## 4. Phase 1 — Track A: Lichess studies by API-verified GMs

### 4.1 The verification mechanism (this is why Track A is trustworthy)
Lichess exposes the FIDE title as a field on the user object. That makes GM authorship
**machine-checkable**, which is exactly the evidence standard §2.2 demands.

Endpoints (all public, no auth needed for public data). **Treat these as NEEDS-VERIFY — confirm each
one actually behaves as described before building on it, and report any that differ:**

| Purpose | Endpoint |
|---|---|
| Verify a user's title | `GET https://lichess.org/api/user/{username}` → JSON, field `title` (`"GM"`, `"IM"`, …) |
| All public studies by a user, as PGN | `GET https://lichess.org/api/study/by/{username}/export.pgn?comments=true&variations=true&clocks=false` |
| One study | `GET https://lichess.org/api/study/{studyId}.pgn?comments=true` |
| Discover titled players | `GET https://lichess.org/api/player/top/200/{perfType}` (`blitz`, `rapid`, `classical`) → entries carry `title` and `id` |

Rules of engagement with the API:
- **Rate limit yourself to ~1 request/second**, and treat that as an upper bound, not a target —
  limits are IP-based and some endpoints are tighter, so expect 429s earlier than you'd like and
  build the backoff in from the start rather than after the first failure. On HTTP 429, sleep 60 s
  and resume — never hammer.
- Send a descriptive `User-Agent` (e.g. `chess_speak_out_loud research (contact: repo owner)`).
- Cache every raw response to `scratch/annotated_games/lichess_raw/` so the work is reproducible and
  you never re-fetch. Reproducibility is part of the deliverable.

### 4.2 What to do
1. Build `backend/training/lichess_study_harvest.py` — a standalone, re-runnable harvester:
   - `verify_title(username) -> str | None` — the `title` field, cached to disk.
   - `discover_gm_candidates() -> list[str]` — from the top-player endpoints plus any GM usernames
     you find by other legitimate means; **every candidate must then pass `verify_title` == `"GM"`.**
     A username that "looks like" a GM's name is not evidence.
   - `harvest(username) -> path` — export their studies to
     `scratch/annotated_games/lichess_gm_<username>.pgn`, with the raw response cached.
   - A `__main__` that runs the whole sweep and prints a summary table.
2. Run it. Aim for **≥ 15 verified GMs** attempted and **≥ 200 substantive-prose records** harvested.
   These are targets, not quotas — see §4.4.
3. For each harvested file, register a `SourceSpec` in `salience_dataset.SOURCES` with
   `annotator_authority="grandmaster"` and `authority_evidence` naming the API check and the date.

### 4.3 The trap in Track A (read carefully)
Most lichess studies are **opening repertoires, puzzle sets, or move-dumps with no prose.** They will
sail through a naive filter and flood the corpus with junk that is technically GM-authored and
analytically worthless. `is_substantive_comment` already rejects bare evals, engine lines and
sub-10-char notes — but it does **not** know that `"This is the main line, and after 15...Qc7 we
transpose"` carries no salience label.

You must therefore report, per GM: studies fetched, games, raw comments, comments surviving
`is_substantive_comment`, and **an eyeball sample of
`min(surviving_comments, max(20, 0.10 * surviving_comments))`, sampled randomly, not cherry-picked
from the top** — with a one-line verdict on each: is it a real
positional/tactical explanation, or navigation ("main line", "White is better", "see chapter 3")?
If **more than half** your sample is navigation, exclude that GM entirely and say so. Volume is not
the goal; labels are.

Log every Track A exclusion to `scratch/temp/track_a_exclusions.json`:
```json
[{"username": "…", "title_returned": "IM", "studies": 12, "games": 140,
  "surviving_comments": 310, "sampled": 31, "navigation_in_sample": 24,
  "excluded": true, "reason": "not_gm" }]
```
Permitted `reason` values: `not_gm` (title ≠ GM), `no_public_studies`, `no_substantive_prose`,
`navigation_majority`, `mixed_authorship`, `fetch_failed`, `other` (with free text).

Also: a study authored on a GM's account may contain guest contributors or quoted material. If the
`[Annotator]` header or the study text names someone else, the record's authority is *that* person's,
not the account owner's. **Collaborative or mixed-author studies: do not attempt per-comment
attribution — you cannot verify it. Tag the whole study `unverified` (bronze) or drop it. Never
split a study's authority across comments.**

### 4.4 If the yield is poor
It may turn out that verified-GM lichess studies with substantive prose are rare. **That is a valid
finding and you must report it as one — do not pad the corpus to hit a number.** A report saying
"12 GMs checked, 3 had prose studies, 41 usable records, here is the evidence" is a *successful*
delivery. Inflating it with repertoire dumps is a failed one.

> ### 🧠 QUIZ 3 — answer in your report, before Phase 2
> **(a)** `GET /api/user/somestrongplayer` returns `{"title": "IM", ...}`. Their annotations are
> excellent. What `annotator_authority` and what tier?
> **(b)** You harvest 400 records from one GM, but on sampling, 380 are of the form
> `"and now White is better"` or `"the main line continues"`. What do you do, and what do you report?
> **(c)** Why does the leader care more about 40 good records than 400 mediocre ones? Answer in terms
> of the salience problem, not in terms of "quality is good".

**STOP POINT 1 — write your Phase 1 findings and QUIZ 1–3 answers into the report file
(`docs/SALIENCE_CORPUS_EXPANSION_REPORT.md`) before starting Phase 2.** Do not wait for a reply;
write it, then continue. The write-up is the checkpoint, not an approval gate.

---

## 5. Phase 2 — Track B: public-domain master books → annotated PGN

This is the heart of the task and where your token budget should go.

### 5.1 Why this is the real gold
Track A gives us modern GMs commenting on other people's games. Track B gives us **world champions
explaining their own decisions**: Alekhine on Alekhine, Capablanca on Capablanca, Lasker, Tarrasch,
Nimzowitsch, Réti. There is no higher-authority salience label available at any price, and it is
legally free. It is not in PGN form only because nobody has done the conversion — which is a language
task, which is what you are for.

### 5.2 Target works (from `docs/public_domain_chess_library.md` — all confirmed PD)
Prioritise in this order. Take the first two you can actually obtain; a third is a bonus.

1. **Alekhine — *My Best Games of Chess 1908–1923*** (1927). Alekhine annotating himself. Dense,
   concrete, plan-level prose. **Best single target.** (The 1924–1937 volume is 1939 — NOT PD.)
2. **Capablanca — *Chess Fundamentals*** (1921) and ***My Chess Career*** (1920). Clear positional
   prose, ideal for our fact kinds.
3. **Tarrasch — *Die moderne Schachpartie*** (1912) / ***Dreihundert Schachpartien*** (1895). German;
   translate per §2.1. Tarrasch names structural features explicitly — excellent for our extractor.
4. **Nimzowitsch — *Mein System*** (1925), German. Outpost/blockade/overprotection vocabulary maps
   directly onto our fact kinds.
5. **Lasker — *Common Sense in Chess*** (1896); **Réti — *Modern Ideas in Chess*** (1922).
6. **Tournament books**: *New York 1924* (annotated by Alekhine, 1925), *London 1922*, *St Petersburg 1909*.

Where to look (**NEEDS-VERIFY — I am not asserting these hold the works; check**): Project Gutenberg,
archive.org, Wikisource, open GitHub PGN repositories. Some of these have *already* been transcribed
to annotated PGN by hobbyists — **if you find such a PGN, it is a shortcut but not a free pass: you
must spot-verify its prose against the original book text** before trusting it, because a hobbyist
transcription can silently contain the hobbyist's own additions. Report your verification method.

### 5.3 The conversion problem — descriptive notation
Pre-1930 English chess books use **descriptive notation** (`P-K4`, `Kt-KB3`, `QxP ch`), not
algebraic. This is the single hardest technical part of Track B and the most likely place to
introduce silent errors.

Your converter must be **verification-driven, not translation-driven**:
- Maintain a real board (`python-chess`) while parsing. At every move, generate the legal moves and
  find the unique one matching the descriptive token. **If zero or more than one legal move matches,
  do not guess — record a parse failure for that game and move on.**
- `Kt` = knight (old notation for N). Squares are named from the *moving side's* perspective, so
  `P-K4` is `e4` for White and `e5` for Black. `ch` = check, `dis ch` = discovered check,
  `e.p.` = en passant. Castling appears as `Castles`, `O-O`, `0-0`, `K-R sq`.
- A game that does not parse cleanly from move 1 to the stated result is **rejected in full**. Do not
  salvage a partial game by inventing the missing moves.

Success criterion: for every game you emit, `chess.pgn.read_game()` re-reads it with
`len(game.errors) == 0`, and the final position is consistent with the stated result.

### 5.4 Attaching the prose
The book interleaves moves and commentary. Attach each comment to **the move it follows**, i.e. as a
python-chess node comment on that move — this matches how the existing corpus is built, and the
pipeline extracts facts from the position *after* the annotated move, which is where a comment like
"the e6 pawn is now backward" is actually true.

Keep, verbatim: positional explanation, plan statements, evaluation reasoning, "the point is…".
Drop: pure move lists, page/diagram references, cross-references to other games, index matter,
publisher front-matter. When a comment mixes prose and a variation, **keep the whole comment as-is** —
`is_substantive_comment` scores move-token density and will reject the ones that are mostly notation.
Do not pre-edit prose to help the filter pass; that is editing a master's words.

**A defect you would otherwise have hit, now fixed — verify it holds.** Until 2026-07-29 that density
check only recognised *algebraic* tokens, so a pure descriptive-notation variation dump
(`If 18. P-K4 PxP 19. KtxP Kt-B3 …`) contained no SAN, scored as 100% prose, and entered the corpus
as though it were a positional explanation. Every Track B record from a pre-1930 English book would
have been polluted. `_DESC_TOKEN_RE` in `salience_dataset.py` now catches descriptive tokens, guarded
by `test_descriptive_notation_dumps_are_not_prose`. Run that test early. If your book uses a
descriptive convention the pattern misses (regional variants exist — `Kt` vs `N`, `Q sq`, `P-K8(Q)`,
`dbl ch`), **extend `_DESC_TOKEN_RE` and add the failing case to that test.** Report every variant
you had to add — that list tells the leader how much of the notation space we now cover.

### 5.5 Deliverables for Track B
- `backend/training/descriptive_notation.py` — the verification-driven descriptive→SAN converter,
  with its own unit tests in `backend/tests/test_descriptive_notation.py` (include at least 10 real
  lines from your source book, plus the ambiguity cases: two knights able to reach the same square,
  pawn captures, promotions, castling in each of its written forms).
- `scratch/annotated_games/book_<author>_<year>.pgn` — the transcribed annotated PGN.
- `scratch/temp/book_transcription_log.json` — how the leader audits you without re-reading the book.
  Exact schema, so a script can check it:
  ```json
  {"book": "Alekhine, My Best Games of Chess 1908-1923 (1927)",
   "source_url": "…", "obtained": "2026-07-30",
   "games": [
     {"game_ref": "Alekhine - Bogoljubow, Hastings 1922",
      "section": "Game 42, pp. 118-121",
      "status": "ok",                          // ok | rejected
      "reject_reason": null,                   // required when status == "rejected"
      "moves_parsed": 41,
      "comments_kept": 9,
      "comments_dropped": [
        {"after_move": "23...Rfe8", "reason": "ocr_garbled", "raw": "the Kt is ###"},
        {"after_move": "31.Qd4",    "reason": "diagram_reference", "raw": "(see diagram, p.120)"}
      ]}
   ],
   "totals": {"games_ok": 40, "games_rejected": 3, "comments_kept": 372, "comments_dropped": 88}}
  ```
  Permitted `reason` values: `ocr_garbled`, `diagram_reference`, `cross_reference`, `front_matter`,
  `pure_variation`, `ambiguous_move`, `other` (with free text). Permitted `reject_reason` values:
  `move_parse_failure`, `ambiguous_descriptive_move`, `result_mismatch`, `incomplete_source`, `other`.
  **Every** dropped comment and rejected game appears here — a silent drop is a gate violation.
- A `SourceSpec` registered with `annotator_authority="world_champion"` (Alekhine, Capablanca, Lasker
  on their own games) or `"grandmaster"`, `license="Public Domain"`, and `authority_evidence` citing
  the work, its publication year, and where you obtained the text.

**Target: ≥ 2 books, ≥ 40 games fully transcribed and verified.** If a book defeats the converter,
report exactly where and why — a documented failure is worth more than a silently mangled game.

> ### 🧠 QUIZ 4 — answer in your report, before Phase 3
> **(a)** Parsing Alekhine, you reach `18. QxKtP` and find that two different legal captures match
> that description. What do you do? What do you NOT do?
> **(b)** Capablanca writes a comment you find genuinely confusing and probably a typo in the 1921
> print. Do you correct it? Why does the answer matter more here than in ordinary software work?
> **(c)** A hobbyist PGN of *My Chess Career* exists online with comments already attached. What must
> you do before tagging it `world_champion`, and what is the specific risk you are guarding against?
> **(d)** Restate, in one sentence and in your own words, why the position facts are extracted from
> the board state AFTER the annotated move rather than before.
> **(e)** `is_substantive_comment("If 18. P-K4 PxP 19. KtxP Kt-B3 20. KtxKt ch")` returns `True` in
> your working copy. Is that correct behaviour? What breaks downstream if you don't notice, and what
> is the fix — change the comment, or change the filter?

---

## 6. Phase 3 — integrate, measure, and be honest about the result

1. Register every new source in `SOURCES` (`backend/training/salience_dataset.py`), each with real
   `annotator`, `annotator_authority`, `authority_evidence`, `license`.
2. Rebuild the artifact: `python -m backend.training.salience_dataset`.
3. Update `backend/tests/test_salience_pipeline.py`:
   - `test_tier_is_derived_from_annotator_authority` currently asserts **no gold records exist**.
     That assertion encodes today's honest state. When you land verified-GM sources, **invert it**:
     assert gold records DO exist, and that every gold record's `annotator_authority` is one of
     `world_champion` / `grandmaster` / `world_class_coach`.
   - `test_corpus_wide_alignment_has_no_regression` asserts `aligned_records >= 12`,
     `aligned_facts >= 15` and a coverage ceiling of 20%. Re-derive these from the new corpus.
     **Do not simply loosen a bound to make a test pass** — if coverage moves, explain why in the
     report before changing the number.
4. Measure and report, split **by tier**, using `salience_matcher.align_prose_to_facts`:
   - records, aligned records, aligned facts, coverage %;
   - the distribution of aligned fact kinds;
   - **the gold-vs-bronze comparison — this is the headline result.** The whole thesis of this task is
     that GM prose aligns better with our fact kinds than club prose does. If gold coverage is *not*
     higher than bronze coverage, say so plainly. A negative result, honestly reported, is a real
     finding and changes what the leader builds next. Do not massage it.
5. Sample **20 gold alignments** and give each a verdict: does the comment really refer to that fact?
   (`yes` / `partial` / `no`). Report the false-alignment rate. For calibration: the current matcher
   audited at **1 false alignment in 19 (5.3%)** on the bronze corpus.
6. Gates — all must pass, paste the actual output:
   ```bash
   python -m pytest backend/tests/test_salience_pipeline.py -o pythonpath=. -q
   python -m pytest backend/tests/test_descriptive_notation.py -o pythonpath=. -q
   C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests -o pythonpath=. -q
   ```
   The full suite was **251 passed, 5 skipped** before your changes. It must be no worse.

> ### 🧠 QUIZ 5 — answer in your report
> **(a)** Your new gold corpus shows 4% alignment coverage; the old bronze corpus showed 5.7%. You
> could reach 9% by adding the words `"bishop"`, `"file"` and `"weakness"` to the lexicon as strong
> phrases. Do you? Why is that specific temptation dangerous?
> **(b)** `test_corpus_wide_alignment_has_no_regression` fails after your import because
> `aligned_records` dropped below 12. Name the two legitimate responses, and the one illegitimate
> response you must avoid.

---

## 7. Phase 4 — the report

Write `docs/SALIENCE_CORPUS_EXPANSION_REPORT.md`. It is the deliverable the leader actually reads.

Required sections:
1. **Answers to QUIZ 1–5**, verbatim question then your answer. Put these first.
2. **What landed** — table of new sources: file, annotator, authority, evidence, licence, records, tier.
3. **Track A results** — GMs checked, verified, harvested, excluded (with reasons); per-GM yield
   table; the 10-comment eyeball sample.
4. **Track B results** — books attempted/obtained, games parsed, games rejected and why, the
   descriptive-notation cases that defeated the converter, the transcription log summary.
5. **Alignment measurements** — the by-tier table and the gold-vs-bronze headline, per §6.4.
6. **The 20-alignment audit** with the false-alignment rate.
7. **Every `file:line` you added or changed.**
8. **Gate output** pasted verbatim.
9. **Honest limitations** — what you could not verify, what you guessed at, what a sceptical reviewer
   should distrust in your delivery. A report with no limitations section is not believable and will
   be sent back.
10. **`NEEDS-VERIFY` list** — every claim in this task document that turned out to be wrong or
    outdated (API shape, availability of a book, anything). I wrote parts of this from memory and
    flagged them; correcting me is part of the job.

**STOP after writing the report. Do not push, do not merge, do not start Phase 5 of your own
invention.**

---

## 8. Anti-goals — things that would look like progress and are not

- Adding records whose annotator you could not verify, "to be filtered later". They never get filtered.
- Writing your own annotations to fill sparse positions. See §2.1.
- Ingesting a copyrighted book because a free PGN of it exists.
- Loosening a test bound so the suite goes green.
- Broadening the lexicon so coverage numbers rise. Coverage is a measurement, not a target — the
  moment you optimise it, it stops measuring anything.
- Rewriting `relational_facts.py` or `salience_matcher.py` because a fact kind is missing. Log the
  gap in the report; the leader decides.
- Padding volume with prose-free repertoire studies.
- Silently dropping a game that failed to parse. Log every drop.

---

## 9. Summary of hard gates

| # | Gate |
|---|---|
| 1 | QUIZ 1–5 answered in the report, before the corresponding phase's work |
| 2 | Every source declares `annotator_authority` + checkable `authority_evidence` |
| 3 | No gold record whose annotator is not a verified GM / world champion / world-class coach |
| 4 | Every `gm_comment` traceable to source text; zero invented prose |
| 5 | Every emitted game re-parses with `len(game.errors) == 0`; every drop/rejection logged in `book_transcription_log.json` |
| 6 | Only PD (≤1930) or explicitly-permitted material; exclusion list respected |
| 7 | `test_salience_pipeline.py` green; `test_descriptive_notation.py` green; full suite ≥ 251 passed |
| 8 | Gold-vs-bronze alignment comparison reported, including if the result is negative |
| 9 | Limitations + NEEDS-VERIFY sections present and substantive |
| 10 | No push, no PR, STOP for leader review |

---

## 10. Questions already asked and answered — do not ask these again

A previous reviewer read this document cold and raised the following. The answers are binding.

1. **"Give me a seed list of GM lichess usernames."** No. Discovery is your job — the top-player
   endpoints plus any GM handles you know of. The seed does not matter because **verification is the
   gate**: a handle is worth nothing until `/api/user/{name}` returns `title == "GM"`. Do not ask for
   a list; build one and prove each entry.
2. **"For a `status: "rejected"` game, must I still list `comments_dropped`?"** No. A rejected game
   needs only `game_ref`, `section`, `status`, `reject_reason`. `comments_dropped` is for `ok` games.
3. **"A German comment contains `18. S-d5`. Do I convert the piece letter to `N`, or to SAN?"**
   Neither — **leave notation inside prose exactly as printed.** Translate the *words*, never the
   *notation*. This is deliberate: our matcher grounds on square coordinates (`d5` is `d5` in every
   language), so foreign piece letters cost us nothing, while rewriting them is an edit to the
   master's text with no upside.
4. **"Verbatim vs. translation is contradictory for German books."** It is not. `gm_comment_original`
   is verbatim source text; `gm_comment` is your faithful, complete translation of that same string.
   "Verbatim" governs *which comments you keep* and forbids editorial rewriting — it does not forbid
   translation, which is the one transformation §2.1 explicitly permits. **Translate the whole
   comment; do not excise variations before translating.**
5. **"Which sites may I obtain book text from?"** Any site that is not paywalled and not login-walled.
   Prefer Project Gutenberg, archive.org and Wikisource because their provenance is checkable. Record
   the exact URL and retrieval date for every text. If a text's provenance looks dubious, spot-verify
   it against a second copy before trusting it, and say so in the report.
6. **"What is 'now', for the public-domain arithmetic?"** The project-present date is **2026**. Use
   2026 as the reference year regardless of your system clock. If your clock disagrees, apply the
   **stricter** of the two — an extra year of caution costs us nothing.

---

## 11. If you get stuck

- **Blocked on a rule that contradicts the repo?** The repo wins; report the contradiction.
- **Blocked on licensing?** Default to *exclude*, tag `unverified`, and flag it for the leader. Never
  resolve a licensing doubt in favour of ingesting.
- **Blocked on the converter?** Ship the games that parse, log the ones that don't, and move on.
  Partial Track B beats no Track B.
- **Network unavailable for Track A?** Do Track B first and report Track A as blocked. The two tracks
  are independent by design.
- **Genuinely unsure whether something counts as inventing prose?** It does. Drop it.
