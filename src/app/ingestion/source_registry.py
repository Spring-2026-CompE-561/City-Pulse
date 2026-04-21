from app.models import Source
from app.region_map import REGION_SAN_DIEGO_ID

DEFAULT_NIGHTLIFE_SOURCES: tuple[dict[str, str | bool | int | None], ...] = (
    {
        "name": "North Park Observatory Calendar",
        "domain": "observatorysd.com",
        "base_url": "https://www.observatorysd.com/events/",
        "source_type": "html",
        "category_hint": "Nightlife",
        "neighborhood": "North Park",
        "crawl_allowed": True,
        "crawl_delay_seconds": 12,
        "rate_limit_per_min": 5,
        "parse_strategy": "generic_html",
    },
    {
        "name": "Gaslamp House Of Blues Events",
        "domain": "houseofblues.com",
        "base_url": "https://www.houseofblues.com/sandiego/events",
        "source_type": "html",
        "category_hint": "Nightlife",
        "neighborhood": "Gaslamp",
        "crawl_allowed": True,
        "crawl_delay_seconds": 12,
        "rate_limit_per_min": 5,
        "parse_strategy": "generic_html",
    },
    {
        "name": "Pacific Beach Nightlife Events",
        "domain": "pbshoreclub.com",
        "base_url": "https://www.pbshoreclub.com/events",
        "source_type": "html",
        "category_hint": "Nightlife",
        "neighborhood": "Pacific Beach",
        "crawl_allowed": True,
        "crawl_delay_seconds": 12,
        "rate_limit_per_min": 5,
        "parse_strategy": "generic_html",
    },
    {
        "name": "Hillcrest Public Events",
        "domain": "hillcrestbia.org",
        "base_url": "https://hillcrestbia.org/events/",
        "source_type": "html",
        "category_hint": "Community",
        "neighborhood": "Hillcrest",
        "crawl_allowed": True,
        "crawl_delay_seconds": 15,
        "rate_limit_per_min": 4,
        "parse_strategy": "generic_html",
    },
)

DEFAULT_MUSIC_SOURCES: tuple[dict[str, str | bool | int | None], ...] = (
    {
        "name": "Soda Bar Shows",
        "domain": "sodabarmusic.com",
        "base_url": "https://www.sodabarmusic.com/events",
        "source_type": "html",
        "category_hint": "Music",
        "neighborhood": "North Park",
        "crawl_allowed": True,
        "crawl_delay_seconds": 12,
        "rate_limit_per_min": 5,
        "parse_strategy": "generic_html",
    },
    {
        "name": "Music Box San Diego",
        "domain": "musicboxsd.com",
        "base_url": "https://musicboxsd.com/events/",
        "source_type": "html",
        "category_hint": "Music",
        "neighborhood": "Little Italy",
        "crawl_allowed": True,
        "crawl_delay_seconds": 12,
        "rate_limit_per_min": 5,
        "parse_strategy": "generic_html",
    },
)


def build_default_sources() -> list[Source]:
    records: list[Source] = []
    for payload in (*DEFAULT_NIGHTLIFE_SOURCES, *DEFAULT_MUSIC_SOURCES):
        records.append(
            Source(
                region_id=REGION_SAN_DIEGO_ID,
                name=str(payload["name"]),
                domain=str(payload["domain"]),
                base_url=str(payload["base_url"]),
                source_type=str(payload["source_type"]),
                category_hint=str(payload["category_hint"]) if payload["category_hint"] else None,
                neighborhood=str(payload["neighborhood"]) if payload["neighborhood"] else None,
                is_active=True,
                crawl_allowed=bool(payload["crawl_allowed"]),
                crawl_delay_seconds=int(payload["crawl_delay_seconds"]),
                rate_limit_per_min=int(payload["rate_limit_per_min"]),
                attribution_text="Source listing courtesy of official venue calendar.",
                parse_strategy=str(payload["parse_strategy"]),
            )
        )
    return records
