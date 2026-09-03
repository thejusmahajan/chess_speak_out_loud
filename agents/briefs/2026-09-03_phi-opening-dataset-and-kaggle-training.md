```
Brief-ID:      2026-09-03_phi-opening-dataset-and-kaggle-training
Written:       2026-09-03
Target repo:   chess_speak_out_loud
Route:         Antigravity (full workspace) for the build; Thejus runs the Kaggle notebook
Type:          dataset build + training run
Blast-radius:  one new dataset directory, one new archive, one Kaggle run
Reversibility: easy -- nothing existing is overwritten
Failure-mode:  SILENT -- an opening dataset whose negatives are not openings learns "is this an
               opening", scores well, and means nothing
```

**Environment:** conda `cszero` for the build (CPU, no engine, no network). Kaggle for the training.

---

## 1. INTENT

*(Intent outranks instructions. If any instruction below conflicts with this paragraph, the intent
wins — stop and report. Doing so is a success, never a boundary violation.)*

**Thejus has decided to train Φ on opening puzzles, for Tal steering in the openings.** Build the
dataset and train it on Kaggle.

His reasoning, and it is the aim this serves:

> *"Preparation against opponents is one of the motifs of Tal steering. Consider the phase of a game
> where the opponent doesn't expect to be steered to an attacking position. That is exactly what Tal
> would do. And say the opponent is calm in his position thinking that it is quite suddenly
> surprised by a pawn or piece sacrifice which is objectively not solid but contains wild attacking
> possibilities, the correct non losing continuation mostly hangs on one or two moves sequence which
> is not at all obvious is something I will look for."*

The opening is where a wrong move is punished fastest, and where preparation pays. This dataset
exists to make Φ good at that phase specifically.

---

## 2. The measurements this brief is built on — all taken 2026-09-03, all re-runnable

**The corpus is richer than expected.** `opening_motifs` holds **1,578 distinct opening tags**, and
they carry the accepted/declined distinction explicitly: `Danish_Gambit_Accepted_Classical_Defense`,
`Italian_Game_Evans_Gambit_Declined`. **276 tags have ≥1,000 puzzles**; rolled up to family, **62 of
129 families have ≥2,000**. The Danish family alone carries ~9,460 (proxy count).

**Availability:** the 1500–2200 band holds **1,907,960** puzzles, ~**4.39%** tagged `opening`
(≈ **84,000**), and **98%** of those carry a named `opening_tags` value.

**⚑ The result that sets the gate.** Φ (`phi_net/runs/phi_b2.pt`) was measured on the *existing*
test split, sliced by phase:

| slice | AUC |
|---|---|
| opening positives vs **opening** negatives | **0.7211** |
| opening positives vs all negatives | 0.7543 |
| **non**-opening positives vs all negatives | 0.6867 |
| whole test split (reference) | 0.6908 |

**Φ is already strongest in the opening, not weakest** — despite only 5.98% of its training
positives being opening positions. That is the number to beat, and it is a demanding one.

**⚠ And it is measured on only 1,086 rows (799 positives / 287 negatives).** Bootstrap over 2,000
resamples: **SE 0.0164, 95% CI [0.6876, 0.7536]**. A +0.03 improvement sits *inside* that interval.
**So the new build must produce a much larger opening test set**, or the comparison cannot decide
anything.

**One more measurement that shapes the sampling.** Opening puzzles are *less* Tal-like than
middlegame ones: `sacrifice` **0.66×**, `kingsideAttack` **0.70×**, `mate` 0.72×; but `short` 1.10×
and `fork` 1.22×. So opening errors are punished **fast and materially**, not usually by mate — and
naive opening oversampling would *dilute* the sacrificial signal. §4 Step 2 handles this.

---

## 3. WHAT YOU MAY TOUCH

```
backend/training/config_steering/build_opening_dataset.py      (new)
data/training/config_steering_opening/                          (new output)
dist/config_steering_opening.zip                                (new archive)
backend/tests/test_opening_dataset.py                           (new)
agents/reports/2026-09-03_phi-opening-dataset-and-kaggle-training_REPORT.md
```

**Do not modify** the existing `build_dataset.py`, `data/training/config_steering/`, `metrics.py`,
or anything in `phi_net/` except by reading it. The existing dataset and model stay exactly as they
are — this is a second dataset, not a replacement. Do not commit.

---

## 4. STEPS

### Step 1 — reuse, do not reinvent

