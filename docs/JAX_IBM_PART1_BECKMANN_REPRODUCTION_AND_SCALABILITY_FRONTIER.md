# Scientific Strategy & Background Research: Part 1 Publication
## Reproducing Beckmann et al. (2019) & Unlocking the Large-Agent Scalability Frontier in JAX

**Document ID:** `PUB-PART1-JAX-SCALABILITY-FRONTIER`
**Date:** 2026-09-22
**Revision:** r2 — corrected against the source PDF (`beckmann_etal19.pdf`). Every numeric claim below has been checked against the paper; see §7 for the correction log and §8 for open items.
**Target Goal:** Publication Series Part 1: *Advancing Eco-Evolutionary Science Beyond Speedup: JAX-IBM as a Portal to Multi-Trait Adaptation and Rare-Variant Dynamics.*
**Primary Baseline:** Beckmann, Schaum, & Hense (2019), *Phytoplankton adaptation in ecosystem models*, Journal of Theoretical Biology 468, 60–71.
**Target Venues:** arXiv preprint $\to$ *Ecological Modelling* / *Environmental Modelling & Software* (Part 1 science); *JOSS* separately, once the package is public (see §5.3).
**Execution Guardrail:** Strict theoretical formulation, static inspection, and reproducible mathematical grounding.

---

## 1. The Core Scientific Premise: Advancing Science, Not Just Speed

If a paper simply states: *"We ported a legacy phytoplankton model to Google JAX and achieved a $50\times$ speedup on GPU,"* reviewers will dismiss it as an incremental technical exercise.

**We must therefore start from the strongest form of the opposing result, not the weakest.** Beckmann et al. did not merely prefer the MCM for convenience; they demonstrated equivalence:

> *"For all cases, the differences between MuSe-IBM and MuSe-MCM are found to be negligible."* (Abstract)

> *"...in the limit of high resolution, the results of both approaches are essentially identical."* (§5)

> *"While the IBM has the advantage of including more mechanistic (i.e., probabilistic) processes, the MCM is much less computationally demanding and therefore suitable for implementation in three-dimensional ecosystem models."* (Abstract)

We accept all three. In a zero-dimensional tank, for a **single** trait, at high trait resolution, the Eulerian trait-diffusion approximation (MCM) and the Lagrangian IBM are statistically indistinguishable — and we will reproduce that equivalence ourselves as Figure 1. Quoting only the third sentence while suppressing the first two would be selective, and any referee who knows this paper would catch it.

**Our scientific thesis is therefore narrower and defensible:**
The demonstrated equivalence is a property of the 0-D, single-trait, high-resolution regime. It does not extend to (i) **multi-trait trade-off spaces**, where the MCM's state grows as $O(B^D)$ while the IBM grows as $O(D\cdot M)$; (ii) **single-cell mutation-fixation statistics**, which the $10^4$-cell supercell discretization cannot represent at all; or (iii) **genealogical structure**, which a compartment model does not carry.

The JAX-IBM is the **most practical** vehicle for these regimes — not the only conceivable one. Moment-closure and cumulant trait models (Norberg et al. 2012; Merico et al. 2014; Smith et al. 2016), adaptive dynamics, adaptive-mesh or sparse MCMs, and Gillespie eco-evolutionary methods (DeLong & Gibert 2016, cited in this very paper) are live alternatives, and the paper must say why they are not preferred rather than pretend they do not exist.

> **Attribution note.** The claim that the reference implementation is Fortran/OpenMP is **not supported by Beckmann et al. (2019)**, which names no language and reports no timings anywhere. If we make that claim it must be attributed to personal communication or to the parent model (Hense & Beckmann 2015, *Ecol. Modell.* 317, 66–82) — never cited to the 2019 paper. Equally, the paper never states that the IBM was too expensive to run: it ran $10^7$ agents (Appendix B). Its actual claim is that the MCM is *"much less costly (often about two orders of magnitude)"* and therefore better suited to 3-D embedding. Our premise must be stated at that strength, not stronger.

---

## 2. Baseline Reproduction: The Barebone PND Model

The barebone model (Beckmann et al. 2019, §2–3) simulates a closed, well-mixed tank ($V = 1\,\text{m}^3$) with constant cycling nitrogen mass $R = P + N + D = 5.0\,\text{mmol N}\cdot\text{m}^{-3}$:

