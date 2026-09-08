# CNP Walkthrough — Hamburg Temperature & Spatial Uncertainty

*A concrete, step-by-step walkthrough of how an Encoder-Decoder Conditional Neural Process (CNP) predicts spatial fields and calibrated uncertainty, using real Hamburg districts and exact arithmetic.*

---

## 1. The Setting: West Hamburg Weather Stations

We wish to predict the ambient temperature and the epistemic uncertainty at an unmonitored location in **Altona** using 3 active weather stations in surrounding districts.

```
                  [Eimsbüttel]
                 (53.57, 9.95)
                    17.0°C
                      |
                      | ~2.5 km
                      v
 [Bahrenfeld] ----> [ALTONA] <---- [St. Pauli]
(53.56, 9.90)    (53.55, 9.93)   (53.55, 9.96)
   15.8°C           TARGET          16.5°C
                    (?, ?)
```

### Context Set $C$ (Known Observations)
* **Station 1 (St. Pauli):** $x_1 = [53.55, 9.96]$, $y_1 = 16.5^\circ\text{C}$
* **Station 2 (Eimsbüttel):** $x_2 = [53.57, 9.95]$, $y_2 = 17.0^\circ\text{C}$
* **Station 3 (Bahrenfeld):** $x_3 = [53.56, 9.90]$, $y_3 = 15.8^\circ\text{C}$

### Target Query $T$ (Unmonitored Location)
* **Target (Altona):** $x_* = [53.55, 9.93]$, $y_* = ?$

---

## 2. Step 1: The Encoder Processes the Context Set

A standard feedforward network cannot take an arbitrary number of stations as input because its input layer has fixed dimensions. A Conditional Neural Process solves this via **DeepSets** (Zaheer et al., 2017; Garnelo et al., 2018):

1. **Local Embeddings ($h_\theta$):**
   Each coordinate-measurement pair $(x_i, y_i) \in \mathbb{R}^3$ is passed independently through a multi-layer perceptron (MLP) $h_\theta$:
   $$r_1 = h_\theta([53.55, 9.96, 16.5])$$
   $$r_2 = h_\theta([53.57, 9.95, 17.0])$$
   $$r_3 = h_\theta([53.56, 9.90, 15.8])$$
   where each $r_i \in \mathbb{R}^{d}$ (e.g., $d = 128$).

2. **Permutation-Invariant Aggregation (The "Weather Vibe"):**
   The network aggregates the vectors using a symmetric operator (mean pooling):
   $$r_C = \frac{1}{|C|} \sum_{i=1}^{|C|} r_i = \frac{r_1 + r_2 + r_3}{3}$$
   * **Why this matters:** Reordering the stations (e.g., St. Pauli first vs. Bahrenfeld first) yields the exact same vector $r_C$. The vector $r_C$ compresses the regional atmospheric condition of West Hamburg into a single latent summary.

---

## 3. Step 2: The Decoder Makes the Prediction for Altona

The decoder $g_\phi$ is given the regional context summary $r_C$ concatenated with the specific target coordinates of Altona $x_* = [53.55, 9.93]$:
$$\text{Input} = [r_C, x_*] = [r_C, 53.55, 9.93]$$

The decoder's final layer splits into two distinct linear pathways producing two raw pre-activations, $z_1$ and $z_2$:

```
                   [r_C, x_*]
                       |
                 [Decoder MLP]
                       |
          +------------+------------+
          |                         |
     Pathway 1                 Pathway 2
      Linear                   Softplus
   (Unconstrained)           (Non-negative)
          |                         |
      z_1 = 16.4                z_2 = 0.5
          |                         |
     mu = 16.4°C         sigma^2 = ln(1 + e^0.5)
                              = 0.974 °C^2
```

### Pathway 1: The Mean ($\mu$) — Linear Layer
* The linear layer produces $z_1 = 16.4$.
* **No activation function is applied.** Physical temperatures can be positive, zero, or negative. Leaving this pathway unconstrained allows the model to predict any real value:
  $$\mu = 16.4^\circ\text{C}$$

