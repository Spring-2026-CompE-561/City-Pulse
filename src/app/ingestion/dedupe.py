import hashlib
from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    value = (url or "").strip()
    if not value:
        return ""
    parsed = urlparse(value)
    normalized_path = parsed.path.rstrip("/")
    return urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            normalized_path,
            "",
            parsed.query,
            "",
        )
    )


def normalize_text(value: str | None) -> str:
    return " ".join((value or "").strip().lower().split())


def build_fingerprint(
    *,
    title: str,
    venue_name: str | None,
    neighborhood: str | None,
    event_start_iso: str | None,
) -> str:
    payload = "|".join(
        [
            normalize_text(title),
            normalize_text(venue_name),
            normalize_text(neighborhood),
            normalize_text(event_start_iso),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_content_signature(
    *,
    title: str,
    content: str | None,
    venue_name: str | None,
    neighborhood: str | None,
    event_start_iso: str | None,
) -> str:
    normalized_content = normalize_text(content)
    payload = "|".join(
        [
            normalize_text(title),
            normalized_content[:180],
            normalize_text(venue_name),
            normalize_text(neighborhood),
            normalize_text(event_start_iso)[:10],
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
