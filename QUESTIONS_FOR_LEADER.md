# QUESTIONS FOR LEADER

## 2026-07-23 — Lever 1 Stage A Policy Source Divergence: LC0 Engine vs NeuralVision evaluate_batch

### Context
When testing Lever 1 (Harvest-then-batch wide screen) in `backend/training/pipeline.py`, Stage A uncached policy distributions were pre-evaluated using `NeuralVision.evaluate_batch(fens)` (Torch/ONNX BT3) instead of `LC0Engine.get_policy_distribution(fen, nodes=1)` (LC0 UCI engine).

### Empirical Finding
Running `scratch/verify_policy_parity.py` on identical FENs revealed a significant divergence between the policy distribution produced by `LC0Engine.get_policy_distribution` and `NeuralVision.evaluate_batch`:
- **FEN 2** (`rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2`):
  - `LC0Engine`: `d2d4` prior = `0.5154` (top move `d2d4`)
  - `NeuralVision.evaluate_batch`: `d2d4` prior = `0.2108` (top move `d2d4`)
  - Max prior difference: `0.3046`, Total L1 difference: `0.9188`
- **FEN 3** (`r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2N2N2/PPPP1PPP/R1BQ1RK1 b kq - 5 5`):
  - `LC0Engine`: top move `d7d6` prior = `0.3069`
  - `NeuralVision.evaluate_batch`: top move `b7b5` prior = `0.0431` (`d7d6` = `0.0385`)
  - Max prior difference: `0.2684`, Total L1 difference: `1.3174`

### Questions for Leader
1. Is Stage A intended to use `LC0Engine.get_policy_distribution` (MCTS/LC0 search policy) or `NeuralVision.evaluate_batch` (raw BT3 ONNX forward pass policy)?
2. If `NeuralVision.evaluate_batch` is intended for Lever 1 wide screening, should the policy divergence thresholds in Stage A be re-calibrated for raw ONNX BT3 priors, or should `LC0Engine` support a native multi-FEN batch policy distribution interface?
