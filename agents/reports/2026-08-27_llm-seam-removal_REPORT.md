# REPORT — 2026-08-27_llm-seam-removal

**Executed:** 2026-08-30, 21:45–22:05
**Executed by:** the **leader** (Opus 5), not the worker.
**Brief:** `agents/briefs/2026-08-27_llm-seam-removal.md`

> ⚠ **Read this before the verdict.** This brief was written for Gemini and sat ACTIVE for three
> days because it needed Thejus to hand-carry it into Antigravity, and the interview took
> priority. Thejus asked for the chess project tonight, so the leader executed it directly.
> **The consequence is that the usual independent audit did not happen** — the person who wrote
> the diff is the person who checked it. Everything below is a real run with real output, but
> "the leader verified his own work" is a weaker claim than this repo's loop normally makes.
> **An independent audit of this diff is a legitimate follow-up brief.**

---

## 1. Null test — the defect existed on HEAD before the change

```
$ grep -c "sound piece activity" data/training/cache/explanations.jsonl
9
```

**The brief said four. It was nine.** Measured, not recalled — see §6.

---

## 2. Suite arithmetic

```
before − deleted + added = after
   301 −      12 +     2 =    291
```

It balances exactly.

**Before** (`backend/tests`, the known flake deselected):

```
==== 301 passed, 5 skipped, 1 deselected, 6 warnings in 151.97s (0:02:31) =====
```

**Deleted** — `backend/tests/test_explanations.py`, measured before removal, all 12 passing:

```
======================== 12 passed, 1 warning in 3.91s ========================
```

**After:**

```
==== 291 passed, 5 skipped, 1 deselected, 5 warnings in 165.85s (0:02:45) =====
```

The warning count fell 6 → 5: one was the `google.generativeai` deprecation
`FutureWarning`, which was raised by importing `llm_client` from the deleted test module and is
no longer raised by the suite's non-test code.

---

## 3. Every gate command, real output

### Gate 1 — `pytest backend/tests -q --deselect …test_ts2_orphan_future_cancellation_handled`

See §2. `291 passed, 5 skipped, 1 deselected`.

### Gate 2 — `grep -rn "llm_client" backend --include=*.py | grep -v __pycache__`

```
backend/app.py:43:# backend/ may import llm_client, so no request path can reach a language model. The motto
backend/tests/test_llm_seam.py:8:`llm_client.generate_move_explanation` with a FEN, a move and an eval -- no
backend/tests/test_llm_seam.py:33:#: unit tests may legitimately reach it); `llm_client.py` obviously imports
backend/tests/test_llm_seam.py:35:EXCLUDED = {BACKEND_DIR / "tests", BACKEND_DIR / "llm_client.py"}
backend/tests/test_llm_seam.py:42:def _imports_llm_client(tree: ast.AST) -> bool:
backend/tests/test_llm_seam.py:43:    """True if this module imports llm_client in any form.
backend/tests/test_llm_seam.py:45:    Covered: `import llm_client`, `import backend.llm_client`,
backend/tests/test_llm_seam.py:46:    `from backend import llm_client`, `from backend.llm_client import X`,
backend/tests/test_llm_seam.py:47:    `from . import llm_client`, `from .llm_client import X`.
backend/tests/test_llm_seam.py:52:                # "backend.llm_client" or "llm_client"
backend/tests/test_llm_seam.py:53:                if alias.name == "llm_client" or alias.name.endswith(".llm_client"):
backend/tests/test_llm_seam.py:57:            if module == "llm_client" or module.endswith(".llm_client"):
backend/tests/test_llm_seam.py:60:                if alias.name == "llm_client":
backend/tests/test_llm_seam.py:65:def test_no_module_reachable_from_app_imports_llm_client():
backend/tests/test_llm_seam.py:79:        if _imports_llm_client(tree):
backend/tests/test_llm_seam.py:83:        "These modules import backend/llm_client.py, so a request path can reach a "
```

**⚠ DEVIATION from the brief's expectation.** The brief expected this to return *only*
`test_llm_seam.py`. There is one extra line: `backend/app.py:43`, a **comment** I added where
`LLM_ENABLED` sits, pointing the next reader at the test that actually holds the line. It is not
an import — that is precisely why the guard parses with `ast` rather than grep. Flagging it rather
than quietly leaving the gate looking wrong.

### Gate 3 — `grep -rn "enrich_tree_explanations" . --include=*.py --include=*.tsx --include=*.ts`

