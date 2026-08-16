# Session log — 14–16 August 2026

What was built, what was found, what was published, and what is still open. Written
so none of it has to be reconstructed from memory or from git archaeology.

---

## 1. Puzzle training

**Goal:** close the gap between a 2350 untimed puzzle rating and repeated failures
in the 1500–2000 band under Storm/Racer time pressure. That gap is *retrieval
speed*, not calculation, so everything is drilled against a clock and the log
records **time-to-answer**, not just correctness.

### What exists

| Component | Location |
|---|---|
| Deck curator + timed terminal drill + SRS + reporting | `backend/training/puzzle_regime.py` |
| Puzzle Streak sets, sessions, move validation | `backend/training/puzzle_sets.py` |
| Streak UI (chessground via existing `TrainingBoard`) | `frontend/src/components/Training/PuzzleStreak.tsx` |
| Full-database importer | `backend/training/build_puzzle_db.py` |
| The regime itself | `docs/PUZZLE_STORM_REGIME.md` |

### The measured finding the regime is built on

Across all **1,361,207** puzzles rated 1500–2000 with popularity ≥ 80:
**27.3%** open with a move that is neither check nor capture — invisible to anyone
scanning forcing moves first, which is what everyone does on a clock.

The themes usually lumped together as "hard" split into two unrelated failure modes:

- **Quiet blindness** — `trappedPiece` 83.2%, `quietMove` 75.1%, `zugzwang` 64.9%.
  Trivial to verify once seen; you never look at them.
- **Forcing but indirect** — `attraction` 3.1%, `intermezzo` 8.2%, `deflection` 9.0%.
  Easy to *find*; the cost is **verifying** them two or three ply out on a clock.

They get different blocks and different clocks. 27 decks, 960 puzzles.

### Database

The old importer carried `if count >= 300000: break` — a development cap never
removed. The local pool was 300k of the export's 6.06M.

| | before | after |
|---|---|---|
| total puzzles | 300,000 | **5,527,851** |
| in the 1500–2000 band | 80,104 | **1,472,045** |

Sessions now draw **fresh from the pool** each time: two sessions of the same set
share **0 of 30** puzzles while remaining strictly ascending in rating. Variety comes
from *which* puzzles appear, never from disturbing the difficulty ramp.

### Bugs found and fixed

1. **Board flipped on solve.** `orientation` came from the live board's turn, so the
   final solver move handed the turn over and flipped the board at the instant a
   puzzle was solved. It only fired on the solved payload, which reads as an
   animation. Orientation is a property of the puzzle, not the board.
2. **Sampling did not scale.** `_sample` materialised every matching row to take 30 —
   151s and 1.06 GB per deck at 5.5M rows. Now selects ids, shuffles those, fetches
   only the chosen rows, and joins `puzzle_flags` only when the query uses it.
   **151s/1056 MB → 59s/228 MB**, with seeded results unchanged.
3. **`puzzle_flags` lost in the rebuild.** `_sample` LEFT JOINs it on every query, so
   a rebuild without it broke deck building outright. The builder creates it now.

---

## 2. Interpretability — two bugs, one public correction

### The reference-frame bug

BT3 encodes the board **from the side to move's perspective**. The extraction code
mapped internal index 0 to a1 unconditionally, so every black-to-move attention map
was **reflected through the horizontal axis**.

Mean per-square residual between the buggy map and the rank-flipped corrected map:
**0.0003** over 40 positions (median 0.0002, max 0.0007). The two are the same map,
reflected. That number is the bug's signature.

It survived because nothing about the broken output looked broken: smooth plausible
heatmaps, no exception, no NaN, and correct for exactly half of all positions.

### The history-planes bug — larger, and found while writing up the first

BT3's input is **112 planes**, ~84 of them the previous eight positions. Every tensor
was built from a bare FEN, leaving those empty — input the network never sees in play.

- `evaluate_batch` returned `value ≈ -1.000`, `wdl ≈ [0,0,1]` on **20/20** midgame
  positions while the LC0 binary on the *same weights* gave sharp priors.
- The start position looked fine only because its true history really is empty. That
  coincidence hid the bug.
- Attention maps moved by **0.11–0.20** per square with real history — two orders of
  magnitude above the frame bug's signature — and **invalidated already-published
  figures**.

**The trap inside the fix:** `chess.Board.mirror()` returns a board with an *empty
move stack*, so mirroring a black-to-move position throws the history away a second
time. The mirrored frame must be rebuilt by replaying mirrored moves (`square ^ 56`).

Validated against the engine as ground truth: **top-1 policy agreement 1/6 → 5/6**,
and the published example position now reads `+0.993` where the broken path said
`-1.000`.

A third bug surfaced from the fix: `_same_position` compared `ep_square` directly,
but `Board.fen()` only emits an en-passant square when the capture is *legal*, so
roughly 1 in 3 valid replays were rejected. Compared via `has_legal_en_passant()` now.

### Corrected figures

For the published position (a real game, Black to move, move 19):

| corrected (absolute frame) | | buggy (side-to-move frame) | |
|---|---|---|---|
| h5 1.000 | Black queen | h4 1.000 | White bishop |
| b8 0.864 | Black king | b1 0.865 | *empty* |
| d8 0.859 | Black rook | d1 0.859 | *empty* |
| f3 0.765 | White knight — **pinned** | f6 0.766 | *empty* |
| d5 0.748 | Black knight | d4 0.749 | *empty* |
| e2 0.670 | White bishop | e7 0.670 | *empty* |
| **6/6 occupied** | | **1/6 occupied** | |

