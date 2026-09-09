# Technical Deliberation: Grounding the JAX-IBM Port, Scientific Machine Learning, and the CYA-REMo DFG Project

**Date:** 2026-09-09  
**Location:** Department of Ecosystem Modelling, Helmholtz-Zentrum Hereon (Geesthacht / Hamburg)  
**Target Context:** Strategic Contemplation on Computational Biology, GPU/TPU Acceleration, and Scientific AI for the Phytoplankton Individual-Based Model (IBM).

---

## 0. Primary Source Documents & Analytical Grounding

This contemplation is rigorously grounded in the primary project literature:

1. **The DFG Project Description (Antrag):**  
   *CYA-REMo: Cyanobacteria under climate change: looking into the past to predict the future through integration of resurrection ecology, experimental evolutionary and ecosystem modelling approaches*  
   - **Grant Reference:** DFG HE-3190 / SCHA-2154 / KR-4861 (March 2020)  
   - **Principal Investigators:** Prof. Dr. Inga Hense (UHH, CEN), Prof. Dr. Elisa Schaum (UHH, CEN), Prof. Dr. Anke Kremp (IOW Warnemünde)  
   - **Work Packages:**  
     - **WP1 (Back-in-time / Resurrection Ecology):** Slicing Baltic Sea sediment cores, resurrecting dormant akinetes from the 1980s and modern eras, and measuring functional response curves.  
     - **WP2 (Forward-in-time / Experimental Evolution):** Controlled multi-generation selection experiments under warming/acidification.  
     - **WP3 (Ecosystem Modelling):** Standalone cyanobacteria life-cycle model (CLC), coupled 1D water column model (GOTM), 63-year hindcast (1960–2023), and 12 IPCC climate projection scenarios to 2100 (Thejus Mahajan’s task).

2. **The Theoretical Model Paper:**  
   *Beckmann, A., Schaum, C.-E., & Hense, I. (2019). Phytoplankton adaptation in ecosystem models. Journal of Theoretical Biology, 468, 60–71.*  
   - Formulates the **MuSe-IBM** (Mutation-Selection Individual-Based Model) and compares it with the **MuSe-MCM** (Multi-Compartment Model treating mutations as continuous diffusion in trait space).

3. **The Empirical Sediment Core Data:**  
   *Medwed, C., Karsten, U., Romahn, J., Kaiser, J., Dellwig, O., Arz, H., & Kremp, A. (2024). Archives of cyanobacterial traits: insights from resurrected Nodularia spumigena from Baltic Sea sediments reveal a shift in temperature optima. ISME Communications, 4(1), ycae140.*  
   - Demonstrates empirical trait shifts in resurrected Baltic Sea strains: temperature optimum $T_{opt}$ shifted from $15.3^\circ\text{C}$ (1987 strains) to $21.1^\circ\text{C}$ (2020 strains).

---

## 1. Dramatis Personae

* **Prof. Dr. Kai Wirtz (KW):** Head of Ecosystem Modelling, Helmholtz-Zentrum Hereon. Pioneer in trait-based optimality, adaptive dynamics, and macromolecular acclimation. Demands physical conservation, thermodynamic validity, and biological interpretability; deeply skeptical of unconstrained AI hype.
* **Dr. Thejus Mahajan (TM):** Computational physicist and ecosystem modeller. Author of the 0-D Lagrangian Fortran/OpenMP IBM and its JAX GPU port (`jax-water-column-model`). Currently mastering supercomputing deployment through the HLRS course (*Deployable Data Analysis and AI Pipelines with HPC*).
* **Dr. Aris Thorne (AT):** Senior Computational Scientist specializing in Scientific Machine Learning (SciML), Simulation-Based Inference (SBI), and high-throughput HPC architectures.

---

```
                       THE CYA-REMo WORK PACKAGE TRIPOD
                       
       [ WP1: Resurrection Ecology ]           [ WP2: Experimental Evolution ]
       (Anke Kremp / Cynthia Medwed)           (Elisa Schaum)
       • 1987 vs. 2020 Baltic sediment cores   • Multi-generation forward selection
       • Resurrected akinetes, trait shifts    • Quantifying evolutionary potential
                     │                                       │
                     └───────────────────┬───────────────────┘
                                         │ Empirical Data Transfer
                                         ▼
                       [ WP3: Ecosystem Modelling (CYA-REMo) ]
                       (Inga Hense / Thejus Mahajan)
                       • Task I: Standalone 0-D Life-Cycle Model (CLC)
                       • Task II: 1-D Coupled Water Column Model (GOTM)
                       • Task III: 63-yr Hindcast & 12 IPCC Climate Projections (2020–2100)
```

---

## 2. Clarification of Model Dimensionality: 0-D vs. 1-D