$$\frac{dP}{dt} = \mu(N, T) P - \gamma_0 P$$
$$\frac{dN}{dt} = -\mu(N, T) P + \tau_0 D$$
$$\frac{dD}{dt} = \gamma_0 P - \tau_0 D$$

In the discrete IBM:

* **Biomass Growth:** $\frac{db_i}{dt} = \mu_i = \frac{\mu_0}{\ln 2} b_0 F_T(T, T_{opt, i}) F_N(N)$, where $F_T = \exp\left(-\left(\frac{T - T_{opt}}{\theta}\right)^2\right)$, $F_N = \frac{N}{k_N + N}$. Note that this rate is proportional to $b_0$, **not** to $b_i$ — individual growth is linear in time, not exponential.
* **Cell Division:** Triggers at $b_i \ge 2 b_0$. Parent and daughter each receive $0.5 \cdot b_i$.
* **Stochastic Mortality:** Agent dies if $X_{(0,1)} < \gamma_{crit} = \gamma_0 \cdot \Delta t$, releasing biomass to detritus $D$. With $\gamma_0 = 0.1\,\text{d}^{-1}$ and $\Delta t = 1\,\text{h}$, $\gamma_{crit} = 1/240$.
* **Mutation (supercell rule — what the published runs actually used):** at **every** division the daughter inherits $T_{opt}' = T_{opt} + \delta$, $\delta \sim \mathcal{N}(0, \sigma_M^2)$, $\sigma_M = 0.1^\circ\text{C}$.
* **Mutation (cell-level rule — what the paper says real cells do):** *"every several hundred cell divisions one of the daughter cells experiences a mutation"* (§3.1), with a correspondingly **larger** step. $\sigma_M = 0.1^\circ\text{C}$ is explicitly described as *"a smaller standard deviation"* chosen so that a supercell emulates rarer, larger single-cell mutations. **These are two different models and must never be conflated** — see §4, Discovery B.
* **Detritus Remineralization:** $\tau_0 = 0.25\,\text{d}^{-1}$.

### 2.1 Complete parameter set (Beckmann Table 1)

| Parameter | Symbol | Value | Unit |
|---|---|---|---|
| Total mass concentration | $R$ | 5 | mmol N m$^{-3}$ |
| Nutrient half saturation | $k_N$ | 0.15 | mmol N m$^{-3}$ |
| Maximum doubling rate | $\mu_0/\ln 2$ | **1 — see §2.2** | doubl. day$^{-1}$ |
| Mortality rate | $\gamma_0$ | 0.1 | day$^{-1}$ |
| Remineralization rate | $\tau_0$ | 0.25 | day$^{-1}$ |
| Scale for thermal reaction norm | $\theta$ | **6** | $^\circ$C |
| Time step | $\Delta t$ | 3600 | s |
| Volume of the tank | $V$ | 1 | m$^3$ |
| Reference biomass | $b_0$ | $5\times10^{-10}$ | mmol N |
| Std. deviation of mutations | $\sigma_M$ | 0.1 | $^\circ$C |
| *(MCM)* max. exponential growth rate | $\mu_0$ | $\ln 2$ | day$^{-1}$ |
| *(MCM)* temperature width of genotypes | $\Delta T_{opt}$ | 0.1 | $^\circ$C |
| *(MCM)* genotype transfer factor | $\delta_{tr}$ | 1/3 | – |
| Scale for reaction norm asymmetry | $\Delta\theta$ | 4 | $^\circ$C |
| Amplitude for increasing $\mu_{max}$ | $\mu_E$ | 0.59 | doubl. day$^{-1}$ |
| Scale for increasing $\mu_{max}$ | $\Lambda$ | 15.8 | $^\circ$C |
| Threshold for resting phase | $F_{T_{crit}}$ | 0.2 | – |
| Resting stage growth | $\mu_{rest}$ | 0.01 | day$^{-1}$ |
| Resting stage mortality | $\gamma_{rest}$ | 0.01 | day$^{-1}$ |

