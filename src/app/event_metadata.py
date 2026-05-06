"""Helpers for extracting event metadata persisted in tags_json."""

import json
import re
from html import unescape


_ORGANIZER_PLACEHOLDERS = {
    "organization",
    "organizer",
    "event organizer",
    "host",
    "hosted by",
    "presented by",
    "n/a",
    "na",
    "none",
    "unknown",
    "tbd",
}
_DESCRIPTION_GARBAGE_TOKENS = (
    "javascript is disabled",
    "enable javascript",
    "cookie policy",
    "all rights reserved",
    "sign up",
    "subscribe",
)
_TAG_PATTERN = re.compile(r"<[^>]+>")
_URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)


def clean_organizer_name(value: str | None) -> str | None:
    if not value:
        return None
    normalized = " ".join(value.strip().split())
    if not normalized:
        return None
    if normalized.lower() in _ORGANIZER_PLACEHOLDERS:
        return None
    return normalized


def clean_event_description(
    value: str | None,
    *,
    title: str | None = None,
    venue_name: str | None = None,
) -> str | None:
    if not value:
        return _fallback_description(title=title, venue_name=venue_name)
    text = unescape(value)
    text = text.replace("\\n", " ").replace("\\t", " ")
    text = text.replace("�", " ")
    text = _TAG_PATTERN.sub(" ", text)
    text = _URL_PATTERN.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip(" -|:;,.")
    if not text:
        return _fallback_description(title=title, venue_name=venue_name)
    lowered = text.lower()
    if any(token in lowered for token in _DESCRIPTION_GARBAGE_TOKENS):
        return _fallback_description(title=title, venue_name=venue_name)
    alpha_chars = len(re.findall(r"[A-Za-z]", text))
    if alpha_chars < 12:
        return _fallback_description(title=title, venue_name=venue_name)
    words = [token for token in text.split(" ") if token]
    if len(words) < 4:
        return _fallback_description(title=title, venue_name=venue_name)
    if lowered.startswith("by ") and len(words) <= 5:
        return _fallback_description(title=title, venue_name=venue_name)
    return text


def _fallback_description(*, title: str | None, venue_name: str | None) -> str | None:
    normalized_title = " ".join((title or "").split())
    normalized_venue = " ".join((venue_name or "").split())
    if normalized_title and normalized_venue:
        return f"{normalized_title} is happening at {normalized_venue} in San Diego."
    if normalized_title:
        return f"{normalized_title} is happening in San Diego."
    return None


def extract_organizer_name(tags_json: str | None) -> str | None:
    if not tags_json:
        return None
    try:
        payload = json.loads(tags_json)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    organizer_value = payload.get("organizer_name")
    if not isinstance(organizer_value, str):
        return None
    return clean_organizer_name(organizer_value)
