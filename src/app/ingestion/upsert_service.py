import json
from dataclasses import replace
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.event_metadata import clean_event_description, clean_organizer_name
from app.event_categories import ALLOWED_EVENT_CATEGORIES
from app.ingestion.dedupe import build_content_signature, build_fingerprint, normalize_url
from app.ingestion.types import NormalizedEvent
from app.models import Event
from app.repository.event import create_event, update_event_fields


def _coerce_ingestion_category(category: str | None, fallback: str) -> str:
    for raw in (category, fallback):
        if raw and raw.strip() in ALLOWED_EVENT_CATEGORIES:
            return raw.strip()
    return "Entertainment"


# Older MySQL schemas may use a short VARCHAR for `events.content` (e.g. 500); stay under that.
_MAX_CONTENT_LEN = 500
_MAX_TITLE_LEN = 512
_MAX_PROMO_LEN = 1024
_MAX_PRICE_INFO_LEN = 255
_MAX_IMAGE_URL_LEN = 2048
_MAX_ORGANIZER_LEN = 255
_REJECT_TITLE_TOKENS = ("calendar", "upcoming events", "all events")


def _clamp_str(value: str | None, max_len: int) -> str | None:
    if value is None:
        return None
    if len(value) <= max_len:
        return value
    return value[: max_len - 3].rstrip() + "..."


def _normalized_clamped_for_db(normalized: NormalizedEvent) -> NormalizedEvent:
    cleaned_description = clean_event_description(
        normalized.content,
        title=normalized.title,
        venue_name=normalized.venue_name,
    )
    return replace(
        normalized,
        title=_clamp_str(normalized.title, _MAX_TITLE_LEN) or "",
        content=_clamp_str(cleaned_description, _MAX_CONTENT_LEN),
        event_image_url=_clamp_str(normalized.event_image_url, _MAX_IMAGE_URL_LEN),
        promo_summary=_clamp_str(normalized.promo_summary, _MAX_PROMO_LEN),
        price_info=_clamp_str(normalized.price_info, _MAX_PRICE_INFO_LEN),
    )


def _ensure_discrete_event_shape(normalized: NormalizedEvent) -> None:
    title = (normalized.title or "").strip().lower()
    if not title:
        raise ValueError("ingestion rejected: missing title")
    if any(token in title for token in _REJECT_TITLE_TOKENS):
        raise ValueError("ingestion rejected: calendar/listing page")
    if not (normalized.venue_name and normalized.venue_name.strip()):
        raise ValueError("ingestion rejected: missing venue")


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
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    content_signature = build_content_signature(
        title=event.title,
        content=event.content,
        venue_name=event.venue_name,
        neighborhood=event.neighborhood,
        event_start_iso=event.event_start_at.isoformat() if event.event_start_at else None,
    )
    result = await db.execute(
        select(Event).where(
            col(Event.origin_type) == "source",
            col(Event.tags_json).like(f"%{content_signature}%"),
        )
    )
    return result.scalar_one_or_none()


async def upsert_normalized_event(
    db: AsyncSession,
    *,
    region_id: int,
    normalized: NormalizedEvent,
) -> str:
    now = datetime.now(UTC)
    normalized = _normalized_clamped_for_db(normalized)
    _ensure_discrete_event_shape(normalized)
    safe_category = _coerce_ingestion_category(normalized.category, "Nightlife (Bars & Clubs)")
    fingerprint = build_fingerprint(
        title=normalized.title,
        venue_name=normalized.venue_name,
        neighborhood=normalized.neighborhood,
        event_start_iso=normalized.event_start_at.isoformat() if normalized.event_start_at else None,
    )
    content_signature = build_content_signature(
        title=normalized.title,
        content=normalized.content,
        venue_name=normalized.venue_name,
        neighborhood=normalized.neighborhood,
        event_start_iso=normalized.event_start_at.isoformat() if normalized.event_start_at else None,
    )
    tags_payload = {
        "tags": normalized.tags,
        "fingerprint": fingerprint,
        "content_signature": content_signature,
        "organizer_name": _clamp_str(
            clean_organizer_name(normalized.organizer_name),
            _MAX_ORGANIZER_LEN,
        ),
    }
    existing = await _find_existing_event(db, normalized)
    if existing:
        await update_event_fields(
            db,
            event=existing,
            title=normalized.title,
            category=safe_category,
            content=normalized.content,
            event_image_url=normalized.event_image_url,
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
        category=safe_category,
        content=normalized.content,
        source_id=normalized.source_id,
        origin_type=normalized.origin_type,
        external_id=normalized.external_id,
        external_url=normalized.external_url,
        canonical_url=normalize_url(normalized.canonical_url),
        event_image_url=normalized.event_image_url,
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
