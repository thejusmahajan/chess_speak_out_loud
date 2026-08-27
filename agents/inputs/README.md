# agents/inputs — evidence a brief consumed

Raw material an audit or a brief was run **against**, kept so a verdict can be re-checked later
against the same input rather than a remembered version of it.

**This is not `agents/briefs/`.** Briefs are instructions and are immutable once filed. Inputs are
evidence: snapshots, pasted exports, logs handed over by Thejus. Do not file a brief here, and do
not leave an input in `briefs/` — that is what caused this directory to exist.

Name files `<topic>_<YYYY-MM-DD>.<ext>` so a snapshot is obviously a snapshot of a moving thing.

| file | what it is | consumed by |
|---|---|---|
| `linkedin_profile_2026-08-27.txt` | LinkedIn profile text, pasted by Thejus on 2026-08-27 — headline, About, Experience, Education, Publications, Languages. A snapshot of a live page; it will drift. | `reports/2026-08-27_public-surface-honesty-sweep_AUDIT.md` §2 |