`build_dataset.py` already implements the pieces this needs and they have been audited twice:
`s_err` extraction (the puzzle `fen`, **one ply before the tactic** — 0 of 5,527,851 solution lines
have odd length), the 18-plane POV-flipped encoder, `material_key` × `phase_bucket` × `in_check` ×
`mobility_bucket` matching, split-by-puzzle-id-hash, and alarms A1–A4.

**Import and reuse them.** Any divergence in the encoder or the matching key makes the two datasets
incomparable, and comparability is the entire point of this experiment.

**CHECKPOINT 1.** List which functions you imported from `build_dataset.py` and which you had to
write fresh, with one line on why for each fresh one.

---

### Step 2 — positives: opening, stratified, and weighted toward sharp

**⛑ AMENDED 2026-09-03 by Thejus: use the WHOLE rating range, not 1500–2200.**

> *"is our puzzles limited to 2200 rating max? If yes, pull all the db. Anyone even the plus
> 3000s can go astray in the opening."*

He is right, and the reason is stronger than volume: **a Lichess puzzle's rating is a *difficulty*
rating** — it rises when solvers fail it — not the rating of the players in the game. So a
high-rated puzzle is by definition one whose saving move is hard to find, which is exactly his
criterion: *"the correct non losing continuation mostly hangs on one or two moves sequence which is
not at all obvious."* Capping at 2200 was systematically discarding the hardest examples.

So: `WHERE themes LIKE '%opening%'`, **no rating filter**. Measured availability, from a 178,442-row
sample (3.2% of the DB), extrapolated:

| rating band | share of opening puzzles | extrapolated count |
|---|---|---|
| below 1500 | **62.6%** | ~168,000 |
| 1500–2200 (what we used) | 31.8% | ~85,000 |
| 2200–2600 | 4.8% | ~12,800 |
| 2600–3000 | 0.8% | ~2,200 |
| above 3000 | 0.0% | — |

**Full range is ~3.1× more opening puzzles (~268,000).** But note where the volume is: the gain is
overwhelmingly *below* 1500, and the hard band he cares about is only ~15,000 puzzles in total.

**So widening the range is not enough on its own — stratify it.** Sample so that puzzles rated
**≥2200 reach at least 20% of positives**, despite being ~5% of the pool. Left unstratified they
are drowned by the sub-1500 material, and the sub-1500 band is the *opposite* of what this dataset
is for.

**Record `rating` per row** and **report AUC by rating band** (below 1500 / 1500–2200 / above 2200)
in the gate table. If Φ-opening does well on easy puzzles and no better than the general model on
hard ones, that is the single most useful thing this experiment can tell us, and a pooled number
would hide it.

Target **80,000 positives before matching** (raised from 60,000 now that the pool is ~268,000) (~40,000 expected to survive at the 65% match rate seen
on the general build, giving ~4,000 in the test split — enough to halve the current SE).

Two constraints, both of which prevent a silently useless dataset:

**2a. Oversample the sharp subset.** Within the opening pool, sample so that puzzles carrying
`sacrifice` **or** `kingsideAttack` reach **at least 25%** of positives (they are ~9% naturally).
That is the population Thejus's aim actually concerns — the objectively-unsound-but-dangerous
sacrifice. Report the achieved share.

**2b. Cap any one opening family.** Roll `opening_tags` up to a family key = the tag truncated at
the second underscore, **but keep any `Accepted` / `Declined` token in the key** (so
`Italian_Game_Evans_Gambit_Declined` → `Italian_Game_Declined`, not `Italian_Game`). Thejus was
explicit that accepted and declined are different objects, and the data agrees.

**No family may exceed 15% of positives.** Sicilian alone carries 132,356 puzzles; uncapped, the
model learns "Sicilian", not "danger". Report the top 15 families with their shares.

Record `opening_family` and `sharp` (bool) **per row** in the `.npz`, so both can be sliced at
evaluation time.

**CHECKPOINT 2.** Positives kept, achieved sharp share, top-15 family table, and the number of
distinct families represented.

---

### Step 3 — ⚑ the trap: the negatives must also be openings

**This is the one thing that will silently ruin the dataset.** If positives are opening positions
and negatives are middlegames, the model learns *"is this an opening"* — it will score beautifully
and mean nothing. It is the same shape as the first `config_steering` build, which passed every
alarm it was given and was separable on check status and mobility.

Both negative pools must be **opening-phase positions**:

- **N1 (primary) — "spent tactic" from opening puzzles.** Same construction as the general build:
  replay `fen` + the full `moves` line, keep the final position. Drawn from opening puzzles in a set
  of puzzle ids **disjoint from the positives**. Exclude in-check and `mate`-themed puzzles, exactly
  as before. **Prefer N1**: it comes from the same population as the positives, so it cannot carry a
  source signature.