$\theta = 6^\circ$C is independently confirmed by the paper's own Eppley result: $\theta^2/(2\Lambda) = 36/31.6 = 1.139 \approx 1.14^\circ$C. $k_N = 0.15$ is independently confirmed by $F_N^* = 0.074 \Rightarrow N^* = k_N F_N^*/(1-F_N^*) = 0.0120$.

The paper writes the MCM genotype transfer factor as $\delta$ (Table 1), the same glyph it uses for a mutation increment. We use $\delta_{tr}$ throughout to avoid the collision.

### 2.2 ⚠️ BLOCKING: an internal factor-of-2 discrepancy in the source paper

**Resolve this before writing `pnd_ibm.py`.** Table 1 prints the maximum doubling rate as $\mu_0/\ln 2 = 1$ doubl. day$^{-1}$ (and the MCM row agrees: $\mu_0 = \ln 2$ day$^{-1}$). That value does **not** reproduce the analytic equilibrium the paper states in §3.3.1.

At steady state, exponential growth balances mortality, so $F_T F_N = \gamma_0/\mu_0$; Eq. 20 (which assumes $F_T = 1$) gives $N^* = \gamma_0 k_N/(\mu_0 - \gamma_0)$:

| max doubling rate | $\mu_0$ (d$^{-1}$) | $F_N^*$ | $N^*$ | $P^*$ | $D^*$ |
|---|---|---|---|---|---|
| 1 /day (Table 1 as printed) | 0.693 | 0.144 | **0.0253** | 3.553 | 1.421 |
| 2 /day (implied) | 1.386 | 0.0721 | **0.0117** | **3.563** | **1.425** |
| **paper §3.3.1 states** | — | **0.074** | **0.012** | **3.563** | **1.425** |

Every published equilibrium value closes exactly at **2 doublings/day** and is off by a factor of two at the printed 1/day.

The ~7-day division time does **not** discriminate between them: in this renewal process the boundary condition is $\gamma_0 T_{div} = \ln 2$, giving $T_{div} = 6.93$ d under either value. $F_N$ is the discriminating quantity.

*Independent cross-check (biomass closure at 2 doubl/day):* the stationary biomass density is $n(b) \propto e^{-\gamma_0 (b-b_0)/g}$ on $[b_0, 2b_0]$, giving $\bar b = 1.443\,b_0$, hence $M = P^*/\bar b = 4.94\times10^9$ cells and growth flux $M g = 0.3564$ mmol d$^{-1}$, against loss $\gamma_0 P^* = 0.3563$ mmol d$^{-1}$. Closes to four figures.

**Action:** implement $\mu_0$ as a free parameter, run both values, adopt whichever reproduces Table 2's $s = 0.859^\circ$C, and report the discrepancy in the paper. Identifying a factor-of-two typo in a widely-cited baseline is a legitimate contribution of a reproduction study — but silently inheriting it would invalidate every downstream experiment.

### 2.3 Analytic verification targets (conditional on §2.2)

$P^* = 3.563$, $N^* = 0.012$, $D^* = 1.425$ mmol m$^{-3}$; $F_N^* = 0.074$; population growth rate $0.1$ d$^{-1}$; $T_{div} \approx 6.93$ d.

These are closed-form and a sharper Figure 1 check than matching a stochastic mean. **They are only valid under the $\mu_0$ resolution of §2.2** — they are the evidence for it, so they cannot also serve as an independent test of it.

### 2.4 The Seven Canonical Reproduction Benchmarks (Beckmann Table 2)

All values are the **MuSe-IBM** column of Table 2 unless noted.

