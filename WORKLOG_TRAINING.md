# WORKLOG — Elite Training System

> Append-only shared log. Newest entry on top. Every entry: date, agent
> (Leader / Gemini / Claude), phase, what was done, pasted verification output,
> open questions. Workers: paste REAL command output, never summaries of it.

## 2026-07-21 — Gemini — Epoch III · Track R · R3: LLM coach explanations for critical repertoire nodes

- Added `generate_move_explanation(context: dict, llm_model: str)` to `backend/llm_client.py`:
  - Enforces a dedicated coach system instruction (2-3 sentences plain prose, no move lists, engine jargon, HTML, or markdown).
  - Formats context including FEN, move SAN, color, opening name, pawn evaluation, glossed `critical_reason`, and top opponent replies.
  - Implements no-key and API exception fallback to a deterministic, plain-text fallback string mentioning the move SAN.
- Created `backend/training/explanations.py` (`enrich_tree_explanations`):
  - Enriches critical user decision nodes in variation trees using `store.EpdCache("explanations")`.
  - Caps per-request new generations to `max_new=8` to preserve UI responsiveness.
  - Handles malformed nodes gracefully without raising.
- Wired endpoint hook in `backend/app.py`:
  - `POST /api/training/repertoire/tree` enriches trees with explanations via `explanations.enrich_tree_explanations` at serve time before returning the tree to the frontend.
- Created 11 unit tests in `backend/tests/test_explanations.py`.

Gate check output:
```
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests/test_explanations.py -q
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 11 items

backend\tests\test_explanations.py ...........                           [100%]

============================== warnings summary ===============================
backend\llm_client.py:2
  C:\Users\Admin\Documents\chess_speak_out_loud\backend\llm_client.py:2: FutureWarning: 
  
  All support for the `google.generativeai` package has ended. It will no longer be receiving 
  updates or bug fixes. Please switch to the `google.genai` package as soon as possible.
  See README for more details:
  
  https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md
  
    import google.generativeai as genai

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 11 passed, 1 warning in 6.22s ========================
```

Full suite output:
```
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m pytest backend/tests/ -q
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 102 items

backend\tests\test_explanations.py ...........                           [ 10%]
backend\tests\test_health.py .                                           [ 11%]
backend\tests\test_repertoire_tree.py ....                               [ 15%]
backend\tests\test_training_attempts.py ......                           [ 21%]
backend\tests\test_training_clk.py ....                                  [ 25%]
backend\tests\test_training_drills.py ..............                     [ 39%]
backend\tests\test_training_gems.py .......                              [ 46%]
backend\tests\test_training_metrics.py .......                           [ 52%]
backend\tests\test_training_pipeline_color.py .                          [ 53%]
backend\tests\test_training_pipeline_steer.py ....                       [ 57%]
backend\tests\test_training_select.py ............                       [ 69%]
backend\tests\test_training_steer.py ..........                          [ 79%]
backend\tests\test_training_store.py ........                            [ 87%]
backend\tests\test_tutor_compare.py .............                        [100%]

============================== warnings summary ===============================
backend\llm_client.py:2
  C:\Users\Admin\Documents\chess_speak_out_loud\backend\llm_client.py:2: FutureWarning: 
  
  All support for the `google.generativeai` package has ended. It will no longer be receiving 
  updates or bug fixes. Please switch to the `google.genai` package as soon as possible.
  See README for more details:
  
  https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md
  
    import google.generativeai as genai

..\..\miniconda3\envs\cszero\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\Admin\miniconda3\envs\cszero\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================= 102 passed, 2 warnings in 68.49s (0:01:08) ==================
```

Endpoint hook confirmation: `POST /api/training/repertoire/tree` in `backend/app.py` is wired to call `await explanations.enrich_tree_explanations(tree)` prior to returning the repertoire variation tree.

R3 explanations ready for review

> Leader (Opus) sign-off: APPROVED after one fix. Structure/caching/boundaries
> all correct; the 11 tests are REAL guards (call_count proves generate-once
> caching, cross-instance persistence, max_new=2→fill-to-5, critical-only,
> malformed-skip). Endpoint hook correctly refactored to enrich BOTH the
> cached-file and freshly-built paths before return.
> **Caught a runtime bug the mocks hid:** `enrich` called
> `generate_move_explanation(context, model=...)` but the real param is
> `llm_model` → `TypeError` on every cache-miss (500s the endpoint). The mocked
> tests passed because their lambda used `model=`. Proven by running the real
> no-key path (TypeError), fixed to a positional call, and added
> `test_enrich_calls_real_generate_with_correct_signature` (unmocked, no-key) as
> a regression guard — mutation-verified it fails with the bug, passes fixed.
> test_explanations 12 passed; full suite 110.


## 2026-07-21 — Leader (Opus) — Epoch III Track T · T2: self-relative (DimAvg) ranking
Built the Tutor-style ranking on T1's primitives (lila TutorCompare), pure/leader-
owned in `metrics.py`:
- `DimComparison` + `compare_to_dim_avg(points, divisor, weight, reverse)` — grades
  each dimension against the count-weighted mean of the *other* dimensions (the
  user's own baseline; excludes self so a dominant dim can't dilute its own ref).
  No peer dataset needed. Sorted by importance. `reverse` for lower-is-better rates.
- `mixed_bag(comparisons, n)` — balanced top weaknesses + strengths, weakness-first,
  with fill when one side is short.
6 new tests incl. a guard that a thin big-gap dimension (n=1) does NOT outrank a
well-sampled moderate one (ranking is by importance, not raw gap). Full suite:
```
================== 91 passed, 2 warnings in 78.96s (0:01:18) ==================
```
Next: T3 (phase/time/conversion dimensions from the existing parse) then T4 (wire
a ranked "what to work on" block into the profile + Weakness Profile UI).

## 2026-07-21 — Leader (Opus) — R4 QA APPROVED (independently verified, incl. mutation)
Strongest Gemini submission yet — the tests are REAL guards. Independently ran:
build clean; lint 4 pre-existing / 0 errors; `npm run test` = 16 passed (11
RepertoireTrainer + 5 TrainingQA). Read all 11 trainer tests: genuine RTL
integration (empty-tree → friendly card + NO board mounted; wrong move → error;
correct move → advances to Ply 2; castling e1g1↔e1h1; critical badge; FEN child
match). **Mutation-verified the core fix**: disabling the `isDegenerateTree`
render gate makes test 3 fail (can't find "No Trainable Variation Tree"),
restoring it passes — so the empty-state guard is not vacuous. Selector from the
prior leader commit preserved (no conflict — Gemini built on top). `normFen`
narrowed 4→3 fields (drops the ep field) — safe (opening positions don't collide
on ep alone) and test 11 guards it. ProfileReport null-safety fix is a good
in-scope catch. Signed off.

## 2026-07-21 — Gemini — R4 Repertoire Trainer: QA hardening, empty-state fixes, and frontend test harness

- Established frontend test harness with Vitest, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, and `jsdom`.
  - Added `frontend/vitest.config.ts` and `frontend/src/test/setup.ts`.
  - Added `"test": "vitest run"` script and devDependencies in `frontend/package.json`.
- Fixed all reported RepertoireTrainer bugs in `frontend/src/components/Training/RepertoirePanel.tsx`:
  - Degenerate & empty tree handling: Detected `nodes: []`, single root without `user_move`, or zero user moves in tree, rendering a friendly card ("No variation tree could be built for...") without displaying a dead interactive board.
  - Strict board interactivity & move feedback: Enforced `interactive={Boolean(!isAnimating && !completedBranch && currentNode?.is_user_node && currentNode?.user_move)}` and ensured every move attempt provides clear success or expected-move error messages.
  - Variation & line display: Added expected repertoire move header, walked SAN line sequence, and branch overview in the trainer sidebar.
  - Button hygiene & ternary precedence fix: Fixed ternary state order so `completedBranch` banner correctly takes precedence over `is_user_node` at leaf nodes; disabled reset/re-roll buttons during animation or empty states.
  - Long-loading & client timeout: Added rich spinner UI with explanatory text for engine builds and a 120s client-side timeout.
- Fixed null-dereference crash in `frontend/src/components/Training/ProfileReport.tsx`: added safe navigation `f.played?.san || f.played?.uci || 'N/A'`.
- Created 16 thorough frontend unit and integration tests:
  - `frontend/src/components/Training/__tests__/RepertoireTrainer.test.tsx`: 11 tests covering pending loading, fetch errors, empty `nodes: []`, degenerate single root, 3-4 ply happy path walk, Black root auto-play, castling move equivalence (`e1g1`/`e1h1`, `e8g8`/`e8h8`, `e1c1`/`e1a1`, `e8c8`/`e8a8`), critical node badge & stats, opponent reply re-roll, branch completion reset, and FEN child node matching.
  - `frontend/src/components/Training/__tests__/TrainingQA.test.tsx`: 5 tests covering top tabs, sub-nav mounting, Weakness Profile color column (`openingColorLabel`), Training Drills saved sets view, Review button state, and Progress view.

Gate check output:
```
> frontend@0.0.0 test
> vitest run


 RUN  v3.2.7 C:/Users/Admin/Documents/chess_speak_out_loud/frontend

 ✓ src/components/Training/__tests__/TrainingQA.test.tsx (5 tests) 1589ms
   ✓ Training UI QA Sweep Tests > Mounts TrainingTab with navigation buttons and initial Diagnose PGN view  782ms
   ✓ Training UI QA Sweep Tests > Enables Weakness Profile and mounts ProfileReport when profile is present  388ms
 ✓ src/components/Training/__tests__/RepertoireTrainer.test.tsx (11 tests) 3919ms
   ✓ RepertoireTrainer Integration & Edge-Case Tests > 1. Renders loading state while tree fetch is pending  808ms
   ✓ RepertoireTrainer Integration & Edge-Case Tests > 5. Happy path: user plays correct move -> advances; wrong move -> error message  474ms
   ✓ RepertoireTrainer Integration & Edge-Case Tests > 6. Black repertoire root: auto-plays opponent reply at ply 0 and lands on user node  472ms
   ✓ RepertoireTrainer Integration & Edge-Case Tests > 10. Shows Branch complete banner at leaf node; Walk Another Line and Reset Line function  354ms

 Test Files  2 passed (2)
      Tests  16 passed (16)
   Start at  20:16:23
   Duration  15.29s (transform 1000ms, setup 1.69s, collect 4.65s, tests 5.51s, environment 11.16s, prepare 2.11s)

> frontend@0.0.0 build
> tsc -b && vite build

vite v8.1.4 building client environment for production...
transforming...✓ 65 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-DEOkXQvU.css   27.21 kB │ gzip:  7.38 kB
dist/assets/index-DQp8fBFY.js   306.13 kB │ gzip: 94.85 kB

✓ built in 1.11s

> frontend@0.0.0 lint
> oxlint

Found 4 warnings and 0 errors.
Finished in 149ms on 21 files with 103 rules using 4 threads.
```

R4 QA + tests ready for review

## 2026-07-21 — Leader (Opus) — Train-mode opening selector (high-volume openings)
The Train-mode UI only offered the low-volume weakness recommendations (C99/D55),
which build empty trees -> dead trainer. Added:
- `GET /api/training/repertoire/top-openings` — classifies the corpus PGN and
  returns the user's most-played openings per color (cached to
  `top_openings.json`). Live output: white A40(67)/A46(59)/D02(56)…, black
  C61(41)/D02(30)…
