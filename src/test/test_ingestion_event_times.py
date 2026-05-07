import json
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from app.ingestion.adapters import _extract_json_ld_events, _normalize_iso_datetime
from app.ingestion.upsert_service import _choose_event_start


SOURCE_TZ = ZoneInfo("America/Los_Angeles")


def test_normalize_iso_datetime_treats_naive_value_as_local_source_time():
    parsed = _normalize_iso_datetime("2026-05-10T19:30:00")
    assert parsed is not None
    local_value = parsed.astimezone(SOURCE_TZ)
    assert local_value.hour == 19
    assert local_value.minute == 30


def test_extract_json_ld_events_applies_start_time_hint_for_date_only_start_date():
    event_payload = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": "Warehouse Live Set",
        "startDate": "2026-05-10",
        "startTime": "7:30 PM",
        "description": "Doors at 7:00 PM, show at 7:30 PM.",
    }
    html = (
        '<script type="application/ld+json">'
        + json.dumps(event_payload)
        + "</script>"
    )
    events = _extract_json_ld_events(
        html,
        start_date=datetime(2026, 5, 1, tzinfo=UTC),
        end_date=datetime(2026, 5, 31, tzinfo=UTC),
    )
    assert len(events) == 1
    event_start = events[0]["event_start_at"]
    assert isinstance(event_start, datetime)
    local_value = event_start.astimezone(SOURCE_TZ)
    assert local_value.hour == 19
    assert local_value.minute == 30


def test_extract_json_ld_events_prefers_pm_for_ambiguous_nightlife_time():
    event_payload = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": "Late Night DJ Set",
        "startDate": "2026-05-10",
        "startTime": "7:00",
        "description": "Dance party all night with guest DJs.",
    }
    html = (
        '<script type="application/ld+json">'
        + json.dumps(event_payload)
        + "</script>"
    )
    events = _extract_json_ld_events(
        html,
        start_date=datetime(2026, 5, 1, tzinfo=UTC),
        end_date=datetime(2026, 5, 31, tzinfo=UTC),
    )
    assert len(events) == 1
    event_start = events[0]["event_start_at"]
    assert isinstance(event_start, datetime)
    local_value = event_start.astimezone(SOURCE_TZ)
    assert local_value.hour == 19
    assert local_value.minute == 0


def test_choose_event_start_keeps_existing_precise_time_over_new_midnight():
    existing = datetime(2026, 5, 10, 20, 0, tzinfo=SOURCE_TZ).astimezone(UTC)
    incoming_midnight = datetime(2026, 5, 10, 0, 0, tzinfo=SOURCE_TZ).astimezone(UTC)
    chosen = _choose_event_start(existing, incoming_midnight)
    assert chosen == existing
