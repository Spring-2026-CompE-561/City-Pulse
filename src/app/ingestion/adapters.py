import json
import re
from datetime import UTC, datetime

import httpx

from app.ingestion.dedupe import normalize_url
from app.ingestion.types import NormalizedEvent
from app.models import Source

TITLE_PATTERN = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
JSON_LD_PATTERN = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)
PRICE_PATTERN = re.compile(r"\$[0-9]+(?:\.[0-9]{2})?")
NIGHT_THEME_TOKENS = (
    "karaoke",
    "latin night",
    "emo night",
    "dj",
    "happy hour",
    "trivia",
    "live music",
)


def _extract_title(html: str, fallback: str) -> str:
    match = TITLE_PATTERN.search(html)
    if not match:
        return fallback
    return re.sub(r"\s+", " ", match.group(1)).strip()[:512] or fallback


def _extract_price_info(html: str) -> str | None:
    prices = PRICE_PATTERN.findall(html)
    if not prices:
        return None
    unique = []
    for price in prices:
        if price not in unique:
            unique.append(price)
    return ", ".join(unique[:3])


def _extract_tags(html: str) -> list[str]:
    tags: list[str] = []
    lower = html.lower()
    for token in NIGHT_THEME_TOKENS:
        if token in lower:
            tags.append(token)
    return tags


def _extract_jsonld_events(html: str) -> list[dict]:
    entries: list[dict] = []
    for script_match in JSON_LD_PATTERN.findall(html):
        try:
            payload = json.loads(script_match.strip())
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            entries.append(payload)
        elif isinstance(payload, list):
            entries.extend([item for item in payload if isinstance(item, dict)])
    return entries


async def fetch_source_events(
    source: Source,
    *,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[NormalizedEvent]:
    del start_date
    del end_date
    timeout = httpx.Timeout(10.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.get(source.base_url, headers={"User-Agent": "CityPulseBot/1.0"})
    if response.status_code >= 400:
        return []
    html = response.text
    normalized_base_url = normalize_url(str(response.url))
    title = _extract_title(html, source.name)
    price_info = _extract_price_info(html)
    tags = _extract_tags(html)
    jsonld_events = _extract_jsonld_events(html)
    results: list[NormalizedEvent] = []

    if jsonld_events:
        for index, row in enumerate(jsonld_events):
            row_type = str(row.get("@type") or "")
            if "Event" not in row_type:
                continue
            start_time = row.get("startDate")
            start_at = None
            if isinstance(start_time, str):
                try:
                    start_at = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                except ValueError:
                    start_at = None
            if start_at is None:
                start_at = datetime.now(UTC)
            url_value = row.get("url") if isinstance(row.get("url"), str) else normalized_base_url
            canonical = normalize_url(url_value)
            event_title = str(row.get("name") or title)
            event_description = str(row.get("description") or "").strip() or None
            venue_name = None
            location = row.get("location")
            if isinstance(location, dict):
                venue_name = location.get("name") if isinstance(location.get("name"), str) else None
            results.append(
                NormalizedEvent(
                    source_id=source.id or 0,
                    source_name=source.name,
                    source_type=source.source_type,
                    origin_type="source",
                    external_id=f"{source.id or 0}-jsonld-{index}",
                    external_url=canonical,
                    canonical_url=canonical,
                    title=event_title[:512],
                    category=source.category_hint or "Nightlife",
                    content=event_description,
                    event_start_at=start_at,
                    event_end_at=None,
                    timezone="America/Los_Angeles",
                    venue_name=venue_name or source.name,
                    venue_address=None,
                    neighborhood=source.neighborhood,
                    price_info=price_info,
                    promo_summary="; ".join(tags[:3]) if tags else None,
                    tags=tags,
                    source_confidence=0.88,
                )
            )
        return results

    fallback_start = datetime.now(UTC)
    results.append(
        NormalizedEvent(
            source_id=source.id or 0,
            source_name=source.name,
            source_type=source.source_type,
            origin_type="source",
            external_id=f"{source.id or 0}-fallback",
            external_url=normalized_base_url,
            canonical_url=normalized_base_url,
            title=title,
            category=source.category_hint or "Nightlife",
            content="Imported from source homepage. Connector fallback parser.",
            event_start_at=fallback_start,
            event_end_at=None,
            timezone="America/Los_Angeles",
            venue_name=source.name,
            venue_address=None,
            neighborhood=source.neighborhood,
            price_info=price_info,
            promo_summary="; ".join(tags[:3]) if tags else None,
            tags=tags,
            source_confidence=0.5,
        )
    )
    return results
