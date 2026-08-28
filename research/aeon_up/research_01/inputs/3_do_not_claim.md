# 06. Strict Boundaries: What You Must NOT Claim

> **Reading Time:** ~10 minutes  
> **Target:** Memorize your defensive perimeter. An overclaim in an interview with domain experts like Dr. Ramacher and Dr. Karl can be instantly disqualifying.

---

## 1. The Five Non-Negotiable Boundaries

```
+-----------------------------------------------------------------------------------+
| ❌ NEVER CLAIM                                | ✅ WHAT YOU MAY HONESTLY SAY       |
+-----------------------------------------------+-----------------------------------+
| 1. Published papers in Bayesian Deep          | "I have studied the theoretical   |
|    Learning or Neural Processes.              | literature and implemented these  |
|                                               | architectures in PyTorch, though  |
|                                               | my published papers are in        |
|                                               | computational physical modeling." |
+-----------------------------------------------+-----------------------------------+
| 2. Causal interventions, activation patching, | "I engineer custom forward hooks  |
|    or mechanistic circuit discovery.          | in PyTorch to capture, extract,   |
|                                               | and analyze internal layer        |
|                                               | representations during inference."|
+-----------------------------------------------+-----------------------------------+
| 3. Hands-on experience with CMAQ,             | "I have not run EPISODE-          |
|    EPISODE-CityChem, or WRF-Chem.             | CityChem or CMAQ. My grid         |
|                                               | work is water-column: GOTM-       |
|                                               | FABM, and a Lagrangian IBM,       |
|                                               | on Linux HPC."                    |
+-----------------------------------------------+-----------------------------------+
| 4. Formal domain expertise in Urban Air       | "My background is in computational|
|    Quality regulations or atmospheric science.| environmental simulation, marine  |
|                                               | biogeochemistry, and astrochemistry|
|                                               | reaction networks."               |
+-----------------------------------------------+-----------------------------------+
| 5. Any claims based on the 'sacrifice/Tal'   | "I evaluate machine learning      |
|    metric from the chess project.             | pipelines strictly on verifiable  |
|                                               | statistical calibration, CRPS,    |
|                                               | and invariant regression tests."  |
+-----------------------------------------------+-----------------------------------+
```

---

## 2. Detailed Breakdown of Each Boundary

### Boundary 1: Machine Learning Publications
- **The Risk:** Claiming or implying you have published ML papers invites the committee to search Google Scholar for your ML citations, finding none.
- **The Honest Position:** You are a computational scientist with strong physical modeling foundations and rigorous, hands-on PyTorch engineering experience. You are enthusiastic about publishing your first probabilistic ML papers within the AEON-UP project.

### Boundary 2: Mechanistic Interpretability & Circuit Analysis
- **The Risk:** Talking about "ablation studies," "activation patching," or "mechanistic interpretability circuits" when you have only extracted forward-hook activations will expose you to deep questioning on causal causal graph theory.
- **The Honest Position:** Frame your ML work strictly as **PyTorch pipeline engineering, representation extraction, ONNX translation, and batched inference optimization**.

### Boundary 3: Atmospheric Models (CMAQ / EPISODE-CityChem)
- **The Risk:** Claiming you know the configuration flags of EPISODE-CityChem in front of Dr. Matthias Karl (who wrote the model) will lead to immediate exposure on Fortran namelists or specific turbulence schemes.
- **The Honest Position:** State plainly that your grid experience is water-column — GOTM-FABM, turbulence closure, operator splitting, NetCDF processing — plus a 0D Lagrangian individual-based model, and that you look forward to learning the specific namelists and chemical mechanisms of EPISODE-CityChem from Dr. Karl's team. Do not inflate a 1D water column into a 3D domain; the numerics transfer, the domain size does not.

### Boundary 4: Air Quality Domain Experience
- **The Risk:** Pretending to be an atmospheric chemist when your PhD is in astrochemistry and your postdoc was in marine ecosystems.
- **The Honest Position:** Emphasize the mathematical and computational equivalence of transport and reaction equations across environmental domains.

### Boundary 5: The Unsound Chess Metric
- **The Risk:** Mentioning the "sacrifice/Tal" metric from the chess exploration repository. That metric is documented internally as unsound and uncalibrated.
- **The Honest Position:** Never reference it. When discussing your ML work, focus exclusively on transformer forward hooks, tensor batching, ONNX conversion, and the two silent pipeline bugs you diagnosed and fixed.

---

## 3. Professional Demeanor & External Pressures

> [!CAUTION]
> **Never Communicate Financial Runway or Visa Pressures:**
> - Under no circumstances should visa expiry dates, financial urgency, or personal job-hunt fatigue be mentioned to the hiring committee.
> - Research PIs at Helmholtz institutions hire based on **scientific excellence, engineering competence, low onboarding friction, and collaborative chemistry**.
> - Maintain a calm, high-agency, confident persona: you are evaluating AEON-UP as the ideal scientific convergence for your computational and deep learning career.

---

## 4. Boundary 6 — Added 2026-08-26: The Coursework Claim

- **The Risk:** Letting "I am closing the probabilistic gap through coursework" stand. Neither
  credential on the CV is probabilistic. IBM's *Deep Learning with PyTorch* runs from logistic
  regression to CNNs and transfer learning — **no Bayesian inference, no uncertainty
  quantification, no calibration**. The HLRS course is scalable pipelines (Spark, PyTorch on GPU,
  notebook → HPC job). Both syllabi are public and take two minutes to read.
- **The Honest Position:** The courses are *the engineering foundation underneath* — which is
  precisely how the cover letter now words it. The probabilistic work is self-directed: the
  literature, plus a conditional neural process you are implementing yourself.
- **Full breakdown:** `12_pytorch_course.md`.
