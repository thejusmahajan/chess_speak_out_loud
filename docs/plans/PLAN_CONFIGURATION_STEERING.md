# PLAN — Configuration steering

**Status:** v1 design, 2026-09-01. **Owner of the aim: Thejus.** Owner of this spec: the leader.
**Source of record for the idea:** `ideas/2026-09-01_steering_to_tal_configurations.md` — his words,
not to be paraphrased in place of quoting.
**Worker report + audit:** `agents/reports/2026-09-01_tal-configuration-steering-contemplation_REPORT.md`
and its `_AUDIT.md`.

This document is the technical spec only. It does not re-open the aim.

---

## 1. The aim

> *"For a player, making that moves once the position is reached is easy, but getting that position
> is what needs carefully study."*
>
> *"we first learn from the configuration of the lichess puzzles. This confuguration are what we aim
> for. If there are pieces and pawn positions that could possibly lead to the starting positions in
> the puzzle we will find moves that will steer our quiet position or position in hand towards it."*
>
> *"Now, LC0 evaluating a position good doesn't mean it is a tactical position."*

Four stages, his order:

| stage | question | this plan |
|---|---|---|
| **A** | which configurations carry attacking potential? | learn Φ from the 5.5M puzzles (§4, §5) |
| **B** | from the quiet position in hand, is such a configuration achievable? | climb Φ under LC0's safety gate (§6) |
| **C** | list 5–7 candidate arrangements | retrieve real puzzle positions, do not synthesise (§7) |
| **D** | which moves get us there without blundering? | `steer_candidates()`, already built (§6) |

**The roll-back / precursor idea is retained but deferred**, at his instruction: *"do not cloud your
thinking with this idea. First the initial idea."*

---

## 2. Two facts measured on 2026-09-01 that shape the design

**Fact 1 — the puzzle `fen` is one ply *before* the tactic.** The losing side is to move in `fen`;
`moves[0]` is their error; the solver moves second. Proof: **0 of 5,527,851 solution lines have odd
length**, which is only possible under that convention. Already implemented correctly in
`backend/training/puzzle_regime.py:96-105`.

So every puzzle row hands us **two** positions for free:

- **`s_err`** = `fen` — the opponent is to move and is about to go wrong.
- **`s_tac`** = `fen` + `moves[0]` — the tactic is now on the board, ours to play.

**Fact 2 — precursor positions are cheap when we want them.**
`data/puzzles/lichess_db_puzzle.csv.zst` (289 MB, on disk) carries `GameUrl`
(`https://lichess.org/787zsVup/black#48`) — game id *and* ply. `build_puzzle_db.py` drops the
column. v2 only.

---

## 3. Decision: the steering target is `s_err`, not `s_tac`

This is the one design decision that matters, and it follows from his own sentence rather than from
any engine argument.

You cannot steer into `s_tac`. `s_tac` exists only because the opponent already played `moves[0]`,
and you do not control that move. What you *can* steer into is **`s_err`: a position where it is the
opponent's turn and a natural-looking continuation loses.**

That is also the honest reading of what a Tal position is. It is not a picture of your own pieces on
good squares. It is a position in which the other person has to solve something, and — this is the
part the corpus gives us and no engine does — **a real human of a known rating actually failed to
solve it.** 5.5M recorded human failures, each with the rating of the player who failed.

| | `s_err` (chosen) | `s_tac` (not the target) |
|---|---|---|
| whose move | opponent's | ours |
| reachable by steering? | **yes** | no — requires their error first |
| what it encodes | a problem posed | a problem already conceded |
| used for | Φ's positive class (§5) | the 5-to-7 display library (§7) |

**Consequence, stated plainly:** Φ learns *what a human at rating R gets wrong*, not *objective
attacking potential*. That is the strongest objection to this whole plan and I am not going to bury
it in a caveat. For a coaching tool aimed at his 1500–2200 opponents it is the correct target and
arguably better than objectivity; for any claim about chess truth it is not. Say it that way in
public, always.

This also satisfies his constraint directly: nothing here consults LC0's evaluation to decide
whether a position is tactical. **The label comes from a human having lost the thread, not from a
number the engine likes.**

---

## 4. What Φ is

A small convolutional network, written in PyTorch by Thejus, trained on Kaggle or Colab.

**Input:** 18 planes × 8 × 8, **always from the side-to-move's point of view** (board flipped and
colour-swapped when black is to move, so the network never has to learn the mirror twice — the
frame bug in `docs/writeup_attention_frame_bug.md` was exactly this class of error).

```
 0-5   our  P N B R Q K
 6-11  their P N B R Q K
 12-15 castling rights (us K, us Q, them K, them Q)
 16    en-passant target square
 17    constant 1  (padding / bias plane)
```

