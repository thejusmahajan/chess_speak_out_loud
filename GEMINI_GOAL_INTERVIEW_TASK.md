# TASK FOR GEMINI — Interview the user to build the GOAL BOOK (elicitation, NOT coding)

The user is a **serious chess student** with a rich training vision for this tool. We will
build its capabilities **one by one**, and before building each we need PRECISION about what
he actually wants. Your job now is to **quiz him** — produce a well-organized, PRIORITIZED
set of questions whose answers let the leader (Claude) synthesize a durable **`GOAL_BOOK.md`**
that drives development. Ask, don't solve. Depth over polish — he explicitly is "not
interested in shiny stuff."

## The flow this feeds (so you frame questions to serve it)
1. You write `GOAL_ELICITATION_QUESTIONS.md` (this task).
2. He answers (in his own words).
3. Gemini drafts an analysis; **the leader audits and owns the final `GOAL_BOOK.md`.**
4. Then: gather the knowledge to execute each goal, then execute — one at a time.
So every question must earn its place by unblocking a real design decision.

## Grounding — what the tool ALREADY does (connect aspirations to buildable reality)
Ask questions that bridge his vision to THIS engine, not abstract wishes:
- **BT3 policy** → a "policy-blindness" metric (where his move sits vs LC0's move
  distribution) and LC0's ranked candidate moves with probabilities.
- **BT3 attention (`saliency_absolute`)** → per-square heatmap of what the net "attends to".
- **lc0 node-limited search** → confirmed mistakes, eval swings, WDL, best lines.
- **TS2 tactical steering** → per-position `steer_findings`: a "steer" (often sacrificial/Tal)
  move vs the objective best, with a **complexity** score broken into components
  (decisiveness, narrowness, policy_trap, attention) + `had_tal_move`.
- A **diagnosis profile**: findings by phase/clock/motif/concept, aggregates, 256 steer
  candidates incl. **63 sacrificial/Tal** moves, and a repertoire builder.
- Current state: diagnosis works well; the **training/UI experience is where we're far from
  the aim.** (Opening/ECO grouping is currently broken — being fixed separately.)

## His vision — VERBATIM (preserve his exact words in the doc; they are the source of truth)
Cluster the questions around these eight jobs-to-be-done:
1. "Steer a position towards a tactical landmine."
2. "Find positions in the usual openings I play where I can take the game to complex
   positions, a tight rope walking game, where every decision matters."
3. "Train me such expected positions where a kind of tactical positions dominate and train me
   in those tactical themes so that I don't miss it."
4. "I want to train to see how LC0 views a position."
5. "Develop intuition like LC0."
6. "Correct the usual suspects pervading in my games."
7. "Tactical themes I am afraid to take, like a pawn sacrifice that Tal would make, and such
   positions happen over and over again with the same blindness."
8. "Categorize my weaknesses and train me solve them one by one."

## For EACH job, your questions must extract these GOAL-BOOK fields
- **Definition**: what precisely counts as (e.g.) a "tactical landmine" / "tightrope
  position" / "the same blindness"? What's true of a GOOD one vs a bad one the tool surfaced?
- **User story / workflow**: concretely, what does he do, what does the tool show, what does
  he do next? (a step-by-step of one session.)
- **Success criteria**: how would he KNOW it's working / training him — what would make him
  say "yes, this made me better"?
- **Mapping to the engine**: which existing signal(s) above plausibly power it (so we know
  what's near-term vs research).
- **Priority & MVP**: how important vs the others, and the smallest version that would already
  be useful.

## The KIND of questions to ask (exemplars — match this depth, don't copy verbatim)
- "Walk me through a real recent game where you wish this tool had helped. What happened, and
  what would you have wanted it to show you — before, during review, or as training after?"
- "When you say 'tactical landmine,' picture the ideal position the tool hands you. What is
  true about it? (only one good move? a tempting wrong move? a sacrifice on offer? your
  opponent likely to go wrong?) Rank what matters most."
- "'Tightrope, every decision matters' — is that about the POSITION's sharpness, or about
  training YOUR decision-making under pressure? What would the drill actually make you do?"
- "For 'see / develop intuition like LC0' — which teaches you most: (a) see LC0's top move +
  a why, (b) you guess LC0's move then compare, (c) see the attention heatmap of what LC0
  'looks at', (d) predict which side is better and by how much? Pick and explain."
- "'Same blindness over and over' — do you want the tool to PROVE a pattern recurs (e.g. 'you
  declined a sound pawn sac in 9 games') before drilling it? How many repeats = a real theme?"
- "'Solve them one by one' — one theme per week? Spaced repetition until mastered? What does
  'mastered' mean to you?"
- "Of all eight, if only ONE existed next month, which moves your chess the most — and why?"

## Meta / context questions (also ask — the leader needs these)
- Chess profile: rating(s) + platform, main openings as White and Black, time controls,
  ~games/week, and how you study TODAY (puzzles? game review? books? coach?).
- Diagnosis vs training: should training positions be AUTO-generated from your games, or
  curated/approved by you first?
- Progress: do you want the tool to TRACK a weakness over time ("missed this theme 12×, now
  2×")? How do you want to see improvement?
- The "serious, not shiny" bar: what would make you trust a feature is REAL training vs a toy?
- Constraints: how long is a study session, on what device, how often?

## Output format & constraints
- File: `GOAL_ELICITATION_QUESTIONS.md`.
- **Tier the questions** so he isn't overwhelmed (he said "too much all at once"):
  - **Tier 1 — Foundations (answer first, ~6–8 Qs):** the meta/context + the "which ONE
    first" prioritization + the general workflow question.
  - **Tier 2 — Per-job deep dives:** grouped under each of the 8 jobs, to be answered in
    later rounds (he can do a few clusters at a time).
- Each question gets a one-line **"why this matters"** (the decision it unblocks).
- ASK, do not propose solutions or designs. Leave explicit room for "I don't know yet /
  let's discover this together." Preserve his verbatim phrases. Keep it a document a busy
  serious student can actually answer. STOP when written.
