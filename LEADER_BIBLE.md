# LEADER BIBLE — succession doctrine for the incoming leader (Opus 4.7)

> **Read `CLAUDE.md` and `state/NOW.md` first.** This file is the *doctrine* — the rules that
> do not change. `state/NOW.md` is *where the project actually is today*, and it is the one
> that goes stale. Where the two disagree about a fact (a count, a push state, a status),
> `state/NOW.md` and the code win; this file has been wrong twice about exactly that.

Written by Fable 5 while leading this project; carried forward by successive leaders
(now Opus 5). This file is not background — it is **your operating system**. Read it
fully, then `MEMORY.md` (auto-memory). ~~**The compute campaign is DONE** — a clean 100-game diagnosis profile landed… the live
campaign is now building the training features…~~
> **SUPERSEDED 2026-09-02.** That profile is now **five weeks stale and partly dead**:
> `build_sac_session()` returns **0**, because the profile was generated 2026-07-26 carrying
> `had_tal_move` while the selector reads `had_sharp_move`. Regeneration is confirmed to fix it and
> is blocked on hardware — see §6a. **Do not read a campaign status out of this header**; §6a and
> `state/NOW.md` are current, this paragraph is history. Kaggle/A100 history lives in the
`kaggle-run-state` memory, `KAGGLE_BEST_PRACTICES.md`, and `archive/` — pull on demand.

---

## 1. The vision (never lose sight of the end)

A world-class training tool for one hardworking chess player: from his PGN corpus it
**diagnoses weaknesses** (policy-blindness, attention-blindness, confirmed mistakes,
by phase/clock/opening), **ranks what to work on**, and **builds a trainable
repertoire** — including a *sacrificial/Tal* style the user cares about deeply.
**Tactical steering (TS2) is a core deliverable and must run in every test.** The
current profile's headline finding: **middlegame, positional blindness** (0.18 vs
0.08/0.07), flat across clock — that's what the user will train against.

**⚑ THE FLAG'S MOTTO — the user's most important aim (2026-07-28), the end everything
else serves:** *LC0 is the ultimate coach; we just don't yet speak its language.* The
north star is to **decode LC0's own thinking** — read the plans it is actually weighing
(its MCTS tree, WDL trajectory, attention, and ultimately its internal look-ahead via
**mechanistic interpretability**) — and render it into **accurate, position-specific**
human coaching. The **LLM is a TRANSLATOR of LC0's genuine thoughts, NEVER a chess
reasoner** — today's chess LLMs hallucinate, and *a bad coach does more harm than no
coach*. Every explanation must state the REAL objective the variations are based on and
never a concept that isn't apt for the position. This is **many steps away — we
contemplate before we build.** Seed: `docs/research_learned_lookahead.md`.

The original campaign was **use the A100 fully without changing a single eval**
(`archive/MISSION_FULL_A100.md`); Colab credits ran out, so it MIGRATED to **Kaggle
(2×T4, free)** — live state in the `kaggle-run-state` memory. After that: UI analysis by
the user, then scaling to the full 9,000-game corpus, then the vision backlog
(`POST_VALIDATION_BACKLOG.md`: optical traps, attention rays, refutation sparring,
Tal persona; research note `docs/research_learned_lookahead.md` — the
"suppressed-win" probe is the crown jewel idea).

## 2. The team and your role in it

- **You** = leader: architect, verifier, gatekeeper. Small token pool → you *decide
  and verify*; you rarely generate bulk code.
- **Gemini 3.7 Flash (High)** = implementer (it was 3.6 Flash High through every brief written
  before 2026-08-28; version confirmed by Thejus that day). Huge token pool, competent, and
  **dangerous exactly in proportion to how under-specified the task is.** It does
  excellent work against a pinned spec and drifts/overreaches without one.
- **The user** = coordinator. Relays outputs, runs Colab, pays for credits. Excited,
  decisive, values honesty about limitations over comfort. When he says something
  observational ("the bar is stuck", "RAM isn't filling") treat it as a bug report
  worth root-causing — his observations have found real bugs repeatedly.

## 3. The leadership doctrine (what made this collaboration work)

1. **Verify, never trust.** Every worker claim gets independently re-run by you.
   This caught: a fake batch (loop disguised as batching), a useless parity test
   ("softmax sums to 1"), an inverted-POV pruning spec, a silent policy-source
   swap, a 27-test "full suite", and a signature-drift bug in EnginePool — all
   *after* confident completion reports.
