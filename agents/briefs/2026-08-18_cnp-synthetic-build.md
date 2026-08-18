```
Brief-ID:     2026-08-18_cnp-synthetic-build
Written:      2026-08-18
Target repo:  cnp_synthetic  (C:\Users\Admin\Documents\cnp_synthetic)
Route:        API/standalone - deliberately self-contained; needs no workspace access
Type:         implementation
Status:       ACTIVE (handed over, not yet run - the Gemini worker was unavailable)
Depends on:   none
```

> **ARCHIVE SNAPSHOT.** The canonical copy the worker actually reads lives at
> `C:\Users\Admin\Documents\cnp_synthetic\WORKER_TASK_CNP_SYNTHETIC.md`, committed in that
> repo so the build stays self-contained. This copy exists so the archive is complete.
> Briefs are immutable after handover, so the two cannot drift.

---

# WORKER TASK — Conditional Neural Process on synthetic data, with an honest uncertainty evaluation

Model: use your strongest available model. Token budget is not a concern —
follow this spec precisely. Detail invested here is the biggest lever on quality.

**Read the whole document before writing a line of code.** Everything you need is
in it. Do not consult other repositories; this file is self-contained.

---

## 0. THE ONE THING THAT MATTERS MOST

This code exists so that a specific sentence becomes **true and defensible in a job
interview**: *"I have implemented a conditional neural process and evaluated its
uncertainty properly."*

That means the deliverable is judged on **whether every number in it is real**, not
on whether the numbers are impressive. A CNP that underfits, produces over-smooth
means and over-wide uncertainty is a **completely acceptable result** — it is the
known, published behaviour of this model class. Reporting that honestly is worth
more than a good-looking number that cannot be reproduced.

**Three hard prohibitions. A submission that violates any of them is rejected
outright, no revision:**

1. **Never write a number that a run did not produce.** No estimated, expected,
   illustrative, or placeholder metrics. Not in `RESULTS.md`, not in `README.md`,
   not in a docstring, not in a comment.
2. **Never claim a check you did not execute.** If you did not run it, say "not
   run".
3. **Never soften a bad result.** If the CNP loses to a baseline, report that it
   lost, in the table, in plain language.

Every reported number is mechanically traced back to a saved log (§8). The reviewer
greps the logs for each number in your `RESULTS.md`. Numbers that do not appear
verbatim in a log are treated as fabricated.

---

## 1. ENVIRONMENT (pinned — do not deviate, do not install anything else)

Windows. The **only** interpreter to use, by full path:

```
C:\Users\Admin\miniconda3\envs\cszero\python.exe
```

Already installed and verified present — do not upgrade, downgrade, or reinstall:

| package | version |
|---|---|
| Python | 3.11.15 |
| torch | 2.13.0+**cpu** |
| numpy | 2.4.6 |
| matplotlib | 3.11.1 |
| pytest | 9.1.1 |

**There is no GPU.** `torch.cuda.is_available()` is `False`. All code must run on
CPU and the runtime budget in §7 assumes CPU.

**`scipy` is NOT installed and you may not install it.** You therefore need the
normal CDF and PDF without scipy. Use these exactly:

```python
import math, torch
SQRT2 = math.sqrt(2.0)
INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)

def std_normal_cdf(z):            # Phi
    return 0.5 * (1.0 + torch.erf(z / SQRT2))

def std_normal_pdf(z):            # phi
    return INV_SQRT_2PI * torch.exp(-0.5 * z * z)
```

**Do not `pip install` anything.** If you believe a package is genuinely required,
STOP and report it instead of installing it.

---

## 2. SCOPE AND BOUNDARIES (hard)

