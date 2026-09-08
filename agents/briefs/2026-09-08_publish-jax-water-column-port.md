```
Brief-ID:      2026-09-08_publish-jax-water-column-port
Written:       2026-09-08
Target repo:   a NEW repository, prepared locally. Source archive lives in chess_speak_out_loud.
               Report is filed in chess_speak_out_loud/agents/reports/, as always.
Route:         Antigravity (full workspace). No web access needed except pip.
Type:          implementation -- packaging and publication preparation
Blast-radius:  EXTERNAL -- this becomes a public repository linked from a CV that is in front of a
               hiring committee. Everything in it is permanently attributable to Thejus.
Reversibility: costly -- a public repo can be deleted but not un-seen, and copyrighted material
               pushed to GitHub persists in forks and caches
Failure-mode:  SILENT -- a plausible README claim that the code does not support looks exactly like
               a true one until somebody runs it
Depends on:    none
Status:        ACTIVE
```

**Environment:** conda `cszero` or a fresh venv. CPU only. JAX installs from pip. No GPU, no engine.
Under 90 minutes.

---

## 1. INTENT

*(Intent outranks instructions. If any instruction below conflicts with this paragraph, the intent
wins — stop and report. Doing so is a success, never a boundary violation.)*

Thejus's CV makes this claim:

> *Ported the legacy Fortran/OpenMP particle engine to Google JAX … the port keeps binary output
> compatibility with the original Fortran, so its runs can be compared against it directly.*

It is the most job-relevant claim on his CV and it is **currently unverifiable by anyone who reads
it.** The public repository named on his CV
(`Agent_Based_Phytoplankton_Model-IBM-Phytoplankton`) contains the **Fortran/OpenMP** model and
advertises OpenMP. The JAX port existed only inside a Google Drive archive until 2026-09-08.

**Your job is to turn that claim into something a reviewer can check in thirty seconds**, by
preparing a clean, honest, publishable repository from the archive.

**You are not here to make the port look impressive.** You are here to make it *inspectable*. If the
code does not do something the README would like to say, the README does not say it. A modest repo
whose every sentence is true is worth far more to this application than an enthusiastic one, because
the person reading it may well be the author of a paper on exactly this problem.

---

## 2. The source archive

```
C:\Users\Admin\Documents\chess_speak_out_loud\downloads\python_port-20260908T155704Z-1-001.zip
```

Extract it to a **working directory of your choosing outside both repos**. 22 entries. Known
contents: `main.py`, `biology.py`, `state.py`, `config.py`, `config.yaml`, `io_utils.py`,
`calendar_utils.py`, `run_sediment_model.py`, `requirements.txt`, `README.md`,
`WCM_Colab_Notebook.ipynb`, `WCM_Colab_Optimized.ipynb`, `knowledge/beckmann.txt`,
`knowledge/medwed.txt`, `results/simulation_results.csv`, `fort.12`, `simulation_1month.png`,
`__pycache__/*`.

**⚠ This archive is Thejus's only copy.** Work on an extracted copy. Do not modify, move or delete
the zip.

---

## 3. WHAT YOU MAY TOUCH

```
<your working dir>/                          -- the prepared repository (new files, freely)
agents/reports/2026-09-08_publish-jax-water-column-port_REPORT.md   (new -- the deliverable)
```

Everything else is read-only. Explicitly forbidden:

- **Do not `git push`, do not create a GitHub repository, do not publish anything.** You prepare it;
  **Thejus publishes it.** This is his account and his name on it.
- **Do not touch `job_search/applications/hereon_agentic_ai_1059/`.** An application is being sent
  from that folder.
- **Do not touch `trainer/content/ladders/*.json`.** Every `.json` under it is off limits — no cards,
  no edits, no rewording. Three fabricated deliveries on this project came from a worker being asked
  for content, and the rule was broken again on 2026-09-03.
- **Do not commit anything in any existing repository.**

---

## 4. STEPS

### Step 1 — inventory, and find what must NOT be published

Before any packaging, classify **every file** in the archive into one of:

| class | meaning |
|---|---|
| `OWN-CODE` | written by Thejus (or his agents) — publishable |
| `OWN-OUTPUT` | results he generated — publishable if small and useful |
| `THIRD-PARTY` | **not his** — text, data or figures originating from someone else |
| `JUNK` | caches, editor swap files, stray binaries — exclude |

**⚠ Look hardest at `knowledge/beckmann.txt` and `knowledge/medwed.txt`.** The repository's
`paper/` directory elsewhere contains **published PDFs** (Beckmann et al. 2019, Medwed 2024). If
those `.txt` files are extracted text from copyrighted papers, **publishing them is a copyright
violation on a repository linked from a job application.** Open them, read enough of each to judge,
and say plainly what they are.

Also check `fort.12`, `results/simulation_results.csv` and `simulation_1month.png` for anything
institution-specific or not his to release.

**CHECKPOINT 1.** The classification table, one row per file, with a one-line justification for every
`THIRD-PARTY` call. **If anything is `THIRD-PARTY`, stop and report before going further.**

---

### Step 2 — make it run, and record what actually happens

In a clean environment:

