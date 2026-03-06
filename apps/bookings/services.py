import logging
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from .models import Seat, SeatLock, Booking
from .exceptions import (
    SeatAlreadyReserved,
    SeatAlreadyLocked,
    LockNotFound,
    LockExpired,
    LockOwnedByAnotherUser,
    StaleVersionError,
    BookingAlreadyExists,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# STEP 1 — Lock the seat (short atomic transaction)
#
# - Grabs a Postgres row-level lock with select_for_update()
# - Checks permanently booked → raises
# - Checks active lock by someone else → raises with time remaining
# - Same user re-locking → refreshes expiry
# - Creates SeatLock with expiry window
# - Commits — DB row lock released immediately after block
#
# IntegrityError catch is the final safety net:
# Two requests can pass all checks simultaneously.
# First commits the OneToOne row, second hits DB constraint.
# We catch and convert to SeatAlreadyLocked.
# ─────────────────────────────────────────────────────────────────
def lock_seat(seat_id: int, user) -> SeatLock:
    lock_timeout = getattr(settings, 'SEAT_LOCK_TIMEOUT_SECONDS', 300)

    with transaction.atomic():
        try:
            seat = Seat.objects.select_for_update().get(id=seat_id)
        except Seat.DoesNotExist:
            from .exceptions import SeatNotFound
            raise SeatNotFound(f"Seat {seat_id} does not exist")

        # Guard 1 — permanently booked
        if seat.is_reserved:
            raise SeatAlreadyReserved(f"Seat {seat.seat_number} is already reserved")

        # Guard 2 — active lock check
        try:
            existing_lock = SeatLock.objects.get(seat=seat)

            if not existing_lock.is_expired():
                if existing_lock.user_id != user.id:
                    # Another user holds this lock
                    raise SeatAlreadyLocked(existing_lock.expires_at)
                else:
                    # Same user — refresh expiry instead of raising
                    existing_lock.expires_at = timezone.now() + timedelta(seconds=lock_timeout)
                    existing_lock.save(update_fields=['expires_at'])
                    return existing_lock
            else:
                # Expired lock — clean up before creating new one
                existing_lock.delete()

        except SeatLock.DoesNotExist:
            pass  # no lock exists — safe to proceed

        # Guard 3 — IntegrityError safety net
        try:
            seat_lock = SeatLock.objects.create(
                seat=seat,
                user=user,
                expires_at=timezone.now() + timedelta(seconds=lock_timeout)
            )
        except IntegrityError:
            # Lost the race at DB level — fetch winning lock for context
            seat_lock = SeatLock.objects.filter(seat_id=seat_id).first()
            if seat_lock:
                raise SeatAlreadyLocked(seat_lock.expires_at)
            else:
                # Created and immediately expired — extremely rare
                raise SeatAlreadyReserved()

    return seat_lock


# ─────────────────────────────────────────────────────────────────
# STEP 2 — Payment
#
# Happens in the VIEW, completely outside any DB transaction.
# Seat is held via SeatLock during this window.
# If payment takes too long and lock expires → user must restart.
# ─────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────
# STEP 3 — Confirm booking (second short atomic transaction)
#
# - Re-acquires row lock on the seat
# - Validates lock still exists and belongs to this user
# - Deletes the SeatLock
# - Creates the Booking
# - Marks seat reserved + bumps version (single query, atomic)
# ─────────────────────────────────────────────────────────────────
def confirm_booking(seat_id: int, user, payment_ref: str = None, expected_version: int = None) -> Booking:

    with transaction.atomic():
        seat = Seat.objects.select_for_update().get(id=seat_id)

        # Re-check permanent reservation
        if seat.is_reserved:
            raise SeatAlreadyReserved()

        # Validate lock exists
        try:
            seat_lock = SeatLock.objects.get(seat=seat)
        except SeatLock.DoesNotExist:
            raise LockNotFound("No lock found — it may have expired. Please try again.")

        if seat_lock.is_expired():
            seat_lock.delete()
            raise LockExpired("Your seat hold expired. Please select the seat again.")

        if seat_lock.user_id != user.id:
            raise LockOwnedByAnotherUser("This lock belongs to a different user.")

        # Idempotency guard
        if Booking.objects.filter(seat=seat).exists():
            raise BookingAlreadyExists()

        # Single query optimistic locking — check BEFORE creating booking
        # expected_version comes from before payment so we detect concurrent changes
        version_to_check = expected_version if expected_version is not None else seat.version
        rows_updated = Seat.objects.filter(
            id=seat.id,
            version=version_to_check   # stale version → WHERE matches 0 rows
        ).update(
            is_reserved=True,
            version=version_to_check + 1
        )

        if rows_updated == 0:
            raise StaleVersionError("Concurrent modification detected. Please retry.")

        seat_lock.delete()

        booking = Booking.objects.create(
            seat=seat,
            user=user,
            status=Booking.Status.CONFIRMED,
        )

    return booking


# ─────────────────────────────────────────────────────────────────
# UTILITY — Release lock manually (user clicks cancel)
# ─────────────────────────────────────────────────────────────────
def release_lock(seat_id: int, user) -> None:
    with transaction.atomic():
        try:
            seat_lock = SeatLock.objects.select_for_update().get(seat_id=seat_id)
        except SeatLock.DoesNotExist:
            return  # already gone

        if seat_lock.user_id != user.id:
            raise LockOwnedByAnotherUser("This lock belongs to a different user.")

        seat_lock.delete()