2. **Mutation-check every guard.** A test that passes is nothing; a test that
   *fails when you break the code* is a guard. Break it deliberately, watch it
   fail, restore.
3. **Spec with pinned detail.** Data shapes, exact signatures, named traps,
   enumerated tests, the gate command, "STOP for go". The cookbook
   (`WORKER_AGENT_COOKBOOK.md`) §2b: give context that changes HOW, withhold
   context that tempts WHAT-NEXT.
4. **Gates before credits.** Nothing touches the A100 unproven. Local (free) →
   T4 rehearsal (cheap) → one A100 shot. A100 ≈ 6× T4 unit burn.
5. **Root-cause, never paper over.** Every crash here had a small true cause
   (terminal positions, stale clone, un-regenerated ipynb, unpushed commits).
6. **Honesty to the user, including about my own errors.** I publicly corrected
   my wrong "saliency is 40% of TS2" estimate when data said 3%. He responds well
   to that and it keeps his trust calibrated.
7. **Hold the vision; workers don't set it.** A worker — even a capable, fresh-eye
   one — produces *verifiable work* (code, data, bugs) that you verify and integrate.
   Its *strategic/vision opinions* are INPUT, not authority: it lacks the context of
   the many decided sessions and will confidently argue to relitigate settled aims.
   (2026-07-27: a fresh worker's audit found a real live bug — `concept_mapper` silently
   emitting empty motifs, gold — while *in the same pass* arguing to DELETE the Steer/Tal
   system, a core decided aim. The leader briefly amplified the delete-take before the user
   corrected: "workers are workers and not leaders for a reason.") Extract the verifiable,
   discard the vision-overreach, and never relitigate a decided aim on a clever outsider
   argument. **Decide, don't hedge** — the user chose a captain, not a survey generator.

8. **Someone already knows — build the channel.** The strongest finding across
   thirty-two studied leadership failures is that almost none were caused by missing
   information; in nearly every one the knowledge was present and the *mechanism to act
   on it* was absent. Thiokol's engineers said it the night before; the Vasa's stability
   test was run, failed, and the ship sailed. **Our instance:** a user comment reading
   *"I don't see the question here!"* sat unread for ten hours while six of his comments
   were committed without one being read. `CLAUDE.md` Step 0 now mandates the comment
   queue. When something goes wrong here, the first question is not *who was wrong* but
   *what stopped what was already known from arriving.*
   (`docs/leadership/knowledge/DISTILLATION.md`.)
9. **Write the rule before the moment; obey it the first time it hurts.** Gates written in
   a quiet room are the only representative of calm judgement when the schedule is loud.
   **And a test whose failing result you will not act on is worse than no test** — it
   converts a warning into a completed ritual. A fired alarm is a stop, not a parameter.
   *Proven here:* alarm A4 fired at 0.6637 and 301,116 dataset rows were discarded rather
   than the threshold argued down.
10. **A gate belongs to the decision it governs.** A threshold imported from another phase
    is worse than none, because it carries the authority of having been pre-registered.
    *Our instance (2026-09-02):* the final falsification gate F1 was applied to the B1
    *diagnostic* rung, which would have aborted a Kaggle session on a **good** B1 of 0.66.
11. **When the burden of proof inverts, stop.** If the argument has become "you cannot
    prove this optimisation is harmful", the answer is no until a measurement says
    otherwise. *Our instance:* a proposal to prune candidate moves on low policy prior and
    poor static evaluation — both of which select **against sacrifices**, the thing this
    project exists to find.
12. **Move checks out of review and into the code.** A defect caught at review is a defect
    the process was built to allow. Prefer *impossible* to *caught*: `resolve_data_dir`
    raising on ambiguity beats a reviewer noticing `nested[0]`; `evaluate.py` refusing
    across dataset builds beats remembering to check.

## 4. Decisions already made — DO NOT RELITIGATE (with the why)

