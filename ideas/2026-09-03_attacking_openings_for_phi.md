# Training on attacking games in an opening — Thejus's idea

**Origin:** Thejus, 2026-09-03. Raw source: `temp/idea1.txt`.
**Status:** idea recorded, measured against the corpus we already hold. No brief filed by the leader yet.

> **Section 1 is his words, unedited.** Everything after it is measurement or the leader's view and
> can be argued with. Section 1 cannot be edited. *(This convention exists because on 2026-09-01 a
> leader-written discussion was pointed at one of his ideas and he had it deleted from disk.)*

---

## 1. The idea — 2026-09-03, verbatim

> Does it make sense to train attacking wild games played by both humans and engines in a particular
> opening? Since opening moves are hard to calculate for Tal steer because of the sheer number of
> opponent possiblities, it would add some knowledge how an attacking game could behave in the
> opening. We could take a dataset of attacking games played in a particular opening, say danish
> gambit and train the ResNet on that? What do you say?

---

## 2. The diagnosis is correct — measured 2026-09-03

**Φ is under-trained on the opening, and by a factor of eight.** Counted over all 130,874 `s_err`
positives in the built dataset, using the frozen theme vocabulary in `manifest.json`:

| theme | positives | share |
|---|---|---|
| `endgame` | 62,376 | **47.66%** |
| `middlegame` | 60,669 | **46.36%** |
| **`opening`** | **7,829** | **5.98%** |

So the instinct is right: the phase where steering is hardest is the phase Φ has seen least.

**But the answer in `temp/idea1.txt` overstates it.** It says Φ "was trained on 261,000
middlegame/endgame tactical puzzles". Two corrections:

- **261,748 is the total row count including negatives.** The positives are **130,874**.
- **Opening positions are not absent** — there are 7,829 of them. Under-represented, not missing.

That distinction changes the fix from *acquire a new corpus* to *sample the one we have differently*.

---

## 3. What is already on disk — measured, not recalled

| fact | value |
|---|---|
| puzzles in the 1500–2200 rating window | **1,907,960** |
| share of that band tagged `opening` (sampled) | **4.39%** → roughly **84,000 opening puzzles available** |
| of those, carrying a named `opening_tags` value | **98.0%** |
| `opening_motifs` table | **57,033** rows of `opening_tag × theme × n` |
| opening positives actually used by Φ | **7,829** (a stride-9 sample) |

**There is about a ten-fold increase available for free, in the corpus we already own, with the
same `s_err` label semantics** — a real human of a known rating who actually went wrong. No
scraping, no new licence, no second labelling scheme.

Most common opening tags in the band: Sicilian Defense, Italian Game, French Defense, Scandinavian,
Caro-Kann, Queen's Pawn Game.

---

## 4. Leader's view

**Do the sampling change; do not curate a "romantic corpus" first.**

Three reasons, in order of weight.

1. **Selecting games by opening *name* is a proxy for sharpness, not sharpness.** "Danish Gambit"
   does not mean the game was sharp — gambits get declined into quiet positions constantly. Using an
   opening label as a stand-in for attacking character is the **metric-mislabel family**
   (`LEADER_BIBLE.md` §5), and it is the same mistake as `had_tal_move`, which measured complexity
   and was used as "sacrifice" until the London System came out looking dangerous.
2. **The small-N objection in the file is correct and it applies to the whole plan.** A
   542k-parameter network on a few thousand Danish Gambit games memorises move orders. The file
   proposes fixing this by widening to a dozen gambit families, which reduces memorisation but keeps
   the proxy problem in (1).
3. **A sampling change is a filter parameter** — cheap, reversible, and it reuses a pipeline that
   has already been audited twice. A curated corpus is a new acquisition, a new labelling decision,
   and a new set of ways to be silently wrong.

**Concretely:** rebuild with the positive sampler stratified so `opening`-tagged puzzles reach
roughly a third of the positives instead of a sixteenth, keeping the same matched-negative
machinery and the same A1–A4 alarms. Then re-run the B1 rung. If opening AUC improves while overall
AUC holds, the diagnosis is confirmed at a cost of one CPU build and 48 seconds of GPU.

**Report `opening` AUC separately** in `evaluate.py`, the way N1 and N2 are already reported. Right
now a gain in the opening would be invisible inside a single aggregate number.

## 5. Two things in `temp/idea1.txt` to treat carefully

**"Approach A: the attacking policy prior."** Training a network to predict *which move an attacking
player chose* is a different object from Φ. Φ is a potential function over configurations that
never consults an engine evaluation; an imitation prior is a **second opinion about what move to
play**. That is close to the line drawn in `docs/NORTH_STAR_decoding_lc0.md` — the learned layer is a
translator of LC0's thinking, never an independent chess reasoner. It is not forbidden, but it would
need the same structural guarantee Φ has: **LC0 keeps an absolute veto and the prior only re-ranks
moves already declared sound.** Without that it is a bad coach with good taste.

**"Predicted opponent blunder rates" in the UI.** This is the overclaim corrected on 2026-09-03.
Φ's held-out AUC is **0.6908** — it failed its pre-registered F1 gate of 0.70 — and its calibration
holds on the puzzle-derived distribution it was trained on. Gambit lines are outside that
distribution. A per-line blunder-rate percentage would be a confident number about a population the
model has never been evaluated against.

**Unsourced figures.** The claim that engines score aggressive gambits at "-0.30 to -0.50" is
plausible directionally and is stated as fact. If it is going to drive a design decision, it takes
one `analyze()` call per gambit line to check, and we have the engine.
