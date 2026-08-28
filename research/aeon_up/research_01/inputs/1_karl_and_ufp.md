# 15. The other half of the panel — Dr. Karl, and ultrafine particles

**Written 2026-08-28. This is H5.** The cover letter is addressed to both PIs and engages only
Ramacher's Code4Earth work. **Ultrafine particles — Karl's named area, and named in the advert —
appear in it nowhere.** Half the panel was not written to. This file prepares that half in the
room instead, which is the only place left to do it.

> `01_domain.md` already carries the physics. **This file does not repeat it** — it is about what
> Karl will actually ask, and about the one argument that turns UFP from a subject he has read
> about into the strongest case for his own thesis.

---

## 1. Who is across the table

**Dr. Matthias Karl** wrote and maintains **EPISODE-CityChem**. He is a physics-based CTM
specialist — aerosol dynamics, chemistry, dispersion, exposure — and he has **no published machine
learning track record**.

Two consequences, and they pull in opposite directions:

1. **He can expose an overclaim about his own model instantly.** Never discuss EPISODE-CityChem
   internals, namelists, turbulence schemes or chemical mechanisms as though you have run it.
   `06_do_not_claim.md`, Boundary 3. This is the single most dangerous boundary in the room,
   because it is the one where the person opposite is the primary source.
2. **He may be the sceptic on the ML half.** A physics modeller watching a neural network get
   pointed at his output has a fair worry: that it will produce something plausible that nobody
   can check. **You already agree with him.** That agreement is your way in, and it is genuine —
   it is the same worry that made you find your own two silent bugs.

**The posture toward Karl:** not "machine learning can do this better", but *"here is how we make
the learned half checkable, so it earns a place next to the physics."*

---

## 2. The five UFP facts to have cold

From `01_domain.md` §4. Know them well enough to say without hedging.

1. **Mass measurement makes UFP invisible.** One 10 µm particle carries the mass of about a
   million 100 nm particles. UFP is under 1% of PM mass and **80–90% of particle number.** So the
   quantity of interest is **PNC — particle number concentration**, not µg/m³. Getting this wrong
   in front of Karl would be bad.
2. **The gradients are brutal.** PNC drops by a factor of **5 to 10 within 100–200 m** of a
   highway or a ship plume.
3. **UFP is not a passive tracer.** Number concentration evolves by **coagulation, which is
   second-order in N** — high concentrations in a fresh plume decay very fast — plus condensational
   growth out of the ultrafine range entirely. **Number is not conserved.**
4. **Monitoring is extremely sparse.** Routine networks measure NO₂, O₃, PM10, PM2.5. UFP needs
   CPCs and SMPS instruments, so stations are rare.
5. **There is no binding limit value.** Directive **2008/50/EC** sets limits for PM10 (40 µg/m³
   annual) and PM2.5; the **revised AAQD agreed in 2024** mandates UFP *monitoring* at supersites
   but still sets **no numerical limit**. WHO's 2021 guidelines give **"Good Practice Statements"**
   for UFP, not a guideline value.

> ⚠ **Verify before you say it:** the exact title of Karl's UFP paper. `01_domain.md` gives it as
> *"City Scale Modeling of Ultrafine Particles in Urban Areas"*. Confirm the title, year and
> venue on his publication page before naming it — **naming a paper wrongly to its author is worse
> than not naming it.** His EPISODE-CityChem Part 2 paper is safe and verified:
> *Karl et al. (2019), Geoscientific Model Development 12, 3357–3389,
> doi:10.5194/gmd-12-3357-2019* — the Hamburg application.

---

## 3. ⚑ The bridge — why UFP is the best possible case for your thesis

**This is the section to actually learn.** It is the argument the cover letter should have made,
and it is stronger spoken than it would have been written.

Facts 4 and 5 together are unusual, and they change what a model is *for*:

> **There is no legal limit to check against, and almost nowhere to measure.**

So an AEON-UP model is not producing a compliance number that a monitor can later confirm. It is
producing an **exposure estimate at places nobody measures**, feeding health and policy work. A
point prediction with no honest uncertainty is close to useless there — and worse than useless if
it is confidently wrong, because there is no monitoring station to contradict it.

**Say something close to this:**

