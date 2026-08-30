# Knowledge Trainer

Two things that share one app:

1. **Spaced-repetition drilling** (SM-2 + Elo) for AEON-UP and LC0 neural interpretability
   interview preparation.
2. **The 24/7 timetable** — the day plan, running as an alarm clock that announces every
   session boundary.

## How to Run

Double-click **`launch_knowledge_trainer.bat`** in the repo root. It starts both the timetable
daemon and the web server, then opens the browser. **`stop_knowledge_trainer.bat`** stops both.

Manually:

```powershell
C:\Users\Admin\miniconda3\envs\cszero\python.exe -m uvicorn trainer.app:app --port 8010
```

Open your browser at `http://127.0.0.1:8010/`.

---

## The timetable

The day plan lives in **`trainer/content/timetable.json`** — one JSON file, editable by hand.
It is the single source of truth for the web bar, the API and the desktop daemon.

### The one rule that matters

**Every block boundary produces exactly one reminder, five minutes before it.** That single
reminder is simultaneously *"this session is about to end"* and *"the next session is about to
start"*, so nothing is ever announced twice.

**It makes a sound only when the block *starting* at that boundary is not rest or sleep.**

| boundary | example | sound |
|---|---|---|
| work → rest | 05:55, "Interview prep ends at 06:00" | **silent** — he is concentrating |
| rest → work | 06:10, "Rest ends at 06:15, then Coursera" | **ALARM** — get back to the desk |
| rest → meal | 07:55, "Breakfast at 08:00" | **ALARM** |
| work → sleep | 21:55, "Sleep at 22:00" | **silent** |
| 03:00 wake-up | fires *at* 03:00, not 02:55 | **ALARM** |

### Editing the schedule

Edit `content/timetable.json` and save. The daemon reloads it on the next tick (it watches the
mtime); the browser picks it up within ten minutes, or immediately on refresh. If the edit is
broken, the daemon keeps the last good version running and says so — the alarm clock never goes
down because of a typo.

The blocks must **tile the full 24 hours** with no gap and no overlap; exactly one block may wrap
past midnight (`"start": "22:00", "end": "03:00"`). A gap is rejected at load time with a message
naming both sides of it — silent dead time is the one failure this thing cannot afford.

Per-block fields:

| field | meaning |
|---|---|
| `start`, `end` | `"HH:MM"`, local time |
| `task` | what the bar and the banner say |
| `kind` | `chore` / `focus` / `work` / `meal` / `rest` / `sleep`. `rest` and `sleep` are the quiet kinds |
| `note` | one line of detail, e.g. *"Eat light — hot and cooked."* |
| `start_alarm` | sound *at* the start instead of five minutes before (the wake-up) |
| `lead_sound` | force the sound decision, overriding what `kind` implies |

`lead_minutes` at the top of the file changes the warning time for everything.

### The desktop daemon (this is the reliable half)

```powershell
python -m trainer.schedule_daemon                # run it
python -m trainer.schedule_daemon --check        # print the next 8 reminders and exit
python -m trainer.schedule_daemon --test-alarm   # prove the sound works and exit
python -m trainer.schedule_daemon --no-gui       # console only, no popup banner
```

Or double-click **`launch_schedule.bat`** / **`stop_schedule.bat`**.

It pops an always-on-top banner that cannot hide behind the IDE, and plays a rising three-tone
alarm through `winsound.Beep` — which drives the timer chip directly, so it works even with the
volume mixer muted.

It re-reads `datetime.now()` every tick rather than accumulating, so it survives laptop sleep,
DST and a clock correction. After a long suspend it does **not** dump the backlog: anything more
than `--stale-seconds` (default 120) late is logged as *missed* and skipped.

Runtime files, both gitignored:

- `state/schedule_daemon.json` — the cursor, so a restart neither repeats nor skips.
- `state/schedule_log.jsonl` — one line per reminder fired or missed. This is the adherence
  record; it is the only honest answer to *"did I actually keep the schedule this week?"*.

**To have it running at 03:00 without remembering to start it**, put a shortcut to
`launch_schedule.bat` in the Startup folder (`Win+R` → `shell:startup`), or register it as a
Task Scheduler task with trigger *At log on*.

### In the browser

The bar under the header shows the current block, a progress track, a live countdown, and what
comes next — and fires the same reminders as an on-page overlay plus a system notification.

**Click "🔔 Enable alarm" once per browser.** Browsers refuse to play audio until a user gesture,
so until you click it the overlay appears silently. The choice is remembered. The tab must stay
open for browser alarms; the daemon is what covers you when it is not.

---

## Tests

```powershell
python -m pytest trainer/tests -q
```

`tests/test_schedule.py` pins the reminder doctrine — which boundaries sound and which do not,
that the wake-up fires at 03:00 rather than 02:55, and that the firing window is half-open so
nothing can fire twice. Each of those guards has been mutation-checked.
