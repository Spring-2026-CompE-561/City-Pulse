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


def build_fingerprint(
    *,
    title: str,
    venue_name: str | None,
    neighborhood: str | None,
    event_start_iso: str | None,
) -> str:
    payload = "|".join(
        [
            title.strip().lower(),
            (venue_name or "").strip().lower(),
            (neighborhood or "").strip().lower(),
            (event_start_iso or "").strip().lower(),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
