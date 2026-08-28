# BRIEF — trainer: make the interview ladder actually reachable

**Filed:** 2026-08-28 by the leader
**Worker:** Gemini 3.7 Flash (High), Antigravity IDE, workspace `chess_speak_out_loud`
**Status:** ACTIVE

**Why this before the interview?** This *is* the interview. The `hereon-aeon-up` ladder holds 51
cards and **46 of them cannot be served to the user by any route the app currently offers** — the
17 Level-4 cards on the publication gap and facing Karl, and the 9 Level-5 cards on delivering the
talk, are unreachable. The rehearsal instrument does not serve the material it was built for.

---

## 0. The contract

`agents/README.md` applies in full. Three clauses matter most here:

- **You touch code only.** Do not write, edit, reword or add a single flashcard. Every `.json`
  file under `trainer/content/ladders/` is **off limits**. Card content is the leader's, and three
  fabricated deliveries on this project all came from a worker being asked for content.
- **Never invent a number.** Every count in your report comes from a command you actually ran and
  whose output you paste.
- **Stop and ask** for anything this brief does not cover.

**Files you may modify — exactly two:**

```
trainer/engine.py
trainer/tests/test_engine.py
```

Everything else is read-only. Do not commit. Do not push. Leave the tree dirty; the leader audits
the diff.

---

## 1. The defect, established

Run this first, from the repo root, and paste the output into your report as **Evidence A**:

```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -c "import sys,datetime,collections; sys.path.insert(0,'.'); from trainer import engine; from trainer.app import load_all_cards, load_progress; cards=[c for c in load_all_cards() if c.get('ladder')=='hereon-aeon-up']; prog=load_progress(); now=datetime.datetime.now(datetime.timezone.utc); print('total', len(cards)); print('normal', len(engine.filter_selectable_cards(cards,prog,now,cram_mode=False))); print('cram  ', len(engine.filter_selectable_cards(cards,prog,now,cram_mode=True)))"
```

The leader's run gives `total 51`, `normal 5`, `cram 6`. Two independent gates are stacking:

1. **Level gating** (`get_ladder_active_level`) serves only the lowest level that is under 80 %
   mastered. For `hereon-aeon-up` that is Level 0, so Levels 1–5 are not served at all.
2. **Prerequisites** (`is_card_unlocked`). Cram mode already bypasses level gating and due dates,
   but it still applies `is_card_unlocked`, and the ladder's `requires` chains are five deep. So
   cram raises the pool from 5 to 6, not to 51.

Gate 1 is correct behaviour and **must not be weakened** — ladder progression is a deliberate
design decision (`briefs/2026-08-20_trainer-level-progression.md`). The bug is gate 2: **cram mode
does not actually cram.**

---

## 2. What to build

A third selection mode, so the three modes are:

| mode | level gate | prerequisites | due dates |
|---|---|---|---|
| normal | enforced | enforced | enforced |
| cram | bypassed | **bypassed (this is the change)** | bypassed |

There is no fourth mode. Do not add one. Do not rename `cram`.

### Step 2.1 — `trainer/engine.py`, `filter_selectable_cards`

The cram branch currently reads:

```python
    if cram_mode:
        for card in cards:
            card_id = card["id"]
            reqs = card.get("requires", [])
            if is_card_unlocked(reqs, progress):
                selectable.append(card)
        return selectable
```

Change it so cram mode returns every card handed to it, with no unlock filtering and no due-date
filtering. Keep the function's signature, its docstring's first line, and the normal-mode branch
below it **byte-for-byte unchanged**. Update the docstring to say what cram now means.

`select_next_card` applies `ladder_filter` *before* calling this function, so a cram request scoped
to one ladder will correctly return that ladder's whole card set. **Do not touch
`select_next_card`, `is_card_unlocked`, `_is_card_mastered`, `get_ladder_active_level`,
`is_card_due`, `update_sm2` or `calculate_elo`.** The Elo window, the recency buffer and the
unseen-first preference all stay exactly as they are.

### Step 2.2 — `trainer/tests/test_engine.py`

Add tests. Do not modify or delete any existing test.

1. `test_cram_mode_ignores_prerequisites` — build a small synthetic card list where card `B`
   has `requires: ["A"]` and progress is empty. Assert `B` is absent from
   `filter_selectable_cards(..., cram_mode=False)` and present with `cram_mode=True`.
2. `test_cram_mode_ignores_level_gate` — a card at level 4 in a ladder whose level 0 is unmastered
   is absent in normal mode and present in cram mode.
3. `test_normal_mode_still_enforces_prerequisites` — the regression guard. With `cram_mode=False`,
   a locked card stays locked. **This test must fail if you delete the `is_card_unlocked` call from
   the normal-mode branch.**

---

## 3. ✅ CHECKPOINT — run these, paste every output

Run all four from the repo root. A report without all four pasted verbatim is not accepted.

**Gate 1 — the defect is closed.** Re-run the Evidence A command. It must now print
`total 51`, `normal 5`, `cram 51`. If `cram` is anything other than 51, **stop and report** — do
not adjust the number by changing card content.

**Gate 2 — the unit tests.**
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest trainer/tests -q
```

**Gate 3 — the content gate still passes, unchanged.**
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe trainer\verify_cards.py
```
It must report **205 cards** and `[PASS]`. If the card count moved, you edited content — revert it.

**Gate 4 — mutation check, and you must actually perform it.** In `filter_selectable_cards`'s
*normal-mode* branch, temporarily delete the `is_card_unlocked` check. Re-run
`pytest trainer/tests -q` and confirm `test_normal_mode_still_enforces_prerequisites` goes **red**.
Restore the line. Re-run and confirm green. Paste both outputs. A guard that has never been seen
to fail is not a guard.

**Gate 5 — the app still boots and serves the locked material.**
```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn trainer.app:app --port 8010
```
Then, in a second shell:
```powershell
curl.exe "http://127.0.0.1:8010/api/next-card?ladder=hereon-aeon-up&cram=true"
```
Paste the returned card id. Repeat the curl five times and paste all five ids. At least one must be
a `her-l3-*`, `her-l4-*` or `her-l5-*` id — that is the whole point of the change. Stop the server.

---

## 4. Report

Write `agents/reports/2026-08-28_trainer-interview-mode_REPORT.md`. Include:

1. The diff you made, as a `git diff` you actually ran and pasted.
2. All five gate outputs verbatim.
3. Anything you changed that this brief did not name, and why. (The correct answer is "nothing".)
4. Confirm in one line that you modified no file under `trainer/content/`.

Then stop. Do not commit, do not push, do not proceed to any other brief.
