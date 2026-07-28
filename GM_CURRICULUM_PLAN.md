# GM-Annotation Curriculum — teaching the machine what's SALIENT (plan)

The strategic unlock (user, 2026-07-28). We built the relational-fact extractor (the machine's eyes,
`relational_facts.py`). The hard problem that remains is **salience** — which of the many true facts is
THE objective. Using the user as the single oracle, position by position, does not scale. **GM/coach
annotations are expert salience labels at scale.** This is the training corpus that makes the north star
(`docs/NORTH_STAR_decoding_lc0.md`) *learnable* instead of hand-tuned. The paradigm we validated on `Bc6`,
generalized: **instead of the user's analysis, the GM's annotation becomes the objective label.**

## The pipeline (the paradigm, generalized)
1. **Source** openly-available, computer-friendly annotated games — ideally **annotated PGN** (moves +
   `{comments}` + NAGs). It hands us `(FEN, GM_comment)` pairs directly.
2. **Parse** → `(FEN, gm_comment, nag, source, game_ref)`. Filter to **critical positions** (substantive
   prose explanations — not bare `!`/`?` or raw sub-variations).
3. **Run our LC0 extractor** on each FEN → relational facts + (later) forcing-tree read.
4. **Pair**: `LC0 facts  ↔  GM annotation` = one training example. The GM annotation is the salience label.
5. **Learn** which facts the GM foregrounds → the facts→coaching-language mapping (teaches salience; later
   tunes the translator, north-star S1). The user audits samples; the GM corpus does the bulk teaching.

## Leader / worker split (token-effective — this is the point)
- **Leader:** design, the data schema, the "critical position" criteria, task specs, and AUDIT of samples
  (parse quality + fact/annotation alignment). NOT the bulk labor.
- **Worker:** the labor — source research, the annotated-PGN parser, running the extractor, producing the
  paired dataset + samples for audit.

## Phases (small, validate-first — the user is ready to invest long-term)
- **P0 — Source research (dispatch NOW):** worker compiles a vetted list of open annotated-PGN sources +
  licensing + a 2–3 game sample proving the format parses. Cheap, high value. (WORKER TASK 1 below.)
- **P1 — Pilot (5–10 games):** parse → `(FEN, annotation)`, run the extractor, build the paired dataset for
  ~10–20 critical positions. Leader + user validate: do the GM annotations align with LC0's facts? Useful?
- **P2+ — Scale:** more games / more masters; build the corpus; begin the salience + translation learning.

## Honest challenges (name them up front)
- **Prose→fact alignment IS the core research.** GM comments are free text ("Black seizes the initiative");
  our facts are discrete. Aligning the two is the value AND the hard part — do not pretend it's trivial.
- **Open licensing ONLY.** Public-domain / openly-licensed sources; note the license per source. No
  paywalled scraping. Books (Dvoretsky, Yusupov, New in Chess) are copyrighted — the "extract from a book"
  idea is a deliberate FUTURE step, out of scope now.
- **Annotation quality / granularity** varies — filter to substantive positional/tactical explanations.

## Modular knowledge architecture (design decision, user, 2026-07-28)
The GM-derived knowledge is a **versioned, quality-tiered DATA ARTIFACT**, decoupled from the code that
builds it and the app that consumes it — so a bigger/better corpus can REPLACE and IMPROVE it without
touching anything else. Four independently-replaceable layers, with a stable contract between them:

1. **Extractor** (`relational_facts.py`, + forcing-tree later) — pure: position → facts. NEVER changes
   when the knowledge changes.
2. **Corpus** (append-only) — parsed records: `{fen, lc0_facts, gm_annotation, provenance{source,
   annotator, url, license}, quality_tier}`. **Provenance + quality tagged on EVERY record** — we always
   know what the knowledge is made of, and can trust/distrust accordingly.
3. **Knowledge build** — `build_knowledge(corpus, quality_filter, config) -> knowledge_vN`: deterministic,
   reproducible, runnable offline (GPU for big corpora), and **filterable by quality tier**. Emits a
   manifest (corpus hash, filter, extractor version, date, metrics). Knowledge is a BUILD OUTPUT, never
   hand-edited.
4. **Knowledge interface** — a **stable contract** the app/translator calls; the app references the
   ACTIVE knowledge version. Swapping = repoint to a new version; consumers are untouched.

**How this meets the requirements:**
- **Replace & improve:** rebuild `knowledge_v2` from a larger/better corpus → validate → promote
  (repoint active). The app is unaffected (stable interface).
- **Quality tiers / "truth" override:** every record carries `quality_tier`; a curated top tier (the
  gold/"knowledge of truth" set) OVERRIDES lower tiers. **"Absolute best knowledge" = build from gold only.**
- **Uncertain-source PGNs:** ingest them tagged at a lower tier; they inform but never override the gold.
- **Future gold mine:** ingest → rebuild → promote. No rewrite anywhere.

**Incremental path (don't over-build now):** fix the BOUNDARIES + the **record schema (with provenance +
quality_tier) from day one** — even the pilot corpus carries them. The heavy `build_knowledge` (the
salience learning), versioning, GPU batch, and promotion workflow come as we scale, and slot in without
rework. *Caveat:* the internal FORM of "knowledge" (rules vs. a learned model vs. a mapping table) is still
TBD — it is the core research — but the modularity (boundaries, provenance, quality-tiering, versioning) is
independent of that form and is fixed now.

## Masters/coaches to target (annotators or annotated-by-others)
Carlsen, Anand, Kasparov, Capablanca, Alekhine, Tal, Petrosian, Botvinnik, Lasker, Morphy (annotated by
others); coaches Dvoretsky, Yusupov, Pandolfini. Prefer whoever is **openly available in PGN** first.

---

## WORKER TASK 1 — vetted open annotated-PGN sources (dispatch)
Research + report. Web-capable worker. Cite every source with its access method and license. Do NOT
scrape paywalled content. Output `docs/annotated_sources.md`.

**Deliver a table:** `Source | Annotator(s) | Format (annotated PGN? study? text-only?) | License/openness |
Access (URL/API) | Est. volume | Parseability notes`.

**Prioritize (investigate these first):**
- **Lichess Studies** — public studies are exportable as **PGN with comments + NAGs**; huge, open, API-able.
  Confirm the export format and how to find strong/annotated studies.
- **Public-domain classic collections** — Morphy / Capablanca / Lasker / Alekhine games annotated in
  now-public-domain books, transcribed to PGN (look for open PGN repos / archives).
- **Open annotated-PGN repositories** (e.g. GitHub PGN collections with `{comments}`), TWIC, and
  lichess/chess.com **broadcasts** (annotated).
- Flag clearly copyrighted (Dvoretsky/Yusupov books, New in Chess) as **out of scope for now**.

**Then, for the TOP 2 open sources:** fetch **2–3 actual annotated games as PGN** into `scratch/temp/`,
and confirm per move that `(FEN, comment)` is extractable (python-chess reads the comments). Paste a short
sample showing a FEN + its GM comment.

**Report:** the table, the sample PGNs (paths), a one-paragraph **recommendation of the single best source
to pilot P1 with**, and any licensing caveats. STOP for leader review — the leader picks the pilot source.
