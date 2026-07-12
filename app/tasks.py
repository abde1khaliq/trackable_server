import hashlib
import logging
from datetime import datetime, timedelta
from sqlalchemy import func, select
from app.celery import celery_app
from app.database.sync_session import SyncSessionLocal
from app.models import Trackable, Snapshot
from app.utils.parser import parse_html

logger = logging.getLogger(__name__)


@celery_app.task
def dispatch_due_checks():
    with SyncSessionLocal() as db:
        due_trackables = db.execute(
            select(Trackable).where(Trackable.next_check_at <= func.now())
        ).scalars().all()

        for trackable in due_trackables:
            check_trackable.delay(trackable.id)
            trackable.next_check_at = datetime.utcnow() + timedelta(
                minutes=trackable.interval_minutes
            )

        db.commit()


@celery_app.task
def check_trackable(trackable_id: int):
    with SyncSessionLocal() as db:
        trackable = db.execute(
            select(Trackable).where(Trackable.id == trackable_id)
        ).scalar_one()

        last_snapshot = db.execute(
            select(Snapshot)
            .where(Snapshot.trackable_id == trackable_id)
            .order_by(Snapshot.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()

        parsed = parse_html(trackable.url, trackable.tracked_element_selector)

        if parsed is None:
            logger.warning(
                "Check failed for trackable %s (%s): selector matched nothing "
                "or the page could not be fetched",
                trackable.id,
                trackable.tracked_element_selector,
            )
            # Don't overwrite snapshot_data/hash with None — just skip this check.
            # Optionally mark the trackable so it surfaces in the UI:
            # trackable.status = "error"
            # db.commit()
            return

        if last_snapshot is None or parsed != last_snapshot.snapshot_data:
            new_snapshot = Snapshot(
                trackable_id=trackable.id,
                snapshot_data=parsed,
                snapshot_hash=hashlib.sha256(parsed.encode()).hexdigest(),
            )
            db.add(new_snapshot)
            db.commit()