Nothing under `backend/`, `frontend/` or `docs/`. One prose mention in the new test's docstring.
**But it also returned 15 hits under `kaggle_files/` — see §6.**

### Gate 4 — `ls data/training/cache/`

```
policy.jsonl
stage_b.jsonl
steer.jsonl
```

`explanations.jsonl` is gone; the three siblings are untouched.

**⚠ Note for whoever audits this:** `data/.gitignore:1` is `*`, so that cache file was **never
tracked by git**. Its deletion is real on disk but **invisible in the diff** — you cannot verify
it from `git show`. Run `ls data/training/cache/` yourself.

### Gate 5 — `cd frontend && npm test` (`vitest run`, per `package.json`)

```
 Test Files  9 passed (9)
      Tests  49 passed (49)
   Duration  55.04s
```

Includes `RepertoireTrainer.test.tsx`, which mounts the panel that was edited.

### Gate 6 — `git status --short`

```
 M HOW_TO_RUN.md
 M backend/app.py
D  backend/tests/test_explanations.py
D  backend/training/explanations.py
 M docs/plans/ARCHITECTURE.md
 M frontend/src/components/Training/RepertoirePanel.tsx
 M trainer/state/answers.jsonl
 M trainer/state/comments.jsonl
 M trainer/state/progress.json
?? backend/tests/test_llm_seam.py
```

