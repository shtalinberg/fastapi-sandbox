"""
General utility tasks.
"""
from core.celery_app import celery_app


@celery_app.task(name="tasks.general.test_task")
def test_task(message: str = "Hello from Celery!"):
    """
    Simple test task for debugging.
    """
    return {
        "status": "success",
        "message": message,
        "task_id": test_task.request.id
    }