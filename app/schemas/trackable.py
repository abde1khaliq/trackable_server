from pydantic import BaseModel, Field
from datetime import datetime

class TrackableBase(BaseModel):
    url: str
    content_type: str
    interval_minutes: int = Field(default=60, ge=1)
    status: str = Field(default="active")

class TrackableResponse(TrackableBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None
    last_snapshot: str | None = None
