from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Celery tasks are sync by nature — no event loop involved,
# so a normal pooled sync engine works cleanly with no loop-affinity concerns.
sync_engine = create_engine(settings.database_url.replace("+asyncpg", "+psycopg"))
SyncSessionLocal = sessionmaker(bind=sync_engine)