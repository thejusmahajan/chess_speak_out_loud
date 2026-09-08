```
Brief-ID:      2026-09-07_publication-list-independent-verification
Written:       2026-09-07
Target repo:   job_search  (workspace: C:\Users\Admin\Documents\bioinformatics_project\job_search)
               Report is filed in chess_speak_out_loud, as always.
Route:         Antigravity (full workspace) + WEB ACCESS REQUIRED
Type:          audit -- independent verification, no implementation
Blast-radius:  external -- this list goes on a CV that is being sent to a hiring committee
Reversibility: costly -- a wrong publication on a CV cannot be recalled after sending
Failure-mode:  SILENT -- a plausible-looking citation is indistinguishable from a correct one
                until someone checks it, and the person who checks it is the hiring panel
Depends on:    none
Status:        AUDITED ACCEPT 2026-09-07
```

**Environment:** any Python; terminal; web access. No engine, no GPU, no repo build required.
Under 45 minutes.

---

## 1. INTENT

*(Intent outranks instructions. If any instruction below conflicts with this paragraph, the intent
wins — stop and report. Doing so is a success, never a boundary violation.)*

Thejus is sending a job application to Helmholtz-Zentrum Hereon **today**. His CV now carries, for
the first time, a **full publication list**. The leader assembled that list and believes it is
correct. **This brief exists because the leader's belief is not evidence.**

Your job is to **independently reconstruct the publication list from primary sources, and then say
where you disagree with the leader.** You are not checking his work by reading it — you are doing
the work again, separately, and comparing at the end.

**A disagreement is the most valuable thing you can produce.** If you find the leader listed a
paper he is not an author of, or missed one he is, that finding is the entire value of this task.
Say it plainly.

There is already one confirmed error in the existing material: his public website lists a paper
that is **not his** and one whose DOI **does not resolve**. So the base rate of citation error in
this material is not zero. Assume nothing.

---

## 2. ⚑ THE ONE RULE THAT MAKES THIS AUDIT WORTH ANYTHING

**Do not read Appendix A until you reach Step 5.**

Appendix A contains the leader's answer. If you read it first, you will anchor on it, and this
audit becomes a proofread instead of an independent derivation — which is worth almost nothing,
because the leader already proofread it himself.

Build your list from the sources in Steps 2–4. Only then open Appendix A and diff.

If you have already read Appendix A by accident, **say so in the report**. That is not a failure;
concealing it would be.

---

## 3. WHAT YOU MAY TOUCH

```
agents/reports/2026-09-07_publication-list-independent-verification_REPORT.md   (new -- the deliverable)
```

**That is the complete list. This is a read-only audit of everything else.**

Explicitly forbidden, and none of this is covered by the brief:

- **Do not edit any `.tex`, `.pdf`, `.cls` or any file in
  `applications/hereon_agentic_ai_1059/`.** If you believe something there is wrong, **report it**;
  the leader makes the change. The application is being sent today and an unexpected edit to a
  built document is the one thing that could actually break it.
- **Do not touch `trainer/content/ladders/*.json`.** Every `.json` under that directory is off
  limits — no new cards, no edits, no rewording. Card content is the leader's. Three fabricated
  deliveries on this project came from a worker being asked for content, and this rule was broken
  again on 2026-09-03. It is not ambiguous.
- **Do not edit the website** (`C:\Users\Admin\Documents\thejusmahajan.github.io`). You will find
  errors in it. Report them; do not fix them.
- **Do not commit anything, in any repository.**

---

## 4. STEPS

### Step 1 — read the primary sources, and only the primary sources

These are Thejus's own bibliography files. They are outside both repos:

```
C:\Users\Admin\Documents\application\cv\ref.bib
C:\Users\Admin\Documents\application\cv\cv_thejus.bib
C:\Users\Admin\Documents\application\cv\publication.bib
C:\Users\Admin\Documents\application\cv\mahajan2017.bib
C:\Users\Admin\Documents\application\cv\mahajan2019.bib
C:\Users\Admin\Documents\application\cv\mahajan2020.bib
C:\Users\Admin\Documents\application\cv\tij2018.bib
```

Also read, as *claims to be tested* rather than as sources of truth:

```
C:\Users\Admin\Documents\thejusmahajan.github.io\projects.html      (a 5-item list)
C:\Users\Admin\Documents\thejusmahajan.github.io\experience.html    (a sentence claiming a count)
```

Build one table of **every distinct work** mentioned anywhere in those files: title, full author
list, journal, volume, issue, pages/article number, year, DOI if present, and which file it came
from. Deduplicate by DOI where you have one, and by title otherwise.

**CHECKPOINT 1.** Paste that table. State how many distinct works you found and how many of them
name Thejus Mahajan in the author list. Note any work that appears in more than one file with
**different** metadata — that is a signal, not noise.