| # | Experiment | $\bar T_{opt}$ | $s$ | Additional targets |
|---|---|---|---|---|
| 1 | Constant $15^\circ$C | 15.00 | 0.859 | converges from uniform $[5,25]$ in ~3 yr; ~20 coexisting generations after 4 yr |
| 2 | Sudden shift $15\to20^\circ$C | 20.00 | 0.858 | $\tau = \mathbf{465.5}$ d (IBM); full adjustment **7–8 yr / 350–400 generations** |
| 3 | Seasonal sinusoid $\pm5^\circ$C | 14.10 | 1.071 | best-fit amplitude **0.92**$^\circ$C (IBM); ~20% of forcing; 3-month lag |
| 4 | Diurnal square wave $10\leftrightarrow20^\circ$C | 15.02 (full) | 5.636 | **bimodal**: lower **11.09** ($s=1.040$), upper **18.92** ($s=1.039$); split takes ~4 yr / 200–220 gen |
| 5 | Seasonal resting phase, $F_{T_{crit}}=0.2$ | 11.43 | 2.010 | **trimodal** near 10 / 15 / 20$^\circ$C; ~120 coexisting generations and still increasing |
| 6 | Asymmetric reaction norm, $\Delta\theta=4^\circ$C | 15.56 | 0.854 | positively skewed distribution; $\bar T_{opt} > T_{env}=15.0$ |
| 7 | Eppley scaling, $\mu_E=0.59$, $\Lambda=15.8$ | 16.14 | 0.861 | analytic $T_{opt}^* = T_{env} + \theta^2/(2\Lambda) = 15.0 + 1.14$ |

> **Correction applied (r2):** benchmark 2 previously carried $\tau \approx 458.4$ d. That is the **MuSe-MCM** value. §4.3 reads *"(458.4 vs 465.5 days for the IBM)"* — the parenthetical attaches to the second number. The same construction fixes the seasonal amplitude: *"(0.89 vs. 0.92 °C for the IBM)"*, so 0.92 is our IBM target.

---

## 3. The Scalability Frontier: Where the Demonstrated Equivalence Ends

### 3.1 First, correct the supercell arithmetic

Beckmann et al. did not choose $10^6$ as a target. The tank's mass balance **forces** the cell count: $P^* = 3.563$ mmol N m$^{-3}$ at $\bar b = 1.443\,b_0$ gives $\approx 4.9\times10^9$ real cells, which the paper rounds to $10^{10}$. Grouping $10^4$ cells per agent then *yields* $\approx10^6$ agents:

> *"typical cell concentrations in nature prohibit the use of one model variable per cell; therefore, one model variable combines $10^4$ identical cells into one 'agent' (or 'supercell')... The model then tracks about $10^6$ independent agents, representing $10^{10}$ cells in total."* (§3.1)

**$M$ is a discretization parameter, not a population size.** Appendix B makes this explicit — Fig. B.10 compares $10^3$ agents $\times\,10^7$ cells each against $10^6$ agents $\times\,10^4$ cells each: *the same $10^{10}$ cells at different resolution*. (The paper itself blurs this, writing *"carried out with $10^6$ individuals"* in Appendix B; we should not inherit the blur.)

Two consequences bind everything below:

1. **Sweeping $M$ measures Monte Carlo convergence, not genetic drift.** The biological population never changes size.
2. **Beckmann already ran $10^7$.** Appendix B: *"$10^4$ or $10^5$ agents do not suffice, unless time- or ensemble averaging is done. All experiments in this study are carried out with $10^6$ individuals, which do not really differ from a 10 time higher resolution case."* Fig. B.10 caption: *"The differences between $10^6$ and $10^7$ agents are hardly visible."* Any figure whose payload is "the distribution stabilizes by $10^6$" re-derives a published negative result.

### 3.2 The headline argument, and the objection it must survive

A referee will write: **"Why not just port the MCM to the GPU?"** The paper has already told them the two models agree and that the MCM is 100× cheaper. If we have no answer, the paper fails.

The answer is dimensionality, and it is the **only** one of our five frontiers that a GPU cannot hand to the MCM as well. A GPU buys the MCM a constant factor; it cannot beat $O(B^D)$ at $D=3$. **Discovery A below is therefore the headline of Part 1; the other four are supporting or deferred to Part 2.**

