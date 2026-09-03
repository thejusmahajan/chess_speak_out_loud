```
Brief-ID:      2026-09-03_mean-pooled-cnp-comparison
Written:       2026-09-03
Target repo:   chess_speak_out_loud
Route:         Antigravity (full workspace)
Type:          teaching artifact -- a comparison, not a model
Blast-radius:  one new script, one new figure, a docstring/title correction to an existing script
Reversibility: trivial
Failure-mode:  SILENT -- a model labelled CNP that is not one produces a confident, wrong answer in
               a job interview, which is the worst place to find out
```

**Environment:** conda `cszero`. CPU only, no engine, no network, under two minutes per run.

---

## 1. INTENT

*(Intent outranks instructions. If any instruction below conflicts with this paragraph, the intent
wins — stop and report. Doing so is a success, never a boundary violation.)*

**Thejus is doing this to understand how Neural Processes work.** That is the requirement, not a
side benefit. The deliverable is therefore **a comparison he can read off one figure**, not another
model.

`scripts/chess_trajectory_cnp.py` already exists, runs, and its uncertainty genuinely pinches
(measured: σ 0.0689 at context vs 0.1472 in gaps, **2.14×**). **Do not change its behaviour.**

But **it is not a Conditional Neural Process**, and its title and docstring say it is. Its own code
says what it really is:

```
line 7   "Kernel Cross-Attention Aggregator: Attends over context moves using an RBF kernel."
line 115 "The uncertainty sigma^2(x_t) is conditioned directly on the kernel proximity to ..."
```

It aggregates **per target query**. A CNP does not. Hence its training log prints `Prior sigma` and
`Noise sigma`, which are Gaussian-process hyperparameters with no place in a CNP.

**Build the real one beside it, so the difference is visible.**

---

## 2. Why the difference is the whole lesson

A **CNP** (Garnelo et al., 2018) collapses the entire context set into **one** vector:

```
r_c = encoder(x_c, y_c)        for each context point
r   = mean(r_c)                <-- ONE vector for the whole game
mu, sigma = decoder(r, x_t)    <-- the decoder sees r and x_t. Nothing else.
```

The decoder **can never look back at an individual context point.** That is what makes it O(N), and
it is what makes it *oversmooth*: a sharp blunder at ply 15 is averaged into the same vector as
everything else, so the model cannot tighten around that one observation.

The existing script instead computes, for every target ply, an RBF-weighted attention back over the
individual context points. That is the *fix* the field invented later — the Attentive Neural Process
— arrived at without first showing the problem it fixes.

**So the figure this brief asks for is the argument for why ANPs exist**, drawn from Thejus's own
data rather than quoted from a paper.

---

## 3. WHAT YOU MAY TOUCH

```
scripts/chess_trajectory_cnp_comparison.py                (new -- the deliverable)
scratch/cnp_comparison_demo.png                           (new -- the figure)
scripts/chess_trajectory_cnp.py                           (docstring/title ONLY -- see Step 6)
agents/reports/2026-09-03_mean-pooled-cnp-comparison_REPORT.md
```

**Do not change the behaviour, architecture, hyper-parameters or output numbers of the existing
script.** Its only permitted edit is the honesty fix in Step 6. Do not touch `backend/`, `phi_net/`,
`data/`, or anything under `docs/plans/`. Do not commit.

---

## 4. STEPS

### Step 1 — settle one open question first

In the current figure the predicted mean does not appear to pass through several context points —
at ply ~36 the context value is ≈ +0.34 and the plotted mean is ≈ −0.05. With σ ≈ 0.069 there, that
is a ~5σ miss, which the NLL should never have tolerated. **Either the plotted mean and the context
set disagree, or it is a rendering artefact.**

Add, temporarily, to the existing script's verification block:

```python
print("|mu - y| at context plies:", np.abs(mu[context_plies] - y_true[context_plies]))
```

**CHECKPOINT 1.** Paste that output. If the errors are small (≲ 0.1) it was a rendering artefact and
you may remove the line. **If they are large, stop and report — that is a real defect in the existing
script and it changes what this whole exercise means.**

---

### Step 2 — the mean-pooled CNP, strictly

New class in the new file. Reuse the existing `ChessTrajectoryGenerator` by importing it, so both
models see **identical data**.

```
Encoder   MLP: (x_c, y_c) -> r_c            Linear(2,128) ReLU Linear(128,128) ReLU Linear(128,128)
Aggregate r = r_c.mean(dim=context)          <-- ONE vector. Permutation-invariant. No x_t anywhere.
Decoder   MLP: (r, x_t) -> (mu, log_var)     Linear(129,128) ReLU Linear(128,128) ReLU Linear(128,2)
sigma     = softplus(raw) + 1e-4
Loss      exact Gaussian NLL (the existing gaussian_nll is correct -- import it)
```

**⚑ The one invariant that makes this a CNP and not something else: `r` must be computed before any
target query is seen, and must be identical for every target ply in the game.** If `r` depends on
`x_t` in any way, you have rebuilt the thing that already exists.

