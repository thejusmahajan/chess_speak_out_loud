# REPORT — trainer: make the interview ladder actually reachable

**Filed:** 2026-08-28  
**Brief:** `agents/briefs/2026-08-28_trainer-interview-mode.md`  
**Worker:** Gemini 3.7 Flash (High), Antigravity IDE  
**Status:** COMPLETE  

---

## 1. Git Diff

The following is the exact `git diff trainer/engine.py trainer/tests/test_engine.py` output:

```diff
diff --git a/trainer/engine.py b/trainer/engine.py
index 16a4998..eac7f99 100644
--- a/trainer/engine.py
+++ b/trainer/engine.py
@@ -230,17 +230,15 @@ def filter_selectable_cards(
 ) -> List[Dict[str, Any]]:
     """
     Filter cards that are unlocked (prerequisites met), level-eligible, and due (if not in cram mode).
+
+    In cram mode, all cards are returned directly, bypassing level gating, prerequisite
+    unlock checks, and due-date scheduling.
     """
+    if cram_mode:
+        return list(cards)
+
     selectable = []
     cards_progress = progress.get("cards", {})
-    
-    if cram_mode:
-        for card in cards:
-            card_id = card["id"]
-            reqs = card.get("requires", [])
-            if is_card_unlocked(reqs, progress):
-                selectable.append(card)
-        return selectable
 
     # Level gating: compute active level per ladder
     ladder_groups: Dict[str, List[Dict[str, Any]]] = {}
@@ -308,19 +306,23 @@ def select_next_card(
         return float(c.get("difficulty", 1200))
     
     # 1. Elo window matching (|Rc - Ru_ladder| <= window, starting at 150)
-    window = 150.0
-    elo_matched = []
-    while window <= 2000.0:
-        elo_matched = [
-            c for c in candidates
-            if abs(get_card_rating(c) - get_ladder_rating(progress, c.get("ladder", "default"))) <= window
-        ]
-        if len(elo_matched) >= 3 or len(elo_matched) == len(candidates):
-            break
-        window += 50.0
-        
-    if not elo_matched:
-        elo_matched = candidates
+    # In cram mode, skip the Elo window entirely to allow drilling all material
+    if cram_mode:
+        elo_matched = list(candidates)
+    else:
+        window = 150.0
+        elo_matched = []
+        while window <= 2000.0:
+            elo_matched = [
+                c for c in candidates
+                if abs(get_card_rating(c) - get_ladder_rating(progress, c.get("ladder", "default"))) <= window
+            ]
+            if len(elo_matched) >= 3 or len(elo_matched) == len(candidates):
+                break
+            window += 50.0
+            
+        if not elo_matched:
+            elo_matched = candidates
         
     # 2. Prefer unseen cards within the Elo-matched pool
     unseen = [c for c in elo_matched if c["id"] not in cards_progress]
diff --git a/trainer/tests/test_engine.py b/trainer/tests/test_engine.py
index fd2b706..541b438 100644
--- a/trainer/tests/test_engine.py
+++ b/trainer/tests/test_engine.py
@@ -164,7 +164,7 @@ def test_level_zero_prerequisite_gating():
     progress = {"user_rating": 800.0, "cards": {}}
     
     # Level-1 is locked; only Level-0 is selectable
-    selectable = filter_selectable_cards(cards, progress, now, cram_mode=True)
+    selectable = filter_selectable_cards(cards, progress, now, cram_mode=False)
     assert len(selectable) == 1
     assert selectable[0]["id"] == "pyt-l0-001"
     
@@ -177,7 +177,7 @@ def test_level_zero_prerequisite_gating():
         "mastered": False,
         "history": [{"score": 0.5}],
     }
-    selectable = filter_selectable_cards(cards, progress, now, cram_mode=True)
+    selectable = filter_selectable_cards(cards, progress, now, cram_mode=False)
     assert len(selectable) == 1
     assert selectable[0]["id"] == "pyt-l0-001"
     
@@ -190,7 +190,7 @@ def test_level_zero_prerequisite_gating():
         "mastered": True,
         "history": [{"score": 1.0}],
     }
-    selectable = filter_selectable_cards(cards, progress, now, cram_mode=True)
+    selectable = filter_selectable_cards(cards, progress, now, cram_mode=False)
     assert len(selectable) == 2
     assert any(c["id"] == "pyt-l1-001" for c in selectable)
 
@@ -353,11 +353,11 @@ def test_selection_rating_window_widening():
     
     # 5 cards in range [1100..1300], 1 far out [1900]
     cards = [
-        {"id": f"c{i}", "level": 1, "difficulty": 1200, "requires": []} for i in range(5)
-    ]
-    cards.append({"id": "c_far", "level": 5, "difficulty": 1900, "requires": []})
-    
-    selected = select_next_card(cards, progress, now, cram_mode=True, random_seed=42)
+        {"id": f"c{i}", "level": 0, "difficulty": 1200, "requires": []} for i in range(5)
+    ]
+    cards.append({"id": "c_far", "level": 0, "difficulty": 1900, "requires": []})
+    
+    selected = select_next_card(cards, progress, now, cram_mode=False, random_seed=42)
     assert selected is not None
     assert selected["id"] != "c_far"
 
@@ -747,4 +747,77 @@ def test_selector_never_starves():
         assert selected["id"] in ("card-A", "card-B")
 
 
+# =====================================================================
+# 8. Cram Mode & Prerequisite Selection Tests
+# =====================================================================
+
+def test_cram_mode_ignores_prerequisites():
+    """Card B requiring A is absent in normal mode (empty progress) and present in cram mode."""
+    now = datetime.now(timezone.utc)
+    card_a = {"id": "card-a", "ladder": "test", "level": 0, "difficulty": 800, "requires": []}
+    card_b = {"id": "card-b", "ladder": "test", "level": 0, "difficulty": 800, "requires": ["card-a"]}
+    cards = [card_a, card_b]
+    progress = {"cards": {}}
+
+    selectable_normal = filter_selectable_cards(cards, progress, now, cram_mode=False)
+    assert not any(c["id"] == "card-b" for c in selectable_normal)
+    assert any(c["id"] == "card-a" for c in selectable_normal)
+
+    selectable_cram = filter_selectable_cards(cards, progress, now, cram_mode=True)
+    assert any(c["id"] == "card-b" for c in selectable_cram)
+    assert any(c["id"] == "card-a" for c in selectable_cram)
+
+
+def test_cram_mode_ignores_level_gate():
+    """A card at level 4 in a ladder whose level 0 is unmastered is absent in normal mode and present in cram mode."""
+    now = datetime.now(timezone.utc)
+    card_l0 = {"id": "card-l0", "ladder": "test-ladder", "level": 0, "difficulty": 800, "requires": []}
+    card_l4 = {"id": "card-l4", "ladder": "test-ladder", "level": 4, "difficulty": 1600, "requires": []}
+    cards = [card_l0, card_l4]
+    progress = {"cards": {}}
+
+    selectable_normal = filter_selectable_cards(cards, progress, now, cram_mode=False)
+    assert not any(c["id"] == "card-l4" for c in selectable_normal)
+    assert any(c["id"] == "card-l0" for c in selectable_normal)
+
+    selectable_cram = filter_selectable_cards(cards, progress, now, cram_mode=True)
+    assert any(c["id"] == "card-l4" for c in selectable_cram)
+    assert any(c["id"] == "card-l0" for c in selectable_cram)
+
+
+def test_normal_mode_still_enforces_prerequisites():
+    """Regression guard: with cram_mode=False, a locked card stays locked."""
+    now = datetime.now(timezone.utc)
+    card_base = {"id": "card-base", "ladder": "ladder-x", "level": 0, "difficulty": 800, "requires": []}
+    card_locked = {"id": "card-locked", "ladder": "ladder-x", "level": 0, "difficulty": 800, "requires": ["card-base"]}
+    cards = [card_base, card_locked]
+    progress = {"cards": {}}
+
+    selectable = filter_selectable_cards(cards, progress, now, cram_mode=False)
+    assert any(c["id"] == "card-base" for c in selectable)
+    assert not any(c["id"] == "card-locked" for c in selectable)
+
+
+def test_cram_mode_ignores_elo_window():
+    """A ladder whose user rating is far below its high-level cards must still be able to return one in cram mode."""
+    now = datetime.now(timezone.utc)
+    cards = [
+        {"id": f"c_low_{i}", "ladder": "test", "level": 0, "difficulty": 800, "requires": []}
+        for i in range(5)
+    ]
+    cards.append({"id": "c_high", "ladder": "test", "level": 5, "difficulty": 1950, "requires": []})
+    progress = {"ladder_ratings": {"test": 800.0}, "cards": {}}
+
+    # In normal mode, c_high is never selected
+    for i in range(20):
+        normal_sel = select_next_card(cards, progress, now, cram_mode=False, random_seed=i)
+        assert normal_sel is not None
+        assert normal_sel["id"] != "c_high"
+
+    # In cram mode, c_high is in the pool and can be selected
+    cram_selected = [select_next_card(cards, progress, now, cram_mode=True, random_seed=i)["id"] for i in range(50)]
+    assert "c_high" in cram_selected
+
+
+
 
```

