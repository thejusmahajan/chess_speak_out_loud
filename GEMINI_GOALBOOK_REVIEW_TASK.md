# TASK FOR GEMINI — Second opinion on the leader's GOAL_BOOK synthesis (critique, don't rewrite)

The leader (Claude) read the user's answers in `GOAL_ELICITATION_QUESTIONS.md` and synthesized
them into `GOAL_BOOK.md`. Your job is an **adversarial second opinion**: find where the leader
**misread, over-inferred, mis-prioritized, or missed something the user actually said.** This is
high-stakes — the GOAL_BOOK drives all future development, so a misread here compounds. Report
only; do NOT rewrite the GOAL_BOOK. Output `GOALBOOK_REVIEW.md`.

## Read both, side by side
- `GOAL_ELICITATION_QUESTIONS.md` — the user's raw answers (the ground truth).
- `GOAL_BOOK.md` — the leader's synthesis. Note its **[E]** (explicit) vs **[I]** (inference) tags.

## What to check (cite the specific answer + the GOAL_BOOK line for each)
1. **Faithfulness:** Does every **[E]** claim actually match what the user wrote? Quote the
   answer. Flag any [E] that is really an inference (should be [I]), or any claim with no basis.
2. **Misreads:** Any place the leader misunderstood the user's intent? (e.g., the
   theme/piece-configuration "backbone" thesis — is that genuinely central to Jobs 1/2/3/7, or
   is the leader over-fitting? The "dry openings → sharp/Tal" north star — supported?)
3. **Prioritization:** The user's #1 (Q3) is recurring-mistake identification → the leader made
   that Sprint 1. Correct? Does the proposed sprint SEQUENCE respect his stated priorities AND
   the real dependencies (e.g., does J1/J7 truly depend on the theme KB in Sprint 3)? Any sprint
   that should move earlier/later given his answers?
4. **Omissions:** Anything the user said that the GOAL_BOOK dropped or under-weighted? (Scan
   every Tier-2 answer for a concrete want that isn't represented — e.g., "example games from
   master DB / his own games" for landmines; "explain WHY LC0 favors a move via the tactical
   config"; the review/approve gate; the play-out-vs-LC0 requirement recurring across jobs.)
5. **Contradictions / tensions:** Any conflict between answers the leader smoothed over? (e.g.,
   "3 reps is fine" vs "90% over 30 days" vs "mastery = OTB recognition" — are these reconciled
   correctly? "automated" vs "review and approve"?)
6. **Open questions:** Did the leader flag the right unknowns (repertoire not fully given; the
   1.e4 switch; heatmaps parked; "similarity ∝ loss factor" undefined)? Any OTHER unknown that
   must be re-elicited before building Sprint 1?

## Output — `GOALBOOK_REVIEW.md`
- A table: `GOAL_BOOK claim/line | user answer (quoted) | verdict: FAITHFUL / OVERREACH /
  MISREAD / MISSING | note`.
- A short list: **"Must fix before the GOAL_BOOK is trusted"** (the high-severity items).
- A verdict on the Sprint sequencing (agree / change, with the user-answer basis).
- Anything the user implied that neither the leader nor these questions captured — worth a
  follow-up question.

## Constraints
- Ground EVERY critique in a quoted user answer; if you can't quote it, it's your speculation —
  label it as such. Do not invent user preferences. Critique, don't redesign. STOP when written.