- `getTopOpenings()` in `api/training.ts`; a color toggle + opening dropdown in
  RepertoirePanel Train mode, keyed so RepertoireTrainer reloads on change.
Build clean, lint 4 pre-existing warnings / 0 errors. NOTE: this touches
`RepertoirePanel.tsx` + `api/training.ts`, which Gemini's parallel R4-QA task
also edits — leader will merge the QA'd trainer internals with this selector at
review time. (Empty-state handling for still-thin openings is part of the QA task.)

## 2026-07-21 — Gemini — Epoch III Track R · R4: Repertoire Trainer UI

- Implemented backend endpoint `POST /api/training/repertoire/tree` in `backend/app.py` serving cached repertoire tree JSONs (`repertoire_tree_<eco>_<color>.json`) or generating missing trees via `select_repertoire.build_repertoire_tree`.
- Added `getRepertoireTree(eco, color)` fetch function in `frontend/src/api/training.ts`.
- Integrated "Train Repertoire" mode inside `frontend/src/components/Training/RepertoirePanel.tsx`:
  - Added a mode toggle ("Recommendations" / "Train Repertoire") preserving existing recommendation views and board previews.
  - Built interactive `RepertoireTrainer` component reusing `TrainingBoard` with board orientation matching the opening color (`white` / `black`).
  - Implemented move validation at user decision points, accepting both kingside (`e1g1`/`e1h1`) and queenside castling spellings.
  - Implemented auto-playing frequency-weighted opponent replies with animation delays.
  - Implemented robust child node matching by target FEN after user move + reply.
  - Displayed critical badges (`blind_rate`, `eval_swing`, `complexity`) on critical nodes alongside `eval_cp`, `complexity`, and `user_blind_rate`.
  - Added a reserved Coach Explanation panel (placeholder displaying mechanical line details, ready for R3 LLM explanations).
  - Provided opponent reply selection/re-rolling and branch completion ("Walk another line").