**Work only inside** `C:\Users\Admin\Documents\cnp_synthetic\`.

This directory is a fresh git repository whose committed baseline is exactly three
files: `.gitignore`, a stub `README.md`, and this brief. Everything you produce will
therefore show up as uncommitted changes. The reviewer runs `git status` and
`git diff` against that baseline, so keep the tree clean and commit nothing.

**You may create or edit only these paths:**

```
cnp/__init__.py
cnp/data.py
cnp/gp.py
cnp/metrics.py
cnp/model.py
cnp/plotting.py
tests/test_metrics.py
tests/test_gp.py
tests/test_model.py
tests/test_data.py
train_1d.py
train_city.py
README.md
RESULTS.md
figures/          (PNG output only)
runs/             (log output only)
```

**Do NOT touch, read from, or write to any of these — they are unrelated projects
and a write there is a boundary violation:**

- `C:\Users\Admin\Documents\chess_speak_out_loud\` (any file)
- `C:\Users\Admin\Documents\job_search\` (any file)
- The conda environment itself (no installs, no upgrades)

If you think you need something outside the permitted list, **STOP and report it**
rather than doing it.

**No scratch left behind.** No `debug_*.py`, no commented-out experiments, no
`tmp/`. Do not commit anything — leave the changes uncommitted for review.

---

## 3. WHAT A CNP IS (pinned specification — implement exactly this)

A Conditional Neural Process (Garnelo et al., 2018, arXiv:1807.01613) maps a
**context set** of observed input/output pairs plus a set of **target inputs** to a
**Gaussian predictive distribution at each target input**.

### 3.1 Tensor shapes (pinned — do not guess, do not reorder)

`B` = number of tasks in a batch, `N_c` = context points, `N_t` = target points,
`D_x` = input dimension, `D_y` = output dimension (**always 1 in this project**).

| tensor | shape | dtype |
|---|---|---|
| `x_context` | `(B, N_c, D_x)` | float32 |
| `y_context` | `(B, N_c, D_y)` | float32 |
| `x_target`  | `(B, N_t, D_x)` | float32 |
| `y_target`  | `(B, N_t, D_y)` | float32 |
| `mu` (out)  | `(B, N_t, D_y)` | float32 |
| `sigma` (out)| `(B, N_t, D_y)` | float32, strictly positive |

`D_x = 1` for the 1-D task (§5.1), `D_x = 2` for the city task (§5.2). The same
model class must serve both, parameterised by `D_x` — do not write two models.

### 3.2 Architecture (pinned)

**Encoder** — an MLP applied pointwise to each context pair:

- input: `concat([x_context, y_context], dim=-1)` → shape `(B, N_c, D_x + D_y)`
- hidden: `Linear → ReLU` layers with widths `[128, 128, 128]`
- output: `Linear` to representation width `R = 128`, giving `(B, N_c, 128)`

**Aggregator** — **mean over the context dimension**:

- `r = encoded.mean(dim=1)` → `(B, 128)`

This mean is not a stylistic choice. It is what makes the model **invariant to the
order of the context points** and able to accept **any number** of them. A test in
§9 checks this property directly, and an order-dependent aggregator (RNN, attention,
concatenation, sum-without-mean) will fail it. Use the mean.

**Decoder** — an MLP applied pointwise to each target input, conditioned on `r`:

- expand `r` to `(B, N_t, 128)` (`r.unsqueeze(1).expand(-1, N_t, -1)`)
- input: `concat([r_expanded, x_target], dim=-1)` → `(B, N_t, 128 + D_x)`
- hidden: `Linear → ReLU` layers with widths `[128, 128, 128]`
- output: `Linear` to `2 * D_y`, split into `mu_raw` and `sigma_raw`

**Output head (pinned exactly):**

```python
mu = mu_raw
sigma = 0.01 + 0.99 * torch.nn.functional.softplus(sigma_raw)
```

The `0.01` floor is deliberate: it stops the predictive variance collapsing to zero
and producing an infinite log-likelihood. Do not change it, and do not use
`exp(log_sigma)` instead.

### 3.3 Training objective (pinned)

The loss is the **negative mean Gaussian log-likelihood of the target outputs**
under the predicted `(mu, sigma)`:

```python
dist = torch.distributions.Normal(mu, sigma)
loss = -dist.log_prob(y_target).mean()
```

Mean over **all** dimensions (batch, points, output dim).

### 3.4 The context/target convention (pinned — this is the classic silent bug)

There are two different conventions and mixing them up quietly corrupts the results.
Implement **both** of these, exactly:

- **During TRAINING**, the target set is a **superset of the context set**:
  `x_target = concat([x_context, x_extra])`. The model is scored on points it has
  seen *and* points it has not. This is the convention in the original paper and it
  is what makes training stable.
- **During EVALUATION**, the target set is **disjoint from the context set** —
  held-out points only, never any context point. Every metric in §6 is computed on
  held-out points only.

Write this distinction into a docstring in `cnp/data.py` so it is not lost. A
data-generation function must make clear in its name or arguments which of the two
it produces (e.g. `sample_train_batch` vs `sample_eval_batch`).

---

## 4. THE TWO BASELINES (mandatory — the CNP number is meaningless alone)

A metric without a comparison is not a result. Implement both.

### 4.1 The oracle: exact GP posterior (1-D task only)

The 1-D data is drawn *from* a Gaussian process whose kernel you know (§5.1). The
exact GP posterior, computed with the **true** hyperparameters that generated that
task, is the **best achievable** predictive distribution. It is an upper bound.

`cnp/gp.py`, pure functions, numpy or torch (your choice, but no scipy):

Kernel (RBF / squared exponential):

```
k(x, x') = s^2 * exp( -(x - x')^2 / (2 * l^2) )
```

Posterior at test inputs `X*` given context `(X, y)` with observation noise
variance `sn^2`:

```
K   = k(X, X) + sn^2 * I          # (n, n)
Ks  = k(X, X*)                    # (n, m)
Kss = k(X*, X*)                   # (m, m)
alpha = solve(K, y)
mean  = Ks^T @ alpha                                  # (m,)
var   = diag(Kss) - sum(Ks * solve(K, Ks), axis=0)    # (m,)
predictive_sigma = sqrt(var + sn^2)
```

Use `numpy.linalg.solve` (or `torch.linalg.solve`) — **not** an explicit matrix
inverse. Add jitter `1e-8` to the diagonal of `K` for numerical stability.

**Note carefully:** the predictive sigma **includes** the observation noise `sn^2`,
because the CNP is predicting noisy observations `y`, not the latent function. If
you omit it, the GP will look falsely overconfident and the comparison is invalid.

The CNP should **approach but not beat** this oracle. If your CNP beats the exact
GP posterior on CRPS, something is wrong — most likely a context/target leak (§3.4)
or the noise term above. Investigate and report it; do not celebrate it.

### 4.2 The floor: the climatology baseline (both tasks)

A single Gaussian, constant over all target inputs, using the **context** points of
that task:

```
mu    = mean(y_context)
sigma = std(y_context, unbiased=True), clamped to a minimum of 0.01
```

This predictor ignores position entirely. **Any model that claims to have learned
spatial structure must beat it.** If the CNP does not beat climatology, say so
prominently in `RESULTS.md` — that is a finding, and hiding it is the one
unrecoverable failure.

---

## 5. THE TWO SYNTHETIC DATASETS (pinned)

### 5.1 Task A — 1-D GP samples (the standard benchmark)

Per task, sampled independently:

- domain: `x ∈ [-2, 2]`
- kernel: RBF as in §4.1 with `s = 1.0`, lengthscale `l ~ Uniform(0.3, 1.0)`
- observation noise: `sn = 0.02`
- `N_c ~ UniformInt{3, ..., 50}` context points at uniformly random `x`
- `N_extra ~ UniformInt{1, ..., 50}` extra target points at uniformly random `x`
- draw `y` jointly from the GP prior at all sampled `x` (Cholesky of the kernel
  matrix plus jitter `1e-8`, times a standard normal vector), then add `sn` noise

This task exists because its oracle (§4.1) is computable in closed form. That makes
it the one place where "is my CNP actually working?" has an objective answer.

### 5.2 Task B — the synthetic city (the one that maps to the real problem)

A 2-D scalar concentration field on `[0, 1]^2`, built from a **smooth regional
background** plus a **sharp local road source** — the structure that makes urban air
quality hard, in miniature. Deterministic given a seed:

```
field(x1, x2) = background(x1, x2) + road(x1, x2)

