# 01. Domain Briefing: Atmospheric Science, CTMs, and Ultrafine Particles

> **Reading Time:** ~25 minutes  
> **Target:** Understand the physical processes, numerical modeling mechanics, and pollutant dynamics relevant to AEON-UP.

---

## 1. What a Chemistry Transport Model (CTM) Does

A **Chemistry Transport Model (CTM)** is a numerical simulation system that solves the atmospheric conservation of mass equation for multiple reacting chemical species and aerosols in a 3D Eulerian domain.

### 1.1 The Governing Advection-Diffusion-Reaction Equation

For a chemical species with concentration C_i(x, y, z, t) at location (x, y, z) and time t:

```
d(C_i)/dt = - div(u * C_i) + div(K * grad(C_i)) + R_i(C_1, ..., C_N) + E_i - S_i
```

Where:
- `- div(u * C_i)`: **3D Advection** driven by mean wind vector u = (u, v, w).
- `div(K * grad(C_i))`: **Turbulent Diffusion** parameterized using turbulent eddy diffusivity tensors K (K-theory).
- `R_i(C_1, ..., C_N)`: **Chemical Transformation** (non-linear chemical kinetics, photolysis, gas-to-particle partitioning).
- `E_i`: **Emissions** (anthropogenic traffic, industrial stacks, domestic heating, biogenic sources).
- `S_i`: **Sinks** (dry deposition to vegetation/soil and wet scavenging by precipitation).

### 1.2 The Operator Splitting Technique

Because chemical reaction timescales (seconds to minutes) differ radically from advection timescales (hours), CTMs use **operator splitting** (e.g. Yanenko or Strang splitting). The numerical engine updates concentration C_i at step t -> t + dt sequentially:

```
Step 1: Advection    -->  C*   = A(dt) C(t)
Step 2: Diffusion    -->  C**  = D(dt) C*
Step 3: Chemistry    -->  C*** = R(dt) C**
Step 4: Deposition   -->  C(t+dt) = S(dt) C***
```

### 1.3 CTM Required Inputs and Boundaries

CTMs operate in **offline mode** and require three massive boundary datasets:
1. **Meteorology (NWP):** Hourly 3D wind fields, temperature, planetary boundary layer height (PBLH), humidity, and solar radiation from models like WRF or IFS.
2. **Emission Inventories:** High-resolution spatial/temporal emission rates (e.g., UrbEm, SMOKE, TNO-MACC).
3. **3D Boundary Conditions:** Chemical concentrations at the domain perimeter, typically provided by regional models (e.g., CMAQ or Copernicus CAMS).

---

## 2. EPISODE-CityChem: The Urban-Scale Model

**EPISODE-CityChem** is the urban-scale CTM developed and maintained at Helmholtz-Zentrum Hereon by Dr. Matthias Karl and colleagues. It extends the Norwegian Institute for Air Research (NILU) EPISODE dispersion model to simulate reactive pollutants at high urban resolution.

### 2.1 The Two-Scale Hybrid Architecture

Standard Eulerian grid models cannot resolve street canyons without exorbitant computational costs. EPISODE-CityChem solves this by embedding **sub-grid Lagrangian/Gaussian models** inside a **3D Eulerian main grid**:

```
+-------------------------------------------------------------------+
| 3D Eulerian Main Grid (Coarse: 1 km x 1 km or 500 m x 500 m)       |
|                                                                   |
|   Solves: Regional background, advection, turbulent K-diffusion   |
|                                                                   |
|   +-------------------------------------------------------------+ |
|   | Embedded Sub-Grid Modules:                                  | |
|   | 1. Gaussian Plume/Puff: Point sources (industrial stacks)   | |
|   | 2. Line Source Dispersion: Street canyons & major roads      | |
|   | 3. Photo-Stationary Equilibrium: Fast local photochemistry  | |
|   +-------------------------------------------------------------+ |
|                                                                   |
| Output: Combined Concentration C_total = C_Eulerian + C_subgrid   |
+-------------------------------------------------------------------+
```

### 2.2 Fast Photochemistry: The NO-NO2-O3 Triad

In the sub-grid line source model near roads, the chemistry cannot wait for the full chemical mechanism. It calculates **Photo-Stationary Equilibrium (PSE)** across three reactions:

```
1. NO + O3  ---> NO2 + O2        (Fast titration of ozone by emitted NO)
2. NO2 + hv ---> NO + O(3P)      (Photolysis of NO2 by sunlight)
3. O(3P) + O2 + M ---> O3 + M    (Rapid regeneration of ozone)
```

At steady state:

```
[NO2] / ([NO] * [O3]) = k_1 / j_NO2
```

Where `k_1` is the temperature-dependent reaction rate and `j_NO2` is the photolysis rate.

### 2.3 The Computational Bottleneck

