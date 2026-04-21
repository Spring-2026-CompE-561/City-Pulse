from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class NormalizedEvent:
    source_id: int
    source_name: str
    source_type: str
    origin_type: str
    external_id: str | None
    external_url: str
    canonical_url: str
    title: str
    category: str
    content: str | None
    event_start_at: datetime | None
    event_end_at: datetime | None
    timezone: str
    venue_name: str | None
    venue_address: str | None
    neighborhood: str | None
    city: str = "San Diego"
    price_info: str | None = None
    promo_summary: str | None = None
    tags: list[str] = field(default_factory=list)
    source_confidence: float = 0.7
