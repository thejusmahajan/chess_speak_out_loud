# Application to this project

What actually changes. Written 2026-09-02, after the corpus, and deliberately short on inspiration.

---

## 0. First, the honest accounting of what this corpus can and cannot fix

On 2026-09-02 an independent review found **eight defects** in my work. Sorted by what would
actually have prevented them:

| defect | prevented by |
|---|---|
| `--no-amp` added, not threaded to `predict()` | `grep` |
| `sys.path` repair in `run_kaggle.py`, not `evaluate.py` | `grep` |
| `--no-amp` never exposed on `run_kaggle.py` | `grep` |
| how-to fixed, notebook written with a different mechanism | running the command |
| `subprocess.call` output invisible in a notebook | running the command |
| `roc_auc` Python loop, 1.22 s/call | timing it |
| `bfloat16` on a T4 | checking the hardware |
| **B1 gate applied at the wrong altitude** | **judgement — Kranz** |
| **stale checkpoint mistaken for a result** | **judgement — Vaughan, Knight** |

**Seven of nine are mechanical.** They are fixed by `grep`, by executing the command, and by timing
the function. Reading about Shackleton does not touch them, and any claim otherwise would be the
"infrastructure that postpones exposure" this project has on its own charge sheet.

Two are genuinely leadership failures of the kind this corpus addresses, and both were found by
someone else. That is the honest yield, and it is not nothing — the B1 gate trap would have wasted a
Kaggle session and the stale-checkpoint mask would have reported a dead model's numbers as a result.

So this document has two halves, kept apart on purpose.

---

## Part A — the mechanical interlocks (these do the most work)

To be added to `docs/leadership/LEADER_GROUNDING.md`, because a rule that lives only in a corpus is a
rule I will break while quoting it.

**A1. Change one thing → grep the identifier.** Every new flag, parameter, function or config key
gets `grep -n "<name>"` across the tree before the work is called done, and every call site is
inspected. *Knight Capital, seven servers of eight.* Catches three of today's eight.

**A2. Fix a file → name its sibling.** `train.py`/`evaluate.py`, README/how-to, notebook/how-to,
source/`dist` copy. Same-class files are checked as a set, never singly.

**A3. Every invocation in a document is executed exactly as written**, before the document is
committed. Not a similar command. That one. *This was learned at 18:00 on 2026-09-02 and violated by
21:50 in the notebook.*

**A4. Any function on a per-epoch or per-request path gets timed once**, not reasoned about.
*Feynman's ice water; the 1.22 s `roc_auc`.*

**A5. Edit the source, never the build artefact.** `dist/` is output. *Gemini edited
`dist/kaggle_phi_net.ipynb`; the next rebuild would have discarded it silently.*

**A6. When reusing anything — a cache, a label, a benchmark, a component — write down which
environment made it valid, and store that record with the artefact.** *Ariane 5; the EPD cache keyed
by position and not by budget; the manifest now carried inside every checkpoint.*

---

## Part B — the judgement changes

**B1. A gate belongs to the decision it governs.** F1 (AUC > 0.70) is B2's gate on the test split. I
applied it to the B1 diagnostic rung, which would have aborted the session on a *good* B1. Before
writing any threshold, state which decision it governs and at what altitude. *Kranz: mission rules
are written per phase.*

**B2. Delete this run's outputs before the run starts.** A crash must leave no artefact that a later
step can mistake for a result. Already implemented as `clear_stale_outputs()`. *Commit `33ff814`;
Columbia; Vaughan.*

**B3. When the burden of proof flips, stop.** If an argument's shape has become "you cannot prove
this optimisation is harmful", the answer is no until a measurement says otherwise. *Challenger; the
sacrifice-pruning proposal, where both halves of the filter selected against the thing the project
exists to find.*

**B4. Brief Gemini toward its strength, and never for a verdict.** Three audits' evidence: it is
better than me at exhaustive local inspection, and worse at determinism under ambiguity and at
judging severity. Ask it to *enumerate every caller of X*, not *what do you think of X*. Its
opinions produced an unsourced T4 throughput figure, a "parameter corruption" claim that measured
0.0, and a pruning rule that would have destroyed the aim. *Manhattan: Groves and Oppenheimer did
not do each other's jobs.*

**B5. Move checks from review into code.** The target is fewer defects *found*, more defects made
*impossible*. Precedents set this week: `resolve_data_dir` raises on ambiguity; `evaluate.py`
refuses across dataset builds; `b1_verdict` is a tested function rather than reviewed prose.
*Deming: cease dependence on inspection.*

**B6. A round table is convened when Thejus asks, and is aimed at our engineering, never at his
aim.** Already recorded in `discussions/README.md`. *Sloan manufactures disagreement about his own
proposal, not a subordinate's.*

**B7. Write the interpretation of success in advance, not only of failure.** We pre-registered
F0/F1/F2 and never wrote down what a *pass* would mean. Φ passing F1 means configurations are
learnable from 18 planes. It does **not** mean the steering works, and that is exactly where a
project talks itself into an overclaim. *Eisenhower wrote the failure note; nobody writes the success
note, which is why success is where overclaiming lives.*

---

## Part C — three things this corpus says we should be doing and are not

**C1. There is no path by which a second Gemini challenge reaches Thejus over my head.** If it
flags something twice and I overrule it twice, the record of the override is mine. CRM's
two-challenge rule exists because the senior person is sometimes wrong and confident. *Proposal:
any finding I downgrade twice gets stated explicitly in the reply to Thejus, with my measurement, so
he can adjudicate.*

**C2. Nobody has asked whether the profile regeneration should happen at all.** Grove's question,
asked properly: a stranger arriving today, told the interview is live, the permit expires in about
eighteen months and the money is borrowed, would look at 9,000 games of which 8,617 are two-minute
bullet — a corpus of *reflex* errors — and ask what a knowledge-diagnosis profile built from it is
worth. The Wright answer follows: decompose. Does a 200-game profile answer the coaching question?
Does the bullet corpus contain knowledge errors at all? Both are cheap and neither has been asked.

**C3. The dataset exists in exactly one place.** `data/` is gitignored, so `config_steering` lives
on one laptop with no backup. Uploading it to Kaggle is the fix and is worth doing for that reason
alone. *Amundsen's flag lines: build for the error you will certainly make.*

---

## The one-line version

The corpus is worth what Part A and Part C are worth. Part A is `grep`, running the command, and
timing the function — and it would have prevented seven of my last eight defects. Part C is three
questions nobody has asked, one of which is whether a fifty-one-day compute job should exist at all.

Everything else here is context, and context is only worth having if it changes what gets typed
tomorrow.
