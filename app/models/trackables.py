from app.database.session import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Trackable(Base):
    __tablename__ = "trackables"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, index=True)
    interval_minutes = Column(Integer, nullable=False, default=60)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="active")
    tracked_element_class = Column(String, nullable=True)
    next_check_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    snapshots = relationship(
        "Snapshot",
        back_populates="trackable",
        cascade="all, delete-orphan",
        order_by="desc(Snapshot.created_at)",
    )