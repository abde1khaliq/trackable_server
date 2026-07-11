from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery("watcher", broker=settings.redis_broker, include=["app.tasks"])

celery_app.conf.beat_schedule = {
    "dispatch-due-checks": {
        "task": "app.tasks.dispatch_due_checks",
        "schedule": 60.0,
    },
}