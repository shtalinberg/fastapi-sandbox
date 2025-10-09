"""
Product synchronization tasks.
"""
import httpx
from celery import current_task

from core.celery_app import celery_app
from core.config import settings


@celery_app.task(bind=True, name="tasks.sync_products.sync_products_task")
def sync_products_task(self):
    """
    Periodic task to synchronize products from external API.
    """
    try:
        # Update task state
        current_task.update_state(
            state="PROGRESS",
            meta={"message": "Starting product synchronization..."}
        )

        # Make request to external API
        with httpx.Client() as client:
            response = client.get(f"{settings.EXTERNAL_API_URL}/posts", timeout=30)
            response.raise_for_status()

            products_data = response.json()

            # Process products (placeholder logic)
            processed_count = len(products_data)

            # Update task state
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "message": f"Processing {processed_count} products...",
                    "processed": processed_count
                }
            )

            # TODO: Save products to database when models are implemented

            return {
                "status": "success",
                "message": f"Successfully synchronized {processed_count} products",
                "processed_count": processed_count
            }

    except httpx.RequestError as e:
        # Update task state on error
        current_task.update_state(
            state="FAILURE",
            meta={"message": f"HTTP request failed: {str(e)}"}
        )
        raise

    except Exception as e:
        # Update task state on error
        current_task.update_state(
            state="FAILURE",
            meta={"message": f"Task failed: {str(e)}"}
        )
        raise