---

## 2. Gate Outputs Verbatim

### Evidence A (Initial Defect Check)
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -c "import sys,datetime,collections; sys.path.insert(0,'.'); from trainer import engine; from trainer.app import load_all_cards, load_progress; cards=[c for c in load_all_cards() if c.get('ladder')=='hereon-aeon-up']; prog=load_progress(); now=datetime.datetime.now(datetime.timezone.utc); print('total', len(cards)); print('normal', len(engine.filter_selectable_cards(cards,prog,now,cram_mode=False))); print('cram  ', len(engine.filter_selectable_cards(cards,prog,now,cram_mode=True)))"
```
**Output:**
```
total 51
normal 5
cram   6
```

### Gate 1 — The defect is closed
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -c "import sys,datetime,collections; sys.path.insert(0,'.'); from trainer import engine; from trainer.app import load_all_cards, load_progress; cards=[c for c in load_all_cards() if c.get('ladder')=='hereon-aeon-up']; prog=load_progress(); now=datetime.datetime.now(datetime.timezone.utc); print('total', len(cards)); print('normal', len(engine.filter_selectable_cards(cards,prog,now,cram_mode=False))); print('cram  ', len(engine.filter_selectable_cards(cards,prog,now,cram_mode=True)))"
```
**Output:**
```
total 51
normal 5
cram   51
```

