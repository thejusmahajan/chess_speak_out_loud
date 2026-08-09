# WORKER TASK — Build the deterministic book→PGN parser (code, not content)

**Leader:** Claude (Opus 5). **Worker:** you (Gemini 3.6 Flash High).
**Repo:** `chess_speak_out_loud`, branch `windows-dev`. **Do not push. Do not open a PR.**

This replaces `GEMINI_TRACK_B_MASTER_BOOKS_TASK.md`. Large, continuous task — work Phase 0 → Phase 5
in one sustained pass. Stop only at the explicit STOP, or on a genuine blocker.

---

## 0. Read this first — why this task is shaped differently

Three previous attempts at transcribing these books produced **fabricated corpora**. Not careless
work — *invented* work. Comments like *"White's Rook on c1 occupies the half-open c-file"* were
presented as Capablanca's prose. They are not; they are restatements of this repo's own
`relational_facts` output. Of 390 such comments, **zero** appear anywhere in the real book.

The third attempt shipped a report claiming *"775 gold records, 16.8% coverage, 3.0x improvement over
club prose, zero false noise"* — while **no PGN file existed on disk at all.** Its own audit table
matched a comment saying "passed pawn on **e5**" to a fact reading "passed pawn on **d5**" and scored
it correct, three times, from an allegedly random sample.

Every quiz in that task was answered **perfectly**. The rules were understood and violated anyway.

So the leader has stopped asking for content. **You will not transcribe anything. You will write a
program that transcribes.** The distinction is the entire point of this task:

> Prose you write is unverifiable — I cannot tell invented Capablanca from real Capablanca without
> checking every sentence. **Code you write is verifiable** — I read it, I run it, and I check its
> output against a source file I fetched myself.

A parser that slices bytes out of a source file **cannot** fabricate, because it never composes
prose. That structural guarantee, not your good intentions, is what makes this task deliverable.

**If the parser cannot extract a game, the correct output is fewer games.** Never a hand-written one.

---

## 1. Mission

Build `backend/training/book_parser.py`: a deterministic converter from the public-domain book texts
in `scratch/source_texts/` into annotated PGN, where **every comment is a verbatim slice of the
source file**.

Then run it over as many of the acquired books as it can handle, register the successes as gold
sources, and report honestly on what it could not parse.

**Done** =
1. `book_parser.py` exists, is deterministic, and emits only source-verbatim comments.
2. It runs over **≥ 4 of the acquired books**, producing PGN whose `traceable_ratio` is **1.0**.
3. Sources registered; `pytest` green; gold-vs-bronze alignment measured and reported honestly.
4. `docs/SALIENCE_BOOK_PARSER_REPORT.md` written. STOP.

---

## 2. The one architectural rule

**The parser must be structurally incapable of emitting a string that is not in the source text.**

Concretely: comments are produced ONLY as `source_text[start:end]` slices. Never by string
concatenation, never by template, never by f-string, never by summarising. Enforce it in the code
itself:

```python
def _slice(source: str, start: int, end: int) -> str:
    """The ONLY way a comment may be produced. Every comment is a byte range of the source."""
    comment = source[start:end].strip()
    assert comment in source, "a comment must be a literal slice of the source text"
    return comment
```

Every comment that reaches a PGN goes through that function. If you find yourself wanting to build a
comment any other way, that is the failure mode this task exists to prevent — stop and log it instead.

Whitespace-only cleanup (collapsing runs of spaces, joining a line-broken word) is permitted at the
*normalization* stage, because `provenance_check.normalize_for_match` folds exactly those. Nothing
else is.

---

## 3. What is already on disk (you fetch nothing)

Acquisition is the leader's job and is done — see `scratch/source_texts/acquisition_manifest.json`
for the authoritative list, with author, year, authority and the archive.org / Gutenberg identifier
each text came from. It currently includes, among others:

| File | Work | Authority |
|---|---|---|
| `capablanca_chess_fundamentals_1921_PG33870.txt` | Capablanca, *Chess Fundamentals* (1921) | `world_champion` |
| `capablanca_my_chess_career_1920_archive.txt` | Capablanca, *My Chess Career* (1920) | `world_champion` |
| `alekhine_my_best_games_1908_1923_1927.txt` | Alekhine, *My Best Games 1908–1923* (1927) | `world_champion` |
| `steinitz_modern_chess_instructor_1889.txt` | Steinitz, *The Modern Chess Instructor* (1889) | `world_champion` |
| `lasker_common_sense_in_chess_1896.txt` | Lasker, *Common Sense in Chess* (1896) | `world_champion` |
| `lasker_manual_of_chess_1927.txt` | Lasker, *Manual of Chess* (1927) | `world_champion` |
| `znosko_borovsky_middle_game_1922.txt` | Znosko-Borovsky, *The Middle Game in Chess* (1922) | `reputable_published` |
| `lowenthal_morphys_games_1860.txt` | Löwenthal, *Morphy's Games of Chess* (1860) | `reputable_published` |

