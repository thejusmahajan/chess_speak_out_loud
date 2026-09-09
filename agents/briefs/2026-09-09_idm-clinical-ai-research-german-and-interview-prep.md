```
Brief-ID:      2026-09-09_idm-clinical-ai-research-german-and-interview-prep
Written:       2026-09-09
Target repo:   job_search/applications/idm_clinical_ai/  (ONE new file) + report in chess_speak_out_loud
Route:         Antigravity (full workspace) + WEB ACCESS REQUIRED
Type:          research + drafting
Blast-radius:  external -- feeds a live job application in a 7-month visa window
Reversibility: costly -- a wrong fact about the employer, or an overclaim in German, is said once
Failure-mode:  SILENT -- an invented detail about a company reads exactly like a researched one
Depends on:    none
Status:        ACTIVE
```

**Environment:** web access. No GPU, no engine. **Time-box: 2 hours.**

---

## 1. INTENT

*(Intent outranks instructions. If any instruction conflicts with this paragraph, the intent wins —
stop and report.)*

Thejus is applying to **IDM gGmbH, Hamburg** for **AI/ML Engineer, Clinical AI**
(`https://www.idmedizin.de/de/karriere/ai-ml-engineer-clinical-ai`). A CV and cover letter are
already built in `job_search/applications/idm_clinical_ai/`.

He needs four things, and **the honesty of them matters more than the volume**:

1. **Who IDM actually are** — verified, cited. Not impressions.
2. **Whether the application should be in German**, decided from evidence, not assumption.
3. **A German draft, if the answer is yes** — one that does not make him sound more German than he is.
4. **Interview preparation** — the questions he will actually face, and which of *his real experiences*
   answer them.

**⚠ Read this paragraph twice.** Three worker-written "strategy" documents for a previous
application were audited on 2026-09-07. Their science was accurate and their **paperwork was
invented**: a mandatory reference number that appears nowhere in the posting, a portal file-size
limit contradicted by the employer's own guide, and a "lexical optimisation" table instructing him
to relabel his CV in the hiring group's vocabulary for systems he had never built. That audit is at
`agents/reports/2026-09-07_hereon-1059-strategy-documents_AUDIT.md`. **Do not repeat it.**
**Every factual claim about IDM carries a URL, or it does not go in the report.**

---

## 2. WHAT YOU MAY TOUCH

```
job_search/applications/idm_clinical_ai/GERMAN_DRAFT.md          (new -- German text, ONLY if Step 2 says yes)
agents/reports/2026-09-09_idm-clinical-ai-research-german-and-interview-prep_REPORT.md   (new)
```

**That is the complete list.**

- **Do not edit `cover_letter_idm.tex`, `cv_idm_clinical_ai.tex`, or any `.pdf`.** If you find an
  error in them, **report it**; the leader makes the change. This rule exists because a previous
  delivery wrote three files into an application folder while an application was being sent from it.
- **Do not add a single skill, tool or framework to his CV or letter.** Not MLflow, not Docker, not
  Kubernetes, not HuggingFace, not spaCy, not NLP. He does not have them. Suggesting he claim them
  is the exact failure mode named in §1.
- **Do not invent a contact person, reference number, deadline or salary band** beyond what the
  posting states (`75.000–100.000 €`, "ab sofort", reports to CTO / AI Research Lead).
- Do not touch `trainer/content/ladders/*.json`, other applications, or the website repo.
- **Do not commit anything.**

---

## 3. STEPS

### Step 1 — Who is IDM gGmbH? (facts, each with a URL)

Establish, from primary sources — their own website, Impressum, Handelsregister, LinkedIn, press,
university-hospital announcements:

- Legal form and what `gGmbH` implies here (non-profit); founding date; ownership/backers.
- **What they actually do** — product, service, or research? Who pays them?
- Size: headcount, and how many are engineers.
- The "Universitätskliniken in unserem Netzwerk" the posting mentions — **which** clinics, named.
- Any published work, funding, or clinical studies.
- Anything about engineering culture, stack or hiring process they have said publicly.

**Every row needs a URL.** Where you cannot verify something, write **UNVERIFIED** and say what you
looked at. A short sourced profile beats a long plausible one.

**CHECKPOINT 1.** The profile, with a URL per claim, and an explicit UNVERIFIED list.

---

### Step 2 — German or English? Decide from evidence

Do **not** assume. Gather evidence and give a verdict:

- What language is the careers page, the application portal, and the rest of their site?
- Does the posting state a language requirement? *(It says
  `"Deutschkenntnisse (nicht erforderlich, aber hilfreich für die klinische Zusammenarbeit)"` — quote
  it and weigh it.)*
- What language are their job ads, LinkedIn posts and team communications in?
- Is the tech stack section in English? What does that suggest about working language?

**Verdict, one of:** *German expected* · *English fully acceptable* · *Either, with German a mild
advantage*. State which, and the evidence.

**CHECKPOINT 2.** The verdict and its evidence.

---

### Step 3 — What they really expect, versus what they wrote

Separate the posting's requirements into:

- **Hard filters** — likely to screen him out automatically.
- **Strong preferences** — matter, but negotiable for the right profile.
- **Wish-list** — stated, rarely decisive.

