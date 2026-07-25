# =====================================================================
#  KAGGLE DIAGNOSTIC RUN — instrument the 1,000-game hang (do NOT fix, OBSERVE).
#  Paste this whole thing into a fresh Kaggle notebook cell and run it.
#  It reuses the same backend/weights/lc0 your working run used, but with:
#    - env + hardware facts printed up front,
#    - periodic ALL-THREAD stack dumps (faulthandler) — the key hang tool,
#    - a 10s heartbeat logging per-GPU utilization + which stage/index we're at,
#    - a watchdog that declares HANG (and dumps stacks) if no progress for N sec.
#  Start SMALL and SAFE (2 workers, 150 games). Read the output, then tell Claude:
#    (a) which STAGE the last heartbeat showed when it froze,
#    (b) the repeated faulthandler stack dump (what each thread is stuck on),
#    (c) whether GPU1 shows 0% the whole time (the all-on-GPU0 bug).
# =====================================================================
import os, sys, glob, time, threading, subprocess, faulthandler
from pathlib import Path

WORKING = Path("/kaggle/working")
os.chdir(WORKING)
if str(WORKING) not in sys.path:
    sys.path.insert(0, str(WORKING))

# ---- knobs (override via env; defaults are small + safe for diagnosis) ----
MAX_GAMES    = int(os.environ.get("MAX_GAMES", "150"))
LC0_WORKERS  = int(os.environ.get("LC0_WORKERS", "2"))
HANG_SECONDS = int(os.environ.get("HANG_SECONDS", "150"))   # no progress this long => HANG
os.environ.setdefault("LC0_BACKEND", "cuda-fp16")
os.environ.setdefault("STEER_SEARCH_BUDGET", "50000")
print(f"[cfg] MAX_GAMES={MAX_GAMES} LC0_WORKERS={LC0_WORKERS} HANG_SECONDS={HANG_SECONDS}", flush=True)

# ---- install python deps (Kaggle has torch preinstalled; the rest are not) ----
print("[deps] installing python-chess + lczerolens + friends...", flush=True)
subprocess.run([sys.executable, "-m", "pip", "-q", "install",
                "python-chess", "onnx", "onnx2torch", "lczerolens",
                "python-dotenv", "numpy", "fastapi", "uvicorn",
                "google-generativeai", "tqdm", "nest_asyncio"], check=True)
print("[deps] done", flush=True)

# ---- 0. hardware facts (is it really 2 GPUs? how many CPUs?) ----
try:
    import torch
    gpu_count = torch.cuda.device_count()
    print(f"[env] torch {torch.__version__} | CUDA GPUs={gpu_count}", flush=True)
    for i in range(gpu_count):
        print(f"[env]   GPU{i}: {torch.cuda.get_device_name(i)}", flush=True)
except Exception as e:
    gpu_count = 0
    print("[env] torch/cuda unavailable:", e, flush=True)
print(f"[env] CPU count (vCPUs): {os.cpu_count()}", flush=True)

# ---- 1. periodic ALL-THREAD stack dumps: if it freezes, these show EXACTLY
#         what every engine loop-thread + the main task is stuck on ----
faulthandler.enable()
faulthandler.dump_traceback_later(60, repeat=True)

# ---- 2. shared progress state + heartbeat/GPU logger + hang watchdog ----
_last = {"t": time.time(), "stage": "init", "n": 0}
_stop = threading.Event()

def _gpu_line():
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,utilization.gpu,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10).stdout.strip()
        return "  ".join("GPU%s:%s%% %s/%sMiB" % tuple(r.split(", "))
                         for r in out.splitlines()) if out else "(no smi)"
    except Exception as e:
        return f"(smi err: {e})"

def _heartbeat():
    t0 = time.time()
    hung = False
    while not _stop.wait(10):
        idle = time.time() - _last["t"]
        print(f"[hb {int(time.time()-t0):5d}s] stage={_last['stage']} n={_last['n']} "
              f"idle={idle:.0f}s | {_gpu_line()}", flush=True)
        if idle > HANG_SECONDS and not hung:
            hung = True
            print(f"\n[HANG] no progress {idle:.0f}s (> {HANG_SECONDS}). ALL-THREAD STACKS:\n", flush=True)
            faulthandler.dump_traceback()
            print("\n[HANG] ^ that is where it is stuck. Copy this whole block to Claude.\n", flush=True)

threading.Thread(target=_heartbeat, daemon=True).start()

# ---- 3. locate lc0 / weights / nets / pgn (reuse the working layout) ----
if not (WORKING / "backend").exists():
    m = glob.glob("/kaggle/input/**/diagnose_on_kaggle.py", recursive=True)
    if m:
        os.system(f"cp -r {Path(m[0]).parent}/* {WORKING}/")

def _find(name):
    p = WORKING / "engine" / name
    if p.exists():
        return str(p)
    hit = glob.glob(f"/kaggle/input/**/{name}", recursive=True) or \
          glob.glob(f"{WORKING}/**/{name}", recursive=True)
    return hit[0] if hit else None

import shutil
(WORKING / "engine").mkdir(exist_ok=True)

