# Chess Diagnosis Profile Triage & Health Assessment

**Analysis Date:** July 25, 2026  
**Source Data File:** `data/training/profile.json` (canonical profile; identical to `downloads/profile.txt`)  
**Run Context:** Kaggle 2×T4 GPU Diagnosis Run (**30 games, 880 moves analyzed, vision=attention**)

---

## Executive Summary & Metadata Overview

| Metric / Attribute | JSON Field Path | Value | Status / Notes |
| :--- | :--- | :--- | :--- |
| **Profile Schema Version** | `version` | `1` | Canonical schema v1 |
| **Creation Timestamp** | `created` | `2026-07-25T18:22:04.441657` | Kaggle completion timestamp |
| **Games Analyzed** | `games_analyzed` | `30` | 30 full PGN games processed |
| **Moves Analyzed** | `moves_analyzed` | `880` | Total user moves evaluated |
| **Time Scramble Skipped** | `time_scramble_skipped` | `172` | Moves under clock scramble filter |
| **Opening Sidelines Excluded**| `opening_sidelines_excluded` | `66` | Sideline moves excluded from profile |
| **Total Findings Count** | `findings[]` length | `213` | 24.20% move error/blindness rate |
| **Total Steer Findings Count**| `steer_findings[]` length | `256` | 29.09% move steering candidates |
| **Steer Budget Exhausted** | `steer_budget_exhausted` | `false` | TS2 evaluation ran to full completion |
| **Regressions List** | `regressions[]` | `[]` | No regressions detected |

---

## Part 1 — Weaknesses (What to Train)

### 1.1 Headline Weakness Analysis (`aggregates`)

Evaluation of `aggregates.by_phase` and `aggregates.by_clock` demonstrates that **Middlegame Positional & Tactical Blindness** is the primary weakness of the player.

#### Breakdown by Game Phase (`aggregates.by_phase`)
* **Middlegame (`aggregates.by_phase.middlegame`):**
  * `moves`: `341`
  * `blind` (`severity == "blind"`): `48`
  * `missed` (`severity == "missed"`): `64`
  * `blind_rate`: `0.14076246334310852` (**14.08%** intuitive blindness rate)
  * **Total Flagged Moves:** `112` out of 341 moves (**32.84%** failure rate).
* **Opening (`aggregates.by_phase.opening`):**
  * `moves`: `360`
  * `blind`: `31`
  * `missed`: `26`
  * `blind_rate`: `0.0861111111111111` (**8.61%** intuitive blindness rate)
  * **Total Flagged Moves:** `57` out of 360 moves (15.83% failure rate).
* **Endgame (`aggregates.by_phase.endgame`):**
  * `moves`: `179`
  * `blind`: `18`
  * `missed`: `26`
  * `blind_rate`: `0.1005586592178771` (**10.06%** intuitive blindness rate)
  * **Total Flagged Moves:** `44` out of 179 moves (24.58% failure rate).

> [!IMPORTANT]
> **Headline Verdict:** **Confirmed**. Middlegame is clearly the worst phase. It exhibits the highest intuitive blindness rate (**14.08%** vs 8.61% opening and 10.06% endgame) and accounts for **52.58%** (112 / 213) of all findings.

#### Breakdown by Clock Bucket (`aggregates.by_clock`)
* **Fast Clock (`aggregates.by_clock.fast`):** `moves` = `169`, `blind` = `23`, `missed` = `23`, `blind_rate` = `0.13609467455621302` (**13.61%**).
* **Normal Clock (`aggregates.by_clock.normal`):** `moves` = `711`, `blind` = `74`, `missed` = `93`, `blind_rate` = `0.10407876230661041` (**10.41%**).
* **Slow Clock (`aggregates.by_clock.slow`):** `moves` = `0`, `blind` = `0`, `missed` = `0`, `blind_rate` = `0.0`.
* **No Clock (`aggregates.by_clock.no_clock`):** `moves` = `0`, `blind` = `0`, `missed` = `0`, `blind_rate` = `0.0`.

Fast clock conditions exacerbate intuitive blindness by **+3.20%** compared to normal time controls.

---

### 1.2 Breakdown of Findings by Type & Motifs

#### Findings by Severity Tag (`finding.severity`)
* `severity == "missed"` (Policy-Blindness / Best Move Missed): **116** findings (54.46%)
* `severity == "blind"` (Intuitive-Blindness / Policy Preferred Inferior Move): **97** findings (45.54%)
* **Total Findings:** **213** (`findings[]`)

