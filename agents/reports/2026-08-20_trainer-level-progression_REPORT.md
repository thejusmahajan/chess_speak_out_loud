# Delivery Report: Level-Gated Progression (2026-08-20_trainer-level-progression)

**Brief ID:** `2026-08-20_trainer-level-progression`  
**Date:** 2026-08-20  
**Status:** COMPLETED & VERIFIED  

---

## 1. Executive Summary & Intent Fulfillment

The 18 Level 0 cards created in the previous delivery were not being served because the global ±150 Elo selection window around user rating `1055.6` selected Level 1 cards (`[1020..1060]`) while skipping Level 0 cards (`[780..840]`).

To resolve this without altering the audited Elo, SM-2, or prerequisite mechanics:
1. **Level-Gated Candidate Pool:** Implemented per-ladder active level gating in `trainer/engine.py`. For each ladder, the active eligible level `L` is the lowest level with `< 80%` mastered cards. Cards with `level > L` are excluded from normal selection.
2. **Independent Ladder Progression:** Each ladder advances independently from `L` to `L+1` as soon as at least 80% of level `L` cards in that ladder are mastered.
3. **Rating Reset:** Reset `user_rating` in `trainer/state/progress.json` from `1055.64` to `820.0` (middle of Level 0 band), preserving all card histories and rep counters.
4. **Cram Mode Preserved:** Cram mode bypasses level gating and due-date filters, maintaining the unconstrained review escape hatch.

---

## 2. Gate Verification Results (Real Terminal Outputs)

### Gate 1: Pytest Test Suite (16 passing tests)
```
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
```
**Output:**
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 16 items

trainer\tests\test_engine.py ................                            [100%]

============================= 16 passed in 0.79s ==============================
Exit code: 0
```

---

### Gate 2: Card Verification & Boundaries Gate
```
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer/verify_cards.py
```
**Output:**
```
=================================================================
Verifying Knowledge Trainer Content Ladders & Boundaries...
=================================================================
Loaded 5 authoritative forbidden claim boundaries from 06_do_not_claim.md.

[PASS] All content, grounding, and constraint gates passed!

Card Counts by Ladder:
  - air_quality: 14 cards (Level 0: 2)
  - neural_processes: 15 cards (Level 0: 3)
  - own_work: 14 cards (Level 0: 2)
  - pytorch: 19 cards (Level 0: 7)
  - uncertainty: 16 cards (Level 0: 4)

Total verified cards: 78
Total repo citations: 91
Total URL citations:  74
=================================================================
Exit code: 0
```

---

### Gate 3: Working Tree Status
```
git status
```
**Output:**
```
On branch windows-dev
Your branch is ahead of 'origin/windows-dev' by 28 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   trainer/engine.py
	modified:   trainer/state/progress.json
	modified:   trainer/tests/test_engine.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	gemini_stable_drill_ids_srs.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

---

## 3. Real Progress.json 400-Draw Measurement

```
$ python -c "
import json
from datetime import datetime, timezone
from pathlib import Path
from trainer.engine import select_next_card

ladders_dir = Path('trainer/content/ladders')
all_cards = []
for jf in ladders_dir.glob('*.json'):
    with open(jf, 'r', encoding='utf-8') as f:
        data = json.load(f)
        all_cards.extend(data if isinstance(data, list) else data.get('cards', []))

with open('trainer/state/progress.json', 'r', encoding='utf-8') as f:
    progress = json.load(f)

now = datetime.now(timezone.utc)
draws = {}
for i in range(400):
    c = select_next_card(all_cards, progress, now, cram_mode=False, random_seed=i)
    if c:
        lvl = c.get('level', 0)
        draws[lvl] = draws.get(lvl, 0) + 1

print('stored user rating:', progress.get('user_rating'))
print('levels served over 400 draws:', draws)
"
```

**Output:**
```
stored user rating: 820.0
levels served over 400 draws: {0: 400}
```

---

## 4. User Rating Before / After

- **Before:** `1055.64` (inherited from initial 1200 assumed baseline after early session drops)
- **After:** `820.0` (centered in the Level 0 difficulty band `[780..840]`)

All card histories, repetition counts, interval days, ease factors, and timestamps in `trainer/state/progress.json` were strictly preserved.

---

## 5. Mutation Proof (Test 1 Guard)

1. **Mutation Injected:** Commented out `# if card_level > active_levels.get(ladder, 0): continue` in `trainer/engine.py:filter_selectable_cards`.
2. **Measurement Run with Mutation:**
   ```
   With mutation and empty progress (rating 1200), levels served: {0, 1}
   With mutation and inherited rating 1055.6, levels served: {0, 1}
   ```
3. **Test Failure:** `test_new_user_is_served_level_zero` strictly failed asserting `levels_served == {0}` because Level 1 cards were served before Level 0 mastery.
4. **Restoration:** Restored level-check logic in `trainer/engine.py`; all 16 tests passed.

---

## 6. Required Reflection Question

> **"If exactly one thing in this delivery is still wrong, what is it most likely to be, and did I check it?"**

**Answer:**  
The most likely edge case was that when a user masters 80% of Level 0 cards, the remaining 20% of unmastered Level 0 cards might be starved or permanently bypassed if the Elo window widens directly into Level 1 cards.

**How it was checked:**  
I verified in `filter_selectable_cards` that cards with `card_level <= active_level` remain in the eligible candidate pool. In `test_level_one_unreachable_until_level_zero_mastered`, when 80% of Level 0 cards were mastered (leaving 2 unmastered Level 0 cards), 50 draws produced `{1: 34, 0: 16}`, proving that both the newly unlocked Level 1 cards and the remaining due Level 0 cards are served proportionally according to rating distance.
