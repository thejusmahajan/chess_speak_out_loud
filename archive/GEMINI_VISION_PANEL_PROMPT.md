# TASK FOR GEMINI — Simulated vision panel (DOC ONLY, feeds the backlog)

Produce ONE markdown file, `VISION_PANEL_DISCUSSION.md`, at the repo root: a focused,
technical roundtable that generates **concrete, buildable training-tool ideas** for
this project. This is IDEATION that feeds `POST_VALIDATION_BACKLOG.md` — it commits us
to nothing. No code, run nothing. Your only output is the md file.

## Honesty guardrail (read first)
The panel includes voices modeled on real people (Gukesh, Tal) and real roles (an lc0
maintainer, an AlphaZero scientist). These are **clearly-labeled SIMULATED personas for
internal brainstorming** — a creative device to surface ideas from different lenses. The
doc must state this up front and must NOT present any line as an actual quotation or real
statement by a living or historical person. Keep every persona's content in-scope
(training chess with our tools); don't put words in a real person's mouth beyond the
craft.

## The cast and each one's distinct lens (keep them genuinely different)
- **LC0-DEV** — Leela maintainer. What BT3/lc0 can *expose* as training signal: policy
  priors, value/WDL heads, MCTS tree stats (visits, virtual loss, PV churn), the
  transformer's attention (our `saliency_absolute`), node-limited search internals, and
  the "hidden look-ahead" the net computes in its layers. Concrete extractability.
- **AZ-SCIENTIST** — AlphaZero/MCTS researcher. The *theory*: how the net "understands" a
  position, policy-vs-value tension, where a human's move distribution diverges from the
  net's, and the science behind the **"suppressed-win"** phenomenon (net finds a win in
  hidden layers but the prior buries it). How self-play knowledge maps to human training.
- **GUKESH** (simulated) — elite modern practitioner. How a world-class player actually
  trains WITH engines without becoming one; what "middlegame positional understanding"
  means in practice and how you *drill* it; calculation habits; turning engine truth into
  human-usable plans.
- **TAL** (simulated) — the sacrificial/attacking imagination. Intuition over exhaustive
  calc, the psychology of the sac, sound vs speculative, and how you *cultivate* attacking
  vision rather than memorize it. This is the persona for the Tal-style repertoire the
  user wants deeply.
- **CLAUDE-ARCHITECT** — the tool architect. Synthesizes every thread into features our
  stack can actually build, tags feasibility, flags real-vs-aspirational, owns the closing
  synthesis.

## Read these to ground yourself (do not invent capabilities we don't have)
- `LEADER_BIBLE.md` §1 (the vision) and §4 (decided nets/metrics).
- `POST_VALIDATION_BACKLOG.md` (optical traps, attention rays, refutation sparring, Tal
  persona — the parked ideas this panel should sharpen and extend).
- `docs/research_learned_lookahead.md` (the "suppressed-win probe" — the crown-jewel idea).

## The verified facts to build on (ground truth)
- **The player**: one hardworking human. Headline profile finding = **middlegame,
  positional blindness** (policy-blindness ~0.18 vs 0.08/0.07 other phases), flat across
  the clock. He explicitly wants to develop a **sacrificial / Tal style**.
- **What the tool ALREADY has** (tag ideas against this):
  - BT3-768x15x24h policy → the **policy-blindness metric** (Stage A) — where the human's
    move sits vs the net's policy mass.
  - lc0 **node-limited search** (Stage B, "deep confirmation") → confirmed mistakes,
    eval swings, WDL.
  - `saliency_absolute(fen)` → BT3 transformer **attention** per square (black-to-move
    correct).
  - **TS2 tactical steering** → produces `steer_findings` (candidate tactical/sac moves
    with a complexity score + components). A CORE deliverable that must run in every test.
  - A diagnosis **profile** (findings + steer_findings + aggregates) and a repertoire
    builder.
  - Research idea (NOT yet built): the **suppressed-win probe** — detect positions where
    BT3's deeper computation favors a winning (often sacrificial) move that its own prior
    suppresses → "forgotten puzzles" that fit Tal/TS2.

## Agenda — keep to these four threads, then synthesize (no meandering)
- **A. Deeper diagnosis.** Beyond the current metrics, what MORE can BT3 policy/value/
  attention + MCTS tree stats reveal specifically about THIS player's *middlegame
  positional* blindness? (LC0-DEV + AZ-SCIENTIST lead; GUKESH sanity-checks "what a coach
  would actually want.")
- **B. The suppressed-win probe.** Is the phenomenon real and exploitable as a training
  signal? How do you operationalize it into "forgotten-win" drills, and how do you avoid
  false positives? (AZ-SCIENTIST + LC0-DEV; TAL: why these are the moves worth training.)
- **C. Cultivating the Tal style.** How do we build a repertoire + drills that grow
  sacrificial *intuition* (not memorized lines), using TS2 steering and attacking-position
  bias? What makes a sac trainable vs a blunder? (TAL + GUKESH lead; CLAUDE maps to TS2.)
- **D. Engine-truth vs human-practical.** How to improve the human without overfitting to
  engine lines; the right drillable abstraction of "positional understanding."
  (GUKESH + AZ-SCIENTIST.)

## Required output structure (`VISION_PANEL_DISCUSSION.md`)
1. One-paragraph framing + the SIMULATED-personas disclaimer.
2. The four threads as dialogue — every line carries an idea, no filler.
3. **Synthesis table (CLAUDE-ARCHITECT owns it):**
   `Idea | Thread | What it gives the player | Feasibility tag | Uses which existing piece`
   Feasibility tag ∈ **AVAILABLE** (buildable on today's profile/TS2/saliency),
   **BUILDABLE** (new code, no new research), **RESEARCH** (needs a probe/experiment,
   e.g. suppressed-win).
4. **Top 3 "do next"** picks with a one-line why, biased toward AVAILABLE/BUILDABLE that
   directly attack *middlegame positional blindness* and/or *Tal-style* development.

## Constraints (leader will check)
- Simulated personas, labeled as such; no fabricated real quotes.
- Ground every idea in the stated tools/profile; tag anything beyond them as BUILDABLE or
  RESEARCH — never imply we already ship it.
- Concrete over poetic: an idea I can turn into a feature or a probe, not a vibe.
- No code, doc only. STOP when the md is written; this feeds the backlog, decides nothing.