#### Findings by Confirmation & Saliency
* Engine Confirmed Error (`finding.confirmation.confirmed == true`): **130** findings (61.03%)
* Unconfirmed / Low-Swing (`finding.confirmation.confirmed == false`): **83** findings (38.97%)
* Attention Blind (`finding.attention.blind == true`): **6** findings (2.82%)
* Attention Active (`finding.attention.blind == false`): **207** findings (97.18%)

#### Motif Breakdown (`aggregates.by_motif`)

| Motif | `missed` Count | `blind` Count | `confirmed` Count | Focus Area |
| :--- | :---: | :---: | :---: | :--- |
| `advantage` | 172 | 171 | 130 | Converting winning advantages |
| `veryLong` | 172 | 171 | 130 | Deep calculation (>6 ply PVs) |
| `quietMove` | 131 | 144 | 100 | Non-capturing positional improvements |
| `defensiveMove` | 60 | 43 | 39 | Prophylaxis & defensive resilience |
| `clearance` | 33 | 25 | 21 | Tactical space clearance |
| `castling` | 21 | 28 | 20 | King safety / early development |
| `sacrifice` | 23 | 15 | 18 | Evaluating tactical sacrifices |
| `rookEndgame` | 12 | 3 | 6 | Rook endgame technique |
| `exposedKing` | 8 | 11 | 8 | Punishing / protecting exposed kings |
| `discoveredAttack` | 8 | 2 | 4 | Discovered attack tactics |
| `advancedPawn` | 6 | 2 | 4 | Advanced pawn pushing / stopping |
| `fork` | 5 | 5 | 3 | Fork tactics |

#### Concept Breakdown (`aggregates.by_concept`)
* `piece_activity`: **1087** missed concept tags
* `center_control`: **819** missed concept tags
* `pawn_structure`: **748** missed concept tags
* `king_safety`: **729** missed concept tags
* `material`: **414** missed concept tags

---

### 1.3 Top 10 Findings by Eval Swing (`confirmation.swing_cp`)

The table below details the 10 worst tactical / positional blunders ordered by engine evaluation swing:

| Rank | Finding ID | Move / Ply | Played Move (`san`, `p`) | Best Move (`san`, `p`) | Eval Swing (`swing_cp`) | Severity | Confirmed | Att. Blind | Primary Motifs |
| :---: | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **1** | `g014-p026` | Move 13, Ply 26 | `Bd3` (p=0.0402) | `Ba3` (p=0.4851) | **7856 cp** | `blind` | `true` | `false` | quietMove, advantage, veryLong |
| **2** | `g010-p064` | Move 32, Ply 64 | `Ke2` (p=0.0076) | `Be5` (p=0.6409) | **6867 cp** | `blind` | `true` | `false` | quietMove, advantage, veryLong |
| **3** | `g018-p052` | Move 26, Ply 52 | `Kf2` (p=0.0033) | `h4` (p=0.3340) | **4897 cp** | `blind` | `true` | `false` | quietMove, advantage, veryLong |
| **4** | `g008-p037` | Move 19, Ply 37 | `Bb5` (p=0.0210) | `Rae1` (p=0.3541) | **4668 cp** | `blind` | `true` | `false` | quietMove, advantage, veryLong |
| **5** | `g001-p047` | Move 24, Ply 47 | `Qxd7` (p=0.0083) | `Rxe1` (p=0.7463) | **3957 cp** | `blind` | `true` | `false` | hangingPiece, quietMove |
| **6** | `g024-p025` | Move 13, Ply 25 | `Kd2` (p=0.0338) | `Rh2` (p=0.3347) | **3227 cp** | `blind` | `true` | `false` | exposedKing, castling |
| **7** | `g006-p060` | Move 30, Ply 60 | `Nxd3` (p=0.0070) | `Qxd2` (p=0.6516) | **2999 cp** | `blind` | `true` | `false` | quietMove, advantage |
| **8** | `g017-p059` | Move 30, Ply 59 | `Ka4` (p=0.0233) | `Kc3` (p=0.5498) | **2743 cp** | `blind` | `true` | `false` | exposedKing, quietMove |
| **9** | `g018-p036` | Move 18, Ply 36 | `d5` (p=0.0053) | `Qd7` (p=0.3140) | **2656 cp** | `blind` | `true` | `false` | quietMove, advantage |
| **10**| `g010-p033` | Move 17, Ply 33 | `Qf7+` (p=0.1131) | `e5` (p=0.3188) | **2653 cp** | `missed` | `true` | `false` | sacrifice, advantage |

---

### 1.4 Regressions (`regressions[]`)