```
                    THE SCALABILITY FRONTIER (r2 hierarchy)

        ┌──────────────────────────────────────────────────────────┐
        │  DISCOVERY A  —  HEADLINE, PART 1, FIGURE 4              │
        │  Multi-Trait Curse of Dimensionality                     │
        │  MCM O(B^D) collapse  vs.  JAX-IBM O(D·M) linearity      │
        │  >> the one argument a GPU-ported MCM cannot answer <<   │
        └───────────────────────────┬──────────────────────────────┘
                                    │
      ┌─────────────────────────────┼─────────────────────────────┐
      ▼                             ▼                             ▼
┌─────────────────┐   ┌──────────────────────────┐   ┌─────────────────────┐
│  DISCOVERY B    │   │  DISCOVERY C             │   │  DISCOVERY D / E    │
│  Single-cell    │   │  Evolutionary rescue &   │   │  Branching under    │
│  mutation       │   │  the demographic         │   │  red noise (D);     │
│  fixation       │   │  threshold  (REQUIRES    │   │  dormancy coalescent│
│  (Part 1 text,  │   │  REDESIGN — see §4)      │   │  genealogies (E)    │
│   Part 2 figure)│   │  PART 2, FIGURE 3        │   │  PART 2             │
└─────────────────┘   └──────────────────────────┘   └─────────────────────┘
```

---

## 4. The Five Frontiers

### Discovery A (HEADLINE): Overcoming the Curse of Dimensionality

* **The structural limit of trait diffusion (MCM):**
  - 1 trait ($T_{opt}$, 200 bins) $\implies J = 200$ compartments.
  - 2 traits ($T_{opt} \times k_N$) $\implies J = 40{,}000$.
  - 3 traits ($T_{opt} \times k_N \times$ cell size) $\implies J = \mathbf{8\times10^6}$ compartments **per grid cell**.

* **State the cost honestly — the memory claim must be the real one.** An $8\times10^6$ state vector is only 64 MB, and the trait-diffusion operator is **not** a dense matrix: for $D$ traits with independent mutation it is a sum of tridiagonal operators, i.e. a $(2D{+}1)$-point stencil — $\approx450$ MB of nonzeros in 3-D, and in practice never assembled at all. The r1 claim of a *">64 GB diffusion tensor"* matches nothing (a dense operator would be ~512 TB) and would be shot down immediately.

* **The cost that is actually fatal — the 3-D multiplier:** $8\times10^6$ genotypes $\times \sim10^6$ wet grid cells $= 8\times10^{12}$ state values $\approx$ **64 TB**, with per-timestep flops scaling the same way. *That* is why the MCM cannot carry three traits into an ocean model, and no GPU port changes it.

* **A second, compounding constraint (Beckmann Eq. 26).** The genotype transfer factor is $\delta_{tr} = \sigma_M^2/(3\,\Delta T_{opt}^2)$, and §4.2 warns that $\delta_{tr} > 0.5$ makes the self-growth terms $\mu_j(1-2\delta_{tr})$ **negative** — unphysical. Hence $\Delta T_{opt} \ge \sigma_M/\sqrt{1.5} = 0.816\,\sigma_M$: **the trait grid is pinned to the mutation width.**

  This is *not* a tail-resolution barrier — at $\sigma_M = 0.1$ it permits $\Delta T_{opt} = 0.082^\circ$C, i.e. 10.5 bins per distribution SD, which is ample. Its real bite is dimensional: $J \propto \sigma_M^{-1}$ per trait and $\sigma_M^{-D}$ overall. At $\sigma_M = 0.01^\circ$C over a 20$^\circ$C range, $J = 2{,}449$ per trait and $J^3 = \mathbf{1.5\times10^{10}}$ compartments. Smaller mutations — the regime that *promotes* branching — make the MCM superlinearly worse.

* **The JAX-IBM counterpart, stated fairly.** IBM memory is $\propto D \times M$: four continuous traits for $10^6$ agents is $4 \times 8\,\text{MB} = 32$ MB (fp64), or 16 MB at fp32. **But the IBM is not free in 3-D either:** it needs $\sim10^2$–$10^3$ agents per grid cell $\times \sim10^6$ cells $= 10^8$–$10^9$ agents. That is large but tractable on a GPU, and — this is the whole point — **it is independent of $D$.** Adding a fourth trait costs one more array, not another factor of $B$. Presenting the IBM as costless in 3-D would be an apples-to-oranges comparison and would hand the referee an easy rebuttal; presenting it as $D$-independent wins the argument honestly.

### Discovery B: Single-Cell Mutation and True Fixation Statistics