> *"With PM10 you have a limit value and a network — a wrong prediction gets caught. With UFP there
> is no binding limit and almost no monitoring, so the model's own uncertainty estimate is doing
> the work that a monitoring station would otherwise do. That is exactly the case where a
> confidently wrong model does real damage, and it is why I care so much about calibration rather
> than only about skill."*

**And the honest technical link — this is real, not a stretch:**

The second task in the CNP I implemented was a synthetic 2-D city field built as **a smooth
regional background plus a sharp road ridge**, evaluated **leave-one-station-out**. That is the UFP
problem's geometry exactly: a broad urban background with steep near-road structure, and so few
sensors that you must hold one out to know anything. **I did not build it for air quality — I built
it because that shape is the hard case — but it is the same shape.** (`fig3_city_field.png`,
`fig4_loso.png`.)

**Do not overstate it.** It is synthetic, it is not UFP data, and it has no microphysics. Say that
before he does.

**The physics constraint you should raise yourself** (fact 3, and it shows you have thought like a
modeller rather than a curve-fitter):

> *"Because coagulation is second-order in number, UFP is not a passive tracer — you cannot treat
> a learned correction as if it were linear in concentration, and I would not want a model
> extrapolating into plume concentrations it never saw in training. That is an argument for
> conditioning on the CTM's own output rather than replacing it, and for epistemic uncertainty
> that goes up honestly outside the training regime."*

Raising a limitation on your own approach, unprompted, in front of the physics PI, does more for
you than any claim of skill.

---

## 4. Questions Karl is likely to ask

**"What do you actually know about aerosol microphysics?"**
Answer honestly and short: astrochemistry reaction networks and marine biogeochemistry — coupled
reaction–transport systems, but **not** aerosol dynamics. You know why number and mass diverge,
why coagulation is second-order and what that implies for a learned model. You have not
implemented a modal or sectional aerosol scheme. **Then stop.** Do not fill the silence.

**"Why not just improve the CTM instead of bolting on a network?"**
Do not argue against the CTM — he wrote it. *"I would not replace it. The CTM carries the physics
and the emissions inventory; what it cannot do is condition cheaply on sparse observations at
arbitrary locations. The learned part is an observation-conditioning layer on top, and if it
cannot beat kriging on the same data it has not earned its place."*

**"How would we know your model is right where we have no measurements?"**
The best question you will get, and your answer is prepared: **leave-one-station-out**, not random
splits — random splits leak spatially and flatter everything. Score with **CRPS and calibration,
with mean σ reported beside it**, because calibration without sharpness is trivially achievable by
predicting a wide band everywhere. And the honest limit: LOSO tells you about *station-like*
locations; a street canyon with no station nearby is extrapolation, and the model should say so
through its epistemic uncertainty rather than through a confident number.

**"Have you worked with EPISODE-CityChem?"**
*"No."* Then Boundary 3: water-column grids, GOTM-FABM, operator splitting, NetCDF at scale; the
numerics transfer, the domain does not; you would learn the namelists and mechanisms from his team.
**Do not soften the "no" into "not directly".**

---

## 5. Two questions to ask Karl

Ask these of him specifically — it shows you prepared for both PIs, which is exactly what the
letter failed to do. (More in `16_questions_for_the_panel.md`.)

1. *"For UFP, is the target particle number concentration, or the size distribution? Predicting a
   distribution and predicting a scalar are quite different learning problems, and it changes what
   the uncertainty even means."* — a real design question, and it makes clear you know PNC is not a
   mass concentration.
2. *"Where do you expect EPISODE-CityChem to be weakest — is it emissions, the near-road gradient,
   or the microphysics? I would rather aim the learned correction at the part you least trust than
   at whatever is easiest to fit."* — invites him to talk about his own model's limits, which
   experts enjoy, and it positions the ML as serving the physics.

---

## 6. What must not be said to Karl

- ❌ Any hands-on claim about **EPISODE-CityChem, CMAQ or WRF-Chem.**
- ❌ **"Machine learning can replace the CTM"** or anything that implies it.
- ❌ µg/m³ for UFP. It is **number concentration.**
- ❌ Naming his UFP paper before verifying the title (§2).
- ❌ Presenting the synthetic city field as if it were air-quality data.
