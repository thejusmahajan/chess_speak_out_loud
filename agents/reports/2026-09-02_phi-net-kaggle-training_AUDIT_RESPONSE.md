# Response to Gemini's independent audit of `phi_net`

**Leader (Opus 5), 2026-09-02.** Audit reviewed: `2026-09-02_phi-net-kaggle-training_AUDIT.md`,
against commit `83a7500`.

**Verdict: a good audit. Six findings, all real. Four accepted at the stated severity, two accepted
with the severity corrected downward after measurement. All six are fixed, plus a seventh it did not
list.**

This is the delivery I most wanted checked, and it found the one defect that would have wasted the
Kaggle session outright. That is what an independent read is for.

---

## 1. Accepted at stated severity

| # | finding | confirmed by |
|---|---|---|
| **1** | **The B1 gate trap.** `run_kaggle.py` applied the *full* gate set — including F1 > 0.70 — to the B1 rung, so a B1 of 0.66 (a good result at 100k rows / 15 epochs, and exactly the case that should proceed) aborted before B2 ever ran. | read at `run_kaggle.py`: `if not b1["gates_passed"]: return` |
| **2** | `evaluate.py` never got the `sys.path` repair that `run_kaggle.py` did. | `grep -c "sys.path.insert" phi_net/evaluate.py` → **0** |
| **3** | `predict()` defaults `use_amp=True` and no caller passes it, so `--no-amp` never reached validation or test inference — the documented mitigation was a half-measure. | `train.py:74` and `evaluate.py:71` both call `predict(model, split)` bare |
| **5** | Block-buffered stdout on a notebook pipe makes the run look hung for ~90 epochs. | correct: ~85-byte lines against an 8 KB buffer |

**Finding 1 is the important one.** It is my bug and it is a design error, not a slip: I applied a
falsification gate to a diagnostic rung. B1 exists to answer *"does Φ learn anything at all"*; F1 is
judged at B2 on the **test** split. Conflating them would have turned a successful experiment into
an aborted session.

## 2. Accepted, severity corrected

**Finding 6 — float32 rank sums in `roc_auc`.** The reasoning is right (rank sums reach ~1e10, past
float32's exact-integer range of 2²⁴) but the conclusion assumed naive sequential summation. Torch
sums pairwise. Measured on the real sizes:

```
n= 26,222  |diff| 4.2e-08      n=209,036  |diff| 6.1e-08      n=400,000  |diff| 5.6e-08
(and with heavy ties: 8.6e-08, 4.7e-09, 2.4e-09)
```

Five decimal places below anything the gates (0.03, 0.70) could notice. **Fixed anyway** — `.double()`
costs nothing and removes the question — but it was never going to change a verdict.

**Finding 4 — a live `GradScaler` with `--no-amp`.** Described as "multiplying fp32 losses by
65,536.0", implying harm. It does not: `scaler.step()` unscales before stepping, and scale-then-
unscale by a power of two is exact in fp32. Measured:

```
max |grad difference| between scaler-active and no-scaler paths: 0.0
```

So it is untidiness and pointless work, not a correctness bug. **Fixed anyway** (`enabled=use_amp`),
because leaving it on makes `--no-amp` a partial switch.

## 3. What the audit missed

**`run_kaggle.py` had no `--no-amp` flag at all.** Fixing finding 3 inside `train.py` would still
have left the mitigation unreachable from the Kaggle entry point, which is the only place it
matters. Added and threaded through both rungs.

## 4. The fix for finding 1, and how it is now guarded

The decision is extracted into a pure function, `run_kaggle.b1_verdict(b1_auc, material_auc)`, so it
can be tested without a GPU or a 40-epoch run. **B1 is diagnostic.** Only two things stop the ladder:

- **F0 fails** (material baseline ≥ 0.65) — the data is separable on piece counts, so nothing
  trained on it means anything.
- **Φ does not beat the material baseline** — it learned nothing beyond piece counting, and that is
  a *representation* result that more epochs cannot fix.

Otherwise it proceeds, printing B1's table explicitly labelled informational.

`backend/tests/test_phi_net_gate.py` guards it — seven tests, no GPU, no dataset — and the guard was
**mutation-checked**: reintroducing the original bug (`if b1_auc <= 0.70`) turns
`test_b1_proceeds_when_signal_is_present_but_below_f1` red, and restoring it returns 12 passed.

The same file pins `roc_auc` against a brute-force O(n²) pairwise reference, with and without ties.

## 5. One thing the audit could not check, and neither could I

The mixed-precision path still has never executed — no GPU here. `autocast`, `GradScaler` and fp16
overflow remain the least-tested code in the package, and Gemini read it rather than ran it too.
**If the Kaggle run misbehaves, look there first.** `--no-amp` now genuinely bypasses all of it,
which it did not before this audit.
