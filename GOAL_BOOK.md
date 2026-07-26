# GOAL BOOK — the product vision, as the user means it

> The product-vision counterpart to `LEADER_BIBLE.md`. Every worker anchors here so no one
> drifts from the aim. Sourced from the user's answers in `GOAL_ELICITATION_QUESTIONS.md`
> (2026-07-26). **[E]** = the user stated it explicitly; **[I]** = leader inference (flagged
> for the user to confirm/correct). Leader-owned; update as the vision sharpens.

## North star (the soul of the tool)
A ~2100–2200 Lichess player, **bored by dry/equal positions** (his London System drifts to
"dry draw or not advantageous"), who **wants sharp, dynamic, sacrificial, Tal-like chess** —
but who says openly that **tactics are one of the weakest parts of his game** [E, Q1/Q2/Q2.1].
So the tool's job is not "surface sharp moves." It is: **turn his own games into a personal
path from dry-and-equal toward sharp-and-tactical, while teaching him the tactical vision to
survive there.** He is a serious student; depth over polish; **UI speed matters, analysis
latency is fine** [E, Q6].

## The recurring backbone he keeps returning to: THEME / PIECE-CONFIGURATION as the atomic unit
Across Jobs 1, 2, 3, 7 he asks for the same thing in different clothes: a **knowledge base
mapping piece-configurations → tactical themes** (built from Lichess themes / articles) [E,
Q2.1]. He wants it to (a) **explain WHY LC0 favors a move** — "because it leads to a tactical
configuration, not just a slight advantage" [E, Q2.1]; (b) organize thematic drills [E, Q3];
(c) enable **similar-position testing** with similarity scaled to the stakes [E, Q7.3]; (d)
link a position to **example games** (masters / recent / his own) where the theme appears [E,
Q1.1]. **This KB is the enabling infrastructure under half the vision.** He admits low tactical
knowledge, so the KB is both a teaching tool and a search index.

## Two loops the whole system runs on
1. **Correction loop** (fix what recurs): diagnose his games → detect **recurring** mistakes →
   he **reviews/approves** [E, Q4] → **blended spaced-repetition queue weighted by severity**
   [E, Q8.2] on his **exact game positions** [E, Q6.2] → re-test → "corrected" = **90% on
   spaced-rep re-tests over 30 days** [E, Q6.3] → **re-diagnose newly played games to prove
   the mistake rate drops** [E, Q5] (the ultimate proof).
