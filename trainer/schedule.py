"""
Knowledge Trainer — Timetable engine.

Pure, testable logic for a 24/7 time-based day plan: which block is running right
now, what comes next, and which reminders must fire. No I/O beyond reading the
timetable JSON; no clock of its own — every function takes `now` explicitly, so
the whole thing is deterministic under test.

Reminder doctrine
-----------------
Every block boundary produces exactly ONE reminder, `lead_minutes` before it.
That single reminder is simultaneously "the current session is about to end" and
"the next session is about to start", so nothing is ever announced twice.

It plays an alarm sound IFF the block STARTING at that boundary is not a quiet
kind (rest / sleep). The consequence is exactly the rule Thejus asked for:

    work -> rest boundary   silent   (he is concentrating; do not break it)
    rest -> work boundary   ALARM    (get him back to the desk after the break)

The one exception is the wake-up block, which carries `start_alarm` and therefore
sounds AT its start instead of five minutes before it.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

BASE_DIR = Path(__file__).resolve().parent
TIMETABLE_FILE = BASE_DIR / "content" / "timetable.json"

MINUTES_PER_DAY = 24 * 60

#: Boundaries *into* one of these kinds are announced silently.
QUIET_KINDS = frozenset({"rest", "sleep"})

#: Purely cosmetic; used by the web UI and the daemon banner.
KIND_ICONS = {
    "chore": "🧹",
    "focus": "🧘",
    "work": "📚",
    "meal": "🍲",
    "rest": "☕",
    "sleep": "🌙",
}


# =====================================================================
# 1. Time helpers
# =====================================================================

def parse_hhmm(value: str) -> int:
    """Parse 'HH:MM' into minutes since midnight. Raises ValueError if malformed."""
    text = str(value).strip()
    parts = text.split(":")
    if len(parts) != 2:
        raise ValueError(f"Bad time {value!r}: expected 'HH:MM'")
    hours, minutes = int(parts[0]), int(parts[1])
    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        raise ValueError(f"Bad time {value!r}: out of range")
    return hours * 60 + minutes


def format_hhmm(minutes: int) -> str:
    """Format minutes-since-midnight as 'HH:MM' (wrapping past 24h)."""
    minutes %= MINUTES_PER_DAY
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def format_duration(seconds: float) -> str:
    """Human countdown: '1h 24m' / '9m 05s' / '48s'."""
    seconds = max(0, int(seconds))
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h {minutes:02d}m"
    if minutes:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"


# =====================================================================
# 2. Data model
# =====================================================================

@dataclass(frozen=True)
class BlockSpec:
    """One timetable row, in minutes-since-midnight. `end_min` may exceed 1440
    for the single block that wraps past midnight."""

    start_min: int
    end_min: int
    task: str
    kind: str = "work"
    note: str = ""
    start_alarm: bool = False
    lead_sound: Optional[bool] = None

    @property
    def duration_minutes(self) -> int:
        return self.end_min - self.start_min

    @property
    def is_quiet(self) -> bool:
        return self.kind in QUIET_KINDS

    @property
    def icon(self) -> str:
        return KIND_ICONS.get(self.kind, "•")

    def wants_lead_sound(self) -> bool:
        """Should the 5-minute reminder *into* this block make a noise?"""
        if self.lead_sound is not None:
            return bool(self.lead_sound)
        return not self.is_quiet

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": format_hhmm(self.start_min),
            "end": format_hhmm(self.end_min),
            "start_min": self.start_min,
            "end_min": self.end_min,
            "duration_minutes": self.duration_minutes,
            "task": self.task,
            "kind": self.kind,
            "note": self.note,
            "icon": self.icon,
            "quiet": self.is_quiet,
            "start_alarm": self.start_alarm,
            "lead_sound": self.wants_lead_sound(),
        }


@dataclass(frozen=True)
class Block:
    """A `BlockSpec` pinned to absolute local datetimes on a particular day."""

    spec: BlockSpec
    start: datetime
    end: datetime

    @property
    def task(self) -> str:
        return self.spec.task

    @property
    def kind(self) -> str:
        return self.spec.kind

    def contains(self, moment: datetime) -> bool:
        return self.start <= moment < self.end

    def to_dict(self) -> Dict[str, Any]:
        payload = self.spec.to_dict()
        payload["start_iso"] = self.start.isoformat()
        payload["end_iso"] = self.end.isoformat()
        return payload


@dataclass(frozen=True)
class Reminder:
    """A single thing to announce at `fire_at`."""

    fire_at: datetime
    boundary: datetime
    event: str          # "lead" | "start"
    sound: bool
    incoming: BlockSpec
    outgoing: Optional[BlockSpec]

    @property
    def title(self) -> str:
        if self.event == "start":
            return f"{self.incoming.icon}  {self.incoming.task} — NOW"
        return f"{self.incoming.icon}  {self.incoming.task} in {self.lead_minutes} min"

    @property
    def lead_minutes(self) -> int:
        return max(0, round((self.boundary - self.fire_at).total_seconds() / 60))

    @property
    def body(self) -> str:
        at = self.boundary.strftime("%H:%M")
        if self.event == "start":
            return f"Starts now, {at}. {self.incoming.note}".strip()
        lines = []
        if self.outgoing is not None:
            lines.append(f"{self.outgoing.task} ends at {at}.")
        lines.append(f"Then: {self.incoming.task} ({at}–{format_hhmm(self.incoming.end_min)}).")
        if self.incoming.note:
            lines.append(self.incoming.note)
        return " ".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fire_at": self.fire_at.isoformat(),
            "boundary": self.boundary.isoformat(),
            "event": self.event,
            "sound": self.sound,
            "title": self.title,
            "body": self.body,
            "incoming": self.incoming.to_dict(),
            "outgoing": self.outgoing.to_dict() if self.outgoing else None,
        }


@dataclass(frozen=True)
class Timetable:
    lead_minutes: int
    specs: Tuple[BlockSpec, ...]
    name: str = "timetable"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "lead_minutes": self.lead_minutes,
            "blocks": [s.to_dict() for s in self.specs],
        }


# =====================================================================
# 3. Loading and validation
# =====================================================================

def build_timetable(payload: Dict[str, Any]) -> Timetable:
    """Turn parsed JSON into a validated `Timetable`."""
    raw_blocks = payload.get("blocks") or []
    if not raw_blocks:
        raise ValueError("timetable has no blocks")

    specs: List[BlockSpec] = []
    for row in raw_blocks:
        start_min = parse_hhmm(row["start"])
        end_min = parse_hhmm(row["end"])
        if end_min <= start_min:
            # The single wrapping block: 22:00 -> 03:00 becomes 1320 -> 1620.
            end_min += MINUTES_PER_DAY
        specs.append(
            BlockSpec(
                start_min=start_min,
                end_min=end_min,
                task=str(row["task"]).strip(),
                kind=str(row.get("kind", "work")).strip().lower(),
                note=str(row.get("note", "")).strip(),
                start_alarm=bool(row.get("start_alarm", False)),
                lead_sound=row.get("lead_sound"),
            )
        )

    specs.sort(key=lambda s: s.start_min)
    validate_specs(specs)
    lead = int(payload.get("lead_minutes", 5))
    if lead < 1:
        raise ValueError("lead_minutes must be >= 1")
    return Timetable(lead_minutes=lead, specs=tuple(specs), name=str(payload.get("name", "timetable")))


def validate_specs(specs: Sequence[BlockSpec]) -> None:
    """The day must tile exactly: contiguous, no overlap, wrapping back to the
    first block's start after 24h. A gap here means silent dead time in a
    schedule whose whole purpose is that there is none."""
    wrapping = [s for s in specs if s.end_min > MINUTES_PER_DAY]
    if len(wrapping) > 1:
        raise ValueError("at most one block may wrap past midnight")

    for prev, nxt in zip(specs, specs[1:]):
        if nxt.start_min != prev.end_min:
            raise ValueError(
                f"timetable is not contiguous: {prev.task!r} ends {format_hhmm(prev.end_min)} "
                f"but {nxt.task!r} starts {format_hhmm(nxt.start_min)}"
            )

    total = sum(s.duration_minutes for s in specs)
    if total != MINUTES_PER_DAY:
        raise ValueError(f"timetable covers {total} minutes, expected {MINUTES_PER_DAY}")

    last_end = specs[-1].end_min % MINUTES_PER_DAY
    if last_end != specs[0].start_min:
        raise ValueError(
            f"timetable does not close the loop: last block ends {format_hhmm(last_end)}, "
            f"first block starts {format_hhmm(specs[0].start_min)}"
        )


def load_timetable(path: Optional[Path] = None) -> Timetable:
    """Read and validate the timetable JSON (defaults to content/timetable.json)."""
    target = Path(path) if path else TIMETABLE_FILE
    with open(target, "r", encoding="utf-8") as handle:
        return build_timetable(json.load(handle))


# =====================================================================
# 4. Placing blocks on the clock
# =====================================================================

def blocks_for_day(timetable: Timetable, day: date) -> List[Block]:
    """Absolute blocks whose *start* falls on `day`."""
    midnight = datetime(day.year, day.month, day.day)
    return [
        Block(spec=s, start=midnight + timedelta(minutes=s.start_min), end=midnight + timedelta(minutes=s.end_min))
        for s in timetable.specs
    ]


def window_blocks(timetable: Timetable, now: datetime, days_back: int = 1, days_forward: int = 2) -> List[Block]:
    """Blocks spanning yesterday..tomorrow so midnight-wrapping blocks resolve."""
    out: List[Block] = []
    for offset in range(-days_back, days_forward + 1):
        out.extend(blocks_for_day(timetable, (now + timedelta(days=offset)).date()))
    out.sort(key=lambda b: b.start)
    return out


def current_block(timetable: Timetable, now: datetime) -> Block:
    """The block running at `now`. The timetable tiles 24h, so this always exists."""
    for block in window_blocks(timetable, now):
        if block.contains(now):
            return block
    raise RuntimeError(f"no block covers {now.isoformat()} — timetable validation should have caught this")


def next_block(timetable: Timetable, now: datetime) -> Block:
    """The block that begins when the current one ends."""
    boundary = current_block(timetable, now).end
    for block in window_blocks(timetable, now):
        if block.start == boundary:
            return block
    raise RuntimeError(f"no block starts at {boundary.isoformat()}")


def upcoming_blocks(timetable: Timetable, now: datetime, count: int = 4) -> List[Block]:
    """The next `count` blocks after the current one, in order."""
    boundary = current_block(timetable, now).end
    later = [b for b in window_blocks(timetable, now) if b.start >= boundary]
    return later[:count]


# =====================================================================
# 5. Reminders
# =====================================================================

def reminders_for_block(timetable: Timetable, block: Block, previous: Optional[Block]) -> List[Reminder]:
    """Every reminder attached to one block's start boundary."""
    out: List[Reminder] = []
    if block.spec.start_alarm:
        # A wake-up alarm belongs AT the boundary, not five minutes before it —
        # nobody wants to be woken at 02:55 to be told about 03:00.
        out.append(
            Reminder(
                fire_at=block.start,
                boundary=block.start,
                event="start",
                sound=True,
                incoming=block.spec,
                outgoing=previous.spec if previous else None,
            )
        )
        return out

    out.append(
        Reminder(
            fire_at=block.start - timedelta(minutes=timetable.lead_minutes),
            boundary=block.start,
            event="lead",
            sound=block.spec.wants_lead_sound(),
            incoming=block.spec,
            outgoing=previous.spec if previous else None,
        )
    )
    return out