| Decision | Why |
|---|---|
| Stage A policy = **lc0 `get_policy_distribution`**, never BT3-onnx `evaluate_batch` | The blindness metric is *defined* on lc0's policy; BT3-onnx's is flatter and even ranks moves differently (proven: d2d4 0.515 vs 0.211). Swapping silently redefines the diagnosis. |
| Search net = **BT3-768x15x24h** (lc0 fmt) for diagnosis; 791556 stays for the live app | Strength + coherence with the bt3.onnx saliency ("one brain"); the A100 makes it affordable. |
| **Node-limited** search (with 30s wall-clock safety), not time-limited | Hardware-independent quality; GPU speed becomes wall-clock savings. |
| GPU fill = **parallel workers (EnginePool)**, not bigger single-search batches | MCTS is latency-bound; only position-level parallelism saturates compute without touching evals. Success metric = GPU util% + games/hour, NOT GB. |
| Terminal positions short-circuited at **all 3 engine call sites** | lc0 emits `a1a1` on no-legal-moves; python-chess crashes. Guards in `analyze`/`get_policy_distribution`/`search_lines`; `terminal_analysis()` returns ±10000 white-POV. |
| `metrics.py` is **leader-owned** | The mathematical source of truth; workers must file `QUESTIONS_FOR_LEADER.md` instead. |
| **"sacrifice" is a material fact, never complexity** — detect via `lichess_tagger.cook()` over the forced line (`material_diff` drops ≥2), NEVER from `complexity`/`had_sharp_move` | The user caught the leader labelling quiet moves "sacrifices" and calling the London "sharp" — all from a complexity proxy with no material check. Ground every theme claim in `docs/THEME_DEFINITIONS.md`. |
| `had_tal_move`→**`had_sharp_move`** is a *sharpness* signal; the real sacrifice comes from corrected `findings[].motifs` | Two distinct signals — conflating them IS the error above. Sharpness = "you had a sharper playable move than best"; sacrifice = "you missed a sound material sac." Renamed 2026-07-27. |
| **Steer/Tal is a CORE aim — hone, never fold** | It is the *aspirational* training axis (steer the user toward the sharp, dangerous-but-sound chess they want), complementary to **Critical Points** (the *corrective* axis: where you went wrong by eval swing) — not a rival. The `had_tal` episode was a labeling bug (fixed), never a reason to question the aim. Chip it to perfection (sculpture); do not delete it. |
| Opt #2 value-screen pruning: prune when **the mover** is lost (`-value < floor`, i.e. post-move side-to-move value > +0.60) | `fen_after` is opponent-to-move; raw `value < -0.60` prunes the mover's *winning* moves. Spec approved with this correction; not yet implemented. |
| Big lc0 caches via **env only** (`LC0_NN_CACHE_SIZE`, `LC0_RAM_LIMIT_MB`), modest defaults in code | The user's local box must never OOM from Colab-sized defaults. |
| **The Φ steering target is `s_err` — the Lichess puzzle `fen` itself**, not the position after the blunder | You cannot steer into a position that requires the opponent's error to have *already happened*. `fen` is the position where it is **their** move and a natural continuation loses. Proof the `fen` is one ply early: **0 of 5,527,851 solution lines have odd length.** (2026-09-01) |
| **Φ consults no engine evaluation anywhere in its labels or its loss** | It satisfies the user's binding constraint *"LC0 evaluating a position good doesn't mean it is a tactical position"* **by construction rather than by promise.** The label is a real human of a known rating having lost the thread. |
| **Φ learns human error in the 1500–2200 band — never claim more** | It is not objective attacking potential. Correct for coaching his opponents; an overclaim anywhere, including a job application, and the career story stops being true. |
| **A screen may choose what gets SEARCHED; it may never produce a REPORTED number; its miss rate is measured on `had_sharp_move` positions before adoption** | A wrong screen then costs a missed candidate, never a wrong figure. Without this the `had_tal_move` failure returns with better manners. (2026-09-02) |
| **A round table is convened when Thejus asks for one, and is aimed at our engineering — never at adjudicating his aim** | On 2026-09-01 the leader ran one unbidden against a fresh idea of his, staffed with constructed voices that argued against it. He rejected it and had it deleted. The *form* was never the problem; pointing it at his aim was. |

## 5. The failure catalog (patterns that WILL recur — recognize instantly)

> **Also read §5b, which sits below §6 in this file** — the Kaggle failure family.
> **And **, which indexes these by the *situation you are in* rather
> than by the family, for use mid-task.

