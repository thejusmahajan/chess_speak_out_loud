# GEMINI WORKER SPEC — Adjustable LC0 Thinking Time

> **You are Gemini, the implementation worker.** Same discipline as always: **verify before coding,
> no invented APIs, run the build, report honestly.** This is a **frontend-only, additive** task in
> `frontend/src/components/PgnViewer.tsx`. **Do not touch the backend, `engine_manager.py`, the
> neural pipeline, the event-loop code, or the no-LLM decision.**

---

## GOAL

Let the user control how long LC0 thinks per position, and let them **re-analyze the current
position with extra time** ("think deeper at this specific point"), without changing anything else.

Two controls, both in the right-hand **"Neural Vision"** panel:

1. **Thinking Time selector** — sets the time budget (in seconds) sent with every analysis from now
   on. Presets: **1s (Fast)**, **2s (Normal — default)**, **5s (Deep)**, **15s (Very Deep)**.
2. **"Think Deeper ⏱" button** — immediately re-analyzes the **current** position with a fixed
   **15s** budget, regardless of the selector. This is the "at a specific point in the game" feature.

That's it. No new files, no new endpoints, no styling frameworks.

---

## WHY THIS IS MOSTLY DONE ALREADY (read — do not re-invent)

The backend **already accepts a thinking-time parameter.** In `backend/app.py` the analyze request
model is:

```python
class AnalyzeRequest(BaseModel):
    fen: str
    depth: Optional[int] = Field(default=None, ge=1, le=100)
    multipv: int = Field(default=3, ge=1, le=10)
    time_limit: float = Field(default=2.0, ge=0.1, le=300.0)
```

`time_limit` already flows all the way to `chess.engine.Limit(time=time_limit)`. **The only reason
LC0 always thinks ~2s today is that the frontend never sends `time_limit`** — look at `analyzeFen`
in `PgnViewer.tsx`, the fetch body is `JSON.stringify({ fen, multipv: 5 })`.

**Therefore: the entire task is to send `time_limit` in that request body and add two UI controls to
set it. DO NOT modify `backend/app.py` or `backend/engine_manager.py`.** If you find yourself
editing Python, stop — you are off track.

Valid range the backend accepts: **0.1 to 300.0 seconds.** Never send a value outside that or the
request 422s.

---

## CRITICAL — DO NOT REGRESS THE STATE MODEL (read before editing)

`PgnViewer.tsx` uses a deliberate ref/state model. **You must follow it or you will introduce a
stale-value bug that is invisible in casual testing.**

- The chessground move handler (`movable.events.after: handleMove`) is **captured once at mount**
  (inside the `useEffect(..., [])`). Any plain `useState` value read inside `analyzeFen` will be
  **stale** when analysis is triggered by dragging a piece.
- The existing code already solves this exact problem for the "Show Top 20" checkbox using a **ref
  mirror**: `showTop20Ref.current = showTop20;` (see near the top of the component). **You will copy
  that pattern for thinking time.** Do NOT read the thinking-time `useState` directly inside
  `analyzeFen`.
- All navigation still goes through `goToIndex(i)`. Do not add your own navigation.
- Keep the fetch URL exactly `http://127.0.0.1:8000/api/analyze`. Keep `multipv: 5`.

---

## EXACT EDITS

### Edit 1 — Add state + a ref mirror

Find this existing block near the top of the component:

```tsx
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showTop20, setShowTop20] = useState(false);
```

Add a thinking-time state right after it:

```tsx
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showTop20, setShowTop20] = useState(false);
  const [thinkSeconds, setThinkSeconds] = useState(2); // LC0 time budget per analysis (seconds)
```

Then find this existing ref-mirror line:

```tsx
  const showTop20Ref = useRef(showTop20);
  showTop20Ref.current = showTop20;
```

Add a matching mirror for thinking time immediately after it:

```tsx
  const showTop20Ref = useRef(showTop20);
  showTop20Ref.current = showTop20;
  const thinkSecondsRef = useRef(thinkSeconds);
  thinkSecondsRef.current = thinkSeconds;
```

### Edit 2 — Send `time_limit`, and allow a per-call override

Change the signature of `analyzeFen` to accept an optional time override. Find:

```tsx
  const analyzeFen = async (fen: string, uciPlayed: string | null, stateIndex: number) => {
```

Replace with:

```tsx
  const analyzeFen = async (
    fen: string,
    uciPlayed: string | null,
    stateIndex: number,
    timeOverride?: number,
  ) => {
```

