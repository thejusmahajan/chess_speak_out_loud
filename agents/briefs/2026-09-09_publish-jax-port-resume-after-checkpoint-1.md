```
Brief-ID:      2026-09-09_publish-jax-port-resume-after-checkpoint-1
Written:       2026-09-09
Target repo:   a NEW repository prepared locally. Report filed in chess_speak_out_loud.
Route:         Antigravity (full workspace). pip needs network.
Type:          implementation -- packaging only. NOTHING IS PUBLISHED.
Blast-radius:  external -- this becomes a public repo linked from a CV in front of hiring committees
Reversibility: costly -- a public repo can be deleted but not un-seen
Failure-mode:  SILENT -- a README claim the code does not support looks exactly like a true one
Depends on:    2026-09-08_publish-jax-water-column-port (CHECKPOINT 1 stop, AUDITED ACCEPT)
Status:        ACTIVE
```

**Environment:** conda `cszero` or a fresh venv; network for pip. CPU only. **Time-box: 90 minutes.**

---

## 0. Where this picks up

The previous brief stopped at Checkpoint 1, correctly, because the archive contained third-party
material. **The leader has audited that stop and accepted it.** The classification of all 22 entries
was verified independently and stands. Resume at Step 2 of the original brief, with the decisions
below already made — do not re-litigate them.

### Decisions taken by the leader and Thejus (do not revisit)

| item | decision |
|---|---|
| `knowledge/beckmann.txt` | **EXCLUDE, permanently.** Elsevier, *J. Theor. Biol.* 468, 60–71 (2019). The file itself carries "© 2019 Elsevier Ltd. All rights reserved." Publishing it would be infringement |
| `knowledge/medwed.txt` | **EXCLUDE, permanently.** *ISME Communications* 4(1), ycae140 (2024). ⚠ **Correction to the previous report:** this paper is **CC BY 4.0 open access**, so redistribution with attribution would in fact be *legal*. It is still excluded — a code repository should not ship full paper texts, and this copy retains an institutional download banner naming a user. Exclude on hygiene, not on law. Do not repeat the claim that it is a copyright violation |
| `__pycache__/*` (5 files) | EXCLUDE |
| `results/simulation_results.csv` (1.37 MB) | **EXCLUDE.** A 21,901-row output file makes the clone heavy and demonstrates nothing a reader needs |
| `fort.12` (32 KB) | **KEEP.** Small, and it is the artefact that demonstrates the Fortran binary record contract |
| `simulation_1month.png` | **KEEP.** The one demo figure |
| Everything classified `OWN-CODE` | KEEP |

Both papers stay cited in the README as references. Citing them is right; shipping their text is not.

---

## 1. INTENT

*(Intent outranks instructions. If any instruction conflicts with this paragraph, the intent wins —
stop and report.)*

Thejus's CV says he ported a legacy Fortran/OpenMP engine to JAX and kept **binary output
compatibility with the original Fortran** so the port could be checked rather than asserted. That
claim is currently unverifiable by anyone reading it: the public repository his CV links contains
the **Fortran** model and advertises OpenMP.

**Your job is to make that claim inspectable in thirty seconds** — a clean, honest, publishable
repository. **Not impressive. Inspectable.** If the code does not support a sentence, the sentence
does not go in the README. The people most likely to read this are the ones best placed to catch it.

---

## 2. WHAT YOU MAY TOUCH

```
<a working directory OUTSIDE both repos>   -- the prepared repository, freely
agents/reports/2026-09-09_publish-jax-port-resume-after-checkpoint-1_REPORT.md   (new -- deliverable)
```

- **Do not publish. No `git remote add`, no `git push`, no repository created on GitHub.** You
  prepare it; **Thejus publishes it.** His name, his account.
- **Do not touch `job_search/`**, the website repo, or `trainer/content/ladders/*.json`.
- **Do not commit in any existing repository.**
- **Do not modify the source zip.**

---

## 3. STEPS

### Step 1 — assemble, with the exclusions above

Copy only the KEEP files into the working directory. Add a `.gitignore` that covers at minimum:

```
__pycache__/
*.pyc
knowledge/
results/
.venv/
venv/
*.swp
*.swo
```

**`knowledge/` must be in `.gitignore` even though you are not copying those files.** It is the
guard against someone later dropping the archive in wholesale.

