# %% [markdown]
# # Chess Speak Out Loud — GPU diagnosis on Colab
#
# Runs the full diagnosis pipeline (LC0 + BT3) on a Colab **GPU** so a large PGN
# finishes in ~minutes instead of ~hours, then builds repertoire trees + drills.
# Outputs land in `data/training/` and are zipped for download.
#
# **This notebook is an untested best-effort draft** (I have no GPU/Colab to run
# it). The cells marked `⚠️ ITERATE` are the env-specific parts you (with the
# Antigravity/Gemini agent) will likely need to tweak — CUDA LC0 setup and BT3
# device placement. Everything else (the pipeline invocation) is exactly how the
# app runs it.
#
# ## Before you start — get these into the runtime (they are NOT on GitHub; the
#    nets and PGN are gitignored):
#   - `791556.pb.gz`  (LC0 policy weights, ~18 MB)
#   - `bt3.onnx`      (BT3 attention net, ~410 MB — big; use Google Drive)
#   - your games PGN  (e.g. `lichess_derdiedasdie_2026-07-21.pgn`, ~19 MB)
# Easiest: upload all three to a Google Drive folder once, then mount Drive below.
#
# **Runtime → Change runtime type → GPU (T4)** before running.

# %% [markdown]
# ## 1. GPU check
# %%
import subprocess, sys
print(subprocess.run(["nvidia-smi"], capture_output=True, text=True).stdout or "NO GPU — set Runtime→GPU")
import importlib
try:
    import torch
    print("torch", torch.__version__, "| cuda:", torch.cuda.is_available(),
          "|", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu")
except Exception as e:
    print("torch not yet installed:", e)

# %% [markdown]
# ## 2. Mount Drive (nets + PGN live here) and set paths
# %%
from google.colab import drive
drive.mount("/content/drive")
# ⚠️ EDIT these to where you put the files on your Drive:
DRIVE = "/content/drive/MyDrive/colab_chess_speak_out_loud"          # folder holding the 3 files
WEIGHTS_SRC = f"{DRIVE}/791556.pb.gz"
BT3_SRC     = f"{DRIVE}/bt3.onnx"
PGN_SRC     = f"{DRIVE}/lichess_derdiedasdie_2026-07-21.pgn"
PLAYER_NAME = "derdiedasdie"
import os
for p in (WEIGHTS_SRC, BT3_SRC, PGN_SRC):
    print(("OK  " if os.path.exists(p) else "MISSING "), p)

# %% [markdown]
# ## 3. Clone the repo (private → needs a GitHub token) + install deps
# %%
# ⚠️ paste a GitHub PAT with read access, or upload the repo zip instead.
GH_TOKEN = ""  # e.g. "github_pat_..."
GH_REPO = "thejusmahajan/chess_speak_out_loud"
BRANCH = "windows-dev"
%cd /content
if not os.path.exists("/content/repo"):
    url = f"https://{GH_TOKEN}@github.com/{GH_REPO}.git" if GH_TOKEN else f"https://github.com/{GH_REPO}.git"
    subprocess.run(["git", "clone", "--branch", BRANCH, "--depth", "1", url, "repo"], check=True)
%cd /content/repo
# The conda env holds the deps locally; on Colab pip-install the real ones:
!pip -q install python-chess onnx onnx2torch lczerolens python-dotenv numpy fastapi uvicorn google-generativeai
# torch is preinstalled on Colab with CUDA — do NOT reinstall it.

# %% [markdown]
# ## 4. ⚠️ ITERATE — install a CUDA LC0 and place the weights
# LC0 uses the GPU via its own CUDA backend (not torch). Grab a Linux GPU build
# from the lczero releases. The exact asset name/version changes — check
# https://github.com/LeelaChessZero/lc0/releases and adjust the URL.
# %%
os.makedirs("/content/repo/engine", exist_ok=True)
import shutil
shutil.copy(WEIGHTS_SRC, "/content/repo/engine/791556.pb.gz")
shutil.copy(BT3_SRC,     "/content/repo/engine/bt3.onnx")

# LC0 compilation & binary resolution:
# Official LC0 GitHub releases do not provide pre-compiled Linux CUDA archives.
# We compile LC0 from source (takes ~1 min with ninja) and cache per GPU type (T4 vs A100).

import torch
gpu_name = torch.cuda.get_device_name(0).replace(" ", "_") if torch.cuda.is_available() else "cpu"
LC0_DRIVE_BIN = f"{DRIVE}/lc0_{gpu_name}"
LC0_BIN = "/content/lc0/build/release/lc0"

if os.path.exists(LC0_DRIVE_BIN):
    print("Using cached LC0 binary from Drive for", gpu_name, ":", LC0_DRIVE_BIN)
    LC0_BIN = LC0_DRIVE_BIN
else:
    print(f"Compiling LC0 from source for {gpu_name} (~1 min)...")
    !apt-get update -qq && apt-get install -y -qq git ninja-build libprotobuf-dev protobuf-compiler libopenblas-dev
    !pip -q install meson
    !cd /content && if [ ! -d "lc0" ]; then git clone -b release/0.31 --recurse-submodules https://github.com/LeelaChessZero/lc0.git; fi
    !rm -rf /content/lc0/build
    !cd /content/lc0 && ./build.sh
    if os.path.exists(LC0_BIN) and os.path.exists(DRIVE):
        try:
            shutil.copy(LC0_BIN, LC0_DRIVE_BIN)
            print("Cached LC0 binary to Drive:", LC0_DRIVE_BIN)
        except Exception as e:
            print("Could not cache binary to Drive:", e)

!chmod +x "$LC0_BIN"
print("lc0 binary:", LC0_BIN)
# sanity: should print a version banner and list a 'cuda' backend
res = subprocess.run([LC0_BIN, "--help"], capture_output=True, text=True)
print(res.stderr[:400] or res.stdout[:400])

# %% [markdown]
# ## 5. Build the engine + vision objects (same classes the app uses)
# %%
sys.path.insert(0, "/content/repo")
from backend.engine_manager import LC0Engine
from backend.neural_vision import NeuralVision

engine = LC0Engine(engine_path=LC0_BIN,
                   weights_path="/content/repo/engine/791556.pb.gz")
await engine.start()   # Colab notebooks allow top-level await
print("engine available (GPU LC0):", engine.is_available())

# ⚠️ ITERATE — BT3 on GPU. NeuralVision loads bt3.onnx via lczerolens; whether it
# lands on the GPU depends on lczerolens' device handling. Try enabling a default
# CUDA device BEFORE constructing it; if attention saliency errors, fall back to
# CPU (remove the set_default_device line) — LC0 will still be GPU-accelerated.
if torch.cuda.is_available():
    try:
        torch.set_default_device("cuda")
    except Exception as e:
        print("could not set default cuda device:", e)
vision = NeuralVision(onnx_path="/content/repo/engine/bt3.onnx")
print("vision mode:", vision.mode)   # want "attention"; "policy_fallback" = BT3 didn't load

# %% [markdown]
# ## 6. VALIDATE on a small subset first (do NOT run the full PGN blindly)
# Slice the newest N games of the player, run diagnosis, confirm it produces a
# non-degenerate profile, and time it — then scale up.
# %%
import re, time, chess.pgn
from tqdm.notebook import tqdm
from backend.training import store, pipeline, metrics

# Optimize engine search time limits for GPU acceleration (A100 runs 10,000+ nodes in <0.1s!)
metrics.DEFAULT_CONFIG = metrics.TrainingConfig(confirm_best_seconds=1.0, confirm_played_seconds=0.5)

def select_recent_games(pgn_text, player, n):
    player_lower = player.lower()
    raw_blocks = pgn_text.split("\n[Event ")
    games = []
    for i, b in enumerate(raw_blocks):
        full_game = b if i == 0 else "[Event " + b
        if player_lower in full_game.lower():
            games.append(full_game)
    
    def key(g):
        d = re.search(r'\[UTCDate "([^"]+)"\]', g)
        t = re.search(r'\[UTCTime "([^"]+)"\]', g)
        return ((d.group(1) if d else ""), (t.group(1) if t else ""))
        
    games.sort(key=key)
    return games[-n:]

print("Reading PGN file...")
pgn_text = open(PGN_SRC, encoding="utf-8").read()
N_TEST = 40
subset_games = select_recent_games(pgn_text, PLAYER_NAME, N_TEST)
print(f"Selected {len(subset_games)} games for player '{PLAYER_NAME}'. Starting diagnosis...")

# Wrap pipeline progress with tqdm.notebook progress bar
pbar = None
orig_progress = pipeline._progress
def custom_progress(job_id, total=None, stage_a_done=None, stage_b_done=None, stage_steer_done=None, **kwargs):
    global pbar
    orig_progress(job_id, total=total, stage_a_done=stage_a_done, stage_b_done=stage_b_done, stage_steer_done=stage_steer_done, **kwargs)
    if total is not None and pbar is None:
        pbar = tqdm(total=total, desc="Diagnosing Games", unit="move")
    if pbar is not None:
        current = stage_steer_done or stage_b_done or stage_a_done or 0
        pbar.n = min(current, pbar.total or current)
        pbar.refresh()

pipeline._progress = custom_progress
subset = "\n\n".join(subset_games)
t0 = time.time()
await pipeline.run_diagnosis("colab-test", subset, PLAYER_NAME, engine, vision)
if pbar is not None:
    pbar.close()
    pipeline._progress = orig_progress

prof = store.load_profile()
dt = time.time() - t0
print(f"✅ {N_TEST} test games completed in {dt:.0f}s ({dt/N_TEST:.1f}s/game) -> "
      f"findings={len(prof.get('findings',[]))} "
      f"by_phase={'yes' if 'by_phase' in prof.get('aggregates',{}) else 'NO'}")

# %% [markdown]
# ## 7. Full run (set N to how many games you want; None = all)
# %%
N_FULL = None     # None = analyze ALL games in the PGN (e.g. all 4000+ games)
games = select_recent_games(pgn_text, PLAYER_NAME, N_FULL or 10**9)
print(f"Starting FULL diagnosis over all {len(games)} games for player '{PLAYER_NAME}'...")

pbar_full = None
def custom_progress_full(job_id, total=None, stage_a_done=None, stage_b_done=None, stage_steer_done=None, **kwargs):
    global pbar_full
    orig_progress(job_id, total=total, stage_a_done=stage_a_done, stage_b_done=stage_b_done, stage_steer_done=stage_steer_done, **kwargs)
    if total is not None and pbar_full is None:
        pbar_full = tqdm(total=total, desc="Full Corpus Diagnosis", unit="move")
    if pbar_full is not None:
        current = stage_steer_done or stage_b_done or stage_a_done or 0
        pbar_full.n = min(current, pbar_full.total or current)
        pbar_full.refresh()

pipeline._progress = custom_progress_full
await pipeline.run_diagnosis("colab-full", "\n\n".join(games), PLAYER_NAME, engine, vision)
if pbar_full is not None:
    pbar_full.close()
    pipeline._progress = orig_progress

prof = store.load_profile()
agg = prof.get("aggregates", {})
print("✅ FULL DIAGNOSIS COMPLETED!")
print("games", prof.get("games_analyzed"), "moves", prof.get("moves_analyzed"),
      "findings", len(prof.get("findings", [])),
      "| by_phase:", agg.get("by_phase"), "| by_clock:", agg.get("by_clock"))

# %% [markdown]
# ## 8. Build repertoires + a few trees + a drill set (optional)
# %%
from backend.training import select_repertoire, drills
for style in ("weakness", "sacrificial"):
    for color in ("white", "black"):
        try:
            rep = await select_repertoire.build_repertoire(prof, color, engine, style=style)
            store.save_repertoire(rep)
            print(f"repertoire {style}/{color}: {len(rep.get('recommendations',[]))} lines")
        except Exception as e:
            print(f"repertoire {style}/{color} failed:", e)

# a couple of variation trees for the top openings (adjust ECOs/colors)
for eco, color in [("A40", "white"), ("A46", "white"), ("D02", "white")]:
    try:
        tree = await select_repertoire.build_repertoire_tree(
            eco, color, PGN_SRC, PLAYER_NAME, engine, profile=prof)
        n_crit = sum(1 for n in tree["nodes"] if n.get("critical"))
        print(f"tree {eco}/{color}: {len(tree['nodes'])} nodes, {n_crit} critical")
    except Exception as e:
        print(f"tree {eco}/{color} failed:", e)

await engine.stop()

# %% [markdown]
# ## 9. Package the artifacts for download
# The whole `data/training/` (profile.json, profiles/, repertoire_*.json,
# repertoire_tree_*.json, drills/, srs.json, cache/) — bring it back to your
# machine and drop it into the repo's `data/training/`.
# %%
!cd /content/repo && zip -q -r /content/cszero_training_data.zip data/training && ls -lh /content/cszero_training_data.zip
from google.colab import files
files.download("/content/cszero_training_data.zip")
# (or copy to Drive: shutil.copy("/content/cszero_training_data.zip", f"{DRIVE}/"))


# %% [markdown]
# ## DIAGNOSIS — run AFTER Cell 5: GPU/CPU per component, per-stage timing, Stage B findings.
# Paste the full output back to plan the edits. Step 4 overwrites profile.json with a 3-game profile.
# %%
import subprocess, time
from collections import Counter
from backend.training import store, pipeline

WEIGHTS = "/content/repo/engine/791556.pb.gz"
START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def _gpu():
    return subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used",
                           "--format=csv,noheader"], capture_output=True, text=True).stdout.strip()


