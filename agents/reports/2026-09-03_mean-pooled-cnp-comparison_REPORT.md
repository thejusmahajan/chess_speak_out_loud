# REPORT — Mean-Pooled CNP Comparison & Defect Audit

**Date:** 2026-09-03  
**Target Repo:** `chess_speak_out_loud`  
**Brief:** `agents/briefs/2026-09-03_mean-pooled-cnp-comparison.md`  
**Status:** **CHECKPOINT 1 STOP & REPORT** (Real defect confirmed in `scripts/chess_trajectory_cnp.py`)

---

## 1. Checkpoint 1 — Verification of Context Plies Error

As instructed in Step 1 of the brief, we evaluated the absolute reconstruction error $| \mu - y |$ of `scripts/chess_trajectory_cnp.py` at the 6 context plies:

```python
print("|mu - y| at context plies:", np.abs(mu[context_plies] - y_true[context_plies]))
```

### Measured Output:
```text
|mu - y| at context plies: [0.11915131 0.22911036 0.21047744 0.31212386 0.24079809 0.13567322]
Mean Sigma at Evaluated Moves (Context): 0.0689
Mean Sigma at Unsearched Moves (Gaps):    0.1472
```

### Analysis of the Defect:
1. **The errors are large ($> 0.10$ everywhere, peaking at $0.3121$):**
   * Context ply 4 (move 5): $| \mu - y | = 0.1192$
   * Context ply 13 (move 14): $| \mu - y | = 0.2291$
   * Context ply 23 (move 24): $| \mu - y | = 0.2105$
   * **Context ply 35 (move 36): $| \mu - y | = 0.3121$** (ground truth $y = +0.339$, predicted $\mu = +0.027$)
   * Context ply 47 (move 48): $| \mu - y | = 0.2408$
   * Context ply 55 (move 56): $| \mu - y | = 0.1357$

2. **The Statistical Miss ($4.53\sigma$):**
   At ply 36, the context value is $+0.34$, while the predicted mean is $+0.027$ (an error of $0.3121$). With a reported context uncertainty of $\sigma = 0.0689$, the observation lies **$4.53\sigma$ outside the predicted mean**.
   In a calibrated Gaussian predictive distribution, a $4.53\sigma$ event has probability $p \approx 6 \times 10^{-6}$. This is not a rendering artifact; it is a genuine structural defect in the script.

---

## 2. Root Cause: Why Did This Happen?

In `scripts/chess_trajectory_cnp.py`, the model decoupled the mean prediction from the uncertainty prediction:

1. **The Hardcoded Variance Inductive Bias:**
   $$\sigma^2(x_t) = \sigma_{\text{noise}}^2 + \sigma_{\text{prior}}^2 \left(1 - \max_{c \in C} k(x_t, x_c)\right)$$
   This formula mechanically forces $\sigma(x_c) \to \sigma_{\text{noise}} \approx 0.068$ whenever $x_t$ is close to a context point $x_c$.
2. **The Unconstrained Neural Mean Decoder:**
   $$\mu(x_t) = \text{Decoder}(\sum_c w_{tc} v_c, x_t)$$
   The mean $\mu$ was produced by an MLP decoder from kernel-weighted latent vectors $v_c$. An MLP decoder does **not** guarantee exact interpolation; after 300 epochs of training across heterogeneous game trajectories, its reconstruction error at context points remained around $0.21$ (and $0.31$ on sharp turns).
3. **The Silent Failure:**
   Because $\sigma$ was dictated by distance rather than the decoder's actual reconstruction accuracy, the model reported an extremely confident, tight uncertainty band ($\pm 0.13$) around a mean that was off by $0.31$.
   The model was **confidently wrong at the very points it was given**.

---

## 3. Implications for the Comparison (Why This Proves the Brief's Point)

This failure illustrates the exact conceptual difference between:
* **Exact Gaussian Process (C2):** Solves the linear system $K^{-1} Y$, guaranteeing exact interpolation ($\mu(x_c) = y_c$) and exact mathematical posterior variance $\sigma^2(x_c) = \sigma_n^2$.
* **True Mean-Pooled CNP (Garnelo et al., 2018):** Learns $\mu$ and $\sigma$ jointly from a single global vector $r = \frac{1}{|C|}\sum r_c$ via NLL. Because it cannot resolve individual points from $r$, it underfits and honestly keeps $\sigma$ wider ($\sim 0.25$) rather than falsely claiming $\sigma = 0.06$.
* **Ad-hoc Kernel Model:** Fused a neural mean with a synthetic GP variance formula, creating an overconfident, uncalibrated predictor.

---

## 4. Next Steps Awaiting Direction

Per Step 1 instructions ("*If they are large, stop and report — that is a real defect in the existing script and it changes what this whole exercise means*"):

We have stopped at Checkpoint 1. We can proceed with:
1. Proceeding to **Step 2** (implementing the true DeepSets mean-pooled CNP `r = r_c.mean()`), **Step 3** (Linear C1 and Exact GP C2), **Step 4** (4-panel comparison figure), and **Step 5** (invariant table).
2. Fixing the mean interpolation of the kernel model (e.g. using a Nadaraya-Watson residual head $\mu(x_t) = \sum_c w_{tc} y_c + \text{residual}$) so its mean actually passes through the context points before comparing it against the CNP and GP.
