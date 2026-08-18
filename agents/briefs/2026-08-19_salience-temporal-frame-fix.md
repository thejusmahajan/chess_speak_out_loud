```
Brief-ID:     2026-08-19_salience-temporal-frame-fix
Written:      2026-08-19
Target repo:  chess_speak_out_loud (this one)
Route:        Antigravity (full workspace)
Type:         implementation (correctness fix)
Status:       ACTIVE
Depends on:   2026-08-19_salience-cnp-brainstorm (its §5.3 found the underlying defect)
```

# Fix the temporal frame in `rank_salient_facts`

`backend/training/salience_matcher.py` currently asserts **future facts as present facts**.
This is a correctness bug in the exact function that decides what the coach says, and
accuracy is this project's one non-negotiable rule: **a false fact is a bad coach.**

Scope is deliberately narrow. Read §6 before you start — there is one thing you must NOT
do, and it is the kind of change that looks helpful.

---

## 1. The bug, with a reproducible witness

`rank_salient_facts(fen, pov, line_ucis=...)` merges three kinds of fact into one flat,
undifferentiated list:

- `position_facts` — true of the **queried position**
- `per_move[i].creates` — true only **after** move `i` of the line
- `per_move[i].removes` — true **before** move `i`, false after

They come out indistinguishable, phrased in the present tense. Run this yourself:

```
C:\Users\Admin\miniconda3\envs\cszero\python.exe -c "
import chess
from backend.training.salience_matcher import rank_salient_facts
fen='r1b2rk1/pp1nqppp/2pbpn2/8/2BP4/2N1PN2/PP2QPPP/R1B2RK1 w - - 0 11'
b=chess.Board(fen)
print('d3:', b.piece_at(chess.D3), ' c4:', b.piece_at(chess.C4), ' e4:', b.piece_at(chess.E4))
for f in rank_salient_facts(fen, chess.WHITE, line_ucis=['c4d3','f6g4','e2e4'], top_k=6):
    print(round(f['salience_score'],2), f['text'])
"
```

Observed today:

```
d3: None   c4: B   e4: None
0.91  P on e6 is pinned by e4 to Q on e7
0.56  White's c1 bishop is a bad bishop - 5 of its own pawns sit on its colour...
0.46  White's d3 bishop is active - unobstructed by its own pawns, controlling 9 squares
...
```

- **"P on e6 is pinned by e4"** — scored highest of all. There is **no piece on e4**. That pin
  is created three plies later by `e2e4`.
- **"White's d3 bishop is active"** — **d3 is empty**. The bishop is on c4 and only reaches d3
  after the first move of the line.

Both are false statements about the position that was asked about. This belongs to the
documented **POV/frame failure family** in `LEADER_BIBLE.md` §5 — the same class of bug as
white-POV/mover-POV confusion, but on the **time** axis rather than colour.

### A second, quieter defect

`salience_matcher.py:336` dedups with `key = (fact["kind"], fact["text"])`. When the same
fact text arises both statically and as created-by-a-move, the two collapse into one entry
and the **first seen (static) wins**. The dynamic instance disappears silently.

---

## 2. Scope and boundaries (hard)

**Create or edit ONLY:**
```
backend/training/salience_matcher.py
backend/tests/test_salience_pipeline.py
```

**Do NOT touch — a write here is a boundary violation:**
- `backend/training/relational_facts.py` — the extractor is audited and locked by regression
  tests. It already produces the right data; this bug is entirely in the consumer.
- `backend/training/metrics.py` — leader-owned.
- `backend/training/salience_dataset.py`, `salience_lexicon.json`, `provenance_check.py`
- Any file under `docs/`, `agents/`, `data/`

If you believe you need something outside this list, **STOP and report it.**

---

## 3. What to build

### 3.1 Tag every fact with its temporal frame

Every fact returned by `rank_salient_facts` must carry these three fields, always present:

| field | type | value |
|---|---|---|
| `delta_role` | `str` | `"static"` \| `"created"` \| `"removed"` |
| `delta_move` | `str \| None` | the UCI of the move that created/removed it; `None` when `static` |
| `delta_ply` | `int \| None` | 0-based index of that move within `line_ucis`; `None` when `static` |

`static` means the fact came from `position_facts` — true of the queried position.

### 3.2 Qualify the `text` of non-static facts

**This is the load-bearing part of the fix.** Downstream consumers (ultimately an LLM
translator) read `text`. A tag they might ignore is not enough — the sentence itself must not
be able to state a falsehood. Encode the frame in the artifact rather than trusting the reader.
That is the standing lesson from the POV bugs.

Rewrite `text` for non-static facts, leaving `static` text **byte-identical** to today:

- `created` → `"After {san_prefix}: {original_text}"`
- `removed` → `"No longer true after {san_prefix}: {original_text}"`

`san_prefix` is the line in **SAN**, from the start of `line_ucis` up to and including the
move responsible, space-separated — for the witness line that is `"Bd3 Ng4 Qe4"`. Derive SAN by
pushing the UCI moves onto a board built from the queried FEN, and take whatever
`python-chess` produces — including check/mate suffixes (`+`, `#`). Do not hand-format it and
do not strip suffixes. (Note `e2e4` here is a **queen** move, `Qe4`, not a pawn push — this is
exactly why SAN must be derived, never assembled from the UCI string.)

Preserve the unmodified sentence in a new field `text_raw` so nothing is lost.

Applied to the witness above, the top fact must read:
`"After Bd3 Ng4 Qe4: P on e6 is pinned by e4 to Q on e7"` — which is true.

