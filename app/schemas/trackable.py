from pydantic import BaseModel, Field
from datetime import datetime

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
    interval_minutes: int = Field(default=60, ge=1)
    description: str | None = None
    status: str = Field(default="active")
    created_at: datetime
    updated_at: datetime | None = None