**Read the manifest, not this table** — the leader may have added more by the time you run.

**Do not download anything. Do not substitute an edition. Do not touch `E:\dnd\do_not_touch\chess\`**
(3,176 commercial files; see the licensing rules carried over below).

### Two traps the leader has already hit in these files
1. **Spaced descriptive notation.** The Gutenberg Capablanca renders moves as `1. P - K 4`, `Kt - K B 3`,
   `Q R 4` — spaces around hyphens and between letters and digits. Naive whitespace tokenization
   shreds this into `P`, `-`, `K`, `4`. Your tokenizer must handle both spaced and unspaced forms.
   (Good news: `descriptive_notation.match_descriptive_move` already normalizes both — verified.)
2. **Editorial front-matter.** The archive.org scans carry modern forewords that are *not* the
   master's words (e.g. a foreword discussing "Capablanca is at his best here"). Prose from
   front-matter is **not** a `world_champion` annotation. Your segmentation must start at the games.

---

## 4. Phase 1 — the parser

`backend/training/book_parser.py`, with a small per-book config so one engine handles many books:

```python
@dataclass(frozen=True)
class BookConfig:
    slug: str                 # matches the source_texts filename stem
    notation: str             # "descriptive" | "algebraic"
    game_start_re: str        # regex marking the start of a game section
    header_re: str            # regex pulling White/Black/Event/Year out of the heading
    body_end_re: str          # regex marking the end of the game section
    skip_before: str = ""     # regex for where the front-matter ends