### 3.3 Fix the dedup collision

Change the dedup key to include the temporal frame, so a static fact and a created fact with
the same underlying text no longer collapse:

```python
key = (fact["kind"], fact["text_raw"], fact["delta_role"], fact["delta_move"])
```

### 3.4 Keep the no-line behaviour byte-identical

When `line_ucis` is empty or `None`, every fact is `static`, every `text` is unchanged, and
the returned ordering and scores are exactly what they are today. This is a hard requirement
and it has its own test (§4.6).

---

## 4. Tests — each must be a REAL guard

Add to `backend/tests/test_salience_pipeline.py`. **These are mutation-checked**: the leader
will break the production code each test claims to protect and confirm the test goes red. A
test that would still pass with the feature deleted rejects the whole submission.

1. `test_created_facts_are_not_asserted_about_the_queried_position` — **the regression witness.**
   Use the exact FEN and line from §1. Assert that every returned fact with
   `delta_role == "created"` has `text` starting with `"After "`, and that **no** returned
   `text` contains the substring `"d3 bishop is active"` without an `"After "` prefix. This is
   the test that would have caught the bug.
2. `test_every_fact_carries_a_temporal_frame` — every returned fact has `delta_role`,
   `delta_move`, `delta_ply`, `text_raw`; `delta_role` is one of the three legal values;
   `delta_move`/`delta_ply` are `None` **iff** `delta_role == "static"`.
3. `test_san_prefix_is_correct` — for the §1 line, a fact created by the third move carries
   `delta_ply == 2`, `delta_move == "e2e4"`, and a `text` beginning `"After Bd3 Ng4 Qe4: "`.
   Assert the exact string. (Verified by the leader against `python-chess`; `e2e4` is a queen
   move from e2, so `Qe4` is correct and `e4` is not.)
4. `test_removed_facts_are_marked_as_no_longer_true` — use FEN
   `8/2r1b3/1pk5/6P1/5q2/3R4/Q1P1K3/8 w - - 5 38` with line `["a2d5"]`. The fact whose
   `text_raw` is `"White's queen on the open a-file"` must come back with
   `delta_role == "removed"` and `text` beginning `"No longer true after Qd5#: "`. The `#` is
   correct — that move is checkmate, and SAN suffixes are kept verbatim (§3.2).
5. `test_static_and_created_variants_both_survive_dedup` — construct a position and line where
   the same `(kind, text_raw)` appears both statically and in a `creates` list; assert **both**
   are returned with distinct `delta_role` values. If you cannot find such a position, say so
   in your report rather than weakening the test — a synthetic fact dict passed through the
   dedup helper is an acceptable substitute, but it must exercise the real dedup code.
6. `test_no_line_output_is_unchanged` — call with `line_ucis=None` on the §1 FEN; assert every
   `delta_role == "static"`, every `text == text_raw`, and that the `(text, salience_score)`
   pairs equal the values recorded **before** your change. Capture that baseline first (§5,
   step 1) and hard-code it in the test.
7. `test_gm_comment_path_still_works` — the prose-alignment branch (`gm_comment` given) still
   returns aligned facts and is unaffected by the new fields.

---

## 5. Gate — run these and paste REAL terminal output

1. **First, before changing anything**, capture the baseline and save it:
   ```
   C:\Users\Admin\miniconda3\envs\cszero\python.exe -c "..." > agents/reports/tmp_before.txt
   ```
   Run both the §1 witness command and the same call with `line_ucis=None`. Paste both.
2. Full backend suite **before** your change — record the exact pass/skip counts.
   ```
   C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests -q
   ```
   Do **not** target a remembered number; report what you actually observe. If
   `test_ts2_orphan_future_cancellation_handled` fails, it is a known load-sensitive flake —
   note it and move on.
3. Make the change.
4. Full backend suite **after**. The counts must match step 2 plus your new tests, with no
   new failures. Paste it.
5. Re-run the §1 witness command and paste the output. Every non-static fact must now be
   temporally qualified.
6. `git status` — only the two permitted files changed. Delete `tmp_before.txt` before you
   finish; it is scratch, not a deliverable.

---

## 6. What you must NOT do — read this twice

**Do not change how facts are scored.** Do not touch the values in `INFERENCE_PRIORS`, do not
add a bonus for `created` or `removed` facts, do not reweight anything.

It is tempting, and it looks like an obvious improvement: *"a fact the move creates is surely
more salient than a background fact."* Resist it. That would be **hand-coding salience**, which
this project's doctrine forbids (`LEADER_BIBLE.md` §4, §6) after a metric named "sacrifice"
turned out to measure complexity with no material check and false conclusions were built on it.

The decisive reason: **we currently cannot measure whether such a change helps.** The corpus
yields 19 salience labels in total and **zero** on the gold tier. A reweighting we cannot
evaluate is an unfalsifiable judgement — exactly the failure mode above.

This brief makes the temporal signal **correct and available**. Deciding what to do with it is
a separate, later, measurable step.

---

## 7. Your report

Write `agents/reports/2026-08-19_salience-temporal-frame-fix_REPORT.md` covering:

1. Every gate command and its real outcome, including the before/after suite counts.
2. Whether test 5 used a real position or the synthetic substitute, and why.
3. Anything in this brief that turned out to be wrong about the code. **Deviating because
   reality contradicts the spec is a good outcome** — report it with evidence. Deviating to
   make a gate pass is not.
4. Anything you did not do, explicitly listed.
