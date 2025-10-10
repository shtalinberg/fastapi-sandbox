"""
Celery application configuration.
"""

from celery import Celery

from core.config import settings

# Create Celery app
celery_app = Celery(
    "faproject",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["services.tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=60,  # 1 minute
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks configuration
celery_app.conf.beat_schedule = {
    "sync-products": {
        "task": "services.tasks.sync_products_task",
        "schedule": settings.SYNC_INTERVAL_MINUTES * 60.0,  # Convert to seconds
    },
}

if __name__ == "__main__":
    celery_app.start()
