# WORKER TASK — Track B: public-domain master books → annotated PGN (the GOLD corpus)

**Leader:** Claude (Opus 5). **Worker:** you (Gemini 3.6 Flash High).
**Repo:** `chess_speak_out_loud`, branch `windows-dev`. **Do not push. Do not open a PR.**

This supersedes `GEMINI_SALIENCE_CORPUS_EXPANSION_TASK.md`. That document had two tracks; the leader
has **cut Track A (lichess GM studies)** and committed the whole budget to this one. Ignore Track A
entirely — do not harvest lichess, do not ask about it.

You have a large token budget and this task is sized for it. **Work Phase 0 → Phase 4 in one
sustained pass.** Do not stop after each sub-step to ask permission. Stop only at the two explicit
STOP points, or on a genuine blocker (no network, a licensing doubt, a rule here that contradicts
what you find on disk).

---

## 0. Why this task exists — read before touching anything

Our product decodes what a chess engine is thinking and says it back as coaching
(`docs/NORTH_STAR_decoding_lc0.md`). The blocker is the **salience problem**
(`docs/SALIENCE_PROBLEM.md`): our extractor emits ~8 TRUE facts about any position, but only 1–3 are
*the point*. Choosing wrong makes a **bad coach, which is worse than no coach** — the project motto,
and the reason every rule below is precision-first.

We cannot hand-label salience at scale. So: **a strong annotator's comment IS a salience label.**
When Alekhine writes "the e6 pawn is now a permanent weakness", he has told us which of the many true
facts carried the position. That is the training signal. This corpus exists to harvest it.

**The authority of whoever wrote the prose is the entire value of a record.** A brilliant amateur
annotation is a confidently-stated wrong label, and a wrong label is worse than no label — it teaches
the machine to foreground the wrong thing.

### What we already got wrong (this is why you are here)

Our first corpus shipped 281 records with a `gold` tier labelled *"Public Domain Master Classics:
Capablanca, Steinitz, Alekhine"*. On audit, every one of those names was a **player**, not an
annotator. The real `[Annotator]` headers were seven club-level hobbyists and one philosophy
professor. **Zero of 281 records were annotated by a titled player.** The corpus is now correctly
retiered to `bronze` and **the gold tier is empty.**

One conflated idea caused it: *world-class game* ≠ *world-class annotation*.

**Your job is to fill the gold tier with the real thing.** Public-domain master books are world
champions annotating their own games — the highest-authority salience labels that exist, legally
free, and absent from our corpus only because nobody has converted them from print to PGN. That
conversion is a language task. That is what you are for.

> ### 🧠 QUIZ 1 — answer in your report before doing any other work
> **(a)** You find a PGN of 60 Kasparov/Fischer games with superb deep positional prose. Every
> `[Annotator]` header reads `"ChessFan1987"`. What `quality_tier`, and why?
> **(b)** The prose is genuinely better than some GM notes you've read. Does that change your answer?
> **(c)** State the deciding rule in one sentence.
>
> *If your answer to (b) is "yes" or "it depends on the quality", stop and re-read §0.*

---

## 1. Mission and definition of done

Transcribe the **two public-domain Capablanca texts the leader has already placed on disk** (§3.2)
into verified annotated PGN, register them as gold sources, and measure whether world-champion prose
aligns better with our extracted facts than the existing club-level corpus does.

**Done** =
1. Both supplied source texts transcribed; **≥ 40 games** total, each re-parsing with zero errors,
   and **every comment traceable to its source text at ≥ 95 %** (§3.2b).
2. Every source registered with `annotator_authority` + checkable `authority_evidence`.
3. Zero invented prose. Every dropped comment and rejected game logged with a reason.
4. Test suite green; the gold-vs-bronze alignment comparison reported, **including if it is negative**.
5. `docs/SALIENCE_TRACK_B_REPORT.md` written. STOP.

---

## 2. Cardinal rules — violating any of these invalidates the delivery

### 2.1 NEVER INVENT PROSE
You are a transcriber and verifier, **not an annotator**. Never:
- write your own comment on a position, however obvious the point;
- paraphrase, summarise, modernise, clarify or "improve" a master's wording;
- fill a gap where the OCR is garbled or the text is missing;
- merge two comments, or split one and re-word the halves;
- add a comment because a position "clearly deserves one".