* **The limit in the published model:** grouping $10^4$ cells into one agent means the IBM's own granularity floor is $10^4$ cells. A single mutant cell cannot be represented. The supercell mutates as a block, bypassing the stochastic hazard zone in which a lone beneficial mutant is lost to accidental death. Under Haldane's branching-process result $P_{fix} \approx 2s$, a mutant with $s = 0.01$ is lost ~98% of the time — **state the $s$ explicitly**; "over 98% are lost" is a statement about $s=0.01$, not a general fact. Note too that with nutrient feedback closing the mass balance, selection here is density-dependent, so $2s$ is a heuristic reference rather than an exact prediction — which is itself worth measuring.

* **Mandatory kernel rescaling.** One cannot set 1 agent = 1 cell and keep $\sigma_M = 0.1^\circ$C: that inflates mutational input by $\sim\sqrt{p^{-1}}$. Hold the trait-diffusion coefficient fixed, $p\,\sigma_{single}^2 = \sigma_M^2$, giving $\sigma_{single} = \sigma_M/\sqrt{p} \approx 2.2^\circ$C at $p = 1/500$. Also note the implied geometry: 1 agent = 1 cell at $M = 10^7$ means $V \approx 2\,\text{L}$ ($2,000\,\text{cm}^3$ or $2\times 10^{-3}\,\text{m}^3$), not $1\,\text{m}^3$. State the volume rescaling or the mass balance is silently broken.

* **⚠️ Appendix A is a headwind — address it directly.** Beckmann already showed that swapping the Gaussian mutation kernel for a uniform one yields *the same* emergent distribution once the SDs are matched ($\sigma_M \times \sqrt{3}$). **Only the second moment of the kernel affects the steady-state distribution.** Discovery B therefore cannot claim a different distribution from single-cell mutation — the rescaling above guarantees the distributions agree. The claim must be confined to quantities Appendix A never examined: **empirical fixation probability, waiting time $\tau_{adapt}$, and rare-event/large-jump statistics** (the kernels match in variance but differ in kurtosis). Say this explicitly, or a referee will cite Appendix A against us.

### Discovery C: Evolutionary Rescue — REQUIRES REDESIGN

* **The error in the r1 formulation.** It treated agent count $M$ as $N_e$ and proposed sweeping $M \in [10^3, 10^7]$ to find a critical threshold $M_c$. Per §3.1, the biological population is fixed at $\approx5\times10^9$ cells regardless of $M$; the sweep measures Monte Carlo noise, not drift. **There is no $M_c$ in this configuration.**

* **Also corrected:** the claim that at $M \le 10^4$ the tails beyond $3\sigma$ hold "fewer than 3 agents" is wrong. With $s = 0.859$, $M = 10^4$ gives **13.5 agents per tail (27 two-tailed)**. Fewer than 3 requires $3.43\sigma$, or $M \approx 10^3$.

* **Redesign.** To study rescue, change the **biology**, not the discretization: shrink $V$, lower $R$, or impose an explicit demographic bottleneck — and state which. Then $N_e$ is a modelled quantity and $M$ is held at convergence.

* **Compute budget.** The proposed `jax.vmap` over 1,000 trajectories $\times\,10^7$ agents is $10^{10}$ agent-states = **40 GB per fp32 array**, before biomass, alive-mask, and lineage IDs. This contradicts Discovery A's own memory argument. Chunk the ensemble and state the budget.

* **The strongest available motivation is our own** — see §6.

### Discovery D: Sympatric Branching Under Continuous Environmental Noise

* Beckmann et al. (Exp. 4) obtained bimodality only under a zero-noise diurnal square wave, and needed ~4 years (200–220 generations) for the split. Whether the branch survives realistic continuous forcing (e.g. Ornstein–Uhlenbeck red noise) is untested, and is a legitimate open question.
* Note which way the structural difference cuts: a deterministic compartment model **cannot** lose a morph to demographic accident, because its compartments never reach zero. That is the next point.

### Discovery E: Dormancy, Genealogies — and the Continuum Artifact

* **Genealogies.** JAX tracks integer lineage tensors cheaply, enabling reconstruction of coalescent trees and measurement of how resting stages inflate $N_e$. A compartment model carries no ancestry at all, so this is a **capability gap** rather than an accuracy claim — the cleanest kind of argument, and the hardest to rebut.