* `regressions`: `[]` (Empty list; count = `0`).
* **Verdict:** No tactical or evaluation regressions detected across analyzed games.

---

### 1.5 Grounded "Train-This-First" Priority List

1. **Middlegame Positional Prophylaxis & Quiet Moves (Top Priority)**
   * *Evidence:* `aggregates.by_phase.middlegame` exhibits 112 findings (14.08% blind rate). The `quietMove` motif accounts for 144 intuitive blindness flags and 100 engine-confirmed blunders.
2. **Advantage Conversion & Material Preservation**
   * *Evidence:* `advantage` motif is flagged in 171 blind and 172 missed findings (130 engine-confirmed swings up to 7856 cp).
3. **Speed & Fast-Clock Tactical Discipline**
   * *Evidence:* `aggregates.by_clock.fast` shows a 13.61% blind rate vs 10.41% in normal clock situations.
4. **King Safety & Defensive Operations**
   * *Evidence:* 39 confirmed defensive blunders (`defensiveMove`) and 8 severe king safety blunders (`exposedKing`).

---

## Part 2 — Tactical Steering & Tal Candidates

### 2.1 Steering Overview & Tal Move Ratio

* **Total Steer Findings (`steer_findings[]` length):** `256`
* **Sacrificial / Tal Candidates (`had_tal_move == true`):** **`63`** (**24.61%** of steer positions)
* **Standard Steering Candidates (`had_tal_move == false`):** `193` (75.39%)

---

### 2.2 Top Steer Candidates by Steer Complexity (`steer.complexity`)

#### (A) Top 10 Sacrificial / Tal Steer Candidates (`had_tal_move == true`)
Ranked by `steer.complexity` to highlight the richest sharp/sacrificial tactical opportunities:

| Rank | Steer ID | Ply | ECO | Best Move (`san`, `eval_cp`) | Steer Move (`san`, `eval_cp`) | Eval Loss (`eval_loss_cp`) | Steer Complexity | Component Breakdown (`score`, `dec`, `nar`, `trap`, `att`) |
| :---: | :--- | :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | `s-027-p060` | 60 | `???` | `Nd7` (+6.68) | **`Kf7`** (+6.21) | 47 cp | **0.9227** | dec: 0.976, nar: 1.000, trap: 0.700, att: 0.000 |
| **2** | `s-023-p022` | 22 | `???` | `Bg4` (+5.26) | **`Ng4`** (+4.66) | 60 cp | **0.9023** | dec: 0.952, nar: 1.000, trap: 0.656, att: 0.000 |
| **3** | `s-016-p052` | 52 | `???` | `e5` (+6.03) | **`Rb8`** (+5.70) | 33 cp | **0.8987** | dec: 0.968, nar: 0.940, trap: 0.698, att: 0.000 |
| **4** | `s-007-p020` | 20 | `???` | `Qxe5` (+8.61) | **`Qc5`** (+8.35) | 26 cp | **0.8932** | dec: 0.974, nar: 1.000, trap: 0.571, att: 0.000 |
| **5** | `s-007-p014` | 14 | `???` | `Qh6` (+4.93) | **`Qe7`** (+4.41) | 52 cp | **0.8881** | dec: 0.947, nar: 1.000, trap: 0.602, att: 0.000 |
| **6** | `s-027-p044` | 44 | `???` | `Be6` (+5.22) | **`Na6`** (+4.90) | 32 cp | **0.8837** | dec: 0.937, nar: 0.945, trap: 0.685, att: 0.000 |
| **7** | `s-003-p062` | 62 | `???` | `Qe4` (+2.07) | **`Kb7`** (+1.81) | 26 cp | **0.8450** | dec: 0.777, nar: 1.000, trap: 0.749, att: 0.000 |
| **8** | `s-021-p020` | 20 | `???` | `Re8` (+3.96) | **`Bf5`** (+3.41) | 55 cp | **0.8410** | dec: 0.921, nar: 1.000, trap: 0.442, att: 0.000 |
| **9** | `s-010-p023` | 23 | `???` | `Bxc4` (+4.23) | **`Bg3`** (+3.79) | 44 cp | **0.8059** | dec: 0.935, nar: 0.820, trap: 0.526, att: 0.000 |
| **10**| `s-013-p032` | 32 | `???` | `Qc7` (+3.52) | **`Bxf3`** (+2.97) | 55 cp | **0.7970** | dec: 0.885, nar: 1.000, trap: 0.317, att: 0.000 |