print("=== 1) lc0 backend + speed (what the app engine gets) ===")
print("GPU idle:", _gpu())
b = subprocess.run([LC0_BIN, "benchmark", f"--weights={WEIGHTS}", "--num-positions=2"],
                   capture_output=True, text=True)
for ln in (b.stderr + b.stdout).splitlines():
    if any(k in ln.lower() for k in ("creating backend", "backend:", "nps", "nodes/s",
                                     "blas", "eigen", "error")):
        print("  ", ln.strip())

print("\n=== 2) app engine: is the net on the GPU? (non-zero MiB while alive) ===")
if "engine" in globals() and engine.is_available():
    print("GPU w/ engine loaded:", _gpu())
    t = time.time()
    await engine.analyze(START, multipv=2, time_limit=2.0)
    print(f"analyze(2.0s) wall: {time.time()-t:.2f}s")
else:
    print("engine not built — run Cell 5 first")

print("\n=== 3) BT3 saliency device/speed ===")
if "vision" in globals():
    print("vision.mode:", vision.mode, "(want 'attention')")
    t = time.time()
    n = len(vision.saliency_absolute(START))
    print(f"one saliency: {time.time()-t:.2f}s over {n} squares  (GPU <0.1s / CPU ~1.5s)")
else:
    print("vision not built — run Cell 5 first")

