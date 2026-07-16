# Realignment Report

## Phase 2: Transformer Migration Complete
- Downloaded `BT3-768x15x24h-swa-2790000.pb.gz` and passed architecture checks (GATE A).
- Converted network to ONNX format using `leela2onnx` (`bt3.onnx`) (GATE B).
- Resolved Windows-specific `tempfile.NamedTemporaryFile` lock issues with `safe_shape_inference` in `onnx2torch` by applying a local monkey-patch (GATE C).
- Explored the ONNX model structure dynamically using `register_forward_hook` and discovered that the exact target `[*, 24, 64, 64]` shape self-attention weights were available at `module.encoder{0..14}/mha/QK/softmax` (GATE D).
- Implemented `NeuralVision._attention_saliency` in `backend/neural_vision.py`. The extraction averages the multi-head self-attention queries layer-by-layer and outputs a structural distribution to highlight which squares receive the highest cognitive load from the transformer.
- GATE E was passed: `nv.mode` is confirmed to be `"attention"`, and the saliency heat maps to heavy pieces on the back rank instead of raw policy moves (proving distinct signals).

## Open Questions / Pending
- Currently, policy priors are still queried from `791556` for speed, while the attention saliency is fetched from `BT3`. If conceptual integrity is paramount, we should switch the engine's main config to use BT3 exclusively, though this might incur slower processing times on a CPU. User approval is requested before proceeding.