### Gate 2 — Unit tests
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
```
**Output:**
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 30 items

trainer\tests\test_engine.py ..............................              [100%]

============================= 30 passed in 0.57s ==============================
```

### Gate 3 — Content gate verification
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer\verify_cards.py
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
  - bridge: 17 cards (Level 0: 5)
  - de-grammatik: 20 cards (Level 0: 8)
  - de-konnektoren: 17 cards (Level 0: 5)
  - de-wortschatz: 15 cards (Level 0: 3)
  - hereon_aeon_up: 51 cards (Level 0: 5)
  - neural_processes: 15 cards (Level 0: 3)
  - own_work: 20 cards (Level 0: 8)
  - pytorch: 19 cards (Level 0: 7)
  - uncertainty: 17 cards (Level 0: 5)

Total verified cards: 205
Total repo citations: 193
Total URL citations:  175
=================================================================
```

### Gate 4 — Mutation check

1. With `is_card_unlocked` removed in normal-mode branch of `filter_selectable_cards`:
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
```
**Output (RED):**
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 30 items

trainer\tests\test_engine.py ..........................F.F.              [100%]

================================== FAILURES ===================================
____________________ test_cram_mode_ignores_prerequisites _____________________
trainer\tests\test_engine.py:763: in test_cram_mode_ignores_prerequisites
    assert not any(c["id"] == "card-b" for c in selectable_normal)
E   assert not True
E    +  where True = any(<generator object test_cram_mode_ignores_prerequisites.<locals>.<genexpr> at 0x0000020362693100>)
________________ test_normal_mode_still_enforces_prerequisites ________________
trainer\tests\test_engine.py:798: in test_normal_mode_still_enforces_prerequisites
    assert not any(c["id"] == "card-locked" for c in selectable)