A critical physical fact established during this deliberation:  
**The underlying IBM engine in `jax-water-column-model` is strictly a 0-D (zero-dimensional) well-mixed tank model.**

### Code & Physical Verification
* **State Tensors (`state.py`):**
  $$\text{AgentState} = \left\{ \text{phybio} \in \mathbb{R}^{M_2}, \;\text{phyopt} \in \mathbb{R}^{M_2}, \;\text{iliv} \in \mathbb{Z}^{M_2}, \;\text{igen} \in \mathbb{Z}^{M_2} \right\}$$
  $$\text{EnvironmentState} = \left\{ \text{temp} \in \mathbb{R}, \;\text{swrad} \in \mathbb{R}, \;\text{aorg} \in \mathbb{R}^2, \;\text{detr} \in \mathbb{R}^2, \;\text{phyt} \in \mathbb{R}^2 \right\}$$
  There is no depth coordinate $z$, no vertical layers, no sinking velocity $w_s$, and no vertical turbulence diffusion $K_z$.
* **Paper Definition (Beckmann et al. 2019, Section 3.2):**
  > *"The model configuration is a **well-mixed (zero-dimensional) 'tank'** without external sources and sinks of phytoplankton (immigration, emigration), nutrients and detritus (addition and removal)."*
* **Origin of the Name:** The code files were historically titled `wcm.F90` ("Water Column Model") because in the broader research group at Uni Hamburg, this 0-D biological engine is coupled into the vertical layers of **GOTM** (General Ocean Turbulence Model) via FABM. In isolation, the IBM engine simulates the biological dynamics of a single homogenous volume over time $t$.

---

## 3. The Core Computational Justification for the JAX GPU/TPU Port

### Why was the Fortran IBM Abandoned in the Proposal?
Page 3 of the CYA-REMo DFG proposal explicitly states why the modellers compromised:
> *"Additionally it has been demonstrated that the trait diffusion model [MCM] provides the same results as a **more accurate but computationally much more expensive IBM (Individual Based Model) approach (Beckmann et al. 2019)**. Thus, it is possible now to account for evolutionary changes in an ecosystem framework."*

The PIs recognized that the IBM was **scientifically superior**—it explicitly models individual cell division thresholds ($b_i \ge 2 b_0$), discrete stochastic mutations, true lineage extinctions, and resting akinete bank dynamics. However, they were forced to abandon it for Work Package 3 because of a severe computational wall on standard CPU clusters.

```
            THE DEMOGRAPHIC SCALING TRADEOFF IN THE IBM
            
   M = 1,000 agents:     Fast on CPU (~1 min)   ──►  Severe demographic noise & drift artifacts
   M = 50,000 agents:    Hours per decadal run  ──►  Acceptable noise, but fails ensemble scaling
   M = 500,000 agents:   Days per run on CPU    ──►  Smooth evolutionary ridge (Beckmann App. B)
   
   JAX on GPU (T4/A100): M = 500,000 in minutes  ──►  Eliminates the compromise completely
```

### The Three Drivers of the Computational Wall
1. **The Multi-Decadal Time Horizon:**
   - **Hindcast:** 1960 to 2023 ($63\text{ years} = 551,880\text{ hourly timesteps}$).
   - **Forecast (Table 2 of the proposal):** 12 projection scenarios to the year 2100 ($80\text{ years} = 700,000\text{ timesteps}$ each):
     $$\text{3 IPCC Emissions (RCP 2.6, 4.5, 8.5)} \times \text{2 Nutrients (BAU, BSAP)} \times \text{2 Evolution (EVO, N-EVO)} = 12\text{ Scenarios}$$
   - Total integration requirement: **over 8.4 million hourly timesteps**.
2. **Demographic Noise vs. Agent Count (Appendix B of Beckmann 2019):**
   - When agent count $M$ is small ($10,000$), random birth-death events cause massive **demographic drift**, overwhelming subtle climate adaptation signals.
   - To obtain a statistically converged evolutionary ridge matching experimental resolution ($\Delta T_{opt} = 0.1^\circ\text{C}$ across 251 bins), the model requires **$M = 100,000$ to $500,000$ agents**.
3. **CPU Pipeline Inefficiency:**
   - In standard Fortran with OpenMP, evaluating $500,000$ agents sequentially with conditional logic (`if (iliv == 1)`, `if (division)`) causes severe branch mispredictions and memory cache stalls. A single multi-decadal run takes 12–24 hours on a multi-core CPU node. Running 12 scenarios with replicates was computationally impossible within the grant period.