background = 0.6 * exp(-((x1-0.3)^2 + (x2-0.7)^2) / (2 * 0.25^2))
           + 0.4 * exp(-((x1-0.8)^2 + (x2-0.2)^2) / (2 * 0.30^2))
           + 0.3 * x1

road       = 1.2 * exp(-(d(x1, x2))^2 / (2 * 0.03^2))
```

where `d` is the perpendicular distance from the point to the straight line segment
running from `(0.1, 0.15)` to `(0.9, 0.85)`. The road width `0.03` is deliberately
much smaller than typical station spacing — the model **cannot** resolve it from
sparse stations, and its uncertainty should reflect that.

- "stations": `N_c ~ UniformInt{5, ..., 40}` at uniformly random locations in the
  unit square, with observation noise `sn = 0.02`
- for training, vary the field between tasks by adding a per-task random offset
  `~ Uniform(-0.2, 0.2)` to each of the two background bump centres and a per-task
  amplitude scale `~ Uniform(0.8, 1.2)` on the road term; keep the road geometry
  fixed. **The road position is fixed across tasks — state this limitation in
  `RESULTS.md`.**
- evaluation grid: `64 x 64` regular grid over `[0, 1]^2`

There is no exact oracle for this task (the field is not a GP sample), so
climatology (§4.2) is the only baseline here. Say so in `RESULTS.md` rather than
inventing one.

---

## 6. THE EVALUATION (this is the actual deliverable)

All of these are computed on **held-out target points only** (§3.4).

### 6.1 NLL

Mean negative log-likelihood per target point, under `Normal(mu, sigma)`. Report as
a plain float. Lower is better. Note in `RESULTS.md` that this is the training
objective, so it flatters the CNP relative to the baselines — state it, do not hide
it.

### 6.2 CRPS (Continuous Ranked Probability Score) — closed form, PINNED

For a Gaussian predictive distribution `N(mu, sigma^2)` and an observation `y`, with
`z = (y - mu) / sigma`, `Phi` the standard normal CDF and `phi` its PDF:

```
CRPS(N(mu, sigma^2), y) = sigma * ( z * (2*Phi(z) - 1) + 2*phi(z) - 1/sqrt(pi) )
```

**Implement exactly this formula.** Do not derive your own, do not use a sample-based
approximation, do not look for an alternative form. It is from Gneiting & Raftery
(2007). Lower is better. Report the mean over all held-out target points.

CRPS matters because, unlike NLL, it is not the training objective and it does not
blow up on a single confident mistake — it is the standard scoring rule in
probabilistic environmental forecasting.

### 6.3 Calibration — central-interval coverage

For nominal levels `p` in `numpy.linspace(0.05, 0.95, 19)`:

- the central `p`-interval is `[mu + sigma * q_lo, mu + sigma * q_hi]` where
  `q_lo`, `q_hi` are the standard normal quantiles at `(1-p)/2` and `(1+p)/2`
- **empirical coverage** at level `p` = the fraction of held-out targets whose `y`
  falls inside their own interval

You need standard-normal quantiles without scipy. Get them by **bisection on
`std_normal_cdf`** (§1) to a tolerance of `1e-10` on the interval `[-10, 10]`, or
equivalently via `torch.erfinv`: `q(p) = sqrt(2) * erfinv(2p - 1)`. Either is fine;
`erfinv` is simpler and preferred.

Report **ECE** (expected calibration error) = `mean(|empirical(p) - p|)` over the 19
levels. Lower is better; 0 is perfect.

Also produce a **PIT histogram**: `z_i = Phi((y_i - mu_i) / sigma_i)` should be
Uniform(0,1) if the model is calibrated. 20 bins. A U-shape means overconfident
(intervals too narrow); a dome means underconfident (too wide).

### 6.4 Sharpness — and why it must be reported next to calibration

Report **mean sigma** over held-out targets.

State this explicitly in `RESULTS.md`, in your own words: **calibration alone is
trivial to achieve.** A model that always predicts a huge sigma is perfectly
calibrated and completely useless. The goal is the **sharpest** predictive
distribution **subject to** being calibrated. A calibration number reported without
a sharpness number next to it is not a result. Any table containing ECE must contain
mean sigma in an adjacent column.

### 6.5 Leave-one-station-out (Task B) — the field's actual protocol

On a **single fixed evaluation instance** with exactly **25 stations** and seed
`20260818`:

- for each station `i` in `0..24`: condition the CNP on the **other 24** stations,
  predict at station `i`'s location, record `(y_i, mu_i, sigma_i)`
- report NLL, CRPS, ECE and mean sigma over those 25 held-out predictions
- do the same for climatology (conditioned on the same 24 each time)

This is exactly how a spatial interpolation model is validated when stations are
scarce, which is why it is here.

---

## 7. RUNTIME BUDGET (CPU — respect it)

- Adam, learning rate `3e-4`, batch of `B = 16` tasks per step.
- Task A: **60,000** training steps. Task B: **60,000** training steps.
- **Hard budget: each training run must finish in under 15 minutes wall-clock.**
  Print elapsed time. If a run exceeds the budget, **reduce the step count** until
  it fits, and report the number of steps you actually ran. Do not silently run
  longer; do not report the step count you intended rather than the one you ran.
- Print the running mean training loss every 2,000 steps so progress is visible.
- Evaluate on **512 freshly sampled evaluation tasks** (disjoint context/target,
  §3.4) with seed `20260818`.

### Reproducibility (required)

- Seed `torch`, `numpy`, and Python `random` at the top of every entry point.
- Training seed: `1234`. Evaluation seed: `20260818`.
- Save the trained weights to `checkpoints/` (git-ignored already).
- **Gate:** running the evaluation twice must produce **identical** metrics to 4
  decimal places. Show this by running it twice and pasting both outputs.

---

## 8. PROVENANCE — how every number gets traced (mandatory mechanism)

Each entry point writes its **full stdout, verbatim** to a log file, in addition to
printing it:

```
runs/train_1d.log
runs/train_city.log
runs/eval_repeat_check.log
runs/pytest.log
```

**Every numeric value that appears in `RESULTS.md` must appear verbatim in one of
these logs.** The reviewer will grep for them. Round consistently: print metrics to
**4 decimal places** and quote them in `RESULTS.md` at the same 4 decimal places, so
the strings match exactly.

Print each metrics table in a single clearly delimited block, e.g.:

```
=== TASK A (1-D GP) — EVAL ON 512 HELD-OUT TASKS, SEED 20260818 ===
model         NLL        CRPS       ECE      mean_sigma
cnp           ...        ...        ...      ...
gp_oracle     ...        ...        ...      ...
climatology   ...        ...        ...      ...
```

If a metric could not be computed, print `n/a` and explain why in `RESULTS.md`.

---

## 9. TESTS (enumerated — each must be a REAL guard)

`pytest`, run with the pinned interpreter. **Every test below must fail if the
behaviour it protects is broken.** The reviewer mutation-tests these: he will break
the production code a test claims to protect and confirm the test goes red. **A test
that would still pass with the feature deleted is a rejection of the whole
submission.** Do not write a test that only asserts a tensor shape when the point is
a value.

**`tests/test_metrics.py`**

1. `test_crps_standard_normal_at_zero` — `crps_gaussian(mu=0, sigma=1, y=0)` equals
   **0.2336949773** to 8 decimal places. (This is `2*phi(0) - 1/sqrt(pi)`, and also
   `(sqrt(2)-1)/sqrt(pi)`; two independent expressions agree on it, so it is a hard
   target, not an approximation.)
2. `test_crps_collapses_to_absolute_error` — as `sigma → 0` (use `sigma = 1e-6`),
   CRPS approaches `|y - mu|`; assert within `1e-5` for `mu=1.0, y=2.5`.
3. `test_crps_is_minimised_at_truth` — for fixed `sigma=1.0` and `y=0`, CRPS at
   `mu=0` is strictly less than CRPS at `mu` in `{-1.0, -0.5, 0.5, 1.0}`.
4. `test_crps_scales_with_sigma` — CRPS at `y = mu` is exactly proportional to
   sigma: `crps(0, 2, 0) == 2 * crps(0, 1, 0)` within `1e-9`.
5. `test_coverage_curve_on_perfectly_calibrated_samples` — draw 200,000 samples
   `y ~ N(0,1)` with predicted `mu=0, sigma=1`; empirical coverage must match every
   nominal level within `0.01`, and ECE must be below `0.005`.
6. `test_coverage_detects_overconfidence` — same samples, but predict `sigma=0.5`;
   assert ECE is **greater than 0.1** and that empirical coverage is **below**
   nominal at the `0.5` level. (This is the guard that proves the metric can detect
   a miscalibrated model at all.)
7. `test_pit_uniform_for_calibrated` — PIT values of calibrated samples have mean
   within `0.01` of `0.5` and standard deviation within `0.01` of `1/sqrt(12)`.

**`tests/test_gp.py`**

8. `test_gp_interpolates_observations` — with tiny noise `sn=1e-6`, the GP
   posterior mean **at an observed input** equals the observed `y` within `1e-4`,
   and the posterior sigma there is within `1e-3` of `sn`.
9. `test_gp_reverts_to_prior_far_away` — at an input 50 lengthscales from any
   observation, posterior mean is within `1e-4` of `0` and posterior sigma is within
   `1e-4` of `sqrt(s^2 + sn^2)`.
10. `test_gp_posterior_variance_is_non_negative` — over 100 random configurations,
    all posterior variances are `>= 0`.

**`tests/test_model.py`**

11. `test_permutation_invariance_of_context` — build a CNP, run it on a context set,
    then run it on a **randomly permuted** version of the same context set; `mu` and
    `sigma` must be identical within `1e-6`. **This is the structural guard on §3.2's
    mean aggregator** — it fails for any order-dependent encoder.
12. `test_accepts_variable_context_size` — the same model instance runs without error
    on `N_c` of 1, 7, and 63, returning correct shapes each time.
13. `test_sigma_is_strictly_positive_and_above_floor` — for random inputs, `sigma`
    is everywhere `>= 0.01`.
14. `test_output_shapes` — `mu` and `sigma` both have shape `(B, N_t, D_y)` for
    `D_x = 1` and `D_x = 2`.
15. `test_untrained_model_loses_to_a_trained_one` — **a real end-to-end guard**:
    train a small CNP on Task A for 2,000 steps (must take under 60 seconds) and
    assert its held-out CRPS is **lower** (better) than an untrained model's on the
    same evaluation batch. This is the test that proves the training loop actually
    learns, and it must run unmocked, on real generated data.
16. `test_predictive_sigma_shrinks_with_more_context` — using the model trained in
    test 15, mean predicted sigma over a fixed target grid with 40 context points is
    **lower** than with 3 context points, averaged over 32 tasks. This proves the
    model actually conditions on its context rather than ignoring it.

**`tests/test_data.py`**

17. `test_train_batch_targets_include_context` — for a training batch, every context
    point appears in the target set (§3.4).
18. `test_eval_batch_targets_exclude_context` — for an evaluation batch, **no**
    target input coincides with any context input (within `1e-9`).
19. `test_city_field_road_is_a_sharp_ridge` — the field value **on** the road
    centreline exceeds the value at a point `0.1` away, perpendicular to it, by at
    least `1.0`. Guards the geometry in §5.2.
20. `test_data_is_deterministic_given_seed` — the same seed produces bitwise
    identical batches on two calls.

---

## 10. FIGURES (matplotlib, saved to `figures/`, 150 dpi, readable labels)

Every figure needs axis labels, units where they exist, a legend, and a title.

1. **`fig1_1d_fit.png`** — four panels, context sizes 5 / 10 / 25 / 50 on the same
   underlying GP task. Each panel: the true function, the context points as dots,
   the CNP mean as a line, a shaded `±2σ` band, and the **exact GP oracle mean as a
   dashed line**. This single figure shows both what the model does and how far it
   is from optimal.
2. **`fig2_calibration.png`** — two panels. Left: coverage curve (empirical vs
   nominal) for CNP, GP oracle and climatology, with the `y = x` diagonal. Right:
   PIT histogram for the CNP, 20 bins, with the uniform density as a horizontal
   reference line.
3. **`fig3_city_field.png`** — four panels on the 64×64 grid, for one evaluation
   instance with 25 stations: (a) the true field, (b) CNP mean, (c) CNP sigma,
   (d) absolute error `|true - mean|`. Overlay the station locations on every panel.
   Use a **shared colour scale** for (a) and (b) and state the scale in the caption.
   Panels (c) and (d) are the interesting pair: **if the uncertainty is honest, high
   sigma and high error should appear in the same places.**
4. **`fig4_loso.png`** — leave-one-station-out (§6.5): predicted vs observed for the
   25 stations, with `±2σ` error bars and the `y = x` line.

In `RESULTS.md`, write one sentence per figure saying **what it shows**, including
where the model does badly.

---

## 11. `RESULTS.md` (the document that gets read in an interview)

Structure, in this order:

1. **What was built** — two sentences.
2. **Task A results table** — CNP / GP oracle / climatology × NLL / CRPS / ECE /
   mean sigma. Numbers verbatim from `runs/train_1d.log`.
3. **Task B results table** — CNP / climatology, same columns, plus the separate
   leave-one-station-out table. Numbers verbatim from `runs/train_city.log`.
4. **The four figures**, each with its one-sentence reading.
5. **"What this shows"** — 3–5 bullets, factual.
6. **"What this does NOT show"** — this section is mandatory and must be honest.
   At minimum it must state: the model was trained and tested on synthetic data
   from a known generative process; the city road position is fixed across tasks
   (§5.2), so generalisation to new road geometries is untested; a CNP is known to
   underfit relative to an attentive or convolutional neural process; and no real
   measurement data was used at any point.
7. **Reproduction** — the exact commands, in order, that regenerate everything.

Keep it factual and short. No adjectives about how good the results are.

---

## 12. GATE — run these and paste the REAL terminal output

Paste actual output. Not a summary, not a description, not "all tests passed".

```
cd C:\Users\Admin\Documents\cnp_synthetic

