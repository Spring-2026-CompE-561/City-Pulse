"""CLI command to run event ingestion from the backend."""

import argparse
import asyncio
import json
from datetime import datetime

from app.config import settings
from app.database import async_session_maker, init_db
from app.ingestion.service import run_ingestion


def _parse_datetime(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "Invalid datetime format. Use ISO-8601, e.g. 2026-05-05T00:00:00Z"
        ) from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="city-pulse-ingest",
        description="Run backend event ingestion manually.",
    )
    parser.add_argument(
        "--source-id",
        type=int,
        default=None,
        help="Optional source id. Omit to ingest all active sources.",
    )
    parser.add_argument(
        "--area",
        type=str,
        default=None,
        help="Optional neighborhood filter.",
    )
    parser.add_argument(
        "--start-date",
        type=_parse_datetime,
        default=None,
        help="Optional ISO-8601 ingestion window start.",
    )
    parser.add_argument(
        "--end-date",
        type=_parse_datetime,
        default=None,
        help="Optional ISO-8601 ingestion window end.",
    )
    return parser


async def _run_ingestion_command(args: argparse.Namespace) -> int:
    if not settings.skip_db_init:
        await init_db()
    async with async_session_maker() as db:
        result = await run_ingestion(
            db,
            source_id=args.source_id,
            area=args.area,
            start_date=args.start_date,
            end_date=args.end_date,
            trigger_type="cli",
        )
        await db.commit()
    print(json.dumps(result))
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    return asyncio.run(_run_ingestion_command(args))


if __name__ == "__main__":
    raise SystemExit(main())
