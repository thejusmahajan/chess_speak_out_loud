# GEMINI WORKER SPEC — "Calculation Glow" (aggregated deep-search attention)

> **You are Gemini, the implementation worker. Claude is driving and will verify every step.**
> Discipline: **verify before coding, no invented APIs, run the build/tests, report honestly, stop
> on failure.** This touches the backend (`neural_vision.py`, `engine_manager.py`, `app.py`) and the
> frontend (`PgnViewer.tsx`). **Do not touch the event-loop code in `engine_manager.py` (the
> `_ensure_loop`/`_submit`/ProactorEventLoop machinery) — only ADD methods. Do not re-enable the
> LLM.**

---

## THE IDEA (what we're building and what we are NOT building)

Today the board shows **Intuition Glow**: BT3's attention on the *current* position — what the net
"sees at first glance." We want a second mode, **Calculation Glow**: where the engine's *deep search*
is focused. When LC0 finds a forced sequence on the queenside, the glow should shift to the
queenside.

**Be precise about what is technically possible (do NOT try to exceed this):**

- ❌ We **cannot** hook LC0's internal MCTS and read the thousands of leaf positions it visits. UCI
  does not expose them. Do not try to parse a search tree out of `lc0.exe`. If you go looking for a
  "get me all visited nodes" API, **it does not exist** — stop.
- ✅ We **can** get, from a real timed search: the top **principal variations (PVs)** — the concrete
  lines LC0 considers best — via `engine.analyse(..., multipv=N)`, and the root move visit
  distribution via `VerboseMoveStats`.
- ✅ We **can** compute BT3 attention for **any** position (`NeuralVision._attention_saliency(fen)`).

**So "Calculation Glow" = aggregate BT3 attention over the future positions along LC0's top PVs,
weighted by line strength and decayed by depth.** This is a faithful *approximation* of "where the
search is looking," not a literal readout of the MCTS tree. Describe it that way; do not oversell it.

**Scope for THIS task = a synchronous, on-demand snapshot** (user clicks → ~10–15s → glow updates).
Real-time streaming of the glow as the search deepens is a *future* phase (see the last section) —
**do not build streaming/WebSockets now.**

---

## HARD CONSTRAINTS YOU MUST DESIGN AROUND (measured, not guessed)

1. **One BT3 forward pass ≈ 1.5s on CPU.** Therefore you MUST cap the number of positions evaluated.
   Use **`MAX_POSITIONS = 8`**. Never evaluate more than that per request. Expected latency ~10–15s;
   that is acceptable for an explicit button. Do NOT call this on every move.