print("\n=== 4) instrumented 3-game run: where does the wall-clock go? ===")
raw = open(PGN_SRC, encoding="utf-8").read()
blocks = raw.split("\n[Event ")
allg = [(g if i == 0 else "[Event " + g) for i, g in enumerate(blocks)]
mine = [g for g in allg if PLAYER_NAME.lower() in g.lower()][:3]
subset = "\n\n".join(mine)
print(f"running {len(mine)} games...")

t0 = time.time()
ev = []
_orig = pipeline._progress
def _tap(job_id, **kw):
    _orig(job_id, **kw)
    ev.append((time.time() - t0, kw))
pipeline._progress = _tap
await pipeline.run_diagnosis("diag3", subset, PLAYER_NAME, engine, vision)
pipeline._progress = _orig
tot = time.time() - t0

def _win(key):
    ts = [t for t, kw in ev if kw.get(key) is not None]
    return (min(ts), max(ts)) if ts else None
for lbl, key in [("Stage A (policy)", "stage_a_done"),
                 ("Stage B (confirm)", "stage_b_done"),
                 ("TS2 (steering)", "stage_steer_done")]:
    w = _win(key)
    print(f"  {lbl:18s}: " + (f"{w[0]:.1f}s -> {w[1]:.1f}s  ({w[1]-w[0]:.1f}s active)"
                              if w else "-- (never reported / 0 items)"))
print(f"  TOTAL 3 games: {tot:.1f}s")

print("\n=== 5) what the 3-game run PRODUCED (Stage B ground truth) ===")
prof = store.load_profile()
fs = prof.get("findings", [])
print("findings:", len(fs),
      "| severity:", dict(Counter(f.get("severity") for f in fs)),
      "| confirmed:", dict(Counter(bool(f.get("confirmation", {}).get("confirmed")) for f in fs)))
print("by_phase:", prof.get("aggregates", {}).get("by_phase"))
print("\nGPU final:", _gpu())