Running EPISODE-CityChem over a full metropolitan area (e.g. Hamburg, Greater Barcelona) for an entire year requires single-processor Linux execution producing hundreds of gigabytes of NetCDF files. Simulating thousands of street segments with sub-grid Gaussian modules is computationally prohibitive for real-time forecasting, scenario exploration, or pan-European deployment.

**The AEON-UP Mission:** Replace or augment these expensive sub-grid calculations and downscaling steps with a probabilistic deep learning model (**Neural Processes**) that predicts urban concentration fields with calibrated uncertainty.

---

## 3. Spatial Behavior: NO2 vs. Particulate Matter (PM2.5 / PM10)

Air quality modeling must handle pollutants with completely different spatial scales and physical lifetimes.

```
Pollutant Concentration Drop-Off from Road Centerline:

Concentration
  ^
  |  ***  [NO2 / UFP: Sharp local peak, drops within 50-100m]
  |  *  *
  |  *   *
  |  *    ********* [PM2.5 / PM10: Dominated by smooth regional background]
  |  *            *
  +--------------------------------------------------------->
  0m             50m           100m           200m     Distance from road
```

### 3.1 Nitrogen Dioxide (NO2): Sharp and Local
- **Primary Source:** Direct emission as Nitric Oxide (NO) and NO2 from combustion engines (especially diesel vehicles).
- **Spatial Signature:** Extreme spatial gradients. Peak concentrations occur directly on road axes and drop off by 60–80% within 50 to 100 meters of the roadway.
- **Why?** Rapid local titration of ozone (`NO + O3 -> NO2`) occurs immediately upon emission, and the chemical lifetime of NOx in the urban boundary layer is short (a few hours).

### 3.2 Particulate Matter (PM2.5 and PM10): Smooth and Regional
- **Primary vs. Secondary:** While primary PM is emitted by tire wear, brake dust, and tailpipes, a substantial fraction of urban PM2.5 consists of **Secondary Inorganic Aerosols (SIA)** (ammonium sulfate, ammonium nitrate) and **Secondary Organic Aerosols (SOA)** formed over regional transport scales.
- **Spatial Signature:** Spatially homogeneous over kilometers. The urban background accounts for 70–80% of the total PM2.5 mass; local traffic adds only a modest localized increment.
- **Why?** Particles in the 0.1–2.5 micrometer accumulation mode have low dry deposition velocities and long atmospheric lifetimes (several days to a week), enabling regional transport across hundreds of kilometers.

---

## 4. Ultrafine Particles (UFP): The Aerosol Frontier

Dr. Matthias Karl has published extensively on Ultrafine Particles (*City Scale Modeling of Ultrafine Particles in Urban Areas*). UFP is a centerpiece of the AEON-UP proposal.

### 4.1 Definition and Measurement Metric
- **Size Definition:** Particles with an aerodynamic diameter **D_p < 100 nanometers (0.1 micrometers)**.
- **The Critical Metric:** Measured by **Particle Number Concentration (PNC)** in units of **`particles / cm3`**, NOT by mass (`micrograms / m3`).
- **Why Mass Fails for UFP:** 
  - A single 10-micrometer particle has the same mass as **1,000,000** ultrafine particles of 100 nm diameter.
  - In mass measurements (`ug/m3`), UFP is completely invisible (accounting for < 1% of total PM mass).
  - Yet UFP dominates **total particle number** (> 80–90% of all particles in urban air) and provides the largest specific surface area for toxic chemical absorption.

### 4.2 Dynamic Aerosol Microphysics
Unlike inert tracers, UFP concentrations evolve through rapid non-linear microphysical processes:
1. **Nucleation:** Gas-to-particle conversion of low-volatility vapors forming new nanometer-scale clusters.
2. **Coagulation:** Brownian collision between two ultrafine particles merging into a single larger particle. The rate of loss of particle number concentration N is proportional to N^2:
   ```
   dN/dt = - K_coag * N^2
   ```
   Because coagulation is second-order in N, high UFP concentrations (e.g. > 100,000 particles/cm3 in a ship plume or highway) decay extremely rapidly in the first minutes.
3. **Condensation:** Vapors condensing onto existing particles, growing them out of the UFP range into the accumulation mode.

### 4.3 Regulatory Status in the European Union

> [!IMPORTANT]
> **EU Regulatory Fact (Crucial for Interview):**
> - Under current EU Ambient Air Quality Directives (Directive 2008/50/EC), **there are NO legally binding concentration limit values for Ultrafine Particles (PNC)**. Limit values exist only for PM10 (40 ug/m3 annual) and PM2.5 (25 ug/m3 annual).
> - In the **revised Ambient Air Quality Directive** (agreed in 2024 for implementation toward 2030), the EU mandates **monitoring obligations** for UFP (PNC and size distribution) at urban background and traffic supersites, but **still does NOT impose a binding numerical limit value**.
> - The **WHO Air Quality Guidelines (2021)** introduced "Good Practice Statements" for UFP:
>   - Low PNC: `< 1,000 particles/cm3` (24h mean)
>   - High PNC: `> 10,000 particles/cm3` (24h mean) or `> 20,000 particles/cm3` (1h mean)

