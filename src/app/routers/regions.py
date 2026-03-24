"""Region API: list regions; list events and users in a region (by id or string 'san diego')."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.region_repository import (
    list_events_in_region as list_region_events,
    list_regions as list_all_regions,
    list_users_in_region as list_region_users,
)
from app.region_map import parse_region_param
from app.schemas import EventRead, RegionRead, UserRead
from app.routers.users import _user_to_read

router = APIRouter(prefix="/api/regions", tags=["Regions"])


@router.get("/", response_model=list[RegionRead])
async def list_regions(db: AsyncSession = Depends(get_db)):
    """List all regions (e.g. San Diego)."""
    return await list_all_regions(db)


@router.get("/{region_id_or_name}/events", response_model=list[EventRead])
async def list_events_in_region(
    region_id_or_name: str | int,
    db: AsyncSession = Depends(get_db),
):
    """List events in this region. region_id_or_name: 0 or 'san diego' / 'san-diego'."""
    try:
        region_id = parse_region_param(region_id_or_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return await list_region_events(db, region_id=region_id)


@router.get("/{region_id_or_name}/users", response_model=list[UserRead])
async def list_users_in_region(
    region_id_or_name: str | int,
    db: AsyncSession = Depends(get_db),
):
    """List users in this region. region_id_or_name: 0 or 'san diego' / 'san-diego'."""
    try:
        region_id = parse_region_param(region_id_or_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    users = await list_region_users(db, region_id=region_id)
    return [_user_to_read(u) for u in users]