---

### Step 2 — resolve every DOI, and check the author list against the publisher

For each candidate with a DOI, query Crossref directly:

```
https://api.crossref.org/works/<DOI>
```

For each candidate **without** a DOI, find it via a Crossref bibliographic query, e.g.

```
https://api.crossref.org/works?query.bibliographic=<title words>&rows=5
```

For every work, record from the **publisher/Crossref record, not from the .bib file**:
title, complete author list in order, journal, volume, issue, page/article number, year.

Then answer, per work, one question: **is "Mahajan" in the author list returned by Crossref?**
Give the position (e.g. "author 8 of 9"). If Crossref returns a truncated or empty author list,
say so and check the publisher's own landing page instead.

**A work stays on the list only if a source outside Thejus's own files confirms he is an author.**

**CHECKPOINT 2.** A table: candidate, DOI, resolves yes/no, Mahajan present yes/no, position,
and the source you used. Paste the raw command or URL for at least three of them.

---

### Step 3 — hunt for publications that are MISSING

The leader's list was built from files Thejus happens to have kept. That method cannot find a paper
he forgot. Search independently:

- Crossref by author: `https://api.crossref.org/works?query.author=Mahajan&query.bibliographic=Beroff+Chabot+CnN&rows=20`
- The same for co-author surnames that recur: **Béroff, Chabot, IdBarkach, Diaz-Tendero, Le Padellec, Launoy, Aguirre**.
- Google Scholar profile `PJkZwAwAAAAJ` — treat it as a *lead generator only*; its author lists are
  truncated with "and others" and it lists his PhD thesis as though it were a paper.
- His PhD thesis (Université Paris-Saclay, 2018) may list his own publications; if you can reach it,
  its list is a strong independent check.

**CHECKPOINT 3.** Any work naming Mahajan that is **not** in your Step 2 table. For each: full
record, and your judgement on whether it is (a) a genuine missing publication, (b) a different
person named Mahajan, or (c) the PhD thesis / a non-peer-reviewed item. **Be careful with (b)** —
"Mahajan" is a common surname; require a co-author overlap or subject match before claiming it.

---

### Step 4 — classify what you have

For each confirmed work, label it:

| label | meaning |
|---|---|
| `JOURNAL` | peer-reviewed journal article |
| `PROCEEDINGS` | conference proceedings (e.g. *J. Phys.: Conf. Ser.*) |
| `THESIS` | doctoral thesis |
| `OTHER` | anything else — say what |

This matters: *Journal of Physics: Conference Series* is proceedings, not a peer-reviewed journal
article, and a CV that calls everything "peer-reviewed publications" is overclaiming. **State how
many are `JOURNAL` and how many are `PROCEEDINGS`.** Do not decide how the CV should word it —
that is the leader's call. Just give the counts.

**CHECKPOINT 4.** The labelled list, with counts per label.

---

### Step 5 — NOW open Appendix A, and diff

Read Appendix A. Produce a three-column reconciliation:

| in the leader's list | in your list | verdict |
|---|---|---|

Verdicts to use: `AGREE`, `LEADER HAS IT WRONG` (metadata differs — say which field),
`LEADER LISTED A PAPER HE SHOULD NOT` (Mahajan not an author), `LEADER MISSED ONE`.

For every row that is not `AGREE`, give the evidence — the Crossref record, the URL, the field.

**CHECKPOINT 5.** The reconciliation table. If it is entirely `AGREE`, say so plainly; that is a
valid and useful result. Do not manufacture a disagreement to look thorough.

---

### Step 6 — verify the built PDF matches the source

The application PDFs are already built. Confirm the shipped artefact says what the source says:

```
cd C:\Users\Admin\Documents\bioinformatics_project\job_search\applications\hereon_agentic_ai_1059
pdftotext -f 3 -l 3 cv_hereon_1059.pdf -
pdfinfo cv_hereon_1059.pdf
pdfinfo Mahajan_CoverLetter_CV_1059.pdf
pdfinfo Mahajan_Additional_Documents_1059.pdf
```

Check and report:

1. Page 3 of `cv_hereon_1059.pdf` lists exactly the works in the `.tex`, with the same volumes,
   issues, article numbers and years. **Compare the rendered text, not the source.**