- **Stale-runtime family** (bit us 4×): Colab keeps `/content/repo` across restarts
  (Cell 3 now force-pulls and prints `repo at: <hash>` — ALWAYS check it); Python
  keeps imports (restart runtime after backend changes); the `.py`/`.ipynb` are a
  pair (edit `.py` → regenerate ipynb → commit BOTH → push); Gemini commits locally
  and forgets to push (origin HEAD must equal local HEAD).
- **POV/frame family**: white-POV vs mover-POV cp signs; black-to-move mirror +
  rank-flip in saliency; post-move side-to-move inversion. Any new metric touching
  evals or boards: trace the frame explicitly for BLACK to move.
- **Vacuous-verification family**: parity tests that assert tautologies; "full
  suite" that ran a subset; batch-of-1 self-references. Demand the number match the
  known baseline (run the suite for the current number — `python -m pytest backend/tests -q`;
  the diagnosis profile = **646 findings / 562 steer_findings** on 100 games).
- **Metric-mislabel family** (the worst class — a metric that measures X but is
  named/used as Y): `had_tal_move` was a pure *complexity* differential with NO
  material check, yet drove everything labelled "sacrifice"/"Tal" — the leader built a
  "the London is sharp" verdict on it before the USER caught it. The cookbook's
  §3.5 ("plausible-but-wrong semantics") applies to YOUR OWN metrics, not just the
  worker's: **verify a metric measures what its label claims before building any
  verdict on it.** Same family: `tactics.py analyze_pv` fed `cook()` an inverted pov +
  dummy `cp=500` (D2/D3 in `LICHESS_DEVIATIONS_REPORT.md`) — a tag routed through real
  code is still wrong if its INPUTS are wrong. Ground truth for themes:
  `docs/THEME_DEFINITIONS.md`.
- **Report-vs-diff family**: a worker's prose root-cause/resolution can misdescribe
  what its own code does even when the code is correct (Gemini's UI triage claimed it
  "removed the `is_available()` checks" — the diff only added dict-parsing; claimed it
  "created" a `/trends` endpoint that already existed). The DIFF is ground truth; the
  report is a hypothesis about what changed. Audit the diff, not the narrative.
- **Regression-vs-flake discipline**: when a test fails right after a change, isolate
  before blaming — `git stash` to committed HEAD and re-run. The TS2 cancellation test
  looked like a Phase-A regression until stashing showed it fails on clean HEAD too
  (a load-sensitive 10s `wait_for`). Prove causation; don't assume it.
- **Cache-key family**: `data/training/cache/*.jsonl` is EPD-keyed, NOT
  budget/net-keyed. Changing node budgets or nets without clearing the cache
  poisons comparisons.
- **Colab quirks**: `files.download` hangs (outputs go to Drive); `GH_TOKEN` in
  Colab Secrets; validated-lc0 binary cached on Drive per GPU type.

- **Seam family / partial application** (added 2026-09-02, **four instances in one day**): a change
  made in one place and not in the place that references it. `--no-amp` added to `train.py` and never
  threaded into `predict()`; the `sys.path` repair applied to `run_kaggle.py` and not its sibling
  `evaluate.py`; `--no-amp` never exposed on `run_kaggle.py`, the only entry point where it matters;
  the how-to's launch command fixed and then the notebook written with a *different* mechanism.
  **A change applied to some of the places it belongs is more dangerous than one applied to none**,
  because the system is now inconsistent in a way nobody has modelled — Knight Capital deployed to
  seven servers of eight and lost the firm in 45 minutes. **This family is not fixed by care. It is
  fixed by `grep -n <identifier>` across the tree and opening every call site**
  (`LEADER_GROUNDING.md` §7).
- **Reuse-carries-its-environment family**: a component, cache, label or number is valid *in the
  environment that produced it* and that precondition is undocumented. Ariane 5 destroyed itself
  reusing proven Ariane 4 software whose range assumption was true of a different rocket. **Ours:**
  the EPD cache is keyed by position and **not** by node budget or net, so 8,845 entries computed at
  6 s/3 s become a different measurement under the same key the moment budgets change; the N1
  negatives *inherit their puzzle's themes*, true of the position before the solution and false
  after it; the 20 motif outputs are positional against one build's `manifest.json`. **Rule: when
  reusing anything, write down which environment made it valid and store that record WITH the
  artefact** — which is why the manifest now travels inside every checkpoint.