2. **Vision/intuition loop** (see & think like LC0): predictive drills — **guess LC0's top
   policy move in ~10s** [E, Q5.2] → wrong = a gap → study the principle/theme → retry [E,
   Q5.1]. Primary signals he wants: **raw policy probabilities + search eval + policy ranking**
   (NOT attention heatmaps yet — he's unsure how to read them; parked for later w/ a guidebook)
   [E, Q4.1/Q5.2].

## Cross-cutting principles (non-negotiables — treat as constraints on every feature)
- **His exact game positions, not synthetic** for correction drills [E, Q6.2].
- **Automated identification, but a human review/approve gate** before a position enters the
  deck [E, Q4].
- **Blended spaced-rep queue weighted by severity**, NOT one-topic-per-week [E, Q8.2].
- **Mastery = pattern recognition in real games**, not rote reps (~3 reps, then spaced over
  time; the point is recognizing it OTB) [E, Q3.3].
- **Fast, lean UI**; no gamified animation bloat; analysis can be slow [E, Q6].
- **Sessions 30–60 min, 3–4×/week, desktop-first** (plays on lichess desktop/mobile) [E, Q7].
- **Both broad AND specific weakness taxonomies** (overview + precise technical diagnosis)
  [E, Q8.1].

## The 8 jobs, distilled (his words → what it means → session → success → engine mapping)
- **J6+J8 — Recurring weaknesses ("usual suspects"), categorized & drilled** *(his #1 pick)*.
  "Identify the common mistakes I make often" — tactical oversights, missed simplifications
  into winning endgames, missed winning sacs, **repeated opening mistakes** [E, Q3/Q6.1].
  Needs NEW capability: **recurrence detection** (same theme/opening-line across many games),
  broad+specific categories, exact-position mini-sets, severity-weighted spaced-rep queue, a
  dashboard of *weakness / opening / tactical-theme-needing-attention* [E, Q8.3]. Maps to: the
  existing diagnosis profile (findings by phase/clock/motif/concept) + a new clustering layer.
- **J4+J5 — See & develop intuition like LC0.** Predictive **10-min daily speed-guess of LC0's
  top policy** [E, Q5.2/Q5.3]; a cycle of guess→gap→study→retry. Maps to: BT3 policy + search
  eval (already have). Small, clean, largely independent — a good early win.
- **J3 — Thematic tactical drilling.** Motifs he wants [E, Q3.1]: kingside sacs (B/N/Q), pawn
  sacs for dynamics, exchange sacs, knight forks, double attacks in London structures, KGA
  kingside attacks as Black, "sac to land a knight near the king." Drill = **solve the principle
  THEN play the full continuation vs LC0** to feel the flow [E, Q3.2]. Depends on the theme KB.
- **J1 — Steer to a "tactical landmine."** Good landmine = sharp line (Fried Liver / Evans /
  sharp Giuoco Nc3) with an early sac where only 1–few moves survive [E, Q1.1]. Must
  **auto-complement** each landmine with its tactical theme + drills + example games [E, Q1.1].
  Session: **play out 3–5 moves vs LC0** to prove survival; ask questions; show the continuation
  if wrong [E, Q1.2]. Losing moves flagged; landmines where the opponent is likely to walk into
  disaster [E, Q1.3]. Maps to: TS2 steer complexity components; depends on theme KB.
- **J7 — Face feared Tal-style sacrifices.** Root of the fear: **he can't foresee the winning
  final position / the piece-configuration the sac produces** [E, Q7.1]. Session: is there a
  sac? → identify it + why you'd hesitate → evaluate the post-sac position → **pick its tactical
  theme from a list** → play the attack vs LC0 [E, Q7.2]. Verify by testing **similar
  configurations, similarity scaled to the loss if missed** [E, Q7.3]. Maps to: `had_tal_move`
  steer_findings + theme KB.
- **J2 — Sharp/"tightrope" positions from his own openings** *(his emotional driver)*. Wants
  LC0 to find moves that reach **typical tactical piece-configurations** in his repertoire, so
  he can escape the dry London — even willing to switch to 1.e4 or new openings [E, Q2/Q2.1].
  MVP: a few positions from his openings that lead to known tactical themes / sacs with
  compensation, where one wrong move = disaster; plus a **repertoire tree/graph highlighting
  high-complexity nodes** [E, Q2.2/Q2.3]. Hardest / most research — needs the theme KB +
  reachability search + the (currently broken) ECO/opening layer.

## Sequenced roadmap (one by one — respecting his #1 pick and dependencies) [I — for confirmation]
1. **Sprint 1 — "Usual Suspects": recurring-weakness detection + review/approve + severity-
   weighted spaced-rep deck on his exact positions + a minimal dashboard** (J6+J8). His stated
   #1; builds directly on the existing profile; delivers the correction loop end-to-end.
2. **Sprint 2 — LC0 intuition speed-drill** (J4+J5). Small, independent, early win; 10s policy
   guessing on his positions.
3. **Sprint 3 — Tactical-theme knowledge base + thematic drilling** (J3). Build the config→theme
   backbone (Lichess themes/articles), tag findings/steer with themes, solve-then-play-out drills.
4. **Sprint 4 — Landmine + sac-hesitation training** (J1+J7). Depends on the theme KB; the
   play-out-vs-LC0 + theme-pick + similarity-test flows.
5. **Sprint 5 — Sharp-opening steering & config-reachability** (J2). The "escape dry openings"
   dream; hardest; needs KB + reachability + fixed ECO layer.

## Open questions / to re-elicit (do not guess — confirm with the user)
- Full opening repertoire (both colors) + time controls + weekly game volume were not fully
  given (Q1). Needed before J2/J3.
- The **1.e4 / new-opening switch** — a real decision he's weighing (Q2); does the tool advise
  on it, or work with whatever he plays?
- **Attention heatmaps** parked — revisit once he's studied more themes (Q4.1).
- "Similarity proportional to the loss factor" (Q7.3) needs a concrete definition before build.
- What we already have that maps in: diagnosis profile, steer_findings + complexity/`had_tal_move`,
  BT3 policy + search, `lichess_tagger` motifs, DrillMode + attempts + SRS scaffolding,
  repertoire builder (once ECO is fixed).
