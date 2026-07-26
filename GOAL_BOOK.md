# GOAL BOOK — the product vision, as the user means it

> The product-vision counterpart to `LEADER_BIBLE.md`. Every worker anchors here so no one
> drifts from the aim. Sourced from `GOAL_ELICITATION_QUESTIONS.md` (2026-07-26) + the user's
> follow-up answers + Gemini's `GOALBOOK_REVIEW.md` (leader-audited). **[E]** = user stated it
> explicitly; **[I]** = leader inference (flagged for the user to confirm). Leader-owned.
> **v2 (2026-07-26):** decoupled the theme-KB from the drill features, fixed J2 scope
> (current repertoire AND new sharp openings), added master-DB example games, defined the
> similarity-scoring rule, un-parked attention heatmaps.

## North star (the soul of the tool)
A ~2100–2200 Lichess player, **bored by dry/equal positions** (his London System drifts to
"dry draw or not advantageous"), who **wants sharp, dynamic, sacrificial, Tal-like chess** —
but who says openly that **tactics are one of the weakest parts of his game** [E, Q1/Q2/Q2.1].
So the tool's job is not "surface sharp moves." It is: **turn his games into a personal path
from dry-and-equal toward sharp-and-tactical, while teaching him the tactical vision to
survive there — and actively steering him toward openings that produce that chess.** Serious
student; depth over polish; **UI speed matters, analysis latency is fine** [E, Q6].

## Two loops the whole system runs on
1. **Correction loop** (fix what recurs): diagnose his games → detect **recurring** mistakes →
   he **reviews/approves** [E, Q4] → **blended spaced-rep queue weighted by severity** [E, Q8.2]
   on his **exact game positions** [E, Q6.2] → re-test → "corrected" = **90% on re-tests over
   30 days** [E, Q6.3] → **re-diagnose newly played games to prove the mistake rate drops** [E,
   Q5] (the ultimate proof).
2. **Vision/intuition loop** (see & think like LC0): predictive drills — **guess LC0's top
   policy move in ~10s** [E, Q5.2] → wrong = a gap → study the principle/theme → retry [E,
   Q5.1]. Primary signals: **raw policy probabilities + search eval + policy ranking** [E, Q4.1].
   **Attention heatmaps [I — leader discretion, user is curious but unsure how to use, Q4.1]:**
   fold them into this drill — the user predicts not just LC0's move but **which squares LC0
   attends to** (training the eye for where the tactic lives), and use the heatmap as a
   "why is this position tactically charged" explainer. Refine once he's studied more themes.