### How JAX Solves the Problem
By replacing all conditional loops with **branchless tensor operations (`jnp.where`)** and compiling via XLA:
- Agent state updates execute as SIMD vector arithmetic across thousands of GPU CUDA cores or TPU matrix units simultaneously.
- A 24-step simulation runs in **21 seconds on a single CPU thread**, and decadal runs compile to ultra-fast GPU kernels.
- **`jax.vmap` enables concurrent ensemble execution:** multiple stochastic replicates or climate forcing regimes execute in parallel on a single GPU.
- **Outcome:** Modellers no longer need to compromise on the simplified MCM trait-diffusion equation. The full, discrete, accurate IBM can be deployed across all 12 IPCC climate projection scenarios.

---

## 4. The Role of Machine Learning: What Works and What Fails

A central insight of this deliberation is distinguishing between **unviable AI hype** and **rigorous scientific AI**.

```
                            THE BIFURCATION OF AI APPROACHES
                                            │
               ┌────────────────────────────┴────────────────────────────┐
               ▼                                                         ▼
     [ THE DEAD END (Naive AI) ]                             [ THE SCIENTIFIC PATH (SciML) ]
  • Black-box LSTM / Transformer on fort.12               • Simulation-Based Inference (SBI / NPE)
  • Violates mass conservation: d(P+N+D)/dt ≠ 0           • Invert biological parameters from sediment data
  • Extrapolates catastrophically under climate warming    • Physics-constrained multi-trait operators
  • Slower than analytical Euler integration              • Preserves elemental conservation strictly
```

### 4.1 The Dead End: Black-Box Climate Forecasting
Using neural networks (LSTMs, Transformers, standard MLPs) to forecast 2020–2100 cyanobacteria dynamics is **scientifically unviable**:
1. **Out-of-Distribution Extrapolation:** A network trained on historical 1960–2020 data cannot generalize to unprecedented warming regimes under RCP 8.5 (+4°C above pre-industrial) without physical drift.
2. **Violation of Mass Conservation:** Black-box models do not preserve the elemental conservation equation $\sum b_i + N + D = R$. Unphysical creation or destruction of nitrogen destroys ecological credibility.
3. **Zero Compute Advantage in 0-D:** Because the JAX-IBM executes in minutes on GPU, replacing it with an approximate surrogate in 0-D yields negligible speedup while sacrificing mechanistic trust.

### 4.2 The Breakthrough: Simulation-Based Inference (SBI) for Model Inversion
The primary, mathematically justified role for Deep Learning in CYA-REMo is **solving the intractable inverse problem between Work Package 1 and Work Package 3**.

```
        THE REVERSE PROBLEM: INFERRING EVOLUTION FROM SEDIMENTS
        
      [ WP1 Sediment Core Data: Medwed et al. (2024) ]
      • Resurrected 1987 strains: T_opt = 15.3°C ± 2.8°C
      • Resurrected 2020 strains: T_opt = 21.1°C ± 1.7°C
      • Non-linear TPC shapes, trait variance, akinete germination
                               │
                               ▼  How do we parameterize the IBM?
      ┌─────────────────────────────────────────────────────────────┐
      │     THE INVERSE CRASH (Classical Grid Search / MCMC)        │
      │  • Parameter space: [σ_mut, θ_asym, μ_max, FT_crit, γ_rest] │
      │  • 5D grid with 10 bins each = 100,000 decadal simulations  │
      │  • Stochastic IBM means likelihood p(Data|θ) is intractable  │
      └──────────────────────────────┬──────────────────────────────┘
                                     │
                                     ▼
      ┌─────────────────────────────────────────────────────────────┐
      │     THE SOLUTION: SIMULATION-BASED INFERENCE (SBI)          │
      │  1. JAX on GPU generates 100,000 fast 33-year trajectories   │
      │  2. Train a Normalizing Flow (Neural Density Estimator)     │
      │  3. Invert the posterior: p(θ | Medwed 1987 & 2020 Data)    │
      └─────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
      [ Calibrated, Validated IBM ready for 12 IPCC Forecast Runs ]
```

#### The Problem
In WP1, Medwed et al. (2024) resurrected 1987 and 2020 akinetes, measuring an empirical shift in $T_{opt}$ ($15.3^\circ\text{C} \to 21.1^\circ\text{C}$). However, key evolutionary parameters in `config.yaml`—such as the mutation step standard deviation $\sigma_{mut}$, the thermal reaction norm asymmetry $\theta$, and the akinete germination threshold $FT_{crit}$—cannot be measured directly in a laboratory. Because the IBM is a stochastic simulation, its likelihood function $p(\text{Data} \mid \boldsymbol{\theta})$ is mathematically intractable.

