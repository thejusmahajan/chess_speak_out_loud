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
DRIVE = "/content/drive/MyDrive/cszero"          # folder holding the 3 files
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

# ⚠️ Example — verify the asset URL for a current release with a CUDA build:
LC0_URL = "https://github.com/LeelaChessZero/lc0/releases/download/v0.31.2/lc0-v0.31.2-linux-gpu-nvidia-cuda.tar.gz"
!cd /content && wget -q "$LC0_URL" -O lc0.tar.gz && mkdir -p lc0bin && tar xzf lc0.tar.gz -C lc0bin
LC0_BIN = subprocess.run("find /content/lc0bin -name lc0 -type f | head -1",
                         shell=True, capture_output=True, text=True).stdout.strip()
!chmod +x "$LC0_BIN"
print("lc0 binary:", LC0_BIN)
# sanity: should print a version banner and list a 'cuda' backend
print(subprocess.run([LC0_BIN, "--help"], capture_output=True, text=True).stderr[:400])

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
from backend.training import store, pipeline

def select_recent_games(pgn_text, player, n):
    blocks = re.split(r"\n\s*\n", pgn_text.strip()); games=[]; cur=[]
    for b in blocks:
        if b.lstrip().startswith("[Event"):
            if cur: games.append("\n\n".join(cur))
            cur=[b]
        elif cur: cur.append(b)
    if cur: games.append("\n\n".join(cur))
    def key(g):
        d=re.search(r'\[UTCDate "([^"]+)"\]',g); t=re.search(r'\[UTCTime "([^"]+)"\]',g)
        return ((d.group(1) if d else ""),(t.group(1) if t else ""))
    mine=[g for g in games if any(player.lower() in nm.lower()
          for _,nm in re.findall(r'\[(White|Black) "([^"]+)"\]',g))]
    mine.sort(key=key)
    return mine[-n:]

pgn_text = open(PGN_SRC, encoding="utf-8").read()
N_TEST = 40
subset = "\n\n".join(select_recent_games(pgn_text, PLAYER_NAME, N_TEST))
t0 = time.time()
await pipeline.run_diagnosis("colab-test", subset, PLAYER_NAME, engine, vision)
prof = store.load_profile()
dt = time.time() - t0
print(f"{N_TEST} games in {dt:.0f}s ({dt/N_TEST:.1f}s/game) -> "
      f"findings={len(prof.get('findings',[]))} "
      f"by_phase={'yes' if 'by_phase' in prof.get('aggregates',{}) else 'NO'}")
# Extrapolate: full run ~ (dt/N_TEST) * total_games seconds. Decide before scaling.

# %% [markdown]
# ## 7. Full run (set N to how many games you want; None = all)
# %%
N_FULL = 693     # or a bigger number, or None for every game
games = select_recent_games(pgn_text, PLAYER_NAME, N_FULL or 10**9)
print("running", len(games), "games...")
await pipeline.run_diagnosis("colab-full", "\n\n".join(games), PLAYER_NAME, engine, vision)
prof = store.load_profile()
agg = prof.get("aggregates", {})
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