### Pathway 2: The Variance ($\sigma^2$) — Softplus Activation
* The linear layer produces raw logit $z_2 = 0.5$.
* Variance must be strictly positive ($\sigma^2 > 0$). Negative variance is mathematically undefined.
* The model passes $z_2$ through the **Softplus** function, $\text{softplus}(z) = \ln(1 + e^z)$:
  $$\sigma^2 = \ln(1 + e^{0.5}) = \ln(1 + 1.6487) = \ln(2.6487) \approx \mathbf{0.974^\circ\text{C}^2}$$

---

## 4. Step 3: Translating into Real-World Statistical Uncertainty

The Neural Process outputs the parameters of a univariate Gaussian distribution for Altona:
$$p(y_* \mid x_*, C) = \mathcal{N}(\mu = 16.4^\circ\text{C}, \, \sigma^2 = 0.974^\circ\text{C}^2)$$

To interpret this physically:
1. **Standard Deviation ($\sigma$):**
   $$\sigma = \sqrt{0.974} \approx \mathbf{0.987^\circ\text{C}} \approx 1.0^\circ\text{C}$$

2. **Confidence Intervals:**
   Because the predictive distribution is continuous Gaussian (not a discrete $[0, 1]$ classification score), we use standard normal quantiles:
   * **68.3% Confidence ($\pm 1\sigma$):**
     $$16.4 \pm 1.0^\circ\text{C} \implies [\mathbf{15.4^\circ\text{C}}, \, \mathbf{17.4^\circ\text{C}}]$$
   * **95.4% Confidence ($\pm 2\sigma$):**
     $$16.4 \pm 2.0^\circ\text{C} \implies [\mathbf{14.4^\circ\text{C}}, \, \mathbf{18.4^\circ\text{C}}]$$

---

## 5. Scenario B: Stations 50 km Away & The Sigmoid Trap

Suppose our 3 context stations were located in **Kiel** (85 km north), **Lübeck** (60 km northeast), and **Bremen** (95 km southwest), rather than within Hamburg.

```
       [Kiel] (85 km)
          \
           \
            v
         [ALTONA] <---- [Lübeck] (60 km)
            ^
           /
          /
       [Bremen] (95 km)
```

1. **Information Degradation:** The context summary $r_C$ now provides much weaker local information about Altona.
2. **Decoder Response:** The decoder's uncertainty pathway produces a much higher pre-activation, e.g., $z_2 = 16.0$.
3. **Softplus vs. Sigmoid:**
   * **If we mistakenly used Sigmoid ($\frac{1}{1 + e^{-z}}$):**
     The output would be capped at $\sigma^2 \le 1.0$. Even if the stations are in another state, the model could never express an uncertainty greater than $\sigma = 1.0^\circ\text{C}$. This is catastrophic for physical regression.
   * **With Softplus ($\ln(1 + e^z)$):**
     As $z \to \infty$, $\text{softplus}(z) \to z$.
     $$\sigma^2 = \text{softplus}(16.0) \approx 16.0^\circ\text{C}^2 \implies \sigma = \mathbf{4.0^\circ\text{C}}$$
     The 95% confidence interval expands appropriately:
     $$16.0 \pm 2(4.0)^\circ\text{C} = 16.0 \pm 8.0^\circ\text{C} \implies [\mathbf{8.0^\circ\text{C}}, \, \mathbf{24.0^\circ\text{C}}]$$

---

## 6. Three "Interviewer-Level" Nuances (What Hereon / AEON-UP Will Probe)

When discussing this in an interview with Dr. Martin Ramacher or Dr. Matthias Karl, be ready for these three follow-up questions:

### Nuance 1: How does the model *actually* know the stations are 50 km away? (CNP vs. GP)
* **In a Gaussian Process (GP):** Distance is enforced **analytically** through a covariance kernel:
  $$k(x_t, x_c) = \sigma_f^2 \exp\left(-\frac{\|x_t - x_c\|^2}{2\ell^2}\right)$$
  When $\|x_t - x_c\| \gg \ell$, the kernel correlation $k \to 0$ mathematically. The posterior variance $\sigma^2(x_*)$ automatically reverts to the prior variance $\sigma^2_{\text{prior}}$.