C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest tests/ -v

C:\Users\Admin\miniconda3\envs\cszero\python.exe train_1d.py

C:\Users\Admin\miniconda3\envs\cszero\python.exe train_city.py

git status
```

Then, for the reproducibility gate of §7, re-run **evaluation only** (from the saved
checkpoint, no retraining) twice and paste both metric blocks so they can be
compared line by line.

---

## 13. YOUR REPORT (append to `RESULTS.md` as a final section, or a separate `WORKER_REPORT.md`)

State plainly:

1. **Every gate command you ran, and its real outcome.** If something failed and you
   fixed it, say what failed and what the fix was.
2. **Did the CNP beat climatology on each task and metric?** Yes or no, per cell.
   If no, say so.
3. **How far is the CNP from the GP oracle on Task A** (CRPS ratio)? A gap is
   expected. Report it.
4. **Anything you had to deviate from in this spec, and why.** Deviating because the
   spec was wrong about reality is a *good* outcome — report it clearly with the
   evidence rather than silently working around it. Deviating to make a gate pass is
   not.
5. **Anything you did not do**, explicitly listed.
6. **Actual wall-clock time and actual step count** for each training run.

---

## 14. SUMMARY OF THE HARD RULES

- Only the pinned interpreter. No installs. No GPU. No scipy.
- Only files inside `cnp_synthetic/`, only the paths listed in §2.
- Every number in a document must exist verbatim in a log in `runs/`.
- Every test must fail when the thing it guards is broken.
- Evaluation metrics on held-out points only; training targets include context.
- Report bad results as bad results.
- If you are unsure about a design decision not covered here, **STOP and ask** rather
  than choosing for yourself. An unanswered question is cheap; a plausible wrong
  choice discovered later is not.
