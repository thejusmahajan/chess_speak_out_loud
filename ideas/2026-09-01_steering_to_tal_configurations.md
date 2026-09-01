# Steering toward Tal-like configurations — the idea, and round table 1

**Origin:** Thejus, 2026-09-01, unprompted.
**Status:** idea recorded, round table 1 held. Next: brief to Gemini → round table 2 → plan.
**Do not implement from this document.** It ends in open questions, deliberately.

---

## 1. The idea, verbatim

Recorded exactly as given, as the source of record. Everything after this section is
interpretation and can be argued with; this section cannot be edited.

> But this doesn't fulfils the purpose that we are aiming at. Definitions one side, aim on the
> other side. From a position, that have a potential for getting steered towards Tal like
> position is the key here. For this placing the pieces on attacking squares is important. For
> this, concieving where the pieces could be placed is important. So we imagine, given our stock
> of pieces, a variety of arrangements of pieces and pawns so that this would give us possibly a
> checkmate or gain in material. We could first figure out which combinations of piece placement
> gives us this attacking potential. This can be figured out by utilizing the piece positions
> from the tactical exercises that we have. The patterns in these exercises, or the piece
> placements in these positions are the one we will aim for, taking also into account of the
> positions of opponents pieces and the king. Then we will list five or seven possible piece
> placements that we can cocieve and we will figure out which moves will help us get this done.
> To find the piece placements and their importance, we could train on the tactical exercises and
> the corresponding engine evaluation. Then we use the trained neural network to identify if it
> is possible for the position in our hand, usually quiet to acieve such patterns. Then we will
> use LC0 to find moves that could let us achieve this, without making a blunder or getting into
> very low evaluation. We can use kaggle or google colab to train our model. We could create it
> using pytorch and this will also be a great learning experience.

---

## 2. What this proposes, stated precisely

The current `steer_candidates` asks a **local, one-ply, evaluation** question: *of the moves I can
play here without losing more than N centipawns, which is the sharpest?* Thejus's objection is
that this is a definition, not an aim. It can only find sharpness that is **already present at
this node**. It cannot answer *"is this quiet position one from which a Tal position can be
built, and how do I get there?"*

His proposal replaces the local question with a three-stage one:

| stage | question | proposed mechanism |
|---|---|---|
| **A. Learn** | which *arrangements* of pieces carry attacking potential? | train on tactical exercises + engine evaluation |
| **B. Detect & propose** | from this quiet position, which 5–7 arrangements are achievable? | the trained net, over our material and the opponent's king/pieces |
| **C. Path-find** | which moves get us there without blundering? | LC0, constrained not to drop the evaluation |

The unit of reasoning changes from **move** to **configuration**. That is the substantive idea,
and it is a good one.

---

## 3. What we already hold — measured today, not recalled

Any plan must start from this inventory, because three of the four pieces already exist.

| asset | state |
|---|---|
| **Lichess puzzle DB** | `data/puzzles/puzzles.sqlite`, **5,527,851 puzzles**, columns `fen, moves, rating, themes, opening_tags`. **The `moves` column is the solution line, so precursor positions are free — roll back k plies.** |
| **Puzzle flags** | `puzzle_flags`, 1,472,045 rows, incl. `quiet_first` — puzzles whose solution opens with a quiet move |
| **Relational extractor** | `backend/training/relational_facts.py` — pins, x-rays, conditional pins, defender-removal, king pressure, outposts, tied defenders. **This is the machinery that can NAME a configuration.** |
| **BT3 interpretability** | forward hooks capturing `[15, N, 24, 64, 64]` attention; policy prior extraction |
| **Steering core** | `metrics.steer_candidates`, `tactical_complexity`; 29 tests green |
| **⚠ Cautionary precedent** | the old `had_tal_move` was **complexity-only with no material check**, and produced the unfounded claim "London is sharp". The live sacrifice drill currently returns **0** because the profile still carries that dead key. |

---

## 4. Round table 1 — CONSTRUCTED SIMULATION

> **Not a record.** Four constructed voices used as a reasoning device. **Mikhail Tal died in
> 1992**; nothing here is a quotation or a claim about what he thought. The DeepMind and AlphaZero
> voices are composites representing those bodies of published work, not individuals.

---