## The theme / piece-configuration layer (enrichment + explanation — NOT a gate)
A recurring, genuine ask [E, Q2.1]: a **knowledge base mapping piece-configurations → tactical
themes** ("typical piece formations for tactics must *first* be laid down from lichess themes
or articles, then asked LC0 if it can be arrived at from my opening"). Its value: (a) **explain
WHY LC0 favors a move** — "because it leads to a tactical configuration, not just a slight
advantage" (he called this "immensely helpful"); (b) train him to *imagine* tactical
formations; (c) enrich drill themes; (d) power similarity testing; (e) link to example games.
**Decoupling decision [leader, per Gemini review]:** the **drills (J1/J3/J7) ship first on
existing `TS2` outputs (`had_tal_move`, `policy_trap`, complexity) + `lichess_tagger` motif
tags** — they do NOT wait on this KB. The KB is a **parallel enrichment track**, and it is
genuinely more foundational for **J2** (reaching a named tactical configuration *from an
opening*), where the user himself said the formations must be laid down "first".

## Cross-cutting principles (constraints on every feature)
- **His exact game positions, not synthetic** for correction drills [E, Q6.2].
- **Automated identification + a human review/approve gate** before a position enters the deck
  [E, Q4].
- **Blended spaced-rep queue weighted by severity**, NOT one-topic-per-week [E, Q8.2].
- **Mastery = OTB pattern recognition**, not rote reps (~3 reps then spaced; recognizing it in
  real games is the point) [E, Q3.3]; the *correction-tracking* metric is 90% over 30 days
  [E, Q6.3]; the *ultimate* proof is fewer mistakes in newly played games [E, Q5].
- **Fast, lean UI**; analysis can be slow [E, Q6]. Sessions **30–60 min, 3–4×/week,
  desktop-first** [E, Q7]. **Both broad AND specific weakness taxonomies** [E, Q8.1].
- **His repertoire is derived from his ~9000-game PGN corpus** (or via Lichess) [E, follow-up].

## The 8 jobs, distilled
- **J6+J8 — Recurring weaknesses ("usual suspects"), categorized & drilled** *(his #1)*. "Identify
  the common mistakes I make often" — tactical oversights, missed simplifications into winning
  endgames, missed winning sacs, **repeated opening mistakes** [E, Q3/Q6.1]. NEW capability:
  **recurrence detection** (same theme/opening-line across many games), broad+specific
  categories, **his exact-position mini-sets**, severity-weighted spaced-rep queue, dashboard of
  *weakness / opening / tactical-theme-needing-attention* [E, Q8.3]. Maps to: existing diagnosis
  profile (findings by phase/clock/motif/concept) + a new clustering layer.
- **J4+J5 — See & develop intuition like LC0.** Predictive **10-min daily 10s speed-guess of
  LC0's top policy** [E, Q5.2/Q5.3], guess→gap→study→retry [E, Q5.1]; optionally predict the
  attention hotspots too (see Vision loop). Maps to: BT3 policy + search eval (already have).
  Small, independent — an early win.
- **J1 — Steer to a "tactical landmine."** Good landmine = sharp line (Fried Liver / Evans /
  sharp Giuoco Nc3) with an early sac where only 1–few moves survive [E, Q1.1]. **Auto-complement
  each landmine with: its tactical theme + drills + EXAMPLE GAMES from a master database / recent
  games / his own games** [E, Q1.1]. Session: **play out 3–5 moves vs LC0** to prove survival;
  ask questions; show the continuation if wrong [E, Q1.2]. Flag losing moves; favor landmines
  where the opponent is likely to walk into disaster [E, Q1.3]. Maps to: TS2 complexity
  components + `lichess_tagger` + a master-PGN lookup. (No KB gate.)
- **J7 — Face feared Tal-style sacrifices.** Root of the fear: **he can't foresee the winning
  final position / the piece-configuration the sac produces** [E, Q7.1]. Session: is there a sac?
  → identify it + why you'd hesitate → evaluate the post-sac position → **pick its tactical theme
  from a list** → play the attack vs LC0 [E, Q7.2]. Verify via **similar-configuration tests**,
  where **the penalty for a miss scales UP with the position's similarity to the trained one**
  (miss a near-identical pattern → lose more; a distant one → more forgivable) [E, Q7.3-followup].
  Maps to: `had_tal_move` steer_findings + motif tags. (No KB gate; KB enriches the theme list.)
- **J3 — Thematic tactical drilling.** Motifs [E, Q3.1]: kingside sacs (B/N/Q), pawn sacs for
  dynamics, exchange sacs, knight forks, double attacks in London structures, KGA kingside
  attacks as Black, "sac to land a knight near the king." Drill = **solve the principle THEN play
  the full continuation vs LC0** [E, Q3.2]. Maps to: `lichess_tagger` motifs now; KB later enriches.
- **J2 — Sharp openings: his own AND new ones** *(emotional driver)*. TWO sides [E, Q2 + follow-up]:
  (a) **derive his actual repertoire from the 9000-game corpus** and surface where it can be
  steered to tactical configurations / sacs with compensation; (b) **actively DIRECT him to NEW
  sharp openings** — he wants this — specifically 1.e4 gambit/sharp lines (Fried Liver, Evans,
  Giuoco Nc3), since he's ready to abandon the dry London. Wants LC0 to find moves reaching
  **typical tactical piece-configurations** [E, Q2.1], plus a **repertoire tree/graph highlighting
  high-complexity nodes** [E, Q2.2/Q2.3]. Hardest; needs the theme layer (config-reachability) +
  the (currently broken) ECO/opening layer.

## Sequenced roadmap (one by one) [I — for user confirmation; adopts Gemini's resequencing]
1. **Sprint 1 — "Usual Suspects"** (J6+J8): recurring-mistake detection across his PGNs →
   review/approve gate → severity-weighted spaced-rep deck on his exact positions → minimal
   dashboard. His #1; builds on the existing profile; delivers the correction loop end-to-end.
2. **Sprint 2 — LC0 intuition speed-drill** (J4+J5): 10-min daily 10s policy-guessing; lean,
   standalone, zero new engine deps. Early win.
3. **Sprint 3 — Landmine + Tal-sac hesitation drills** (J1+J7): powered by TS2 (`had_tal_move`,
   complexity) + `lichess_tagger` + **master-DB example lookup** + play-out-vs-LC0. **No KB
   blocker** — delivers the sharp/sacrificial experience he craves early.
4. **Sprint 4 — Sharp openings** (J2): derive current repertoire from the corpus + **recommend
   new 1.e4 sharp lines**; repertoire tree with high-complexity nodes. Needs the ECO fix.
5. **Sprint 5 — Deep theme/config knowledge base** (enrichment): config→theme from articles/
   Lichess themes; the "explain WHY LC0 chose this via the tactical configuration" layer; richer
   similarity + imagination training. Upgrades J1/J2/J3/J7 — an enhancement, not a gate.

## Decisions locked + remaining open questions
1. **Game ingestion — CONFIRMED (2026-07-26):** **Manual PGN for Sprint 1** (we already have
   the 9000-game corpus as PGN, and the diagnosis pipeline already consumes PGN), with **Lichess
   API auto-sync as a fast-follow** (for the Q5 "re-diagnose newly played games" proof loop).
2. **Recurrence rule — CONFIRMED (2026-07-26):** **rank by frequency × severity with a 2+ game
   floor** (faithful to Q8.2 "blended, severity-weighted queue").
3. **Master-DB source (Sprint 3, not urgent):** Lichess Masters DB API online vs local master
   PGN on desktop. Still open.
- Later: full time-control mix; how far the tool should go in *recommending* a new repertoire
  (a few candidate openings? a full switch plan?); and how "attention-hotspot prediction" should
  score once he's studied more themes.
