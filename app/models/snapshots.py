from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.database.session import Base

class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, index=True)
    trackable_id = Column(Integer, ForeignKey("trackables.id"))
    snapshot_data = Column(String, nullable=False)
    snapshot_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())