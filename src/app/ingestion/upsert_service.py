import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.ingestion.dedupe import build_fingerprint, normalize_url
from app.ingestion.types import NormalizedEvent
from app.models import Event
from app.repository.event import create_event, update_event_fields


async def _find_existing_event(db: AsyncSession, event: NormalizedEvent) -> Event | None:
    if event.external_id:
        result = await db.execute(
            select(Event).where(
                col(Event.source_id) == event.source_id,
                col(Event.external_id) == event.external_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

    canonical = normalize_url(event.canonical_url)
    if canonical:
        result = await db.execute(select(Event).where(col(Event.canonical_url) == canonical))
        existing = result.scalar_one_or_none()
        if existing:
            return existing

    fingerprint = build_fingerprint(
        title=event.title,
        venue_name=event.venue_name,
        neighborhood=event.neighborhood,
        event_start_iso=event.event_start_at.isoformat() if event.event_start_at else None,
    )
    result = await db.execute(
        select(Event).where(col(Event.tags_json).like(f"%{fingerprint}%"))
    )
    return result.scalar_one_or_none()


async def upsert_normalized_event(
    db: AsyncSession,
    *,
    region_id: int,
    normalized: NormalizedEvent,
) -> str:
    now = datetime.now(UTC)
    fingerprint = build_fingerprint(
        title=normalized.title,
        venue_name=normalized.venue_name,
        neighborhood=normalized.neighborhood,
        event_start_iso=normalized.event_start_at.isoformat() if normalized.event_start_at else None,
    )
    tags_payload = {
        "tags": normalized.tags,
        "fingerprint": fingerprint,
    }
    existing = await _find_existing_event(db, normalized)
    if existing:
        await update_event_fields(
            db,
            event=existing,
            title=normalized.title,
            category=normalized.category,
            content=normalized.content,
            event_start_at=normalized.event_start_at,
            event_end_at=normalized.event_end_at,
            timezone=normalized.timezone,
            venue_name=normalized.venue_name,
            venue_address=normalized.venue_address,
            neighborhood=normalized.neighborhood,
            price_info=normalized.price_info,
            promo_summary=normalized.promo_summary,
            source_confidence=normalized.source_confidence,
            last_seen_at=now,
        )
        existing.source_id = normalized.source_id
        existing.origin_type = normalized.origin_type
        existing.external_id = normalized.external_id
        existing.external_url = normalized.external_url
        existing.canonical_url = normalize_url(normalized.canonical_url)
        existing.tags_json = json.dumps(tags_payload, ensure_ascii=True)
        await db.flush()
        return "updated"

    await create_event(
        db,
        region_id=region_id,
        user_id=None,
        title=normalized.title,
        category=normalized.category,
        content=normalized.content,
        source_id=normalized.source_id,
        origin_type=normalized.origin_type,
        external_id=normalized.external_id,
        external_url=normalized.external_url,
        canonical_url=normalize_url(normalized.canonical_url),
        event_start_at=normalized.event_start_at,
        event_end_at=normalized.event_end_at,
        timezone=normalized.timezone,
        venue_name=normalized.venue_name,
        venue_address=normalized.venue_address,
        neighborhood=normalized.neighborhood,
        city=normalized.city,
        price_info=normalized.price_info,
        promo_summary=normalized.promo_summary,
        tags_json=json.dumps(tags_payload, ensure_ascii=True),
        source_confidence=normalized.source_confidence,
        last_seen_at=now,
    )
    return "inserted"
