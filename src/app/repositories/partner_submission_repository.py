from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models import PartnerSubmission


async def create_submission(db: AsyncSession, submission: PartnerSubmission) -> PartnerSubmission:
    db.add(submission)
    await db.flush()
    await db.refresh(submission)
    return submission


async def get_submission_by_id(db: AsyncSession, submission_id: int) -> PartnerSubmission | None:
    return await db.get(PartnerSubmission, submission_id)


async def list_submissions(
    db: AsyncSession, *, region_id: int, moderation_status: str | None = None
) -> list[PartnerSubmission]:
    query = select(PartnerSubmission).where(col(PartnerSubmission.region_id) == region_id)
    if moderation_status is not None:
        query = query.where(col(PartnerSubmission.moderation_status) == moderation_status)
    result = await db.execute(query.order_by(col(PartnerSubmission.created_at).desc()))
    return list(result.scalars().all())


async def review_submission(
    db: AsyncSession,
    *,
    submission: PartnerSubmission,
    moderation_status: str,
    moderation_notes: str | None,
    published_event_id: int | None,
) -> PartnerSubmission:
    submission.moderation_status = moderation_status
    submission.moderation_notes = moderation_notes
    submission.published_event_id = published_event_id
    submission.reviewed_at = datetime.now(UTC)
    await db.flush()
    await db.refresh(submission)
    return submission
