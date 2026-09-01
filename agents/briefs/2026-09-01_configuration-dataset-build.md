```
Brief-ID:      2026-09-01_configuration-dataset-build
Written:       2026-09-01
Target repo:   chess_speak_out_loud
Route:         Antigravity (full workspace)
Type:          implementation -- dataset builder + encoder + tests
Blast-radius:  one new package under backend/training/, one new data directory, one test file
Reversibility: trivial (new files only; nothing existing is modified)
Failure-mode:  SILENT -- a dataset that is subtly wrong trains a model that scores well and means
               nothing, and nobody finds out until a human looks at its output weeks later
```

**Environment:** conda `cszero` → `C:\Users\Admin\miniconda3\envs\cszero\python.exe`.
No GPU. **No engine.** No network. Everything here is CPU and local disk.

---

## 1. INTENT

*(Intent outranks instructions. If any instruction below conflicts with this paragraph, the intent
wins — stop and report. Doing so is a success, never a boundary violation.)*

Build the training dataset for **configuration steering**: a set of chess positions labelled
*"the side to move is about to go wrong here"* versus matched positions where they are not, encoded
as compact bitboards, split cleanly, with the leakage alarms measured and reported.

**You are not training anything.** Thejus writes the PyTorch model himself — that is deliberate and
is part of the point of the project. Your output is the data he trains on and the code that made it,
and both have to be right, because he cannot see a labelling error by looking at a loss curve.

**Read first, in this order:**
1. `docs/plans/PLAN_CONFIGURATION_STEERING.md` — the spec. §3 and §5 are the ones that matter.
2. `ideas/2026-09-01_steering_to_tal_configurations.md` — the aim, in Thejus's own words.
3. `backend/training/puzzle_regime.py` lines 90-130 — the puzzle convention, already correct here.

---

## 2. THE TRAP THAT MATTERS MOST

The `fen` column of a Lichess puzzle is **one ply before the tactic**. The side to move in `fen` is
the side that is *about to blunder*; `moves[0]` is their blunder; the solver moves second.

**Our positive class is that `fen` position, unmodified.** Not the position after `moves[0]`.

Verified on disk 2026-09-01: 0 of 5,527,851 solution lines have odd length, which is only possible
under this convention.

If you find yourself pushing `moves[0]` to build a positive sample, you have built the wrong
dataset. Push `moves[0]` only where §4 Step 3 explicitly says to (the N1 negatives and the display
library).

---

## 3. FILES YOU MAY CREATE

Exactly these. **Do not modify any existing file.** Do not commit.

```
backend/training/config_steering/__init__.py
backend/training/config_steering/encode.py
backend/training/config_steering/build_dataset.py
backend/training/config_steering/load.py
backend/tests/test_config_steering.py
data/training/config_steering/          (output; see Step 5)
agents/reports/2026-09-01_configuration-dataset-build_REPORT.md
```

---

## 4. STEPS

### Step 1 — `encode.py`: position → 18 bitboards

```python
def encode(board: chess.Board) -> np.ndarray:   # dtype=np.uint64, shape=(18,)
def decode(bb: np.ndarray) -> chess.Board:      # inverse, for the round-trip test
def unpack(bb: np.ndarray) -> np.ndarray:       # -> float32 (18, 8, 8), for reference only
```

Plane order, **always from the side-to-move's point of view**:

```
 0-5   our   P N B R Q K
 6-11  their P N B R Q K
 12-15 castling: our K-side, our Q-side, their K-side, their Q-side (all-ones or all-zeros)
 16    en-passant target square (single bit, or empty)
 17    all ones (bias/padding plane)
```

**When black is to move, mirror the board vertically AND swap colours before encoding**, so that
"our pieces" always advance up the board. `chess.Board.mirror()` and `chess.square_mirror()` do
this; verify against a hand-checked case rather than trusting the helper. This project has already
shipped one bug from exactly this omission (`docs/writeup_attention_frame_bug.md`) — a black-to-move
frame that was silently wrong for months.

`decode()` need not restore move counters or the exact ep square legality; it must restore piece
placement, side to move and castling rights, which is what the round-trip test checks.

**CHECKPOINT 1.** Paste the output of:
```
python -c "import chess,numpy as np; from backend.training.config_steering.encode import encode,unpack; b=chess.Board(); print(encode(b).dtype, encode(b).shape); print(unpack(encode(b)).sum())"
```

---

### Step 2 — the positive class

Stream `data/puzzles/puzzles.sqlite`, table `puzzles`, `WHERE rating BETWEEN 1500 AND 2200`.

Take **200,000** rows, sampled deterministically (`ORDER BY id`, then take every *n*-th row so the
sample spans the whole table rather than one alphabetical corner; state *n* in the report).
`random.seed(20260901)` / `np.random.seed(20260901)` for everything else.

For each: the board is `chess.Board(row["fen"])`, **unmodified**. Record

```
puzzle_id, bitboards(18), label=1, source="s_err",
material_key, phase_bucket, rating, themes
```

```
material_key = f"{P}-{N}-{B}-{R}-{Q}|{p}-{n}-{b}-{r}-{q}"   # counts, side-to-move first
phase_bucket = (number of non-king pieces on the board) // 4
```

**CHECKPOINT 2.** Report: rows scanned, positives kept, the sampling stride *n*, wall-clock seconds,
and the 5 most common `material_key` values with counts.

---

### Step 3 — the negative pools

**Pool N1 — "spent tactic".** From a set of puzzle ids **disjoint from the positives** (partition the
filtered id list; do not reuse a puzzle in both classes): replay `fen` + the **entire** `moves` line
and keep the final position. Label 0, `source="n1_spent"`.

