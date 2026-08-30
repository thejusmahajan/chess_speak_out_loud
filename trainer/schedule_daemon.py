"""
Knowledge Trainer — 24/7 timetable daemon.

Runs all day in the background and announces every block boundary in the
timetable, whether or not a browser is open. This is the part that has to be
reliable: the web UI is a convenience, this is the alarm clock.

    python -m trainer.schedule_daemon              # run it
    python -m trainer.schedule_daemon --check      # print the next reminders, exit
    python -m trainer.schedule_daemon --test-alarm # prove the sound works, exit
    python -m trainer.schedule_daemon --no-gui     # console only, no banner

What it does at a boundary
--------------------------
* Pops an always-on-top banner that cannot hide behind the IDE.
* Plays a rising three-tone alarm — but ONLY when the block starting at that
  boundary is real work. A boundary into a rest block is announced silently,
  because a session ending is not a reason to break concentration.

Design notes
------------
* The clock is re-read from `datetime.now()` every tick, never accumulated, so
  the daemon survives laptop sleep, DST and a system clock correction.
* After a long suspend the daemon does NOT dump the backlog: reminders older
  than `--stale-seconds` are logged as missed and skipped.
* The timetable JSON is re-read whenever its mtime changes, so editing the
  schedule takes effect without restarting anything.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from trainer import schedule as schedule_engine
from trainer.schedule import Reminder, Timetable

BASE_DIR = Path(__file__).resolve().parent
TIMETABLE_FILE = BASE_DIR / "content" / "timetable.json"
STATE_DIR = BASE_DIR / "state"
CURSOR_FILE = STATE_DIR / "schedule_daemon.json"
LOG_FILE = STATE_DIR / "schedule_log.jsonl"

IS_WINDOWS = sys.platform.startswith("win")

BANNER_COLOURS = {
    "chore": ("#1f2b1a", "#7ee787"),
    "focus": ("#1b2432", "#a371f7"),
    "work": ("#101d2e", "#58a6ff"),
    "meal": ("#2b210f", "#e3b341"),
    "rest": ("#161b22", "#8b949e"),
    "sleep": ("#12151c", "#6e7681"),
}


# =====================================================================
# 1. Sound
# =====================================================================

class Alarm:
    """A rising three-tone pattern, repeated until it is stopped or times out.

    winsound.Beep drives the motherboard timer directly, so it works with the
    volume mixer muted and does not depend on any audio file being present.
    """

    PATTERN = ((880, 180), (1175, 180), (1568, 320))
    GAP_SECONDS = 0.9

    def __init__(self) -> None:
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def play(self, repeats: int = 5) -> None:
        self.stop()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, args=(repeats, self._stop), daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _run(self, repeats: int, stop: threading.Event) -> None:
        try:
            import winsound  # noqa: WPS433 — Windows only, imported lazily on purpose
        except ImportError:
            for _ in range(repeats):
                if stop.is_set():
                    return
                sys.stdout.write("\a")
                sys.stdout.flush()
                if stop.wait(self.GAP_SECONDS):
                    return
            return

        for _ in range(repeats):
            for freq, duration in self.PATTERN:
                if stop.is_set():
                    return
                try:
                    winsound.Beep(freq, duration)
                except RuntimeError:
                    return
            if stop.wait(self.GAP_SECONDS):
                return


# =====================================================================
# 2. Banner
# =====================================================================

class Banner:
    """An always-on-top popup. Falls back to console-only if Tk is unavailable."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self._tk = None
        self._root = None
        if not enabled:
            return
        try:
            import tkinter as tk  # noqa: WPS433
        except ImportError:
            print("[banner] tkinter unavailable — running console-only", flush=True)
            self.enabled = False
            return
        self._tk = tk
        self._root = tk.Tk()
        self._root.withdraw()

    def pump(self) -> None:
        """Service the Tk event loop. Called from the daemon's own tick loop so
        we never hand control of the process over to Tk's mainloop."""
        if self._root is None:
            return
        try:
            self._root.update()
        except Exception:  # window torn down under us; degrade rather than die
            self._root = None
            self.enabled = False

    def show(self, reminder: Reminder, seconds: int, on_dismiss) -> None:
        if not self.enabled or self._root is None:
            return
        tk = self._tk
        bg, fg = BANNER_COLOURS.get(reminder.incoming.kind, ("#161b22", "#c9d1d9"))

        win = tk.Toplevel(self._root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg=fg)

        frame = tk.Frame(win, bg=bg, padx=28, pady=18)
        frame.pack(padx=3, pady=3, fill="both", expand=True)

        tk.Label(
            frame, text=reminder.title, bg=bg, fg=fg,
            font=("Segoe UI", 22, "bold"), justify="left", anchor="w",
        ).pack(fill="x")
        tk.Label(
            frame, text=reminder.body, bg=bg, fg="#c9d1d9", wraplength=680,
            font=("Segoe UI", 12), justify="left", anchor="w",
        ).pack(fill="x", pady=(6, 0))
        hint = tk.Label(
            frame, text="click or press Esc to dismiss", bg=bg, fg="#6e7681",
            font=("Segoe UI", 9), anchor="w",
        )
        hint.pack(fill="x", pady=(10, 0))

        win.update_idletasks()
        width, height = win.winfo_width(), win.winfo_height()
        x = (win.winfo_screenwidth() - width) // 2
        win.geometry(f"+{x}+60")

        closed = {"done": False}

        def close(_event=None) -> None:
            if closed["done"]:
                return
            closed["done"] = True
            on_dismiss()
            try:
                win.destroy()
            except Exception:
                pass

        win.bind("<Button-1>", close)
        win.bind("<Escape>", close)
        for child in frame.winfo_children():
            child.bind("<Button-1>", close)
        win.after(max(1, seconds) * 1000, close)
        win.focus_force()