### 4.4 Why UFP is Hard to Model and Monitor
- **Sparse Monitoring:** Standard air quality networks monitor NO2, O3, PM10, and PM2.5. Routine UFP monitoring stations are exceptionally rare due to instrument costs (Condensation Particle Counters, CPC, and Scanning Mobility Particle Sizers, SMPS).
- **Extreme Gradients:** UFP number concentrations drop by a factor of 5 to 10 within 100–200 meters of a major highway or ship plume due to rapid dilution and coagulation.

---

## 5. Meteorology: Boundary Layer Height and Inversions

The vertical structure of the lower atmosphere determines the dilution capacity for urban emissions.

```
Normal Day (Convective Mixing):         Thermal Inversion (Pollution Trapped):

   Altitude (z)                           Altitude (z)
      ^                                      ^
      |                                      |    Warm Air Layer (Inversion Lid)
      |  Temperature decreases with height   |  ==================================
      |  dT/dz < 0                           |    Temperature INCREASES with height
      |  Deep Mixing Layer (1000m - 2000m)   |    dT/dz > 0
      |                                      |  ----------------------------------
      |  Pollutants dilute vertically        |    Shallow Cold Air Layer (50m - 200m)
      |                                      |    * * * NO2 & UFP TRAPPED * * *
      +--------------------------------->    +--------------------------------->
                      Temp                                   Temp
```

- **Planetary Boundary Layer Height (PBLH):** The height below which surface-induced turbulence mixes heat, moisture, and pollutants.
- **Thermal Inversions:** When cold air is trapped at the surface beneath warmer air aloft (`dT/dz > 0`), vertical turbulent mixing is suppressed (`K_z -> 0`).
- **Impact:** Winter inversions suppress the dilution volume by a factor of 10 to 20, causing severe pollution episodes even when emission rates remain constant.

---

## 6. The Resolution Gap: CTM Grid vs. Street Canyon

```
+---------------------------------------------------------------------+
| CTM Grid Cell (1 km x 1 km)                                         |
| Concentration = Volume Average C_avg = 22 ug/m3                     |
|                                                                     |
|   Street Canyon (Width W = 20m, Height H = 25m):                    |
|                                                                     |
|       Wind --->                                                     |
|       +-------------------+       +-------------------+             |
|       | Roof Level        |       | Roof Level        |             |
|       |                   |       |                   |             |
|       |   Building A      |       |   Building B      |             |
|       |                   | (Vortex)                  |             |
|       |                   |   <-- |                   |             |
|       |                   |  |   ||                   |             |
|       |                   |   --> |                   |             |
|       |                   |       |                   |             |
|       | Leeward Sidewalk  | Road  | Windward Sidewalk |             |
|       | [NO2 = 65 ug/m3]  | Cars  | [NO2 = 28 ug/m3]  |             |
|       +-------------------+-------+-------------------+             |
|                                                                     |
+---------------------------------------------------------------------+
```

- **The Problem:** An Eulerian CTM grid cell of 1 km x 1 km computes a single uniform volume average (e.g. 22 ug/m3 NO2).
- **The Reality:** Inside a street canyon (aspect ratio H/W >= 1), cross-winds create a recirculating **helical vortex**. The vortex sweeps vehicle emissions directly toward the **leeward building facade**, creating pedestrian sidewalk concentrations that can exceed the cell average by 300–400%.
- **Machine Learning Role:** High-resolution spatial downscaling models must learn to integrate local building geometry (aspect ratio, sky view factor), high-resolution traffic vectors, and wind direction to map these microscale gradients without solving full computational fluid dynamics (CFD).

---

## 7. Key Domain References

1. **Karl, M., et al. (2019):** *The Eulerian urban dispersion model EPISODE - Part 2: Extensions to the source dispersion and photochemistry for EPISODE-CityChem v1.2 and its application to the city of Hamburg*. Geoscientific Model Development, 12, 3357–3389. DOI: [10.5194/gmd-12-3357-2019](https://doi.org/10.5194/gmd-12-3357-2019).
2. **Karl, M., et al. (2020):** *City Scale Modeling of Ultrafine Particles in Urban Areas*. Int. J. Environ. Res. Public Health, 17(6), 2099. DOI: [10.3390/ijerph17062099](https://doi.org/10.3390/ijerph17062099).
3. **Ramacher, M.O.P., et al. (2020):** *Contributions of traffic and shipping emissions to city-scale NOx and PM2.5 exposure in Hamburg*. Atmospheric Environment, 237, 117674. DOI: [10.1016/j.atmosenv.2020.117674](https://doi.org/10.1016/j.atmosenv.2020.117674).
4. **World Health Organization (2021):** *WHO Global Air Quality Guidelines: Particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide*. Geneva: World Health Organization.
