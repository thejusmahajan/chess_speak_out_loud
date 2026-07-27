# LEADER BIBLE — succession doctrine for the incoming leader (Opus 4.7)

Written by Fable 5 while leading this project; carried forward by successive leaders
(now Opus 4.8). This file is not background — it is **your operating system**. Read it
fully, then `MEMORY.md` (auto-memory). **The compute campaign is DONE** — a clean
100-game diagnosis profile landed (646 findings / 562 steer_findings, ECOs backfilled;
`data/training/profile.json`). The live campaign is now **building the training features**
per `GOAL_BOOK.md` (the product-vision anchor — read it before any feature work) and the
**theme-tagger correctness fix** in flight (see §6). Kaggle/A100 history lives in the
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
- **Gemini 3.6 Flash (High)** = implementer. Huge token pool, competent, and
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
| Opt #2 value-screen pruning: prune when **the mover** is lost (`-value < floor`, i.e. post-move side-to-move value > +0.60) | `fen_after` is opponent-to-move; raw `value < -0.60` prunes the mover's *winning* moves. Spec approved with this correction; not yet implemented. |
| Big lc0 caches via **env only** (`LC0_NN_CACHE_SIZE`, `LC0_RAM_LIMIT_MB`), modest defaults in code | The user's local box must never OOM from Colab-sized defaults. |

## 5. The failure catalog (patterns that WILL recur — recognize instantly)

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
  known baseline (backend full suite ≈ **200 passed + 5 skipped**, frontend **45**;
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

## 6. State at handover (2026-07-27 — verify then proceed)

- Branch `windows-dev`. Backend suite ≈ **200 passed / 5 skipped**, frontend **45**.
  (One TS2 test, `test_ts2_orphan_future_cancellation_handled`, is a **pre-existing
  load-sensitive flake** — a 10s wall-clock `wait_for` that fails under sustained
  suite load AND on clean HEAD; deselect it, don't chase it. See §5.)
- **Compute campaign DONE.** A clean 100-game Kaggle run produced
  `data/training/profile.json` (**646 findings / 562 steer_findings**, 54 real ECOs
  backfilled). That was the milestone the old §6 chased for days; it landed. The
  Kaggle instrument + failure family (§5b) stay as reference if compute resumes for
  the full 9000-game corpus.
- **Training features shipping one-by-one per `GOAL_BOOK.md`.** Sprints 1–4 built,
  audited, committed: S1 Usual Suspects (recurrence clustering — **sacrifice is the
  user's #1 recurring weakness**), S2 LC0 intuition speed-drill, S3 Landmine +
  Tal-sac drills + play-out-vs-LC0, S4 Sharp openings + repertoire tree; plus
  SRS-aware deck ordering (`attempts.py`, SM-2-lite).
- **THE ACTIVE FIGHT: theme-tagger correctness.** The user caught that our
  "sacrifice" was bogus (complexity, no material check — see §5 metric-mislabel +
  the `sacrifice-metric-is-bogus` memory). Grounding docs: `docs/THEME_DEFINITIONS.md`
  + `docs/LICHESS_DEVIATIONS_REPORT.md` (D1–D6). Phased fix in `THEME_TAGGER_FIX_SPEC.md`:
  - **Phase A — COMMITTED (`977edaa`):** `tactics.py analyze_pv(pre_fen, setup_uci,
    pv_san, cp)` drives Lichess `cook()` with correct pov/parity/real-cp; verified
    (Greek gift→sacrifice, material-win→NOT, g004-p031 no longer "sacrifice").
  - **UI-issues low-risk fixes — COMMITTED (`f55ac24`):** #1,4,6,8,9,11
    (`UI_ISSUES_TRIAGE.md`); #8 = honest relabel of copy only, `metrics.py` untouched.
  - **Phase B — IN FLIGHT:** split *sharpness* from real *sacrifice* + relabel. Leader
    pre-step DONE (uncommitted): `metrics.py` renamed `had_tal_move`→`had_sharp_move`,
    `tal_move`→`sharp_move` (pure rename, function-verified). Gemini task pinned in
    `GEMINI_THEME_TAGGER_PHASE_B.md` (downstream rename + re-source sacrifice from
    `findings[].motifs` + mutation tests) — dispatched, awaiting output to audit.
  - **Phase C — PENDING:** the stored profile's motifs are STILL bogus (645/646 carry a
    phantom `advantage`, 69 a phantom `sacrifice`). Re-tag WITHOUT a Kaggle re-run:
    backfill `pre_fen`/`setup_uci` from the corpus PGN, re-run corrected `analyze_pv`,
    rewrite `motifs`/`by_motif`, migrate old profile keys, then RE-VERIFY
    usual-suspects/by_motif on corrected tags (no theme verdict trusted before this).
- **After Phase C:** Sprint 5 (theme/config KB — the "why LC0 chose this" enrichment),
  Lichess auto-sync for the Q5 re-diagnosis proof loop, then the full 9000-game corpus,
  then `POST_VALIDATION_BACKLOG.md` (optical traps, attention rays, Tal persona).

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
