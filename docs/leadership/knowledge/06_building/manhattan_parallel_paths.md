# The Manhattan Project — buying certainty with parallel paths

**United States, 1942–1945. Leslie Groves (Army, executive direction) and J. Robert Oppenheimer (Los Alamos, scientific direction).**

## The situation

Nobody knew which method of producing fissile material would work. Uranium enrichment had at least
three candidate routes — gaseous diffusion, electromagnetic separation, and centrifuges — and
plutonium production by reactor was a fourth path to a bomb. Each was unproven at scale, each
required an industrial plant costing an appreciable fraction of a national budget, and the schedule
was set by a war.

The rational thing under normal budget discipline is to choose the most promising method.

## What was done

**Groves pursued the paths in parallel**, building full industrial plants for methods that might
turn out to be dead ends. Oak Ridge ran both electromagnetic separation and gaseous diffusion; the
plutonium route ran at Hanford. This was enormously wasteful in expectation, and it was correct: the
objective was not to minimise cost but to minimise the probability of arriving late.

**When plutonium turned out to be unusable in a gun-type weapon** — because reactor-bred plutonium
contained an isotope causing predetonation — the implosion design had to be invented under time
pressure. The parallel structure is what made that survivable; the uranium gun weapon was still
proceeding.

**The Groves–Oppenheimer division of labour** is the other lesson. Groves handled resources,
schedule, security and the industrial scale; Oppenheimer handled the scientific problem and the
scientists. Neither did the other's job, and each had authority in his own domain.

**Compartmentalisation** was Groves's security policy and it had a real cost: scientists who could
not see the whole problem could not contribute to parts of it. Oppenheimer fought for more openness
inside Los Alamos and largely got it. The trade-off between security and intellectual throughput was
made explicitly, not by default.

## The principle

**When the schedule matters more than the cost and the technology is genuinely uncertain, buy
insurance by running paths in parallel.** And separate resource authority from technical authority so
neither is bottlenecked on the other's competence.

## For us

**Parallel paths are affordable here in exactly one currency and not in another.** Our scarce
resource is not money for plants; it is Thejus's borrowed money, his time, and a permit expiring in
about eighteen months. Compute on Kaggle is free but rationed by the week.

So the honest reading: *we cannot run parallel paths at the scale of the profile regeneration*, and
pretending otherwise is how a project spends its runway. But we can and should run them where the
cost is minutes:

- **We already did it once.** `PLAN_CONFIGURATION_STEERING.md` §10.3 keeps N1 and N2 as separate
  negative sources, with `source` recorded per row, so F1 can be run against each independently. If
  Φ separates positives from spent tactics but not from real quiet play, that is diagnostic — and it
  costs nothing because both paths ride in one dataset.
- **The three-shape mount resolver** is a parallel path in miniature: I do not know whether Kaggle
  expands the archive, so both outcomes are handled rather than predicted.

**The division of labour is the part to take seriously.** Groves and Oppenheimer worked because
neither pretended to the other's competence. Our analogue — the leader specs and verifies, the worker
implements — has been tested three times this week and the results are consistent: Gemini is better
than me at exhaustive local inspection, and worse at determinism under ambiguity and at judging
severity. That is a real division, not a hierarchy, and the right response is to brief *toward* its
strength (enumerate every caller of X) rather than to ask it for verdicts.

**And compartmentalisation has a cost we are paying.** Gemini works from a brief and cannot see the
whole aim. That is what produced the sacrifice-pruning proposal: a locally excellent optimisation
that contradicted the project's purpose. Oppenheimer's answer — more openness inside the fence — is
why briefs now carry the intent and the aim in Thejus's own words, and not only the task.
