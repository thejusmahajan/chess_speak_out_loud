"""
Unit tests for the Knowledge Trainer timetable engine.

The point of these is the reminder doctrine, which is easy to get subtly wrong:
one reminder per boundary, sounding only when the block *starting* at that
boundary is real work.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta

import pytest

from trainer.schedule import (
    MINUTES_PER_DAY,
    BlockSpec,
    Timetable,
    all_reminders,
    build_timetable,
    current_block,
    day_state,
    format_duration,
    format_hhmm,
    load_timetable,
    next_block,
    parse_hhmm,
    reminders_between,
    upcoming_blocks,
    validate_specs,
)


# =====================================================================
# 0. Fixtures
# =====================================================================

def _payload(blocks, lead_minutes=5):
    return {"lead_minutes": lead_minutes, "blocks": blocks}


TINY = _payload([
    {"start": "06:00", "end": "06:30", "task": "Wake", "kind": "chore", "start_alarm": True},
    {"start": "06:30", "end": "08:00", "task": "Study", "kind": "work"},
    {"start": "08:00", "end": "08:15", "task": "Rest", "kind": "rest"},
    {"start": "08:15", "end": "22:00", "task": "Long work", "kind": "work"},
    {"start": "22:00", "end": "06:00", "task": "Sleep", "kind": "sleep"},
])


@pytest.fixture
def tiny():
    return build_timetable(TINY)


@pytest.fixture
def real():
    """The actual timetable shipped in content/timetable.json."""
    return load_timetable()


# =====================================================================
# 1. Time helpers
# =====================================================================

def test_parse_hhmm_roundtrip():
    assert parse_hhmm("00:00") == 0
    assert parse_hhmm("03:00") == 180
    assert parse_hhmm("23:59") == 1439
    assert format_hhmm(180) == "03:00"
    assert format_hhmm(1620) == "03:00"  # a wrapping end time folds back


@pytest.mark.parametrize("bad", ["25:00", "12:60", "1200", "", "ab:cd"])
def test_parse_hhmm_rejects_garbage(bad):
    with pytest.raises(ValueError):
        parse_hhmm(bad)


def test_format_duration():
    assert format_duration(45) == "45s"
    assert format_duration(305) == "5m 05s"
    assert format_duration(5040) == "1h 24m"
    assert format_duration(-10) == "0s"


# =====================================================================
# 2. Validation — a gap in the day is a silent failure, so it must raise
# =====================================================================

def test_gap_in_the_day_is_rejected():
    with pytest.raises(ValueError, match="not contiguous"):
        build_timetable(_payload([
            {"start": "06:00", "end": "07:00", "task": "A"},
            {"start": "07:30", "end": "06:00", "task": "B"},
        ]))


def test_overlap_is_rejected():
    with pytest.raises(ValueError, match="not contiguous"):
        build_timetable(_payload([
            {"start": "06:00", "end": "07:00", "task": "A"},
            {"start": "06:30", "end": "06:00", "task": "B"},
        ]))


def test_short_day_is_rejected():
    with pytest.raises(ValueError, match="covers"):
        validate_specs([
            BlockSpec(0, 60, "A"),
            BlockSpec(60, 120, "B"),
        ])


def test_two_wrapping_blocks_rejected():
    with pytest.raises(ValueError, match="wrap"):
        validate_specs([
            BlockSpec(0, MINUTES_PER_DAY + 10, "A"),
            BlockSpec(MINUTES_PER_DAY + 10, MINUTES_PER_DAY + 20, "B"),
        ])


def test_empty_timetable_rejected():
    with pytest.raises(ValueError, match="no blocks"):
        build_timetable(_payload([]))


# =====================================================================
# 3. The shipped timetable
# =====================================================================

def test_real_timetable_loads_and_tiles_the_whole_day(real):
    assert len(real.specs) == 24
    assert real.lead_minutes == 5
    assert sum(s.duration_minutes for s in real.specs) == MINUTES_PER_DAY


def test_real_timetable_matches_the_authored_plan(real):
    by_start = {format_hhmm(s.start_min): s for s in real.specs}
    assert by_start["03:00"].task.startswith("Wake up")
    assert by_start["03:00"].start_alarm is True
    assert by_start["04:30"].task == "Interview prep"
    assert by_start["06:15"].task == "Coursera — ML"
    assert by_start["10:45"].task == "Statistics + Weiterbildung project revision"
    assert by_start["13:00"].task == "Coursera — ML with Python"
    assert by_start["14:45"].kind == "work" and by_start["14:45"].task == "German"
    assert by_start["16:15"].task == "German"
    assert by_start["18:15"].task == "Revision"
    assert by_start["20:45"].task == "Mech-interp project"
    assert by_start["22:00"].kind == "sleep"
    assert by_start["12:00"].kind == "meal"


# =====================================================================
# 4. Locating the current block
# =====================================================================

def test_current_block_and_next(tiny):
    now = datetime(2026, 8, 30, 7, 0)
    assert current_block(tiny, now).task == "Study"
    assert next_block(tiny, now).task == "Rest"


def test_block_boundary_is_half_open(tiny):
    """08:00 belongs to Rest, not to the Study block that ends at 08:00."""
    assert current_block(tiny, datetime(2026, 8, 30, 7, 59, 59)).task == "Study"
    assert current_block(tiny, datetime(2026, 8, 30, 8, 0, 0)).task == "Rest"


def test_wrapping_block_covers_after_midnight(tiny):
    for probe in [datetime(2026, 8, 30, 23, 30), datetime(2026, 8, 31, 0, 0), datetime(2026, 8, 31, 5, 59)]:
        assert current_block(tiny, probe).task == "Sleep"
    assert current_block(tiny, datetime(2026, 8, 31, 6, 0)).task == "Wake"


def test_wrapping_block_start_is_on_the_previous_day(tiny):
    block = current_block(tiny, datetime(2026, 8, 31, 1, 0))
    assert block.start == datetime(2026, 8, 30, 22, 0)
    assert block.end == datetime(2026, 8, 31, 6, 0)


def test_upcoming_blocks_are_consecutive(tiny):
    blocks = upcoming_blocks(tiny, datetime(2026, 8, 30, 7, 0), count=3)
    assert [b.task for b in blocks] == ["Rest", "Long work", "Sleep"]


def test_every_minute_of_the_day_is_covered(real):
    """No dead minute anywhere in 24h — this is what makes the daemon safe."""
    start = datetime(2026, 8, 30, 0, 0)
    for minute in range(0, MINUTES_PER_DAY, 7):
        current_block(real, start + timedelta(minutes=minute))  # raises if uncovered


# =====================================================================
# 5. Reminder doctrine — the part that must not regress
# =====================================================================

def _day_reminders(timetable, day=datetime(2026, 8, 30)):
    return reminders_between(timetable, day, day + timedelta(days=1))


def test_boundary_into_rest_is_silent(tiny):
    """He is concentrating when a session ends. Do not make a noise."""
    fired = {r.boundary.strftime("%H:%M"): r for r in _day_reminders(tiny)}
    assert fired["08:00"].incoming.task == "Rest"
    assert fired["08:00"].sound is False


def test_boundary_out_of_rest_sounds_the_alarm(tiny):
    """The break ending is exactly when he needs to be pulled back."""
    fired = {r.boundary.strftime("%H:%M"): r for r in _day_reminders(tiny)}
    assert fired["08:15"].incoming.task == "Long work"
    assert fired["08:15"].sound is True


def test_boundary_into_sleep_is_silent(tiny):
    fired = {r.boundary.strftime("%H:%M"): r for r in _day_reminders(tiny)}
    assert fired["22:00"].sound is False


def test_lead_time_is_five_minutes(tiny):
    for reminder in _day_reminders(tiny):
        if reminder.event == "lead":
            assert reminder.boundary - reminder.fire_at == timedelta(minutes=5)


def test_wake_up_alarm_fires_at_the_start_not_before(tiny):
    """A 02:55 pre-alarm for a 03:00 wake-up would wake him five minutes early."""
    wake = [r for r in _day_reminders(tiny) if r.incoming.task == "Wake"]
    assert len(wake) == 1
    assert wake[0].event == "start"
    assert wake[0].sound is True
    assert wake[0].fire_at == wake[0].boundary == datetime(2026, 8, 30, 6, 0)


def test_exactly_one_reminder_per_boundary(tiny):
    """The 'session ending' and 'next session starting' notices are the same
    event; announcing both would double every alert."""
    reminders = _day_reminders(tiny)
    boundaries = [r.boundary for r in reminders]
    assert len(boundaries) == len(set(boundaries))
    assert len(reminders) == len(tiny.specs)


def test_real_timetable_reminder_sound_map(real):
    fired = {r.boundary.strftime("%H:%M"): r.sound for r in _day_reminders(real)}
    # Into work / meals / meditation: ALARM.
    for at in ["03:00", "03:30", "04:30", "06:15", "08:00", "09:00", "10:45",
               "12:00", "13:00", "14:45", "16:15", "18:15", "20:00", "20:45"]:
        assert fired[at] is True, f"{at} should sound"
    # Into rest / sleep: silent.
    for at in ["04:15", "06:00", "07:45", "08:45", "10:30", "12:45",
               "14:30", "16:00", "18:00", "22:00"]:
        assert fired[at] is False, f"{at} should be silent"


def test_lead_sound_override_beats_the_kind_default():
    timetable = build_timetable(_payload([
        {"start": "06:00", "end": "12:00", "task": "A", "kind": "work"},
        {"start": "12:00", "end": "06:00", "task": "Quiet break", "kind": "rest", "lead_sound": True},
    ]))
    fired = {r.boundary.strftime("%H:%M"): r.sound for r in _day_reminders(timetable)}
    assert fired["12:00"] is True


# =====================================================================
# 6. reminders_between — the daemon's firing window
# =====================================================================

def test_window_is_half_open_so_nothing_fires_twice(tiny):
    """The daemon advances its cursor to `now` each tick; a reminder landing
    exactly on the cursor must belong to the earlier tick only."""
    boundary = datetime(2026, 8, 30, 8, 15)
    fire_at = boundary - timedelta(minutes=5)
    first = reminders_between(tiny, fire_at - timedelta(seconds=1), fire_at)
    second = reminders_between(tiny, fire_at, fire_at + timedelta(seconds=1))
    assert [r.boundary for r in first] == [boundary]
    assert second == []


def test_window_across_midnight_finds_the_wake_up(real):
    window = reminders_between(real, datetime(2026, 8, 30, 23, 0), datetime(2026, 8, 31, 4, 0))
    tasks = [r.incoming.task for r in window]
    assert any(t.startswith("Wake up") for t in tasks)
    assert "Meditation" in tasks


def test_a_quiet_hour_yields_nothing(tiny):
    assert reminders_between(tiny, datetime(2026, 8, 30, 9, 0), datetime(2026, 8, 30, 10, 0)) == []


def test_reminders_are_chronological(real):
    fired = all_reminders(real, datetime(2026, 8, 30, 12, 0))
    assert fired == sorted(fired, key=lambda r: r.fire_at)


# =====================================================================
# 7. day_state — the payload the UI and daemon render
# =====================================================================

def test_day_state_shape_and_countdown(real):
    state = day_state(real, datetime(2026, 8, 30, 5, 57, 0))
    assert state["current"]["task"] == "Interview prep"
    assert state["next"]["task"] == "Rest"
    assert state["remaining_seconds"] == 180
    assert state["remaining_human"] == "3m 00s"
    assert state["in_lead_window"] is True
    assert 0 < state["progress"] < 1
    assert len(state["upcoming"]) == 4


def test_day_state_next_reminder_carries_the_sound_decision(real):
    state = day_state(real, datetime(2026, 8, 30, 6, 1, 0))
    assert state["current"]["task"] == "Rest"
    assert state["next_reminder"]["boundary"].endswith("06:15:00")
    assert state["next_reminder"]["sound"] is True
    assert state["seconds_to_next_reminder"] == 9 * 60


def test_day_state_not_in_lead_window_mid_session(real):
    state = day_state(real, datetime(2026, 8, 30, 5, 0, 0))
    assert state["in_lead_window"] is False


def test_reminder_body_names_both_sides_of_the_boundary(real):
    reminder = next(r for r in _day_reminders(real) if r.boundary.strftime("%H:%M") == "06:15")
    assert "Rest ends at 06:15" in reminder.body
    assert "Coursera — ML" in reminder.body


def test_timetable_to_dict_is_json_shaped(real):
    payload = real.to_dict()
    assert payload["lead_minutes"] == 5
    first = payload["blocks"][0]
    for key in ("start", "end", "start_min", "end_min", "task", "kind", "icon", "lead_sound", "start_alarm"):
        assert key in first


# =====================================================================
# 8. The daemon heartbeat — what stops the tab and the daemon both sounding
# =====================================================================

def _write_cursor(state_dir, moment, pid=4242):
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "schedule_daemon.json").write_text(
        json.dumps({"cursor": moment.isoformat(), "pid": pid}), encoding="utf-8"
    )


@pytest.fixture
def client(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from trainer import app as trainer_app

    monkeypatch.setattr(trainer_app, "STATE_DIR", tmp_path)
    return TestClient(trainer_app.app), tmp_path


def test_daemon_reported_alive_when_the_heartbeat_is_fresh(client):
    api, state_dir = client
    _write_cursor(state_dir, datetime.now())
    body = api.get("/api/schedule/daemon").json()
    assert body["alive"] is True
    assert body["pid"] == 4242
    assert body["age_seconds"] < 5


def test_daemon_reported_dead_when_the_heartbeat_is_stale(client):
    """A killed daemon stops rewriting the file; after the staleness window the
    browser must take the sound back rather than assume it is covered."""
    api, state_dir = client
    _write_cursor(state_dir, datetime.now() - timedelta(seconds=120))
    body = api.get("/api/schedule/daemon").json()
    assert body["alive"] is False
    assert body["age_seconds"] > 100


def test_daemon_reported_dead_when_there_is_no_heartbeat_file(client):
    api, state_dir = client
    body = api.get("/api/schedule/daemon").json()
    assert body == {"alive": False, "last_seen": None, "age_seconds": None, "pid": None}


def test_daemon_reported_dead_when_the_heartbeat_file_is_corrupt(client):
    """A half-written file must read as 'not covered', never as 'covered'."""
    api, state_dir = client
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "schedule_daemon.json").write_text('{"cursor": "not-a-', encoding="utf-8")
    assert api.get("/api/schedule/daemon").json()["alive"] is False


def test_a_heartbeat_from_the_future_is_not_alive(client):
    """A clock jump must not latch the browser silent for hours."""
    api, state_dir = client
    _write_cursor(state_dir, datetime.now() + timedelta(hours=2))
    assert api.get("/api/schedule/daemon").json()["alive"] is False


def test_schedule_endpoints_answer(client):
    api, _ = client
    day = api.get("/api/schedule").json()
    assert len(day["blocks"]) == 24
    live = api.get("/api/schedule/now").json()
    assert live["current"]["task"]
    assert live["next"]["task"]