Everything in Scope, plus three `trainer/state/*` files that were **already dirty before this
work began** (Thejus's drilling this morning) and are unrelated.

---

## 4. Mutation test — all three steps

The **first attempt was malformed and that was worth more than a clean pass.** I inserted
`from backend import llm_client` at line 1 of `backend/training/select_repertoire.py`, above its
`from __future__ import annotations` — a `SyntaxError`. Instead of the guard going red, pytest
died at **collection**:

```
ERROR: found no collectors for …test_llm_seam.py::test_no_module_reachable_from_app_imports_llm_client
backend\tests\test_llm_seam.py:25: in <module>
    from backend.tests.test_repertoire_tree import MockEngine, _epd_after, _game, _stub_eco
…
SyntaxError: from __future__ imports must occur at the beginning of the file
```

That exposed **a real weakness in my own test**: it imported fixtures at module scope, so a
broken module under `backend/` took the guard down with it — exactly when you most need the guard
to tell you which file is at fault. **Fixed:** those imports moved inside the behavioural test, so
the static guard is now completely independent of importing any backend module.

**Step 1** — insert after the `__future__` line:

```
$ sed -n 17,19p backend/training/select_repertoire.py
from __future__ import annotations
from backend import llm_client
```

**Step 2** — the guard goes RED and names the file:

```
backend\tests\test_llm_seam.py F.                                        [100%]

____________ test_no_module_reachable_from_app_imports_llm_client _____________
E   AssertionError: These modules import backend/llm_client.py, so a request path can reach a language model:
E       backend\training\select_repertoire.py
E
E     The motto is that the LLM translates LC0's thinking and never reasons about chess itself. …
E   assert not ['backend\\training\\select_repertoire.py']
```

The behavioural test correctly still passed (`F.`) — an import is not yet an attached explanation.

**Step 3** — revert, byte-identical, green:

```
$ git checkout -- backend/training/select_repertoire.py
$ git diff --stat backend/training/select_repertoire.py
(no output)
$ pytest backend/tests/test_llm_seam.py -q
============================== 2 passed in 1.02s ==============================
```

---

## 5. What changed

| file | action |
|---|---|
| `backend/training/explanations.py` | **deleted** |
| `backend/tests/test_explanations.py` | **deleted** (12 tests) |
| `data/training/cache/explanations.jsonl` | **deleted** (16 entries, gitignored) |
| `backend/tests/test_llm_seam.py` | **created** — 2 tests |
| `backend/app.py` | unused `generate_conversation` import removed; **both** `enrich_tree_explanations` call sites removed; `LLM_ENABLED` comment corrected to say it is a historical flag nothing reads |
| `frontend/.../RepertoirePanel.tsx` | generated-prose branch removed; the LC0-derived branch is now the only content of the Coach Explanation card |
| `HOW_TO_RUN.md` | line 90 corrected |
| `docs/plans/ARCHITECTURE.md` | line 30 **and** the mermaid edge at line 20 corrected |

**Deviation:** the brief's scope table says `ARCHITECTURE.md`; the file was moved to
`docs/plans/ARCHITECTURE.md` by commit `3e2d403` after the brief was written. Same file, followed
to its new path. It also had a **second** stale assertion the brief did not name — the mermaid
edge `API -.->|Dormant/Disabled| Gemini` — corrected too.

---

## 6. Second LLM path, and corrections to the brief's own evidence

**This is the highest-value section, per the brief.**

### 6.1 The brief named one call site. There are two.

```
backend/app.py:659  (repertoire tree endpoint)
backend/app.py:745  (repertoire drills endpoint — "attach coach explanations so drills carry
                     them in their reveal")
```

The brief's scope table said `657-659` only. **The drills endpoint served the same generated text
into drill reveals** and nobody had recorded it. Both are removed.

### 6.2 The filler was on nine entries, not four

```
16 entries, 8 distinct EPDs.
9 carry _build_fallback_explanation's fixed tail ("Focus on maintaining sound piece
  activity and watch out for opponent counter-play"), length 186–187.
7 are 25–37 chars and do NOT match the fallback template.
```

The 7 short ones are **real model output, truncated mid-word** — `"Developing your knight to"`,
`"Playing c4 immediately stakes a claim"`. The fallback always ends with its fixed sentence, so
these did not come from it. **The app has genuinely called Gemini and served its chess text**,
which is a stronger statement of the violation than the brief made. (Why they truncate is not
established — `max_output_tokens=180` is far above 37 characters. Unresolved, see §7.)

### 6.3 `kaggle_files/` holds a complete second copy of the defect — NOT fixed, as instructed

```
kaggle_files/backend/app.py:548  tree = await explanations.enrich_tree_explanations(tree)
kaggle_files/backend/app.py:634  tree = await explanations.enrich_tree_explanations(tree)
kaggle_files/backend/training/explanations.py
kaggle_files/backend/llm_client.py
```

A full 64-file clone of `backend/`, frozen **2026-07-21**, with both call sites and its own
`llm_client.py`. Mitigating: `.gitignore:63` ignores `kaggle_files/`, so it is **local-only and
not in the repository**, and it is not reachable from the served app. My interlock walks
`backend/` only and does **not** cover it.

**Recommendation, not taken:** do not patch that snapshot. It is five weeks stale for other
reasons too; regenerate it from HEAD when Kaggle is next used. Recording it so the next person
does not re-serve a July backend and reintroduce this.

### 6.4 The brief's claim about `generate_conversation` checks out

`backend/app.py:288` is `#     coach_summary = await generate_conversation(...)` — genuinely
commented out. Only the import at line 35 was live and unused; removed.

---

## 7. What I could not check

**This section is non-empty on purpose. Twice in this project the worker's "could not verify"
held the most important finding.**

1. **Nobody has looked at the Coach Explanation card in a running browser.** `vitest` passes and
   `RepertoireTrainer.test.tsx` mounts the panel, but I did not start the app and look at that
   card with a real repertoire tree loaded. **This project's single most repeated failure is
   correct work that nobody looked at** — it has now happened four times. Treat this as open.
2. **The two repertoire endpoints were not exercised over HTTP.** They need the live LC0 engine
   and a games corpus; I tested `build_repertoire_tree` directly instead, which is what the brief
   permits. So "the endpoint returns no `explanation`" is inferred from the tree builder plus the
   removed call, not observed on the wire.
3. **Why the 7 cached generations truncate mid-word is unexplained.** `max_output_tokens=180`
   does not account for a 25-character output. Could be a safety-filter stop, a `_clean_plain_text`
   bug, or partial-response handling in `llm_client`. The cache is deleted so the evidence is gone
   from disk — **it survives only in this report**. If the translator role is ever built on
   `llm_client.py`, that truncation is an unresolved bug sitting under it.
4. **No independent audit.** See the banner at the top. I wrote this diff and I checked it.
5. **`google.generativeai` is deprecated** — the suite emits
   `FutureWarning: All support for the google.generativeai package has ended`. `llm_client.py`
   also targets model id `gemini-3.5-flash`, **which is not a real model**. Whenever the
   translator is built, that module needs rewriting against `google.genai` regardless; it is not
   usable scaffolding as it stands.

---

## 8. Verdict

The seam is closed. No non-test module under `backend/` imports `llm_client`; neither endpoint
calls the enricher; the poisoned cache is gone; the UI falls back to text derived from LC0's own
computed values; and a mutation-verified static guard fails loudly, naming the file, if anyone
re-introduces the import.

`LLM_ENABLED = False` was a sign for five weeks and it did not hold. There is now an interlock.
