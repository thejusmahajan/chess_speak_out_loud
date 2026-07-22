# Post-Validation Backlog — ideas lifted from `docs/discussion_4_ai_vision_gukesh_tal.md`

**Status: PARKED.** Do not start any of this until the problem at hand — the
small-subset diagnosis + UI validation, **with Tactical Steering (TS2) as a
witness** — is finished and the user gives the nod. This is a to-do list, not a
work order.

## Standing rules (from the user, 2026-07-22)
- **Tactical Steering (TS2 / the "Tal engine") is a CORE deliverable.** It must
  run as a witness in **every** test. We optimize it further, but never drop it.
- **Audio output (TTS voices) is DEPRIORITIZED** — likely not needed now. Keep
  the *persona* idea in **text**; park the voice/audio indefinitely.

## Lifted ideas — grounded in what already exists

### B1 — "Optical Trap" surfacing + unified intuition/search overlay  (Discussion D1)
- **Idea:** one board overlay — green = policy & search agree; **red = high policy
  prior but search refutes it (optical trap)**; gold = low policy, high search
  (hidden gem).
- **Already have:** Stage A policy screen / policy divergence (`pipeline.py`),
  hidden gems (`gems.py`), Calculation Glow, policy arrows.
- **New:** first-class "optical trap" detection (tempting-but-refuted) + the
  unified agree/trap/gem overlay. Directly the "where does my intuition fail"
  Gukesh asks for. Ties into TS2.
- **Effort: M · Value: high.**

### B2 — Spatial tensor attention RAYS (piece-to-piece sightlines)  (Discussion D2)
- **Idea:** draw directed attention rays (attacker→target, king-safety corridors)
  from LC0/BT3 intermediate-layer attention (QKᵀ), not just square heatmaps.
- **Already have:** BT3 square saliency (`neural_vision.saliency_absolute`).
- **New:** extract piece-to-piece attention from intermediate transformer layers
  via `lczerolens` → ray overlay. The flagship "AI vision" feature.
- **Effort: L (deep extraction + new UI, experimental) · Value: high but pricey.**
  Prototype in isolation before committing.

### B3 — Refutation Sparring Engine  (Discussion D3)
- **Idea:** drop the player into their *own* blind-spot positions; when they fail,
  LC0 plays the exact personal refutation and the coach explains the flaw.
- **Already have:** SRS + repertoire drills (`drills.py`, `attempts.py`), the
  blind-spot taxonomy (findings by phase/clock/opening), TS2 steer findings.
- **New:** live sparring loop = failed drill → engine plays personal refutation →
  explanation. Natural extension of drills + TS2.
- **Effort: M · Value: high training payoff.** Strong fit with the TS2 focus.

### B4 — Coach PERSONAS in text (lift persona, drop audio)  (Discussion D4, de-scoped)
- **Idea (de-scoped):** Tal / Botvinnik / DeepMind commentary. Skip TTS/audio.
- **Already have:** cached LLM coach explanations (`explanations.py`,
  `llm_client.py`).
- **New:** a `persona` parameter on explanations; a **Tal persona wired to TS2
  steer findings** (dynamic/sacrificial voice for the sacrificial repertoire).
- **Effort: S · Value: medium, high delight, cheap.** Best first pick after
  validation. Audio stays parked.

### B5 — Motif-level blind-rate matrix  (Discussion D5, mostly already done)
- **Idea:** blind rates per tactical **motif** × phase × clock.
- **Already have:** phase + clock + opening blind-rate aggregation (`pipeline.py`);
  50+ motif classifier (`backend/tactics.py`, lichess_tagger logic).
- **New:** cross the existing clock/phase aggregation with per-motif tags → a
  motif-level blind-rate breakdown. Mostly a join of two things we already have.
- **Effort: M · Value: high diagnostic specificity.**

## Research inputs (logged, not scheduled)
- **Learned look-ahead in BT3** — `docs/research_learned_lookahead.md`. The net
  simulates 3–7 plies ahead *inside its hidden layers*, and its output priors can
  **override a winning line its middle layers already found** ("forgotten
  puzzles"). Mechanistic grounding for **B1** (hidden gems / optical traps), **B2**
  (attention rays → "time-traveling heads"), and the **Tal/TS2** theme (a
  "suppressed-win" probe = exactly the sacrifices the net's own instinct flinches
  at). BT3 is the net studied, and we already do `lczerolens` layer extraction.

## Recommended order (for after the nod)
1. **B4** (Tal persona, text) — cheap, reinforces TS2, high flavor.
2. **B3** (Refutation Sparring) — high training value, extends drills + TS2.
3. **B5** (motif-level matrix) — largely a join, big specificity gain.
4. **B1** (optical-trap overlay) — solid, moderate effort.
5. **B2** (tensor rays) — flagship but expensive/experimental; prototype last.
- **Audio/TTS:** parked indefinitely.