def get_linux_lc0():
    """Find lc0 (working dir -> dataset -> PATH), else compile (same as the
    working diagnose_on_kaggle.py). Compile takes a few min with ninja -j2."""
    lc0_bin = WORKING / "engine" / "lc0"
    if lc0_bin.exists():
        os.chmod(lc0_bin, 0o755); print("[lc0] found in working dir", flush=True); return str(lc0_bin)
    for cand in glob.glob("/kaggle/input/**/lc0", recursive=True):
        if os.path.isfile(cand) and not cand.endswith((".py", ".pb", ".gz", ".onnx")):
            try:
                os.chmod(cand, 0o755); shutil.copy(cand, lc0_bin); os.chmod(lc0_bin, 0o755)
                print("[lc0] found in dataset:", cand, flush=True); return str(lc0_bin)
            except Exception:
                pass
    sys_lc0 = shutil.which("lc0")
    if sys_lc0:
        print("[lc0] found on PATH:", sys_lc0, flush=True); return sys_lc0
    print("[lc0] compiling from source (ninja -j2, a few min)...", flush=True)
    subprocess.run(["apt-get", "update", "-qq"], check=False)
    subprocess.run(["apt-get", "install", "-qq", "-y", "meson", "ninja-build",
                    "libz-dev", "libopenblas-dev"], check=False)
    clone_dir = WORKING / "lc0_src"
    if not clone_dir.exists():
        subprocess.run(["git", "clone", "--recursive",
                        "https://github.com/LeelaChessZero/lc0.git", str(clone_dir)], check=True)
    build_dir = clone_dir / "build" / "release"
    subprocess.run(["meson", "setup", str(build_dir), str(clone_dir)], check=True)
    subprocess.run(["ninja", "-j2", "-C", str(build_dir)], check=True)
    shutil.copy(build_dir / "lc0", lc0_bin); os.chmod(lc0_bin, 0o755)
    print("[lc0] compiled ->", lc0_bin, flush=True)
    return str(lc0_bin)

LC0_BIN = get_linux_lc0()
assert LC0_BIN, "lc0 binary could not be found or built"

SEARCH_WEIGHTS = _find("BT3-768x15x24h-swa-2790000.pb.gz") or _find("791556.pb.gz")
assert SEARCH_WEIGHTS, (
    "LC0 WEIGHTS NOT FOUND. lc0's cuda-fp16 backend needs a .pb.gz network file; "
    "without it lc0 errors 'requires a network file' and every search HANGS. "
    "The .pb.gz weights are gitignored, so they are NOT in kaggle_files/. "
    "Add BT3-768x15x24h-swa-2790000.pb.gz (or 791556.pb.gz) to your Kaggle dataset "
    "under an engine/ folder, then re-run.")
ONNX = _find("bt3.onnx")
pgn_hits = glob.glob("/kaggle/input/**/lichess_derdiedasdie_2026-07-21.pgn", recursive=True) or \
           glob.glob(f"{WORKING}/**/lichess_derdiedasdie_2026-07-21.pgn", recursive=True)
assert pgn_hits, "PGN not found"
PGN = pgn_hits[0]
print(f"[setup] lc0={LC0_BIN}", flush=True)
print(f"[setup] weights={SEARCH_WEIGHTS}", flush=True)
print(f"[setup] onnx={ONNX}", flush=True)
print(f"[setup] pgn={PGN}", flush=True)

# ---- 4. build engine (SMALL pool) + vision ----
from backend.engine_manager import LC0Engine
from backend.engine_pool import EnginePool
from backend.neural_vision import NeuralVision
from backend.training import pipeline

def _factory():
    return LC0Engine(LC0_BIN, SEARCH_WEIGHTS, custom_uci_options={"Backend": "cuda-fp16"})

engine = EnginePool(LC0_WORKERS, _factory) if LC0_WORKERS > 1 else _factory()
if gpu_count:
    try:
        torch.set_default_device("cuda")
    except Exception as e:
        print("[setup] set_default_device warn:", e, flush=True)
vision = NeuralVision(onnx_path=ONNX)
print(f"[setup] vision.mode={vision.mode}", flush=True)

# ---- 5. select N games + tap _progress so the heartbeat sees liveness ----
raw = open(PGN, encoding="utf-8").read()
parts = raw.split("\n[Event ")
allg = [parts[0]] + ["[Event " + p for p in parts[1:]]
mine = [g for g in allg if "derdiedasdie" in g.lower()][:MAX_GAMES]
pgn_text = "\n\n".join(mine)
print(f"[setup] running {len(mine)} games", flush=True)

_orig_progress = pipeline._progress
def _tap(job_id, **kw):
    _last["t"] = time.time()
    if kw.get("stage_steer_done") is not None:
        _last["stage"], _last["n"] = "TS2", kw["stage_steer_done"]
    elif kw.get("stage_b_done") is not None:
        _last["stage"], _last["n"] = "B", kw["stage_b_done"]
    elif kw.get("stage_a_done") is not None:
        _last["stage"], _last["n"] = "A", kw["stage_a_done"]
    return _orig_progress(job_id, **kw)
pipeline._progress = _tap

# ---- 6. run under asyncio with clean start/stop ----
import asyncio
async def _main():
    if hasattr(engine, "start"):
        await engine.start()
    t0 = time.time()
    try:
        await pipeline.run_diagnosis("kaggle_diag", pgn_text, "derdiedasdie", engine, vision)
        print(f"\n[DONE] completed {len(mine)} games in {time.time()-t0:.0f}s", flush=True)
    finally:
        if hasattr(engine, "stop"):
            await engine.stop()
        _stop.set()
        faulthandler.cancel_dump_traceback_later()

try:
    import nest_asyncio; nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(_main())
except RuntimeError:
    asyncio.run(_main())