**CLAUDE:** The proposal is to change the unit of reasoning from the move to the configuration.
Learn which arrangements carry attacking potential from the puzzle corpus, detect achievable ones
from a quiet position, then let LC0 find the path. I want to test it before we cost it.

**DEEPMIND DEV:** Then start where I always start. What is your label? You said "train on the
tactical exercises and the corresponding engine evaluation". A puzzle is a position in which a
tactic **already exists**. If you train on that, you get a detector for *"there is a combination
here right now"*. That is not what you asked for. You asked for *"a combination can be
manufactured from here in a few moves"*. Those are different functions and the second one is the
whole product.

**CLAUDE:** The corpus gives us the second one almost for free. Every puzzle row carries its
solution line. Roll the position back three or five plies and you have a position that is quiet,
that a human would not flag, and from which a combination demonstrably arrives. That is a
precursor, and there are five and a half million of them.

**DEEPMIND DEV:** Better. Now the harder half, which is the half people get wrong: what is your
**negative** set? If your negatives are random quiet positions from anywhere, your network will
learn what a Lichess puzzle *looks like* — material imbalance, unusual piece density, a king
already exposed — and you will get 95% accuracy and a useless model. The negatives have to be
positions matched to the positives on everything except the outcome. Same game, same phase,
similar material, similar evaluation — and no combination within k plies.

**AZ EXPERT:** Before you build any of this, I want to say the uncomfortable thing. LC0's value
head already integrates attacking potential. That is what it *is* — a learned estimate of the
outcome given optimal continuation, which absorbs "my pieces are aimed at his king" as a matter of
course. And the policy head already prefers moves that lead to good positions. You are proposing
to train a second network to tell you something the first one has already encoded.

**CLAUDE:** That is the north-star constraint, and it is binding for us: **the LLM and any learned
layer are translators of LC0's thinking, never a parallel chess reasoner.** A bad coach does more
harm than no coach.

**AZ EXPERT:** Then the honest version of the idea is not a new network. It is a **different
objective inside search**. AlphaZero-style engines are steerable in two well-understood places:
you can bias the prior at the root, or you can modify what the backup maximises. If you want Tal
positions, you do not need to learn what one looks like from scratch — you need a value that
rewards *complications the opponent must solve* while constraining the objective evaluation not to
fall. That is search-time steering and it is far cheaper than a training run.

**TAL:** May I say something about the premise? You are all talking about attacking potential as
if it were a property of an arrangement. It is not. It is a property of an arrangement **and the
person on the other side of the board, and the clock.** I did not aim at pictures. I aimed at
positions in which my opponent had to find four only-moves in twenty minutes, and I was very
happy to be objectively worse while he did it.

**CLAUDE:** That is the objection I most want on the record, because our metric already failed
this way once. Our first "sharpness" measure was complexity with no material check, and it told us
the London System was sharp. It was measuring the wrong thing confidently.

**TAL:** Then hear the rest of it. A configuration can be perfectly sound and completely harmless,
because it poses no question. And a configuration can be objectively dubious and win the game,
because the refutation is six moves deep and unpleasant to find. If your network learns which
arrangements are *evaluated well by an engine*, you will teach the student to build tidy positions
that a machine likes and a human refutes at leisure. You will have taught him to lose slowly.

**DEEPMIND DEV:** That is a label-design problem and it is solvable. The label should not be the
engine's evaluation of the arrangement. It should be something closer to *how hard the position is
to hold* — the gap between the best move and the second best, how many replies survive, how
sharply the evaluation moves if the defender errs. You already compute most of that in
`tactical_complexity`.

**AZ EXPERT:** And note what Tal has actually just told you: your target function is **defender
difficulty**, not attacker beauty. Those correlate but they are not the same, and the difference
is exactly where the London result came from.

**CLAUDE:** There is a cheaper experiment available before any of this, and it is the one most
faithful to what we are for. The learned-look-ahead work on this exact network reports that BT3's
**middle layers already carry internal representations of the board three to seven plies ahead**,
recoverable by a linear probe at high accuracy. We have the hooks. If "a combination is coming" is
linearly readable from activations we already capture, then the detector is not a training run at
all — it is a probe.

