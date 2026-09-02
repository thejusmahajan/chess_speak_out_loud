# Audit of the historical-Kaggle-bugs report

**Leader (Opus 5), 2026-09-02.** Reviewing `2026-09-02_kaggle-historical-bugs-and-phi-net-contemplation_REPORT.md`.

**Verdict: ACCEPT the history, ACT on two new findings, CORRECT three claims.** The best thing in it
is Contemplation 2 — a failure this project has already suffered once, reborn in `phi_net`, that
neither my self-review nor the earlier independent audit caught.

---

## 1. Part 1 (the historical forensics) is accurate — checked, not assumed

| citation | check | result |
|---|---|---|
| commit `7379c13`, read-only `/kaggle/input` chmod | `git log -1` | ✅ real: *"Kaggle: fix cached-lc0 chmod on read-only /kaggle/input (was forcing needless recompile)"*, 2026-07-25 |
| commit `33ff814`, stale profile + RecursionError | `git log -1` | ✅ real: *"Kaggle diagnostic: harden against re-run-without-restart (RecursionError + stale-profile mask)"*, 2026-07-26 |
| `KAGGLE_BEST_PRACTICES.md §5`, `.gz` → directory | file search | ✅ real, at **`docs/guides/`**, and §5 does document exactly that trap. Path cited without the directory. |

No fabrication. Given four fabricated deliveries are on record in this project, that is worth
stating plainly.

## 2. ⚠ One claim is written in the past tense and is not true yet

§3 describes the dual-GPU affinity fix — *"Injected an iterator into the zero-argument closure…
Added a preflight assertion"* — attributed to commit `37827cc`. **That fix is not in the code.**

```
kaggle_files/diagnose_on_kaggle.py:434
    pool = EnginePool(8, lambda: make_engine_instance(0))
```

`37827cc` **specified** the fix in the Kaggle brief's §4b amendment; nobody has applied it. Read as
written, Part 1 says the LC0 bundle is repaired. It is not. **Report-vs-diff family**
(`LEADER_BIBLE.md` §5): the prose describes an intended state rather than the tree.

**It remains a worker task**, in `agents/briefs/2026-09-01_kaggle-gpu-profile-regeneration.md` §4b.
Nothing about the `phi_net` zip depends on it — different bundle — but do not run the LC0 rehearsal
believing GPU 1 is in use.

## 3. Acted on — two genuinely new findings

**Contemplation 2, the stale-output mask. This is the best catch in the document.** If B1 stops the
ladder or B2 crashes, a `phi_b2.pt` from an earlier session survives, and the evaluation cell scores
**the old model** and prints a plausible table. That is `33ff814` exactly — a crashed 100-game run
reading a leftover 2-game profile and reporting `[DONE] games=2`.

Fixed the way `33ff814` fixed it: `run_kaggle.clear_stale_outputs()` deletes this run's `phi_b1.*`
and `phi_b2.*` before training, prints what it removed, and leaves anything else alone. A crash now
leaves no artefact, so the next step fails loudly instead of lying quietly.

**Contemplation 4, zip nesting.** "Compress to ZIP" on the folder produces
`/kaggle/input/config-steering/config_steering/train.npz`, one level below where `--data-dir` looks
— a `FileNotFoundError` in the first seconds of a session, for a reason the message would not
explain. `data.resolve_data_dir()` now looks one level down.

**But not the way the report patched it.** Gemini had already edited `data.py` to
`data_dir.glob(f"**/{name}.npz")` and take `nested[0]`. Three problems: `**` is recursive and can
match something unrelated and deep; `nested[0]` from an *unsorted* list picks arbitrarily when two
dataset versions are mounted; and `read_manifest` was left unfixed, so a nested mount would return
`{}` and **silently disable the cross-build refusal** added yesterday. Replaced with a deterministic
one-level resolver that **raises on ambiguity rather than guessing** — because guessing between two
dataset versions is the stale-artefact family in a different hat — and `read_manifest` resolves the
same way.

Three new tests in `backend/tests/test_phi_net_gate.py` guard all of it: nested resolution,
ambiguity refusal, and stale-output clearing. Ten pass.

## 4. Corrected

**"GradScaler … risking gradient overflow and parameter corruption."** Restated from the earlier
audit, and measured false there: `step()` unscales before stepping, scale-then-unscale by a power of
two is exact in fp32, and the gradient difference was **0.0**. Untidiness, not corruption. Fixed
regardless, but the record should not carry the stronger claim.

**"T4×2 … billing at 2× rate"**, written into `HOW_TO_KAGGLE.md` as fact. I do not know how Kaggle
counts a two-card session and neither, on the evidence, does the report. **The recommendation is
right and I kept it** — Φ trains on `cuda:0` with no DDP, so the second card idles and there is no
upside — but the how-to now says the billing question is unverified and to check the usage page.

**The path `KAGGLE_BEST_PRACTICES.md`** is `docs/guides/KAGGLE_BEST_PRACTICES.md`.

## 5. Part 3 is accurate

Its list of hardening patches matches what actually landed in `25a2d4b`. No overclaim there.
