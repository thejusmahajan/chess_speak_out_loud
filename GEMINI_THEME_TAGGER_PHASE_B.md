# TASK FOR GEMINI — Theme-Tagger Phase B: split "sharpness" from real "sacrifice" + relabel

Phase A (committed `977edaa`) fixed the motif tagger so `findings[].motifs` now carry Lichess-correct,
**material-based** tags (`cook()` driven with the right pov/parity/real-cp). Phase B makes the training
surfaces USE that correctly: it separates the two signals we have been wrongly conflating, and removes
every user-facing "sacrifice"/"Tal" label from the signal that has no material check.

Read `docs/THEME_DEFINITIONS.md` and `docs/LICHESS_DEVIATIONS_REPORT.md` FIRST. Ground every claim there.
**Cite `file:line` for every change.** Keep suites green, add mutation tests, no push, STOP for leader review.

---

## The conceptual correction (PINNED — do not re-interpret)

There are **two distinct signals**. They must never be conflated again:

1. **SHARPNESS** — `had_tal_move` (+ `tal_move`, `complexity`, `steer`). This is a **complexity differential
   only**: "you had a *sharper / more forcing playable* move than the objective best." It has **NO material
   check** and is NOT a sacrifice. It legitimately powers a coaching signal, but it must be **named and
   labelled "sharp", never "sacrifice"/"Tal".** It drives: the existing SacDrill mechanic (`sac_drill.py`),
   the sharp-openings "sac count" (`openings_sharpness.py:71`), the general-deck "sac" filter
   (`drills.py:116`), and repertoire sharpness classification (`select_repertoire.py`).

2. **SACRIFICE (real)** — a `finding` whose corrected `motifs` (Phase A) contain `"sacrifice"`. Meaning:
   "the move you *missed* (your objective-best line) is a **sound material sacrifice** — material drops ≥2
   over the forced line and you stay winning." This is the genuine, Lichess-`cook`-based theme. It lives on
   `profile["findings"][*]["motifs"]` (confirmed: `findings` carry `motifs`; `steer_findings` do NOT).
   The real "sacrifice" surface must be sourced from **here**, NEVER from `had_tal_move`.

