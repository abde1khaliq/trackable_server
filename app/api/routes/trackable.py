from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.models.trackables import Trackable
from app.api.dependencies import get_current_user
from app.schemas.trackable import TrackableResponse, TrackableForm
from app.utils.parser import parse_html

router = APIRouter(prefix="/trackables", tags=["Trackables"])


@router.get("/", response_model=list[TrackableResponse])
async def get_trackables(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    result = await db.execute(select(Trackable).where(Trackable.user_id == user_id))
    trackables = result.scalars().all()
    return trackables


@router.post("/", response_model=TrackableResponse)
async def create_trackable(
    trackable: TrackableForm,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    new_trackable = Trackable(**trackable.dict(), user_id=user_id)
    db.add(new_trackable)
    await db.commit()
    await db.refresh(new_trackable)
    return new_trackable