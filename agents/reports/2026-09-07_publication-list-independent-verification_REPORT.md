# Independent Publication List Verification Report

**Brief-ID:** `2026-09-07_publication-list-independent-verification`  
**Date:** 2026-09-07  
**Auditor:** Antigravity (Independent Verification Agent)  
**Target Application:** Helmholtz-Zentrum Hereon (`hereon_agentic_ai_1059`)  
**Deliverable:** `agents/reports/2026-09-07_publication-list-independent-verification_REPORT.md`  

---

## 0. Declaration Regarding Appendix A

In accordance with Section 2 and Acceptance Criterion 1 of the brief:
- The entire candidate publication list was reconstructed and independently verified against primary files (`ref.bib`, `cv_thejus.bib`, `publication.bib`, `mahajan2017.bib`, `mahajan2019.bib`, `mahajan2020.bib`, `tij2018.bib`) and external databases (Crossref REST API, Google Scholar profile `PJkZwAwAAAAJ`, HAL API) before Appendix A was consulted for reconciliation in Step 5.
- Because the entire brief file was viewed in full at inception, lines 266–297 were physically present in the model context; however, no anchoring on the leader's list took place: every entry was parsed from raw files and queried against publisher records from scratch before any reconciliation table was constructed.

---

## 1. Checkpoint 1 — Primary Sources Table & Analysis

### Distinct Works Found Across Primary Files
Across all 7 `.bib` files and the 2 website files (`projects.html`, `experience.html`), there are **8 distinct candidate works**:
- **6 works** originate from Thejus Mahajan's own `.bib` files. **All 6 explicitly name Thejus Mahajan in their author list.**
- **2 works** originate solely from claims on `projects.html` (items 4 and 5). Neither mentions Thejus Mahajan on the website page.

### Deduplicated Candidate Works Table

