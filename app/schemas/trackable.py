from pydantic import BaseModel, Field
from datetime import datetime

class TrackableBase(BaseModel):
    id: int
    user_id: int
    url: str
    content_type: str
    interval_minutes: int = Field(default=60, ge=1)
    status: str = Field(default="active")
    last_snapshot: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