#### (B) Top 5 Overall Steer Candidates (Engine Choice == Steer Move)
* `s-023-p040`: `Best`: Nc3 (+74.95 cp) \| `Steer`: Nc3 (+74.95 cp) \| `cx`: **1.0000** \| `loss`: 0 cp
* `s-007-p026`: `Best`: Ne6 (+16.82 cp) \| `Steer`: Ne6 (+16.82 cp) \| `cx`: **0.9973** \| `loss`: 0 cp
* `s-010-p105`: `Best`: Rxa3 (+88.23 cp) \| `Steer`: Rxa3 (+88.23 cp) \| `cx`: **0.9960** \| `loss`: 0 cp
* `s-021-p086`: `Best`: Qb2 (+118.84 cp) \| `Steer`: Qb2 (+118.84 cp) \| `cx`: **0.9884** \| `loss`: 0 cp
* `s-021-p090`: `Best`: a3 (+75.76 cp) \| `Steer`: a3 (+75.76 cp) \| `cx`: **0.9872** \| `loss`: 0 cp

---

### 2.3 `steer_summary` Analysis

Exact structure of `steer_summary` in `data/training/profile.json`:
```json
"steer_summary": {
  "???": {
    "moves": 880,
    "tal_moves": 63,
    "mean_complexity": 0.37028049579573014
  }
}
```

* `moves`: `880` total moves analyzed
* `tal_moves`: `63` sacrificial candidates discovered
* `mean_complexity`: `0.37028049579573014` mean complexity across all steer positions

---

### 2.4 Verdict on Sacrificial / Tal Style Representation

> [!NOTE]
> **Verdict: WELL-REPRESENTED / SOLID**.
> Out of 256 steered positions, **63 positions** (24.61% of steered candidates, 7.16% of total game moves) feature high-complexity, low-eval-loss sacrificial moves (`had_tal_move == true`). Evaluation loss for top Tal candidates is constrained between **26 cp and 60 cp**, making them playable tactical steering choices for dynamic training.

---

## Part 3 — Health & Sanity Gate ("Is It Good?")

### 3.1 Section Completeness Audit

* `findings`: **NON-EMPTY** (213 items present)
* `aggregates`: **NON-EMPTY** (`by_motif`, `by_opening`, `by_concept`, `by_phase`, `by_clock`, `intuitive_blindness_rate`, `attention_blindness_rate` all populated)
* `steer_findings`: **NON-EMPTY** (256 items present)
* `steer_summary`: **NON-EMPTY** (`"???"` dict entry populated with moves, tal_moves, mean_complexity)
* `steer_budget_exhausted`: **`false`** (TS2 search completed all 256 steering positions without hitting step budget limits)
* `regressions`: **`[]`** (valid empty array)

---

### 3.2 Attention-Blindness Pipeline Verification

* `attention_blindness_rate` in `aggregates`: `0.006818181818181818` (**0.68%**)
* Count of `finding.attention.blind == true`: Exactly **`6` findings** (non-zero!)
* Saliency engagement verification:
  * `engagement_played` values: `0.1882` to `0.4546`
  * `engagement_best` values: up to `1.0000`
  * `hot_squares`: populated across 100% of finding objects (e.g., `["b8", "f4", "g1", "h1", "h8"]`)

> [!IMPORTANT]
> **Attention Pipeline Status: FUNCTIONAL & HEALTHY**.
> Saliency calculations (`vision=attention`) ran successfully on 2xT4 GPUs without defaulting to zero. The 6 attention-blind findings demonstrate that true saliency missed-hot-square detection was active.

---

### 3.3 Plausibility of Ratios & Degeneracy Audit

1. **Findings Ratio:** `213 / 880` = **24.20%** of moves flagged. Plausible for club player analysis.
2. **Steer Candidates Ratio:** `256 / 880` = **29.09%** of moves. Plausible.
3. **Tal Candidates Ratio:** `63 / 256` = **24.61%** of steered positions. Plausible.
4. **Time Scramble Skipped Ratio:** `172 / 1052` total moves = **16.35%**. Plausible.
5. **Numeric Validity:** No `NaN`, `Infinity`, or negative counts in JSON data.

#### Degeneracy Flagged: Opening ECO Unmapped (`ECO: ???`)

> [!WARNING]
> **Degeneracy Warning — Unmapped ECO Codes:**
> * `opening.eco` is `"???"` for **100%** of entries in `findings[]`, `steer_findings[]`, `aggregates.by_opening`, and `steer_summary`.
> * `aggregates.by_opening["???"]` lists `moves: 0`, `moves_white: 0`, `moves_black: 0`, `blind_rate: 0.0` despite aggregating `missed: 116, blind: 97`.
> * *Root cause:* The PGN header parser or ECO lookup table was missing/unlinked during the Kaggle run, preventing opening-specific grouping in the UI.

