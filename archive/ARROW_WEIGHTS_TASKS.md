# GEMINI WORKER SPEC — Make Policy-Arrow Weights Readable

> **You are Gemini, the implementation worker.** Small, contained **frontend-only** change in
> `frontend/src/components/PgnViewer.tsx` — specifically the **arrow-drawing block inside
> `drawOverlays`** (the `if (policy && policy.length > 0)` loop). Do not touch anything else:
> not the state model, not the saliency glow, not the analyze pipeline, not the backend.
> Same discipline: verify build, then **commit**.

---

## PROBLEM

Policy arrows currently encode probability as `opacity = max(0.2, p)` and
`width = max(1, p*4)%`. Because LC0 policy `p` values are small and close together (top move
~0.30, others ~0.10), the arrows all look nearly identical — the user cannot *see* which move
the network favors. We want the **best move to be an obviously fat, bright arrow** and weaker
candidates progressively thinner/fainter, plus an optional numeric label.

---

## REQUIRED CHANGE — normalize relative to the top move

Inside `drawOverlays`, in the policy loop, compute the max policy probability **once** before the
loop and scale each arrow relative to it, so the best move is always ratio = 1:

```ts
if (policy && policy.length > 0) {
  const pMax = Math.max(...policy.map((m: any) => m.p ?? 0)) || 1;

  for (const move of policy) {
    const fromSq = move.from, toSq = move.to, p = move.p;
    if (!fromSq || !toSq || p < 0.01) continue;

    const ratio = Math.min(1, p / pMax);        // best move -> 1, others proportional
    const width = 0.6 + ratio * 4.4;            // 0.6% (weak) .. 5% (best), board-relative
    const opacity = 0.25 + ratio * 0.75;        // 0.25 .. 1.0

    const fromCoords = getCoords(fromSq);
    const toCoords = getCoords(toSq);

    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', fromCoords.x + '%');
    line.setAttribute('y1', fromCoords.y + '%');
    line.setAttribute('x2', toCoords.x + '%');
    line.setAttribute('y2', toCoords.y + '%');
    line.setAttribute('stroke', `rgba(0, 255, 204, ${opacity})`);
    line.setAttribute('stroke-width', width + '%');
    line.setAttribute('marker-end', 'url(#arrowhead)');
    svg.appendChild(line);
  }
}
```

Keep the existing `getCoords`, the `arrowhead` marker, and the orientation handling exactly as
they are.

---

## OPTIONAL — numeric % labels (only for the strongest few, to avoid clutter)

For arrows where `ratio >= 0.15` **or** the move is in the top 5, draw a small SVG `<text>` with
the rounded percentage (e.g. `31%`) near the target square. Suggested placement: a point ~70% of
the way from `from` to `to` (so labels don't all pile on the origin square). Keep it small and
readable in both light/dark board squares — a semi-transparent dark pill behind the text, or a
white stroke/outline on the text, is acceptable. Do **not** label every arrow (20 labels is
noise); cap it at ~5.

If the labels look cluttered at the top-20 setting, gate them behind the existing `showTop20`
being **off** (i.e. only show labels in the top-5 view). Use your judgment; readability is the goal.

---

## VERIFY & COMMIT

1. Must both be clean (0 errors) before claiming done:
   ```powershell
   cd C:\Users\Admin\Documents\chess_speak_out_loud\frontend
   npx tsc --noEmit
   npx vite build
   ```
2. Manual check (backend from the conda env
   `C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn backend.app:app`; `npm run dev`):
   load a position — the **best move is a clearly fatter/brighter arrow** than the rest, and the
   relative thickness visibly tracks the policy. If labels were added, they read cleanly and
   don't overlap into a mess.
3. Commit from the repo root (no `--no-verify`):
   ```powershell
   cd C:\Users\Admin\Documents\chess_speak_out_loud
   git add -A
   git commit -m "Scale policy-arrow weight/opacity relative to top move for readability"
   ```

### Self-audit
- [ ] Only the arrow block in `drawOverlays` changed; state model, glow, analyze untouched.
- [ ] Best move is visibly the thickest/brightest arrow; weaker moves clearly thinner.
- [ ] `npx tsc --noEmit` and `npx vite build` both clean.
- [ ] Committed (no `--no-verify`).
