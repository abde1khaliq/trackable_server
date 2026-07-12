from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.models import Trackable, Snapshot
from app.api.dependencies import get_current_user
from app.schemas.trackable import TrackableWithSnapshot, TrackableForm
from app.utils.parser import parse_html
import hashlib
from datetime import datetime

router = APIRouter(prefix="/trackables", tags=["Trackables"])


@router.get("/", response_model=list[TrackableWithSnapshot])
async def get_trackables(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    result = await db.execute(select(Trackable).where(Trackable.user_id == user_id))
    trackables = result.scalars().all()

    response = []
    for trackable in trackables:
        snapshot_result = await db.execute(
            select(Snapshot)
            .where(Snapshot.trackable_id == trackable.id)
            .order_by(Snapshot.created_at.desc())
            .limit(1)
        )
        last_snapshot = snapshot_result.scalar_one_or_none()
        response.append({"trackable": trackable, "last_snapshot": last_snapshot})

    return response

from fastapi import HTTPException

@router.post("/")
async def create_trackable(
    trackable: TrackableForm,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    new_trackable = Trackable(
        **trackable.model_dump(),
        next_check_at=datetime.utcnow(),
        user_id=user_id,
    )

    db.add(new_trackable)
    await db.flush()

    extracted_content = parse_html(new_trackable.url, new_trackable.tracked_element_selector)

    if extracted_content is None:
        await db.rollback()
        raise HTTPException(
            status_code=422,
            detail="Selector did not match any element on the page — check the CSS selector and try again",
        )

    new_snapshot = Snapshot(
        trackable_id=new_trackable.id,
        snapshot_data=extracted_content,
        snapshot_hash=hashlib.sha256(extracted_content.encode()).hexdigest(),
    )

    db.add(new_snapshot)
    await db.commit()

    return {"message": "Trackable created successfully"}