E   assert not True
E    +  where True = any(<generator object test_normal_mode_still_enforces_prerequisites.<locals>.<genexpr> at 0x00000203626DBB90>)
=========================== short test summary info ===========================
FAILED trainer/tests/test_engine.py::test_cram_mode_ignores_prerequisites - a...
FAILED trainer/tests/test_engine.py::test_normal_mode_still_enforces_prerequisites
======================== 2 failed, 28 passed in 0.86s =========================
```

2. With `is_card_unlocked` restored:
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
```
**Output (GREEN):**
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 30 items

trainer\tests\test_engine.py ..............................              [100%]

============================= 30 passed in 0.56s ==============================
```

### Gate 5 — The app boots and serves locked material in Cram Mode (Extended to 15 draws)

Server started on port 8010:
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn trainer.app:app --port 8010
```

15 sequential draws from `curl.exe "http://127.0.0.1:8010/api/next-card?ladder=hereon-aeon-up&cram=true"`:
```
Draw  1: her-l2-002
Draw  2: her-l2-006
Draw  3: her-l5-007
Draw  4: her-l4-002
Draw  5: her-l5-001
Draw  6: her-l5-008
Draw  7: her-l3-001
Draw  8: her-l3-005
Draw  9: her-l5-003
Draw 10: her-l4-015
Draw 11: her-l2-003
Draw 12: her-l4-012
Draw 13: her-l3-007
Draw 14: her-l3-006
Draw 15: her-l3-009
```

Sample curl response payload:
```json
{"card":{"id":"her-l3-008","ladder":"hereon-aeon-up","level":3,"topic":"leave-one-station-out, and its honest limit","question":"\"How would we know your model is right where we have no measurements?\" - answer it, including the limitation.","answer":"Leave-one-station-out, not random splits - random splits leak spatially and flatter everything. Score with CRPS and calibration, with mean sigma reported beside it, because calibration without sharpness is trivially achievable. And the honest limit: LOSO tells you about station-like locations. A street canyon with no station nearby is extrapolation, and the model should say so through its epistemic uncertainty rather than through a confident number.","explanation":"This is described as the best question you are likely to get, and the answer is fully prepared. The limitation at the end is what separates it from a memorised protocol - it shows you know what your own validation does not cover.","trap":"Stopping after 'leave-one-station-out'. The protocol without its limit sounds rehearsed; the limit is the part that shows judgement.","sources":["../bioinformatics_project/job_search/applications/hereon_aeon_up/study_room/15_karl_and_ufp.md","../bioinformatics_project/job_search/applications/hereon_aeon_up/study_room/14_talk_script.md"],"difficulty":1500,"requires":["her-l2-005"]},"current_rating":1500,"reps":0,"user_rating":838.07,"ladder_rating":838.07,"ladder_ratings":{"own-work":890.63,"uncertainty":946.8,"neural-processes":895.14,"de-grammatik":1180.02,"de-wortschatz":1181.34,"air-quality":892.23,"pytorch":923.66,"de-konnektoren":1237.69,"hereon-aeon-up":838.07,"bridge":838.5}}
```

---

## 3. Scope and Changes Made

Beyond the brief's initial text, the following changes were made under the leader's authorized amendment:
1. In `trainer/engine.py` (`select_next_card`): When `cram_mode=True`, skip Elo windowing by setting `elo_matched = list(candidates)` directly so cram mode can sweep the full ladder regardless of rating difference.
2. In `trainer/tests/test_engine.py`:
   - Updated `test_level_zero_prerequisite_gating` to `cram_mode=False` so it tests normal-mode prerequisite gating.
   - Updated `test_selection_rating_window_widening` to `cram_mode=False` so it tests normal-mode Elo windowing.
   - Added four new tests in Section 8: `test_cram_mode_ignores_prerequisites`, `test_cram_mode_ignores_level_gate`, `test_normal_mode_still_enforces_prerequisites`, and `test_cram_mode_ignores_elo_window`.

Nothing else was modified.

---

## 4. Content Integrity Confirmation

I modified no file under `trainer/content/`.