- **N2 (secondary) — real opening play from his own games.** From
  `games_of_derdiedasdie/lichess_derdiedasdie_2026-07-21.pgn`, take positions **within the first 20
  plies only**. Report the pool size.

Then match with the **unchanged** key (`material_key`, `phase_bucket`, `in_check`,
`mobility_bucket`). Positives with no match are dropped, never back-filled.

**⚠ Expect A3 to be near 0.5 by construction** — in the opening everyone still has all their pieces,
so material carries almost no information. That makes A3 *uninformative here rather than reassuring*,
which is exactly why Step 4 adds a new alarm.

**CHECKPOINT 3.** Pool sizes for N1 and N2, match rate, and the final per-source counts.

---

### Step 4 — alarms: A1–A4 unchanged, plus A5

Run A1–A4 exactly as the general build does, and add:

**A5 — phase-only AUC.** Logistic regression on **five features only**: total piece count, pawn
count, the four castling-rights bits collapsed to a count, `in_check`, and `n_legal_moves`.
**Must be < 0.60.** If a model that can see nothing but "how developed is this position" separates
the classes, the negatives are not really openings and the whole build is void.

**If A5 fires, stop and report. Do not tune it away.** A fired alarm is a stop, not a parameter.

**CHECKPOINT 4.** `STATS.md` in full, with A1–A5 and the single-feature AUCs.

---

### Step 5 — archive and hand over

Write `data/training/config_steering_opening/` in the same format as the general build (`bb`, `y`,
`motif`, `source`, plus `opening_family` and `sharp`), with `manifest.json` and `STATS.md`. Build
`dist/config_steering_opening.zip` **flat** — no folder inside the archive; the notebook copies
`/kaggle/input/<ds>/*` and a nested zip is the trap `resolve_data_dir` had to be written for.

**CHECKPOINT 5.** `ls -l` of the output, `manifest.json`, and a sha256 round-trip check that the
extracted files match.

---

### Step 6 — the Kaggle run (Thejus executes; you prepare and report)

Use the existing notebook `dist/kaggle_phi_net.ipynb` unchanged — it discovers its inputs by content
and handles all three mount shapes. Two runs, both minutes on a single GPU:

- **Run A (primary): fine-tune from `phi_net/runs/phi_b2.pt`.** Load the existing weights, train on
  the opening dataset at a reduced learning rate (start `2e-4`, an order below the `2e-3` used for
  scratch training). This starts from a model that already knows tactics.
- **Run B (control): from scratch**, identical settings to the general build.

Both need the `--no-amp` escape available, and both must print the gate table.

**CHECKPOINT 6.** For each run: best val AUC, per-source AUC, wall clock, and the full gate table.

---

### Step 7 — the gate that decides this experiment

Report all of these on the **held-out test split of the opening dataset**:

| # | measurement | bar |
|---|---|---|
| **G1** | Φ-opening AUC, opening positives vs opening negatives | **> 0.7211**, and the **bootstrap 95% CI must not contain 0.7211** |
| **G2** | the *general* `phi_b2.pt` scored on the **same** opening test rows | reported for comparison, not a bar |
| **G3** | AUC vs N1 and vs N2 separately | if vs-N2 ≫ vs-N1, the model found a source signature, not danger |
| **G4** | AUC restricted to the `sharp` subset | this is the population Thejus's aim concerns |

**G1 is the experiment.** The comparison is against Φ's *existing* opening performance, not against
an abstract 0.70 — a gate belongs to the decision it governs, and the decision here is whether an
opening-specialised model beats the general one on openings.

**Report the bootstrap CI (2,000 resamples) for every AUC.** The current baseline has SE 0.0164 on
1,086 rows; without a CI, a 0.02 difference is indistinguishable from noise and we will fool
ourselves.

**CHECKPOINT 7.** The four measurements with CIs, and a one-line verdict on G1.

---

## 5. REPORT

`agents/reports/2026-09-03_phi-opening-dataset-and-kaggle-training_REPORT.md`, every checkpoint's
real pasted output, plus:

> **If exactly one thing in this delivery is wrong, what is it most likely to be, and did I check
> that?**

A non-empty "could not check" section is expected.

---

## 6. STOP AND ASK

Not covered: modifying the existing dataset, `build_dataset.py`, `metrics.py` or `phi_net/`;
changing the rating window, the matching key, the encoder, or the split scheme; tuning any alarm
threshold; proceeding past a fired alarm; committing; spending Colab units.

**A stop with a clear question is a successful delivery, and a fired alarm is a stop.**