Comment the code at exactly three places, because this is a teaching artifact and those are the
three ideas: (a) why mean-pooling gives permutation invariance and variable context size, (b) that
the decoder receives only `r` and `x_t`, (c) how the NLL trades mean accuracy against σ.

**CHECKPOINT 2.** Paste the model summary and parameter count, plus the assertion you used to prove
`r` is independent of the target set (e.g. compute `r` for two different target sets and assert the
tensors are equal).

---

### Step 3 — two comparators, because a pretty ribbon proves nothing

**C1 — linear interpolation + constant σ.** Straight lines between context points; σ = the residual
standard deviation on the training trajectories. Zero training, ~10 lines. **This is the floor.** If
a neural model cannot beat it on held-out NLL, it has learned nothing.

**C2 — exact GP posterior.** RBF kernel, exact solve, on the same context points. With ~60 plies
this is a small linear system. **This is the ceiling** — the thing a Neural Process is trying to
approximate cheaply.

**Fit the GP's hyper-parameters on training trajectories, never on the test game.** Fitting on the
game you then plot makes the ceiling look better than it is.

**CHECKPOINT 3.** Held-out NLL for all four methods on ≥200 unseen trajectories, with a bootstrap
95% CI on each. Order expected: C1 worst, CNP better, kernel model better still, GP best or near it.
**Report what you actually get, including if it contradicts that.**

---

### Step 4 — one figure, four curves, one game

`scratch/cnp_comparison_demo.png`. Two panels sharing an x-axis, or four stacked — your choice, but:

- **The same game, the same 6 context plies, the same seed for every method.** Different context sets
  make the comparison meaningless.
- Ground truth dashed; context points marked; predicted mean solid; ±2σ shaded.
- **Label each panel with what it is**: "CNP (DeepSets mean-pooling)", "RBF kernel attention (the
  existing script)", "Exact GP", "Linear interpolation".
- Annotate each with its measured σ at context and σ in gaps. **Compute them; do not hardcode.**

---

### Step 5 — ⚑ measure the invariant for every method, and do not tune toward the expected answer

For each method report σ at context, σ in gaps, and the ratio, exactly as the existing script does.

**The expected result is that the mean-pooled CNP pinches LESS than the kernel model.** That is not
a defect. **That is the finding, and it is the entire point of the exercise.**

**Do NOT tune the CNP — width, depth, epochs, learning rate — to make its ratio approach the kernel
model's.** If you find yourself adjusting hyper-parameters until the CNP looks better, stop: you are
erasing the lesson. Report the honest numbers from a reasonable, standard configuration.

If the CNP happens to pinch *just as sharply*, that is a genuinely surprising result and it means
something is wrong with the setup — most likely `r` is leaking target information. Say so and stop.

**CHECKPOINT 5.** The four-row table: method, σ_context, σ_gap, ratio, held-out NLL with CI.

---

### Step 6 — correct the existing script's name, and nothing else about it

`scripts/chess_trajectory_cnp.py` is currently titled and documented as a Conditional Neural
Process. It is not. Change **only** the module docstring, the class docstring, and the plot title to
describe what it actually is — an RBF-kernel attentive interpolator — with one sentence noting it is
closer to an ANP/GP than to a CNP.

**Change no code, no hyper-parameter, no output number.** Re-run it afterwards and confirm the
invariant numbers are unchanged.

**Why this matters beyond tidiness:** Thejus intends to describe this work in an interview with a
Gaussian-process researcher. A model labelled CNP that aggregates per-query is exactly the claim
that gets unpicked in one question. Fixing the label now costs a minute; not fixing it costs the
interview.

**CHECKPOINT 6.** The diff of the docstring change, and the re-run invariant output showing the
numbers are identical.

---

## 5. REPORT

`agents/reports/2026-09-03_mean-pooled-cnp-comparison_REPORT.md`: every checkpoint's real pasted
output, the four-row table, and — because this is a teaching artifact — **a short section written
for Thejus, not for me**, answering in plain language:

1. What is the mean-pooled CNP doing that the kernel model is not?
2. Looking at the figure, where does the CNP oversmooth, and why does mean-pooling cause that?
3. What does the gap between the CNP's NLL and the exact GP's NLL cost us, and what does it buy?

Then the standing question:

> **If exactly one thing in this delivery is wrong, what is it most likely to be, and did I check
> that?**

---

## 6. ACCEPTANCE

1. `python scripts/chess_trajectory_cnp_comparison.py` runs on CPU, no arguments, under two minutes.
2. Training NLL **decreases and plateaus**. *(Not "monotonically decreases" — minibatch NLL is noisy
   and will not be monotone. The plan's original criterion would fail a healthy run, and a criterion
   that fails spuriously is one you learn to ignore.)*
3. `r` proven independent of the target set (Step 2 assertion).
4. All four methods measured on the same games, same context, same seed.
5. Existing script's numbers unchanged after the docstring fix.

## 7. STOP AND ASK

Not covered: changing the existing script's behaviour or hyper-parameters; tuning the CNP to
improve its ratio; touching `backend/`, `phi_net/` or `data/`; running an engine; committing.

**A stop with a clear question is a successful delivery. And an unexpected result is a result, not a
bug to be tuned away.**
