import hashlib
import json
import re
from datetime import UTC, datetime
from html import unescape
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import httpx

from app.ingestion.dedupe import normalize_url
from app.ingestion.types import NormalizedEvent
from app.models import Source

TITLE_PATTERN = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_PATTERN = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
OG_TITLE_PATTERN = re.compile(
    r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']',
    re.IGNORECASE,
)
META_DESC_PATTERN = re.compile(
    r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)["\']',
    re.IGNORECASE,
)
OG_IMAGE_PATTERN = re.compile(
    r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
TWITTER_IMAGE_PATTERN = re.compile(
    r'<meta[^>]+name=["\']twitter:image(?::src)?["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
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
TAG_RE = re.compile(r"<[^>]+>")
HREF_PATTERN = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
IMG_SRC_PATTERN = re.compile(
    r'<img[^>]+(?:src|data-src|data-lazy-src)=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
JSON_LD_SCRIPT_PATTERN = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)
GOOGLE_URL_PATTERN = re.compile(r'href=["\'](/url\?q=[^"\']+)["\']', re.IGNORECASE)
GOOGLE_SNIPPET_PATTERN = re.compile(
    r'<div[^>]*class=["\'][^"\']*VwiC3b[^"\']*["\'][^>]*>(.*?)</div>',
    re.IGNORECASE | re.DOTALL,
)
MONTH_NAME_PATTERN = re.compile(
    r"\b("
    r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
    r")\s+\d{1,2}(?:,\s*\d{4})?",
    re.IGNORECASE,
)
KNOWN_EVENT_HOST_TOKENS = (
    "eventbrite",
    "sandiegoreader",
    "visitsandiego",
    "allevents",
    "event",
    "ticket",
)
CALENDAR_PAGE_TOKENS = (
    "calendar",
    "upcoming events",
    "all events",
    "events calendar",
    "monthly events",
)
EVENT_LINK_TOKENS = (
    "/event",
    "/events",
    "/calendar",
    "/festival",
    "/show",
    "ticket",
)
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif")
ORGANIZER_PATTERN = re.compile(
    r"(?:organizer|hosted by|presented by)\s*[:\-]\s*([a-z0-9&'.,()\- ]{2,120})",
    re.IGNORECASE,
)


def _strip_tags(fragment: str) -> str:
    text = TAG_RE.sub(" ", fragment)
    return re.sub(r"\s+", " ", text).strip()


def _extract_title(html: str, fallback: str) -> str:
    match = TITLE_PATTERN.search(html)
    if not match:
        return fallback
    return _strip_tags(match.group(1))[:512] or fallback


def _extract_og_title(html: str) -> str | None:
    match = OG_TITLE_PATTERN.search(html)
    if not match:
        return None
    text = _strip_tags(match.group(1))
    return text[:512] if text else None


def _extract_h1(html: str) -> str | None:
    match = H1_PATTERN.search(html)
    if not match:
        return None
    text = _strip_tags(match.group(1))
    return text[:512] if text else None


def _extract_meta_description(html: str) -> str | None:
    match = META_DESC_PATTERN.search(html)
    if not match:
        return None
    text = _strip_tags(match.group(1))
    return text[:1024] if text else None


def _normalize_image_url(raw: str, *, base_url: str) -> str | None:
    candidate = normalize_url(urljoin(base_url, unescape(raw).strip()))
    if not candidate:
        return None
    lower = candidate.lower()
    if not lower.startswith(("http://", "https://")):
        return None
    if any(token in lower for token in ("/logo", "/icon", "/avatar", "sprite", ".svg")):
        return None
    parsed = urlparse(lower)
    if any(parsed.path.endswith(ext) for ext in IMAGE_EXTENSIONS):
        return candidate
    if "image" in lower or "photo" in lower or "poster" in lower or "flyer" in lower:
        return candidate
    return None


def _extract_primary_image(html: str, *, base_url: str) -> str | None:
    for pattern in (OG_IMAGE_PATTERN, TWITTER_IMAGE_PATTERN):
        match = pattern.search(html)
        if not match:
            continue
        candidate = _normalize_image_url(match.group(1), base_url=base_url)
        if candidate:
            return candidate
    for raw_src in IMG_SRC_PATTERN.findall(html):
        candidate = _normalize_image_url(raw_src, base_url=base_url)
        if candidate:
            return candidate
    return None


def _extract_name_from_entity(entity: object) -> str | None:
    if isinstance(entity, dict):
        raw_name = entity.get("name")
        if isinstance(raw_name, str):
            name = raw_name.strip()
            return name[:255] if name else None
    elif isinstance(entity, str):
        name = entity.strip()
        return name[:255] if name else None
    return None


def _extract_json_ld_organizer(html: str) -> str | None:
    for payload in _extract_json_ld_payloads(html):
        for node in _iter_json_nodes(payload):
            node_type = node.get("@type")
            type_blob = " ".join(node_type) if isinstance(node_type, list) else str(node_type or "")
            if "event" not in type_blob.lower():
                continue
            for key in ("organizer", "performer", "provider"):
                candidate = node.get(key)
                if isinstance(candidate, list):
                    for item in candidate:
                        parsed = _extract_name_from_entity(item)
                        if parsed:
                            return parsed
                else:
                    parsed = _extract_name_from_entity(candidate)
                    if parsed:
                        return parsed
    return None


def _extract_organizer_from_html(html: str) -> str | None:
    from_json = _extract_json_ld_organizer(html)
    if from_json:
        return from_json
    body = _strip_tags(html).lower()
    match = ORGANIZER_PATTERN.search(body)
    if not match:
        return None
    candidate = match.group(1).strip()
    if not candidate:
        return None
    return " ".join(part.capitalize() for part in candidate.split())[:255]


def _stock_image_fallback(category: str | None, title: str) -> str:
    seed = re.sub(r"[^a-z0-9]+", "-", f"{category or 'community'}-{title}".lower()).strip("-")
    seed = seed[:80] or "san-diego-event"
    return f"https://picsum.photos/seed/{seed}/1200/800"


def _extract_json_ld_event_image(html: str, *, base_url: str) -> str | None:
    for payload in _extract_json_ld_payloads(html):
        for node in _iter_json_nodes(payload):
            node_type = node.get("@type")
            type_blob = " ".join(node_type) if isinstance(node_type, list) else str(node_type or "")
            if "event" not in type_blob.lower():
                continue
            image_value = node.get("image")
            if isinstance(image_value, str):
                candidate = _normalize_image_url(image_value, base_url=base_url)
                if candidate:
                    return candidate
            elif isinstance(image_value, list):
                for item in image_value:
                    if isinstance(item, str):
                        candidate = _normalize_image_url(item, base_url=base_url)
                        if candidate:
                            return candidate
                    elif isinstance(item, dict):
                        item_url = item.get("url")
                        if isinstance(item_url, str):
                            candidate = _normalize_image_url(item_url, base_url=base_url)
                            if candidate:
                                return candidate
            elif isinstance(image_value, dict):
                item_url = image_value.get("url")
                if isinstance(item_url, str):
                    candidate = _normalize_image_url(item_url, base_url=base_url)
                    if candidate:
                        return candidate
    return None


async def fetch_event_image_for_url(
    client: httpx.AsyncClient,
    page_url: str,
    *,
    category: str | None,
    title: str,
) -> str:
    metadata = await fetch_event_metadata_for_url(
        client,
        page_url,
        category=category,
        title=title,
    )
    return metadata["event_image_url"] or _stock_image_fallback(category, title)


async def fetch_event_metadata_for_url(
    client: httpx.AsyncClient,
    page_url: str,
    *,
    category: str | None,
    title: str,
) -> dict[str, str | None]:
    try:
        response = await client.get(
            page_url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; CityPulseSimpleBot/1.0)"},
        )
    except httpx.HTTPError:
        return {
            "event_image_url": _stock_image_fallback(category, title),
            "organizer_name": None,
        }
    if response.status_code >= 400:
        return {
            "event_image_url": _stock_image_fallback(category, title),
            "organizer_name": None,
        }
    resolved_url = str(response.url)
    html = response.text
    organizer_name = _extract_organizer_from_html(html)
    image_from_json = _extract_json_ld_event_image(html, base_url=resolved_url)
    if image_from_json:
        return {"event_image_url": image_from_json, "organizer_name": organizer_name}
    image_from_meta = _extract_primary_image(html, base_url=resolved_url)
    if image_from_meta:
        return {"event_image_url": image_from_meta, "organizer_name": organizer_name}
    return {
        "event_image_url": _stock_image_fallback(category, title),
        "organizer_name": organizer_name,
    }


def _extract_price_info(html: str) -> str | None:
    prices = PRICE_PATTERN.findall(html)
    if not prices:
        return None
    unique: list[str] = []
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


def _build_search_queries(source: Source, *, start_date: datetime, end_date: datetime) -> list[str]:
    del end_date
    month_label = start_date.strftime("%B")
    return [
        f"{source.name} {source.domain} san diego {month_label} events",
        f"site:{source.domain} san diego events {source.neighborhood or ''}".strip(),
        f"{source.base_url} events",
    ]


def _extract_google_candidate_urls(html: str) -> list[str]:
    urls: list[str] = []
    for raw_href in GOOGLE_URL_PATTERN.findall(html):
        parsed = urlparse(unescape(raw_href))
        query = parse_qs(parsed.query)
        raw_url = query.get("q", [None])[0]
        if not raw_url:
            continue
        candidate = normalize_url(unquote(raw_url))
        if not candidate:
            continue
        lower = candidate.lower()
        if lower.startswith("https://webcache.googleusercontent.com"):
            continue
        if "google." in lower:
            continue
        if candidate not in urls:
            urls.append(candidate)
    return urls


def _extract_google_snippets(html: str) -> list[str]:
    snippets: list[str] = []
    for raw in GOOGLE_SNIPPET_PATTERN.findall(html):
        text = _strip_tags(unescape(raw))
        if text:
            snippets.append(text[:280])
    return snippets


def _source_matches_host(source: Source, url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    domain = source.domain.lower().lstrip(".")
    if not host or not domain:
        return False
    return host == domain or host.endswith(f".{domain}")


def _looks_like_event_host(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    if not host:
        return False
    return any(token in host for token in KNOWN_EVENT_HOST_TOKENS)


def _is_likely_event_url(url: str) -> bool:
    lowered = url.lower()
    return any(token in lowered for token in EVENT_LINK_TOKENS)


def _looks_like_calendar_page(title: str, content: str | None, url: str) -> bool:
    blob = f"{title} {content or ''} {url}".lower()
    return any(token in blob for token in CALENDAR_PAGE_TOKENS)


def _normalize_iso_datetime(value: str) -> datetime | None:
    raw = value.strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _stable_external_id(source_id: int, canonical_url: str) -> str:
    digest = hashlib.sha1(canonical_url.encode("utf-8")).hexdigest()[:16]  # noqa: S324
    return f"{source_id}-{digest}"


def _event_within_window(
    event_start: datetime | None,
    *,
    start_date: datetime,
    end_date: datetime,
) -> bool:
    if event_start is None:
        return False
    return start_date <= event_start <= end_date


def _extract_event_datetime(
    html: str,
    *,
    start_date: datetime,
    end_date: datetime,
) -> datetime | None:
    body = _strip_tags(html)
    for raw_match in MONTH_NAME_PATTERN.findall(body):
        # findall returns capture group; recover the full string via search around first hit
        hit = re.search(raw_match + r"\s+\d{1,2}(?:,\s*\d{4})?", body, re.IGNORECASE)
        if not hit:
            continue
        date_text = hit.group(0)
        with_year = date_text if "," in date_text else f"{date_text}, {start_date.year}"
        for fmt in ("%B %d, %Y", "%b %d, %Y"):
            try:
                parsed = datetime.strptime(with_year, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
            if start_date <= parsed <= end_date:
                return parsed
    return None


def _extract_source_links(source: Source, html: str, base_url: str) -> list[str]:
    links: list[str] = []
    for raw_href in HREF_PATTERN.findall(html):
        href = unescape(raw_href).strip()
        if not href or href.startswith("#") or href.startswith("mailto:"):
            continue
        candidate = normalize_url(urljoin(base_url, href))
        if not candidate:
            continue
        if not _source_matches_host(source, candidate):
            continue
        if not _is_likely_event_url(candidate):
            continue
        if candidate not in links:
            links.append(candidate)
        if len(links) >= 40:
            break
    return links


def _iter_json_nodes(payload: object):
    if isinstance(payload, dict):
        yield payload
        for value in payload.values():
            yield from _iter_json_nodes(value)
    elif isinstance(payload, list):
        for item in payload:
            yield from _iter_json_nodes(item)


def _extract_json_ld_payloads(html: str) -> list[object]:
    payloads: list[object] = []
    for block in JSON_LD_SCRIPT_PATTERN.findall(html):
        body = block.strip()
        if not body:
            continue
        try:
            decoded = json.loads(body)
        except json.JSONDecodeError:
            continue
        payloads.append(decoded)
    return payloads


def _extract_json_ld_events(
    html: str,
    *,
    start_date: datetime,
    end_date: datetime,
) -> list[dict[str, str | datetime | None]]:
    extracted: list[dict[str, str | datetime | None]] = []
    for payload in _extract_json_ld_payloads(html):
        for node in _iter_json_nodes(payload):
            node_type = node.get("@type")
            type_blob = " ".join(node_type) if isinstance(node_type, list) else str(node_type or "")
            if "event" not in type_blob.lower():
                continue
            title = str(node.get("name") or "").strip()
            if not title:
                continue
            start_value = node.get("startDate")
            end_value = node.get("endDate")
            event_start = _normalize_iso_datetime(str(start_value)) if start_value else None
            if not _event_within_window(event_start, start_date=start_date, end_date=end_date):
                continue
            event_end = _normalize_iso_datetime(str(end_value)) if end_value else None
            description = node.get("description")
            content = str(description).strip()[:1024] if isinstance(description, str) else None
            event_url = node.get("url")
            normalized_url = normalize_url(str(event_url)) if isinstance(event_url, str) else ""
            location = node.get("location")
            venue_name: str | None = None
            if isinstance(location, dict):
                location_name = location.get("name")
                if isinstance(location_name, str):
                    venue_name = location_name.strip()[:255] or None
            organizer_name: str | None = None
            for key in ("organizer", "performer", "provider"):
                organizer_candidate = node.get(key)
                if isinstance(organizer_candidate, list):
                    for item in organizer_candidate:
                        organizer_name = _extract_name_from_entity(item)
                        if organizer_name:
                            break
                else:
                    organizer_name = _extract_name_from_entity(organizer_candidate)
                if organizer_name:
                    break
            image_url: str | None = None
            image_value = node.get("image")
            if isinstance(image_value, str):
                image_url = image_value
            elif isinstance(image_value, list):
                for candidate in image_value:
                    if isinstance(candidate, str) and candidate.strip():
                        image_url = candidate
                        break
                    if isinstance(candidate, dict):
                        candidate_url = candidate.get("url")
                        if isinstance(candidate_url, str) and candidate_url.strip():
                            image_url = candidate_url
                            break
            elif isinstance(image_value, dict):
                candidate_url = image_value.get("url")
                if isinstance(candidate_url, str) and candidate_url.strip():
                    image_url = candidate_url
            extracted.append(
                {
                    "title": title[:512],
                    "event_start_at": event_start,
                    "event_end_at": event_end,
                    "content": content,
                    "canonical_url": normalized_url or None,
                    "venue_name": venue_name,
                    "organizer_name": organizer_name,
                    "event_image_url": image_url,
                }
            )
    return extracted


async def _search_google_for_candidates(
    client: httpx.AsyncClient,
    query: str,
) -> tuple[list[str], list[str]]:
    response = await client.get(
        "https://www.google.com/search",
        params={"q": query, "num": 7, "hl": "en"},
        headers={"User-Agent": "Mozilla/5.0 (compatible; CityPulseSimpleBot/1.0)"},
    )
    if response.status_code >= 400:
        return [], []
    html = response.text
    return _extract_google_candidate_urls(html), _extract_google_snippets(html)


def _build_normalized_event(
    *,
    source: Source,
    canonical_url: str,
    title: str,
    content: str | None,
    organizer_name: str | None,
    event_image_url: str | None,
    event_start_at: datetime | None,
    event_end_at: datetime | None,
    venue_name: str | None,
    price_info: str | None,
    tags: list[str],
    confidence: float,
) -> NormalizedEvent:
    source_id = source.id or 0
    chosen_image = event_image_url or _stock_image_fallback(source.category_hint, title)
    return NormalizedEvent(
        source_id=source_id,
        source_name=source.name,
        source_type=source.source_type,
        origin_type="source",
        external_id=_stable_external_id(source_id, canonical_url),
        external_url=canonical_url,
        canonical_url=canonical_url,
        title=title[:512],
        category=source.category_hint or "Community",
        content=content,
        organizer_name=organizer_name,
        event_image_url=chosen_image,
        event_start_at=event_start_at,
        event_end_at=event_end_at,
        timezone="America/Los_Angeles",
        venue_name=venue_name or source.name,
        venue_address=None,
        neighborhood=source.neighborhood,
        city="San Diego",
        price_info=price_info,
        promo_summary="; ".join(tags[:3]) if tags else None,
        tags=tags,
        source_confidence=confidence,
    )


async def fetch_source_events(
    source: Source,
    *,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[NormalizedEvent]:
    """Crawl source pages and parse event detail pages."""
    if start_date is None or end_date is None:
        return []
    timeout = httpx.Timeout(15.0, connect=10.0)
    queries = _build_search_queries(source, start_date=start_date, end_date=end_date)
    results: list[NormalizedEvent] = []
    seen_urls: set[str] = set()
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        try:
            listing_response = await client.get(
                source.base_url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; CityPulseSimpleBot/1.0)"},
            )
        except httpx.HTTPError:
            listing_response = None

        listing_html = listing_response.text if listing_response and listing_response.status_code < 400 else ""
        listing_url = str(listing_response.url) if listing_response is not None else source.base_url

        # First pass: parse structured event payloads directly from the source listing page.
        for event_payload in _extract_json_ld_events(
            listing_html,
            start_date=start_date,
            end_date=end_date,
        ):
            canonical_url = normalize_url(
                str(event_payload.get("canonical_url") or listing_url)
            )
            if not canonical_url or canonical_url in seen_urls:
                continue
            seen_urls.add(canonical_url)
            event_image_url = None
            if event_payload.get("event_image_url"):
                event_image_url = _normalize_image_url(
                    str(event_payload.get("event_image_url")),
                    base_url=listing_url,
                )
            if event_image_url is None:
                event_image_url = _extract_primary_image(listing_html, base_url=listing_url)
            results.append(
                _build_normalized_event(
                    source=source,
                    canonical_url=canonical_url,
                    title=str(event_payload.get("title") or source.name),
                    content=(
                        str(event_payload.get("content"))
                        if event_payload.get("content") is not None
                        else None
                    ),
                    organizer_name=(
                        str(event_payload.get("organizer_name"))
                        if event_payload.get("organizer_name")
                        else None
                    ),
                    event_image_url=event_image_url,
                    event_start_at=event_payload.get("event_start_at"),  # type: ignore[arg-type]
                    event_end_at=event_payload.get("event_end_at"),  # type: ignore[arg-type]
                    venue_name=(
                        str(event_payload.get("venue_name"))
                        if event_payload.get("venue_name")
                        else source.name
                    ),
                    price_info=None,
                    tags=[],
                    confidence=0.8,
                )
            )

        # Second pass: crawl source-domain event links found on the listing page.
        candidate_urls = _extract_source_links(source, listing_html, listing_url)
        for candidate_url in candidate_urls:
            if candidate_url in seen_urls:
                continue
            seen_urls.add(candidate_url)
            try:
                detail_response = await client.get(
                    candidate_url,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; CityPulseSimpleBot/1.0)"},
                )
            except httpx.HTTPError:
                continue
            if detail_response.status_code >= 400:
                continue
            detail_html = detail_response.text
            canonical_url = normalize_url(str(detail_response.url))
            if not canonical_url:
                continue
            if _looks_like_calendar_page("", None, canonical_url):
                continue
            # Prefer page-level JSON-LD event metadata when available.
            detail_structured_events = _extract_json_ld_events(
                detail_html,
                start_date=start_date,
                end_date=end_date,
            )
            if detail_structured_events:
                first = detail_structured_events[0]
                structured_image_url = None
                if first.get("event_image_url"):
                    structured_image_url = _normalize_image_url(
                        str(first.get("event_image_url")),
                        base_url=canonical_url,
                    )
                detail_image_url = structured_image_url or _extract_primary_image(
                    detail_html,
                    base_url=canonical_url,
                )
                results.append(
                    _build_normalized_event(
                        source=source,
                        canonical_url=canonical_url,
                        title=str(first.get("title") or source.name),
                        content=str(first.get("content")) if first.get("content") else None,
                        organizer_name=(
                            str(first.get("organizer_name"))
                            if first.get("organizer_name")
                            else None
                        ),
                        event_image_url=detail_image_url,
                        event_start_at=first.get("event_start_at"),  # type: ignore[arg-type]
                        event_end_at=first.get("event_end_at"),  # type: ignore[arg-type]
                        venue_name=str(first.get("venue_name")) if first.get("venue_name") else source.name,
                        price_info=_extract_price_info(detail_html),
                        tags=_extract_tags(detail_html),
                        confidence=0.82,
                    )
                )
                if len(results) >= 20:
                    return results
                continue

            og_title = _extract_og_title(detail_html)
            page_title = og_title or _extract_title(detail_html, source.name)
            h1 = _extract_h1(detail_html)
            if h1 and len(h1) > 2 and h1.lower() not in page_title.lower():
                display_title = f"{h1} — {page_title}"[:512]
            else:
                display_title = page_title
            meta_desc = _extract_meta_description(detail_html)
            content = (meta_desc or "").strip() or None
            event_start = _extract_event_datetime(
                detail_html,
                start_date=start_date,
                end_date=end_date,
            )
            if not _event_within_window(event_start, start_date=start_date, end_date=end_date):
                continue
            results.append(
                _build_normalized_event(
                    source=source,
                    canonical_url=canonical_url,
                    title=display_title,
                    content=content,
                    organizer_name=_extract_organizer_from_html(detail_html),
                    event_image_url=_extract_primary_image(detail_html, base_url=canonical_url),
                    event_start_at=event_start,
                    event_end_at=None,
                    venue_name=source.name,
                    price_info=_extract_price_info(detail_html),
                    tags=_extract_tags(detail_html),
                    confidence=0.65,
                )
            )
            if len(results) >= 20:
                return results

        # Third pass fallback: web search candidates for sparse sources.
        for query in queries:
            candidate_urls, snippets = await _search_google_for_candidates(client, query)
            snippet_text = snippets[0] if snippets else None
            for candidate_url in candidate_urls:
                if candidate_url in seen_urls:
                    continue
                seen_urls.add(candidate_url)
                if not (_source_matches_host(source, candidate_url) or _looks_like_event_host(candidate_url)):
                    continue
                try:
                    detail_response = await client.get(
                        candidate_url,
                        headers={"User-Agent": "Mozilla/5.0 (compatible; CityPulseSimpleBot/1.0)"},
                    )
                except httpx.HTTPError:
                    continue
                if detail_response.status_code >= 400:
                    continue
                detail_html = detail_response.text
                canonical_url = normalize_url(str(detail_response.url))
                if not canonical_url:
                    continue
                og_title = _extract_og_title(detail_html)
                page_title = og_title or _extract_title(detail_html, source.name)
                h1 = _extract_h1(detail_html)
                if h1 and len(h1) > 2 and h1.lower() not in page_title.lower():
                    display_title = f"{h1} — {page_title}"[:512]
                else:
                    display_title = page_title
                meta_desc = _extract_meta_description(detail_html)
                content = (meta_desc or snippet_text or "").strip() or None
                if _looks_like_calendar_page(display_title, content, canonical_url):
                    continue
                event_start = _extract_event_datetime(
                    detail_html,
                    start_date=start_date,
                    end_date=end_date,
                )
                if event_start is None:
                    continue
                results.append(
                    _build_normalized_event(
                        source=source,
                        canonical_url=canonical_url,
                        title=display_title,
                        content=content,
                        organizer_name=_extract_organizer_from_html(detail_html),
                        event_image_url=_extract_primary_image(detail_html, base_url=canonical_url),
                        event_start_at=event_start,
                        event_end_at=None,
                        venue_name=source.name,
                        price_info=_extract_price_info(detail_html),
                        tags=_extract_tags(detail_html),
                        confidence=0.55,
                    )
                )
                if len(results) >= 20:
                    return results
    return results