### Published

- **https://thejusmahajan.github.io/blog-lc0-attention-frame.html** — includes a
  section on the second bug and a public correction of the first version's figures.
- Sources: `docs/writeup_attention_frame_bug.md`, `docs/artifact_attention_frame_bug.html`,
  figures and raw tensors in `docs/figures/`.

### Policy-prior harvest (data collected, post not yet written)

150 positions from his own games, BT3 weights, priors at `nodes=1` vs 20k-node search.
Clean subset N=144 after dropping records where the mate mapping was incoherent.

- Search **overturns the prior only 14.6%** of the time; the searched-best move is the
  prior's #1 in 123/144 and top-2 in 139/144.
- **The network knows when it will be corrected:** prior mass on the eventual best move
  is **0.206 when overturned vs 0.435 when confirmed**.
- Blunder split: his move matches the prior's top-1 **32.0%** of the time on blunders
  (≥100cp) vs **66.0%** on non-blunders. The original hypothesis — that human and
  network intuition share failure modes — is **refuted as a majority effect**, though
  ~1 in 3 blunders were the network's first instinct too.

Caveat found while auditing: two 20k-node searches of the same position disagree by
245–390cp in sharp positions (2–16cp in quiet ones). The 100cp threshold is safe where
it is applied; anything resting on eval differences in decided positions is not.

---

## 3. Career materials

| Artefact | Where |
|---|---|
| ML/interpretability CV (2 pages) | `job_search/applications/ml_interpretability_general/cv_ml_interpretability.tex` |
| Cover letter (1 page, placeholders) | same directory, `cover_letter_ml.tex` |
| CV bullets, cover-letter paragraph, interview defence, do-NOT-claim list | `docs/CV_AI_MODULE.md` |
| Published CV | https://thejusmahajan.github.io/assets/Thejus_Mahajan_CV_ML.pdf |

Website: new post added, interpretability project added to `projects.html`, homepage
tagline now leads with **Machine Learning**, and a live broken link fixed —
`simulacrum-analysis.html` shipped with an unfilled `[GITHUB-URL-PLACEHOLDER]` on a
prominent "View full code on GitHub" button.

**CV corrections worth remembering:** German practice is **1–2 pages**, tabular,
understated — a metrics dump reads as overselling. First draft was three pages dense
with figures and had to be rewritten. Also fixed: "Jülich Supercomputing *Center*" →
**Centre** (the institute's own English name), a stale date reading 18 April 2026, and
a LaTeX escape that compiled as display math. The template's header breaks if the
tagline wraps past ~80 characters.

### Market assessment (16 Aug 2026)

Favourable: ~2,300–2,565 ML roles open in Germany; PyTorch postings +239%, NLP +337%;
109,000 unfilled IT positions; skills-based hiring rising.
Unfavourable: 2026 recruitment pullback, hiring confidence lowest since COVID, and
**only ~14% of German firms hire internationally** — the single biggest filter.

**Age is not the problem.** At 33 with a PhD and postdoc he is at the normal age for
entering industry; German age effects bite at 45–50. The real liabilities are visa
friction, B1 German, and no industrial ML employment history.

**Research institutes are the target** precisely because they are visa-competent by
default. Boards, not search results — individual postings found via search are
routinely already closed (two of two checked returned `410 Gone` / "not published").

---

## 3b. Hereon AEON-UP — the live application

Postdoctoral Researcher, *Probabilistic Deep Learning for Urban Air Quality*,
Helmholtz-Zentrum Hereon, Geesthacht. **Ref. 1056, deadline 3 September 2026**,
start 1 Oct 2026, two years, TVöD E13. PIs **Dr. Martin Ramacher** and
**Dr. Matthias Karl**.

Best fit found in the search: the required-PhD list names Physics *and*
Environmental Sciences; the project couples physics-based chemistry transport
models (their group runs CMAQ over the North Sea) with probabilistic deep
learning. The gap is Bayesian methods and neural processes.

Materials in `job_search/applications/hereon_aeon_up/` — a one-page cover letter
rebuilt around **uncertainty** (a confidently wrong model is more dangerous than
a visibly uncertain one, evidenced by the two silent pipeline errors), the CV,
and `STUDY_BOOK.md` covering neural processes, the aleatoric/epistemic
distinction, CRPS and calibration, and enough urban air quality to hold a
conversation.

Still open: the letter's salutation, a sentence on ultrafine particles now that
Karl's involvement is known, and implementing a conditional neural process on
synthetic data — the single highest-value piece of preparation.

## 4. Open items

1. **Apply.** Materials are done; the binding constraint is volume. 3 submissions in
   7 months converts to ~0 offers.
2. Helmholtz Job Letter subscription + HIDA board as a daily habit.
3. Warm leads: **Hereon** (guest scientist 05–10/2025), Universität Hamburg postdoc
   group, DESY. One email each; they route around the 14% filter.
4. **Bildungsgutschein email to the BA** — open since April; the HLRS course now gives
   it a concrete subject.
5. Rotate the two exposed GitHub PATs and the Gemini API key.
6. Policy-prior blog post — data harvested and audited, mostly writing now.
7. The causal experiment: ablate the heads carrying king-square attention and measure
   whether the evaluation moves. That is the step from "reads attention" to "tested
   whether attention is load-bearing".
8. German CV not updated with the ML framing — needs a native pass, not a machine
   translation.
