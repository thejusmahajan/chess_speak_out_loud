# WORKLOG — Elite Training System

> Append-only shared log. Newest entry on top. Every entry: date, agent
> (Leader / Gemini / Claude), phase, what was done, pasted verification output,
> open questions. Workers: paste REAL command output, never summaries of it.

## 2026-07-19 — Gemini — Phase G2: Puzzle DB mining
- Added `zstandard` and `requests` to `backend/requirements.txt`.
- Created `scratch/build_puzzle_db.py` to stream lichess puzzles and build `data/puzzles/puzzles.sqlite`.
  - Downloaded CSV header: `PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl,OpeningTags`.
  - Processed a 300,000-row sample to avoid long blocking time in development.
- Created `backend/training/puzzle_db.py` query API.
- Executed acceptance gate G2.

Gate G2 output:
```
> p=puzzle_db.motif_profile('Sicilian_Defense'); print(sorted(p.items(), key=lambda x:-x[1])[:5])
[('middlegame', 0.17838356029693722), ('short', 0.12337151565803058), ('advantage', 0.100216311882405), ('mate', 0.07165331104665454), ('crushing', 0.06017403274175311)]

> print(puzzle_db.sample_puzzles(['discoveredAttack'], None, (1500,2100), 5))
[{'id': '2Gcbp', 'fen': '8/2r5/R1Pk1p2/8/4P1p1/4K3/8/8 b - - 1 63', 'moves': 'c7g7 c6c7 d6d7 a6a8 d7c7 a8a7 c7b6 a7g7', 'rating': 1964, 'popularity': 88, 'themes': 'advancedPawn crushing discoveredAttack endgame exposedKing quietMove rookEndgame skewer veryLong', 'opening_tags': ''}, {'id': '2ZomR', 'fen': 'r1bqr1k1/ppp2ppp/8/3Qb3/8/2NB4/PPP2PPP/2KR3R b - - 0 12', 'moves': 'e5c3 d3h7 g8h7 d5h5 h7g8 d1d8', 'rating': 1954, 'popularity': 91, 'themes': 'advantage attraction discoveredAttack kingsideAttack long middlegame sacrifice', 'opening_tags': 'Scotch_Game Scotch_Game_Other_variations'}, {'id': '0rcYL', 'fen': 'r4rk1/pp3pbp/2p5/3bq1pN/5p2/3B3Q/2P2PPP/RR4K1 b - - 1 22', 'moves': 'd5e6 h5f6 g8h8 h3h7', 'rating': 1620, 'popularity': 90, 'themes': 'discoveredAttack kingsideAttack mate mateIn2 middlegame short', 'opening_tags': ''}, {'id': '25Jci', 'fen': '1r1qkb1r/pp2nppp/4p3/2ppP3/Q1P3b1/6P1/PP2PPBP/RNB2RK1 b k - 2 9', 'moves': 'e7c6 c4d5 e6d5 a4g4', 'rating': 1608, 'popularity': 90, 'themes': 'crushing discoveredAttack opening pin short', 'opening_tags': 'Kings_Indian_Attack Kings_Indian_Attack_French_Variation'}, {'id': '13kZw', 'fen': 'r2r2k1/pR1b1ppp/2p1p3/3pP3/5P2/q2B1R2/P1PQ2PP/7K b - - 5 18', 'moves': 'a8b8 d3h7 g8h7 f3a3', 'rating': 1516, 'popularity': 83, 'themes': 'advantage discoveredAttack master middlegame short', 'opening_tags': 'French_Defense French_Defense_Winawer_Variation'}]
```

## 2026-07-19 — Gemini — Phase G3: Openings matcher + Diagnostician pipeline
- Created `scratch/download_openings.py` and downloaded Lichess ECO TSVs.
- Implemented `backend/training/openings.py` with longest-prefix UCI matching and Lichess puzzle tag conversion.
- Implemented `backend/training/pipeline.py` with the 2-stage Diagnostician logic (Stage A policy divergence, Stage B engine confirmation/saliency/tactics).
- Created `scratch/test_diagnosis.py` and executed acceptance gate G3 on two test PGNs.

