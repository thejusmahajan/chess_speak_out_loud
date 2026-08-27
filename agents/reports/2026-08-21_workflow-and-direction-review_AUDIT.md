# AUDIT — `2026-08-21_workflow-and-direction-review`

**Audited:** 2026-08-22 by the leader (Opus 5)
**Delivery:** `agents/reports/2026-08-21_workflow-and-direction-review_REPORT.md` (20,674 bytes)
**Verdict: ACCEPT.** The best-evidenced worker delivery in this project's record. It corrected two
leader measurement errors, independently found the live CV violation, and produced one confirmed
code-level North Star violation that no previous audit caught.

---

## boundary check

```
$ git status --short
 M agents/ACTIVE.md              <- leader (brief registration + this audit's ledger row)
 M trainer/engine.py             <- leader (new ladder defaults)
 M trainer/state/answers.jsonl   <- pre-existing, Thejus's own study sessions
 M trainer/state/progress.json   <- pre-existing, Thejus's own study sessions
?? agents/briefs/2026-08-21_workflow-and-direction-review.md
?? agents/reports/2026-08-21_workflow-and-direction-review_REPORT.md   <- the ONLY worker artefact
?? gemini_stable_drill_ids_srs.txt   <- pre-existing, predates this brief
?? trainer/content/ladders/bridge.json          <- leader
?? trainer/content/ladders/hereon_aeon_up.json  <- leader
```

The brief said "one file, and nothing else. Change no other file. Write no code. Commit nothing."
The worker wrote exactly one file and committed nothing. **Scope clean.**

---

## gate re-run — my commands, my output

The report makes four checkable counting claims. I re-ran all four myself.

```
$ find . -name '*.md' -not -path './.git/*' | wc -l                              -> 432
$ find . -name '*.md' -not -path './.git/*' -not -path '*/node_modules/*' | wc -l -> 262
$ find ./frontend/node_modules -name '*.md' | wc -l                              -> 170
$ grep -n '^> \*\*STATUS:' *.md
GM_CURRICULUM_PLAN.md:1:> **STATUS: SUPERSEDED 2026-08-19 by `PLAN_SALIENCE_CNP.md`.** ...
LEADER_GROUNDING.md:208:> **STATUS: SUPERSEDED 2026-08-19 by <file>.** Kept for the record; do not act on it.
```

**Two leader errors, both correctly caught by the worker:**

1. My brief pinned **430** non-vendor markdown files. Wrong. My exclusion pattern
   `-not -path './node_modules/*'` is root-anchored and never matched `frontend/node_modules`,
   which holds 170 `.md` files. The worker spotted the cause and said so explicitly. This is
   pre-flight check 1 (*every literal machine-verified*) failing again — I ran a command and
   trusted its output without checking that the command meant what I thought.
2. My brief pinned **2** root files carrying a `STATUS:` header. Substantively wrong: the second
   match is `LEADER_GROUNDING.md:208`, which is the *template* for the convention printed inside
   a fenced block, not a file declaring itself superseded. The real count is **1**. The worker's
   number is the correct one.

**One worker error, minor, in the same material:** it reports 261 non-vendor files where I
re-derive **262**, and cites the header at `GM_CURRICULUM_PLAN.md:3` where it is at line **1**.
Both are off-by-one and neither changes any conclusion. Recorded, not held against the delivery.

---

## mutation proof

The report is a document and has no gate of its own to mutate. I mutation-tested the gate
protecting the artefact I built alongside it, since that gate now guards the new cards:

```
# broke her-l1-001's sources to a non-existent path
[FAIL] Found 2 content verification error(s):
  1. Card 'her-l1-001': Cited repo source path does not exist on disk:
     '../job_search/applications/hereon_aeon_up/NO_SUCH_FILE.md'.
  2. Card 'her-l1-001': Sourced exclusively from session logs/transcripts. ...

# restored
[PASS] All content, grounding, and constraint gates passed!
byte-identical after restore: YES
```

The gate is causal for the new content, not decorative.

---

## independent re-derivation — by a different path than theirs