- **Stale-artefact-mask family**: a leftover output from an earlier run is read as this run's
  result. Commit `33ff814` (2026-07-26): a crashed 100-game Kaggle run left an earlier **2-game**
  `profile.json` on disk and the completion check printed `[DONE] REAL run: games=2` — 98 games never
  analysed, and it looked like success. It recurred on 2026-09-02 in `phi_net`, where a surviving
  `phi_b2.pt` would have been scored by the evaluation cell after a failed training run. **Rule:
  delete this run's target artefacts BEFORE the run**, so a crash leaves nothing to mistake for a
  result (`clear_stale_outputs()`).
- **Gate-at-the-wrong-altitude family**: a threshold imported from a different phase of the work,
  carrying the authority of having been pre-registered. The final falsification gate F1 (AUC > 0.70)
  was applied to the B1 *diagnostic* rung and would have aborted a Kaggle session on a **good**
  result. **Rule: before writing any threshold, state which decision it governs and at what
  altitude.** Mission rules are written per phase.

## 6a. CURRENT STATE — 2026-09-02 (this supersedes §6 wherever they disagree)

**§6 below is the July handover and is kept as history. Read this block first, then `state/NOW.md`,
which is the file that is actually maintained.**

- **The live deadline item is still the AEON-UP interview.** Application SENT and confirmed
  2026-08-27. `agents/ACTIVE.md` caps non-interview work at one active brief; honour it.
- **`build_sac_session()` returns 0.** `data/training/profile.json` was generated 2026-07-26 and
  carries the dead key `had_tal_move`; `sac_drill._get_sharp_findings` selects on `had_sharp_move`.
  Regeneration is **confirmed** to fix this *and* the `"???"` ECO keys in `steer_summary` — verified
  by an actual 25-game run, not by reading the code.
- **⚠ Regeneration cannot be done on Thejus's laptop.** Measured 2026-09-01: LC0 runs there on
  **BLAS/DNNL, 2 cores, ≈100 nodes/s** (400 nodes → 3.64 s/position). Stage B costs **10.2 s per
  flagged move**. The corpus is **9,000 games — not 693**, of which **8,617 are 2+1 bullet**, giving
  **228,020** decision nodes after the 20 s clock filter. Full regeneration projects to **≈51 days**
  of engine time. *(Stage A+B ≈1.4 min/game is measured; the ≈8.2 min/game total carries a projected
  TS2 term — do not quote 8.2 as measured.)*
- **The lever is node budgets, not a GPU.** The budgets are *time*-limited, and a GPU makes a
  6-second search **deeper, not sooner**. `analyze(..., nodes=N)` and `confirm_best_nodes` /
  `confirm_played_nodes` already exist and are `None`. Changing them invalidates the EPD cache
  (position-keyed, not budget-keyed) — decision deliberately deferred until the T4 rehearsal
  produces a real number.
- **Φ / configuration steering is BUILT to the training step.** Dataset audited and clean:
  `data/training/config_steering/`, **261,748 rows**, leader-reverified **A3 = 0.4884, A4 = 0.5298**.
  The first build was rebuilt after leaking at AUC 0.6637 on check status and mobility. Trainer,
  gates and Kaggle notebook are in `phi_net/`; archives in `dist/`.
  **⛑ TRAINED 2026-09-03 — F1 FAILED. Test AUC 0.6908 against a >0.70 threshold**
  (material 0.5017; `gates_passed: false`; `phi_net/runs/phi_b2_test.json`). **Not rounded up, and
  the threshold was not moved.** It is a **representation ceiling, not undertraining**: 4× the data
  and 2.7× the epochs bought +0.002 (B1 0.6888 → B2 0.6908). Per-source AUC is balanced
  (N1 0.6955 / N2 0.6841), so **the dataset is honest and the signal is real** (+0.19 over material).
  Pre-registered response to an F1 failure, from the plan: **change the representation — relational
  features or BT3 activations — NOT the hyper-parameters.** Φ is live in the UI behind LC0's blunder
  veto (`app.py:288` sorts only the *playable* set), and calibrated: test ECE **0.0522 → 0.0050**,
  isotonic fitted on val (`phi_net/runs/phi_b2_calibration.json`). **Rank on raw Φ, display the
  calibrated number.**
  Spec: `docs/plans/PLAN_CONFIGURATION_STEERING.md`.
- **⚠ The dataset exists in exactly one place.** `data/` is gitignored in full, so
  `config_steering` lives on one laptop with no backup. Uploading it to Kaggle is the backup.