* **The continuum ("atto-fox") artifact — real, but narrower than r1 claimed.** The MCM is deterministic, so a compartment holding a sub-single-cell biomass still grows, competes, and re-seeds. Quantified against $P^* = 3.563$ mmol m$^{-3}$ with one cell $= 5\times10^{-10}$ mmol:

  | compartment | distance | cell-equivalents held |
  |---|---|---|
  | $T_{opt} = 19^\circ$C (a $+4^\circ$C shock) | $4.7\sigma$ | $1.4\times10^{5}$ — **entirely physical** |
  | $T_{opt} = 10^\circ$C | $5.8\sigma$ | $3.1\times10^{2}$ |
  | $T_{opt} = 5^\circ$C | $11.6\sigma$ | $2.7\times10^{-20}$ — **artifact** |

  The pathology appears only beyond $\sim8$–$9\sigma$. A plain $+4^\circ$C shock will **not** expose it. Demonstrating it requires an engineered scenario — a deep cold refuge, prolonged competitive exclusion, or an explicit extinction threshold imposed on the MCM. Keep the argument; state the $\sigma$-distance condition; do not lead with it.

* **Symmetry worth noting:** the supercell IBM quantizes at $10^4$ cells and the MCM quantizes at zero. **Neither represents a single cell.** Only 1-agent-=-1-cell does, which is Discovery B.

---

## 5. Paper Structure & Publication Strategy

### 5.1 Working Title

> **Breaking the Scalability Barrier in Individual-Based Phytoplankton Modelling: From Trait-Diffusion Approximations to GPU-Accelerated JAX-IBM**

### 5.2 Scope: this is two papers, and the split must be explicit

**Part 1 (reproduction + the dimensionality argument):** Figures 1, 2, 4.
**Part 2 (new eco-evolutionary science):** Discoveries C, D, E.

* **Figure 1 (Reproduction & Verification):** the seven canonical experiments against Beckmann Table 2, plus the analytic equilibrium of §2.3, plus the $\mu_0$ resolution of §2.2. Claim **agreement within Monte Carlo error over a seeded ensemble, with a stated tolerance and confidence interval** — not *"100% numerical and statistical fidelity"*, which is not a meaningful claim about a stochastic model.
* **Figure 2 (Computational Scaling):** the **CPU-vs-GPU timing panel is novel and should stay** — the paper reports no timings anywhere, so we will need our own CPU reference implementation as the baseline. The **variance-vs-$M$ panel needs a new payload**, since convergence by $10^6$ is already published (Fig. B.10).
* **Figure 4 (Breaking the Multi-Trait Curse):** promoted to the paper's centrepiece — $O(B^D)$ vs $O(D\cdot M)$ with 2-D and 3-D trait trade-off manifolds, the 3-D grid multiplier, the Eq. 26 $\sigma_M^{-D}$ amplification, and the honest IBM-in-3-D accounting.
* **Figure 3 ($M_c$ / evolutionary rescue):** deferred to Part 2 pending the redesign in Discovery C.

Note that under the r1 plan Discoveries B, D and E had no figure at all — three of five. The split above resolves that.

### 5.3 Venues

1. ***Ecological Modelling*** / ***Environmental Modelling & Software*** — primary target for Part 1.
2. ***PLOS Computational Biology*** — alternative if the multi-trait result is strong enough to carry a broader audience.
3. ***JOSS*** — **removed from the Part 1 target list.** JOSS reviews the *software*, not the science; its ~1,000-word format has no room for Figures 1–4 or the scientific argument, and "4–6 weeks" is optimistic. Submit to JOSS separately once the package is public, documented and tested. The two are sequential and complementary, not alternatives.

---

## 6. Motivation We Already Own

The strongest available evidence that stochastic tail composition determines outcomes is not an abstract $M_c$ sweep — it is our own Nodularia work (see `Readme.txt`). A memory-layout shift in an input file changed the Fortran RNG stream, which woke a different set of akinetes with a different $T_{opt}$ composition, which cascaded into a **~1$^\circ$C shift in predicted $T_{opt}$**. The fix was to assume standing genetic variation in both germinates and akinetes, plus a large akinete SGV pool; the same work found that akinete SGV is decisive for bloom success and that TPC parameters matter alongside $T_{opt}$ evolution.