*This pool exists to teach one specific thing, and it is Thejus's constraint: a position the engine
now scores as winning is not a tactical position.*

**Pool N2 — "real quiet play".** Parse
`games_of_derdiedasdie/lichess_derdiedasdie_2026-07-21.pgn` with `python-chess`. From each game take
every 6th ply, skipping the first 8 plies (book) and the last 10 plies (conversion). Label 0,
`source="n2_quiet"`.

Report how many N2 positions exist in total — do not assume it is enough.

**CHECKPOINT 3.** Report the size of each pool separately and the wall-clock for each.

---

### Step 4 — matching, which is not optional

Bucket every negative by `(material_key, phase_bucket)`. For each positive, draw (without
replacement) a negative from **its own bucket**. A positive with no available match is **dropped —
never back-filled with an unmatched negative**.

Prefer N2 when both pools can supply a match, so the two negative sources stay separable and
`source` is recorded on every row.

If the match rate is below 60%, **stop and report before continuing** — do not silently widen the
key. The fallback, if I approve it, is to drop pawn counts from `material_key`.

**CHECKPOINT 4.** Report: match rate, final positive count, final negative count, and the
counts of `n1_spent` vs `n2_quiet` in the matched set.

---

### Step 5 — split and write

Split **by puzzle id hash**, not by row: `int(hashlib.md5(pid.encode()).hexdigest(), 16) % 100`
→ `<80` train, `80-89` val, `>=90` test. N2 rows split by game index the same way. **Every row
derived from one puzzle must land in one split.**

Write to `data/training/config_steering/`:

```
train.npz  val.npz  test.npz     # keys: bb (N,18) uint64, y (N,) uint8, motif (N,20) uint8
manifest.json                    # counts per split/class/source, the 20 themes in fixed order,
                                 # the seed, the sampling stride, the build timestamp
STATS.md                         # the alarms of Step 6, in a table
```

The 20-theme vocabulary: the 20 most frequent whitespace-separated tokens in `themes` across the
**positive** rows only. Freeze the order in `manifest.json`. Multi-hot per row. N2 rows get an
all-zero motif vector.

`load.py` exposes one function, returning **numpy, not torch** — the torch `Dataset` is Thejus's to
write:

```python
def load_split(name: str) -> dict:   # {"bb": (N,18) uint64, "y": (N,), "motif": (N,20), "meta": {...}}
```

**CHECKPOINT 5.** Paste `ls -l data/training/config_steering/` and the contents of `manifest.json`.

---

### Step 6 — the three alarms

Compute these and put them in `STATS.md`. They decide whether the dataset is usable at all.

| alarm | how | threshold |
|---|---|---|
| **A1 side-to-move balance** | fraction of white-to-move in each class *before* the POV flip | 50 ± 2% in both classes |
| **A2 material overlap** | top-10 `material_key` by frequency, positives vs negatives, side by side | the two lists must substantially overlap |
| **A3 material-only AUC** | logistic regression (`sklearn`) on **10 features only** — the ten piece counts from `material_key` — trained on train, AUC on val | **must be < 0.65** |

**A3 is the one that matters.** If a model that can see nothing but piece counts separates the
classes, then a network trained on this data will score well and will have learned nothing about
configuration. **If A3 ≥ 0.65, stop and report. Do not proceed and do not tune it away.**

**CHECKPOINT 6.** Paste `STATS.md` in full.

---

### Step 7 — tests

`backend/tests/test_config_steering.py`, `pytest`, no network, no engine, no reliance on the built
`.npz` files (build tiny fixtures in-test):

1. **round trip** — `decode(encode(b))` restores piece placement, turn and castling rights, for 200
   positions drawn from the puzzle DB.
2. **colour invariance** — for a position and its `mirror()`, the *our/their* piece planes are
   identical. This is the frame guard; make it strict.
3. **puzzle parity** — for 500 rows: `chess.Board(row["fen"]).turn != puzzle_position(row)[0].turn`,
   and `len(row["moves"].split()) % 2 == 0`.
4. **matching invariant** — over a small synthetic build: every kept positive has a negative with an
   identical `(material_key, phase_bucket)`.
5. **split disjointness** — no `puzzle_id` appears in two splits.

**CHECKPOINT 7.** Paste the output of:
```
python -m pytest backend/tests/test_config_steering.py -q
python -m pytest backend/tests -q --deselect backend/tests/test_ts2_no_hang.py::test_ts2_orphan_future_cancellation_handled
```
The second command must show **no new failures** against the suite as you found it. Record the
baseline count *before* you start, and both numbers in the report.

---

## 5. REPORT

`agents/reports/2026-09-01_configuration-dataset-build_REPORT.md`, containing every checkpoint's
pasted output, the wall-clock of each step, and a final section:

> **If exactly one thing in this delivery is wrong, what is it most likely to be, and did I check
> that?**

Answer it as a prediction, not a disclaimer. It is scored later.

Also state anything you could not verify. A non-empty "could not check" section is expected.

---

## 6. STOP AND ASK

Not covered by this brief: modifying any existing file; calling LC0, Stockfish or any engine;
network access; training or fine-tuning anything; widening `material_key` after a low match rate;
proceeding past a fired alarm; committing; changing the rating window, the 200,000 target, the seed,
or the split ratios.

If the task appears to require any of these, **stop and report**. A stop with a clear question is a
successful delivery.

**Do not commit. The leader audits the dataset and re-runs A3 independently before Thejus trains on
it.**