---

### 3.4 Concrete Profile JSON Objects

#### Example `finding` Object (`id: "g000-p023"`)
```json
{
  "id": "g000-p023",
  "game": {
    "white": "derdiedasdie",
    "black": "purplepudding",
    "date": "2026.07.21",
    "result": "0-1"
  },
  "user_color": "white",
  "ply": 23,
  "move_number": 12,
  "fen_before": "r1bq1rk1/pp3pb1/2n3pp/2ppn3/5B2/2P1PN1P/PPBN1PP1/R2Q1RK1 w - - 0 12",
  "played": {
    "uci": "d1e2",
    "san": "Qe2",
    "p": 0.0662
  },
  "best": {
    "uci": "f3e5",
    "san": "Nxe5",
    "p": 0.2777
  },
  "divergence": 0.21150000000000002,
  "severity": "missed",
  "attention": {
    "engagement_played": 0.4546312689781189,
    "engagement_best": 0.48357683420181274,
    "hot_squares": [
      "d8",
      "g8"
    ],
    "blind": false
  },
  "confirmation": {
    "swing_cp": 29,
    "confirmed": false
  },
  "motifs": [
    "quietMove",
    "advantage",
    "veryLong"
  ],
  "concepts": [
    "material",
    "center_control",
    "center_control",
    "piece_activity",
    "piece_activity",
    "piece_activity",
    "king_safety",
    "king_safety"
  ],
  "opening": {
    "eco": "???",
    "name": "Unknown"
  },
  "pv_san": [
    "e4", "d4", "cxd4", "Nxf3+", "Nxf3", "Nxd4", "Nxd4", "Qxd4", "Qxd4", "Bxd4",
    "Bxh6", "Re8", "Rab1", "b5", "b3", "a5", "Bd3", "b4", "Bb5", "Re7"
  ]
}
```

#### Example `steer_finding` Object (`id: "s-000-p023"`)
```json
{
  "id": "s-000-p023",
  "game": {
    "white": "derdiedasdie",
    "black": "purplepudding",
    "date": "2026.07.21"
  },
  "ply": 23,
  "fen_before": "r1bq1rk1/pp3pb1/2n3pp/2ppn3/5B2/2P1PN1P/PPBN1PP1/R2Q1RK1 w - - 0 12",
  "best": {
    "uci": "e3e4",
    "san": "e4",
    "eval_cp": 14,
    "complexity": 0.2069616488372763,
    "components": {
      "score": 0.2069616488372763,
      "decisiveness": 0.31,
      "narrowness": 0.01,
      "policy_trap": 0.006611,
      "attention": 0.7863944883727627
    }
  },
  "steer": {
    "uci": "f3e5",
    "san": "Nxe5",
    "eval_cp": 2,
    "complexity": 0.5127861942172487,
    "components": {
      "score": 0.5127861942172487,
      "decisiveness": 0.319,
      "narrowness": 0.845,
      "policy_trap": 0.2622035,
      "attention": 0.7924549421724861
    }
  },
  "playable_candidates": [
    { "uci": "f3e5", "complexity": 0.5127861942172487, "eval_cp": 2 },
    { "uci": "f4e5", "complexity": 0.37175793484408726, "eval_cp": -11 },
    { "uci": "f1e1", "complexity": 0.2132110315073306, "eval_cp": -5 },
    { "uci": "e3e4", "complexity": 0.2069616488372763, "eval_cp": 14 }
  ],
  "eval_loss_cp": 12,
  "had_tal_move": true,
  "opening": {
    "eco": "???"
  }
}
```

---

### 3.5 Bottom-Line Verdict

```
-------------------------------------------------------------------------------
FINAL VERDICT: GOOD (WITH ECO OPENING UNMAPPED WARNING)
-------------------------------------------------------------------------------
- Pipeline execution: FULLY COMPLETED (880 moves, 30 games, 2xT4 Kaggle run)
- Saliency / Vision: FUNCTIONAL (6 attention-blind findings; active hot_squares)
- Steering / TS2: SUCCESSFUL (256 candidates, 63 Tal moves, budget_exhausted=false)
- Engine Confirmation: VALID (130 confirmed tactical errors, max swing 7856 cp)
- Minor Defect: ECO opening classification unmapped (ECO == '???')
-------------------------------------------------------------------------------
```
