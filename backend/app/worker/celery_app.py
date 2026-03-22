# Celery worker — only used in Docker/local dev, not on Vercel
# This file is intentionally kept minimal to avoid import errors
# when celery/redis packages aren't installed in production.

import os

try:
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
        return {"status": "success", "match_id": match_id}

except ImportError:
    # Celery not installed (Vercel serverless) — skip silently
    celery_app = None