Gate G3 output:
```
Profile generated.
Findings count: 2
First finding:
{
  "id": "g000-p029",
  "game": {
    "white": "LC0",
    "black": "Stockfish",
    "date": "????.??.??",
    "result": "1-0"
  },
  "user_color": "white",
  "ply": 29,
  "move_number": 15,
  "fen_before": "r1b2rk1/1p1n1ppp/p3p3/q2pP3/N2Q1P2/P1P5/1P2B1PP/R3K2R w KQ - 1 15",
  "played": {
    "uci": "e1g1",
    "san": "O-O",
    "p": 0.0
  },
  "best": {
    "uci": "e1h1",
    "san": "O-O",
    "p": 0.33899999999999997
  },
  "divergence": 0.33899999999999997,
  "severity": "blind",
  "attention": {
    "engagement_played": 0.3964005410671234,
    "engagement_best": 0.3964005410671234,
    "hot_squares": [
      "a5",
      "g8"
    ],
    "blind": false
  },
  "confirmation": {
    "swing_cp": 11,
    "confirmed": false
  },
  "motifs": [
    "veryLong",
    "quietMove",
    "advantage",
    "clearance"
  ],
  "concepts": [
    "material",
    "center_control",
    "center_control",
    "center_control",
    "piece_activity",
    "piece_activity",
    "king_safety"
  ],
  "opening": {
    "eco": "C11",
    "name": "French Defense: Steinitz Variation, Boleslavsky Variation"
  },
  "pv_san": [
    "O-O",
    "Qc7",
    "b4",
    "b5",
    "Nb2",
    "Bb7",
    "a4",
    "bxa4",
    "Nxa4"
  ]
}
Aggregates:
{
  "by_motif": {
    "veryLong": {
      "missed": 0,
      "blind": 1,
      "confirmed": 0
    },
    "quietMove": {
      "missed": 0,
      "blind": 2,
      "confirmed": 0
    },
    "advantage": {
      "missed": 0,
      "blind": 2,
      "confirmed": 0
    },
    "clearance": {
      "missed": 0,
      "blind": 1,
      "confirmed": 0
    },
    "defensiveMove": {
      "missed": 0,
      "blind": 1,
      "confirmed": 0
    },
    "castling": {
      "missed": 0,
      "blind": 1,
      "confirmed": 0
    },
    "long": {
      "missed": 0,
      "blind": 1,
      "confirmed": 0
    }
  },
  "by_opening": {
    "B00": {
      "moves": 1,
      "missed": 0,
      "blind": 0,
      "blind_rate": 0.0
    },
    "C00": {
      "moves": 1,
      "missed": 0,
      "blind": 0,
      "blind_rate": 0.0
    },
    "C10": {
      "moves": 1,
      "missed": 0,
      "blind": 0,
      "blind_rate": 0.0
    },
    "C11": {
      "moves": 72,
      "missed": 0,
      "blind": 1,
      "blind_rate": 0.013888888888888888
    },
    "B20": {
      "moves": 1,
      "missed": 0,
      "blind": 0,
      "blind_rate": 0.0
    },
    "B30": {
      "moves": 1,
      "missed": 0,
      "blind": 0,
      "blind_rate": 0.0
    },
    "B32": {
      "moves": 1,
      "missed": 0,
      "blind": 0,
      "blind_rate": 0.0
    },
    "B33": {
      "moves": 50,
      "missed": 0,
      "blind": 1,
      "blind_rate": 0.02
    }
  },
  "by_concept": {
    "material": {
      "missed": 2
    },
    "center_control": {
      "missed": 6
    },
    "piece_activity": {
      "missed": 5
    },
    "king_safety": {
      "missed": 3
    },
    "pawn_structure": {
      "missed": 2
    }
  },
  "intuitive_blindness_rate": 0.015625,
  "attention_blindness_rate": 0.0
}
```

---

## 2026-07-19 — Gemini — Phase G1: Storage & job state
- Created `backend/training/store.py` with `EpdCache` and storage helpers for jobs, profiles, repertoires, and drill sets.
- Wrote and executed acceptance gate G1 test suite.

Gate G1 output:
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 5 items

backend\tests\test_training_store.py .....                               [100%]

============================== 5 passed in 0.27s ==============================
```

## 2026-07-19 — Leader (Claude Code) — Phase 0: design + foundations
- Verified oracle APIs (plan §2 table) directly against source.
- Added public `NeuralVision.saliency_absolute(fen)` (absolute frame, both colors,
  falls back gracefully) — training code must use this, never `saliency()`.
- Wrote and tested `backend/training/metrics.py` (normative math). Smoke tests:
  `ALL METRICS TESTS PASSED` (policy divergence severities, en-passant interaction
  squares, attention blindness, mover-POV confirmation swing incl. mate strings,
  quietness, top4 concentration, hidden-gem gate, WDL sharpness, alt solutions).
- Published `TRAINING_SYSTEM_PLAN.md`, `GEMINI_TRAINING_TASKS.md`,
  `CLAUDE_TRAINING_TASKS.md`.
- Open: nothing. Next: Gemini G1 ∥ Claude C1.
