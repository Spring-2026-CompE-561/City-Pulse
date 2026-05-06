"""Partner submission APIs for official social/event intake."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user_required, require_ingest_api_key
from app.database import get_db
from app.event_categories import validate_event_category
from app.models import PartnerSubmission, User
from app.region_map import REGION_SAN_DIEGO_ID
from app.repository.event import create_event
from app.repository.partner_submission import (
    create_submission,
    get_submission_by_id,
    list_submissions,
    review_submission,
)
from app.schemas import (
    PartnerSubmissionCreate,
    PartnerSubmissionRead,
    PartnerSubmissionReview,
)

router = APIRouter(prefix="/api/partner-submissions", tags=["PartnerSubmissions"])


@router.post("/", response_model=PartnerSubmissionRead, status_code=201)
async def submit_partner_event(
    payload: PartnerSubmissionCreate,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    submission = PartnerSubmission(
        region_id=REGION_SAN_DIEGO_ID,
        submitted_by_user_id=current_user.id,
        organizer_name=payload.organizer_name,
        organizer_contact=payload.organizer_contact,
        instagram_handle=payload.instagram_handle,
        instagram_post_url=payload.instagram_post_url,
        external_event_url=payload.external_event_url,
        title=payload.title,
        description=payload.description,
        category=validate_event_category(payload.category),
        neighborhood=payload.neighborhood,
        venue_name=payload.venue_name,
        venue_address=payload.venue_address,
        event_start_at=payload.event_start_at,
        event_end_at=payload.event_end_at,
        moderation_status="pending",
    )
    return await create_submission(db, submission)


@router.get("/", response_model=list[PartnerSubmissionRead])
async def get_partner_submissions(
    moderation_status: str | None = Query(default=None),
    _auth: None = Depends(require_ingest_api_key),
    db: AsyncSession = Depends(get_db),
):
    return await list_submissions(
        db, region_id=REGION_SAN_DIEGO_ID, moderation_status=moderation_status
    )


@router.put("/{submission_id}/review", response_model=PartnerSubmissionRead)
async def review_partner_submission(
    submission_id: int,
    payload: PartnerSubmissionReview,
    _auth: None = Depends(require_ingest_api_key),
    db: AsyncSession = Depends(get_db),
):
    submission = await get_submission_by_id(db, submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    published_event_id: int | None = None
    if payload.moderation_status == "approved":
        event = await create_event(
            db,
            region_id=submission.region_id,
            user_id=submission.submitted_by_user_id,
            title=submission.title,
            category=validate_event_category(submission.category),
            content=submission.description,
            origin_type="partner_submission",
            external_url=submission.external_event_url or submission.instagram_post_url,
            canonical_url=submission.external_event_url or submission.instagram_post_url,
            event_start_at=submission.event_start_at,
            event_end_at=submission.event_end_at,
            timezone="America/Los_Angeles",
            venue_name=submission.venue_name,
            venue_address=submission.venue_address,
            neighborhood=submission.neighborhood,
            city="San Diego",
        )
        published_event_id = event.id
    return await review_submission(
        db,
        submission=submission,
        moderation_status=payload.moderation_status,
        moderation_notes=payload.moderation_notes,
        published_event_id=published_event_id,
    )