```
pip install -r requirements.txt
python main.py --help
```

Then run the **shortest** simulation the config allows (edit a *copy* of `config.yaml` to reduce
`it_end`; do not commit a mutilated config).

Record, from real output:
- the exact commands;
- the `JAX devices:` line `main.py` prints (it calls `jax.devices()`);
- whether it completes, and the wall-clock time;
- any warning or error, verbatim, including deprecation warnings from modern JAX.

**The archive is roughly two years old. Expect API drift.** If it does not run on current JAX, that
is a finding, not a failure — record the exact error. **Do not silently modernise the code.** If a
minimal fix is obvious (a renamed import, a moved symbol), make it in a clearly-marked commit and
say exactly what you changed and why.

**CHECKPOINT 2.** Pasted terminal output for install and run. State plainly: **does it run today,
yes or no?**

---

### Step 3 — establish what the binary-compatibility claim actually means

The README asserts:

> *"**Binary I/O Compatibility**: Output files are byte-compatible with existing Fortran plotting
> scripts"*

Read `io_utils.py` and determine **what the code actually does** to achieve that: record layout,
endianness, record markers, dtype widths, the Fortran unformatted-record convention, whatever is
really there. Describe the mechanism in three or four sentences a reader could check against the
source.

**Do not claim the outputs have been compared against a Fortran run.** No such comparison exists in
the archive, and the Fortran binary is not part of this task. The honest statement is about the
*format contract*, not about a performed equivalence test. If you can see a way the claim could be
demonstrated cheaply later, say so in the report as a suggestion — do not build it here.

**CHECKPOINT 3.** The mechanism, with the `io_utils.py` line numbers that implement it.

---

### Step 4 — prepare the repository

In your working directory, assemble:

1. **The code**, `OWN-CODE` only, with `__pycache__` and swap files excluded.
2. **`.gitignore`** — Python caches, venvs, outputs, `*.swo`/`*.swp`.
3. **`requirements.txt`** — as-is unless Step 2 proved a version constraint is needed; if so, pin it
   and say why in the report.
4. **`README.md`**, rewritten. It must contain, and must contain nothing beyond what you verified:
   - one paragraph on what the model is (Lagrangian individual-based phytoplankton model with NPZD
     dynamics and trait evolution, ported from Fortran/OpenMP);
   - **that this is a port, and what it was ported from**, with a link to the Fortran repository
     `github.com/thejusmahajan/Agent_Based_Phytoplankton_Model-IBM-Phytoplankton`;
   - the branchless-`jnp.where` design and **why** it exists (GPU/TPU portability) — quoting
     `biology.py`'s own header comment;
   - the binary-compatibility contract **as established in Step 3**, worded as a format contract;
   - how to install and run, **with the commands you actually ran in Step 2**;
   - what hardware it has actually been run on. **Colab, T4 GPU** — the two notebooks carry
     `"accelerator": "GPU"` and `"gpuType": "T4"` in their metadata. **There is no evidence of a TPU
     run; do not imply one.**
   - a short "Status / limitations" section: age of the code, whether it runs today per Step 2, and
     the fact that no automated Fortran-equivalence test is included.

**Forbidden in the README:** any speedup figure, any benchmark, any "N× faster than Fortran", any
claim about TPUs, any claim of validation that Step 3 did not establish. **If you catch yourself
wanting a number, that is the signal to stop and leave it out.**

5. **Do not add a LICENSE.** Licence choice is Thejus's and has implications for a model derived
   from published work. **Raise it in the report as a decision for him.**

**CHECKPOINT 4.** `tree` of the prepared repository, and the full README text.

---

### Step 5 — leave it ready, do not publish

Initialise a git repository in the working directory, commit once locally with a plain message, and
**stop**. Do not add a remote. Do not push.

In the report, give Thejus the exact commands he would run to publish it himself, and a suggested
repository name and one-line description.

**CHECKPOINT 5.** `git log --stat` of the single local commit, and `git status` showing a clean tree.

---

## 5. REPORT

`agents/reports/2026-09-08_publish-jax-water-column-port_REPORT.md`, containing every checkpoint's
real pasted output, the file classification table, the README in full, and:

- **"What I could not check"** — mandatory, non-empty.
- The licence question, stated as a decision for Thejus.
- Then the standing question, answered:

> **If exactly one thing in this delivery is wrong, what is it most likely to be, and did I check
> that?**

---

## 6. ACCEPTANCE

1. Nothing published, no remote added, nothing pushed.
2. Every file classified, and every `THIRD-PARTY` item excluded and named.
3. The README contains no number that did not come from a command you ran.
4. The run in Step 2 was actually attempted, and its real result — success or failure — is reported.
5. Nothing outside the working directory and the report file was created or modified.

---

## 7. STOP AND ASK

Not covered by this brief: publishing; choosing a licence; modernising the code beyond a minimal
named fix; editing the application folder; touching flashcards; adding benchmarks; deleting or
altering the source zip.

**A stop with a clear question is a successful delivery.**
**And if the `knowledge/*.txt` files turn out to be copyrighted paper text, stopping to say so is
the single most valuable thing this task can produce.**
