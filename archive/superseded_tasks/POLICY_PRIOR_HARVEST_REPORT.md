# Policy-Prior vs Search Harvest Report

## Metadata & Execution Parameters

- **Weights file**: `BT3-768x15x24h-swa-2790000.pb.gz`
- **Engine executable**: `engine/lc0.exe` (v0.32.1 built Nov 23 2025)
- **ONNX model**: `engine/bt3.onnx`
- **PGN source**: `games_of_derdiedasdie/lichess_derdiedasdie_2026-07-21.pgn`
- **Prior node count**: `nodes=1`
- **Search node count**: `nodes=20000`
- **Sampling seed**: `20260815`
- **Final sample size**: $N = 150$
- **Total wall-clock harvest time**: `9090.91s (2.53 hours)`
- **Output JSON path**: `data/policy_prior/harvest.json`
- **Git commit**: `e54bbdbc6285892b88b416b15ad1ab07bcd905fa`

---

## Files Created & Modified

### 1. `backend/training/policy_prior_harvest.py`
- [extract_candidates](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/policy_prior_harvest.py#L44-L86): Filters games for user `derdiedasdie`, ply $16 \le \text{ply} \le 80$, $\ge 10$ pieces on board.
- [parse_eval](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/policy_prior_harvest.py#L89-L110): Converts engine centipawn scores to integer centipawns and maps `M{x}` mates to $\pm 10000$.
- [run_harvest](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/policy_prior_harvest.py#L113-L288): Samples $N$ positions with fixed seed `20260815`, evaluates LC0 policy prior (`nodes=1`), searches position FEN (`nodes=20000`), searches after-move FEN (`nodes=20000`), computes POV-adjusted centipawn scores and prior ranks, and saves atomically via `store._write_json_atomic` on every position with resume support.
- [compute_metrics](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/policy_prior_harvest.py#L291-L420): Computes overturn rate, rank histogram, prior mass on searched best move, player agreement rates, blunder vs non-blunder subset comparison, and sanity null-rank counts.
- [print_report](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/policy_prior_harvest.py#L423-L515): Prints formatted tables for all 6 metric categories and 5 deterministic sample raw JSON records.
- [run_cross_check](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/policy_prior_harvest.py#L518-L612): Evaluates the first 20 harvest positions using both ONNX `NeuralVision.evaluate_batch` and LC0 engine prior (`nodes=1`), reporting top-3 policy, value, WDL, top-1 agreement, and anomaly flags.

### 2. `scratch/probe_policy.py`
- [test_engine_primitives](file:///c:/Users/Admin/Documents/chess_speak_out_loud/scratch/probe_policy.py#L25-L95): Verification script for Checkpoint 1 (Start and Middlegame FENs).
- [timing_pilot](file:///c:/Users/Admin/Documents/chess_speak_out_loud/scratch/probe_policy.py#L98-L200): Timing pilot runner for Checkpoint 2 (20 candidate positions).

---

## Verifications

### Checkpoint 1: Engine Primitives Verification

Command: `python scratch/probe_policy.py`

```text
Starting LC0 with weights BT3-768x15x24h-swa-2790000.pb.gz...

=== Test 1: Start Position ===
FEN: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
Policy extraction took 3.003s
Policy sum of p: 1.000300
All n == 0: True
Top 10 moves by prior:
  1. d2d4 (d4): p=0.1274, n=0
  2. g1f3 (Nf3): p=0.1248, n=0
  3. c2c4 (c4): p=0.1084, n=0
  4. g2g3 (g3): p=0.0925, n=0
  5. e2e4 (e4): p=0.0846, n=0
  6. e2e3 (e3): p=0.0774, n=0
  7. b2b3 (b3): p=0.0734, n=0
  8. b1c3 (Nc3): p=0.0634, n=0
  9. c2c3 (c3): p=0.0385, n=0
  10. a2a3 (a3): p=0.0336, n=0
Search (nodes=20000) took 29.835s
Search Eval: +12 cp | Best move: d2d4

=== Test 2: Middlegame Position ===
FEN: r1bqkb1r/pp3ppp/2n1pn2/2pp4/2PP4/2N1PN2/PP3PPP/R1BQKB1R w KQkq - 0 6
Policy extraction took 7.369s
Policy sum of p: 0.999800
All n == 0: True
Top 10 moves by prior:
  1. c4d5 (cxd5): p=0.3060, n=0
  2. f1e2 (Be2): p=0.1804, n=0
  3. a2a3 (a3): p=0.1691, n=0
  4. f1d3 (Bd3): p=0.1287, n=0
  5. c4c5 (c5): p=0.0526, n=0
  6. d4c5 (dxc5): p=0.0519, n=0
  7. f1b5 (Bb5): p=0.0334, n=0
  8. b2b4 (b4): p=0.0177, n=0
  9. d1c2 (Qc2): p=0.0142, n=0
  10. h2h3 (h3): p=0.0135, n=0
Search (nodes=20000) took 26.854s
Search Eval: +19 cp | Best move: c4d5
```

---

### Checkpoint 2: Timing Pilot (20 Positions)

Command: `python scratch/probe_policy.py --timing-pilot`

```text
Running 20-position timing pilot with seed 20260815...
Candidate pool size: 186132

[01/20] FEN: 2r2rk1/pp2qpp1/5np1/3N4/3N3P/1Q2PPb1/PP1B2P1/1K1R4 b - - 0 20
       Policy (nodes=1): 5.336s | Search (nodes=20000): 24.286s
[02/20] FEN: r1b1k1nr/p1pp1ppp/1Bp2q2/8/4P3/2N5/PPP2PPP/R2QKB1R b KQkq - 0 8
       Policy (nodes=1): 3.878s | Search (nodes=20000): 26.797s
[03/20] FEN: 4r1k1/p1pq1ppp/2n5/2Pp4/5B2/P2Q1N1P/5PP1/6K1 b - - 2 24
       Policy (nodes=1): 3.682s | Search (nodes=20000): 27.961s
[04/20] FEN: 2kr3r/ppp1bp1p/2nq1p2/1Q6/3p4/1BP2P1P/P2N1P2/2KR3R w - - 0 16
       Policy (nodes=1): 2.865s | Search (nodes=20000): 28.294s
[05/20] FEN: 1r3rk1/ppp1qpp1/5bnp/8/2B1N3/1Q5P/PPP3P1/3R1R1K w - - 0 21
       Policy (nodes=1): 4.900s | Search (nodes=20000): 29.841s
[06/20] FEN: r2q1rk1/bppb1pp1/2np1n1p/p3p3/P1B1P3/2PPBN1P/1PQN1PP1/R4RK1 b - - 0 11
       Policy (nodes=1): 5.225s | Search (nodes=20000): 24.748s
[07/20] FEN: 8/p3kp1Q/3qp3/3nN3/n2P4/r7/P4PPP/R4RK1 b - - 2 26
       Policy (nodes=1): 4.653s | Search (nodes=20000): 24.197s
[08/20] FEN: r1b1kr2/1pp1pq1p/p1n3p1/1Q6/3Pp3/1P6/P1P1PPPP/2KR1B1R w q - 0 15
       Policy (nodes=1): 2.466s | Search (nodes=20000): 24.348s
[09/20] FEN: r1bqkb1r/pp3ppp/2n1pn2/8/2Q5/2N1PN2/PP2BPPP/R1B1K2R b KQkq - 2 8
       Policy (nodes=1): 3.164s | Search (nodes=20000): 26.188s
[10/20] FEN: 1r1q1r2/p3p1bk/2p3pp/3p1p2/N2Pn2B/1P2PQ1P/P4PP1/R2R2K1 w - - 0 17
       Policy (nodes=1): 15.376s | Search (nodes=20000): 29.226s
[11/20] FEN: 2r2rk1/pp3pb1/2n3pp/3B4/4P3/2P4N/PP5B/2K4R w - - 2 22
       Policy (nodes=1): 2.394s | Search (nodes=20000): 25.103s
[12/20] FEN: r1bq1rk1/1p2ppbp/p1np2p1/8/P1N1P1n1/4BN2/1PP1BPPP/R2Q1RK1 w - - 4 14
       Policy (nodes=1): 2.566s | Search (nodes=20000): 28.918s
[13/20] FEN: r1bqk1nr/ppp2ppp/5b2/4p3/2BpPP2/2P5/PP4PP/RNBQ1RK1 w kq - 1 9
       Policy (nodes=1): 6.183s | Search (nodes=20000): 29.439s
[14/20] FEN: 5r1r/pp2k2p/2p1b1q1/3n1ppR/2pP2P1/2N1PQ2/PPBK1P2/R7 w - - 3 22
       Policy (nodes=1): 3.371s | Search (nodes=20000): 26.650s
[15/20] FEN: 3r4/1p6/1p3k1p/2b5/P7/2P1NP2/1PB5/1K4R1 w - - 1 37
       Policy (nodes=1): 3.965s | Search (nodes=20000): 29.295s
[16/20] FEN: 2r1r1k1/5pp1/1p3qn1/pP1p4/P2Pp2p/1N2P2P/5PP1/2RQ1RK1 b - - 3 23
       Policy (nodes=1): 1.445s | Search (nodes=20000): 27.864s
[17/20] FEN: r3r1k1/pp1R1pp1/2p4p/4qB2/8/4nPP1/PP3P2/1QR3K1 w - - 2 23
       Policy (nodes=1): 5.178s | Search (nodes=20000): 28.928s
[18/20] FEN: r1b1kb1r/pp3ppp/1q3n2/3pN3/3P4/1P6/P1P1BPPP/RN1QK2R b KQkq - 0 9
       Policy (nodes=1): 5.424s | Search (nodes=20000): 29.835s
[19/20] FEN: r5k1/1p3ppp/1Pb5/8/p7/5P2/6PP/R5K1 b - - 0 35
       Policy (nodes=1): 5.188s | Search (nodes=20000): 23.756s
[20/20] FEN: r3k2r/pppq1npR/4p3/4P1p1/1b1p2P1/2NQ1PB1/PPP1P3/R3KB2 w Qkq - 0 15
       Policy (nodes=1): 4.434s | Search (nodes=20000): 26.697s

=== Timing Summary ===
Mean policy time per position (nodes=1) : 4.585s
Mean search time per position (nodes=20000): 27.119s
Estimated time per position (1 policy + 2 searches): 58.822s
Budget (3.0 hours = 10800s):
  Max N = 10800 / 58.822 = 183 positions
  Chosen N = 150 positions (est. 8823.3s = 2.45h)
```

---

### Checkpoint 4: Metrics Report ($N = 150$)

Command: `python backend/training/policy_prior_harvest.py report`

```text
================================================================================
                      POLICY-PRIOR VS SEARCH HARVEST REPORT                     
================================================================================
Weights file      : BT3-768x15x24h-swa-2790000.pb.gz
Prior nodes       : 1
Search nodes      : 20000
Sample seed       : 20260815
Target N          : 150
Harvested N       : 150
Git commit        : e54bbdbc6285892b88b416b15ad1ab07bcd905fa
Timestamp         : 2026-08-15T03:26:50.371940Z
Mate mapping      : +-10000 cp
================================================================================

1. OVERTURN RATE
--------------------------------------------------------------------------------
Total positions   : 150
Overturned (prior != searched): 21
Overturn rate     : 0.1400 (14.00%)
--------------------------------------------------------------------------------

2. RANK HISTOGRAM (prior rank of searched best move)
--------------------------------------------------------------------------------
Rank Category   | Count    | Fraction  
--------------------------------------------------------------------------------
1               | 129      | 86.00%
2               | 16       | 10.67%
3               | 1        | 0.67%
4-5             | 2        | 1.33%
6-10            | 0        | 0.00%
>10             | 0        | 0.00%
null            | 2        | 1.33%
--------------------------------------------------------------------------------

3. PRIOR MASS ON SEARCHED BEST MOVE
--------------------------------------------------------------------------------
Subset               | Mean prior p    | Median prior p 
--------------------------------------------------------------------------------
All positions        | 0.3998          | 0.3393         
Overturned           | 0.2056          | 0.2065         
Retained             | 0.4284          | 0.3636         
--------------------------------------------------------------------------------

4. PLAYER AGREEMENT
--------------------------------------------------------------------------------
Agreement with Prior Top-1 (played == prior_top1)   : 0.5267 (52.67%)
Agreement with Searched Best (played == searched_best): 0.5133 (51.33%)
--------------------------------------------------------------------------------

5. BLUNDER SUBSET VS NON-BLUNDER SUBSET (eval_loss_cp >= 100)
--------------------------------------------------------------------------------
Subset             | N      | Agree Prior Top-1    | Mean Prior p of Played
--------------------------------------------------------------------------------
Blunders (>=100)   | 55     | 30.91              % | 0.1900                
Non-Blunders       | 95     | 65.26              % | 0.3847                
--------------------------------------------------------------------------------

6. SANITY COUNTS
--------------------------------------------------------------------------------
Positions harvested                 : 150
Null ranks for searched best move   : 2
Null ranks for played move          : 2
================================================================================

5 SAMPLE RAW JSON RECORDS (deterministic seed 20260815):
--------------------------------------------------------------------------------

--- Sample Record #1 ---
{
  "game_site": "https://lichess.org/81iQ08tQ",
  "ply": 49,
  "fen": "r5k1/3r1ppp/2Nqpn2/PP1p4/2p5/2P1P3/2Q2PPP/RR4K1 w - - 0 25",
  "user_color": "white",
  "played_uci": "a5a6",
  "played_san": "a6",
  "prior": [
    {
      "uci": "a5a6",
      "san": "a6",
      "p": 0.211,
      "n": 0
    },
    {
      "uci": "c2b2",
      "san": "Qb2",
      "p": 0.1098,
      "n": 0
    },
    {
      "uci": "c2a4",
      "san": "Qa4",
      "p": 0.1024,
      "n": 0
    },
    {
      "uci": "f2f3",
      "san": "f3",
      "p": 0.0854,
      "n": 0
    },
    {
      "uci": "c6d4",
      "san": "Nd4",
      "p": 0.073,
      "n": 0
    },
    {
      "uci": "h2h3",
      "san": "h3",
      "p": 0.051,
      "n": 0
    },
    {
      "uci": "c2d1",
      "san": "Qd1",
      "p": 0.0442,
      "n": 0
    },
    {
      "uci": "c2d2",
      "san": "Qd2",
      "p": 0.0369,
      "n": 0
    },
    {
      "uci": "c2c1",
      "san": "Qc1",
      "p": 0.024,
      "n": 0
    },
    {
      "uci": "c2a2",
      "san": "Qa2",
      "p": 0.0235,
      "n": 0
    }
  ],
  "prior_top1_uci": "a5a6",
  "searched_best_uci": "a5a6",
  "searched_eval_cp": 1137,
  "played_eval_cp": 663,
  "prior_rank_of_searched_best": 1,
  "prior_p_of_searched_best": 0.211,
  "prior_rank_of_played": 1,
  "prior_p_of_played": 0.211
}

--- Sample Record #2 ---
{
  "game_site": "https://lichess.org/1cIXzF1g",
  "ply": 29,
  "fen": "r1b1kr2/1pp1pq1p/p1n3p1/1Q6/3Pp3/1P6/P1P1PPPP/2KR1B1R w q - 0 15",
  "user_color": "white",
  "played_uci": "b5c5",
  "played_san": "Qc5",
  "prior": [
    {
      "uci": "b5c5",
      "san": "Qc5",
      "p": 0.2783,
      "n": 0
    },
    {
      "uci": "b5g5",
      "san": "Qg5",
      "p": 0.1949,
      "n": 0
    },
    {
      "uci": "b5a4",
      "san": "Qa4",
      "p": 0.1466,
      "n": 0
    },
    {
      "uci": "b5c4",
      "san": "Qc4",
      "p": 0.1445,
      "n": 0
    },
    {
      "uci": "b5d5",
      "san": "Qd5",
      "p": 0.0199,
      "n": 0
    },
    {
      "uci": "c2c4",
      "san": "c4",
      "p": 0.0079,
      "n": 0
    },
    {
      "uci": "a2a3",
      "san": "a3",
      "p": 0.0076,
      "n": 0
    },
    {
      "uci": "e2e3",
      "san": "e3",
      "p": 0.0076,
      "n": 0
    },
    {
      "uci": "b5e5",
      "san": "Qe5",
      "p": 0.0076,
      "n": 0
    },
    {
      "uci": "g2g3",
      "san": "g3",
      "p": 0.0074,
      "n": 0
    }
  ],
  "prior_top1_uci": "b5c5",
  "searched_best_uci": "b5c5",
  "searched_eval_cp": -1616,
  "played_eval_cp": -1669,
  "prior_rank_of_searched_best": 1,
  "prior_p_of_searched_best": 0.2783,
  "prior_rank_of_played": 1,
  "prior_p_of_played": 0.2783
}

--- Sample Record #3 ---
{
  "game_site": "https://lichess.org/gbAHcwbT",
  "ply": 17,
  "fen": "r1bk1b1r/ppp2ppp/5n2/8/4Pp2/2N5/PPP3PP/R1B1KB1R w KQ - 0 9",
  "user_color": "white",
  "played_uci": "c1f4",
  "played_san": "Bxf4",
  "prior": [
    {
      "uci": "c1f4",
      "san": "Bxf4",
      "p": 0.5696,
      "n": 0
    },
    {
      "uci": "e4e5",
      "san": "e5",
      "p": 0.2104,
      "n": 0
    },
    {
      "uci": "f1c4",
      "san": "Bc4",
      "p": 0.0125,
      "n": 0
    },
    {
      "uci": "c1d2",
      "san": "Bd2",
      "p": 0.0111,
      "n": 0
    },
    {
      "uci": "f1e2",
      "san": "Be2",
      "p": 0.0092,
      "n": 0
    },
    {
      "uci": "f1d3",
      "san": "Bd3",
      "p": 0.0089,
      "n": 0
    },
    {
      "uci": "f1b5",
      "san": "Bb5",
      "p": 0.0081,
      "n": 0
    },
    {
      "uci": "h2h4",
      "san": "h4",
      "p": 0.008,
      "n": 0
    },
    {
      "uci": "c3e2",
      "san": "Ne2",
      "p": 0.0079,
      "n": 0
    },
    {
      "uci": "a2a3",
      "san": "a3",
      "p": 0.0079,
      "n": 0
    }
  ],
  "prior_top1_uci": "c1f4",
  "searched_best_uci": "c1f4",
  "searched_eval_cp": 115,
  "played_eval_cp": 119,
  "prior_rank_of_searched_best": 1,
  "prior_p_of_searched_best": 0.5696,
  "prior_rank_of_played": 1,
  "prior_p_of_played": 0.5696
}

--- Sample Record #4 ---
{
  "game_site": "https://lichess.org/awsWYWKk",
  "ply": 73,
  "fen": "5q2/3b1N2/pkn1pQ2/1p1p4/3P1p2/2PB4/PP3P1P/6K1 w - - 4 37",
  "user_color": "white",
  "played_uci": "f6f4",
  "played_san": "Qxf4",
  "prior": [
    {
      "uci": "f7e5",
      "san": "Ne5",
      "p": 0.2717,
      "n": 0
    },
    {
      "uci": "h2h4",
      "san": "h4",
      "p": 0.2159,
      "n": 0
    },
    {
      "uci": "d3g6",
      "san": "Bg6",
      "p": 0.2113,
      "n": 0
    },
    {
      "uci": "g1g2",
      "san": "Kg2",
      "p": 0.0432,
      "n": 0
    },
    {
      "uci": "d3e2",
      "san": "Be2",
      "p": 0.03,
      "n": 0
    },
    {
      "uci": "g1f1",
      "san": "Kf1",
      "p": 0.0186,
      "n": 0
    },
    {
      "uci": "f6f4",
      "san": "Qxf4",
      "p": 0.0181,
      "n": 0
    },
    {
      "uci": "h2h3",
      "san": "h3",
      "p": 0.0151,
      "n": 0
    },
    {
      "uci": "a2a3",
      "san": "a3",
      "p": 0.0147,
      "n": 0
    },
    {
      "uci": "d3h7",
      "san": "Bh7",
      "p": 0.0115,
      "n": 0
    }
  ],
  "prior_top1_uci": "f7e5",
  "searched_best_uci": "h2h4",
  "searched_eval_cp": 1223,
  "played_eval_cp": -122,
  "prior_rank_of_searched_best": 2,
  "prior_p_of_searched_best": 0.2159,
  "prior_rank_of_played": 7,
  "prior_p_of_played": 0.0181
}

--- Sample Record #5 ---
{
  "game_site": "https://lichess.org/bszg0DaG",
  "ply": 32,
  "fen": "r3k2r/pp3ppp/3b1B2/3p4/8/1P3B2/q1P2P1P/3QK2R b Kkq - 0 16",
  "user_color": "black",
  "played_uci": "g7f6",
  "played_san": "gxf6",
  "prior": [
    {
      "uci": "g7f6",
      "san": "gxf6",
      "p": 0.5312,
      "n": 0
    },
    {
      "uci": "a2a5",
      "san": "Qa5+",
      "p": 0.1492,
      "n": 0
    },
    {
      "uci": "d6b4",
      "san": "Bb4+",
      "p": 0.0593,
      "n": 0
    },
    {
      "uci": "a2a6",
      "san": "Qa6",
      "p": 0.0245,
      "n": 0
    },
    {
      "uci": "e8h8",
      "san": "O-O",
      "p": 0.0235,
      "n": 0
    },
    {
      "uci": "a8c8",
      "san": "Rc8",
      "p": 0.0138,
      "n": 0
    },
    {
      "uci": "e8f8",
      "san": "Kf8",
      "p": 0.0088,
      "n": 0
    },
    {
      "uci": "a2a3",
      "san": "Qa3",
      "p": 0.0066,
      "n": 0
    },
    {
      "uci": "a7a6",
      "san": "a6",
      "p": 0.0065,
      "n": 0
    },
    {
      "uci": "d6a3",
      "san": "Ba3",
      "p": 0.0065,
      "n": 0
    }
  ],
  "prior_top1_uci": "g7f6",
  "searched_best_uci": "g7f6",
  "searched_eval_cp": 4692,
  "played_eval_cp": 3010,
  "prior_rank_of_searched_best": 1,
  "prior_p_of_searched_best": 0.5312,
  "prior_rank_of_played": 1,
  "prior_p_of_played": 0.5312
}
================================================================================
```

---

### Checkpoint 5: ONNX vs LC0 Engine Policy Cross-Check (20 Positions)

Command: `python backend/training/policy_prior_harvest.py cross_check --n 20`

```text
Running ONNX evaluate_batch on 20 positions...
Starting engine for BT3 prior extraction on 20 positions...

================================================================================
           CHECKPOINT 5: ONNX VS LC0 ENGINE POLICY CROSS-CHECK                  
================================================================================
[01] FEN: 2r2rk1/pp2qpp1/5np1/3N4/3N3P/1Q2PPb1/PP1B2P1/1K1R4 b - - 0 20
     LC0 Prior Top-3 : f6d5:0.629, e7e5:0.025, e7d7:0.017
     ONNX Prior Top-3: g8h7:0.057, f6h7:0.053, g8h8:0.042 | value: -1.000 | wdl: [5.590344517258927e-05, 6.147198291728273e-05, 0.9998825788497925]
     Top-1 Match     : NO (LC0=f6d5, ONNX=g8h7)

[02] FEN: r1b1k1nr/p1pp1ppp/1Bp2q2/8/4P3/2N5/PPP2PPP/R2QKB1R b KQkq - 0 8
     LC0 Prior Top-3 : a7b6:0.713, c7b6:0.017, a7a5:0.009
     ONNX Prior Top-3: e8e7:0.053, f6e7:0.050, g8e7:0.049 | value: -1.000 | wdl: [0.0001021364369080402, 8.44134992803447e-05, 0.9998134970664978]
     Top-1 Match     : NO (LC0=a7b6, ONNX=e8e7)

[03] FEN: 4r1k1/p1pq1ppp/2n5/2Pp4/5B2/P2Q1N1P/5PP1/6K1 b - - 2 24
     LC0 Prior Top-3 : h7h6:0.139, d5d4:0.123, f7f6:0.091
     ONNX Prior Top-3: g8f8:0.086, e8f8:0.067, e8e7:0.065 | value: -1.000 | wdl: [6.419740384444594e-05, 8.408753637922928e-05, 0.9998517036437988]
     Top-1 Match     : NO (LC0=h7h6, ONNX=g8f8)

[04] FEN: 2kr3r/ppp1bp1p/2nq1p2/1Q6/3p4/1BP2P1P/P2N1P2/2KR3R w - - 0 16
     LC0 Prior Top-3 : b5f5:0.324, c1b1:0.155, d2c4:0.062
     ONNX Prior Top-3: c1c2:0.052, b3c2:0.050, c1b2:0.043 | value: -1.000 | wdl: [8.216308197006583e-05, 8.502999116899446e-05, 0.9998327493667603]
     Top-1 Match     : NO (LC0=b5f5, ONNX=c1c2)

[05] FEN: 1r3rk1/ppp1qpp1/5bnp/8/2B1N3/1Q5P/PPP3P1/3R1R1K w - - 0 21
     LC0 Prior Top-3 : e4f6:0.608, d1e1:0.042, f1f6:0.015
     ONNX Prior Top-3: h1h2:0.059, h1g1:0.047, f1g1:0.039 | value: -1.000 | wdl: [1.6990226868074387e-05, 2.809382749546785e-05, 0.9999549388885498]
     Top-1 Match     : NO (LC0=e4f6, ONNX=h1h2)

[06] FEN: r2q1rk1/bppb1pp1/2np1n1p/p3p3/P1B1P3/2PPBN1P/1PQN1PP1/R4RK1 b - - 0 11
     LC0 Prior Top-3 : a7e3:0.226, d7e6:0.114, f6h5:0.109
     ONNX Prior Top-3: f8e8:0.039, f6e8:0.038, g8h8:0.038 | value: -1.000 | wdl: [0.00011539612023625523, 8.31580109661445e-05, 0.9998014569282532]
     Top-1 Match     : NO (LC0=a7e3, ONNX=f8e8)

[07] FEN: 8/p3kp1Q/3qp3/3nN3/n2P4/r7/P4PPP/R4RK1 b - - 2 26
     LC0 Prior Top-3 : a4b6:0.122, a3c3:0.103, a4c3:0.098
     ONNX Prior Top-3: e7f6:0.381, d5f6:0.225, d6e5:0.034 | value: -1.000 | wdl: [2.0954516912752297e-06, 3.193024167558178e-05, 0.999966025352478]
     Top-1 Match     : NO (LC0=a4b6, ONNX=e7f6)

[08] FEN: r1b1kr2/1pp1pq1p/p1n3p1/1Q6/3Pp3/1P6/P1P1PPPP/2KR1B1R w q - 0 15
     LC0 Prior Top-3 : b5c5:0.278, b5g5:0.195, b5a4:0.147
     ONNX Prior Top-3: c1b2:0.225, c1d2:0.118, d1d2:0.088 | value: -1.000 | wdl: [7.463966539944522e-06, 3.249727524234913e-05, 0.9999600648880005]
     Top-1 Match     : NO (LC0=b5c5, ONNX=c1b2)

[09] FEN: r1bqkb1r/pp3ppp/2n1pn2/8/2Q5/2N1PN2/PP2BPPP/R1B1K2R b KQkq - 2 8
     LC0 Prior Top-3 : f8e7:0.258, c8d7:0.150, a7a6:0.144
     ONNX Prior Top-3: f8e7:0.036, d8e7:0.035, d8d6:0.035 | value: -0.999 | wdl: [0.00019781517039518803, 0.00013422963093034923, 0.9996680021286011]
     Top-1 Match     : YES

[10] FEN: 1r1q1r2/p3p1bk/2p3pp/3p1p2/N2Pn2B/1P2PQ1P/P4PP1/R2R2K1 w - - 0 17
     LC0 Prior Top-3 : a1c1:0.478, h4g3:0.224, f3e2:0.116
     ONNX Prior Top-3: g1f1:0.089, g1h2:0.087, d1f1:0.078 | value: -1.000 | wdl: [2.4824897991493344e-05, 4.667305984185077e-05, 0.9999284744262695]
     Top-1 Match     : NO (LC0=a1c1, ONNX=g1f1)

[11] FEN: 2r2rk1/pp3pb1/2n3pp/3B4/4P3/2P4N/PP5B/2K4R w - - 2 22
     LC0 Prior Top-3 : h3f4:0.200, h1f1:0.097, h3f2:0.068
     ONNX Prior Top-3: c1d2:0.100, c1d1:0.091, c1c2:0.087 | value: -1.000 | wdl: [0.00010510851279832423, 8.426237036474049e-05, 0.9998106360435486]
     Top-1 Match     : NO (LC0=h3f4, ONNX=c1d2)

[12] FEN: r1bq1rk1/1p2ppbp/p1np2p1/8/P1N1P1n1/4BN2/1PP1BPPP/R2Q1RK1 w - - 4 14
     LC0 Prior Top-3 : e3b6:0.644, e3g5:0.020, e3c1:0.013
     ONNX Prior Top-3: g1h1:0.034, f1e1:0.032, f3e1:0.032 | value: -0.999 | wdl: [0.00019907385285478085, 0.00012833184155169874, 0.9996726512908936]
     Top-1 Match     : NO (LC0=e3b6, ONNX=g1h1)

[13] FEN: r1bqk1nr/ppp2ppp/5b2/4p3/2BpPP2/2P5/PP4PP/RNBQ1RK1 w kq - 1 9
     LC0 Prior Top-3 : f4e5:0.598, c4f7:0.088, d1b3:0.063
     ONNX Prior Top-3: c1d2:0.036, g1f2:0.036, f1f2:0.034 | value: -0.999 | wdl: [0.0005289991968311369, 0.0002864717389456928, 0.9991845488548279]
     Top-1 Match     : NO (LC0=f4e5, ONNX=c1d2)

[14] FEN: 5r1r/pp2k2p/2p1b1q1/3n1ppR/2pP2P1/2N1PQ2/PPBK1P2/R7 w - - 3 22
     LC0 Prior Top-3 : f3g3:0.238, a1h1:0.210, c3d5:0.181
     ONNX Prior Top-3: c3d1:0.038, c2d1:0.036, a1d1:0.036 | value: -0.999 | wdl: [0.00018246188119519502, 0.0001527124986751005, 0.9996647834777832]
     Top-1 Match     : NO (LC0=f3g3, ONNX=c3d1)

[15] FEN: 3r4/1p6/1p3k1p/2b5/P7/2P1NP2/1PB5/1K4R1 w - - 1 37
     LC0 Prior Top-3 : g1g6:0.304, e3g4:0.245, g1e1:0.180
     ONNX Prior Top-3: b1c1:0.092, g1c1:0.081, b2b3:0.078 | value: -0.982 | wdl: [0.006245152559131384, 0.0056130122393369675, 0.9881418347358704]
     Top-1 Match     : NO (LC0=g1g6, ONNX=b1c1)

[16] FEN: 2r1r1k1/5pp1/1p3qn1/pP1p4/P2Pp2p/1N2P2P/5PP1/2RQ1RK1 b - - 3 23
     LC0 Prior Top-3 : f6d6:0.240, c8c1:0.124, g6e7:0.121
     ONNX Prior Top-3: e8e7:0.054, g6e7:0.053, f6e7:0.052 | value: -1.000 | wdl: [3.39393263857346e-05, 4.575349157676101e-05, 0.9999202489852905]
     Top-1 Match     : NO (LC0=f6d6, ONNX=e8e7)

[17] FEN: r3r1k1/pp1R1pp1/2p4p/4qB2/8/4nPP1/PP3P2/1QR3K1 w - - 2 23
     LC0 Prior Top-3 : f5h7:0.538, f5e4:0.155, f5d3:0.050
     ONNX Prior Top-3: c1e1:0.111, g1h1:0.111, d7d2:0.044 | value: -1.000 | wdl: [1.643589826016978e-06, 1.5038915080367588e-05, 0.9999833106994629]
     Top-1 Match     : NO (LC0=f5h7, ONNX=c1e1)

[18] FEN: r1b1kb1r/pp3ppp/1q3n2/3pN3/3P4/1P6/P1P1BPPP/RN1QK2R b KQkq - 0 9
     LC0 Prior Top-3 : f8d6:0.357, f8b4:0.131, g7g6:0.096
     ONNX Prior Top-3: e8d8:0.038, f8e7:0.038, e8e7:0.038 | value: -1.000 | wdl: [0.0001669016492087394, 9.927392238751054e-05, 0.9997338652610779]
     Top-1 Match     : NO (LC0=f8d6, ONNX=e8d8)

[19] FEN: r5k1/1p3ppp/1Pb5/8/p7/5P2/6PP/R5K1 b - - 0 35
     LC0 Prior Top-3 : a4a3:0.107, f7f5:0.072, g7g5:0.060
     ONNX Prior Top-3: g8f8:0.066, g7g6:0.062, f7f6:0.061 | value: -0.998 | wdl: [0.0006988532259128988, 0.0002428323932690546, 0.9990583062171936]
     Top-1 Match     : NO (LC0=a4a3, ONNX=g8f8)

[20] FEN: r3k2r/pppq1npR/4p3/4P1p1/1b1p2P1/2NQ1PB1/PPP1P3/R3KB2 w Qkq - 0 15
     LC0 Prior Top-3 : h7h8:0.453, e1a1:0.174, a2a3:0.074
     ONNX Prior Top-3: e1f2:0.063, g3f2:0.052, f1g2:0.037 | value: -1.000 | wdl: [0.00013776512059848756, 0.00014161746366880834, 0.9997206330299377]
     Top-1 Match     : NO (LC0=h7h8, ONNX=e1f2)

--------------------------------------------------------------------------------
Top-1 Agreement: 1/20 (5.0%)
Extreme WDL / Flat Policy Anomalies (wdl in [[0,0,1],[1,0,0]] or max_p < 0.05): 6
  - Pos #6: FEN=r2q1rk1/bppb1pp1/2np1n1p/p3p3/P1B1P3/2PPBN1P/1PQN1PP1/R4RK1 b - - 0 11 | wdl=[0.00011539612023625523, 8.31580109661445e-05, 0.9998014569282532] | val=-0.9996860608080169 | max_p=0.0394
  - Pos #9: FEN=r1bqkb1r/pp3ppp/2n1pn2/8/2Q5/2N1PN2/PP2BPPP/R1B1K2R b KQkq - 2 8 | wdl=[0.00019781517039518803, 0.00013422963093034923, 0.9996680021286011] | val=-0.9994701869582059 | max_p=0.0364
  - Pos #12: FEN=r1bq1rk1/1p2ppbp/p1np2p1/8/P1N1P1n1/4BN2/1PP1BPPP/R2Q1RK1 w - - 4 14 | wdl=[0.00019907385285478085, 0.00012833184155169874, 0.9996726512908936] | val=-0.9994735774380388 | max_p=0.0338
  - Pos #13: FEN=r1bqk1nr/ppp2ppp/5b2/4p3/2BpPP2/2P5/PP4PP/RNBQ1RK1 w kq - 1 9 | wdl=[0.0005289991968311369, 0.0002864717389456928, 0.9991845488548279] | val=-0.9986555496579967 | max_p=0.0360
  - Pos #14: FEN=5r1r/pp2k2p/2p1b1q1/3n1ppR/2pP2P1/2N1PQ2/PPBK1P2/R7 w - - 3 22 | wdl=[0.00018246188119519502, 0.0001527124986751005, 0.9996647834777832] | val=-0.999482321596588 | max_p=0.0379
  - Pos #18: FEN=r1b1kb1r/pp3ppp/1q3n2/3pN3/3P4/1P6/P1P1BPPP/RN1QK2R b KQkq - 0 9 | wdl=[0.0001669016492087394, 9.927392238751054e-05, 0.9997338652610779] | val=-0.9995669636118691 | max_p=0.0381
================================================================================
```
