from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class SnapshotInfo(BaseModel):
    id: int
    snapshot_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrackableForm(BaseModel):
    name: str
    url: str
    interval_minutes: int = Field(default=60, ge=1)
    description: str | None = None
    status: str = Field(default="active")
    tracked_element_class: str = Field(..., description="The CSS class of the element to track on the webpage.")

class TrackableResponse(BaseModel):
    id: int
    name: str
    url: str
    interval_minutes: int
    description: str | None = None
    status: str
    next_check_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TrackableWithSnapshot(BaseModel):
    trackable: TrackableResponse
    last_snapshot: SnapshotInfo | None = None

    model_config = ConfigDict(from_attributes=True)