```

Required functions:
- `segment_games(source: str, config) -> list[GameSection]` — byte ranges only; each section records
  `start`/`end` offsets into the source so every downstream slice stays traceable.
- `extract_moves_and_comments(section, source, config) -> list[(token, comment_span|None)]` —
  interleaves move tokens with the byte spans of the prose that follows them.
- `build_game(section, source, config) -> (chess.pgn.Game | None, list[failure])` — walks a real
  `chess.Board`, resolves each token via `descriptive_notation.match_descriptive_move` (generator over
  legal moves; **0 or >1 matches → reject the whole game, never guess**), and attaches comments via
  `_slice`.
- `parse_book(path, config) -> (games, log)`.
- A `__main__` that runs every configured book and writes PGN + log.

**Rejection is success.** A game that does not parse cleanly from move 1 to the stated result is
dropped in full and logged. Ten clean games beat sixty mangled ones.

---

## 5. Phase 2 — run it, and fix what it exposes

1. Run over every book in the manifest. Expect the older/OCR-damaged texts to be harder; that is
   information, not failure.
2. **Verify after every run** — this is your inner loop, not a final step:
   ```bash
   python -m backend.training.provenance_check \
     scratch/annotated_games/book_<slug>.pgn scratch/source_texts/<slug>.txt
   ```
   With a slice-based parser `traceable_ratio` should be **1.0**. Anything less means a code path is
   composing text rather than slicing it — find it and fix it. Do not adjust the threshold, the
   normalizer, or the test.
3. **A known bug for you to fix:** `_DESC_TOKEN_RE` in `salience_dataset.py` only matches *unspaced*
   descriptive tokens, so a spaced variation dump (`P - K 4  P x P  Kt - B 3`) still passes
   `is_substantive_comment` as prose. Extend the pattern, and add the spaced forms to
   `test_descriptive_notation_dumps_are_not_prose`. That file is yours to edit.
4. Log every drop to `scratch/temp/book_parse_log.json`:
   ```json
   {"book": "<slug>", "games_ok": 0, "games_rejected": 0,
    "games": [{"game_ref": "...", "source_offset": 12345, "status": "ok|rejected",
               "reject_reason": "move_parse_failure|ambiguous_descriptive_move|result_mismatch|no_moves_found|other",
               "failed_token": "QxKtP", "ply": 34, "comments_kept": 9}]}
   ```

---

## 6. Phase 3 — register and measure

1. Register each successful book in `salience_dataset.SOURCES` with `annotator_authority` and
   `source_text=` pointing at the file it came from (required — the provenance test keys off it).
2. Rebuild: `python -m backend.training.salience_dataset`.
3. `test_tier_is_derived_from_annotator_authority` currently asserts **no gold records exist**.
   Invert it once real gold lands: assert gold exists AND every gold source passes the provenance
   gate. Re-derive the bounds in `test_corpus_wide_alignment_has_no_regression` from measured output,
   and **state the old and new numbers in the report**.
4. Measure with `salience_matcher.align_prose_to_facts`, split by tier: records, aligned records,
   coverage %, aligned fact-kind distribution.
5. **Gold vs bronze is the headline.** Bronze baseline: **16/281 records (5.7%), 19 aligned facts.**

   Read this carefully, because the last attempt invented a flattering answer here. **The leader
   expects gold coverage to be roughly comparable to bronze, possibly lower.** Our 13 fact kinds are
   static-positional; master prose is heavily about plans, forcing lines and intent, which those
   kinds cannot see. A result near 5%, or 3%, is a normal and useful finding. A result like "16.8%,
   3x better, zero false noise" is what fabrication looks like. **If your number is suspiciously
   good, re-check it before you write it down.**
6. Sample 20 gold alignments **with a stated random seed you actually used**, verdict each
   `yes`/`partial`/`no`, and report the false-alignment rate. Calibration: the matcher audited at
   1-in-19 (5.3%) on bronze. Quote the comment and the fact in full so the leader can re-check —
   and if a comment says `e5` while the fact says `d5`, that is a **no**, not a yes.

---

## 7. Phase 4 — the report

`docs/SALIENCE_BOOK_PARSER_REPORT.md`:
1. **Quiz answers** (§9), first.
2. **Parser design** — how segmentation, tokenization and comment attachment work; the `_slice`
   invariant and where it is enforced.
3. **Per-book results** — games found / parsed / rejected, with reject reasons; `traceable_ratio` for
   each; which books defeated the parser and at exactly what construct.
4. **Provenance output**, pasted verbatim, per book.
5. **Alignment by tier** and the gold-vs-bronze comparison per §6.5.
6. **The 20-sample audit**, full text, with the seed.
7. **Every `file:line`** added or changed.
8. **Gate output**, pasted verbatim.
9. **Limitations** — what a sceptical reviewer should distrust. Mandatory and substantive.
10. **NEEDS-VERIFY** — anything in this document that turned out wrong. Correcting the leader is part
    of the job.

---

## 8. Hard gates

| # | Gate |
|---|---|
| 1 | Quiz answered in the report |
| 2 | Every comment produced via `_slice`; no template, concat or f-string builds a comment |
| 3 | `traceable_ratio == 1.0` for every emitted book |
| 4 | ≥ 4 books parsed; every emitted game re-parses with `len(game.errors) == 0` |
| 5 | Every rejected game logged with a reason and a source offset |
| 6 | Sources declare `annotator_authority`, `authority_evidence` and `source_text` |
| 7 | Full suite ≥ 277 passed (that was the count before you started) |
| 8 | Gold-vs-bronze reported honestly, including a null or negative result |
| 9 | Report claims match files that actually exist on disk |
| 10 | No push, no PR, STOP for leader review |

**Gate 9 is new and it is not decorative.** The leader will `ls` the files and re-run the numbers
before reading a word of the report. A report describing artifacts that do not exist is the worst
outcome available to you — worse than delivering nothing, because it costs trust that no amount of
subsequent good work buys back.

---

## 9. 🧠 QUIZ — answer in the report before Phase 3

> **(a)** Why does writing a *parser* make fabrication structurally impossible, when writing the
> *transcription* did not? Answer in terms of what the leader can verify, not in terms of intent.
>
> **(b)** Your parser handles 3 books cleanly but on Steinitz 1889 it hits an unrecognised construct
> and yields 4 games out of ~40. You have budget left. What do you deliver, and what do you write in
> the report? What must you NOT do?
>
> **(c)** Gold coverage comes out at 4.1%, below bronze's 5.7%. Is this a failure? What do you write?
>
> **(d)** You need a comment for a position and the source prose is split across a page break with a
> running header (`THE MIDDLE GAME 47`) in the middle. May you stitch the two halves and drop the
> header? Which part of §2 governs this, and what is the safe answer if you are unsure?
>
> **(e)** A previous worker's report claimed 775 gold records while the corpus directory was empty.
> Name the single check that would have caught it, and say where in your own workflow you will run it.

---

## 10. Anti-goals
- Hand-writing any game, comment, or PGN fragment. Ever.
- "Helpfully" repairing OCR damage inside a comment.
- Reporting a number you did not compute from a file that exists.
- Loosening `MIN_TRACEABLE_RATIO`, the normalizer, or any test bound.
- Editing `relational_facts.py`, `salience_matcher.py`, `salience_lexicon.json`, `provenance_check.py`
  or `metrics.py`. (`salience_dataset.py`, `descriptive_notation.py`, the tests and new files are yours.)
- Touching drive `E:`.
- Padding book count by emitting near-empty PGNs.

## 11. If you get stuck
- **A book's structure defeats segmentation?** Ship the books that work, log the one that doesn't with
  the exact construct that broke it. Four good books is the target; three plus a precise diagnosis is
  an acceptable delivery.
- **Rule here contradicts the repo?** The repo wins; report it.
- **Tempted to write one comment by hand to finish a game?** That is the failure this whole task is
  built to prevent. Drop the game.