* **In a Vanilla CNP:** There is **no analytical kernel**. The network must *learn* to expand variance over distance purely from its meta-training distribution. If the training tasks only included tight city clusters, evaluating stations 50 km away is **out-of-distribution (OOD)**. The MLP decoder might extrapolate erratically or stay overconfident.

### Nuance 2: The Mean-Pooling Bottleneck (Why we need Attentive NPs)
* In Step 1, uniform mean-pooling ($r_C = \frac{1}{3}\sum r_i$) compresses all context points into a single global vector.
* When decoding for Altona, the decoder gets $[r_C, x_{\text{Altona}}]$. It knows Altona's coordinates, but it cannot directly attend to the fact that Bahrenfeld is only 2 km away while St. Pauli is 3 km away.
* **The Solution — Attentive Neural Process (ANP, Kim et al., 2019):**
  Replace uniform mean-pooling with **Cross-Attention**:
  * **Query:** Target location $x_* = \text{Altona}$
  * **Keys / Values:** Context locations and features $(x_c, r_c)$
  Altona assigns heavy attention weights to Bahrenfeld and St. Pauli, and zero weight to distant stations. This eliminates the mean-pooling bottleneck and restores sharp local spatial gradients.

### Nuance 3: Numerical Stability in PyTorch Gaussian NLL
In PyTorch code, never write raw `sigma_sq = torch.softplus(z)`.

The Gaussian Negative Log-Likelihood loss is:
$$\mathcal{L}(\theta, \phi) = \frac{1}{2}\sum_{t \in T} \left[ \ln(2\pi \sigma_t^2) + \frac{(y_t - \mu_t)^2}{\sigma_t^2} \right]$$

If $z$ is strongly negative (e.g., $z = -20$), `softplus(z)` underflows to $0.0$. Taking $\ln(0)$ or dividing by $0$ produces `NaN` and destroys training. Always include a numerical stability floor $\epsilon$:
```python
# Standard PyTorch implementation
sigma_sq = torch.nn.functional.softplus(raw_var) + 1e-4
# or parameterized as std:
sigma = torch.nn.functional.softplus(raw_std) + 1e-3
```

---

## 7. Direct Translation to AEON-UP Urban Air Quality

To adapt this explanation to Helmholtz-Zentrum Hereon's work:

| Component | Temperature Example (Hamburg) | AEON-UP Urban Air Quality (Hereon) |
|---|---|---|
| **Target Variable ($y$)** | Ambient Temperature ($^\circ\text{C}$) | $\text{NO}_2$ or Ultrafine Particle (UFP) count ($\mu\text{g}/\text{m}^3$) |
| **Context Set ($C$)** | 3 weather stations (St. Pauli, Eimsbüttel, Bahrenfeld) | Fixed urban background monitoring stations (e.g., Sternschanze, Veddel) |
| **Target Query ($x_*$)** | Altona district coordinates | Unmonitored street canyon (e.g., Max-Brauer-Allee) with traffic covariates |
| **Epistemic Uncertainty ($\sigma$)** | Uncertainty due to sensor sparsity ($\approx 1.0^\circ\text{C}$) | Spatial uncertainty where street topology / wind channeling is unobserved |
| **Physical Bound** | Softplus for $\sigma^2 > 0$ | Softplus for $\sigma^2 > 0$, Log-Normal or Truncated Gaussian for non-negative pollution ($y \ge 0$) |

---

## 8. Summary Formula Card

$$\begin{aligned}
\text{Encoder:} \quad & r_i = h_\theta(x_i, y_i) \\
\text{Aggregator:} \quad & r_C = \frac{1}{|C|} \sum_{i \in C} r_i \\
\text{Decoder:} \quad & [\mu(x_*), z_2(x_*)] = g_\phi([r_C, x_*]) \\
\text{Variance:} \quad & \sigma^2(x_*) = \ln(1 + \exp(z_2(x_*))) + \epsilon \\
\text{Posterior:} \quad & y_* \sim \mathcal{N}(\mu(x_*), \, \sigma^2(x_*))
\end{aligned}$$
