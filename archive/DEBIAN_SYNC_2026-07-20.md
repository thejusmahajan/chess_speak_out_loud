# Debian sync — porting the 2026-07-20 work

> Scope: the **delta for today only**. Base deployment (conda env, Linux `lc0`
> binary, the two Linux code changes for engine paths) is unchanged and lives in
> [`DEPLOY_DEBIAN.md`](DEPLOY_DEBIAN.md) — do that first if this machine has not
> run the backend before. Everything below assumes it has ("worked on the
> progress yesterday").

## 1. Pull the code

```bash
git checkout windows-dev && git pull origin windows-dev
```

Four commits landed (the first was committed yesterday but only pushed today):

| Commit | What it is |
|---|---|
| `7b24007` | G6 training-memory UI (drill sets list, review queue, trends) |
| `16444dc` | T3 sacrificial repertoire style + familiarity boost |
| `4edfabc` | Drill fixes (stale-closure board, chessground turnColor/premove, promotion picker) + full-line Lichess-semantics solutions (`line_uci`, `check_attempt`, ply-walking attempt API) |
| `8433de2` | `[%clk]` time-scramble filter, overnight runner, atomic-write hardening, 2× engine time budgets |

## 2. Ports with zero changes

- **All backend training code.** Pure Python; no new dependencies. The
  `os.replace` retry in `store._write_json_atomic` exists for a Windows
  antivirus/reader race (WinError 5, killed the first overnight run) — it is
  inert but harmless on Linux. Keep it.
- **`scripts/overnight_run.py`** — stdlib only, pathlib paths, `--base-url`
  arg. Runs unchanged.
- **Frontend changes** — no new npm packages; a rebuild (`npx vite build`) or
  the running vite dev server picking up the pull is all that's needed.

## 3. Platform-specific piece

`overnight.bat` is Windows glue. Its Linux counterpart is **`scripts/overnight.sh`**
(committed today): same behavior — refuses if port 8000 is occupied (stale-code
guard), starts a fresh backend with logs in `data/training/`, then runs the
runner with `--games 693`.

```bash
conda activate cszero          # the script does NOT activate the env itself
chmod +x scripts/overnight.sh  # once
scripts/overnight.sh
```

## 4. Data migration (gitignored — must be copied by hand)

Copy from the Windows machine (`C:\Users\Admin\Documents\chess_speak_out_loud`):

| What | Why |
|---|---|
| `data/training/` **entire folder** | EPD caches (`cache/*.jsonl` — keyed by position, fully portable, worth hours of engine time), profile + history, SRS state + attempts log (the training memory), drill sets, repertoire JSONs, overnight report/logs |
| `games_of_derdiedasdie/*.pgn` | the 693-game corpus (personal exports are gitignored) |
| network weights (791556 net, BT3) | per `DEPLOY_DEBIAN.md`; the `lc0` binary itself must be a **Linux** build, never copied from Windows |

```bash
rsync -av windows-box:/c/Users/Admin/Documents/chess_speak_out_loud/data/training/ data/training/
rsync -av windows-box:/c/Users/Admin/Documents/chess_speak_out_loud/games_of_derdiedasdie/ games_of_derdiedasdie/
```

**Single source of truth:** `srs.json` / `attempts.jsonl` (spaced-repetition
memory) and `profile.json` do not merge. After copying, do all further
diagnosis *and training* on one machine only, or later copies will overwrite
history.

## 5. The overnight run in progress on Windows

Job `bd32855b` (693 games, doubled budgets) started 02:50 on the Windows box;
ETA ~18:00–19:00 local. Two valid moves tomorrow:

- **Option A — let it finish**, then copy `data/training/` as in §4.
- **Option B — finish on the faster Debian box (recommended if it has a GPU):**
  stop the Windows backend+runner, copy `data/training/` as-is (partial caches
  included), then on Debian run `scripts/overnight.sh`. The runner resubmits;
  every already-analyzed position is a cache hit, so only the remainder is
  paid — at the faster machine's speed. Nothing is lost either way.

Note on budgets: the doubled times (stage B 6.0s/3.0s etc., now in
`TrainingConfig`) were tuned for the Windows CPU. On a GPU box the same seconds
buy far more nodes — keep them for maximum quality, or halve them back if wall
time matters more.

## 6. Verify after sync

```bash
python -m pytest backend/tests -q        # expect: 56 passed
cd frontend && npx tsc -b && cd ..       # frontend type-check
curl -s localhost:8000/api/health        # expect: "engine_mode": "live"
```

Then a 2-minute manual check in the Training tab: load a saved drill set, play
a **corpus** drill through its full line (replies auto-play, "So far:" grows),
and try a promotion (picker must appear). Do **not** "smoke-test" the runner
with a tiny `--games` value casually — a diagnosis run *replaces*
`profile.json` (old versions survive under `data/training/profiles/`, but the
app shows the latest).

## 7. Known gaps to carry on the roadmap

- `repertoire.json` is a single slot server-side (last build wins) — the four
  variants live in `data/training/repertoire_<style>_<color>.json` written by
  the runner. Per-color/style storage + UI is a small next task.
- Frontend hardcodes `http://127.0.0.1:8000` (see `DEPLOY_DEBIAN.md` §4) —
  matters if frontend and backend run on different hosts.
- Stage B is serialized through one LC0 process; cluster/multi-worker fan-out
  is the future phase that would actually use the cluster.
