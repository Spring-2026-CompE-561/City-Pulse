from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from app.models import Event
from app.repository.event import create_event, update_event_fields


@pytest.mark.asyncio
async def test_create_event_adds_and_flushes_session():
    db = AsyncMock()
    db.add = Mock()
    db.refresh = AsyncMock()

    event = await create_event(
        db,
        region_id=0,
        user_id=1,
        title="Test event",
        category="Technology",
        content="hello",
    )

    assert isinstance(event, Event)
    db.add.assert_called_once()
    db.flush.assert_called_once()
    db.refresh.assert_called_once_with(event)


@pytest.mark.asyncio
async def test_update_event_fields_only_updates_given_values():
    db = AsyncMock()
    event = Event(
        region_id=0,
        user_id=1,
        title="Old",
        category="Business",
        content="Old content",
        created_at=datetime.now(UTC),
    )

    await update_event_fields(
        db,
        event=event,
        title="New",
        category=None,
        content=None,
    )

    assert event.title == "New"
    assert event.content == "Old content"
    db.flush.assert_called_once()