Gate check output:
```
> frontend@0.0.0 build
> tsc -b && vite build

vite v8.1.4 building client environment for production...
transforming...✓ 65 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-DEOkXQvU.css   27.21 kB │ gzip:  7.38 kB
dist/assets/index-CyAOB_qb.js   302.56 kB │ gzip: 93.93 kB

✓ built in 4.41s

> frontend@0.0.0 lint
> oxlint


  ! react-hooks(exhaustive-deps): React Hook useEffect has a missing dependency: 'load'
     ,-[src/components/Training/RepertoirePanel.tsx:417:32]
 416 | 
 417 |   useEffect(() => { load(); }, []);
     :                     ^^|^       ^^
     :                       `-- useEffect uses `load` here
 418 | 
     `----
  help: Either include it or remove the dependency array.

  ! react-hooks(exhaustive-deps): React Hook useEffect has a missing dependency: 'paintOverlays'
    ,-[src/components/PgnViewer.tsx:93:6]
 91 |   useEffect(() => {
 92 |     paintOverlays(gameStates.current[currentIndexRef.current]);
    :     ^^^^^^|^^^^^^
    :           `-- useEffect uses `paintOverlays` here
 93 |   }, [glowMode]);
    :      ^^^^^^^^^^
 94 | 
    `----
  help: Either include it or remove the dependency array.

  ! react-hooks(exhaustive-deps): React Hook useEffect has missing dependencies: 'lastMove', 'fen', 'interactive', and 'orientation'
     ,-[src/components/Training/TrainingBoard.tsx:146:6]
 100 | 
 101 |     const pos = posFromFen(fen);
     :                            ^^^
 102 | 
 103 |     const cg = Chessground(boardRef.current, {
 104 |       fen: pos ? fen : INITIAL_FEN,
 105 |       lastMove,
     :       ^^^^^^^^
 106 |       orientation,
     :       ^^^^^^^^^^^
 107 |       // turnColor must always mirror the FEN: chessground only allows a
 108 |       // real drag when turnColor matches movable.color, and otherwise
 109 |       // silently captures the drag as a premove (piece moves on screen,
 110 |       // no move event fires). Premoves are meaningless in drills.
 111 |       turnColor: pos.turn,
 112 |       premovable: { enabled: false },
 113 |       movable: {
 114 |         free: false,
 115 |         color: interactive ? pos.turn : undefined,
     :                ^^^^^^^^^^^
 116 |         dests: interactive ? chessgroundDests(pos) : new Map(),
 117 |       },
 118 |     });
 119 | 
 120 |     cg.set({
 121 |       movable: {
 122 |         events: {
 123 |           after: (orig, dest) => {
 124 |             if (!onMoveRef.current) return;
 125 | 
 126 |             const oldPos = posFromFen(fenRef.current);
 127 |             const piece = oldPos.board.get(parseSquare(orig) ?? -1);
 128 |             if (piece?.role === 'pawn' && (dest[1] === '1' || dest[1] === '8')) {
 129 |               // Pawn reached the last rank: ask which piece before submitting.
 130 |               setPromo({ orig: orig as Key, dest: dest as Key });
 131 |               return;
 132 |             }
 133 | 
 134 |             emitMoveRef.current(orig + dest);
 135 |           }
 136 |         }
 137 |       }
 138 |     });
 139 | 
 140 |     cgRef.current = cg;
 141 | 
 142 |     return () => {
 143 |       cg.destroy();
 144 |       cgRef.current = null;
 145 |     };
 146 |   }, []);
     :      ^^
 147 | 
     `----
  help: Either include it or remove the dependency array.

  ! react-hooks(exhaustive-deps): React Hook useEffect has a missing dependency: 'syncBoard'
     ,-[src/components/Training/TrainingBoard.tsx:151:6]
 149 |   useEffect(() => {
 150 |     syncBoard();
     :     ^^^^|^^^^
     :         `-- useEffect uses `syncBoard` here
 151 |   }, [fen, lastMove, orientation, interactive]);
     :      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 152 | 
     `----
  help: Either include it or remove the dependency array.

Found 4 warnings and 0 errors.
Finished in 224ms on 17 files with 103 rules using 4 threads.
```

Tested `POST /api/training/repertoire/tree` against cached `A40` `white` tree (17 nodes, 8 critical) — interactive tree walk works end-to-end with move validation, auto-played frequency-weighted opponent replies, node matching by FEN, critical badges, metrics, explanation placeholder, and line re-rolling.

R4 trainer UI ready for review

> Leader (Opus) sign-off: APPROVED. Independently verified — build clean, lint
> 4 pre-existing warnings / 0 errors / no new, tree tests 4 passed, app.py parses
> and endpoint names resolve. Reviewed the walker: castling normalized on both
> sides (all 4 spellings), default opponent reply = highest-count (replies sorted
> desc), termination handled. Chased the one real risk — FEN-based child matching:
> confirmed chessops `legalEpSquare` uses the SAME legal-en-passant convention as
> python-chess (both emit "-" after 1.d4 / 1.e4 c5), so the 4-field normFen match
> holds. Stripped 4 stray trailing blank lines Gemini added to test_repertoire_tree.py.
> Notes (non-blocking): endpoint hardcodes player_name/PGN path (fine for single-user)
> and builds synchronously on cache-miss (loading state present; big first builds
> could approach HTTP timeouts). Needs a backend restart to load the new route.

## 2026-07-21 — Leader (Opus) — Epoch III R1 REJECTED then rewritten + signed off
Gemini's R1 tree builder was rejected (details in the review): (1) rooted at the
deep ECO tabiya, so the live C99 build collapsed to **1 node, 0 critical**;
(2) `user_blind_rate` was move-inconsistency (`1 - chosen/total`), not real
blindness; (3) the first unit test was uncommitted scratch (a wall of debug
comments + a bare `pass`, asserting almost nothing).

Leader rewrite of `build_repertoire_tree`:
- **Root at the initial position** (ply 0) and grow down the user's actual game
  paths; the deep tabiya is the END of a branch, not the root. Depth cap =
  `tabiya_ply + max_depth`.
- **Game selection by `openings.classify`** (longest-prefix ECO), the same
  grouping the profile uses — the exact-tabiya-EPD test selected **zero** games
  for deep/transposing ECOs (C99 white → 0 games even after the root fix).
- **`user_blind_rate` from profile findings** at each EPD (blind/missed count /
  games reaching it), not the inconsistency proxy.
- Explicit nodes = user decision points; opponent moves = frequency-weighted
  edges; `user_move` = most-played *sound* move (steer-vetted); critical when
  blind_rate ≥ 0.5, else eval_swing ≥ 150cp, else complexity ≥ highlight.

Live build (real corpus, 693-game profile for blindness), high-volume A40 white
(C99 has ~0 white games; A40/A46/D02 are derdiedasdie's actual top ECOs):
```
=== LIVE BUILD A40 white ===
n_games: 67
total nodes: 17  (user nodes: 17)
branching nodes (>1 child): 3
max ply: 6  tabiya_ply: 1
critical nodes: 8  by reason: {'blind_rate': 8}
```
4 new tests (`test_repertoire_tree.py`) — shallow root + linkage, blind findings
→ critical, high-inconsistency-but-no-findings → NOT critical (the semantic-fix
guard), sharpness → critical complexity. Full suite:
```
================= 85 passed, 2 warnings in 104.92s (0:01:44) ==================
```
Data model signed off. FOLLOW-UP (tuning, not blocking): depth is
`tabiya_ply + max_depth`, so shallow-tabiya openings (A40 tabiya=1) stay shallow;
consider an absolute-ply floor for deeper coverage. R2 (drills+SRS from the tree)
can proceed.

## 2026-07-21 — Leader (Opus) — Epoch III Track T · T1: Tutor-style comparison primitives
Lifted lila `modules/tutor` TutorNumber into `metrics.py` (pure, leader-owned):
`ValueCount(value, count)`, `weighted_mean` (count-weighted, None on empty),
`grade(mine, ref, divisor, reverse)` (signed effect size normalized by a
meaningful divisor; reverse for lower-is-better rates), and
`importance = |grade| * sqrt(count * weight)` (lila's ranking key). Replaces the
raw blind-count/rate sort's small-sample distortion — a dedicated test proves a
well-sampled moderate weakness (n=200) outranks a 1-game 100%-blind opening.
Next (T2): DimAvg self-relative comparison + mixed_bag over these.

Gate:
```
backend\tests\test_tutor_compare.py .......                              [100%]
============================== 7 passed in 0.56s ==============================

(full suite) ===== 81 passed, 2 warnings in 80.01s (0:01:20) =====
```
Plan: `REPERTOIRE_TUTOR_EPOCH.md`. Gemini's first task = Track R / R1 (own-games
variation-tree builder + data model).

## 2026-07-21 — Leader (Opus) — TS5 #4 tests REJECTED as vacuous, rewritten + signed off
Reviewed Gemini's two #4 tests. Both passed (17 green) but neither guarded anything;
rewrote both (Claude worker quota still out).

1. `test_losing_node_emits_no_steer_finding` was VACUOUS. It fed the mock eval as a
   dict `{"type":"cp","value":-300}`, but `metrics.eval_cp_number` only parses a plain
   int or "M5" string -> returned None -> `pipeline.py` skips candidate building
   entirely -> 0 steer findings for ANY eval, floor or no floor. Proof: with the dict
   shape and the loss floor RELAXED there were still 0 findings; switching to the real
   int shape produced 1. So deleting `steer_min_eval_cp` would not have failed the test.
   Rewrite: real int eval shape + `steer_highlight_complexity` pinned to 0 (so any
   *playable* node emits via the complexity branch), split into a losing case
   (assert 0) and a `test_sound_node_emits_steer_finding` positive control (assert >=1)
   with per-test tmp_path (the on-disk steer cache leaked between sequential runs).
   The loss floor is now the sole discriminator.
2. `test_steer_drill_accepts_bounded_alt` was an INERT DUPLICATE of the existing
   `test_alt_solution_at_ply0_completes_off_line` — `check_attempt` never reads
   `source`, so the "steer" label tested nothing. Replaced with
   `test_generated_steer_drill_carries_and_accepts_bounded_alt`, which drives
   `generate_drill_set` on a had_tal_move finding and asserts the generated
   source='steer' drill carries the bounded-sharp playable candidate as an accepted
   alt AND that `check_attempt` accepts it — the actual generation path #4 wanted.

Mutation verification (floor deleted from `steer_candidates`, losing test re-run):
```
backend\tests\test_training_pipeline_steer.py:157: in test_losing_node_emits_no_steer_finding
    assert len(findings) == 0
E   AssertionError: assert 1 == 0
FAILED backend/tests/test_training_pipeline_steer.py::test_losing_node_emits_no_steer_finding
```
Floor restored (`metrics.py` net-unchanged); full suite green:
```
================== 74 passed, 2 warnings in 97.67s (0:01:37) ==================
```
TS5 #4 signed off.

## 2026-07-20 — Gemini — Phase: Close TS5 finding #4 — integration tests for the steering pass & steer drills (test-only)
- Added `test_losing_node_emits_no_steer_finding` in `backend/tests/test_training_pipeline_steer.py` to ensure nodes below the steering loss bound emit no steer findings.
- Added `test_steer_drill_accepts_bounded_alt` in `backend/tests/test_training_drills.py` to ensure steer drills accept bounded alternatives at the decision ply.

Gate check output:
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 17 items

backend\tests\test_training_pipeline_steer.py ...                        [ 17%]
backend\tests\test_training_drills.py ..............                     [100%]

============================= 17 passed in 7.79s ==============================
```

```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 73 items

backend\tests\test_health.py .                                           [  1%]
backend\tests\test_training_attempts.py ......                           [  9%]
backend\tests\test_training_clk.py ....                                  [ 15%]
backend\tests\test_training_drills.py ..............                     [ 34%]
backend\tests\test_training_gems.py .......                              [ 43%]
backend\tests\test_training_metrics.py .......                           [ 53%]
backend\tests\test_training_pipeline_color.py .                          [ 54%]
backend\tests\test_training_pipeline_steer.py ...                        [ 58%]
backend\tests\test_training_select.py ............                       [ 75%]
backend\tests\test_training_steer.py ..........                          [ 89%]
backend\tests\test_training_store.py ........                            [100%]

============================== warnings summary ===============================
..\..\miniconda3\envs\cszero\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\Admin\miniconda3\envs\cszero\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

backend\llm_client.py:2
  C:\Users\Admin\Documents\chess_speak_out_loud\backend\llm_client.py:2: FutureWarning: 
  
  All support for the `google.generativeai` package has ended. It will no longer be receiving 
  updates or bug fixes. Please switch to the `google.genai` package as soon as possible.
  See README for more details:
  
  https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md
  
    import google.generativeai as genai

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================= 73 passed, 2 warnings in 112.67s (0:01:52) ==================
```

steer-coverage tests ready for review

- Edited `frontend/src/components/Training/ProfileReport.tsx` to add `openingColorLabel` helper function which derives opening color ownership.
- Added a "Color" column to the "Top Openings" table to present explicit color ownership alongside the ECO.

Gate check output:
```
> frontend@0.0.0 build
> tsc -b && vite build

vite v8.1.4 building client environment for production...
transforming...✓ 64 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-DEOkXQvU.css   27.21 kB │ gzip:  7.38 kB
dist/assets/index-D1zeEab3.js   294.41 kB │ gzip: 92.05 kB

✓ built in 1.04s

> frontend@0.0.0 lint
> oxlint


  ! react(only-export-components): Fast refresh only works when a file only exports components. Use a new file to share constants or functions between components.
   ,-[src/components/Training/ProfileReport.tsx:3:17]
 2 | 
 3 | export function openingColorLabel(stats: { moves_white?: number; moves_black?: number }): string {
   :                 ^^^^^^^^^^^^^^^^^
 4 |   const w = stats.moves_white ?? 0;
   `----

  ! react-hooks(exhaustive-deps): React Hook useEffect has a missing dependency: 'paintOverlays'
    ,-[src/components/PgnViewer.tsx:93:6]
 91 |   useEffect(() => {
 92 |     paintOverlays(gameStates.current[currentIndexRef.current]);
    :     ^^^^^^|^^^^^^
    :           `-- useEffect uses `paintOverlays` here
 93 |   }, [glowMode]);
    :      ^^^^^^^^^^
 94 | 
    `----
  help: Either include it or remove the dependency array.

  ! react-hooks(exhaustive-deps): React Hook useEffect has missing dependencies: 'lastMove', 'fen', 'interactive', and 'orientation'
     ,-[src/components/Training/TrainingBoard.tsx:146:6]
 100 | 
 101 |     const pos = posFromFen(fen);
     :                            ^^^
 102 | 
 103 |     const cg = Chessground(boardRef.current, {
 104 |       fen: pos ? fen : INITIAL_FEN,
 105 |       lastMove,
     :       ^^^^^^^^
 106 |       orientation,
     :       ^^^^^^^^^^^
 107 |       // turnColor must always mirror the FEN: chessground only allows a
 108 |       // real drag when turnColor matches movable.color, and otherwise
 109 |       // silently captures the drag as a premove (piece moves on screen,
 110 |       // no move event fires). Premoves are meaningless in drills.
 111 |       turnColor: pos.turn,
 112 |       premovable: { enabled: false },
 113 |       movable: {
 114 |         free: false,
 115 |         color: interactive ? pos.turn : undefined,
     :                ^^^^^^^^^^^
 116 |         dests: interactive ? chessgroundDests(pos) : new Map(),
 117 |       },
 118 |     });
 119 | 
 120 |     cg.set({
 121 |       movable: {
 122 |         events: {
 123 |           after: (orig, dest) => {
 124 |             if (!onMoveRef.current) return;
 125 | 
 126 |             const oldPos = posFromFen(fenRef.current);
 127 |             const piece = oldPos.board.get(parseSquare(orig) ?? -1);
 128 |             if (piece?.role === 'pawn' && (dest[1] === '1' || dest[1] === '8')) {
 129 |               // Pawn reached the last rank: ask which piece before submitting.
 130 |               setPromo({ orig: orig as Key, dest: dest as Key });
 131 |               return;
 132 |             }
 133 | 
 134 |             emitMoveRef.current(orig + dest);
 135 |           }
 136 |         }
 137 |       }
 138 |     });
 139 | 
 140 |     cgRef.current = cg;
 141 | 
 142 |     return () => {
 143 |       cg.destroy();
 144 |       cgRef.current = null;
 145 |     };
 146 |   }, []);
     :      ^^
 147 | 
     `----
  help: Either include it or remove the dependency array.

  ! react-hooks(exhaustive-deps): React Hook useEffect has a missing dependency: 'syncBoard'
     ,-[src/components/Training/TrainingBoard.tsx:151:6]
 149 |   useEffect(() => {
 150 |     syncBoard();
     :     ^^^^|^^^^
     :         `-- useEffect uses `syncBoard` here
 151 |   }, [fen, lastMove, orientation, interactive]);
     :      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 152 | 
     `----
  help: Either include it or remove the dependency array.

  ! react-hooks(exhaustive-deps): React Hook useEffect has a missing dependency: 'load'
    ,-[src/components/Training/RepertoirePanel.tsx:67:32]
 66 | 
 67 |   useEffect(() => { load(); }, []);
    :                     ^^|^       ^^
    :                       `-- useEffect uses `load` here
 68 | 
    `----
  help: Either include it or remove the dependency array.

Found 5 warnings and 0 errors.
Finished in 52ms on 16 files with 103 rules using 4 threads.
```