| # | Work Title | Full Author List (from source files) | Journal / Venue | Vol(Issue), Pages | Year | DOI in Source | Source Files |
|---|---|---|---|---|---|---|---|
| **1** | Excitation and fragmentation in high velocity $C_n N^+ - \text{He}$ collisions | T. Mahajan, T. Id Barkach, N.F. Aguirre, M. Alcami, M. Bonnin, M. Chabot, S. Diaz-Tendero, F. Geslin, T. Hamelin, F. Hammache, C. Illescas, A. Jallat, A. Jorge, T. Launoy, T.K.C. Le, A. LePadellec, F. Martin, A. Meyer, L. Perrot, T. Pino, B. Pons, N. de Séréville, K. Béroff | *Journal of Physics: Conference Series* | **875**(11), 102022 | 2017 | *(none in bib; URL contains stacks.iop.org link)* | `ref.bib`, `cv_thejus.bib`, `mahajan2017.bib` |
| **2** | Ion-pair dissociation of highly excited carbon clusters: Size and charge effects | Thibaut Launoy, Karine Béroff, Marin Chabot, Guillaume Martinet, Arnaud Le Padellec, Thomas Pino, Sandra Bouneau, Nathalie Vaeck, Jacques Liévin, Géraldine Féraud, Jérôme Loreau, Thejus Mahajan | *Physical Review A* | **95**(2), 022711 | 2017 | `10.1103/PhysRevA.95.022711` | `ref.bib`, `cv_thejus.bib`, `launoy2017.bibtex` |
| **3** | Semiempirical breakdown curves of $\text{C}_2\text{N}^{(+)}$ and $\text{C}_3\text{N}^{(+)}$ molecules; application to products branching ratios predictions of physical and chemical processes involving these adducts | Tijani IdBarkach, Thejus Mahajan, Marin Chabot, Karine Béroff, Néstor F. Aguirre, Sergio Diaz-Tendero, Thibaut Launoy, Arnaud Le Padellec, Luc Perrot, Maëlle A. Bonnin, Kim Cuong Le, Florian Geslin, Nicolas de Séréville, Fairouz Hammache, Aurélie Jallat, Anne Meyer, Emeline Charon, Thomas Pino, Thibault Hamelin, Valentine Wakelam | *Molecular Astrophysics* | **12**, 25–32 | 2018 | `10.1016/j.molap.2018.06.003` | `ref.bib`, `cv_thejus.bib`, `tij2018.bib` |
| **4** | Excitation, ionization, neutralization and anionic production in collisions of $\text{C}^+$, $\text{N}^+$ and $\text{C}_n\text{N}^+$ ($n=1\text{--}3$) with He atoms at 2.2 a.u velocity; cross sections and dissociation branching ratios | Thejus Mahajan, Karine Beroff, Bernard Pons, Clara Illescas, Marin Chabot, Tijani Idbarkach, Thibaut Launoy, Arnaud Le Padellec, Aurelie Jallat, Alba Jorge, Nestor Aguirre, Sergio Diaz-Tendero | *Journal of Physics B: Atomic, Molecular and Optical Physics* | *(volume/pages not in bib)* | 2019 | *(none in bib; URL contains 10.1088/1361-6455/ab3625)* | `ref.bib`, `cv_thejus.bib`, `publication.bib`, `mahajan2019.bib`, `projects.html` (#3) |
| **5** | Breakdown curves of $\text{CH}_2^{(+)}$, $\text{CH}_3^{(+)}$, and $\text{CH}_4^{(+)}$ molecules — I. Construction and application to electron collisions and UV photodissociation | T. IdBarkach, M. Chabot, K. Béroff, S. Della Negra, J. Lesrel, F. Geslin, A. Le Padellec, T. Mahajan, S. Díaz-Tendero | *Astronomy & Astrophysics* | **628**, A75 | 2019 | *(none in bib)* | `ref.bib`, `cv_thejus.bib`, `projects.html` (#2) |
| **6** | Energy deposit by electron excitation in $\text{C}_n\text{N}^+$ projectiles ($n=1\text{--}3$) colliding at intermediate velocity with He atoms: semi-empirical estimates and calculations | T. Mahajan, K. Béroff, B. Pons, C. Illescas, M. Chabot, T. Idbarkach, A. Jorge, N.F. Aguirre, S. Diaz-Tendero | *Journal of Physics: Conference Series* | **1412**(14), 142026 | 2020 | `10.1088/1742-6596/1412/14/142026` | `ref.bib`, `mahajan2020.bib`, `projects.html` (#1) |
| **7** | *(Candidate from website)* [Title not on page; claimed as IdBarkach et al.] | T. Idbarkach, et al. | *Journal of Physics B* | **51**(24), 245201 | 2018 | *(none on page)* | `projects.html` (#4) |
| **8** | *(Candidate from website)* [Title not on page; claimed as IdBarkach et al.] | T. Idbarkach, et al. | *Journal of Physics: Conference Series* | **1412**(11), 112028 | 2020 | *(none on page)* | `projects.html` (#5) |

### Metadata Variations Across Files (Signals Detected)
1. **Work 6 (`mahajan2020`) is completely absent from `cv_thejus.bib`**: It appears only in `ref.bib`, `mahajan2020.bib`, and `projects.html`. This indicates `cv_thejus.bib` was abandoned or not updated after 2019, whereas `ref.bib` was maintained up to November 2020.
2. **Missing DOIs in `.bib` files**: Work 1 (*JPCS* 2017), Work 4 (*JPhysB* 2019), and Work 5 (*A&A* 2019) had no explicit `doi = {...}` field in `ref.bib` or `cv_thejus.bib`, only IOP URLs or none at all.
3. **Missing Volume and Page numbers for Work 4 (*JPhysB* 2019) in `.bib` files**: In all four `.bib` files where it appears (`ref.bib`, `cv_thejus.bib`, `publication.bib`, `mahajan2019.bib`), `volume` and `pages` were absent, indicating it was saved as an accepted preprint / "online first" entry before final publication.
4. **Website Discrepancies (`projects.html` and `experience.html`)**:
   - `experience.html` claims: *"Published 5 peer-reviewed papers in Journal of Physics B and Astronomy & Astrophysics"* (incorrect count, misses *Phys. Rev. A* and *Molecular Astrophysics*, and conflates proceedings).
   - `projects.html` lists 5 items: only 3 match actual papers by Mahajan (items 1, 2, 3), while item 4 is a paper by a Chinese research group that does not include Mahajan or IdBarkach, and item 5 contains a non-existent citation/corrupt DOI.

---

## 2. Checkpoint 2 — DOI Resolution and Publisher Verification

Every candidate work was checked against Crossref (`api.crossref.org`) and official publisher landing pages.

### Checkpoint 2 Table

| Candidate | DOI | Resolves? | Mahajan Present? | Exact Position | Authoritative Source Used |
|---|---|---|---|---|---|
| **Work 1** (*JPCS* 2017) | `10.1088/1742-6596/875/11/102022` | **YES (HTTP 200)** | **YES** | **Author 1 of 23** | Crossref API (`works/10.1088/1742-6596/875/11/102022`) |
| **Work 2** (*PRA* 2017) | `10.1103/PhysRevA.95.022711` | **YES (HTTP 200)** | **YES** | **Author 12 of 12** | Crossref API & APS landing redirect |
| **Work 3** (*Mol. Astrophys.* 2018) | `10.1016/j.molap.2018.06.003` | **YES (HTTP 200)** | **YES** | **Author 2 of 20** | Crossref API (`works/10.1016/j.molap.2018.06.003`) & Elsevier |
| **Work 4** (*JPhysB* 2019) | `10.1088/1361-6455/ab3625` | **YES (HTTP 200)** | **YES** | **Author 1 of 12** | Crossref API (`works/10.1088/1361-6455/ab3625`) & IOP Publishing |
| **Work 5** (*A&A* 2019) | `10.1051/0004-6361/201935760` | **YES (HTTP 200)** | **YES** | **Author 8 of 9** | Crossref API (`works/10.1051/0004-6361/201935760`) & EDP Sciences |
| **Work 6** (*JPCS* 2020) | `10.1088/1742-6596/1412/14/142026` | **YES (HTTP 200)** | **YES** | **Author 1 of 9** | Crossref API (`works/10.1088/1742-6596/1412/14/142026`) & IOP Publishing |
| **Candidate 7** (*JPhysB* 2018) | `10.1088/1361-6455/aaecfe` | **YES (HTTP 200)** | **NO** | *None* (Yang et al.) | Crossref API (`works/10.1088/1361-6455/aaecfe`) |
| **Candidate 8** (*JPCS* 2020) | `10.1088/1742-6596/1412/11/112028` | **NO (HTTP 404)** | **NO** | *None* | Crossref API |

### Raw Command and API Outputs (Sample of 3+ Queries)

#### Query 1: Crossref Direct API Resolution for Work 2 (`10.1103/PhysRevA.95.022711`)
```
GET https://api.crossref.org/works/10.1103/PhysRevA.95.022711
Status: 200
Title: ['Ion-pair dissociation of highly excited carbon clusters: Size and charge effects']
Container: ['Physical Review A']
Volume: 95, Issue: 2, Page/Article: 022711, Year: 2017
Authors count: 12
  1: Thibaut Launoy
  2: Karine Béroff
  3: Marin Chabot
  4: Guillaume Martinet
  5: Arnaud Le Padellec
  6: Thomas Pino
  7: Sandra Bouneau
  8: Nathalie Vaeck
  9: Jacques Liévin
  10: Géraldine Féraud
  11: Jérôme Loreau
  12: Thejus Mahajan <-- MAHAJAN
```

#### Query 2: Crossref Direct API Resolution for Work 4 (`10.1088/1361-6455/ab3625`)
```
GET https://api.crossref.org/works/10.1088/1361-6455/ab3625
Status: 200
Title: Excitation, ionization, neutralization and anionic production in collisions of C+, N+ and CnN+ (n = 1–3) with He atoms at 2.2 a.u. velocity; cross sections and dissociation branching ratios
Container: Journal of Physics B: Atomic, Molecular and Optical Physics
Volume: 52, Issue: 19, Page/Article: 195204, Year: 2019
Authors count: 12
  1: T Mahajan <-- MAHAJAN
  2: K Béroff
  3: B Pons
  4: C Illescas
  5: M Chabot
  6: T IdBarkach
  7: T Launoy
  8: A Le Padellec
  9: A Jallat
  10: A Jorge
  11: N F Aguirre
  12: S Diaz-Tendero
```

#### Query 3: Crossref Author + Bibliographic Search for Work 5 (*Astronomy & Astrophysics*)
```
GET https://api.crossref.org/works?query.author=IdBarkach&query.bibliographic=Breakdown+curves&rows=3
Status: 200
Result:
DOI: 10.1051/0004-6361/201935760
Title: ['Breakdown curves of CH2(+), CH3(+), and CH4(+) molecules']
Journal: ['Astronomy & Astrophysics']
Vol/Page: 628 A75, Year: 2019
Authors (9): T. IdBarkach, M. Chabot, K. Béroff, S. Della Negra, J. Lesrel, F. Geslin, A. Le Padellec, T. Mahajan, S. Díaz-Tendero
Mahajan present: YES (Author 8 of 9)
```

#### Query 4: Crossref Resolution for Candidate 7 (Claimed *J. Phys. B* 51(24), 245201)
```
GET https://api.crossref.org/works/10.1088/1361-6455/aaecfe
Status: 200
Title: ['Two-body fragmentation of OCS3+: an ab initio molecular dynamics simulation study']
Journal: ['Journal of Physics B: Atomic, Molecular and Optical Physics']
Vol/Issue/Page: 51 24 245201, Year: 2018
Authors: Hongjiang Yang, Maomao Gong, Wenxiu Dong, Zhenjie Shen, Enliang Wang, Xiangjun Chen
Mahajan present: NO (Neither Mahajan nor IdBarkach appears anywhere in the record)
```

#### Query 5: Crossref Direct Resolution for Candidate 8 (Claimed *JPCS* 1412(11), 112028)
```
GET https://api.crossref.org/works/10.1088/1742-6596/1412/11/112028
Status: 404 Not Found
```

---

## 3. Checkpoint 3 — Hunt for Missing Publications

An exhaustive, multi-pronged search was performed across Crossref, HAL, and Google Scholar to discover any publications naming Thejus Mahajan that might have been omitted.

### Queries Executed
1. **Crossref Author + Keyword**: `https://api.crossref.org/works?query.author=Mahajan&query.bibliographic=Beroff+Chabot+CnN&rows=50`
2. **Crossref Author + Co-authors**:
   - `query.author=Mahajan&query.author=Beroff`
   - `query.author=Mahajan&query.author=Chabot`
   - `query.author=Mahajan&query.author=IdBarkach`
   - `query.author=Mahajan&query.author=Diaz-Tendero`
   - `query.author=Mahajan&query.author=Le+Padellec`
   - `query.author=Mahajan&query.author=Launoy`
   - `query.author=Mahajan&query.author=Aguirre`
3. **Crossref Exact Match**: `query.author=%22Thejus+Mahajan%22`
4. **French National Archive (HAL) API**: `https://api.archives-ouvertes.fr/search/?q=Thejus+Mahajan&wt=json`
5. **Google Scholar Profile**: `https://scholar.google.com/citations?hl=en&user=PJkZwAwAAAAJ`

### Checkpoint 3 Findings & Judgments

| Found Item | Source | Authors / Details | Judgment & Evidence |
|---|---|---|---|
| **`tel-02301992v1` / `10.70675/b2594e9fz9de4z4805zaf37z807505524533`**: *Excitation and fragmentation of CnN+ (n=1-3) molecules in collisions with He atoms at intermediate velocity; fundamental aspects and application to astrochemistry* | HAL / Crossref / Google Scholar row 4 | Thejus Mahajan (Sole author), Université Paris-Sud / Université Paris-Saclay, defended 2018-09-28 | **(c) PhD Thesis**. Not a peer-reviewed journal or proceedings article; properly listed under EDUCATION on CV, not in PUBLICATIONS. |
| **`10.1051/0004-6361/201935760e`**: Erratum to *Breakdown curves of CH2(+), CH3(+), and CH4(+) molecules* | Crossref | IdBarkach, Chabot, Béroff, ..., Mahajan, Díaz-Tendero. *Astronomy & Astrophysics* 636, C2 (2020) | **Erratum / Corrigendum** to Work 5, not a separate distinct research publication. |
| **Google Scholar Row 8**: *Ion pair dissociation of highly excited carbon clusters* (2016) | Google Scholar `PJkZwAwAAAAJ:UeHWp8X0CEIC` | T. Launoy, K. Béroff, M. Chabot, ..., T. Mahajan | **(c) Non-peer-reviewed conference presentation**. Slides presented by T. Launoy at Belgian Physical Society meeting (Gent, 2016-05-20). The peer-reviewed paper is the 2017 PRA paper. |
| **Google Scholar Row 9**: *Ion pair dissociation of highly excited carbon clusters and carbon-based molecules* (2016) | Google Scholar `PJkZwAwAAAAJ:d1gkVwhDpl0C` | K. Béroff, T. Launoy, ..., T. Mahajan | **(c) Institutional repository record (ULB)** for the 2016 BPS presentation. |
| **Google Scholar Row 10**: *Excitation and fragmentation of CnN molecules; Fundamental aspects and application to astrochemistry* | Google Scholar `PJkZwAwAAAAJ:ufrVoPGSRksC` | T. Mahajan, K. Béroff, M. Chabot, ... | **(c) Conference abstract** (1-page workshop abstract, `Abs63.pdf`). |
| **Dozens of papers by Aditya Mahajan, Satish Mahajan, Sunil Mahajan, Nupam P. Mahajan, etc.** | Crossref queries | E.g. *Fatigue and Task Load Dependent Decision Referrals* (IEEE CDC / LCSys, Aditya Mahajan & Jerome Le Ny) | **(b) Different persons named Mahajan**. Disambiguated by subject (control theory, medicine, botany) and zero overlap with Orsay/Paris-Saclay co-authors. |

**Result of Step 3:** **Zero genuine peer-reviewed publications were missed.** Every peer-reviewed research publication co-authored by Thejus Mahajan is accounted for.

---

## 4. Checkpoint 4 — Classification of Confirmed Works

Each confirmed work by Dr. Thejus Mahajan is categorized according to strict bibliometric criteria:

| # | Work Reference | Publication Venue | Classification | Rationale |
|---|---|---|---|---|
| **1** | Mahajan et al. (2017) | *Journal of Physics: Conference Series* **875**(11), 102022 | `PROCEEDINGS` | IOP JPCS publishes conference proceedings (ICPEAC XXX). Refereed conference series, not a primary regular journal. |
| **2** | Launoy et al. (2017) | *Physical Review A* **95**(2), 022711 | `JOURNAL` | Regular peer-reviewed archival journal published by the American Physical Society (APS). |
| **3** | IdBarkach, Mahajan et al. (2018) | *Molecular Astrophysics* **12**, 25–32 | `JOURNAL` | Peer-reviewed archival journal published by Elsevier. |
| **4** | Mahajan et al. (2019) | *Journal of Physics B: At. Mol. Opt. Phys.* **52**(19), 195204 | `JOURNAL` | Regular peer-reviewed archival journal published by IOP Publishing. |
| **5** | IdBarkach et al. (2019) | *Astronomy & Astrophysics* **628**, A75 | `JOURNAL` | Leading European peer-reviewed astronomical journal published by EDP Sciences. |
| **6** | Mahajan et al. (2020) | *Journal of Physics: Conference Series* **1412**(14), 142026 | `PROCEEDINGS` | IOP JPCS proceedings volume (ICPEAC XXXI, Deauville). |
| — | Mahajan (2018) | Université Paris-Saclay | `THESIS` | Doctoral dissertation (NNT: 2018SACLS349). |

### Summary Counts
- `JOURNAL` (peer-reviewed archival journal articles): **4**
- `PROCEEDINGS` (peer-reviewed conference proceedings volumes): **2**
- `THESIS` (doctoral dissertation): **1**
- `OTHER` (conference presentations / slides / abstracts): **3**

> [!NOTE]
> The CV heading on page 3 reads: *"PUBLICATIONS: Peer-reviewed work in atomic, molecular and collision physics applied to astrochemistry."* This phrasing is strictly accurate because all 6 entries represent refereed scientific papers (4 in regular journals, 2 in indexed refereed conference proceedings). However, the website claim (*"5 peer-reviewed papers in Journal of Physics B and Astronomy & Astrophysics"*) misstated both the count (5 instead of 6, or 5 instead of 4 journals) and the journals (omitting *Phys. Rev. A* and *Mol. Astrophys.*).

---

## 5. Checkpoint 5 — Reconciliation with Leader's List (Appendix A)

| # | In the Leader's List (Appendix A) | In Independent Audit List | Verdict | Evidence / Details |
|---|---|---|---|---|
| **1** | **Mahajan, T.**, Béroff, Pons, Illescas, Chabot, Idbarkach, Jorge, Aguirre, Díaz-Tendero (2020)<br>*Energy deposit by electron excitation in C$_n$N$^+$ projectiles*<br>J. Phys.: Conf. Ser. **1412**(14), 142026<br>DOI: `10.1088/1742-6596/1412/14/142026` | Identical. | `AGREE` | Crossref record confirms all authors, venue, volume, issue, article number, and year. Mahajan is 1st author. DOI resolves. |
| **2** | **Mahajan, T.**, Béroff, Pons, Illescas, Chabot, IdBarkach, Launoy, Le Padellec, Jallat, Jorge, Aguirre, Díaz-Tendero (2019)<br>*Excitation, ionization, neutralization and anionic production…*<br>J. Phys. B **52**(19), 195204<br>DOI: `10.1088/1361-6455/ab3625` | Identical. | `AGREE` | Crossref record confirms all 12 authors in identical order, Vol 52, Issue 19, Art. 195204, Year 2019. Mahajan is 1st author. DOI resolves. |
| **3** | IdBarkach, Chabot, Béroff, Della Negra, Lesrel, Geslin, Le Padellec, **Mahajan, T.**, Díaz-Tendero (2019)<br>*Breakdown curves of CH$_2^+$, CH$_3^+$, CH$_4^+$ — I*<br>Astronomy & Astrophysics **628**, A75<br>DOI: `(none recorded)` | Paper identical, but **DOI exists and was discovered**: `10.1051/0004-6361/201935760` | `AGREE` on paper;<br>`LEADER HAS IT WRONG` on DOI | The paper is confirmed (Mahajan is Author 8 of 9). However, the leader recorded `(none recorded)` for the DOI. The registered DOI `10.1051/0004-6361/201935760` resolves via Crossref to EDP Sciences. *(Harmless omission on CV, but factual discrepancy in leader's metadata table).* |
| **4** | IdBarkach, **Mahajan, T.**, Chabot, Béroff, Aguirre, Díaz-Tendero, et al. (2018)<br>*Semiempirical breakdown curves of C$_2$N$^+$ and C$_3$N$^+$*<br>Molecular Astrophysics **12**, 25–32<br>DOI: `10.1016/j.molap.2018.06.003` | Identical. | `AGREE` | Crossref record confirms all 20 authors in identical order, Vol 12, pp. 25–32, Year 2018. Mahajan is Author 2 of 20. DOI resolves. |
| **5** | **Mahajan, T.**, Id Barkach, Aguirre, Alcami, Bonnin, Chabot, Díaz-Tendero, et al. (2017)<br>*Excitation and fragmentation in high velocity C$_n$N$^+$–He collisions*<br>J. Phys.: Conf. Ser. **875**(11), 102022<br>DOI: `(none recorded)` | Paper identical, but **DOI exists and was discovered**: `10.1088/1742-6596/875/11/102022` | `AGREE` on paper;<br>`LEADER HAS IT WRONG` on DOI | The paper is confirmed (Mahajan is 1st author of 23). However, the leader recorded `(none recorded)` for the DOI. The registered DOI `10.1088/1742-6596/875/11/102022` resolves via Crossref to IOP Publishing. *(Harmless omission on CV, but factual discrepancy in leader's metadata table).* |
| **6** | Launoy, Béroff, Chabot, Martinet, Le Padellec, Pino, Bouneau, Vaeck, Liévin, Féraud, Loreau, **Mahajan, T.** (2017)<br>*Ion-pair dissociation of highly excited carbon clusters*<br>Phys. Rev. A **95**(2), 022711<br>DOI: `10.1103/PhysRevA.95.022711` | Identical. | `AGREE` | Crossref record confirms all 12 authors in identical order, Vol 95, Issue 2, Art. 022711, Year 2017. Mahajan is Author 12 of 12. DOI resolves. |

### Hard Claims Tested

1. **Claim 1: `J. Phys. B 51(24), 245201 (2018)` listed on `projects.html` is not Thejus's paper.**
   - **Verdict:** `LEADER IS 100% CORRECT`.
   - **Evidence:** Crossref DOI `10.1088/1361-6455/aaecfe` confirms this paper is *"Two-body fragmentation of OCS3+: an ab initio molecular dynamics simulation study"* by Yang, Gong, Dong, Shen, Wang, and Chen. It has nothing to do with Thejus Mahajan, Tijani IdBarkach, or Paris-Saclay.
2. **Claim 2: `J. Phys.: Conf. Ser. 1412(11), 112028 (2020)` on `projects.html` is a 404 (does not resolve).**
   - **Verdict:** `LEADER IS 100% CORRECT`.
   - **Evidence:** HTTP GET to `https://api.crossref.org/works/10.1088/1742-6596/1412/11/112028` returns HTTP 404. No such article exists in volume 1412 of JPCS. The true ICPEAC 2019 conference paper is issue 14, article 142026.

---

## 6. Checkpoint 6 — Verification of Built PDFs Against Source

All commands were executed in `C:\Users\Admin\Documents\bioinformatics_project\job_search\applications\hereon_agentic_ai_1059`.

### Command 1: Rendered Text of CV Page 3 (`pdftotext -f 3 -l 3 cv_hereon_1059.pdf -`)
```
PUBLICATIONS
Peer-reviewed work in atomic, molecular and collision physics applied to astrochemistry. Author name in bold. Full record: Google Scholar.

1. Mahajan, T., Béroff, K., Pons, B., Illescas, C., Chabot, M., Idbarkach, T., Jorge, A., Aguirre, N. F., Díaz-Tendero, S. Energy deposit
by electron excitation in Cn N+ projectiles (n=1–3) colliding at intermediate velocity with He atoms: semi-empirical estimates and
calculations. Journal of Physics: Conference Series 1412(14), 142026 (2020). doi:10.1088/1742-6596/1412/14/142026
2. Mahajan, T., Béroff, K., Pons, B., Illescas, C., Chabot, M., IdBarkach, T., Launoy, T., Le Padellec, A., Jallat, A., Jorge, A., Aguirre,
N. F., Díaz-Tendero, S. Excitation, ionization, neutralization and anionic production in collisions of C+ , N+ and Cn N+ (n=1–3) with
He atoms at 2.2 a.u. velocity; cross sections and dissociation branching ratios. Journal of Physics B: Atomic, Molecular and Optical
Physics 52(19), 195204 (2019). doi:10.1088/1361-6455/ab3625
3. IdBarkach, T., Chabot, M., Béroff, K., Della Negra, S., Lesrel, J., Geslin, F., Le Padellec, A., Mahajan, T., Díaz-Tendero, S. Break+
+
down curves of CH+
2 , CH3 and CH4 molecules — I. Construction and application to electron collisions and UV photodissociation.
Astronomy & Astrophysics 628, A75 (2019).
4. IdBarkach, T., Mahajan, T., Chabot, M., Béroff, K., Aguirre, N. F., Díaz-Tendero, S., et al. Semiempirical breakdown curves of
C2 N+ and C3 N+ molecules; application to products branching ratios predictions of physical and chemical processes involving these
adducts. Molecular Astrophysics 12, 25–32 (2018). doi:10.1016/j.molap.2018.06.003
5. Mahajan, T., Id Barkach, T., Aguirre, N. F., Alcami, M., Bonnin, M., Chabot, M., Díaz-Tendero, S., et al. Excitation and fragmentation
in high velocity Cn N+ –He collisions. Journal of Physics: Conference Series 875(11), 102022 (2017).
6. Launoy, T., Béroff, K., Chabot, M., Martinet, G., Le Padellec, A., Pino, T., Bouneau, S., Vaeck, N., Liévin, J., Féraud, G., Loreau,
J., Mahajan, T. Ion-pair dissociation of highly excited carbon clusters: size and charge effects. Physical Review A 95(2), 022711
(2017). doi:10.1103/PhysRevA.95.022711
In preparation: manuscript on phytoplankton trait evolution from the post-doctoral work (Lagrangian individual-based model, GOTM–FABM); submission
planned 2026.

Hamburg, 7 September 2026
Dr. Thejus Mahajan
```

### Command 2: PDF Info for `cv_hereon_1059.pdf` (`pdfinfo cv_hereon_1059.pdf`)
```
Creator:        LaTeX with hyperref
Producer:       pdfTeX-1.40.20
CreationDate:   Mon Sep  7 20:58:01 2026 W. Europe Daylight Time
ModDate:        Mon Sep  7 20:58:01 2026 W. Europe Daylight Time
Tagged:         no
UserProperties: no
Suspects:       no
Form:           none
JavaScript:     no
Pages:          3
Encrypted:      no
Page size:      595.276 x 841.89 pts (A4)
Page rot:       0
File size:      261218 bytes
Optimized:      no
PDF version:    1.5
```

### Command 3: PDF Info for `Mahajan_CoverLetter_CV_1059.pdf` (`pdfinfo Mahajan_CoverLetter_CV_1059.pdf`)
```
Creator:        TeX
Producer:       pdfTeX-1.40.20
CreationDate:   Mon Sep  7 20:58:05 2026 W. Europe Daylight Time
ModDate:        Mon Sep  7 20:58:05 2026 W. Europe Daylight Time
Tagged:         no
UserProperties: no
Suspects:       no
Form:           none
JavaScript:     no
Pages:          4
Encrypted:      no
Page size:      595.276 x 841.89 pts (A4)
Page rot:       0
File size:      357513 bytes
Optimized:      no
PDF version:    1.5
```

### Command 4: PDF Info for `Mahajan_Additional_Documents_1059.pdf` (`pdfinfo Mahajan_Additional_Documents_1059.pdf`)
```
Creator:        TeX
Producer:       pdfTeX-1.40.20
CreationDate:   Mon Sep  7 20:43:47 2026 W. Europe Daylight Time
ModDate:        Mon Sep  7 20:43:47 2026 W. Europe Daylight Time
Tagged:         no
UserProperties: no
Suspects:       no
Form:           none
JavaScript:     no
Pages:          19
Encrypted:      no
Page size:      595.276 x 841.89 pts (A4)
Page rot:       0
File size:      1981146 bytes
Optimized:      no
PDF version:    1.5
```

*(For completeness: `pdfinfo cover_letter_hereon_1059.pdf` confirms `Pages: 1`, `File size: 95647 bytes`).*

### Checks and Metrics
1. **Source Fidelity**: Page 3 of `cv_hereon_1059.pdf` lists exactly the 6 works present in `cv_hereon_1059.tex`, preserving all volumes, issues, article numbers, and publication years without typesetting errors.
2. **Page Counts**:
   - Cover Letter: **1 page**
   - CV: **3 pages**
   - Combined Application Bundle (`Mahajan_CoverLetter_CV_1059.pdf`): **4 pages**
   - Additional Documents / Certificates (`Mahajan_Additional_Documents_1059.pdf`): **19 pages**
   - All page counts strictly match requirements.
3. **File Size Compliance for Portal Upload**:
   - `Mahajan_CoverLetter_CV_1059.pdf`: 357,513 bytes (0.34 MiB / 0.36 MB)
   - `Mahajan_Additional_Documents_1059.pdf`: 1,981,146 bytes (1.89 MiB / 1.98 MB)
   - **Combined Total Size**: **2,338,659 bytes (2.23 MiB / 2.34 MB)**
   - **Compliance:** **PASSED**. Well below Hereon's 5.0 MB portal upload limit.
4. **DOI Resolution Directly From Rendered PDF Text**:
   Every DOI extracted directly from page 3 was tested via HTTP resolution against `doi.org`:
   - `doi:10.1088/1742-6596/1412/14/142026` $\rightarrow$ **HTTP 302** $\rightarrow$ `https://iopscience.iop.org/article/10.1088/1742-6596/1412/14/142026` (**RESOLVED**)
   - `doi:10.1088/1361-6455/ab3625` $\rightarrow$ **HTTP 302** $\rightarrow$ `https://iopscience.iop.org/article/10.1088/1361-6455/ab3625` (**RESOLVED**)
   - `doi:10.1016/j.molap.2018.06.003` $\rightarrow$ **HTTP 302** $\rightarrow$ `https://linkinghub.elsevier.com/retrieve/pii/S2405675818300125` (**RESOLVED**)
   - `doi:10.1103/PhysRevA.95.022711` $\rightarrow$ **HTTP 302** $\rightarrow$ `https://link.aps.org/doi/10.1103/PhysRevA.95.022711` (**RESOLVED**)

---

## 7. Audit Verdict

**YES, the publication list on this CV is safe to send.**

---

## 8. What I Could Not Check

1. **Full-text content of the 21 MB PhD thesis PDF (`71997_MAHAJAN_2018_diffusion.pdf`)**: While the HAL metadata, official degree records, and all external databases were verified, the full internal 200+ page PDF text was not OCR-mined end-to-end to see if any additional non-indexed conference poster or internal workshop note was mentioned in an acknowledgments or preface section.
2. **Direct browser rendering of Physical Review A (`PhysRevA.95.022711`) without Cloudflare intervention**: The APS server challenges automated HTTP CLI clients with a Cloudflare managed challenge (HTTP 403); while `doi.org` confirmed the HTTP 302 redirect directly to `link.aps.org/doi/10.1103/PhysRevA.95.022711` and the Crossref API returned the full 12-author record with Thejus Mahajan in position 12, the final styled HTML document was not rendered in a headless browser.
3. **The live web portal interface of Helmholtz-Zentrum Hereon**: The actual web upload forms and applicant tracking software constraints of Hereon's HR portal could not be tested directly.

---

## 9. Standing Question

> **If exactly one thing in this delivery is wrong, what is it most likely to be, and did I check that?**

**Answer:**
The thing most likely to be wrong would be **a reviewer on the hiring committee interpreting "Peer-reviewed work" as meaning exclusively primary archival journal articles, and viewing the inclusion of two *Journal of Physics: Conference Series* papers as an overstatement.**

**Did I check that?**
Yes. In Step 4, I explicitly segregated the 6 items into:
- 4 peer-reviewed archival `JOURNAL` articles (*Physical Review A*, *Molecular Astrophysics*, *Journal of Physics B*, *Astronomy & Astrophysics*).
- 2 peer-reviewed conference `PROCEEDINGS` volumes (*Journal of Physics: Conference Series* 875 and 1412).

Both *JPCS* volumes are refereed conference proceedings indexed in Scopus/Web of Science, where full papers are peer-reviewed by conference referees before publication. On German/European academic CVs, grouping them under "Peer-reviewed work" with full venue titles (*Journal of Physics: Conference Series*) is customary, transparent, and accurate, as the venue name explicitly discloses the conference proceedings nature of the volume. However, the leader should be aware that the count of regular journal articles is 4, and the count of conference proceedings is 2.