**DEEPMIND DEV:** Do that first. It is a week of work, it costs no GPU, and it is **falsifiable**.
Take precursor positions from the corpus, take matched negatives, capture activations, fit a linear
probe, and measure. If the probe reads it, you have decoded the engine, which is the thing you say
you exist to do. If the probe fails, you have learned that the signal is not linearly available,
and only then is a trained network justified — with a real reason for existing.

**TAL:** And when your probe says "yes, something is here" — what do you tell the student? That is
not coaching. A probe gives you a number. I need to be able to say: *the knight belongs on f5, the
queen comes to h5, and the h-file must be opened.* Your idea about listing five or seven
arrangements is the right instinct, and none of what these two have proposed produces it.

**CLAUDE:** Agreed, and that is the part of Thejus's proposal that survives the argument intact.
But I would change **generation** to **retrieval**. Conceiving arrangements freely is an enormous
search space and it is where this would fail. We have five and a half million solved tactics. Mine
them once into a library of attacking configurations expressed in relational terms — attacker on
the long diagonal, defender tied to f7, king with two flight squares — using the extractor we
already built. Then from a quiet position you are not imagining anything. You are asking which
stored patterns are **near** this position given the material, and ranking them by how far away
they are.

**AZ EXPERT:** That is a nearest-neighbour problem instead of a generative one, which is a very
large simplification. And the distance metric is doing real work: "how far is this position from
that pattern" is measured in moves, so LC0 answers it. Your stage C stops being a separate
component.

**TAL:** Then you have three honest pieces. Something that says a storm is possible. Something
that names the shape of the storm. And the engine that finds the road. I would only insist on the
last thing: whatever you build, the student must be shown the **continuation** — where the pieces
end up and what the opponent is suffering. A target he cannot picture is not a target.

**CLAUDE:** That is already decided doctrine here and it is built — the sacrifice playout exists
for exactly that reason.

**DEEPMIND DEV:** Then the plan is staged and each stage kills the next if it fails. Probe first,
because it is cheap and falsifiable. Mine the pattern library second, because it is useful even if
the probe fails. Train a network only if the probe cannot read the signal — and by then you will
know what the label should be, which you do not know today.

---

## 5. Where it landed

**The idea survives, with two changes and one reordering.**

1. **Generation → retrieval.** Do not conceive arrangements freely. Mine a **library of attacking
   configurations** from the 5.5M puzzles, expressed in the relational vocabulary the extractor
   already speaks, then retrieve and rank by distance from the position in hand. This is the
   single biggest simplification available and it preserves the part of the idea that matters —
   naming a concrete target.
2. **Label = defender difficulty, not engine approval.** Tal's objection is the same failure that
   produced "London is sharp". The target function is how hard the position is to *hold* — best
   vs second-best gap, number of surviving replies, penalty for a defensive error.
3. **Probe before train.** Test whether BT3's own middle layers already carry "a combination is
   reachable". It is cheap, falsifiable, needs no GPU, and it is the north star in its purest
   form. A trained network is justified only if the probe fails, and the probe teaches us the
   label either way.

**Precursor positions are free**: every puzzle row carries its solution line, so rolling back
k plies yields a quiet position from which a combination demonstrably arrives.

**The negative set is the crux.** Matched on phase, material and evaluation; differing only in
whether a combination arrives within k plies. If this is done lazily the whole thing produces a
confident, useless model, and we will not find out until a human looks at its output.

---

## 6. Open questions — to go to Gemini as round table 2

1. **k.** How many plies back is a "precursor"? Three? Five? Variable by theme? Is there a
   principled way to choose it, or is it an experiment?
2. **The negative set.** What is the best matched-negative construction available from this
   corpus alone? Is `puzzle_flags.quiet_first` usable as a harder negative class?
3. **Defender difficulty.** Give a concrete, computable definition. What does it need beyond
   multipv gap and surviving-reply count?
4. **Probe design.** What exactly do we probe — which layers, which pooling over the 64 tokens,
   linear or shallow MLP — and what accuracy would count as success versus refutation?
5. **Pattern vocabulary.** Is the existing relational-facts vocabulary sufficient to express an
   attacking configuration, or does it need geometric primitives it currently lacks?
6. **Distance.** How do you measure "how far is this position from that pattern" in a way that is
   cheap enough to rank a library against a live position?
7. **The falsification test.** State, in advance, what result would tell us this whole direction
   does not work. If we cannot answer this one, we should not start.

**Question 7 is the one to answer first.**
