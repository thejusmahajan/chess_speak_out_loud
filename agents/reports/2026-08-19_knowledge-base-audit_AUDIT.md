# AUDIT — `2026-08-19_knowledge-base-audit`

**Auditor:** Leader (Claude Opus 5) · **Date:** 2026-08-19
**Verdict: ACCEPT.** The strongest design deliverable this project has received from a worker.
Every finding I spot-checked holds, including one genuine CRITICAL I had not seen. It is honest
about a real coverage gap, and **that gap hid a live violation which I found and fixed.**

---

## 1. Boundary check — PASS

One file written, nothing else touched, nothing committed. Explicitly confirmed no knowledge-base
file was "corrected" — which was the instruction most open to well-meaning violation, since
several of these documents are worded the way they are because a lesson was paid for.

## 2. Findings I verified independently

| # | Finding | Verdict |
|---|---|---|
| 1.1 | `CV_AI_MODULE.md` says black-to-move internal index 0 is **h8** | **CONFIRMED — CRITICAL** |
| 1.2 | `LEADER_BIBLE` forbids hand-coded salience; `INFERENCE_PRIORS` is exactly that | **CONFIRMED** |
| 1.3 | `LEADER_BIBLE:175` "pilot validated the method… caught the core concept in every case" | **CONFIRMED false** — measured 0/35 on gold |
| 2.2 | `HOW_TO_RUN:20` "`requirements.txt` is intentionally empty" | **CONFIRMED false** — 36 lines of pinned deps |
| 2.4 | MSE-softmax derivative missing off-diagonal terms | **CONFIRMED** — its correction matches the true Jacobian |
| 3.1/3.2 | `LEADER_BIBLE` states 200 passed at :115 and 239 at :146 | **CONFIRMED** — contradicts itself, both stale vs **302** |
| 3.4 | `COMMAND_BASE:43` links to `docs/career/*` | **CONFIRMED** — the directory is empty |

### 1.1 in detail — the best catch in the report

`docs/CV_AI_MODULE.md` sits under the heading *"Tell me about a bug you found." ← your strongest
interview story; lead with it.* It stated that for a black-to-move position, internal square index
0 is **h8**.

The code does `move.from_square ^ 56`, commented `"""Vertical flip of a move (a1<->a8)"""`. XOR 56
flips rank only and preserves file:

```
idx  0 (a1) -> 56 (a8)      idx 28 (e4) -> 36 (e5)
```

"Index 0 is h8" would require `^63` — a 180° rotation that also mirrors files, a *different*
transformation. The published write-up gets it right (*"reflected through the horizontal axis —
a1↔a8, e4↔e5, h2↔h7"*); only the crib sheet was wrong.

So the error lived exactly where it does most damage: **not in public, but in the document he
would rehearse from before saying it out loud** — while telling the story that demonstrates his
rigour. **Fixed.**

## 3. The gap the worker declared — and what was hiding in it

Part 6 states plainly that `C:\Users\Admin\Documents\job_search\` was outside its workspace, so
**Tier 2 study material was audited via an in-repo specification rather than the files
themselves.** Declaring that instead of glossing it is exactly right, and it is what let me find
what follows.

The substitute matters: `WORKER_TASK_AEON_UP_STUDY_ROOM.md` is a *specification for* the study
room, not the study room. In particular the forbidden-claims sweep ran against §1.5 of that spec,
not against the real `study_room/06_do_not_claim.md`.

**I ran the real sweep. It found a live violation in the CV about to be submitted:**

`cv_hereon_aeon_up.tex:158` listed, among his skills:
> `attention/activation capture (forward hooks), mechanistic interpretability, ONNX→PyTorch conversion…`

`06_do_not_claim.md` Boundary 2 forbids precisely this:
> *NEVER CLAIM: causal interventions, activation patching, or mechanistic circuit discovery… Talking
> about "mechanistic interpretability" when you have only extracted forward-hook activations will
> expose you to deep questioning. Frame your ML work strictly as PyTorch pipeline engineering,
> representation extraction, ONNX translation, and batched inference optimization.*

The CV claimed the term his own preparation forbids — to Karl and Ramacher, who would ask. Worse,
`CV_AI_MODULE.md:80` already contains the correct answer for when asked, so he would have been
walking back his own CV in the room.

**Fixed:** the skills line now reads `representation extraction`, using the do-not-claim file's own
sanctioned wording. CV rebuilt, 2 pages, `mechanistic` no longer appears.

*(Two other hits are fine and stay: the blog post's `<meta keywords>`, and a line in the post that
correctly states the limitation — "establishing that a component is load-bearing requires an
intervention — ablation or activation patching — not a heatmap." That is the honest framing.)*

## 4. Where I differ from the report

- **3.5 is understated.** Stub chapters listed in a concept index are not `LOW` if that index feeds
  the trainer — a card sourced to a stub would be a card with no content behind it. Raise to
  MEDIUM and exclude those chapters from trainer sourcing.
- **Part 5's authority ladder puts `agents/ACTIVE.md` above code.** I disagree. Code plus a passing
  test is the strongest evidence in this repo; the ledger records *what an audit concluded*, which
  is a claim about code. Correct order: **running code and tests → audits → doctrine → history.**
- **Part 5.5's proposed doc-integrity test is a good idea**, but item 4 ("check `INFERENCE_PRIORS`
  is not modified without doc updates") is unenforceable as stated and would just be disabled.
  Items 1–3 are cheap and worth building.

## 5. Fixed now

1. `docs/CV_AI_MODULE.md` — `index 0 is h8` → `index 0 is a8`, with the transformation named
   explicitly ("a vertical reflection, rank-flipped, files unchanged").
2. `cv_hereon_aeon_up.tex` — `mechanistic interpretability` → `representation extraction`; PDF
   rebuilt and verified.

## 6. Queued, not yet done (leader-owned, deliberate)

Doctrine files are not to be bulk-edited; each of these is a decision:

| item | action |
|---|---|
| `LEADER_BIBLE:115` and `:146` test counts | replace both with a pointer to running the suite, rather than a number that will rot again |
| `LEADER_BIBLE:175` "pilot validated the method" | rewrite to record the measured 0/35 — **keep the original claim visible as a superseded line**, since the reversal is the lesson |
| `HOW_TO_RUN:20` requirements.txt | correct outright; it is a plain factual error in a runbook |
| `COMMAND_BASE:43` dead links | either create the two files or drop the references |
| `docs/SALIENCE_PROBLEM.md` §6 | add a header pointing to `PLAN_SALIENCE_CNP.md` for the current strategy; do **not** delete the original reasoning |
| `docs/CV_AI_MODULE.md:26` test counts | stale (339/290) |
| root sprint specs and reports | archive per Part 5.4 |

## 7. Consequence for the trainer

`2026-08-19_knowledge-trainer-build` stays **BLOCKED** until §6 is done. Three specific
constraints now follow from this audit:

1. **No card may be sourced from `docs/SALIENCE_PROBLEM.md` §6, `LEADER_BIBLE:175`, or
   `HOW_TO_RUN:20`** until corrected — all three would teach something false.
2. **The do-not-claim gate must load the real
   `job_search/.../study_room/06_do_not_claim.md`**, not any in-repo paraphrase. That distinction
   is exactly what hid the CV violation.
3. The `own-work` ladder must use the **corrected** frame description. A card teaching "index 0 is
   h8" would drill the error in rather than out.
