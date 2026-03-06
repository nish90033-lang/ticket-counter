import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction

from .models import SeatLock

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def expire_stale_locks(self):
    """
    Runs every 60 seconds via Celery beat.
    Deletes any SeatLock where expires_at is in the past.

    skip_locked=True — skips rows locked by other transactions.
    Prevents this task from blocking under load and avoids
    deadlocks if two beat instances overlap.
    """
    try:
        now = timezone.now()

        with transaction.atomic():
            expired_locks = SeatLock.objects.select_for_update(
                skip_locked=True
            ).filter(
                expires_at__lte=now
            )

            count = expired_locks.count()

            if count == 0:
                logger.info("expire_stale_locks: nothing to clean up")
                return

            expired_locks.delete()
            logger.info(f"expire_stale_locks: deleted {count} expired lock(s)")

    except Exception as exc:
        logger.error(f"expire_stale_locks failed: {exc}", exc_info=True)
        # Exponential backoff: 60s → 120s → 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))