**CHECKPOINT 1.** `tree` of the prepared directory and the full `.gitignore`.

---

### Step 2 — make it run, and report honestly what happens

```
pip install -r requirements.txt
python main.py --help
```

Then run the shortest simulation the config allows — edit a **copy** of `config.yaml` to reduce
`it_end`; do not commit a mutilated config.

Record from real output: the exact commands; the `JAX devices:` line `main.py` prints; whether it
completes; wall-clock time; and any error or deprecation warning **verbatim**.

**The archive is roughly two years old. Expect JAX API drift.** If it does not run, that is a
finding, not a failure — paste the exact error. **Do not silently modernise the code.** If a minimal
fix is obvious (a renamed import, a moved symbol), make it as a separate, clearly-labelled commit
and say exactly what you changed and why.

**CHECKPOINT 2.** Pasted install and run output. **Does it run today — yes or no?**

---

### Step 3 — the binary compatibility contract

You drafted this in the previous report. **Re-state it here in final form**, grounded in
`io_utils.py` with line numbers: the record layout, endianness, record markers, dtype widths — what
the code actually does to remain readable by the Fortran plotting scripts.

**Do not claim the outputs were compared against a Fortran run.** No such comparison exists in the
archive. The honest claim is about the **format contract**, not a performed equivalence test.

**CHECKPOINT 3.** The mechanism, with `io_utils.py:line` references.

---

### Step 4 — the README

Rewrite it. It must contain, and nothing beyond what you verified:

- what the model is (Lagrangian individual-based phytoplankton model, NPZD dynamics, trait evolution);
- **that this is a port, and of what** — link the Fortran original at
  `github.com/thejusmahajan/Agent_Based_Phytoplankton_Model-IBM-Phytoplankton`;
- the branchless `jnp.where` design and why it exists, quoting `biology.py`'s own header;
- the binary-compatibility contract from Step 3, worded as a format contract;
- install and run instructions **using the commands you actually ran in Step 2**;
- hardware it has actually run on: **Google Colab, T4 GPU** — both notebooks carry
  `"accelerator": "GPU"` and `"gpuType": "T4"`. **No TPU run exists. Do not imply one.** The port is
  *portable* to TPU by design; it has not been executed on one;
- **references**: Beckmann, Schaum & Hense (2019) *J. Theor. Biol.* **468**, 60–71, and Medwed
  et al. (2024) *ISME Communications* **4**(1), ycae140 — cited, not reproduced;
- a short **Status / limitations** section: age of the code, whether it runs today per Step 2, and
  that no automated Fortran-equivalence test is included.

**Forbidden:** any speedup figure, any benchmark, any "N× faster than Fortran", any TPU claim, any
validation Step 3 did not establish. **If you find yourself wanting a number, that is the signal to
leave it out.**

**Do not add a LICENSE.** Licence choice is Thejus's and has implications for a model derived from
published work. Raise it in the report as a decision.

**CHECKPOINT 4.** `tree` and the full README text.

---

### Step 5 — leave it ready

`git init`, one local commit, plain message. **No remote. No push.** In the report, give Thejus the
exact commands to publish it himself, plus a suggested repository name and one-line description.

**CHECKPOINT 5.** `git log --stat` and a clean `git status`.

---

## 4. REPORT

`agents/reports/2026-09-09_publish-jax-port-resume-after-checkpoint-1_REPORT.md` — every checkpoint's
real output, the README in full, **"What I could not check"** (mandatory, non-empty), the licence
question, and:

> **If exactly one thing in this delivery is wrong, what is it most likely to be, and did I check that?**

---

## 5. ACCEPTANCE

1. Nothing published; no remote; nothing pushed; nothing committed in an existing repo.
2. `knowledge/`, `__pycache__/` and `results/` absent from the prepared repo **and** in `.gitignore`.
3. No number in the README that did not come from a command you ran.
4. Step 2 actually attempted, and its real result — success or failure — reported.
5. The README states T4 GPU and makes no TPU-execution claim.

---

## 6. STOP AND ASK

Not covered: publishing; choosing a licence; modernising beyond a minimal named fix; re-opening the
exclusion decisions in §0; touching the other repos.

**A stop with a clear question is a successful delivery.**
