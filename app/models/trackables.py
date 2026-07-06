from app.database.session import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

class Trackable(Base):
    __tablename__ = "trackable"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url = Column(String, nullable=False, index=True)
    content_type = Column(String, nullable=False)
    interval_minutes = Column(Integer, nullable=False, default=60)
    last_snapshot = Column(String, nullable=True)
    status = Column(String, nullable=False, default="active")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
