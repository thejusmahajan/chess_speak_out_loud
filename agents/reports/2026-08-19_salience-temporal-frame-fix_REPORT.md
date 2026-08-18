# Report: Salience Temporal Frame Fix

**Brief-ID:** `2026-08-19_salience-temporal-frame-fix`  
**Date:** 2026-08-19  
**Author:** Antigravity Worker (Gemini 3.7 Flash)  
**Target:** `chess_speak_out_loud`  
**Status:** DELIVERED (for Leader Audit)

---

## 1. Gate Execution & Real Terminal Outputs

### Gate 1: Baseline Witness and No-Line Capture (Before Change)

#### Execution Command
```bash
C:\Users\Admin\miniconda3\envs\cszero\python.exe -c "
import chess
from backend.training.salience_matcher import rank_salient_facts
fen='r1b2rk1/pp1nqppp/2pbpn2/8/2BP4/2N1PN2/PP2QPPP/R1B2RK1 w - - 0 11'
b=chess.Board(fen)
print('=== Witness with line_ucis ===')
print('d3:', b.piece_at(chess.D3), ' c4:', b.piece_at(chess.C4), ' e4:', b.piece_at(chess.E4))
for f in rank_salient_facts(fen, chess.WHITE, line_ucis=['c4d3','f6g4','e2e4'], top_k=6):
    print(round(f['salience_score'],2), f['text'])
print('\n=== Baseline with line_ucis=None ===')
for f in rank_salient_facts(fen, chess.WHITE, line_ucis=None, top_k=6):
    print(round(f['salience_score'],2), f['text'])
"
```

#### Real Terminal Output (Before)
```
=== Witness with line_ucis ===
d3: None  c4: B  e4: None
0.91 P on e6 is pinned by e4 to Q on e7
0.56 White's c1 bishop is a bad bishop — 5 of its own pawns sit on its colour, restricting it (mobility 1)
0.55 Black's c8 bishop is a bad bishop — 5 of its own pawns sit on its colour, restricting it (mobility 0)
0.46 White's d3 bishop is active — unobstructed by its own pawns, controlling 9 squares
0.45 Black's d6 bishop is active — unobstructed by its own pawns, controlling 9 squares
0.21 Enemy king on g8 has 3 shield pawn(s) and 1 adjacent defender(s)

=== Baseline with line_ucis=None ===
0.56 White's c1 bishop is a bad bishop — 5 of its own pawns sit on its colour, restricting it (mobility 1)
0.55 Black's c8 bishop is a bad bishop — 5 of its own pawns sit on its colour, restricting it (mobility 0)
0.45 Black's d6 bishop is active — unobstructed by its own pawns, controlling 9 squares
0.21 Enemy king on g8 has 3 shield pawn(s) and 1 adjacent defender(s)
0.2 Enemy king on g1 has 3 shield pawn(s) and 1 adjacent defender(s)
```

---

### Gate 2: Full Backend Test Suite Before Change

#### Execution Command
```bash
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests -q
```

#### Real Terminal Output (Before)
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 295 items

........................................................................ [ 24%]
........................................................................ [ 48%]
........................................................................ [ 73%]
........................................................................ [ 97%]
.......                                                                  [100%]
=========== 290 passed, 5 skipped, 2 warnings in 144.86s (0:02:24) ============
```
*Baseline recorded: 290 passed, 5 skipped (295 collected).*

---

### Gate 4: Full Backend Test Suite After Change

#### Execution Command
```bash
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests -q
```

#### Real Terminal Output (After)
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 302 items

........................................................................ [ 23%]
........................................................................ [ 47%]
........................................................................ [ 71%]
........................................................................ [ 95%]
..............                                                           [100%]
=========== 297 passed, 5 skipped, 2 warnings in 101.46s (0:01:41) ============
```
*Exact match: 297 passed (+7 new tests), 5 skipped, 0 failures (302 collected).*

---

### Gate 5: Re-run Witness Command After Change