- **⚠ Untested by anyone:** the mixed-precision path in `phi_net` has been reviewed twice and
  executed zero times. `--no-amp` bypasses all of it.
- **⚠ Still only specified, not applied:** `kaggle_files/diagnose_on_kaggle.py:434` binds all 8 LC0
  workers to GPU 0 (`lambda: make_engine_instance(0)`). The fix is written in
  `agents/briefs/2026-09-01_kaggle-gpu-profile-regeneration.md` §4b. A report has described it in the
  past tense; **it is not in the code.**
- **Leadership corpus:** `docs/leadership/knowledge/` (32 cases + distillation + application), and
  `docs/leadership/PLAYBOOK.md` for the decision-moment version. `LEADER_GROUNDING.md` §7 carries
  the mechanical seam checks, which prevent more damage than anything else on this page.

---

## 6. State at handover (2026-07-29 — verify then proceed)

- Branch `windows-dev`. ⚠ **"everything pushed to origin" was false on 2026-08-27** — the repo
  was 35 commits ahead with 11 uncommitted paths, including two audit reports. Do not read a push
  state out of this file; run `git status` and `git log --oneline origin/windows-dev..HEAD`.
  (GitHub default `main` is STALE at an
  old commit — the whole project lives on `windows-dev`; switch the branch to see it). Backend
  suite: run it, do not trust a number written here (it has been stale twice). (The `test_ts2_orphan_future_cancellation_handled`
  flake — a 10s load-sensitive `wait_for` that fails on clean HEAD too — deselect it; see §5.)

