# WORKER TASK — Full Salience Pipeline & Matching Engine (P1 + P2 Complete)

Build the complete **Salience Subsystem** in a single pass. This translates the vision from `docs/SALIENCE_PROBLEM.md`, `GM_CURRICULUM_PLAN.md`, and `docs/NORTH_STAR_decoding_lc0.md` into an operational dataset pipeline and salience ranking engine.

Your objective is twofold:
1. **Multi-Source Ingestion & Tiering**: Parse ALL annotated PGN sources in `scratch/annotated_games/`, tag them with strict quality tiers and provenance, and run `relational_facts` to generate `scratch/temp/salience_dataset_full.json`.
2. **Salience Matcher & Ranker**: Build `backend/training/salience_matcher.py` to map GM comment semantics to extracted facts, scoring and selecting the top 1–3 load-bearing facts while suppressing noise.

**ACCURACY IS NON-NEGOTIABLE.** Do NOT touch `metrics.py` (Leader-owned) or `relational_facts.py` (audited primitive). Cite `file:line` for all changes. Suite green, no push, STOP for leader review.

---

## 1. Subsystem Architecture & Requirements

### A. Dataset Ingestion (`backend/training/salience_dataset.py`)
- **Multi-Source Parser**: Ingests all available PGNs in `scratch/annotated_games/`:
  - `source3_great_masters.pgn` $\to$ `quality_tier: "gold"` (Public Domain Master Classics: Capablanca, Steinitz, Alekhine).
  - `source2_electronic_campfire.pgn` $\to$ `quality_tier: "silver"` (Master Open Collections).
  - `source1_lichess_broadcast.pgn` $\to$ `quality_tier: "bronze"` (Broadcast Annotations).
- **Critical Position Extractor**: Filters out bare evaluation numbers, engine lines, or comments under 10 characters. Retains substantive prose annotations.
- **Fact Pairing**: For each critical position, runs `relational_facts(fen, line_ucis=[], pov=board.turn)` to extract baseline position facts.
- **Output Artifact**: Generates `scratch/temp/salience_dataset_full.json` containing the complete tiered dataset.

### Record Schema (Non-Negotiable)
```json
{
  "fen": "r1b1k2r/3nbppp/pq2p3/1p1pPp1p/1P3P2/P2P1N2/3BQ1PP/R2NK2R b KQkq - 0 14",
  "move_san": "f5",
  "gm_comment": "Black's e6 pawn is now backward...",
  "extracted_facts": [ ... ],
  "provenance": {
    "source": "scratch/annotated_games/source3_great_masters.pgn",
    "annotator": "Steinitz / Capablanca / Alekhine",
    "license": "Public Domain"
  },
  "quality_tier": "gold"
}
```

---

### B. Salience Matcher & Ranker (`backend/training/salience_matcher.py`)
Implement the core salience alignment and selection module:

1. `align_prose_to_facts(gm_comment: str, extracted_facts: list[dict]) -> list[dict]`:
   - Maps natural language GM concepts to extracted relational fact kinds:
     - **Tactical**: `"pin"`, `"x-ray"`, `"passed pawn"`, `"fork"`, `"sacrifice"`, `"defends"`, `"removes defender"` $\to$ `pin_or_xray`, `protected_passed_pawn`, `defender_removed`, `attack_on_valuable`.
     - **Positional**: `"backward"`, `"isolated"`, `"outpost"`, `"open file"`, `"7th rank"`, `"bad bishop"`, `"dark squares"`, `"weakness"` $\to$ `pawn_weakness`, `outpost`, `file_control`, `bishop_quality`, `color_complex`.
   - Returns facts with an added `"alignment_score"` (1.0 if explicitly referenced in prose, 0.0 if incidental noise).

2. `rank_salient_facts(board_or_fen: Union[chess.Board, str], pov: chess.Color, gm_comment: Optional[str] = None, top_k: int = 3) -> list[dict]`:
   - Extracts relational facts for the position.
   - If `gm_comment` is provided (training/evaluation): ranks facts using `align_prose_to_facts`.
   - If `gm_comment` is `None` (inference/coaching mode): applies contrastive ranking rules (prioritizes active pins, defender removals, outposts, and pawn weaknesses over quiet background facts like safe pawns).
   - **Noise Filter**: Returns at most `top_k` (default 3) salient facts, filtering out the remaining noise.

---

## 2. Test Suite (`backend/tests/test_salience_pipeline.py`)

Implement a thorough acceptance and mutation test suite in `backend/tests/test_salience_pipeline.py`:

1. **`test_full_dataset_ingestion_and_tiering`**:
   - Runs `salience_dataset.py` on all 3 sources in `scratch/annotated_games/`.
   - Asserts dataset generated with `gold`, `silver`, and `bronze` quality tiers correctly populated.
2. **`test_prose_to_fact_alignment_steinitz`**:
   - Feeds Steinitz's comment *"e6 is backward"* and position FEN into `align_prose_to_facts`.
   - Asserts `pawn_weakness` (`e6` backward) achieves top alignment score (1.0) while incidental facts get 0.0.
3. **`test_prose_to_fact_alignment_capablanca`**:
   - Feeds Capablanca's comment *"White's active bishop on d3"* and position FEN into `align_prose_to_facts`.
   - Asserts `bishop_quality` (`d3` active) achieves top alignment score.
4. **`test_inference_salience_ranking_top_k_suppression`**:
   - Evaluates `rank_salient_facts` on Steinitz position with `top_k=3` without GM comment.
   - Asserts at most 3 facts are returned, and load-bearing facts (`e6` backward, dark-square complex, outpost) are prioritized over noise.
5. **`test_negative_mutation_unmatched_comments`**:
   - Asserts that irrecoverable or empty comments do not throw errors and emit `alignment_score = 0.0`.

---

## 3. Constraints & Execution Gate

- **DO NOT TOUCH**: `backend/training/metrics.py` (Leader owned).
- **DO NOT MODIFY**: `backend/training/relational_facts.py` (Audited primitive).
- **Test Command**: `python -m pytest backend/tests/test_salience_pipeline.py -o pythonpath=.`
- **Output Artifacts**:
  - `backend/training/salience_dataset.py`
  - `backend/training/salience_matcher.py`
  - `backend/tests/test_salience_pipeline.py`
  - `scratch/temp/salience_dataset_full.json`
  - `docs/SALIENCE_PIPELINE_REPORT.md` (Audit report summarizing dataset stats, alignment accuracy, and top-3 ranked facts).
- **Gate**: Full backend suite green, zero false alignments, report `file:line` for all additions. **STOP for leader review.**
