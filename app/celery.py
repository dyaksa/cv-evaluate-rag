from celery import Celery
from core.config import settings


def make_celery(app_name=__name__):
    celery =  Celery(app_name, broker=settings.CELERY_BROKER_URL)

    # Optional: Add configuration
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )

    return celery
    
# Create celery instance
celery = make_celery()