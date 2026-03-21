import os
from celery import Celery

REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

celery_app = Celery(
    "kric11_worker",
    broker=REDIS_URL,
    backend=RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="calculate_points")
def calculate_points_task(match_id: int):
    """
    Background job to ingest live data and trigger point calculations
    during the deadline rush.
    """
    # Logic to fetch ball-by-ball and upate match points to be implemented.
    return {"status": "success", "match_id": match_id, "message": "Points calculation triggered."}
