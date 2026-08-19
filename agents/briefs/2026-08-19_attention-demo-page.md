```
Brief-ID:     2026-08-19_attention-demo-page
Written:      2026-08-19
Target repo:  thejusmahajan.github.io  (C:\Users\Admin\Documents\thejusmahajan.github.io)
Route:        Antigravity (open THAT folder as the workspace)
Type:         implementation (front-end)
Status:       BLOCKED until 2026-08-19_attention-export-json delivers a verified JSON file
Depends on:   2026-08-19_attention-export-json
```

# The attention demo page

An animated, interactive demonstration of real neural-network attention, built from verified
BT3 output. It is the centrepiece portfolio artifact for machine-learning applications.

**Do not start until `scratch/attention_export.json` exists in the chess repo AND the leader has
audited it.** If it is not there, stop and say so. **Never fabricate the data** — no random
numbers, no placeholder gradients, no "temporary" synthetic file. A fake AI visualisation on a
researcher's website is worse than no visualisation.

## 1. The audience constraint — this governs every design choice

Two very different people will open this page:

- **A non-technical HR screener.** Must understand what they are looking at in **five seconds**,
  see relevant keywords, and not feel stupid. If they are overwhelmed they close the tab.
- **A research scientist (PI).** Must find it real and non-trivial within thirty seconds.

**Resolution: a simple surface with depth on demand.** The default view is calm and almost
wordless. Everything technical hides behind one collapsed "What am I looking at?" panel.

**Do not** put jargon in the default view. No "softmax", "QK", "head-averaged", "logits",
"tensor" above the fold. Those words belong inside the expandable panel, where they signal
competence to the person who wants them.

## 2. Scope

**Create:** `attention-demo.html`, `js/attention-demo.js`, `data/attention_export.json`
(copy the audited file from the chess repo's `scratch/`).

**Edit:** `projects.html` only — add one card linking to the demo.

**Do not touch** any other page, `css/style.css`, or any `blog-*.html`. Do not commit or push.

**Stack rules:** match the existing site exactly — hand-written HTML, Tailwind via CDN, Inter
font, the nav and footer blocks copied **verbatim** from `projects.html` so they stay identical
across the site. **No build step, no npm, no framework, no external chart or chess library.**
Draw the board and heatmap with plain HTML/CSS or a `<canvas>`. Everything must work by opening
the file directly.

## 3. What the page shows

A chessboard, an animation across the network's 15 layers, and a heat overlay.

**Default state on load:** the first position, layer 1, animation **playing on a loop**,
roughly 700 ms per layer. It must be doing something the moment the page opens.

**The heat overlay:** each square's brightness = how much attention that square *receives*,
summed over the `from` axis of the 64×64 matrix for the current layer. Use a single-hue scale
(light → deep sky blue, matching the site's `sky-600`). Include a small legend reading simply
`less  ▁▂▃▄▅▆▇  more`.

**Interaction, in priority order:**
1. **Play / pause** and a **layer slider (1–15)**. The layer label reads `Layer 3 of 15`.
2. **Click a square** → the overlay switches to *that square's* attention row: "when the network
   is looking at e4, where else is it looking?" Show the clicked square with a ring. Clicking it
   again returns to the default view. Add a visible `Reset` control.
3. **Position selector** — three buttons using the `label` field from the JSON. One is Black to
   move; when it is selected, show the caption line `Black to move` so the orientation is
   explicit.

**Board orientation:** always draw a1 bottom-left, h8 top-right (White's view), for **all three
positions including the black-to-move one**. The exported data is in absolute squares, so no
flipping is needed anywhere. **Do not add any mirroring logic.** If the board looks wrong,
that is a data bug to report, not something to correct in the front end.

## 4. The copy (leader-written — use exactly)

**Page `<title>`:**
```
Watching a Neural Network Think — Dr. Thejus Mahajan
```

**H1:**
```
Watching a neural network think
```

**Standfirst — the five-second explanation, plain English, no jargon:**
```
This is a real neural network looking at a chess position. Each frame is one layer of the
network, from its first impression to its final judgement. The brighter a square, the more
attention the network is paying to it.
```

**Under the board, one line:**
```
Click any square to see where the network looks when it considers that square.
```

**The collapsed panel, labelled `What am I looking at?`** — this is where the technical depth
lives:
```
The network is BT3, a 15-layer transformer with 24 attention heads per layer, trained to play
chess. It sees the board as 64 tokens, one per square, and every layer computes a 64×64 matrix
of how much each square attends to every other square. What you see here is that matrix,
averaged over the 24 heads, one layer at a time.

The values are real model output, exported directly from the network — not an illustration.

One detail worth naming: the network represents the board from the side-to-move's point of
view, so its internal coordinates flip when it is Black to move. Reading the attention back onto
the true board requires undoing that flip. I originally got this wrong, published the result,
found the error, and corrected it — the write-up is linked below.
```

**Link below the panel** to `blog-lc0-attention-frame.html` with the text
`Read: the frame bug I shipped, found, and fixed`.

**Keyword line for the HR screener** — a plain row of small pills under the standfirst:
```
PyTorch · Transformers · Attention · Interpretability · ONNX · Python
```

## 5. The project card in `projects.html`

Add as the **second** card (immediately after the marine modelling one), matching the existing
card markup exactly:

- **Title:** `Watching a Neural Network Think — interactive attention demo`
- **Body:**
  ```
  An interactive visualisation of real attention from BT3, a 15-layer transformer chess engine.
  Click a square and watch which parts of the board the network attends to, layer by layer. The
  values are exported directly from the model.
  ```
- **Tag pills:** `PyTorch` `Transformers` `Interpretability` `ONNX` `JavaScript`
- **Button:** `Open the demo →` linking to `attention-demo.html`

## 6. Technical requirements

- Decode `attn_u8` from base64 to a `Uint8Array`; recover floats as `u8 / 255 * scale`.
- Index the matrix as `[from * 64 + to]`, where index 0 is **a1** and 63 is **h8**.
- Load the JSON with `fetch`. **Handle failure visibly**: if it does not load, show
  `Could not load the attention data.` — never fall back to generated numbers.
- Must be responsive: usable at 360 px wide. The board scales; controls wrap.
- Respect `prefers-reduced-motion` — if set, do not auto-play; show layer 1 and the controls.
- Keyboard accessible: play/pause and the slider reachable by tab, squares focusable.
- No console errors.

## 7. Gate — paste REAL output and say what you checked

1. Confirm `data/attention_export.json` is the audited file: paste its byte size and its
   `"schema"` and `"generated_utc"` values, and confirm they match the chess-repo original.
2. Open `attention-demo.html` in a browser. Confirm and state: the animation auto-plays; the
   layer label counts 1→15; clicking a square changes the overlay; the reset works; all three
   positions load.
3. **Screenshot or describe** the board for the `black_to_move` position and confirm a1 is
   bottom-left.
4. Paste the browser console output — must be free of errors.
5. Narrow-viewport check at 360 px: state what you observed.
6. `git status` — only the permitted files.

## 8. Your report

`agents/reports/2026-08-19_attention-demo-page_REPORT.md` in the **chess repo**. Include every
gate result, anything the brief got wrong, and anything not done. If you could not verify
something in a real browser, **say that plainly** rather than implying you did.