Then find the fetch body inside `analyzeFen`:

```tsx
        body: JSON.stringify({ fen, multipv: 5 }),
```

Replace with:

```tsx
        body: JSON.stringify({
          fen,
          multipv: 5,
          time_limit: timeOverride ?? thinkSecondsRef.current,
        }),
```

**Note:** every existing caller of `analyzeFen(...)` passes 3 arguments and keeps working unchanged —
they will use `thinkSecondsRef.current` (the selector value). Only the new "Think Deeper" button
passes the 4th argument. Do not change the other call sites.

### Edit 3 — Add the two UI controls

Find this existing block in the JSX (the "Show Top 20" row):

```tsx
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input type="checkbox" checked={showTop20} onChange={(e) => setShowTop20(e.target.checked)} />
            Show Top 20 Arrows
          </label>

          {isAnalyzing && <span style={{ color: '#00ffcc', fontSize: '14px' }}>Analyzing...</span>}
        </div>
```

Insert a new control block **immediately after** that closing `</div>` (do not delete the block
above — add below it):

```tsx
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            Thinking time:
            <select
              value={thinkSeconds}
              onChange={(e) => setThinkSeconds(Number(e.target.value))}
              style={{ padding: '4px', borderRadius: '4px' }}
            >
              <option value={1}>1s (Fast)</option>
              <option value={2}>2s (Normal)</option>
              <option value={5}>5s (Deep)</option>
              <option value={15}>15s (Very Deep)</option>
            </select>
          </label>

          <button
            className="load-btn"
            disabled={isAnalyzing || !currentState}
            onClick={() => {
              const st = gameStates.current[currentIndexRef.current];
              if (st) analyzeFen(st.fen, st.lastMoveUci, currentIndexRef.current, 15);
            }}
          >
            Think Deeper ⏱
          </button>
        </div>
```

Notes for this edit:
- `currentState`, `gameStates`, `currentIndexRef`, and `analyzeFen` all already exist in this
  component — do not redeclare them.
- The button re-runs analysis on **the currently viewed position** with a **15s** budget. It reads
  the live index from `currentIndexRef.current` (not the possibly-stale `currentIndex`), matching
  the rest of the file.

---

## THINGS THAT WILL BITE YOU (Gemini failure modes — check each)

- ❌ **Do NOT** read `thinkSeconds` (the useState) directly inside `analyzeFen`. Use
  `thinkSecondsRef.current`. (Stale-closure bug when moving by dragging pieces.)
- ❌ **Do NOT** edit any `.py` file. The backend already supports `time_limit`.
- ❌ **Do NOT** send a `time_limit` above 300 or below 0.1 — the backend rejects it (HTTP 422).
- ❌ **Do NOT** convert refs to state or "simplify" the existing `gameStates`/`currentIndexRef`
  model. If Load Game / Prev / Next / play-both-sides break, you regressed.
- ❌ **Do NOT** change the fetch URL, the `multipv: 5`, or the response-handling logic.
- ⚠️ A long "Think Deeper" (15s) will make the board feel busy for ~15s because the engine holds its
  lock — that is expected, not a bug. The `disabled={isAnalyzing}` guard already prevents
  double-clicks.

---

## VERIFICATION (do all of these; report results honestly)

1. **Type-check / build** — from `frontend/`:
   ```powershell
   npm run build
   ```
   Must complete with **no TypeScript errors**. (`build` runs `tsc -b && vite build`.)

2. **Run the app** (see `HOW_TO_RUN.md`): backend on `:8000` (must show `engine_mode: "live"`),
   frontend `npm run dev` on `:5173`. Open http://localhost:5173.

3. **Selector works** — set Thinking time to **5s**, play a move. The "Analyzing..." indicator
   should stay up noticeably longer than at 1s. Confirm arrows/eval still render.

4. **Think Deeper works** — navigate to any position, click **Think Deeper ⏱**. Analysis should
   take ~15s and then repaint arrows + evaluation for that position.

5. **No regressions** — confirm Load Game, Prev/Next, clicking moves in the list, and dragging
   pieces to play both sides all still work exactly as before.

6. **Optional backend confirm** — while a 15s analysis runs, the backend log shows the engine busy;
   `curl http://127.0.0.1:8000/api/health` still returns `engine_mode: "live"`.

Report: which edits you made, the exact `npm run build` result, and the outcome of each verification
step. If any step fails, say so and stop — do not paper over it.