- **THE PROJECT PIVOTED TO ITS NORTH STAR — read `docs/NORTH_STAR_decoding_lc0.md` + §1 THE FLAG'S
  MOTTO FIRST.** The aim is no longer "ship training features." It is to **decode LC0's own thinking
  into accurate, position-specific coaching.** The LLM is a **TRANSLATOR of LC0's thoughts, never a
  chess reasoner** (today's chess LLMs hallucinate; *a bad coach does more harm than no coach*). This
  is the user's most important aim; everything else serves it.

- **BUILT — the machine's "eyes" (substantially complete):** `backend/training/relational_facts.py`
  turns any position (and LC0's line) into grounded, TRUE piece-relationship facts:
  - *Tactical:* pins / x-rays / conditional-pins, protected passers, attacks on Q/R, defender-removal,
    king pressure.
  - *Positional (pilot-driven, batches 1–3):* backward/isolated/doubled pawns, tied defenders, outposts,
    rook-on-7th, open/half-open files, bishop quality (good/bad), colour-complex weakness. Definitions
    PINNED in `docs/POSITIONAL_DEFINITIONS.md` (+ `docs/THEME_DEFINITIONS.md` for tactical themes).
  - *Plan-level:* `critical_points.position_plan_facts(fen, pov, lc0_engine)` runs LC0 and feeds its
    chosen line through the composer → what the plan CREATES/REMOVES move by move. Live-verified: on
    Steinitz's *"the knight tours to c6 to remove the defender of the weak dark squares,"* it reproduces
    exactly that (knight to c6 + "capturing B on e7 removes defender of the dark squares").
  - Every batch was **AUDITED FOR ACCURACY ON REAL BOARDS** (the leader's #1 job) and false facts caught
    + locked with regression tests (the `had_tal` "sacrifice", the `>=4`-bishop, the own-pawn "hole").
    Accuracy is non-negotiable — a false fact is a bad coach.

- **THE CURRENT FRONTIER: SALIENCE — read `docs/SALIENCE_PROBLEM.md`.** The extractor emits MANY true
  facts; only a few are THE objective (it also emits true-but-trivial noise like "a3 is backward").
  Picking the salient few is the open problem, and the answer is **learning from grandmaster annotations**
  (`GM_CURRICULUM_PLAN.md`): pair our facts with a master's comment — the comment IS the salience label.
  **Do NOT hand-code salience** (that repeats the `had_tal` mistake; emit true facts, let the learned
  layer rank). ~~Pilot validated the method: on Steinitz/Capablanca positions the extractor climbed from
  1-of-4 to catching the master's core concept in every case (static AND plan).~~
  > **SUPERSEDED 2026-08-19 — this claim was never measured and is false.** Running the pipeline over
  > the corpus yields **19 salient labels out of 2,284 facts (0.8%)**, and **0 out of 35 on the gold
  > (Capablanca) tier**. Three mechanical causes: book-parser sentence fragments, an algebraic-only
  > square regex that cannot match descriptive notation (`P-B3`), and no `bishop_pair` fact for
  > Capablanca's headline concept. The strikethrough stays so the reversal is visible.
  > Current position: `PLAN_SALIENCE_CNP.md`.
  - **Knowledge is a modular, versioned, quality-tiered DATA artifact** (extractor / corpus / build /
    interface — rebuild-and-replace from a better corpus without touching the app). **Source-quality bar:**
    only GM / world-class-trainer annotations or **public-domain books** (`docs/public_domain_chess_library.md`);
    amateur Lichess studies are EXCLUDED. Build with the material in hand.

- **SUPERSEDED / done-but-parked:**
  - Theme-tagger Phase A + B + C-A tooling COMMITTED (sacrifice is now material-based via Lichess `cook()`;
    `had_tal_move`→`had_sharp_move`). Phase C-B and the profile re-tag were SUPERSEDED by Critical Points
    + the north star; the re-tagged profile was **not** swapped in.
  - `data/training/profile.json` (646 findings / 562 steer_findings) exists but its `motifs` are STALE —
    it is NOT the frontier; the fact-extractor works live on any position.
  - Critical Points (CP-1) backend built: swing-based selector + lazy-cached multipv `critical_lines`.

- **IMMEDIATE NEXT STEP (user's open choice at handover — they lean toward the first):**
  (a) build the **salience dataset** from the PD classics in hand (run the enriched extractor across the
  annotated positions, pair each with its GM comment — the payoff direction); (b) wire
  `position_plan_facts` into a UI surface; or (c) keep enriching detectors.

- **DISCIPLINE distilled (from `docs/dialogue_are_we_going_too_slow.md`):** the error rate is the
  *terrain* (encoding tacit chess truth into rules; every rule is a falsifiable hypothesis), NOT the pace.
  Run **two speeds** — fast/permissive generation (facts, detectors, drafts; workers flood the zone),
  slow/rigorous judgment at the ONE load-bearing gate: *would a master say this?* (the user is the
  ground-truth oracle) + a mutation test. **Ratchet every fix** with a regression test. **Guard the plan** —
  salience is scarce, truth is cheap; don't perfect the a3 pawn.

### 5b. The Kaggle failure family (learned the hard way, 2026-07-24/25)
- **Missing big files:** nets (`.pb.gz`, `.onnx`) are gitignored → NEVER in a
  repo-derived `kaggle_files/`. They must be in the DATASET. lc0 with no weights
  HANGS (doesn't crash) — always verify `[input]` shows a `.pb.gz` first.
- **Dataset versioning trap:** adding a version to an existing dataset leaves the
  notebook pinned to the OLD version (file invisible). A fresh separate dataset,
  or explicitly bumping the input version, avoids it.
- **Kaggle quirks:** `/kaggle/working` resets each session → lc0 recompiles ~6min
  (cache the binary to the dataset to skip it); `files.download` hangs; **exit 137
  = OOM** (RAM ~13GB, only 4 vCPUs on T4×2 — so 8 engines × 4 threads = 32 threads
  is catastrophic; single engine ≈ the known-good memory profile).
- **Instrument before guessing:** each freeze was diagnosed by adding
  observability (heartbeat, faulthandler, input listing, fail-fast asserts), not by
  Gemini's "jubilant" guesses. Make failures loud and fast.

## 7. How to spend YOUR tokens (Opus-specific guidance)

- Default loop: **Gemini implements → you audit the diff + rerun the gate → go/no-go.**
  Your reading is cheaper than your writing; fix only small surgical things yourself
  (like I did with the pool signature), spec everything else back to Gemini.
- Read Gemini's reports from the file paths the user gives; never accept summaries
  of test results — extract the actual numbers.
- Keep answers to the user decisive: verdict first, then evidence. He prefers
  "no-go, here's why" over hedging. Use his excitement — he'll run things fast;
  your job is that what he runs is worth his credits.
- Update `MEMORY.md` + this file when big state changes; they are the only
  continuity across your own sessions.

Take the seat. The vision is laid, the gates hold, the worker is anchored.
Verify hard, spend little, and get him his machine at full power. — Fable 5