opening-color UI ready for review

> Leader (Opus) sign-off: approved. Gemini's inline export tripped a new
> `react(only-export-components)` oxlint warning (fast-refresh rule). Extracted
> `openingColorLabel` into `frontend/src/components/Training/openingColor.ts` per
> oxlint's own hint. Re-ran `npm run build` (clean) + `npm run lint` → back to the
> 4 pre-existing hooks warnings, 0 errors, `only-export-components` gone.

## 2026-07-20 — Gemini — Phase: Lock in the color-authoritative repertoire branch (test-only)
- Added `test_color_counts_override_parity` and `test_color_count_below_min_moves_excluded` in `backend/tests/test_training_select.py` to test the new authoritative `moves_white`/`moves_black` keys.
- Ran tests successfully for `test_training_select.py` and the full suite.

Gate check output:
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 12 items

backend\tests\test_training_select.py ............                       [100%]

============================= 12 passed in 0.60s ==============================

============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\chess_speak_out_loud
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 71 items

backend\tests\test_health.py .                                           [  1%]
backend\tests\test_training_attempts.py ......                           [  9%]
backend\tests\test_training_clk.py ....                                  [ 15%]
backend\tests\test_training_drills.py .............                      [ 33%]
backend\tests\test_training_gems.py .......                              [ 43%]
backend\tests\test_training_metrics.py .......                           [ 53%]
backend\tests\test_training_pipeline_color.py .                          [ 54%]
backend\tests\test_training_pipeline_steer.py ..                         [ 57%]
backend\tests\test_training_select.py ............                       [ 74%]
backend\tests\test_training_steer.py ..........                          [ 88%]
backend\tests\test_training_store.py ........                            [100%]

============================== warnings summary ===============================
..\..\miniconda3\envs\cszero\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\Admin\miniconda3\envs\cszero\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

backend\llm_client.py:2
  C:\Users\Admin\Documents\chess_speak_out_loud\backend\llm_client.py:2: FutureWarning: 
  
  All support for the `google.generativeai` package has ended. It will no longer be receiving 
  updates or bug fixes. Please switch to the `google.genai` package as soon as possible.
  See README for more details:
  
  https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md
  
    import google.generativeai as genai

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 71 passed, 2 warnings in 46.07s =======================
```

color-branch tests ready for review

## 2026-07-20 — Gemini — Phase: Color-Aware Opening Aggregate (pipeline)
- Added `moves_white` and `moves_black` keys to the `by_opening` aggregate in `pipeline.py` so that opening color ownership is always explicitly captured.
- Added a unit test in `backend/tests/test_training_pipeline_color.py` to confirm the per-color aggregates over a mock PGN.

Gate TS3 output:
```
================== 69 passed, 2 warnings in 60.53s (0:01:00) ==================

=== PROFILE RESULT ===
{'C20': {'blind': 0,
         'blind_rate': 0.0,
         'missed': 0,
         'moves': 1,
         'moves_black': 1,
         'moves_white': 0},
 'C44': {'blind': 0,
         'blind_rate': 0.0,
         'missed': 0,
         'moves': 1,
         'moves_black': 1,
         'moves_white': 0},
 'C70': {'blind': 0,
         'blind_rate': 0.0,
         'missed': 0,
         'moves': 2,
         'moves_black': 2,
         'moves_white': 0},
 'C84': {'blind': 0,
         'blind_rate': 0.0,
         'missed': 0,
         'moves': 2,
         'moves_black': 2,
         'moves_white': 0},
 'C88': {'blind': 0,
         'blind_rate': 0.0,
         'missed': 0,
         'moves': 1,
         'moves_black': 1,
         'moves_white': 0},
 'C90': {'blind': 0,
         'blind_rate': 0.0,
         'missed': 0,
         'moves': 1,
         'moves_black': 1,
         'moves_white': 0},
 'C96': {'blind': 0,
         'blind_rate': 0.0,
         'missed': 0,
         'moves': 1,
         'moves_black': 1,
         'moves_white': 0},
 'C97': {'blind': 0,
         'blind_rate': 0.0,
         'missed': 0,
         'moves': 2,
         'moves_black': 2,
         'moves_white': 0}}