2. **ORIENTATION IS NOT OPTIONAL. (This is the #1 way this feature silently produces garbage.)**
   `_attention_saliency(fen)` returns a correct absolute-square map **only for white-to-move
   positions.** For a **black-to-move** position it returns the map in the *flipped* (side-to-move)
   frame, mislabeled as absolute. Verified empirically: feeding a black-to-move board directly vs.
   normalizing it differs by ~0.10 mean per-square (large). Since PV positions alternate turn every
   ply, you MUST normalize every position to a white-to-move frame before aggregating, or a queenside
   line will smear onto the kingside. The required normalization is specified below — implement it
   exactly and verify it.

3. **BT3 forwards are synchronous torch/CPU.** Run the whole aggregation off the server event loop
   with `await asyncio.to_thread(...)` so it doesn't freeze the app.

---

## BACKEND EDIT 1 — `backend/neural_vision.py`: orientation-correct + aggregation

Add a module-level constant near the top (after imports):

```python
import chess  # add if not already imported
```

Add these three methods to the `NeuralVision` class (do not modify the existing
`_attention_saliency` — you are adding around it):

```python
    def _saliency_absolute(self, board: "chess.Board") -> dict[str, float]:
        """
        BT3 attention for `board`, always keyed by TRUE absolute squares.

        _attention_saliency is only correct for white-to-move positions. For
        black-to-move positions LC0/BT3 works in the flipped side-to-move frame,
        so we evaluate the vertically-mirrored (white-to-move) board and flip the
        square keys back (rank r -> 9-r). Verified against the white-to-move map.
        """
        if board.turn == chess.WHITE:
            return self._attention_saliency(board.fen())
        mirrored = board.mirror()  # swaps colors + flips ranks -> white to move
        s = self._attention_saliency(mirrored.fen())
        return {sq[0] + str(9 - int(sq[1])): v for sq, v in s.items()}

    def calculation_saliency(
        self,
        root_board: "chess.Board",
        lines: list[dict],
        max_positions: int = 8,
        decay: float = 0.85,
    ) -> dict[str, float]:
        """
        Aggregate absolute-frame BT3 attention over the future positions along the
        engine's top PV lines. `lines` = [{"moves": [chess.Move, ...], "weight": float}, ...].
        Weighting: line weight * decay**ply. Deduplicates positions. Caps at
        max_positions total BT3 forwards (each ~1.5s). Returns a [0,1]-normalized map.
        """
        agg = {sq: 0.0 for sq in chess.SQUARE_NAMES}
        total_w = 0.0
        used = 0
        seen: set[str] = set()

        for line in sorted(lines, key=lambda ln: -ln.get("weight", 0.0)):
            if used >= max_positions:
                break
            board = root_board.copy()
            w = line.get("weight", 0.0)
            for ply, mv in enumerate(line.get("moves", [])):
                if used >= max_positions:
                    break
                try:
                    board.push(mv)
                except Exception:
                    break
                key = board.epd()
                if key in seen:
                    continue
                seen.add(key)
                weight = w * (decay ** ply)
                s = self._saliency_absolute(board)
                for sq, v in s.items():
                    agg[sq] += weight * v
                total_w += weight
                used += 1

        if total_w > 0:
            for sq in agg:
                agg[sq] /= total_w
        mx = max(agg.values()) if agg else 0.0
        if mx > 0:
            for sq in agg:
                agg[sq] /= mx
        return agg
```

> **Note on the existing Intuition Glow:** because `_attention_saliency` is wrong for black-to-move,
> the current single-position glow is subtly off when it's Black's turn. **Optional, only if Claude
> approves in review:** route the existing `saliency()` path through `_saliency_absolute(board)` too.
> Keep it a SEPARATE, clearly-labeled change with its own before/after visual check — do not fold it
> into this feature silently.

---

## BACKEND EDIT 2 — `backend/engine_manager.py`: get the PV lines

Add a public method + its loop-bound impl (mirror the existing `analyze`/`_analyze_impl` pattern
EXACTLY — public method delegates via `self._submit(...)`; the impl holds `self._lock` and runs the
engine calls). Do NOT invent a new locking or loop scheme.

```python
    async def search_lines(self, fen: str, time_limit: float = 5.0, multipv: int = 3) -> list[dict]:
        """
        Run a timed multipv search and return the top PV lines as move sequences,
        for Calculation Glow aggregation. Each item:
            {"moves": [chess.Move, ...], "weight": float}
        weight is a simple rank decay (top line heaviest). [] in mock mode.
        """
        if self.mock_mode or self.engine is None:
            return []
        return await self._submit(self._search_lines_impl(fen, time_limit, multipv))

    async def _search_lines_impl(self, fen: str, time_limit: float, multipv: int) -> list[dict]:
        """Body of search_lines. Runs on the engine loop."""
        async with self._lock:
            try:
                board = chess.Board(fen)
                infos = await self.engine.analyse(
                    board,
                    chess.engine.Limit(time=time_limit),
                    multipv=max(1, min(multipv, 10)),
                )
                if not isinstance(infos, list):
                    infos = [infos]
                lines = []
                for rank, info in enumerate(infos):
                    pv = info.get("pv", [])
                    if not pv:
                        continue
                    lines.append({"moves": list(pv), "weight": 1.0 / (rank + 1)})
                return lines
            except Exception as exc:
                logger.error("search_lines failed: %s", exc)
                return []
```

---

## BACKEND EDIT 3 — `backend/app.py`: new dedicated endpoint

Add a new endpoint (do NOT add this cost to `/api/analyze`). Put it after the existing
`/api/analyze` route. `asyncio` is already importable; add `import asyncio` at the top if it is not
already present.

```python
@app.post("/api/calculation-glow")
async def calculation_glow(request: AnalyzeRequest):
    """
    Compute the aggregated 'Calculation Glow' for a position: BT3 attention
    averaged over the engine's top PV lines, weighted by line strength and depth.
    Expensive (~10-15s). Falls back to the single-position saliency if the engine
    is in mock mode or produced no lines.
    """
    fen = request.fen.strip()
    try:
        board = chess.Board(fen)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {exc}")

    lines = await lc0_engine.search_lines(
        fen, time_limit=request.time_limit, multipv=request.multipv
    )
    if not lines:
        # mock mode or no search result -> just return the intuition map
        policy_dist = await lc0_engine.get_policy_distribution(fen, nodes=1)
        return {
            "fen": fen,
            "calculation_saliency": neural_vision.saliency(fen, policy_dist=policy_dist),
            "positions_used": 0,
            "saliency_source": neural_vision.mode,
        }

    calc = await asyncio.to_thread(
        neural_vision.calculation_saliency, board, lines
    )
    return {
        "fen": fen,
        "calculation_saliency": calc,
        "positions_used": min(8, sum(len(l["moves"]) for l in lines)),
        "saliency_source": neural_vision.mode,
    }
```

Note: `AnalyzeRequest` already has `fen`, `multipv`, and `time_limit` (default 2.0, range 0.1–300).
For this endpoint a good default think time is 5s; the frontend will send it. Do not change the
`AnalyzeRequest` model.

---

## FRONTEND EDIT — `frontend/src/components/PgnViewer.tsx`

Follow the existing ref/state discipline (see `THINKING_TIME_TASKS.md` and the top-of-file comment).
The chessground move handler is captured at mount — read live values via refs, not stale state.

1. **State + ref mirror.** After the existing `showTop20` state, add:
   ```tsx
   const [glowMode, setGlowMode] = useState<'intuition' | 'calculation'>('intuition');
   const [calcLoading, setCalcLoading] = useState(false);
   ```

2. **Store the calc map on each GameState.** Add `calcSaliency: any` to the `GameState` type and
   initialize it to `null` in EVERY place a `GameState` object is created (mount, `handleMove`,
   `handleLoadPgn`'s start state, and the PGN walk loop — there are several; grep for `blunderFlash:`
   and add `calcSaliency: null,` next to each).

3. **Paint the right map.** In `paintOverlays`, choose the map by mode:
   ```tsx
   const paintOverlays = (st: GameState | undefined) => {
     if (!st) return;
     const policy = showTop20Ref.current ? st.policy : st.policy.slice(0, 5);
     const glow = glowMode === 'calculation' && st.calcSaliency ? st.calcSaliency : st.saliency;
     drawOverlays(glow, policy, st.blunderFlash);
   };
   ```
   `glowMode` is read here (not in the mount closure), so a plain state read is fine — BUT also add a
   `useEffect(() => { paintOverlays(gameStates.current[currentIndexRef.current]); }, [glowMode]);`
   (mirror the existing `[showTop20]` effect) so toggling repaints immediately.

4. **Fetch calculation glow on demand.** Add a function:
   ```tsx
   const computeCalcGlow = async () => {
     const st = gameStates.current[currentIndexRef.current];
     if (!st) return;
     setCalcLoading(true);
     try {
       const res = await fetch('http://127.0.0.1:8000/api/calculation-glow', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ fen: st.fen, multipv: 3, time_limit: 5 }),
       });
       const data = await res.json();
       const target = gameStates.current[currentIndexRef.current];
       if (target && target.fen === st.fen) {
         target.calcSaliency = data.calculation_saliency || null;
         setGlowMode('calculation');
         paintOverlays(target);
         forceRender();
       }
     } catch (err) {
       console.error('Calculation glow failed:', err);
     } finally {
       setCalcLoading(false);
     }
   };
   ```

5. **UI controls.** In the "Neural Vision" panel, near the "Show Top 20" row, add a glow-mode toggle
   and a compute button:
   ```tsx
   <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}>
     <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
       <input type="radio" checked={glowMode === 'intuition'} onChange={() => setGlowMode('intuition')} />
       Intuition Glow
     </label>
     <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
       <input type="radio" checked={glowMode === 'calculation'} onChange={() => setGlowMode('calculation')} />
       Calculation Glow
     </label>
     <button className="load-btn" disabled={calcLoading} onClick={computeCalcGlow}>
       {calcLoading ? 'Calculating…' : 'Compute (~15s)'}
     </button>
   </div>
   ```

**Do NOT** change the fetch URL host, the `drawOverlays` rendering internals, or the
`gameStates`/`currentIndexRef` model.

---

## VERIFICATION (Claude will drive these; report each honestly)

1. **Backend imports** — `C:\Users\Admin\miniconda3\envs\cszero\python.exe -c "import backend.app"`
   must succeed with no error.

2. **Orientation self-check (MANDATORY)** — run this and paste the numbers. `abs_diff` must be
   **small** (the normalized map must NOT equal the raw black-to-move map):
   ```python
   # cszero python, from project root
   import chess, logging; logging.disable(logging.WARNING)
   from backend.neural_vision import NeuralVision
   nv = NeuralVision(onnx_path=r'engine\bt3.onnx')
   b = chess.Board('r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3')
   raw = nv._attention_saliency(b.fen())          # WRONG frame for black-to-move
   good = nv._saliency_absolute(b)                # normalized
   import statistics
   print('should differ (proves normalization active):',
         round(statistics.mean(abs(raw[k]-good[k]) for k in raw), 3))
   ```

3. **Endpoint smoke test** — start the backend (see `HOW_TO_RUN.md`, must be `engine_mode: "live"`),
   then:
   ```powershell
   curl -s -X POST http://127.0.0.1:8000/api/calculation-glow -H "Content-Type: application/json" -d "{\"fen\":\"r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3\",\"multipv\":3,\"time_limit\":5}"
   ```
   Must return JSON with a 64-entry `calculation_saliency` and `positions_used > 0` in roughly
   10–15s.

4. **The money test (does the glow actually SHIFT?)** — pick a position with a concrete tactic on
   one wing. Compare `/api/analyze`'s `saliency` (intuition) vs `/api/calculation-glow`'s
   `calculation_saliency` (calculation). The top squares should MOVE toward the tactical wing. If the
   two maps are identical, something is wrong (likely lines empty or normalization no-op) — report
   it, don't hide it.

5. **Build** — `cd frontend; npm run build` → no TypeScript errors.

6. **UI** — toggle Intuition/Calculation, click Compute, confirm the glow repaints (~15s), and that
   Load Game / Prev / Next / dragging pieces all still work (no regression).

---

## FUTURE PHASE (NOT THIS TASK — do not build now)

Real-time "violently shifting" glow: run `engine.analysis()` streaming, recompute the aggregate at a
few checkpoints (e.g., 1s / 4s / 15s) or on major PV changes, and push snapshots to the frontend via
SSE/WebSocket so the glow animates as the search deepens. Bottlenecked by the ~1.5s/forward cost, so
it needs either a GPU or a coarse position budget. Design it as staged snapshots, not per-node.
