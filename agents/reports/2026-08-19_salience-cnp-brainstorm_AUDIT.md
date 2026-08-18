# AUDIT — `2026-08-19_salience-cnp-brainstorm`

**Auditor:** Leader (Claude Opus 5) · **Date:** 2026-08-19
**Verdict: ACCEPT WITH CORRECTIONS.** Strong report, genuinely useful, and it found a real bug.
**Two claims are wrong, and one of them drives a dangerous recommendation.**

---

## 1. Boundary check — PASS

`git status` shows exactly one new file: the report. Other dirty paths
(`docs/study/*`, `docs/pytorch_learning/`, `downloads/`, `kaggle_files/`, `profiles/`)
predate the run — timestamps 2026-08-18 04:50–07:06 versus the report's 2026-08-19 00:29.
Not the worker's doing. Nothing committed, as instructed.

## 2. Verification of Part 0 — PASS, genuinely independent

Every number re-derived and matching what the leader measured separately: 288 records,
7 gold / 281 bronze, 2,284 facts, 35 gold facts, **19 salient (0.83%)**, **0/35 on gold**,
16/288 records with a label, 11 fact kinds. The command is shown and the output is real.
This is what a verification section should look like.

---

## 3. CONFIRMED findings

| # | Finding | Status |
|---|---|---|
| §1.1 | The "task" is degenerate. Task=position fails (no labelled context facts exist at inference on a new position); task=annotator collapses to a global style vector that ridge regression computes analytically | **Correct, and sharp** |
| §1.2 | Mean aggregation destroys the LINKAGE structure that `SALIENCE_PROBLEM.md` §2 says *defines* salience. No pairwise message passing between facts | **Correct — the strongest objection, and the one the leader had already flagged as the sharpest risk** |
| §1.3 | Gaussian-NLL σ is aleatoric (label noise), not the epistemic "I have not seen this kind of position" the motto requires; deterministic CNPs are overconfident OOD | **Correct and important** |
| §5.2 | Calibration/ECE/LOO on N=7–30 gold records is statistically meaningless — one flip moves precision 14% | **Correct. This kills Stage 4 of `PLAN_SALIENCE_CNP.md` as written** |
| §5.3 | **`rank_salient_facts` throws away the move delta** | **CONFIRMED — best finding in the report** |
| §5.4 | False dichotomy between a hand-coded table and a CNP; the standard middle ground was skipped | **Fair hit** |
| Part 4 | Extraction throughput ≈108 puzzles/sec | **Holds** — leader measured **146.6/sec**, 19.0 facts/puzzle. Its figure is conservative; the conclusion ("the label bottleneck was never real") stands |

### §5.3 verified in detail — this one is worth fixing immediately

`backend/training/salience_matcher.py:331-334`:

```python
collected = list(extracted["position_facts"])
for per_move in extracted["per_move"]:
    collected.extend(per_move.get("creates", []))
    collected.extend(per_move.get("removes", []))
```

The `creates` / `removes` provenance is flattened away — the merged dicts carry no marker of
which move produced them or whether they were created or removed. Inference then scores each
fact with `_inference_prior(fact)`, which reads only `kind` and static properties.

**It is worse than the report says.** The dedup key is `(kind, text)`, so a fact appearing both
as a static position fact *and* as created-by-the-move collapses to one entry, first-seen
(static) winning. The dynamic signal is lost twice.

This matters because `SALIENCE_PROBLEM.md` §4 names "the delta vs the alternatives" and "on the
forcing line" as two of the five dimensions of salience. The extractor computes them; the ranker
discards them before ranking.

---

## 4. REJECTED — §1.4 is false, and this repo's own data disproves it

The report claims: *"98%+ of Lichess puzzles are sharp tactical calculations"* and *"Quiet
positional moves do not exist in puzzle databases."*

Measured against `data/puzzles/puzzles.sqlite`:

| check | result |
|---|---|
| puzzles tagged `quietMove` | **235,511** |
| `puzzle_flags.quiet_first = 1`, rating band 1500–2000 | **401,437 of 1,472,045 = 27.3%** |
| `zugzwang` | 59,489 |
| `intermezzo` | 67,765 |
| `clearance` | 74,736 |
| `interference` | 20,575 |
| `defensiveMove` | 339,238 |

