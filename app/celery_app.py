from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()


celery_app = Celery(
    "Deribit-tracker",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
    include=["app.tasks.price_fetcher"],
)


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "fetch-prices-every-minute": {
            "task": "app.tasks.price_fetcher.fetch_and_save_prices",
            "schedule": crontab(minute="*"),
        }
    },
)
