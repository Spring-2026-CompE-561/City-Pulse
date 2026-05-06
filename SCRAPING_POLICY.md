# City Pulse Scraping and Source Policy

## Purpose
City Pulse ingests event metadata for San Diego nightlife, public events, and local music with a legal-first approach.

## Allowed Collection Channels
- Official APIs and structured feeds (preferred): Ticketmaster/Eventbrite/ICS/RSS/public venue APIs.
- Official website event pages with clear public access and compliant crawl policy.
- Partner submissions for social-only listings, including Instagram links.

## Disallowed Collection Channels
- Direct scraping of Instagram pages or private social content.
- Circumventing auth walls, bot-blocking, CAPTCHAs, or anti-automation controls.
- Republishing full copyrighted event copy when attribution requires linking to source.

## Per-Source Controls
- `crawl_allowed` must be true before any source is fetched.
- `crawl_delay_seconds` and `rate_limit_per_min` are enforced by connector policy.
- `robots_txt_url` and `terms_url` should be populated for each source.
- `attribution_text` should be stored and surfaced in UI when relevant.

## Data Handling Rules
- Store summary metadata (title, time, venue, promo summary) and canonical source URL.
- Use source-aware dedupe keys (`source_id + external_id`, canonical URL, fingerprint fallback).
- Track `last_seen_at` and source confidence for freshness indicators.

## Monitoring and Incident Response
- Every ingestion execution writes an `ingest_runs` row.
- Parser errors are logged in `error_summary` and counted in `error_count`.
- Sources with repeated parser failures should be temporarily disabled (`is_active=false`) until fixed.