So: the existing steer/SacDrill machine is a **sharpness trainer** (rename + relabel it honestly). Real
sacrifice training is a **separate source** built from `findings` with the `"sacrifice"` motif ("a sound
sacrifice you missed" — exactly on-theme for the user's goal).

---

## ⚠️ CRITICAL SEQUENCING — do NOT validate against the stored profile

The stored `data/training/profile.json` was tagged with the OLD broken `analyze_pv`. Its
`findings[].motifs` are **still wrong** (645/646 carry a bogus `advantage`; **69 carry a bogus
`sacrifice`**). Those are fixed only in **Phase C** (re-tag). Therefore:
- **Phase B builds + unit-tests the machinery with SYNTHETIC fixtures only.** Do NOT assert counts against
  the stored profile, and do NOT trust its current `sacrifice`/`advantage` tags.
- The real end-to-end count of "sacrifices you missed" is a **Phase C** deliverable (after re-tagging).
- Between Phase B and Phase C the stored profile still has old keys; a short window of empty "sharp"
  surfaces on the old profile is expected and acceptable (Phase C migrates + re-tags).

---

## LEADER PRE-STEP (the leader will do this in `metrics.py` at dispatch — do NOT touch `metrics.py`)

`backend/training/metrics.py` is leader-owned. Before you start, the leader will rename **in metrics.py
only**, with behaviour **identical** (pure rename, math unchanged):
- `had_tal_move` → `had_sharp_move`
- `tal_move` → `sharp_move`

You will receive a tree where `metrics.py` already emits the new keys. Your job is the downstream rename +
re-sourcing + UI + tests below. If `metrics.py` has NOT been renamed when you start, STOP and report.

---

## Your tasks

### B0. Confirm the surface (report only, cite file:line)
List every read of `had_tal_move` / `tal_move` / `tal_moves` and every user-facing string containing
"sacrifice"/"Tal"/"sac" tied to the sharpness signal. (Known set to start from: `pipeline.py:586-646`,
`drills.py:116`, `openings_sharpness.py:71-95`, `sac_drill.py:16,48-52,88-91`, `select_repertoire.py:203-272`,
plus `frontend/.../SacDrill.tsx`, `SharpOpenings.tsx`.) Do not miss any.

### B1. Downstream rename to match `metrics.py` (behaviour identical)
Rename `had_tal_move`→`had_sharp_move`, `tal_move`→`sharp_move`, and the aggregation key
`tal_moves`→`sharp_moves` (`pipeline.py:425,632,646`) across ALL non-`metrics.py` backend files that read
them (`pipeline.py`, `drills.py`, `openings_sharpness.py`, `sac_drill.py`, `select_repertoire.py`). Pure
mechanical rename — **no logic change**. Existing steer/sharpness tests must stay green (they prove
behaviour is unchanged). Do NOT rename the stored-profile keys here — that migration is Phase C.

### B2. Re-source the REAL "sacrifice" surface (from corrected `findings[].motifs`)
Add a selector (suggest `sac_drill.select_missed_sacrifices(profile, eco=None)`) that returns `findings`
where `"sacrifice" in (f.get("motifs") or [])` — i.e. sound sacrifices the user missed. The drill "answer"
is the finding's `best["uci"]` (the sacrifice), position is `fen_before`, reveal uses `pv_san`. Reuse the
existing finding-drill shape (`drills.build_drill_from_finding`) rather than the steer mechanic. This must
**never** fall back to `had_sharp_move`. (`drills.py:116` already filters findings by motif for the deck —
prefer extending that path.)

### B3. Relabel the sharpness surfaces honestly
- `sac_drill.py`: the steer-based drill IS a sharpness drill — rename its selector/docstrings
  ("sharp move" not "sacrifice/tal") and keep its mechanic. It stays valuable, just honestly named.
- `openings_sharpness.py:71-95`: the `had_*`-derived count is a **"sharp_move" count**, not a sacrifice
  count — relabel the field/output. (Optional, low-risk: also compute a real per-opening sacrifice count
  from `findings` motifs; if you add it, name it distinctly, e.g. `missed_sacrifices`.)
- Frontend: verify #8's relabel is COMPLETE — grep `SacDrill.tsx`, `SharpOpenings.tsx`, and anywhere the
  steer/sharp signal renders for leftover "sacrifice"/"Tal"/"Tal move" copy; change to "sharp".
  The real-sacrifice surface (B2) MAY use "sacrifice" honestly.

### B4. Tests (mutation-checked — must FAIL on the wrong behaviour)
Synthetic fixtures only (no stored profile, no engine):
1. **Sharpness ≠ sacrifice**: a `steer_finding` with `had_sharp_move=True` and a `finding` at the same
   position with NO `"sacrifice"` motif ⇒ it is surfaced/labelled **"sharp"**, and `select_missed_sacrifices`
   does NOT return it. (Must fail if any surface calls it "sacrifice" or if the selector falls back to
   `had_sharp_move`.)
2. **Real sacrifice selected**: a `finding` with `"sacrifice"` in `motifs` ⇒ `select_missed_sacrifices`
   returns it; one without ⇒ excluded.
3. **Rename identity**: an existing steer/openings test still passes under the new keys (behaviour unchanged).

---

## Constraints & gates
- Do NOT touch `backend/training/metrics.py` (leader-owned; leader does the rename). Do NOT invent a
  material heuristic — real sacrifice comes ONLY from the Phase-A corrected `motifs`. Ground in
  `docs/THEME_DEFINITIONS.md`.
- Do NOT validate against the stored profile's motifs (they are stale until Phase C). Unit tests use
  synthetic fixtures.
- Backend + frontend suites stay green; add the B4 tests; `npm run build` clean. No push. STOP for leader
  review. In your report: the B0 surface list, every `file:line` changed, the 3 mutation tests + why each
  would fail on the old behaviour, and confirmation `metrics.py` was untouched by you.