The report's highest-consequence claim is Part C §2: that the LLM is asked to reason about chess,
violating the North Star. I did not re-read their citations; I traced the call path myself.

```
backend/app.py:42     LLM_ENABLED = False  # Aim: bypass all text-generation.
                                           # Keep code dormant, never call at runtime.
ARCHITECTURE.md:30    "**Dormant**. ... disabled behind the `LLM_ENABLED` flag."
HOW_TO_RUN.md:90      "dormant by design ... Don't wire it into the runtime."

backend/app.py:658    tree = await explanations.enrich_tree_explanations(tree)   <- UNCONDITIONAL
backend/training/explanations.py:5-71   no LLM_ENABLED check anywhere in the function
backend/training/explanations.py:63     await llm_client.generate_move_explanation(context, model)
```

**CONFIRMED, and worse than the report states.** `enrich_tree_explanations` contains no
`LLM_ENABLED` guard at all — I read the whole function, not a grep hit. The call at
`app.py:658` is unconditional on the repertoire-tree endpoint. The context assembled at
`explanations.py:44-62` is FEN, move UCI, `eval_cp`, `critical_reason`, `user_blind_rate` and
opponent replies: **no LC0 search tree, no policy prior, no relational facts.** The model is
asked to produce chess coaching from a position and a number.

So three documents assert the LLM path is dormant while one endpoint calls it. This is the exact
shape of the failure `LEADER_GROUNDING.md` §3c.6 names — *"a rule that is not mechanically
enforced will be violated while being quoted"* — and `LLM_ENABLED = False` is a sign, not an
interlock.

I also independently confirmed the report's Part D finding before reading the report, while
grounding new trainer cards: `cv_hereon_aeon_up.tex:51` still reads
`{Mechanistic interpretability of transformer neural networks`. Two independent paths to the same
live defect in a document that was about to be submitted.

---

## what I could not check

**Non-empty by design. Read this section first.**

1. **Whether the LLM path actually fires in production.** I confirmed the code path is live and
   unguarded. I did not confirm that `google.generativeai` is configured with a working key at
   runtime, so the call may currently raise and be swallowed rather than emit text. The defect is
   real either way — an unguarded call to a chess-reasoning LLM — but "is Thejus seeing invented
   coaching text today" is unresolved. **This is the first thing to determine.**
2. **The report's percentage claims about the cover letter** (~45% chess bugs, ~25% ERGOM/NetCDF)
   are the one place it gives numbers without showing a derivation. They read as estimated. I did
   not re-measure them, and I would not act on them without doing so. The *qualitative* point —
   that the letter leans heavily on the chess narrative for an audience of atmospheric modellers —
   is independently plausible and worth Thejus's own judgement.
3. **The visual PDF inspection.** The worker says it opened both PDFs and describes page counts,
   dating and layout. I did not re-open them. Its description is consistent with the `.tex`
   sources and file sizes, which is corroboration, not verification.
4. **Part B's proposals and Part C's rankings** are opinion, correctly labelled as such, and are
   not the kind of claim an audit can confirm. They are inputs to a decision, not findings.
5. **"18 questions in `05_interview_questions.md`"** (Part D §4) — `00_START_HERE.md` says 17.
   Not re-counted; immaterial.

---

## what my brief got wrong

Beyond the two counting errors above:

- The brief described Thejus as **"a ~1500-2000 player"**. Wrong, and I should have checked:
  `GOAL_BOOK.md:17` says *"A ~2100–2200 Lichess player"*. 1500–2000 is the **puzzle-difficulty
  band** of the Puzzle Storm regime (`docs/PUZZLE_STORM_REGIME.md:1`), not his rating. I
  conflated a training-set parameter with the user. The worker silently used the correct figure
  from `GOAL_BOOK.md` rather than the wrong one I handed it — the right call, though I would
  rather it had flagged the contradiction than quietly routed around it.

Three errors of mine in one brief, all of the same species: a number I produced myself and did not
interrogate. Pre-flight checks 1, 6 and 7 each would have caught one.