Over a quarter of the target band opens with a **quiet** move — measured by a flags table
**this project built**. The report is also self-contradictory: its own Part 4 experiment
samples `quietMove` as one of ten themes, a theme §1.4 says does not exist.

**What survives:** a weaker and fair version — puzzles are selected by engine eval divergence,
so even their quiet moves are *quiet-but-winning*, not quiet-positional in the Capablanca sense.
The concern about representational bias is legitimate. The factual claim supporting it is not.

**Consequence:** §1.4 is one of four pillars under "reject the CNP". It falls. The other three
(§1.1, §1.2, §1.3) stand, so the conclusion is weakened but **not overturned**.

## 5. REJECTED — §5.5 has the right number and the wrong cause

Claim: the invariant `assert comment in source` *"caused the parser to reject 219 out of 221
games (99.1%)"*, and the fix is to relax it.

- **The number is right.** `docs/SALIENCE_BOOK_PARSER_REPORT.md`: 221 games found, 2 OK, 219 rejected.
- **The cause is wrong.** `book_parser.py` rejects games with `reject_reason` values
  `move_parse_failure`, `ambiguous_descriptive_move`, `no_moves_found` — all **move tokenisation**.
  The `assert comment in source` at line 35 lives in `_slice` and governs *comment* extraction; it
  is not the game-rejection mechanism. Prior analysis (recorded in memory) attributes the yield
  loss to the **U+2014 em dash used as a move separator** (11,260 hits in one book), two-column
  move pairs and line-broken tokens — with only 9 of 219 rejections from descriptive ambiguity.

**Why this matters more than a misattribution.** The recommendation points at the provenance
invariant, and `provenance_check.py` (`MIN_TRACEABLE_RATIO = 0.95`) is the single gate that caught
**three consecutive fabricated corpora**. Standing rule: never relax it, its normaliser, or a test
bound. The real fix — em-dash and column-layout tokenisation — raises yield without touching
provenance at all. **Do the tokenisation fix; leave the invariant alone.**

## 6. Leader's own finding — Part 4's metric is not measurable as specified

The killer experiment scores "does the #1 ranked fact match the human puzzle theme tag?" That
requires a fact-kind → theme mapping. Comparing the two vocabularies:

- extractor kinds: `king_pressure, pawn_weakness, file_control, pin_or_xray, bishop_quality,
  color_complex, tied_defender, outpost, attack_on_valuable, protected_passed_pawn, rook_seventh`
- the ten themes it proposes: `fork, pin, discoveredAttack, defensiveMove, advancedPawn,
  deflection, hangingPiece, attraction, quietMove, sacrifice`

Only **`pin`** maps cleanly (`pin_or_xray`); `advancedPawn` partially (`protected_passed_pawn`).
**Eight of ten themes have no counterpart fact kind at all.** The experiment cannot be run as
written, and inventing the mapping would be a hand-coded salience judgement — the exact thing
doctrine forbids. The experiment needs re-specifying against a label the extractor can actually
express.

Noted also: **Approach 1 (contrastive graph delta) is not a rival — it is `SALIENCE_PROBLEM.md`
§6's own stated approach** ("contrast best line vs alternatives" + "the forcing tree"), formalised.
That is convergent evidence rather than a new idea, and it strengthens the case for building it.

---

## 7. What changes in the plan

1. **`PLAN_SALIENCE_CNP.md` Stage 4 is wrong** — drop calibration/LOO on 7–30 gold records (§5.2).
2. **Fix `rank_salient_facts` first** (§5.3). Cheap, no model, and it uses signal already computed.
3. **Mean-pooled DeepSets is the wrong encoder** if built at all (§1.2); cross-fact attention or a
   graph encoder is the minimum that preserves linkage.
4. **σ from Gaussian NLL will not support abstention** as assumed (§1.3). Revisit before relying on it.
5. **Parser yield: fix tokenisation, not the provenance invariant** (§5.5).
6. **Re-specify the killer experiment** against a measurable label (§6).
