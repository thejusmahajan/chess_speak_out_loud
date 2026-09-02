# Round table — making Φ cheap to train, and LC0 cheap to run

**Convened by Thejus, 2026-09-02**, to explore how to optimise training so that compute hours are
saved and more data becomes affordable.

> **CONSTRUCTED SIMULATION.** Four voices used as a reasoning device. **Nothing here is a
> quotation.** "DeepMind optimisation lead", "LC0 developer" and "Kaggle training expert" are
> composites standing for those bodies of practice, not individuals. Every *number* attributed to
> this project is real and was measured; every number attributed to hardware nobody here owns is
> marked as unverified.

**Not in scope: the aim.** Learning configurations from the puzzle corpus, training Φ in PyTorch,
and steering with LC0 are settled (`docs/plans/PLAN_CONFIGURATION_STEERING.md`). This is an
engineering conversation about cost.

---

## The state everyone is arguing from — measured, 2026-09-02

| | |
|---|---|
| built dataset | 301,116 rows; `train.npz` 39.66 MB, val 4.96, test 5.07 — **49.7 MB total** |
| storage form | 18 × `uint64` bitboards per position = 144 B/row; **34.6 MB** resident as int64 |
| unpacked | uint8 planes **276.9 MB**; float32 **1.11 GB** |
| vectorised unpack, CPU | **27.45 s** for the 240,360-row train split, one shot |
| puzzles available in the 1500–2200 window | **1,907,960** — the build used a stride of 9 |
| LC0 on Thejus's laptop | BLAS/DNNL, 2 cores — **≈100 nodes/s** (400 nodes → 3.64 s) |
| the corpus that needs LC0 | 9,000 games, **228,020** decision nodes |
| status | ⚠ the dataset is being **rebuilt** — the negatives leaked (audit 2026-09-01) |

---

## I. Where does the time actually go?

**CLAUDE.** Before anyone optimises anything: Φ is a small CNN over an 18×8×8 input, and the whole
training set is 49.7 MB on disk. I want to know whether we have a GPU problem at all.

**DEEPMIND OPT.** You don't. You have a data-movement problem wearing a GPU costume. Three hundred
thousand samples of a hundred and forty-four bytes is nothing. If you write the obvious PyTorch —
a `Dataset` whose `__getitem__` unpacks bitboards in Python, a `DataLoader` with workers, pinned
memory, host-to-device copy per batch — you will spend your entire epoch in Python and the T4 will
idle. Your own measurement says it: 27 seconds to unpack one split *once*. Do that per epoch on the
CPU and the GPU never gets a turn.

**CLAUDE.** So the recommendation is to keep the whole thing resident.

**DEEPMIND OPT.** Push all 301,116 rows to the device as `uint64` — 34.6 MB, which is a rounding
error on a 16 GB card — and never move data again. Index batches with a permuted tensor of row
indices. No `DataLoader`, no workers, no `pin_memory`, no collate. Unpack on the GPU with a shift:

```python
bits = torch.arange(64, device='cuda')
planes = ((bb[idx].unsqueeze(-1) >> bits) & 1).float().view(-1, 18, 8, 8)
```

That is the same arithmetic that took 27 seconds on his two CPU cores, running on thousands of
lanes. You could also unpack once into a resident `uint8` tensor — 277 MB — and cast per batch.
Either way the epoch becomes seconds.

**KAGGLE EXPERT.** Agreed, and it matters more than it sounds, because Kaggle bills you in
wall-clock of a GPU-enabled session, not in GPU utilisation. Every second the T4 spends waiting for
a Python loop is quota you paid for and did not use.

---

## II. Mixed precision, `torch.compile`, and the temptation to do everything

**DEEPMIND OPT.** Then the standard kit. AMP with `bfloat16` or `float16` and a `GradScaler`, large
batches — 8,192 or 16,384 given the data is resident — learning rate scaled to match, `channels_last`,
and `torch.compile` on the model.

**KAGGLE EXPERT.** I want to push back on most of that. On a model this small those are not
speedups, they are noise, and two of them are risks. `torch.compile` costs a compile pass at the
start of every session — and on Kaggle you get a *fresh* session every time, so you pay it every
time and you may pay it twice when the batch shape changes. AMP's tensor cores only pay off once
you are compute-bound, and at 18×8×8 with a few dozen channels you are launch-bound: you will be
issuing thousands of tiny kernels and waiting on the launch queue.

**DEEPMIND OPT.** Which is an argument for the large batch, not against precision.

**KAGGLE EXPERT.** It is, and I concede the large batch. Take that one, it is free. But make the
others earn it: run thirty seconds with and thirty seconds without, print both, and keep whichever
wins. Anything else is cargo cult, and on a free tier the measurement is cheaper than the argument.