That is a lived, reproducible demonstration — with real-model provenance — that rare-variant composition in the tails drives system-level outcomes. It motivates Discoveries B and C far better than a synthetic threshold experiment, and it should be worked into Part 2's introduction.

---

## 7. Correction Log (r1 → r2)

| # | Correction |
|---|---|
| 1 | **Added §2.2:** factor-of-2 discrepancy between Table 1's max doubling rate and the paper's own equilibrium. Blocking. |
| 2 | Benchmark 2: $\tau = 458.4$ d (MCM) $\to$ **465.5 d** (IBM); added 7–8 yr full adjustment. |
| 3 | Added $\theta = 6^\circ$C, $k_N = 0.15$, $\Delta t = 3600$ s, $V = 1$ m$^3$ and the full Table 1 (§2.1). |
| 4 | Separated the supercell mutation rule from the cell-level rule; added the $\sigma_{single} = \sigma_M/\sqrt{p}$ rescaling. |
| 5 | Added the Appendix A headwind: kernel shape is irrelevant to the steady-state distribution; Discovery B restricted to fixation/waiting-time/rare-event statistics. |
| 6 | Supercell arithmetic corrected: $10^6$ **agents** $= 10^{10}$ cells, forced by mass balance, not chosen. |
| 7 | **$M$ is a discretization parameter, not $N_e$** — Discovery C flagged as requiring redesign. |
| 8 | $3\sigma$ tail count: "fewer than 3 agents" $\to$ 13.5 per tail at $M = 10^4$. |
| 9 | Deleted *">64 GB diffusion tensor"*; replaced with the 3-D grid multiplier (~64 TB) and the sparse-stencil reality. |
| 10 | Eq. 26 constraint reframed: not a tail-resolution floor (10.5 bins/SD), but a $\sigma_M^{-D}$ amplifier of the curse of dimensionality. |
| 11 | Atto-fox argument quantified and demoted: physical at $4.7\sigma$, artifactual only beyond $\sim8$–$9\sigma$. |
| 12 | Added honest IBM-in-3-D accounting ($10^8$–$10^9$ agents; advantage is $D$-independence, not cheapness). |
| 13 | Added the "why not GPU-port the MCM?" section; promoted dimensionality to headline (Discovery A). |
| 14 | §1 now leads with the "differences are negligible" and "essentially identical" quotes rather than omitting them. |
| 15 | Fortran/OpenMP claim re-attributed; removed the unsupported "too expensive to run" premise. |
| 16 | *"the only mathematically viable vehicle"* $\to$ "most practical", with named alternatives. |
| 17 | *"100% numerical and statistical fidelity"* $\to$ agreement within Monte Carlo error, stated tolerance. |
| 18 | Figure 2 split: timing panel novel and retained; variance panel needs a new payload (Fig. B.10 precedent). |
| 19 | Added Table 2 values previously missing (full-range square wave, resting phase, seasonal). |
| 20 | Part 1 / Part 2 split made explicit; JOSS removed from Part 1 targets. |
| 21 | Added the `vmap` memory budget (40 GB/array) and the $V \approx 2\,\text{L}$ ($2,000\,\text{cm}^3$) implication of 1 agent = 1 cell. |
| 22 | Added §6: the Nodularia RNG/akinete-SGV incident as primary motivation. |

---

## 8. Open Items & Next Steps

1. **Resolve §2.2 first.** Implement $\mu_0$ as a free parameter; run 1 and 2 doubl/day; adopt whichever reproduces $s = 0.859$. Nothing else proceeds until this is settled.
2. Implement the clean barebone PND model (`pnd_ibm.py`) in JAX against the §2.1 table.
3. Verify against the §2.3 analytic equilibrium before any stochastic benchmark.
4. Build the automated reproduction harness for the seven canonical experiments (§2.4), seeded, with ensemble CIs.
5. Write a CPU reference implementation — there is no published timing baseline to cite.
6. Formulate the scaling experiments for Figures 1, 2 and 4; defer Figure 3 pending the Discovery C redesign.
7. **Open question:** does the emergent distribution have Gaussian tails? The mutation-selection balance here sits in the diffusion regime ($\sigma_M \ll s$), which argues yes, but the tail-count arithmetic in Discovery C assumes it. Measure it rather than assume it.