def all_reminders(timetable: Timetable, now: datetime) -> List[Reminder]:
    """Every reminder in the yesterday..tomorrow window, chronologically."""
    blocks = window_blocks(timetable, now)
    by_end = {b.end: b for b in blocks}
    out: List[Reminder] = []
    for block in blocks:
        out.extend(reminders_for_block(timetable, block, by_end.get(block.start)))
    out.sort(key=lambda r: r.fire_at)
    return out


def reminders_between(timetable: Timetable, after: datetime, until: datetime) -> List[Reminder]:
    """Reminders with `after < fire_at <= until`. Half-open at the bottom so a
    polling loop that advances its cursor can never fire the same one twice."""
    return [r for r in all_reminders(timetable, until) if after < r.fire_at <= until]


def next_reminder(timetable: Timetable, now: datetime) -> Optional[Reminder]:
    """The first reminder strictly after `now`."""
    for reminder in all_reminders(timetable, now):
        if reminder.fire_at > now:
            return reminder
    return None


# =====================================================================
# 6. The one call the UI and the daemon both use
# =====================================================================

def day_state(timetable: Timetable, now: datetime) -> Dict[str, Any]:
    """Everything a client needs to render the live bar."""
    current = current_block(timetable, now)
    nxt = next_block(timetable, now)
    elapsed = (now - current.start).total_seconds()
    remaining = (current.end - now).total_seconds()
    total = (current.end - current.start).total_seconds()
    upcoming = next_reminder(timetable, now)

    return {
        "now": now.isoformat(),
        "lead_minutes": timetable.lead_minutes,
        "current": current.to_dict(),
        "next": nxt.to_dict(),
        "elapsed_seconds": round(elapsed),
        "remaining_seconds": round(remaining),
        "progress": round(elapsed / total, 4) if total else 0.0,
        "remaining_human": format_duration(remaining),
        "in_lead_window": remaining <= timetable.lead_minutes * 60,
        "next_reminder": upcoming.to_dict() if upcoming else None,
        "seconds_to_next_reminder": round((upcoming.fire_at - now).total_seconds()) if upcoming else None,
        "upcoming": [b.to_dict() for b in upcoming_blocks(timetable, now, count=4)],
    }