**CLAUDE.** That fits the house rule — never adopt a number you have not produced. I will take the
batch size and the resident data as decided, and AMP and `compile` as *hypotheses with a
thirty-second test attached*.

**DEEPMIND OPT.** Fine. But note what the resident-data trick actually buys, because it is not
"faster training". It is **more experiments per hour**. When an epoch is seconds, the whole ladder —
does it learn at all, does it learn at 50k, does it hold at 300k — runs inside one coffee break, and
you find out that your negatives are broken on the first rung instead of the third.

**CLAUDE.** We found that out with a logistic regression and no GPU at all, which rather makes your
point.

---

## III. How much data can we actually afford?

**CLAUDE.** Thejus's question was partly this: does optimising let us train on more? We sampled
200,000 of the 1,907,960 puzzles in his rating window, with a stride of 9.

**DEEPMIND OPT.** Then the cap is arbitrary and you should say so. At 144 bytes a row, the entire
1.9M window is **274 MB** — still resident, still no dataloader, still seconds an epoch. Compute is
not what is limiting your dataset size. Nothing about the GPU cares.

**LC0 DEV.** Nor does anything about the engine, and this is the part I would put in bold. **Φ never
calls LC0.** Its label comes from a human having blundered in a real game, not from an evaluation.
So the dataset can scale to the whole window on a laptop CPU overnight, for free, and the only cost
is board replays in `python-chess`.

**CLAUDE.** That is the honest answer to "can we train with more data": yes, and it was never a
compute question. **The binding constraint is matched negatives.** After the rebuild, every positive
needs a negative sharing material, phase, check status and mobility bucket. The last build matched
75% and that was on the loose key. The tighter key will match less, and *that* number — not the GPU
— decides how large the dataset can be.

**KAGGLE EXPERT.** Then do the scaling on Thejus's own machine and never in a Kaggle session. I see
this constantly: people build datasets inside a GPU notebook because it is where their code lives,
and burn hours of a weekly GPU allowance running `python-chess` on a CPU. **A GPU session doing
CPU work costs exactly as much as one doing GPU work.**

**CLAUDE.** Noted as a rule: dataset construction is local or CPU-only-session. Never GPU.

**DEEPMIND OPT.** One caution against your own enthusiasm, though. More data is worth nothing if it
is more of the same artefact. You just found negatives separable at AUC 0.66 on mobility and check.
Scaling that dataset ten-fold would have produced a ten-times-more-confident useless model. **Pass
A4 first, then scale.**

---

## IV. The real compute hog is not Φ at all

**LC0 DEV.** Can we move to the part that actually costs money? Φ is minutes. Your profile
regeneration is 228,020 decision nodes against an engine, and on that laptop it is fifty-one days.
Every hour you save there is worth a month of arguing about `torch.compile`.

**CLAUDE.** Go on.

**LC0 DEV.** Three things, in descending order of how much they buy.

First, **your budgets are time-limited and they must not be.** `confirm_best_seconds: 6.0` buys 64
nodes on that laptop and would buy thousands on a T4 — same six seconds either way. A wall-clock
budget converts hardware improvement into *depth you did not ask for*. Switch to
`confirm_best_nodes` / `confirm_played_nodes`, which already exist and are `None`, and the GPU's
speed lands in your pocket instead of the search tree.

**CLAUDE.** Already decided doctrine here, §4 of the Bible, and already in the Kaggle brief. Second?

**LC0 DEV.** Second, **the NN cache is per process**. Eight workers means eight caches and eight
copies of every repeated position — and chess positions repeat enormously across a player's games,
because they all start from his opening repertoire. Fewer workers with a large `--nncache` and a
large `--minibatch-size` may well beat more workers with small ones. On a T4 the minibatch is what
fills the card; more processes just fragment it. **Measure both. Do not assume eight is best because
eight is what the bundle currently says.**

**CLAUDE.** That contradicts what our own Kaggle runner defaults to, which is 8. Good. It goes in
the rehearsal as a comparison rather than a setting.

**LC0 DEV.** Third, and here I expect an argument: **most of your searches are wasted on candidates
that were never going to matter.** The steering stage evaluates the top four policy moves at every
node with `multipv=2`. In most positions three of those four are obviously not playable within your
60-centipawn floor, and you paid a full search to learn it.

---

## V. The argument: screening with the raw net

**DEEPMIND OPT.** So screen them. One batched forward pass of the network over all four resulting
positions gives you a value estimate for each at a fraction of the cost of four searches. Discard
the ones that are far outside the floor, and search only the survivors. Classic two-stage cascade.

**LC0 DEV.** And there it is, and I object. A raw value head is not a search result. You would be
filtering on a quantity that disagrees with the one you report, and it will disagree exactly where
positions are sharp — which is the only place this project cares about. Tactics are where the raw
net is *most* wrong; that is what search is for.

