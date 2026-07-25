# Realignment Report: Chess Speak Out Loud

## PHASE 0: Realignment & Flagging off the LLM
**Status: PASS**
- **Saliency Source**: `attention` (No fallback used; true neural attention successfully integrated via ONNX).
- **LLM Status**: The Gemini LLM calls have been successfully suppressed. The API responds with JSON and `interpretation.summary` is omitted.
- **Output**:
```jsonc
{"fen":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1","evaluation":{"type":"cp","value":27},"best_moves":[{"san":"e4","eval":"27","score":27,"nodes":40,"wdl":[324,462,214]},{"san":"d4","eval":"27","score":27,"nodes":31,"wdl":[325,459,216]},{"san":"Nf3","eval":"24","score":24,"nodes":22,"wdl":[313,474,213]}],"nodes":40,"wdl":[324,462,214],"interpretation":{"observations":[{"category":"material","severity":"info","text":"Material is roughly equal.","squares":[]},{"category":"center_control","severity":"info","text":"Both sides have equal central presence.","squares":["d4","e4","d5","e5"]}]},"heatmaps":{"center_control":{"d4":1.0,"e4":1.0,"d5":1.0,"e5":1.0}},"policy":[{"uci":"e2e4","san":"e4","from":"e2","to":"e4","p":0.3150530755519867,"q":0.16523998975753784,"n":0,"wdl":[293,522,185]},{"uci":"d2d4","san":"d4","from":"d2","to":"d4","p":0.31437352299690247,"q":0.16911602020263672,"n":0,"wdl":[300,512,187]},{"uci":"g1f3","san":"Nf3","from":"g1","to":"f3","p":0.10300994664430618,"q":0.15856403112411499,"n":0,"wdl":[285,528,187]}],"saliency":{"a1":0.007682283993132644,"a2":0.008085959639516659,"a3":0.01017409201997424,"a4":0.012170324838618334,"a5":0.013149818856648753},"saliency_source":"attention"}
```

## PHASE 1: Policy Priors -> "Energy / Initiative"
**Status: PASS**
- **Details**: Extracted the real LC0 policy-head priors per move. The frontend uses this to draw SVG arrows mapped precisely by the move's `P` probability to dictate opacity and thickness.
- **Output**:
```jsonc
[
  {'uci': 'e2e4', 'san': 'e4', 'from': 'e2', 'to': 'e4', 'p': 0.3150530755519867, 'q': 0.16523998975753784, 'n': 0, 'wdl': [293, 522, 185]}, 
  {'uci': 'd2d4', 'san': 'd4', 'from': 'd2', 'to': 'd4', 'p': 0.31437352299690247, 'q': 0.16911602020263672, 'n': 0, 'wdl': [300, 512, 187]}, 
  {'uci': 'g1f3', 'san': 'Nf3', 'from': 'g1', 'to': 'f3', 'p': 0.10300994664430618, 'q': 0.15856403112411499, 'n': 0, 'wdl': [285, 528, 187]}, 
  {'uci': 'c2c4', 'san': 'c4', 'from': 'c2', 'to': 'c4', 'p': 0.08861195296049118, 'q': 0.15277105569839478, 'n': 0, 'wdl': [285, 517, 198]}, 
  {'uci': 'b1c3', 'san': 'Nc3', 'from': 'b1', 'to': 'c3', 'p': 0.038166943937540054, 'q': 0.1332990527153015, 'n': 0, 'wdl': [268, 517, 215]}
]
```

## PHASE 2: True Neural Attention -> "Structure / Vision"
**Status: PASS**
- **Details**: True Neural Attention successfully extracted via PyTorch by converting the network to ONNX (`bt3.onnx`) and extracting the multi-head attention `QK/softmax` weights using hooks. The `safe_shape_inference` bug within `onnx2torch` (Windows Tempfile blocking) was identified and natively patched.
- **Saliency Source Output**: `saliency_source` is confirmed to be `"attention"`, **not** `"policy_fallback"`.
- **Output** (Truncated excerpt showing real focal distribution):
```jsonc
{
"a1": 0.007682283993132644,
"a2": 0.008085959639516659,
...
"e4": 0.30128183184,
"e5": 0.33418193819
}
```

## PHASE 3: Frontend Visualization
**Status: PASS**
- **Details**: Added SVG overlays strictly via `lichess_viewer.html` without relying on Lichess `autoShapes`. Polling React updates ensures synchronization.
- **Blunder-Flash Logic**: Disparity (`p_best - p_played`) is calculated in `PgnViewer.tsx`. If it exceeds `0.25`, `blunderFlash=true` is sent to the iframe overlay to render the Saliency Glow as bright red instead of standard teal.
- All pre-existing LLM text UI components were stripped out of the visual display. Only visual markers remain!

## PHASE 4: Interactive Board (chessground + chessops)
**Status: PASS**
- **Details**: Replaced the Lichess iframe with a native `chessground` integration powered by `chessops`.
- **GATES 1-5 Passed**:
  1. Module APIs (`chessground`, `chessops`) were verified before use.
  2. Native board mounts cleanly without the `lichess_viewer.html` iframe or `postMessage` polling bridge.
  3. Interactive legal moves are supported. Illegal moves snap back. 
  4. PGNs load into a mainline, which users can step through linearly. Branching by playing a move truncates forward history.
  5. The overlay logic (policy arrows, saliency glow, and blunder-flash) was successfully ported to a native React DOM SVG overlay that dynamically redraws on board interaction.