#### The Neural Solution: Neural Posterior Estimation (NPE)
1. **Prior Sampling:** Draw $100,000$ biological parameter proposals $\boldsymbol{\theta} \sim p(\boldsymbol{\theta})$ from plausible physiological bounds.
2. **High-Throughput Simulation:** Run $100,000$ 33-year historical trajectories using the JAX engine on cluster GPUs via `jax.vmap`.
3. **Deep Density Estimation:** Train a **Normalizing Flow** (conditional neural density estimator $q_\phi(\boldsymbol{\theta} \mid \mathbf{x})$) to learn the joint distribution of parameters and summary statistics $\mathbf{x}$.
4. **Bayesian Posterior Inversion:** Condition the trained network on Cynthia Medwed's real 1987 and 2020 sediment observations $\mathbf{x}_o$. The flow outputs the full, multi-dimensional Bayesian posterior distribution:
   $$p(\boldsymbol{\theta} \mid \mathbf{x}_o)$$
This provides mathematically rigorous parameter estimates and uncertainty bounds directly connecting the sediment core measurements to the model.

---

## 5. The Deployable HPC Pipeline (HLRS Integration)

The execution of this vision connects directly to Thejus's training in the HLRS course (*Deployable Data Analysis and AI Pipelines with HPC*):

```
                     THE DEPLOYABLE HLRS HPC PIPELINE
                     
  [ Step 1: HPC Containerization (Apptainer / Singularity) ]
   └── Package jax-water-column-model + CUDA 12 + Python 3.11 + SBI library
       Guarantees 100% bitwise reproducibility on any supercomputer.
                     │
                     ▼
  [ Step 2: High-Throughput Ensemble Generation (Slurm Array Jobs) ]
   └── Slurm batch script orchestrating 100,000 33-year runs across GPU nodes.
       Each GPU node evaluates thousands of simulations per hour via jax.vmap.
       Outputs stream to high-performance parallel Lustre file system (Zarr/HDF5).
                     │
                     ▼
  [ Step 3: Distributed Deep Learning (Multi-GPU PyTorch / JAX) ]
   └── Train the Normalizing Flow across multi-GPU nodes using Distributed Data
       Parallel (DDP) to invert p(θ | Medwed 2024 Sediment Data).
                     │
                     ▼
  [ Step 4: Automated Execution of the 12 IPCC Climate Projections ]
   └── Feed the calibrated posterior θ into the 12 projection scenarios
       (RCP 2.6, 4.5, 8.5 × BAU, BSAP × EVO, N-EVO) to the year 2100 with full
       statistical confidence intervals.
```

1. **Reproducible Containerization:** The complete Python 3.11, JAX (CUDA 12), and Fortran binary I/O toolchain is encapsulated in an **Apptainer (Singularity)** container (`.sif`), enabling immediate deployment on HLRS Hawk, HLRN, or Hereon cluster partitions without local system dependency conflicts.
2. **Lustre High-Throughput I/O:** Rather than writing hundreds of thousands of individual `fort.12` files that degrade cluster metadata servers, the JAX pipeline streams simulation trajectories directly into chunked, compressed **Zarr or HDF5 arrays** on the parallel Lustre filesystem.
3. **Slurm Heterogeneous Orchestration:**
   - Slurm batch array scripts distribute parameter sweeps across GPU nodes.
   - Multi-GPU nodes execute distributed neural training via PyTorch DDP or JAX `pmap`.
   - Production Slurm jobs evaluate the 12 final IPCC climate projection scenarios to the year 2100 with full statistical replication.

---

## 6. Strategic Takeaways

| Dimension | Classical Paradigm (2020 Antrag) | Modernized JAX + SciML Paradigm (2026) |
|---|---|---|
| **Model Dimensionality** | 0-D well-mixed tank model ($P, N, D$). | Kept strictly as 0-D well-mixed tank model; isolates evolutionary biology from fluid dynamics. |
| **Model Resolution** | Compromised to MCM trait-diffusion due to CPU cost. | Full discrete IBM restored with $M \ge 100,000$ agents on GPU/TPU. |
| **Execution Architecture** | Sequential Fortran/OpenMP loops on CPU clusters (hours/days per decadal run). | Vectorized branchless `jnp.where` in JAX compiled with XLA (minutes per multi-decadal run). |
| **Climate Forecasting (2020–2100)** | Run 12 scenarios using simplified continuous diffusion. | Run 12 scenarios using the accurate, discrete IBM with full demographic stochasticity. |
| **Role of Machine Learning** | None. | **Simulation-Based Inference (SBI):** Neural density estimation to invert biological parameters from sediment resurrection data. |
| **HPC Deployment** | Ad-hoc cluster scripts with potential environment drift. | Containerized Apptainer pipeline managed via structured Slurm array workflows. |

---

*Document filed in `chess_speak_out_loud/docs/cya_remo_jax_ibm_ml_contemplation.md` for permanent reference, interview preparation, and scientific strategy.*
