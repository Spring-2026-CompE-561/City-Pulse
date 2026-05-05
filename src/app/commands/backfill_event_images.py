"""One-time CLI command to backfill source event images and organizers."""

import argparse
import asyncio
import json

import httpx
from sqlalchemy import select
from sqlmodel import col

from app.config import settings
from app.database import async_session_maker, init_db
from app.ingestion.adapters import fetch_event_metadata_for_url
from app.models import Event


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="city-pulse-backfill-images",
        description="Backfill source event images and organizer metadata.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=2000,
        help="Maximum number of events to process in one run.",
    )
    return parser


async def _run_backfill(limit: int) -> dict[str, int]:
    if not settings.skip_db_init:
        await init_db()
    if async_session_maker is None:
        raise RuntimeError("Database session factory unavailable")

    updated = 0
    organizer_updated = 0
    skipped_no_url = 0
    total_candidates = 0
    timeout = httpx.Timeout(20.0, connect=10.0)
    async with async_session_maker() as db, httpx.AsyncClient(
        timeout=timeout, follow_redirects=True
    ) as client:
        result = await db.execute(
            select(Event)
            .where(
                col(Event.origin_type) == "source",
            )
            .order_by(col(Event.id))
            .limit(limit)
        )
        events = list(result.scalars().all())
        total_candidates = len(events)
        for event in events:
            page_url = event.canonical_url or event.external_url
            if not page_url:
                skipped_no_url += 1
                continue
            metadata = await fetch_event_metadata_for_url(
                client,
                page_url,
                category=event.category,
                title=event.title,
            )
            image_url = metadata.get("event_image_url")
            organizer_name = metadata.get("organizer_name")
            row_changed = False
            if isinstance(image_url, str) and image_url and not (event.event_image_url or "").strip():
                event.event_image_url = image_url
                row_changed = True
            tags_payload: dict[str, object]
            try:
                tags_payload = json.loads(event.tags_json) if event.tags_json else {}
            except json.JSONDecodeError:
                tags_payload = {}
            existing_organizer = tags_payload.get("organizer_name")
            if (
                isinstance(organizer_name, str)
                and organizer_name.strip()
                and not (isinstance(existing_organizer, str) and existing_organizer.strip())
            ):
                tags_payload["organizer_name"] = organizer_name.strip()
                event.tags_json = json.dumps(tags_payload, ensure_ascii=True)
                organizer_updated += 1
                row_changed = True
            if row_changed:
                updated += 1
        await db.commit()

    return {
        "processed": total_candidates,
        "updated_rows": updated,
        "organizer_updated": organizer_updated,
        "skipped_no_url": skipped_no_url,
    }


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    result = asyncio.run(_run_backfill(args.limit))
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