Ground this in comparable German clinical-AI / ML-engineer postings you can cite, not in intuition.
Say plainly which category **"3+ Jahre Hands-on-Erfahrung in ML/AI mit klarem Fokus auf NLP"** falls
into, and what the realistic effect is on a candidate with roughly two months of self-directed ML
and no NLP.

**CHECKPOINT 3.** The three-tier table.

---

### Step 4 — The gap, honestly, and what actually bridges it

Read his materials first:
`applications/idm_clinical_ai/cover_letter_idm.tex`, `cv_idm_clinical_ai.tex`, and
`applications/clinical_data_science_general/` for the fuller clinical detail.

For each requirement, state: **HAVE / PARTIAL / DO NOT HAVE**, with the evidence from his record.

Then, for each gap, answer: **what would genuinely close it, and how long would it take?** Distinguish
between what he can do before an interview (days) and what takes months. **A gap that cannot be
closed before an interview should be labelled as such** — the strategy is then to answer it honestly,
not to pretend.

**Forbidden:** any recommendation that he claim, imply or "reframe" something he has not done.

**CHECKPOINT 4.** The requirement-by-requirement table with the bridge assessment.

---

### Step 5 — The German draft (ONLY if Step 2 says German is expected or advantageous)

Write `GERMAN_DRAFT.md` in the application folder — **plain German prose, not LaTeX.** The leader
will typeset it.

**⚠ The trap in this step, and it is not obvious.** A flawless, idiomatic German cover letter sets an
expectation that the interview will immediately test. **Thejus holds Goethe-Zertifikat B1 with B2 in
preparation.** His own words: *he can communicate well in German, but not at native level.*

So the German must be **correct, clear and professional — and plainly the German of a competent
non-native speaker.** No literary flourishes, no subjunctive gymnastics, no idioms he would not
produce himself. Short sentences he could defend out loud.

**Include one honest sentence about his level**, in German, in the letter — something to the effect
that he communicates comfortably in German and is working toward B2, and that his technical working
language is English. Draft it; the leader will check the wording.

**Hard requirement: the gap paragraph must survive translation with its meaning intact.** The English
letter says he does not have three years of NLP, has not run MLflow/Kubernetes/CI-CD for models, and
that coursework is not production experience. **That paragraph is deliberate. Do not soften it, do
not shorten it, do not let it become vaguer in German.**

**CHECKPOINT 5.** The German draft, plus a short note on any phrase you found hard to render and why.

---

### Step 6 — Interview preparation

Produce the questions he should expect, in two groups:

**(a) Technical.** From their actual stack and responsibilities: transformers and NLP architecture,
PyTorch, HuggingFace, evaluation and monitoring, MLOps, latency and scalability in a real-time
clinical setting, working with clinical documentation data.

For each: **what a strong answer looks like, and which of Thejus's real experiences supply it.** If
he has nothing to draw on for a question, say so and mark it **NO MATERIAL** — that is more useful
than an invented bridge.

**(b) Non-technical.** Expect at minimum: why the career change; why clinical AI; the ML-years gap;
how he handles a model that is confidently wrong; German language ability; salary expectation
(the band is `75.000–100.000 €`); availability; visa and work authorisation.

**Anchor answers in his record**, which includes: the DeGIR refactor with byte-identical
verification, 257 correction rules externalised, two pre-existing bugs found and reported rather
than silently fixed; two silent correctness errors found in his own pipeline and publicly corrected;
transformer attention capture via PyTorch forward hooks; a Fortran→JAX port with a preserved binary
format contract; teaching two lecture blocks and an R practical; ten years of computational
modelling.

**CHECKPOINT 6.** Both question sets with sourced-to-his-record answer material.

---

### Step 7 — Audit the built application

Read the letter and CV PDFs and report **errors only**: factual mistakes, overclaims, typos,
anything inconsistent between the two, anything that contradicts his record.

**Do not rewrite them.** List findings with the exact text and what is wrong.

**CHECKPOINT 7.** The findings list, or an explicit "no errors found".

---

## 4. REPORT

`agents/reports/2026-09-09_idm-clinical-ai-research-german-and-interview-prep_REPORT.md` — every
checkpoint, plus:

- **"What I could not check"** — mandatory, non-empty.
- Then: **If exactly one thing in this delivery is wrong, what is it most likely to be, and did I
  check that?**

---

## 5. ACCEPTANCE

1. **Every factual claim about IDM carries a URL.** Unsourced impressions go in "what I could not
   check", not in the profile.
2. **Nothing added to his CV or letter that he cannot defend.** No skills, no tools, no reframing.
3. Step 2's verdict is evidence-based and stated plainly.
4. If a German draft was produced: the gap paragraph is intact in meaning, and the German is
   competent-non-native, not literary.
5. Only the two permitted files created. No `.tex` or `.pdf` edited. Nothing committed.
6. Step 6 marks **NO MATERIAL** wherever he genuinely has nothing — the count of those is a finding,
   not a failure.

---

## 6. STOP AND ASK

Not covered: editing the application documents; adding skills; inventing employer details; applying
on his behalf; committing.

**A stop with a clear question is a successful delivery.**
**And if the honest conclusion is "he does not meet the hard filter and this is a long shot", say
so. He already knows. He is applying anyway, with his eyes open, and a report that pretends
otherwise is worth nothing to him.**
