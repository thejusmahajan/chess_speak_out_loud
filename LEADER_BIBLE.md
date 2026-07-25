# LEADER BIBLE — succession doctrine for the incoming leader (Opus 4.7)

Written by Fable 5 while leading this project. You (Opus 4.7) are taking my seat.
This file is not background — it is **your operating system**. Read it fully, then
`MEMORY.md` (auto-memory), `MISSION_FULL_A100.md`, `GEMINI_HANDOFF.md`. Everything
else you can pull on demand.

---

## 1. The vision (never lose sight of the end)

A world-class training tool for one hardworking chess player: from his PGN corpus it
**diagnoses weaknesses** (policy-blindness, attention-blindness, confirmed mistakes,
by phase/clock/opening), **ranks what to work on**, and **builds a trainable
repertoire** — including a *sacrificial/Tal* style the user cares about deeply.
**Tactical steering (TS2) is a core deliverable and must run in every test.** The
current profile's headline finding: **middlegame, positional blindness** (0.18 vs
0.08/0.07), flat across clock — that's what the user will train against.

The active campaign: **use the A100 fully without changing a single eval**
(`MISSION_FULL_A100.md`). ~20% of Colab credits remain. After that: UI analysis by
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
  known baseline (full suite ≈ **141 passed + 5–6 skipped**; subset baseline
  findings=28/steer=22-truncated; complete-steering baseline pending).
- **Cache-key family**: `data/training/cache/*.jsonl` is EPD-keyed, NOT
  budget/net-keyed. Changing node budgets or nets without clearing the cache
  poisons comparisons.
- **Colab quirks**: `files.download` hangs (outputs go to Drive); `GH_TOKEN` in
  Colab Secrets; validated-lc0 binary cached on Drive per GPU type.

## 6. State at handover (verify, then proceed)

- Branch `windows-dev`. Full suite ~141 passed. Baselines: last A100 subset run =
  30 games, findings 339 (subset-run scale) / earlier canonical quick-baseline
  28/22; **openings fix (`f845a26`) and complete-steering budget are in origin but
  NOT yet validated by a fresh Colab run** — the next A100 run produces the first
  fully-correct profile.
- **Mission phase**: Phase A (EnginePool) done+audited at `98f2ea5`.
  Phase B (parallel Stage B/TS2) implemented by Gemini, audited + committed by
  Opus 4.8: all 3 traps verified (sync budget helpers, in-flight-future dedup,
  TS2 `.sort` mutation-verified load-bearing; Stage B uses order-preserving
  `gather`). Gemini's identity gate was BROKEN (cache-dependent on our truncated
  cache, not store-isolated, load-after-error) — I replaced it with a
  cache-independent, store-isolated, deterministic-engine gate proving n=1≡n=4
  (findings+steer), mutation-verified. Suite green. **Caveat:** identity holds in
  the non-binding-budget mode (the A100 run's mode, STEER_SEARCH_BUDGET=50000); if
  the budget BINDS under concurrency, which nodes win the last slots is
  timing-dependent — acceptable degraded mode, not operated in.
  NEXT: Phase C (optional short Opus-4.6 pass) then Phase D (T4 rehearsal → one
  A100 shot). Notebook wiring of `EnginePool(LC0_WORKERS)` into Cell 5 is still
  TODO (spec in `MISSION_FULL_A100.md` Phase D).
- Pending after mission: Opt #2 implementation (spec approved w/ POV fix),
  `by_opening` validation in the fresh run, then the user's UI analysis.

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
