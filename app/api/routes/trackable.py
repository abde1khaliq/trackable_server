from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.models import Trackable, Snapshot
from app.api.dependencies import get_current_user
from app.schemas.trackable import TrackableResponse, TrackableForm
from app.utils.parser import parse_html
import hashlib

router = APIRouter(prefix="/trackables", tags=["Trackables"])


@router.get("/", response_model=list[TrackableResponse])
async def get_trackables(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    result = await db.execute(select(Trackable).where(Trackable.user_id == user_id))
    trackables = result.scalars().all()
    return trackables


@router.post("/")
async def create_trackable(
    trackable: TrackableForm,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    new_trackable = Trackable(**trackable.dict(), user_id=user_id)

    db.add(new_trackable)
    await db.flush()  # ensures new_trackable.id is populated

    extracted_html = parse_html(new_trackable.url, new_trackable.tracked_element_class)

    new_snapshot = Snapshot(
        trackable_id=new_trackable.id,
        snapshot_data=extracted_html,
        snapshot_hash=hashlib.sha256(extracted_html.encode()).hexdigest()
    )

    db.add(new_snapshot)
    await db.flush()  # ensures new_snapshot.id is populated

    new_trackable.last_snapshot = new_snapshot.id # store the snapshot's id in the trackable
    await db.commit()

    return {"message": "Trackable created successfully"}