# =====================================================================
# 3. Cursor + log persistence
# =====================================================================

def read_cursor() -> Optional[datetime]:
    """The last moment we have already announced, so a restart does not repeat."""
    try:
        with open(CURSOR_FILE, "r", encoding="utf-8") as handle:
            return datetime.fromisoformat(json.load(handle)["cursor"])
    except Exception:
        return None


def write_cursor(moment: datetime, attempts: int = 4) -> bool:
    """Persist the cursor, and double as the daemon's heartbeat — the browser
    reads this file's freshness to decide whether the desktop alarm already has
    him covered, so it is written on a tick even when nothing fired.

    os.replace on this machine is intermittently denied with WinError 5 when a
    virus scanner or an indexer holds the target (a documented failure in this
    repo). Retry, and if it still will not land, say so and CARRY ON — a cursor
    write must never be the thing that takes the alarm clock down.
    """
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CURSOR_FILE.with_suffix(".tmp")
    payload = {"cursor": moment.isoformat(), "pid": os.getpid()}
    for attempt in range(attempts):
        try:
            with open(tmp, "w", encoding="utf-8") as handle:
                json.dump(payload, handle)
            tmp.replace(CURSOR_FILE)
            return True
        except OSError:
            if attempt == attempts - 1:
                return False
            time.sleep(0.05 * (attempt + 1))
    return False


def log_event(kind: str, reminder: Reminder, extra: Optional[dict] = None) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "logged_at": datetime.now().isoformat(),
        "event": kind,
        "fire_at": reminder.fire_at.isoformat(),
        "sound": reminder.sound,
        "task": reminder.incoming.task,
        "block": f"{schedule_engine.format_hhmm(reminder.incoming.start_min)}"
                 f"-{schedule_engine.format_hhmm(reminder.incoming.end_min)}",
    }
    entry.update(extra or {})
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as exc:
        say(f"[log] could not append to {LOG_FILE.name}: {exc}")


# =====================================================================
# 4. Console output that survives a cp1252 terminal
# =====================================================================

def say(text: str) -> None:
    """Print without ever dying on a Windows console that cannot encode emoji."""
    try:
        print(text, flush=True)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "ascii"
        print(text.encode(encoding, "replace").decode(encoding), flush=True)