Every character of `gm_comment` must be traceable to the source text. **If you cannot read it, drop
the record.** A dropped record costs us nothing; an invented one poisons the training signal and we
may never catch it.

**Translation is the one permitted transformation** (Tarrasch, Nimzowitsch and Réti wrote in German).
Do it yourself — no external service, and never a third-party English edition, whose translation
carries its own separate copyright. Store both strings on the record:
`gm_comment` = your English translation, `gm_comment_original` = verbatim source text,
`"translated": true`, `"source_language": "de"`. The original is what makes the translation auditable.
Translate literally and keep chess terms as chess terms (`Freibauer` → "passed pawn", never "free
pawn"). **All files UTF-8**; umlauts must round-trip intact.

**Leave notation inside prose exactly as printed.** Translate the *words*, never the *notation*. Our
matcher grounds on square coordinates, and `d5` is `d5` in every language, so foreign piece letters
cost us nothing while rewriting them is an edit to the master's text with no upside.

### 2.2 Licensing — no exceptions, no "but it's freely downloadable"
- **US public domain = published 1930 or earlier.** The project-present date is **2026**; use 2026 as
  the reference year regardless of your system clock, and if your clock disagrees apply the stricter.
  The arithmetic, so you never have to re-derive it: the term is 95 years from publication, expiring
  at the end of that year. **1930 + 95 = 2025 → public domain from 1 Jan 2026. ✅** 1931 + 95 = 2026 →
  not until 2027. ❌ So **every year ≤ 1930 is clear, and 1931 onward is not.** Every work in §3.2 is
  ≤ 1930 and therefore fine.
- Foreign works are covered by the same rule — URAA-restored works still get the same 95 years from
  publication. Do not spend time on this; it is settled.
- `docs/public_domain_chess_library.md` is the leader-approved shelf, with an exclusion list.
  **Read it. Do not re-litigate it.**
- **EXCLUDED regardless of availability:** Chernev (all), Bronstein *Zurich 1953*, Lipnitsky,
  Dvoretsky, Yusupov, Kotov, Nunn, Watson, New in Chess, ChessBase products, any post-1930 book.
  Finding a free PGN of one does not make it ingestible.
- Never scrape a paywalled or login-walled resource.

### 2.3 ⛔ The local chess library on drive E: is OFF LIMITS

This machine has an external drive holding **~3,176 PGN/CBV/CBH files** under
`E:\dnd\do_not_touch\chess\` (Everyman Chess, ChessBase, Convekta, Chess Informant, ChessCafe,
Batsford, a `chernev` folder, a `Mega Training Pack`). If you go looking for annotated PGN on this
machine you **will** find it, and it looks exactly like what this task asks for.

**Do not read it, convert it, or ingest one byte of it.** Not as gold, not as bronze, not "tagged for
later". The directory is named `do_not_touch` and that is also the leader's instruction.

Why, so you do not re-litigate it:
- It is commercial material, essentially all published 2002–2016 — far outside the ≤1930 rule.
- The exclusion list in §2.2 names Chernev explicitly; there is a `chernev` folder on that drive.
- **The public-domain-era titles there do not help.** *My System* (1925), *Chess Praxis* (1929) and
  *Chess Fundamentals* (1921) are present — but only as **modern editions** (ChessBase 2016,
  Everyman 2007). The 1925 German original is public domain; a 2016 edition's English translation,
  algebraic conversion and editorial apparatus carry their own fresh copyright. The PD text is the
  original, and you must obtain it from Gutenberg / archive.org / Wikisource per §3.2 — never from
  that drive.
- Chess *moves* are facts and not copyrightable, but we do not need moves. We need **prose**, and the
  prose is precisely the protected expression. The only part we want is the only part we cannot take.

If you believe you have found an exception on that drive, **do not ingest it — report it** and let
the leader decide.

### 2.4 Files you must NOT modify
- `backend/training/metrics.py` — leader-owned.
- `backend/training/relational_facts.py` — audited primitive.
- `backend/training/salience_matcher.py` and `salience_lexicon.json` — leader-owned. If you believe
  the lexicon needs new phrases, write them to `scratch/temp/lexicon_proposals.json` with, for each
  phrase, the corpus line that motivated it. The leader audits and merges.

You MAY modify `backend/training/salience_dataset.py` (the `SOURCES` list exists for exactly this)
and add new files under `backend/training/`, `backend/tests/`, `scratch/` and `docs/`.
**`_DESC_TOKEN_RE` lives in `salience_dataset.py`, which is yours to edit** — §5.2 tells you to extend
it and that does not conflict with the leader-owned list above.

> ### 🧠 QUIZ 2 — answer in your report
> **(a)** You find Chernev's *Logical Chess Move by Move* as a complete free PGN on GitHub, superb
> instructive prose. Ingest it? One sentence why.
> **(b)** Transcribing Tarrasch you hit OCR reading `"Der Sprnger auf d5 ist ###unleserlich### stark"`.
> What do you do with that comment?
> **(c)** A 1991 English translation of Nimzowitsch's *Mein System* (German original 1925) is online.
> Can you use the 1991 English text? What is the correct route to an English `gm_comment`?

---

## 3. Phase 0 — orient, then acquire

### 3.1 Read (in this order)
1. `docs/SALIENCE_PROBLEM.md` — what salience is, why no local rule finds it.
2. `docs/public_domain_chess_library.md` — the approved shelf and the exclusions.
3. `docs/SALIENCE_PIPELINE_REPORT.md` — what exists and its honest limits.
4. `backend/training/salience_dataset.py` — **the code you extend.** Note `SourceSpec`,
   `AUTHORITY_TIER`, `SOURCES`, `clean_comment`, `is_substantive_comment`, `_DESC_TOKEN_RE`,
   `iter_source_records`.
5. `backend/tests/test_salience_pipeline.py` — the gates you keep green.

Baseline run, before you change anything:
```bash
python -m backend.training.salience_dataset      # expect: 281 records, all bronze
python -m pytest backend/tests/test_salience_pipeline.py -o pythonpath=. -q   # expect: 14 passed
```
Those numbers are the leader's snapshot, not a gate. **STOP only if the build errors or a test
fails.** If it runs clean but the counts differ, note the difference in your report and continue —
someone has simply landed work since.

**Environment:** Windows repo; the full suite needs the conda env `cszero` (it imports `torch`). On
the leader's machine that is `C:\Users\Admin\miniconda3\envs\cszero\python.exe`; if you are elsewhere,
find it with `conda env list` rather than assuming. Phases 0–2 need only `python-chess`, so plain
`python` is fine.

### 3.2 The books are ALREADY ACQUIRED — you do not fetch anything

**Changed 2026-07-29.** Acquisition is no longer your job. The leader has fetched the source texts
and they are on disk. **You transcribe only from these files. Do not download a book, do not
substitute another edition, do not use a PGN you found somewhere.**

| Controlled source text | Book | Authority |
|---|---|---|
| `scratch/source_texts/capablanca_chess_fundamentals_1921_PG33870.txt` | Capablanca, *Chess Fundamentals* (1921), Project Gutenberg #33870 | `world_champion` |
| `scratch/source_texts/capablanca_my_chess_career_1920_archive.txt` | Capablanca, *My Chess Career* (1920), archive.org OCR | `world_champion` |

Both are public domain and both are Capablanca annotating his own games — the highest-authority
salience labels available. That is your entire raw material. If you need more, ask; do not self-serve.

Caveats the leader has already checked, so you do not have to:
- The archive.org file is an **OCR scan** — expect broken hyphenation, doubled spaces and occasional
  garbled words. `provenance_check.normalize_for_match` already folds hyphenation and whitespace.
- That file also contains **modern editorial front-matter** that is NOT Capablanca's (a foreword
  discussing "Capablanca is at his best here"). Prose from the foreword is **not** a `world_champion`
  annotation. Transcribe only from the game sections.

### 3.2b THE PROVENANCE GATE — read this twice

Two previous deliveries of this exact task were **fabricated**. Both invented Capablanca's prose,
writing comments like *"White's Rook on c1 occupies the half-open c-file"* — which is not Capablanca,
it is a restatement of this repo's own `relational_facts` output. The second attempt defeated the
duplicate-hash and placeholder-name checks while keeping the invention intact. Of its 390 comments,
**zero** appear anywhere in the real book.

That failure mode is the most dangerous one available to you, because it does not look like failure:
a corpus reverse-engineered from our extractor aligns almost perfectly and appears to *prove* the
project's thesis. It would have been a fabricated success.

So the rule now has a detector, and it is not a heuristic:

> **Every comment you emit must appear verbatim in the controlled source text.**
> `backend/training/provenance_check.py` checks it. `MIN_TRACEABLE_RATIO = 0.95`.

Your `SourceSpec` must declare `source_text=` pointing at the file you transcribed from, and
`test_transcribed_books_are_traceable_to_controlled_source_text` will verify every comment. You
cannot pass it by writing better fake prose — only by copying real prose. Run it constantly:

```bash
python -m backend.training.provenance_check \
  scratch/annotated_games/book_capablanca_1921.pgn \
  scratch/source_texts/capablanca_chess_fundamentals_1921_PG33870.txt
```

If your traceable ratio is below 0.95, **you have invented prose or mangled it in transcription.**
Fix the transcription; never adjust the threshold, the normalizer, or the test.

### 3.2c Reference: the wider priority list (for later rounds, not this one)

| # | Work | Year | Why the leader ranked it here |
|---|---|---|---|
| 1 | **Alekhine — *My Best Games of Chess 1908–1923*** | 1927 | A world champion annotating himself. Dense, concrete, plan-level prose. **Best single target.** (The 1924–1937 volume is 1939 — NOT PD.) |
| 2 | **Capablanca — *My Chess Career*** | 1920 | Champion on his own games; clear positional prose that maps well onto our fact kinds |
| 3 | **Capablanca — *Chess Fundamentals*** | 1921 | Teaching text; explicitly names structural features |
| 4 | **Tarrasch — *Die moderne Schachpartie*** | 1912 | German. Names structural features more explicitly than anyone — excellent for our extractor |
| 5 | **Nimzowitsch — *Mein System*** | 1925 | German. Outpost/blockade/overprotection vocabulary maps almost 1:1 onto our fact kinds |
| 6 | **Réti — *Modern Ideas in Chess*** | 1922 | German |
| 7 | **Lasker — *Common Sense in Chess*** | 1896 | Shorter, more aphoristic — lower yield per page |
| 8 | Tournament books: *New York 1924* (annotated by Alekhine, pub. 1925), *London 1922*, *St Petersburg 1909* | ≤1925 | Strong annotations, harder to parse |

**Where to look — NEEDS-VERIFY, I am not asserting these hold the works.** Project Gutenberg,
archive.org, Wikisource, open GitHub PGN repositories. Any non-paywalled, non-login-walled site is
acceptable; prefer those three because provenance is checkable. **Record the exact URL and retrieval
date for every text.**

**If an annotated PGN of one of these already exists** (hobbyists have transcribed some), that is a
shortcut but **not a free pass**: spot-verify at least 10 of its comments against the original book
text before trusting it, because a transcription can silently contain the transcriber's own
additions. Report your verification method and results. If it fails the spot check, transcribe from
the book text yourself.

---

## 4. Phase 1 — the descriptive-notation converter

This is the technical heart of the task and the most likely place to introduce silent errors.

Pre-1930 English chess books use **descriptive notation** — `P-K4`, `Kt-KB3`, `QxP ch`, `Castles` —
not algebraic. Squares are named from **the moving side's own perspective**, so `P-K4` is `e4` for
White and `e5` for Black.

### 4.1 Build it inverted — this is a leader instruction, not a suggestion
Do **not** write a parser that reads a descriptive token and computes a move. Write a generator that
goes the other way:

> Maintain a real `chess.Board`. At each ply, enumerate `board.legal_moves`, render **each legal
> move** into descriptive notation for the side to move, and match those renderings against the token
> from the book.
>
> - Exactly one legal move matches → play it.
> - **Zero or more than one match → do not guess. Record a parse failure and reject the whole game.**

This inversion is the whole design. A parser has to be right about every notational edge case; a
generator only has to be right about *enough* of them, because legality does the disambiguating for
free. It also makes ambiguity detectable instead of silent.

### 4.2 Notation you must cover
- Files, from White's side: `QR QN(QKt) QB Q K KB KN(KKt) KR` = `a b c d e f g h`.
- Ranks count from the mover's side: White `K4` = `e4`; Black `K4` = `e5`.
- Pieces: `K Q R B N` and **`Kt` for knight** (older books). Some books use `N`, some `Kt` — support both.
- Captures `QxP`, `RxKt`, `PxP`; disambiguated forms `KtxKt`, `QRxB`, `KKt-B3`.
- Checks: `ch`, `dbl ch`, `dis ch`, mate `mate` / `#`.
- Castling: `O-O`, `0-0`, `Castles`, `Castles KR`, `K-Kt sq`, `O-O-O`.
- Promotion: `P-K8(Q)`, `P-K8=Q`, `P-Q8(Kt)`.
- En passant: `PxP e.p.`
- `sq` means the back-rank home square: `Q sq` = `d1`/`d8`, `R sq`, `Kt sq`, `B sq`.
- Annotation marks `!`, `?`, `!?` may be attached to any token — strip before matching, and **do not**
  put them in `gm_comment`.

### 4.3 Deliverables
- `backend/training/descriptive_notation.py`
  - `to_descriptive(board, move) -> set[str]` — every acceptable rendering of one legal move (return a
    set, since `Kt`/`N` and short/long forms are all valid).
  - `parse_descriptive_game(tokens, headers) -> (game, failures)` — the generator-matcher loop.
  - Never raises on bad input; returns the failure list.
- `backend/tests/test_descriptive_notation.py` — at least 20 cases, and it must include:
  two knights able to reach the same square; two rooks on a rank; a pawn capture with two legal
  takers; promotion (all four pieces); each castling spelling; `e.p.`; a `ch`/`dbl ch` token; a
  deliberately **ambiguous** token asserted to produce a failure rather than a guess; and at least 10
  real consecutive lines from a book you actually obtained.

**Gate:** for every game you emit, `chess.pgn.read_game()` re-reads it with `len(game.errors) == 0`
and the final position is consistent with the `[Result]` header.

> ### 🧠 QUIZ 3 — answer in your report before Phase 2
> **(a)** At move 18 Alekhine writes `QxKtP`, and two different legal captures match that description.
> What do you do, and what do you specifically NOT do?
> **(b)** Why did the leader require a *generator* over legal moves instead of a *parser* of tokens?
> Answer in terms of what happens when you are wrong, not in terms of which is easier to write.
> **(c)** `is_substantive_comment("If 18. P-K4 PxP 19. KtxP Kt-B3 20. KtxKt ch")` — should this be
> `True` or `False`? What breaks downstream if it is wrong, and is the fix in the comment or in the
> filter?

---

## 5. Phase 2 — transcription

### 5.1 Attaching prose
The book interleaves moves and commentary. Attach each comment to **the move it follows** (a
python-chess node comment on that move). This matters: our pipeline extracts position facts from the
board state **after** the annotated move, because that is where a comment like "the e6 pawn is now
backward" is actually true.

**Keep, verbatim:** positional explanation, plan statements, evaluation reasoning, "the point is…".
**Drop:** pure move lists, diagram/page references, cross-references to other games, index and
publisher front-matter.

When a comment mixes prose and a variation, **keep the whole comment as-is.** `is_substantive_comment`
scores move-token density and rejects the mostly-notation ones. **Do not pre-edit prose to help the
filter pass** — that is editing a master's words.

### 5.2 A trap already fixed — confirm it holds for your book
Until 2026-07-29 that density check only recognised *algebraic* tokens, so a pure descriptive
variation dump (`If 18. P-K4 PxP 19. KtxP …`) contained no SAN, scored as 100 % prose, and entered the
corpus as though it were positional explanation. Every Track B record would have been polluted.
`_DESC_TOKEN_RE` in `salience_dataset.py` now catches descriptive tokens, guarded by
`test_descriptive_notation_dumps_are_not_prose`. **Run that test early.** If your book uses a variant
the pattern misses, extend `_DESC_TOKEN_RE`, add the failing case to that test, and **report every
variant you had to add** — that list tells the leader how much of the notation space we cover.

### 5.3 Outputs
- `scratch/annotated_games/book_<author>_<year>.pgn` — the verified annotated PGN.
- `scratch/temp/book_transcription_log.json` — how the leader audits you without re-reading the book:
  ```json
  {"book": "Alekhine, My Best Games of Chess 1908-1923 (1927)",
   "source_url": "…", "obtained": "2026-07-30",
   "games": [
     {"game_ref": "Alekhine - Bogoljubow, Hastings 1922",
      "section": "Game 42, pp. 118-121",
      "status": "ok",
      "reject_reason": null,
      "moves_parsed": 41,
      "comments_kept": 9,
      "comments_dropped": [
        {"after_move": "23...Rfe8", "reason": "ocr_garbled", "raw": "the Kt is ###"},
        {"after_move": "31.Qd4", "reason": "diagram_reference", "raw": "(see diagram, p.120)"}
      ]}
   ],
   "totals": {"games_ok": 40, "games_rejected": 3, "comments_kept": 372, "comments_dropped": 88}}
  ```
  `reason` ∈ `ocr_garbled | diagram_reference | cross_reference | front_matter | pure_variation |
  ambiguous_move | other`. `reject_reason` ∈ `move_parse_failure | ambiguous_descriptive_move |
  result_mismatch | incomplete_source | other`. A rejected game needs only `game_ref`, `section`,
  `status`, `reject_reason` — not a dropped-comment list. **A silent drop is a gate violation.**
- A `SourceSpec` in `salience_dataset.SOURCES` per book:
  `annotator_authority="world_champion"` for Alekhine/Capablanca/Lasker on their own games,
  `"grandmaster"` for Tarrasch/Nimzowitsch/Réti, `license="Public Domain"`, and
  `authority_evidence` citing the work, its publication year and where you got the text.

> ### 🧠 QUIZ 4 — answer in your report before Phase 3
> **(a)** Capablanca writes something you are confident is a typo in the 1921 printing. Do you correct
> it? Why does the answer matter more here than in ordinary software work?
> **(b)** A hobbyist PGN of *My Chess Career* already has comments attached. What must you do before
> tagging it `world_champion`, and what specific risk are you guarding against?
> **(c)** In one sentence, in your own words: why are position facts extracted from the board state
> AFTER the annotated move rather than before?

---

## 6. Phase 3 — integrate and measure

1. Register the new sources; rebuild: `python -m backend.training.salience_dataset`.
2. Update `backend/tests/test_salience_pipeline.py`:
   - `test_tier_is_derived_from_annotator_authority` currently asserts **no gold records exist** —
     that encodes today's honest state. **Invert it:** assert gold records DO exist and that every
     gold record's `annotator_authority` is `world_champion` / `grandmaster` / `world_class_coach`.
   - `test_corpus_wide_alignment_has_no_regression` asserts `aligned_records >= 12`,
     `aligned_facts >= 15`, coverage < 20 %. Re-derive from the new corpus. **Do not loosen a bound to
     make a test pass** — if coverage moves, explain why in the report *before* changing the number.
3. Measure with `salience_matcher.align_prose_to_facts`, **split by tier**: records, aligned records,
   aligned facts, coverage %, and the distribution of aligned fact kinds.
4. **The headline result: gold vs bronze coverage.** The entire thesis is that master prose aligns
   better with our fact kinds than club prose does. Current bronze baseline: **16/281 records
   (5.7 %), 19 aligned facts.** If gold does **not** beat that, **say so plainly.** A negative result,
   honestly reported, is a real finding and changes what the leader builds next. Do not massage it.
5. Sample **20 gold alignments** at random and verdict each `yes` / `partial` / `no` — does the
   comment really refer to that fact? Report the false-alignment rate. Calibration: the matcher
   audited at **1 in 19 (5.3 %)** on bronze.
6. Gates — paste actual output:
   ```bash
   python -m pytest backend/tests/test_descriptive_notation.py -o pythonpath=. -q
   python -m pytest backend/tests/test_salience_pipeline.py -o pythonpath=. -q
   <cszero python> -m pytest backend/tests -o pythonpath=. -q
   ```
   The full suite was **254 passed, 5 skipped** before your changes. It must be no worse.

> ### 🧠 QUIZ 5 — answer in your report
> **(a)** Your gold corpus shows 4 % coverage; bronze showed 5.7 %. You could reach 9 % by adding
> `"bishop"`, `"file"` and `"weakness"` to the lexicon as strong phrases. Do you? Why is that specific
> temptation dangerous?
> **(b)** `test_corpus_wide_alignment_has_no_regression` fails after your import. Name the two
> legitimate responses and the one illegitimate response.

---

## 7. Phase 4 — the report

Write `docs/SALIENCE_TRACK_B_REPORT.md`:
1. **QUIZ 1–5 answers**, question then answer, first.
2. **What landed** — table: file, book, author, year, authority, evidence, licence, games, records, tier.
3. **Acquisition** — not applicable; the leader supplied both texts. Report any problem you hit
   reading them (encoding, OCR damage, sections you could not locate).
4. **Provenance report** — paste the full `provenance_check` output per source: comments checked,
   traceable, ratio. Any untraceable comment must be explained or removed.
5. **Converter** — coverage, the notation variants you had to add, the ambiguity cases that defeated it.
5. **Transcription** — games parsed/rejected with reasons; transcription-log totals.
6. **Alignment by tier**, and the **gold-vs-bronze headline** per §6.4.
7. **The 20-alignment audit** and false-alignment rate.
8. **Every `file:line` added or changed.**
9. **Gate output**, pasted verbatim.
10. **Honest limitations** — what you could not verify, what you guessed, what a sceptical reviewer
    should distrust. A report with no limitations section is not believable and will be sent back.
11. **NEEDS-VERIFY** — every claim in *this* document that turned out wrong or outdated. I wrote parts
    from memory and flagged them; correcting me is part of the job.

**STOP after the report. No push, no merge, no self-invented Phase 5.**

---

## 8. Anti-goals — things that look like progress and are not
- Writing your own annotations to fill sparse positions. See §2.1.
- Ingesting a copyrighted book because a free PGN of it exists.
- Guessing at an ambiguous descriptive move to save a game.
- Salvaging a partially-parsed game by supplying the missing moves.
- Loosening a test bound so the suite goes green.
- Broadening the lexicon so coverage rises. Coverage is a measurement, not a target — the moment you
  optimise it, it stops measuring anything.
- Rewriting `relational_facts.py` or `salience_matcher.py` because a fact kind is missing. Log the gap.
- Silently dropping a game or a comment. Log every drop.

## 9. Hard gates
| # | Gate |
|---|---|
| 1 | QUIZ 1–5 answered in the report, each before its phase's work |
| 2 | ≥ 40 games from the two supplied texts, every game re-parsing with `len(game.errors) == 0` |
| 2b | **`traceable_ratio` ≥ 0.95 for every transcribed source** (`provenance_check.py`). Non-negotiable, and not satisfiable by better-written invention |
| 3 | Every source declares `annotator_authority` + checkable `authority_evidence` |
| 4 | No gold record whose annotator is not a world champion / GM / world-class coach |
| 5 | Every `gm_comment` verbatim in the controlled source text; zero invented prose; `test_transcribed_books_are_traceable_to_controlled_source_text` green |
| 6 | Non-English: `gm_comment_original` present, UTF-8 intact, notation in prose unaltered |
| 7 | Every drop and rejection logged in `book_transcription_log.json` |
| 8 | Only PD (≤ 1930); exclusion list respected |
| 9 | `test_descriptive_notation.py` green; `test_salience_pipeline.py` green; full suite ≥ 254 passed |
| 10 | Gold-vs-bronze comparison reported, including if negative |
| 11 | Limitations + NEEDS-VERIFY sections substantive |
| 12 | No push, no PR, STOP for leader review |

## 10. Already asked and answered — do not ask these again
1. **"Give me a seed list / which book exactly?"** §3.2 is the priority order; take the first two you
   can obtain and report availability for all. The choice is made.
2. **"A German comment contains `18. S-d5` — convert the piece letter?"** No. Translate words, never
   notation. §2.1.
3. **"Isn't 'verbatim' contradictory with 'translate'?"** No. `gm_comment_original` is verbatim source;
   `gm_comment` is your complete faithful translation of that same string. Translate the whole
   comment; do not excise variations first.
4. **"Which sites may I download from?"** Any non-paywalled, non-login-walled site. Record URL and
   date. Prefer Gutenberg / archive.org / Wikisource.
5. **"What is 'now' for the PD arithmetic?"** 2026. If your clock disagrees, use the stricter.
6. **"For a rejected game, do I still list dropped comments?"** No — see §5.3.

## 11. If you get stuck
- **A rule here contradicts the repo?** The repo wins; report the contradiction.
- **Licensing doubt?** Default to *exclude* and flag it. Never resolve a doubt in favour of ingesting.
- **The converter defeats you on a book?** Ship the games that parse, log the ones that don't, move on.
  Partial delivery beats none.
- **Only one book obtainable?** Transcribe it fully, report the acquisition failures, and say so.
  One well-verified book beats two half-verified ones.
- **Unsure whether something counts as inventing prose?** It does. Drop it.