2. Page counts: letter 1, CV 3, combined 4, certificates 19.
3. Combined size of the two `Mahajan_*.pdf` files **must be under 5 MB** (Hereon's portal limit).
   Report the number in MB.
4. Every DOI printed on page 3 resolves. Re-check them **from the PDF text**, not from the `.tex` —
   a typo introduced in typesetting is exactly the kind of error this step exists to catch.

**CHECKPOINT 6.** Paste all four command outputs and the DOI re-check.

---

## 5. REPORT

`agents/reports/2026-09-07_publication-list-independent-verification_REPORT.md`, containing:

- Every checkpoint's real pasted output — commands and their actual stdout, not summaries.
- The Step 5 reconciliation table.
- A one-line **verdict**: is the publication list on this CV safe to send, yes or no?
- **"What I could not check"** — mandatory, and **must be non-empty**. An audit that claims to have
  checked everything is either untrue or trivial.
- Then this standing question, answered:

> **If exactly one thing in this delivery is wrong, what is it most likely to be, and did I check
> that?**

---

## 6. ACCEPTANCE

1. The publication list was derived **before** Appendix A was opened (or the breach is declared).
2. Every work on the final list has non-Thejus-sourced confirmation that he is an author.
3. Every DOI checked by actually resolving it, with the output pasted.
4. Step 3 genuinely attempted — a missing-paper search that returns nothing is a result, but it
   must have been run, and the queries must be shown.
5. Nothing outside `agents/reports/` was created, edited or committed.

---

## 7. STOP AND ASK

Not covered by this brief, and therefore a stop: editing any application document; changing the
CV's wording or the count it claims; editing the website; touching flashcards; committing;
deciding how proceedings should be described on the CV.

**A stop with a clear question is a successful delivery.**
**And if you disagree with the leader, you are probably the reason this brief exists — say it.**

---

---

## APPENDIX A — DO NOT READ UNTIL STEP 5

<!-- The leader's answer. Opening this early converts an independent audit into a proofread. -->

The leader's list is **six works**, ordered reverse-chronologically as they appear on CV page 3:

| # | Authors (leader's rendering) | Title (short) | Venue | Year | DOI |
|---|---|---|---|---|---|
| 1 | **Mahajan, T.**, Béroff, Pons, Illescas, Chabot, Idbarkach, Jorge, Aguirre, Díaz-Tendero | Energy deposit by electron excitation in C$_n$N$^+$ projectiles | J. Phys.: Conf. Ser. **1412**(14), 142026 | 2020 | 10.1088/1742-6596/1412/14/142026 |
| 2 | **Mahajan, T.**, Béroff, Pons, Illescas, Chabot, IdBarkach, Launoy, Le Padellec, Jallat, Jorge, Aguirre, Díaz-Tendero | Excitation, ionization, neutralization and anionic production… | J. Phys. B **52**(19), 195204 | 2019 | 10.1088/1361-6455/ab3625 |
| 3 | IdBarkach, Chabot, Béroff, Della Negra, Lesrel, Geslin, Le Padellec, **Mahajan, T.**, Díaz-Tendero | Breakdown curves of CH$_2^+$, CH$_3^+$, CH$_4^+$ — I | Astronomy & Astrophysics **628**, A75 | 2019 | (none recorded) |
| 4 | IdBarkach, **Mahajan, T.**, Chabot, Béroff, Aguirre, Díaz-Tendero, et al. | Semiempirical breakdown curves of C$_2$N$^+$ and C$_3$N$^+$ | Molecular Astrophysics **12**, 25–32 | 2018 | 10.1016/j.molap.2018.06.003 |
| 5 | **Mahajan, T.**, Id Barkach, Aguirre, Alcami, Bonnin, Chabot, Díaz-Tendero, et al. | Excitation and fragmentation in high velocity C$_n$N$^+$–He collisions | J. Phys.: Conf. Ser. **875**(11), 102022 | 2017 | (none recorded) |
| 6 | Launoy, Béroff, Chabot, Martinet, Le Padellec, Pino, Bouneau, Vaeck, Liévin, Féraud, Loreau, **Mahajan, T.** | Ion-pair dissociation of highly excited carbon clusters | Phys. Rev. A **95**(2), 022711 | 2017 | 10.1103/PhysRevA.95.022711 |

**Two claims the leader made and you should test hardest, because they are the ones that would
embarrass him:**

- `J. Phys. B **51**(24), 245201 (2018)`, listed on `projects.html` as an IdBarkach paper, is
  claimed by the leader to be **not Thejus's at all** — he says it is *"Two-body fragmentation of
  OCS³⁺"* by Yang, Gong, Dong, Shen, Wang & Chen. **Verify this independently.**
- `J. Phys.: Conf. Ser. **1412**(11), 112028 (2020)`, also on `projects.html`, is claimed by the
  leader to be a **DOI that does not resolve (404)** and probably a garbled duplicate of row 1.
  **Verify this independently**, and if it *does* resolve for you, say so loudly — it would mean
  the leader deleted a real publication from a CV.

The leader also asserts the count was previously misstated: the CV used to claim "five
peer-reviewed publications (2018–2020)" and `experience.html` still says "5 peer-reviewed papers in
Journal of Physics B and Astronomy & Astrophysics". **Both counts and both date ranges are
suspected wrong.** Report what the evidence supports; do not adopt the leader's six without
checking it.