# =====================================================================
# 5. The daemon
# =====================================================================

class ScheduleDaemon:
    def __init__(
        self,
        timetable_file: Path = TIMETABLE_FILE,
        gui: bool = True,
        stale_seconds: int = 120,
        tick_seconds: float = 1.0,
        alarm_seconds: int = 25,
        silent_seconds: int = 12,
        status_seconds: int = 300,
        cursor_seconds: float = 3.0,
    ) -> None:
        self.timetable_file = Path(timetable_file)
        self.stale_seconds = stale_seconds
        self.tick_seconds = tick_seconds
        self.alarm_seconds = alarm_seconds
        self.silent_seconds = silent_seconds
        self.alarm = Alarm()
        self.banner = Banner(enabled=gui)
        self._timetable: Optional[Timetable] = None
        self._mtime: Optional[float] = None
        self._last_status = ""
        self._last_status_at: Optional[datetime] = None
        self.status_seconds = status_seconds
        self.cursor_seconds = cursor_seconds

    # -- timetable -----------------------------------------------------
    def timetable(self) -> Timetable:
        """Hot-reload the JSON when it changes; keep the last good copy if an
        edit is mid-flight or broken, rather than taking the alarm clock down."""
        try:
            mtime = self.timetable_file.stat().st_mtime
        except OSError:
            if self._timetable is None:
                raise
            return self._timetable

        if self._timetable is None or mtime != self._mtime:
            try:
                self._timetable = schedule_engine.load_timetable(self.timetable_file)
                self._mtime = mtime
                say(f"[timetable] loaded {self.timetable_file.name} "
                    f"({len(self._timetable.specs)} blocks, {self._timetable.lead_minutes} min lead)")
            except (ValueError, OSError, json.JSONDecodeError) as exc:
                if self._timetable is None:
                    raise
                say(f"[timetable] KEEPING previous version — reload failed: {exc}")
                self._mtime = mtime
        return self._timetable

    # -- firing --------------------------------------------------------
    def fire(self, reminder: Reminder) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        tag = "ALARM " if reminder.sound else "silent"
        say(f"\n[{stamp}] {tag} | {reminder.title}\n           {reminder.body}")
        log_event("fired", reminder)

        if reminder.sound:
            self.alarm.play()
            seconds = self.alarm_seconds
        else:
            seconds = self.silent_seconds
        self.banner.show(reminder, seconds, on_dismiss=self.alarm.stop)

    # -- status line ---------------------------------------------------
    def status(self, now: datetime) -> None:
        """One line when the block changes, plus a heartbeat every few minutes.
        A per-second countdown in the console would bury the reminders it is
        there to make visible."""
        state = schedule_engine.day_state(self.timetable(), now)
        key = state["current"]["task"] + "|" + state["current"]["start"]
        due_heartbeat = (
            self._last_status_at is None
            or (now - self._last_status_at).total_seconds() >= self.status_seconds
        )
        if key == self._last_status and not due_heartbeat:
            return
        say(f"[{now.strftime('%H:%M')}] {state['current']['icon']} {state['current']['task']}"
            f"  ·  {state['remaining_human']} left"
            f"  ·  next: {state['next']['task']} at {state['next']['start']}")
        self._last_status = key
        self._last_status_at = now

    # -- main loop -----------------------------------------------------
    def run(self) -> None:
        now = datetime.now()
        cursor = read_cursor()
        if cursor is None or not (now - timedelta(seconds=self.stale_seconds) <= cursor <= now):
            # No usable cursor (first run, long downtime, or a clock jump):
            # start clean at "now" so we do not replay an old backlog.
            cursor = now - timedelta(seconds=self.stale_seconds)

        say("=" * 72)
        say("  Knowledge Trainer — timetable daemon")
        say(f"  started {now:%Y-%m-%d %H:%M:%S}   ·   Ctrl+C to stop")
        say("=" * 72)
        self.status(now)
        last_write: Optional[datetime] = None
        cursor_warned = False

        try:
            while True:
                now = datetime.now()

                if now < cursor - timedelta(seconds=5):
                    # Clock moved backwards (DST or an NTP correction).
                    say(f"[clock] jumped backwards; resyncing cursor to {now:%H:%M:%S}")
                    cursor = now - timedelta(seconds=1)

                due = schedule_engine.reminders_between(self.timetable(), cursor, now)
                for reminder in due:
                    age = (now - reminder.fire_at).total_seconds()
                    if age > self.stale_seconds:
                        say(f"[missed] {reminder.fire_at:%H:%M} {reminder.incoming.task} "
                            f"({int(age)}s late — machine was asleep?)")
                        log_event("missed", reminder, {"late_seconds": int(age)})
                        continue
                    self.fire(reminder)

                cursor = now
                # One replace a second is ~86k pointless writes a day, each a
                # chance at the AV race above. Every few seconds is still a
                # fresh enough heartbeat for the browser to trust.
                if (last_write is None
                        or (now - last_write).total_seconds() >= self.cursor_seconds):
                    if write_cursor(cursor):
                        last_write = now
                    elif not cursor_warned:
                        say("[cursor] cannot write the heartbeat file (AV or a reader holds "
                            "it); reminders are unaffected, the browser just will not see "
                            "that the daemon is running")
                        cursor_warned = True
                self.status(now)
                self.banner.pump()
                time.sleep(self.tick_seconds)
        except KeyboardInterrupt:
            self.alarm.stop()
            say("\n[stopped] timetable daemon shut down.")