Stored as **18 uint64 bitboards per position** (144 bytes), unpacked to float planes in the
`Dataset.__getitem__`. 400k samples = ~58 MB, which uploads to Kaggle without ceremony. Writing the
unpack is a good first PyTorch exercise and belongs to him, not to the worker.

**Output, two heads:**

1. **Φ ∈ [0,1]** — "is this a position of the shape where the side to move goes wrong". One logit, BCE.
2. **motif affinity ∈ [0,1]^20** — multi-label over the 20 most frequent `themes` strings, BCE. This
   is what lets stage C say *which* storm, not just *a* storm.

No value head, no engine evaluation anywhere in the loss. Φ is a **potential function**, not a
second opinion about who is winning.

---

## 5. The dataset — and the trap that decides whether any of this is real

**Positives.** `s_err` from `puzzles`, filtered `rating BETWEEN 1500 AND 2200` (his opponents' band;
see the Puzzle Storm regime note). Target **200,000**.

**Negatives — the crux.** Both the worker report and the deleted round table flagged the negative
set as the thing that quietly kills projects like this, and they were right. Two pools:

- **N1 "spent tactic"** — the position after the *full* solution line of a puzzle. The pieces are the
  same players' pieces, the game is the same game, and the tactic is over. This negative exists
  precisely to teach his constraint: a position the engine now scores +5 is **not** a tactical
  position.
- **N2 "real quiet play"** — positions from `games_of_derdiedasdie/lichess_derdiedasdie_2026-07-21.pgn`
  (19 MB of his own games), sampled every 6th ply, excluding the last 10 plies of each game.

**Matching, which is not optional.** Every sample carries

```
material_key = "<our P N B R Q><their p n b r q>"     e.g. "5-1-2-2-1|6-2-1-2-1"
phase_bucket = (count of non-king pieces) // 4
```

Negatives are bucketed by `(material_key, phase_bucket)` and each positive draws a negative from its
own bucket. Positives with no match are **dropped, not back-filled**. If the match rate falls below
60%, the key is widened by dropping pawn counts — and the report says so.

**Three alarms that must be reported before anyone trains anything.** These exist because the
cheapest way to pass a gate is to not do the work, and I am the one specifying the gate:

| alarm | threshold | what it means if it fires |
|---|---|---|
| side-to-move balance per class | must be 50 ± 2% | the net can read the class off whose turn it is |
| top-10 `material_key` distributions, positive vs negative | must overlap | matching failed; the net will learn material |
| **material-only logistic regression AUC** (10 features: the piece counts, nothing else) | **must be < 0.65** | the dataset is trivially separable. **Stop.** A CNN trained on this would score well and mean nothing. |
| **A4 — cheap-tactical-features AUC** (the 10 counts **plus** `in_check`, `n_legal_moves`, `capture_available`, `n_checks_available`) | **must be < 0.60** | the same failure through a different door. **Stop.** |

**⛑ A4 exists because the first build passed A1–A3 and was still unusable** (2026-09-02 audit).
The N1 "spent tactic" negative is the position *after* the full solution line, and puzzle solutions
disproportionately end in check or mate — so N1 was systematically low-mobility and in check:
positives 11.2% in check / 28.3 legal moves, negatives **36.7% / 19.4**. `n_legal` alone gave
AUC 0.6621; the three together 0.6637. Three alarms that all interrogated material could not see it.

**Consequences, now part of the spec:** N1 candidates are dropped when the side to move is in check
or the puzzle's themes contain `mate`; the matching key is
`(material_key, phase_bucket, in_check, mobility_bucket)`; N2 is sampled every 3rd ply to make up
the volume; and every row stores its `source` so F1 can be run against N1 and N2 separately.

**The general lesson, and it is mine:** I asked *"what is the cheapest way to pass this gate without
doing the work?"* about material, and stopped there. Ask it about **every** axis the label could
correlate with, not the one that came to mind first.

The third one is the whole audit in a single number. It costs seconds and it is not fakeable.

---

## 6. Stage B and D — steering, with LC0 holding the veto

Already built and already correct: `metrics.steer_candidates()` (`backend/training/metrics.py:474`)
takes evaluated candidate moves and keeps only those costing ≤ `steer_max_loss_cp` (60) against best
and never landing below `steer_min_eval_cp` (−60). **LC0 keeps an absolute veto over blunders; Φ
never overrides it, it only re-ranks what LC0 has already declared safe.**

v1 is one field: `steer_candidates` currently ranks the playable set by `complexity`. Rank instead by

```
score(move) = Φ(position after move)
```