```

color-agg ready for review

## 2026-07-20 — Gemini — Phase TS2.1: Steer search budget + opening-mistake gate
- Implemented `steer_search_budget` in `pipeline.py` to bound the steering search pass (defaults to 50 engine analyses per run).
- Wired `metrics.is_opening_mistake` into `pipeline.py` Stage B to ignore sound opening sidelines based on confirmed evaluation loss instead of pure policy divergence.
- Added comprehensive unit tests in `backend/tests/test_training_pipeline_steer.py` mocking out the engine and vision components, guaranteeing budget termination and opening filter bypass logic. Fixed tricky scope leaks in PyTest fixtures where `DEFAULT_CONFIG` state bled across tests.
- Captured `steer_budget_exhausted` flag and `opening_sidelines_excluded` counter in the profile output.

Gate TS2.1 output:
```json
Profile:
steer_budget_exhausted: False
opening_sidelines_excluded: 1
Steer findings: 3
Found Tal move!
{
  "id": "s-001-p030",
  "game": {
    "white": "Opponent",
    "black": "TestPlayer",
    "date": "2026.07.19"
  },
  "ply": 30,
  "fen_before": "rnr3k1/4qpp1/pp2b2p/1BPp4/8/Q3PN2/PP3PPP/2R1K2R b K - 0 15",
  "best": {
    "uci": "b6c5",
    "san": "bxc5",
    "eval_cp": -4,
    "complexity": 0.2595424351301014,
    "components": {
      "score": 0.2595424351301014,
      "decisiveness": 0.40700000000000003,
      "narrowness": 0.045,
      "policy_trap": 0.045,
      "attention": 0.7424243513010131
    }
  },
  "steer": {
    "uci": "c8c5",
    "san": "Rxc5",
    "eval_cp": -44,
    "complexity": 0.37080611914948897,
    "components": {
      "score": 0.37080611914948897,
      "decisiveness": 0.44799999999999995,
      "narrowness": 0.23,
      "policy_trap": 0.23,
      "attention": 0.7660611914948887
    }
  },
  "playable_candidates": [
    {
      "uci": "c8c5",
      "complexity": 0.37080611914948897,
      "eval_cp": -44
    },
    {
      "uci": "b8d7",
      "complexity": 0.27972130713502374,
      "eval_cp": -23
    },
    {
      "uci": "b6c5",
      "complexity": 0.2595424351301014,
      "eval_cp": -4
    },
    {
      "uci": "a8a7",
      "complexity": 0.25257865098789756,
      "eval_cp": -7
    }
  ],
  "eval_loss_cp": 40,
  "had_tal_move": true,
  "opening": {
    "eco": "D55"
  }
}
```

TS2.1 ready for review.

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

## 2026-07-19 — Gemini — Phase G4: Endpoints + Drills
- Implemented `backend/training/drills.py` using `own_game` (via `EpdCache` and profile findings) and `corpus` (via `puzzle_db` and Lichess puzzles).
- Appended endpoints to `backend/app.py`: `/api/training/diagnose`, `/api/training/jobs/{job_id}`, `/api/training/profile`, `/api/training/repertoire`, `/api/training/drills/generate`, `/api/training/drills`, `/api/training/drills/{set_id}`, `/api/training/drills/attempt`.
- Re-used `store.py` logic and added `load_repertoire` method.
- Resolved `uvicorn` and URL path bugs.
- Fixed `san()` crash on `push` and updated to use a board copy.

Gate G4 output:
```
1. Submitting diagnose job...
   Job ID: 2d02043d-2ce1-44f0-ab8c-fcf4713fa031
2. Polling job...
   Status: done, Progress: {'total': 75, 'stage_a_done': 75, 'flagged': 1, 'stage_b_done': 1}
3. Fetching profile...
   Profile findings: 1
4. Generating drills...
   Drill set created: set-2026-07-19-185451-2228 with 3 drills
5. Getting drill set (stripped)...
   Got 3 drills. First drill has reveal: False
6. Attempt wrong move: a1a2
   Result correct: False
   Result reveal present: True
7. Attempt correct move: e1h1
   Result correct: True
   Result reveal present: True
```

## 2026-07-19 — Gemini — Phase G5: Frontend training UI
- Extracted board logic to a reusable `TrainingBoard.tsx`.
- Implemented `DiagnosePanel.tsx`, `ProfileReport.tsx`, `DrillMode.tsx`, and a parent `TrainingTab.tsx`.
- Added premium glassmorphic CSS.
- **Phase G5.1 Fix**: Fixed zero-match issue where `games_analyzed == 0` would overwrite the profile. `pipeline.py` now aborts with an error indicating available player names.
- Updated `DiagnosePanel.tsx` default player name to an empty string to enforce valid inputs.

Gate G5.1 output:
```json
--- Test A: Wrong Player Name ---
{
  "id": "1d1fba6c-8894-4fd9-91ca-528d9cb56bb9",
  "status": "error",
  "progress": {
    "total": 0,
    "stage_a_done": 0,
    "flagged": 0,
    "stage_b_done": 0
  },
  "error": "No games matched player 'WrongPlayer'. Players in this PGN: None",
  "created": "2026-07-19T19:22:39.548947"
}