#### Execution Command
```bash
C:\Users\Admin\miniconda3\envs\cszero\python.exe -c "
import chess
from backend.training.salience_matcher import rank_salient_facts
fen='r1b2rk1/pp1nqppp/2pbpn2/8/2BP4/2N1PN2/PP2QPPP/R1B2RK1 w - - 0 11'
b=chess.Board(fen)
print('d3:', b.piece_at(chess.D3), ' c4:', b.piece_at(chess.C4), ' e4:', b.piece_at(chess.E4))
for f in rank_salient_facts(fen, chess.WHITE, line_ucis=['c4d3','f6g4','e2e4'], top_k=6):
    print(round(f['salience_score'],2), f['text'])
"
```

#### Real Terminal Output (After)
```
d3: None  c4: B  e4: None
0.91 After Bd3 Ng4 Qe4: P on e6 is pinned by e4 to Q on e7
0.56 White's c1 bishop is a bad bishop — 5 of its own pawns sit on its colour, restricting it (mobility 1)
0.55 Black's c8 bishop is a bad bishop — 5 of its own pawns sit on its colour, restricting it (mobility 0)
0.46 After Bd3: White's d3 bishop is active — unobstructed by its own pawns, controlling 9 squares
0.46 No longer true after Bd3 Ng4 Qe4: White's d3 bishop is active — unobstructed by its own pawns, controlling 9 squares
0.45 Black's d6 bishop is active — unobstructed by its own pawns, controlling 9 squares
```

---

## 2. Test 5: Real Position vs. Synthetic Substitute

**Test 5 used a REAL position.**

- **Position & Line:**
  - FEN: `3r2k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1`
  - Line UCIs: `["d1e1", "g8f8", "e1d1"]`
- **Why it exercises the dedup collision on real boards:**
  1. Statically on move 0, White's rook stands on the open d-file (`delta_role == "static"`, `text_raw == "White's rook on the open d-file"`).
  2. At move 0 (`d1e1`), the rook moves to e-file, which removes control of d-file (`delta_role == "removed"`).
  3. At move 2 (`e1d1`), the rook returns to d-file, which creates control of d-file anew (`delta_role == "created"`, `delta_move == "e1d1"`, `delta_ply == 2`).
- **Outcome:**  
  Under the old dedup key `(kind, text)`, the created instance was dropped because the static fact had registered first. Under the new dedup key `(kind, text_raw, delta_role, delta_move)`, both `"static"` and `"created"` survive and are returned by `rank_salient_facts`.

---

## 3. Findings, Edge Cases & Realities Encountered

1. **`top_k` Truncation in Test 4:**
   - In Test 4 (FEN `8/2r1b3/1pk5/6P1/5q2/3R4/Q1P1K3/8 w - - 5 38` with move `["a2d5"]`), the removed fact `"White's queen on the open a-file"` has a lower inference prior (`0.45` / `0.46`) than high-priority tactical/weakness facts (protected passer on g5, isolated pawns, color complexes).
   - Calling `rank_salient_facts` with default `top_k=3` or `top_k=10` naturally truncated the fact. Querying with `top_k=20` returns all 18 extracted facts, correctly verifying that the removed fact is marked with `delta_role == "removed"` and `text == "No longer true after Qd5#: White's queen on the open a-file"`.
2. **SAN Prefix Construction:**
   - As observed in §1 of the brief, move `e2e4` from the witness FEN is a queen move (`Qe4`), and `a2d5` in Test 4 is checkmate (`Qd5#`). Pushing moves sequentially on a `chess.Board(fen)` instance derived SAN prefixes with check/mate annotations naturally, with zero hand-formatting.

---

## 4. Explicit List of What Was NOT Done

Per §6 of the brief and project doctrine (`LEADER_BIBLE.md` §4, §6):
1. **No scoring weights were touched:** `INFERENCE_PRIORS` was not modified in any way.
2. **No dynamic score bonus was added:** Created and removed facts receive the exact same score from `_inference_prior` as static facts of the same kind.
3. **No files outside declared scope were created or modified:**
   - `backend/training/relational_facts.py` was NOT touched.
   - `backend/training/metrics.py` was NOT touched.
   - `backend/training/salience_dataset.py`, `salience_lexicon.json`, and `provenance_check.py` were NOT touched.
   - Only `backend/training/salience_matcher.py` and `backend/tests/test_salience_pipeline.py` were modified.
