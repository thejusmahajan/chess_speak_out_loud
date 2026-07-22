# GPU SMOKE TEST (~15s) — run AFTER Cell 5, once the repo is pulled to latest.
# Confirms BT3 is on the A100 and measures the batched-saliency + evaluate_batch
# wins. Rebuilds `vision` from the reloaded (device-aware) NeuralVision. Writes a
# clean report and auto-downloads it (no terminal copy-paste needed).
import importlib, time, torch
import backend.neural_vision as nv
importlib.reload(nv)                     # pick up device-aware NeuralVision + evaluate_batch
vision = nv.NeuralVision(onnx_path="/content/repo/engine/bt3.onnx")
assert vision.mode == "attention", "BT3 not in attention mode"

R = []
def out(*a):
    s = " ".join(str(x) for x in a); print(s); R.append(s)

out("=== 1) is BT3 on the GPU? ===")
dev = next(vision.model.parameters()).device
out("BT3 model device:", dev, "->", "ON GPU" if "cuda" in str(dev) else "STILL ON CPU (!)")

FENS = [
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
    "6k1/5ppp/8/8/8/8/5PPP/6K1 b - - 0 1",
] * 16   # 64 positions

out("\n=== 2) saliency: serial vs batched ===")
t = time.time(); [vision.saliency_absolute(f) for f in FENS[:16]]; ts = time.time() - t
out(f"  serial  x16: {ts:.2f}s  ({ts/16*1000:.0f} ms/pos)")
t = time.time(); vision.saliency_absolute_batch(FENS[:64]); tb = time.time() - t
out(f"  batched x64: {tb:.2f}s  ({tb/64*1000:.0f} ms/pos)  -> {(ts/16)/(tb/64):.1f}x faster per position")

out("\n=== 3) evaluate_batch (the TS2 candidate-screen primitive) ===")
t = time.time(); res = vision.evaluate_batch(FENS[:64]); te = time.time() - t
r0 = res[0]
out(f"  evaluate_batch x64: {te:.2f}s  ({te/64*1000:.0f} ms/pos)")
out(f"  sample: value={r0['value']:+.3f}  top={r0['policy'][0]['uci']}@{r0['policy'][0]['p']:.3f}  "
    f"legal_mass={sum(m['p'] for m in r0['policy']):.3f}")

open("/content/gpu_smoke.txt", "w", encoding="utf-8").write("\n".join(R))
from google.colab import files
files.download("/content/gpu_smoke.txt")
print("\n>>> gpu_smoke.txt downloading to your machine.")
