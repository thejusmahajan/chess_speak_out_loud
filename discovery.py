import lczerolens
from lczerolens import LczeroModel, LczeroBoard

print("lczerolens dir:", [x for x in dir(lczerolens) if not x.startswith("_")])
print("LczeroModel methods:", [x for x in dir(LczeroModel) if not x.startswith("_")])

print("Loader methods:")
for name in ["from_path", "from_onnx", "from_pb", "load"]:
    print(name, hasattr(LczeroModel, name))

try:
    path = r"C:\Users\Admin\Documents\chess_speak_out_loud\engine\791556.pb.gz"
    print(f"\nAttempting to load {path}")
    model = LczeroModel.from_path(path)
    print("Model loaded successfully via from_path")
    print("Modules:")
    for name, module in model.named_modules():
        if 'attn' in name.lower() or 'attention' in name.lower() or 'mha' in name.lower():
            print(f" - {name}: {type(module).__name__}")
            
    board = LczeroBoard("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1")
    inputs = model.prepare_boards([board])
    outputs = model(**inputs)
    print("Output keys:", outputs.keys())
    
except Exception as e:
    import traceback
    traceback.print_exc()