# =====================================================================
# 6. CLI
# =====================================================================

def cmd_check(timetable_file: Path, count: int) -> int:
    timetable = schedule_engine.load_timetable(timetable_file)
    now = datetime.now()
    state = schedule_engine.day_state(timetable, now)
    say(f"now {now:%H:%M:%S}")
    say(f"  current : {state['current']['task']}  ({state['current']['start']}–{state['current']['end']}), "
        f"{state['remaining_human']} left")
    say(f"  next    : {state['next']['task']}  at {state['next']['start']}")
    say("")
    say(f"next {count} reminders:")
    window = schedule_engine.reminders_between(timetable, now, now + timedelta(hours=24))
    for reminder in window[:count]:
        tag = "ALARM " if reminder.sound else "silent"
        say(f"  {reminder.fire_at:%a %H:%M}  {tag}  {reminder.title}")
        say(f"                        {reminder.body}")
    return 0


def cmd_test_alarm() -> int:
    say("Playing the alarm pattern (about 5 seconds)…")
    alarm = Alarm()
    alarm.play(repeats=3)
    time.sleep(5)
    alarm.stop()
    say("Done. If you heard nothing, check that the PC speaker/system sounds are not disabled.")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Knowledge Trainer timetable daemon")
    parser.add_argument("--timetable", type=Path, default=TIMETABLE_FILE)
    parser.add_argument("--no-gui", action="store_true", help="console only, no popup banner")
    parser.add_argument("--check", action="store_true", help="print upcoming reminders and exit")
    parser.add_argument("--count", type=int, default=8, help="how many reminders --check prints")
    parser.add_argument("--test-alarm", action="store_true", help="play the alarm and exit")
    parser.add_argument("--stale-seconds", type=int, default=120,
                        help="skip reminders older than this (suspend/resume guard)")
    parser.add_argument("--alarm-seconds", type=int, default=25, help="banner dwell for alarm reminders")
    parser.add_argument("--silent-seconds", type=int, default=12, help="banner dwell for silent reminders")
    args = parser.parse_args(argv)

    if args.test_alarm:
        return cmd_test_alarm()
    if args.check:
        return cmd_check(args.timetable, args.count)

    ScheduleDaemon(
        timetable_file=args.timetable,
        gui=not args.no_gui,
        stale_seconds=args.stale_seconds,
        alarm_seconds=args.alarm_seconds,
        silent_seconds=args.silent_seconds,
    ).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