**CLAUDE.** I am with the engine developer, and for a house-specific reason. This project has a
failure family called metric-mislabel: `had_tal_move` was a complexity differential with no material
check, and it produced a confident verdict that the London System was sharp. A screen that silently
changes what "playable candidate" means is the same error with better manners.

**DEEPMIND OPT.** Then constrain it so it cannot. The cascade is only unsound if the screen decides
the *answer*. Let it decide only **what gets searched**, and require that every number you keep — the
evaluation, the complexity, the playability — still comes from a real search. Then a wrong screen
costs you a missed candidate, never a wrong figure.

**LC0 DEV.** …That I can live with, with one addition: measure the miss rate before you trust it.
Take a few hundred nodes, run both — screen-then-search, and search-everything — and report how
often the screen discarded a move that the full search would have called playable. If that number is
small you have a real saving. If it is not, you have learned something about the value head.

**CLAUDE.** Accepted, and it is falsifiable, which is what makes it worth doing. **Screen may
prune the search set; screen may never produce a reported number; the miss rate is measured before
adoption, not after.** That last clause is the whole difference between this and the London result.

**KAGGLE EXPERT.** One practical note. `evaluate_batch` on BT3 already exists in this repository,
and the previous session's audit flagged an open lead on it. If you are going to lean on it, check
it first — a screen built on a function with a known open question is how you get a fast wrong
answer.

**CLAUDE.** It is on the record as an open lead in the attention frame-bug work. Verify before use.

---

## VI. Kaggle economics, from someone who has wasted the quota

**KAGGLE EXPERT.** The quota rules matter more than any of the tuning above, so let me be concrete
about what wastes it. **Verify the current numbers on Kaggle's own page before planning around
them** — they have changed more than once — but the shapes are stable:

- A weekly GPU allowance (roughly 30 hours at the time of writing) and a per-session cap (roughly
  12 hours). Both are wall-clock of a GPU-enabled session.
- **Interactive sessions die on idle.** A long run must be a committed batch run — "Save & Run All"
  — not a browser tab you leave open overnight and hope about.
- Output persists as a notebook version; the way to resume is to save the artefacts you need and
  mount that version as an input dataset next time.

**CLAUDE.** Which is exactly the warm-then-assemble scheme in the regeneration brief: warming
sessions fill the EPD cache and throw their profile away, and one final pass runs every game against
a fully warm cache and does no engine work. A cached 25-game run took 32 seconds on the laptop.

**KAGGLE EXPERT.** Then size the cache before you plan on shuttling it. You are talking about
roughly 3.6 GB by the end. Mounting and copying that is not free, and it happens every session.

**DEEPMIND OPT.** And do not spend the first session on Φ. Φ is minutes; you can train it any time.
Spend the GPU on the engine work, which is the thing that cannot be done anywhere else.

**KAGGLE EXPERT.** I disagree, and this is where we do not converge. Spend the first session on Φ
precisely *because* it is minutes — you get an end-to-end proof that the bundle works, the data
loads, the environment is sane, and you spend an hour of quota learning it instead of discovering it
eleven hours into an engine run. Cheap failure first.

**LC0 DEV.** Both of you are describing the rehearsal that is already written. It measures
throughput and runs thirty games. Do that, and stop planning past the first number you do not have.

---

## VII. Where it landed

Points of agreement, in the order they are worth money:

1. **Node budgets, not time budgets.** Otherwise a GPU buys depth nobody asked for. Already decided;
   the rehearsal sets the value.
2. **The whole dataset lives on the GPU.** 34.6 MB as `uint64`, unpacked per batch with a shift. No
   `DataLoader`, no workers, no per-batch host copy. Large batches with the learning rate scaled.
3. **Dataset construction never runs in a GPU session.** It is CPU work and the quota does not care.
4. **Φ's size is not limited by compute.** The full 1.9M-puzzle window is 274 MB. The limit is
   matched-negative availability — and scaling waits until alarm A4 passes.
5. **Screen-then-search is allowed under one rule:** the screen may choose what to search; it may
   never produce a number that gets reported; and its miss rate against full search is measured
   before adoption.
6. **Worker count is a measurement, not a setting.** Eight processes fragment the card and split the
   NN cache; test 2, 4 and 8 against minibatch size before committing.
7. **AMP and `torch.compile` are hypotheses with a thirty-second test attached**, not defaults.

**Unresolved, deliberately:** whether the first Kaggle session goes to Φ or to warming the engine
cache. The optimisation lead wants the scarce resource spent on the thing only it can do; the Kaggle
expert wants the cheap end-to-end failure first. Both are right about something and the rehearsal
settles it either way.

**The one thing nobody in this room could help with:** whether the negatives are honest. That was
found with a logistic regression on four features and no accelerator of any kind. Compute
optimisation makes a wrong dataset wrong faster.