**⛑ Corrected 2026-09-02.** This originally read `Φ(after) − Φ(before)`, which is a
frame error. Φ is defined on the *side to move*, so `Φ(before)` scores **my own**
error-proneness while `Φ(after)` scores the **opponent's** — different questions. For ranking
candidates the subtraction is harmless (`Φ(before)` is constant across them) but it must not be
written down, because it invites cross-ply differences that are meaningless. **Any Φ difference
must be between positions with the same side to move.** Gate F3's four-ply comparison preserves
parity and is fine; a three- or five-ply one would not be.

That is a **potential-based** re-ranking, which is the one form of steering with a proof attached
(Ng, Harada & Russell, ICML 1999): shaping by a potential difference cannot change which policy is
optimal, only which one is found first. Deeper integration — biasing the PUCT prior inside search —
is v2 and needs no decision now.

---

## 7. Stage C — the five-to-seven list

**Retrieve, do not synthesise.** From the reachable positions found in §6, take the penultimate
hidden layer of Φ as an embedding, and find nearest neighbours among **real `s_tac` positions in the
puzzle DB** with a compatible `material_key`.

The user is then shown, for each of 5–7 candidates: the actual board, the theme, the rating, and the
move that actually won — a position a real player really reached. Nothing is invented, so nothing
can be hallucinated. This is what makes it coaching instead of a score, and it is the requirement he
has held since the beginning: **the student must be able to picture the target.**

---

## 8. Falsification, stated before the work

| # | test | falsified if | cost |
|---|---|---|---|
| **F0** | material-only logistic baseline on the built dataset | AUC ≥ 0.65 → the dataset is broken; fix before training | seconds, CPU |
| **F1** | Φ held-out AUC vs matched negatives | ≤ 0.70 → configurations are not learnable at this representation | ~30 min, free Kaggle T4 |
| **F2** | Φ AUC minus material-only AUC | < 0.03 → Φ learned material, not configuration | free |
| **F3** | on ≥ 200 quiet positions from his own games: does the Φ-max playable move raise Φ four plies later more than the objective-best move does? | no measurable edge → steering adds nothing over just playing well | LC0, local, hours |

**F0 runs before the first epoch. F3 is the one that decides whether the product exists**, and it
cannot run until F1 passes.

---

## 8b. Batching — and why none of this needs paid compute

**The dataset is already a batch, by construction.** §5 samples **200,000** positives from the
5,527,851 with a stride across the whole table — it never touches the full corpus. At 18 uint64 per
position, 400,000 samples is **57.6 MB**. The build is CPU-only and runs in minutes.

**Train in a ladder, not in one shot.** The built dataset is subsettable for free, so:

| batch | size | question it answers |
|---|---|---|
| **B0** | the whole built set, no training | **F0 / alarm A3** — is the dataset trivially separable? Seconds, CPU. |
| **B1** | 50k pos + 50k neg | does Φ learn anything at all? Minutes on a T4. |
| **B2** | the full 200k + 200k | does it hold up at scale, and what is the held-out AUC (**F1**)? |

Each stage can kill the next, and B0 costs nothing. Do not build a smaller dataset to do this —
build the 200k once and subset it.

**Compute: Kaggle's free tier is sufficient, and Colab units should not be spent here.** The model
is a small CNN over an 18×8×8 input on ~58 MB of data — an epoch is minutes on a free T4, not
hours (estimate; the first run replaces it with a real number). Kaggle gives ~30 GPU-hours a week
at no cost.

**The only thing in this project that could justify paid compute is LC0 search** for the profile
regeneration — not Φ. And if Kaggle's weekly quota turns out to be too small for that, the correct
response is to cut the game count or the node budget, **not** to spend borrowed money. Colab Pro
units stay in reserve for one specific case: a contiguous run that genuinely cannot be split across
12-hour sessions. The batching scheme in
`agents/briefs/2026-09-01_kaggle-gpu-profile-regeneration.md` §7 exists so that case does not arise.

---

## 9. Who does what

| | |
|---|---|
| **Gemini** | builds the dataset, the encoder and the loader, and reports the three alarms of §5. Bulk, mechanical, verifiable. Brief: `agents/briefs/2026-09-01_configuration-dataset-build.md`. |
| **Thejus** | writes the PyTorch model and the training loop on Kaggle. This is his stated goal — *"this will also be a great learning experience"* — and it is a requirement of the plan, not a nice-to-have. |
| **Leader** | this spec, the audit of the dataset before it is trusted, and F0 re-run independently. |

---

## 10. Not decided, and not to be decided by guessing

1. The rating window 1500–2200 is a first cut from his own band. Widen or narrow after F1.
2. The 20-theme vocabulary for the motif head — pick by frequency at build time, then freeze.
3. Whether N1 or N2 is the stronger negative. The build reports both separately so F1 can be run
   against each.
4. v2 only: precursor positions via `GameUrl`; PUCT prior biasing inside search.
