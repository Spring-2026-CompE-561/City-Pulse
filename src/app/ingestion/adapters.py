import re
from datetime import UTC, datetime
from html import unescape
from urllib.parse import parse_qs, unquote, urlparse

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
        f"{source.name} san diego {month_label} event",
        f"san diego events this weekend {source.neighborhood or ''}".strip(),
        "foodieland san diego",
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


def _looks_like_event_host(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    if not host:
        return False
    return any(token in host for token in KNOWN_EVENT_HOST_TOKENS)


def _looks_like_calendar_page(title: str, content: str | None, url: str) -> bool:
    blob = f"{title} {content or ''} {url}".lower()
    return any(token in blob for token in CALENDAR_PAGE_TOKENS)


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


async def fetch_source_events(
    source: Source,
    *,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[NormalizedEvent]:
    """Search event candidates and parse a single event per candidate page."""
    if start_date is None or end_date is None:
        return []
    if "calendar" in source.name.lower():
        return []

    timeout = httpx.Timeout(15.0, connect=10.0)
    queries = _build_search_queries(source, start_date=start_date, end_date=end_date)
    results: list[NormalizedEvent] = []
    seen_urls: set[str] = set()
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        for query in queries:
            candidate_urls, snippets = await _search_google_for_candidates(client, query)
            snippet_text = snippets[0] if snippets else None
            for candidate_url in candidate_urls:
                if candidate_url in seen_urls:
                    continue
                seen_urls.add(candidate_url)
                if not _looks_like_event_host(candidate_url):
                    continue
                detail_response = await client.get(
                    candidate_url,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; CityPulseSimpleBot/1.0)"},
                )
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
                venue_name = source.name
                price_info = _extract_price_info(detail_html)
                tags = _extract_tags(detail_html)
                results.append(
                    NormalizedEvent(
                        source_id=source.id or 0,
                        source_name=source.name,
                        source_type=source.source_type,
                        origin_type="source",
                        external_id=f"{source.id or 0}-{abs(hash(canonical_url))}",
                        external_url=canonical_url,
                        canonical_url=canonical_url,
                        title=display_title[:512],
                        category=source.category_hint or "Community",
                        content=content,
                        event_start_at=event_start,
                        event_end_at=None,
                        timezone="America/Los_Angeles",
                        venue_name=venue_name,
                        venue_address=None,
                        neighborhood=source.neighborhood,
                        city="San Diego",
                        price_info=price_info,
                        promo_summary="; ".join(tags[:3]) if tags else None,
                        tags=tags,
                        source_confidence=0.55,
                    )
                )
                if len(results) >= 3:
                    return results
    return results