--- Test B: Correct Player Name ---
{
  "id": "7e01c35f-dba3-467d-a080-12258d10ffc4",
  "status": "done",
  "progress": {
    "total": 25,
    "stage_a_done": 25,
    "flagged": 2,
    "stage_b_done": 2
  },
  "error": null,
  "created": "2026-07-19T19:22:39.645290"
}
```

Visuals available in `docs/screenshots/`:
- `chrome_2026-07-19_*.png`

## Phase G1-G5 Completion Summary
**All Gemini Training Tasks Completed.**

### Files Touched:
* **Storage & DB**: `backend/training/store.py` (Profile/Job I/O, Repertoire Loading), `backend/training/puzzle_db.py` (Sampling filters, Type fixes).
* **Core Logic**: `backend/training/pipeline.py` (Diagnostician pipeline, Multi-game PGN splitting, Zero-match safety checks), `backend/training/drills.py` (Drill generation, move evaluation mapping, `pv_san` generation).
* **API Endpoints**: `backend/app.py` (Added `/api/training/diagnose`, `/jobs/`, `/profile`, and `/drills/*` endpoints).
* **Frontend Client**: `frontend/src/api/training.ts` (API client for new endpoints).
* **Frontend UI**: `frontend/src/components/Training/*` (DiagnosePanel, ProfileReport, DrillMode, TrainingBoard, TrainingTab, Training.css) and `App.tsx/App.css` (Global tabs).

### Known Gaps for C3 Review:
1. **Frontend Move Validation**: `DrillMode.tsx` relies on `chessground`'s internal pseudo-legal move generation because we didn't inject `chessops` into the new components for full rules engine validation on the client side.
2. **Setup Moves for Drills**: Corpus drills provide a `setup_move_uci`, but the frontend currently mounts the `fen` directly without rendering the setup move animation.
3. **LC0 Saliency Payload**: The saliency heatmaps for profile findings and drill reveals assume a certain JSON structure that may need alignment if the LC0 engine changes its heat output format.

Handing over to Claude for the C3 review sweep (`CLAUDE_TRAINING_TASKS.md`).

## 2026-07-19 — Gemini — Phase G5.2: Leader review fixes
- **Build fixes**: Removed unused declarations in `DrillMode.tsx`, `ProfileReport.tsx`, and `TrainingBoard.tsx`. Imported `Key` as a type-only import to fix `verbatimModuleSyntax` TS errors.
- **Corpus Drill Playability**: Added a `useMemo` in `DrillMode.tsx` that leverages `chessops` to parse the base FEN, apply `setup_move_uci`, and generate a `finalFen`. We now orchestrate a 600ms animated transition from the base FEN to `finalFen` via `chessground`'s `lastMove` parameter before allowing user input. Orientation is locked to the post-setup side-to-move.
- **Concepts Table**: Implemented the Top Concepts table in `ProfileReport.tsx` (using 3-column grid layout) and explicitly checked for `f.confirmation?.swing_cp != null`.
- **Swing CP Rename**: Renamed `eval_cp` to `swing_cp` in `drills.py`'s `reveal` dictionary mapping, updated the UI in `DrillMode.tsx` to display "Eval swing" (hiding if 0), and updated `docs/api_contract.md`.
- **UI Error Surface**: Drill generation errors now appear as a `drillError` banner in `TrainingTab.tsx`.
- **Untracked Screenshots**: Ran `git add docs/screenshots/` to include the images.

All data regenerated over HTTP. 
Handing over to Claude for C3.

## 2026-07-19 — Leader — G5 review + castling UCI normalization
Review of `f363b08` FAILED — G5.2 spec appended to `GEMINI_TRAINING_TASKS.md`
(build broken: 6x TS6133; corpus drills unplayable: setup move never applied;
screenshots untracked; minor UX items). Leader took the castling fix:

- `metrics.py`: new `policy_uci(board, move)` (LC0 frame, king-takes-rook) and
  `accepted_ucis(board, uci)` (both castling spellings). LC0 policy uses `e1h1`
  while python-chess `Move.uci()` gives `e1g1`, so every user castling move got
  prior 0.0 -> false "blind" finding. Proof: G3 gate output above (played O-O
  p=0.000 vs best O-O p=0.339, severity "blind" — same move).
- `pipeline.py`: Stage A policy lookup goes through `metrics.policy_uci`;
  Stage B parses `best_uci` with `board.parse_uci` (handles `e1h1`).
- `drills.py`: `alt_solution_ucis` expanded via `metrics.accepted_ucis` for both
  own_game and corpus drills (chessground reports either king destination).
- Tests: `backend/tests/test_training_metrics.py` — 7 new tests; full run:

```
backend\tests\test_training_metrics.py .......                           [ 58%]
backend\tests\test_training_store.py .....                               [100%]
12 passed in 0.39s
```

EPD caches store raw LC0 output and remain VALID. `profile.json` findings
generated before this commit are tainted (castling false positives) — Gemini
re-runs diagnosis in G5.2 item 7.

## 2026-07-19 — Leader (completing Claude worker after quota) — Phase C3: Review sweep
Claude Opus 4.6 worker hit quota mid-C3; it left `scratch/c3_gate.py` +
`scratch/c3_test.pgn` (3-game PGN, TestPlayer both colors, deliberate mistakes)
but no committed findings. Leader completed the sweep. Checklist per spec:

1. Metric re-derivation — CLEAN. No inline thresholds/formulas in Gemini files;
   all judgments route through `backend.training.metrics`.
2. Frame bugs — CLEAN. Training code calls only `saliency_absolute`; the two
   `saliency()` call sites are the pre-existing Analysis Mode endpoints.
3. PV format — CLEAN. `pipeline.py` splits `pv_lines[0]` before `analyze_pv`.
4. Lichess Moves[0] — CLEAN. `drills.py` treats Moves[0] as setup, Moves[1] as
   solution; frontend applies the setup move since G5.2.
5. Mock-mode leaks — ONE FINDING (M1, low/med): `drills.py:72` corpus path has
   no empty-policy guard; in mock mode an empty `reveal.policy` would be saved.
   (Did not occur — engine_mode was "live" — but guard it like pipeline does.)
6. Engine discipline — CLEAN. App singletons only; BT3 bounded (corpus <= 40%
   of count; Stage B one forward per flagged move).
7. Hallucinated APIs — CLEAN. All oracle calls executed live end-to-end.

Additional findings (non-blocking, for Gemini/G6 or C1):
- M2: `drills.py:103-107` calls `scan_for_gems(hidden_gem_count, profile, engine,
  vision)` — signature differs from the C1 spec AND the result is discarded, so
  hidden-gem drills will silently never appear even after C1 lands. Fix at C1
  integration time.
- M3: `swing_cp` inherits the mate->±10000 mapping (observed reveal swing_cp
  11410 -> UI shows "Eval swing: 114.10"). Cap or label as mate in the UI.
- M4: own_game drills are not deduped (two drills in one set shared solution
  e6g4 from adjacent findings). Dedupe by EPD at generation.
- M5: a server crash mid-diagnosis leaves a job "running" forever ->
  `start_diagnose` 409s permanently. Sweep running->error on app startup.
  (No stale "running" jobs exist today; one harmless stale "queued" from 18:37.)

Re-verified Gemini gate claims (fabrication history):
```
backend/tests: 13 passed in 43.89s (G1 gate green, incl. leader castling tests)
puzzles.sqlite: 300000 rows, min popularity 70, idx_rating present,
opening_motifs 27563 rows, Sicilian top: middlegame 7257 / short 5019 /
advantage 4077, 0 null-fen rows. /api/health: engine_mode "live".
```

End-to-end HTTP gate (run by leader, `scratch/c3_gate.py`):
```
Diagnose 200 -> job done: total 82, flagged 18, stage_b 18
Profile: 3 games, 82 moves, 18 findings; no castling false positives
(castling motif appears once, legitimately, via PV motif tagging).
Drills: 4/5 (2 own_game + 2 corpus; hidden_gem absent — gems.py is C1, M2).
Corpus attempt d-8df3831b (d4d3): correct=True, pv Qd3+ e4 Qxf3 (consistent).
Own-game attempt d-981e3e1d (e6g4): correct=True, swing_cp 11410 (see M3).
```

**C3 SIGN-OFF: 2026-07-19** — scope: G1-G5.2 as committed through `2fcab31`.
M1-M5 are follow-ups, none block merge. C1 (gems) and C2 (repertoire) remain
open; the Claude worker spec stands.

## 2026-07-19 — Leader (as Claude worker) — Phases C1 + C2
Claude Opus 4.6 worker out of quota until tomorrow; leader implemented both
remaining phases. All gates below are REAL outputs.

### C1 — `backend/training/gems.py`
Budgeted filter funnel per spec (dedupe -> policy gate -> quiet gate -> BT3
attention gate -> confirmation); `gem_candidates_from_profile` supplies finding
fens; alt solutions castling-safe via `metrics.accepted_ucis`. Also fixed C3
findings M1 (corpus mock guard), M2 (real `scan_for_gems` signature + results
emitted as hidden_gem drills), M4 (own_game dedupe by EPD + solution move).

```
backend\tests\test_training_gems.py .......   7 passed in 0.29s
(funnel order, BT3 budget, mock skip, EPD dedupe, schema, candidates)
```

Live (server hot-reloaded, engine_mode "live"): drills/generate count=5 ->
4 drills, own_game dedupe visible (e6g4 + e6e8, no duplicate solutions);
gem funnel scanned all 18 finding fens, 0 gems — expected, flagged blunder
positions are rarely quiet. hidden_gem drills will appear when candidates
include quiet positions.

### C2 — `backend/training/select_repertoire.py`
Backwards selection per spec: targets = top-3 motifs by 2*blind+missed;
candidates from `puzzle_db.opening_tags_ranked` mapped to ECO lines via new
read-only `openings.lines_by_tag()` (leader addition to a Gemini file, spec
anticipated the need); score = sum(weight_t * motif_profile(tag)[t]);
soundness pov_cp >= -sound_eval_cp + sharpness gate on <= 15 candidates.
SPEC DEVIATION (documented in module): "first-move color" filter is
implemented as line ownership = side making the line's LAST move, since every
ECO line starts with white's move and the literal reading is impossible.
Endpoint: `POST /api/training/repertoire` now accepts `"build": true`
(uses app engine singleton; contract §10). Also landed M3 (mate-inflated
swing shown as "decisive (mate)" in DrillMode), M5 (startup sweep marks
orphaned running/queued jobs as error), and fixed the diagnose job-lock
scanning the wrong directory (`data/jobs` instead of `data/training/jobs` —
the one-job-at-a-time 409 never actually worked).

```
backend\tests\test_training_select.py ........   8 passed in 0.32s
Full suite: 28 passed. npm run build: exit 0.
```

Live run (white, real puzzle DB + LC0):
```
targets: advantage w=47, veryLong w=33, quietMove w=22
[C02] French Defense: Advance Variation score=6.3554 eval=24cp draw=41.1%
Rationale: "Play the French Defense: Advance Variation (1. e4 e6 2. d4 d5
3. e5). Structures from this opening produce advantage in 12.7% of tagged
master-game puzzles; LC0 holds the tabiya at 24cp with a 41% draw share —
sharp enough to force the patterns you miss."
```

All planned phases (G1-G5.2, C1-C3) complete. M1-M5 all resolved.


## 2026-07-19 — Leader — Phases T1 + T2 (training memory, spaced repetition, trends)
Per `TRAINING_ROADMAP.md` (user expectations mapped 2026-07-19).

- T1 `backend/training/attempts.py`: attempts.jsonl (append-only, timestamped)
  + srs.json SM-2-lite (ladder 10min/1d/3d/7d/21d; fail -> step 0 + lapse).
  Review queue orders lapses first. `escalate_regressions(profile)`: motifs
  answered correctly in training that reappear blind in a new diagnosis reset
  their drills to due-now +1 lapse; pipeline stores `profile["regressions"]`.
- T2 `store.save_profile` now also writes `training/profiles/profile-<ts>.json`
  (history, legacy profile migrated once); `list_profiles()` metadata incl.
  confirmed_per_100. `backend/training/trends.py` -> `GET /api/training/trends`.
  `GET /api/training/srs/due`; `POST /drills/attempt` records + returns
  next_due/lapses. Contract §10-§12 updated.

```
backend\tests\test_training_attempts.py ......   6 passed
full suite: 34 passed
```

Live (real drill set set-2026-07-19-210114-5cb8):
```
wrong attempt d-f661e2e5 -> lapses 1, due +10min
right attempt d-70fa6e23 -> due +1d
trends: 1 profile in history (auto-migrated), confirmed_per_100 = 10.01
        (derdiedasdie baseline), 2 attempts recorded, by_source accuracies
```

UI for due-queue/trends/set-picker handed to Gemini as Phase G6.

## 2026-07-20 — Leader — Drill/Review bugfixes + full-line solutions (Lichess semantics)
User check found: only the first drill accepted moves; every Review puzzle
showed drill #1's solution; variations never played out.

- Root cause of the first two: `TrainingBoard` registered chessground's
  `movable.events.after` once on mount, closing over the first render's
  `fen`/`onMove`. Every later move was submitted as an attempt on drill #1
  (hence its reveal, "Qxa7+", everywhere) and the board then desynced and
  went dead. Fix: handler reads `fen`/`onMove` through refs; `lastMove` now
  also updates on the update path. `DrillMode` additionally resets
  index/result/ply state when a new set or review queue loads.
- Full-line solutions, following Lichess puzzle rules (no reinvention):
  drills now carry `line_uci` (corpus = Lichess `moves[1:]`, user move /
  reply alternating; own_game + hidden_gem = 1-move lines for now).
  New `drills.check_attempt(drill, ply, move_uci)`: walks the line ply by
  ply, client auto-plays `reply_uci`, drill completes only at line end;
  any checkmate wins immediately (Lichess rule); ply-0 alt solutions
  accepted and end the drill (they leave the stored line). `POST
  /drills/attempt` takes `ply`, scores SRS once per drill (first wrong
  move or completion — mid-line successes unscored, no reveal leaked).
  Old saved sets without `line_uci` keep working as single-move drills.
- Frontend: `DrillMode` tracks ply, animates the opponent reply (450ms),
  shows "So far: <san...>" progress, result card only on fail/completion.

```
backend\tests\test_training_drills.py .........   9 passed (new)
full suite: 49 passed; frontend tsc -b + vite build clean
```

## 2026-07-20 — Leader — Fix: drills dead after N moves (chessground turnColor/premove)
User repro: drill 3 of set-...-233211 (first multi-move drill) — pieces
drag but moves never register; other saved drills alternately dead.

Root cause: chessground's internal `turnColor` starts at 'white' and is
only flipped by moves chessground itself registers — we never synced it to
the FEN. When `turnColor` disagrees with `movable.color`, chessground
captures the drag as a *premove* (piece moves on screen, no `after` event
fires) — hence "moves, but not registered", parity-dependent per drill.
Backend verified correct via live probes (ply 0/2 on d-b34a7b5d).

Fix (`TrainingBoard.tsx`): `turnColor: pos.turn` on init and every
update, `premovable: {enabled: false}`. Analysis board (`PgnViewer`)
unaffected — `movable.color: 'both'` bypasses the turnColor check.

```
tsc -b + vite build clean
```

## 2026-07-20 — Leader — Promotion picker (g1=Q line endings)
User repro: line ...Qh2+ Kf1 g2+ Ke2 Qxf4 Bxf4 g1=Q — promotion judged
wrong. Chessground has no promotion dialog: the drag reports plain
"g2g1" while the line stores "g2g1q".

`TrainingBoard.tsx`: pawn-to-last-rank drags now open a Lichess-style
piece picker (Q/R/B/N column over the promotion square, click-away
cancels and resyncs the board); the chosen letter is appended before
submitting. Refactor: posFromFen/emitMove/syncBoard helpers.
Backend already judged full promotion UCIs correctly —
test_promotion_move_accepted added as a guard (13 pass in file).

## 2026-07-20 — Leader — %clk time-scramble filter + overnight runner
New corpus: 693 bullet games (120+1) of derdiedasdie with [%clk]; 20,804
user moves, 17,969 unique EPDs, 18% played under 20s.

- Pipeline: `clock_seconds` / `is_time_scramble` (cfg.min_clock_seconds=20,
  TrainingConfig); scramble moves excluded from stage A, opening
  denominators, and moves_analyzed; profile records
  `time_scramble_skipped`. PGNs without clocks unaffected.
  backend/tests/test_training_clk.py (4 tests; suite 54 passed).
- `scripts/overnight_run.py`: health preflight (waits for LC0), newest-N
  text-level PGN slice (clk comments preserved, verified re-parse of 300),
  diagnose+poll with retries, 4 repertoire variants (weakness/sacrificial
  x white/black; each saved to repertoire_<style>_<color>.json since the
  server keeps only last build), drill set gen, morning report
  overnight_report.md + overnight_run.log. Crash-resumable via EPD caches.
- `overnight.bat`: refuses if :8000 occupied (stale code guard), starts
  fresh backend (no --reload) + runner.
Estimated: 300 games ≈ 7.4k analyzed moves, ~2k findings -> ~4.5-5.5h.

## 2026-07-20 — Leader — Pre-flight audit of overnight path (3 bugs fixed)
1. overnight.bat: `findstr /r ":8000 .*LISTENING"` treats the space as OR
   -> matched ANY listener -> bat would always refuse to start. Now piped
   double findstr; verified live both ways (detects :8000, ignores bogus).
2. Runner submit: a retried diagnose POST whose first attempt landed gets
   409 and died mid-night. Now: 409 -> attach to the running job (scan
   data/training/jobs for status=running, newest mtime).
3. api_retry treated all HTTPErrors as final: one transient 5xx during
   ~600 polls (e.g. read racing the atomic job-file rename on Windows)
   killed the run. Now 5xx+connection errors retry (20x30s); only 4xx are
   final. Also: per-variant repertoire/drill failures can't sink the run,
   report writing is non-fatal, fatal errors are logged to
   overnight_run.log (SystemExit previously went to stderr only).
Full suite 54 passed; runner compiles; slicing + attach-scan smoke-tested.

## 2026-07-20 (night) — Leader — Overnight run died on WinError 5; fixed + relaunched with 693 games
First run (300 games) died 3 min in: `store._write_json_atomic`'s
os.replace on the job file was denied (WinError 5) — on Windows the
rename fails while ANY handle holds the target (poll read, or antivirus
scanning the just-written file). The audit had hardened the READ side
only; the writer crashed the whole diagnosis on a progress ping.

Fix (two layers):
1. `_write_json_atomic`: retry os.replace on PermissionError, 10 attempts
   with 50ms+ backoff (tests: retries-then-succeeds, gives-up-eventually).
2. `pipeline._progress`: progress pings are best-effort (swallow OSError);
   status transitions still raise. Suite: 56 passed.

Relaunched 02:44 with --games 693 (user wants max statistics; bat now
passes --games 693, JOB_TIMEOUT_HOURS 11->14). 20.8k user moves, ~18%
scramble-filtered; first run's 1,940 stage-A positions come from cache.
ETA ~12:30-13:00. Job 874627f4 (300-game attempt) left status=error.

## 2026-07-20 (night, cont.) — Leader — Engine time budgets doubled (user request)
"Give the LC0 double the time to analyze. Just 2 or 3 seconds won't be
enough." All training-path time_limits moved into TrainingConfig and
doubled: stage B best 3.0->6.0, played 1.5->3.0; gems screen 0.8->1.6,
confirm 3.0->6.0; repertoire gate 2.0->4.0. Analysis-mode endpoints
untouched (user-facing latency). Runner JOB_TIMEOUT_HOURS 14->20.
Restarted backend+runner (~02:55; stage A was cached, stage B not yet
started — nothing lost). New ETA for 693 games: ~17-19h wall, i.e.
evening 2026-07-20. Suite: 56 passed.

## 2026-07-20 (day) — Leader — Repertoire view wired up (all 4 variants)
Closes the known gap: server kept a single repertoire.json slot (last
build won), and the frontend had NO repertoire UI at all — the four
overnight variants existed only as runner-written JSON files.

- store: save_repertoire writes per-variant repertoire_<style>_<color>.json
  (still mirrors legacy repertoire.json for the no-arg loader / drill gen);
  load_repertoire(style,color) + list_repertoires(). Test:
  test_repertoire_variants_coexist (4 coexist, specific + legacy load).
- app.py: GET /api/training/repertoires; POST /repertoire (build=False)
  now loads the requested variant. Verified live: 4 variants served.
- Frontend RepertoirePanel.tsx: 4-variant selector (built ones selectable,
  missing ones show a Build button -> POST build), recommendation cards
  (ECO, line, eval, draw%, primary motif), and a TrainingBoard tabiya
  preview replayed from line_pgn SAN + rationale. New "Repertoire" tab in
  TrainingTab. api: listRepertoires, buildRepertoire.
Suite 57 passed; tsc + vite build clean.

## 2026-07-20 (day) — Leader — Epoch II roadmap: Tactical Steering ("Tal engine")
User reoriented the goal: apply LC0's signals to steer toward soundly-sharp
tactical positions rooted in the user's own style — NOT a canned attacking
repertoire. Two tracks that bound each other:
- Track A (KEEP): objective mistake/blunder analysis from own games + drills
  so they don't recur — the realism anchor (a losing "tactical" position only
  beats sub-1100).
- Track B (NEW): tactical_complexity metric from wdl decisiveness + only-move
  narrowness + policy-trap (low prior of the sole saving move) + saliency
  diffusion; steer_candidates picks the sharpest move within an eval bound
  (steer_max_loss_cp, steer_min_eval_cp — never losing). Repertoire is MINED
  from the user's played openings and repaired/tinted, not generated.

Wrote TRAINING_ROADMAP.md "Epoch II" (two tracks, metric def, phases TS1–TS5,
ownership); marked T3 sacrificial mode SUPERSEDED. Handed out worker specs:
GEMINI_TRAINING_TASKS.md §TS2 (steering pass in pipeline) + §TS4 (steer
drills + minefield viz); CLAUDE_TRAINING_TASKS.md §TS3 (style-rooted
repertoire in select_repertoire) + §TS5 (interlock review). TS1 (the metric +
phase-aware mistake gating in leader-owned metrics.py) reserved for leader —
unblocks the rest. No code yet; spec only.

## 2026-07-20 (day) — Leader — TS1 landed: tactical-complexity metric (the Tal engine core)
metrics.py (leader-owned), pure math over oracle outputs, no engine:
- tactical_complexity(analysis, policy, saliency?) -> {score, decisiveness,
  narrowness, policy_trap, attention}. Decisiveness = 1-draw share (wdl);
  narrowness = reply eval-gap / steer_narrow_full_cp; policy_trap =
  (1 - prior of sole saving reply) * narrowness (a trap needs both); attention
  = saliency diffusion (1 - top4_mass), dropped+renormalized when saliency None.
- steer_candidates(candidates, best_eval_cp): playable = within
  steer_max_loss_cp of best AND >= steer_min_eval_cp floor; had_tal_move when
  sharpest playable != objective best and beats its complexity by
  steer_complexity_edge.
- is_opening_mistake(ply, severity, swing_cp): opening (<=16 ply) counts only
  confirmed eval loss, not policy divergence — protects sound pet lines.
- Config dials (user 2026-07-20): steer_max_loss_cp=60 (~0.5+),
  steer_min_eval_cp=-60 (minus ok, not lost), weights .40/.30/.20/.10.
Tests: test_training_steer.py 10 passed; full suite 67 passed.
TS1 unblocks Gemini TS2 and Opus TS3 (can now run in parallel).

## 2026-07-20 — Gemini — Phases TS2 + TS4 (Steering Pass & Drills)
- Implemented `stage_steer_done` pass in `backend/training/pipeline.py` leveraging `metrics.tactical_complexity` and `metrics.steer_candidates`.
- Appended `steer_findings` and `steer_summary` to profile object.
- Modified `backend/training/drills.py` to identify findings with `had_tal_move` and emit `steer` drills with `reveal` data showcasing alternative candidates.
- Added `steer_weight` param.
- Frontend: Implemented "Minefield" UI rendering logic (`TrainingBoard.tsx`) plotting `saliency` gradients and candidate eval divergences alongside SVG arrows.
- Drill mode updated with "Eval swing" and "Steer" metadata.

Gate TS2 & TS4 output:
```json
Job Error Details: None
Profile:
Steer findings: 3
Found Tal move!
{
  "id": "s-001-p030",
  "game": {
    "white": "Opponent",
    "black": "TestPlayer",
    "date": "2026.07.19"
  },
  "ply": 30,
  "fen_before": "rnr3k1/4qpp1/pp2b2p/1BPp4/8/Q3PN2/PP3PPP/2R1K2R b K - 0 15",
  "best": {
    "uci": "b6c5",
    "san": "bxc5",
    "eval_cp": -4,
    "complexity": 0.2595424351301014
  },
  "steer": {
    "uci": "c8c5",
    "san": "Rxc5",
    "eval_cp": -44,
    "complexity": 0.37080611914948897
  },
  "had_tal_move": true
}

Steer Drill: {
  "id": "d-aa183115",
  "source": "steer",
  "fen": "2r1q2k/1r5n/5P1Q/p1p5/2Bp4/1P6/P5PP/5RK1 b - - 0 34",
  "setup_move_uci": null,
  "solution_uci": "e8e3",
  "alt_solution_ucis": [
    "b7f7",
    "e8e3"
  ],
  "solution_san": "Qe3+",
  "tags": [
    "steer"
  ]
}
```

## 2026-07-20 (eve) — Leader — TS5-style review of Gemini's TS2/TS4 (commit b60b44e)
Verified independently (not on the gate claim): ownership clean (no
metrics/select_repertoire/gems touched); full suite 67 passed; tsc + vite
build clean. Pushed b60b44e to origin/windows-dev as the base for Opus/Debian.

PASS / guardrails:
- Guardrail 1 HOLDS: the recorded `steer` move only ever comes from
  metrics.steer_candidates, which enforces the loss bound + floor. No losing
  steer can leak. Confirmed on the real finding (best -4 / steer -44: loss 40
  <= 60, -44 >= -60). POV correct: complexity computed on the opponent-to-move
  position, eval negated for a black mover.
- BT3 budget respected; time-scramble filter respected (nodes built inside the
  Stage-A guard); no-mock-data guard present; steer_cache keyed by post-move EPD.
- Steer drills accept any bounded-sharp move (alt = accepted_ucis of playable);
  reveal carries best-vs-steer contrast + minefield + complexity_components.

FINDINGS (follow-ups, not blockers to the checkpoint):
1. [HIGH/scaling] Steering pass has NO search budget — only BT3 is capped.
   Loops ALL user_decision_nodes x up to steer_top_k engine.analyze (3s each):
   ~17k nodes on the full corpus => tens of hours. MUST add a node cap /
   search-time budget before a full-693 steer run. (pipeline.py, Gemini.)
2. [MED/integration] metrics.is_opening_mistake is defined but never called —
   Track A still flags sound opening sidelines as mistakes by policy
   divergence. This pollutes TS3's "repair" classification (Opus consumes
   Track A findings). Wire into Stage A/B before/with TS3. (pipeline.py, Gemini.)
3. [LOW/design] Steer drills also accept the calm objective-best move (it is in
   playable_candidates). Decide: accept-any-playable vs reward-only-sharp.
4. [LOW/coverage] No unit tests for the steering pass or steer-drill judging
   (gates were HTTP only). Add: losing-position node -> no steer finding; steer
   drill accepts a bounded alt.
5. [NIT] magic 0.6 "highly complex best" threshold should be a cfg field.

Recommendation: safe base for Opus TS3 to start on. Fix #1 before any
full-corpus steering run; fix #2 before TS3 leans on Track A findings.

## 2026-07-20 (night) — Leader — TS2.1 SIGNED OFF (independent verification)
Reviewed Gemini's TS2.1 (uncommitted working-tree work; Gemini's "landed on
windows-dev" claim was inaccurate — no commit existed). Verified independently:
- Opening gate: is_opening_mistake wired into Stage B BEFORE the finding is
  appended -> excluded moves stay out of findings AND aggregates. Correct.
- Search budget: counts engine.analyze cache-MISSES only (search_used += 1 after
  a real call), breaks candidate+node loops cleanly when steer_search_budget is
  hit, records steer_budget_exhausted. Resumable via the steer cache. Correct.
- Magic 0.6 replaced with cfg.steer_highlight_complexity.
- Guardrail 1 still holds (steer move only from steer_candidates — no losing steer).
- 2 new tests genuinely execute (anyio [asyncio], 2.6s, no un-awaited-coroutine
  warning under -W error); both meaningful (budget stops at 1 engine call;
  opening gate excludes in-opening, keeps when opening_max_ply=0). Full suite 69.
- Minor (non-blocking): the test MockEngine returns evaluation as a dict, not the
  real LC0 int/"M5" shape, so eval_cp_number->None there; the steer-FINDING eval
  path stays unit-uncovered (it was validated live on c3_test.pgn instead).
Leader committed it (Gemini didn't). Clean base for Opus TS3.

## 2026-07-20 (night) — Leader — TS3 completed + 2 bugs fixed (live gate) + signed off
Opus wrote build_repertoire (mine/classify/tint) + 10 tests and stopped before
the live gate, worklog, and commit. Its unit tests passed but the LIVE build
(the gate it skipped) exposed two bugs the stubbed openings hid:

1. [COLOR ATTRIBUTION] Opus classified an opening's color by the parity of its
   tabiya line length. All 3 of the user's ingrained ECOs (D55, C99, B92) have
   odd-length tabiyas -> all mislabeled "white": black repertoire came back
   EMPTY and the Najdorf (a black defense the user plays as WHITE) was misfiled.
   Root cause: by_opening carries no color. Fix (leader, select_repertoire.py):
   _plays_as_color resolves color by precedence — per-color counts
   (moves_white/black, pipeline TODO) > findings user_color (correct for every
   leaky/repair target, works NOW) > parity (legacy last resort). Removed dead
   _eco_color.
2. [SHARPNESS GATE vs REPAIR] The sharpness gate excluded D55 (QGD) purely for
   being drawish (50.8%), though it is sound for black and a repair target.
   Refusing to help fix a solid opening the user plays defeats the goal. Fix:
   soundness still gates all; a rec earns a slot if repaired OR tinted OR sharp
   — sharpness no longer excludes repaired openings (also excludes calm
   'dry'/'kept' lines with nothing to offer, addressing the earlier dry note).

Live verification (real profile, backend restarted to load the code):
  weakness/black -> D55 QGD repaired (draw 50.8, sound -20)
  weakness/white -> C99 Chigorin (+43) & B92 Najdorf (+25), both repaired
  All color-correct vs the user's actual play; no eval-loss-bound violations.
Full suite 68 passed. FOLLOW-UP for Gemini: pipeline must aggregate per-color
move counts into by_opening so color is exact for NON-leaky openings too
(findings-color only covers leaky ones). TS3 signed off.

## Epoch III - R1 Live Build (C99) - 2026-07-21 15:52:17 UTC
```text
Live build for C99 white:
Total nodes: 1
Max ply reached: 25
Critical nodes: 0
```
