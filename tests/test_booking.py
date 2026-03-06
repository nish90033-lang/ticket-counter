import pytest
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from apps.events.models import Event
from apps.bookings.models import Seat, SeatLock, Booking
from apps.bookings.services import lock_seat, confirm_booking
from apps.bookings.exceptions import (
    SeatAlreadyBooked, LockNotFound, LockExpired, NotLockOwner
)


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='pass')


@pytest.fixture
def user2(db):
    return User.objects.create_user(username='testuser2', password='pass')


@pytest.fixture
def event(db):
    return Event.objects.create(
        name='Test Concert',
        venue='Test Venue',
        date=timezone.now() + timedelta(days=30),
        total_seats=50
    )


@pytest.fixture
def seat(db, event):
    return Seat.objects.create(event=event, seat_number='A1')


@pytest.fixture
def locked_seat(db, seat, user):
    lock_seat(seat.id, user)
    return seat


# ── Happy Path ────────────────────────────────────────────────────────────────

class TestHappyPath:

    def test_booking_created_successfully(self, db, locked_seat, user):
        booking = confirm_booking(locked_seat.id, user)
        assert booking.seat   == locked_seat
        assert booking.user   == user
        assert booking.status == Booking.Status.CONFIRMED

    def test_seat_marked_reserved_after_booking(self, db, locked_seat, user):
        confirm_booking(locked_seat.id, user)
        locked_seat.refresh_from_db()
        assert locked_seat.is_reserved

    def test_version_bumped_after_booking(self, db, locked_seat, user):
        original_version = locked_seat.version
        confirm_booking(locked_seat.id, user)
        locked_seat.refresh_from_db()
        assert locked_seat.version == original_version + 1

    def test_lock_deleted_after_booking(self, db, locked_seat, user):
        confirm_booking(locked_seat.id, user)
        assert not SeatLock.objects.filter(seat=locked_seat).exists()

    def test_booking_ref_generated(self, db, locked_seat, user):
        booking = confirm_booking(locked_seat.id, user)
        assert booking.booking_ref
        assert len(booking.booking_ref) > 5


# ── Lock Guards ───────────────────────────────────────────────────────────────

class TestLockGuards:

    def test_confirm_without_lock_raises(self, db, seat, user):
        with pytest.raises(LockNotFound):
            confirm_booking(seat.id, user)

    def test_confirm_with_expired_lock_raises(self, db, seat, user):
        lock = lock_seat(seat.id, user)
        lock.expires_at = timezone.now() - timedelta(seconds=1)
        lock.save()
        with pytest.raises(LockExpired):
            confirm_booking(seat.id, user)

    def test_confirm_with_wrong_user_raises(self, db, locked_seat, user2):
        with pytest.raises(NotLockOwner):
            confirm_booking(locked_seat.id, user2)


# ── Optimistic Locking ────────────────────────────────────────────────────────

class TestOptimisticLocking:

    def test_stale_version_raises(self, db, locked_seat, user):
        from apps.bookings.exceptions import StaleVersionError
        # DB is now at version=999; pass expected_version=0 to simulate stale pre-payment snapshot
        Seat.objects.filter(id=locked_seat.id).update(version=999)
        with pytest.raises(StaleVersionError):
            confirm_booking(locked_seat.id, user, expected_version=0)

    def test_no_booking_created_on_stale_version(self, db, locked_seat, user):
        from apps.bookings.exceptions import StaleVersionError
        Seat.objects.filter(id=locked_seat.id).update(version=999)
        with pytest.raises(StaleVersionError):
            confirm_booking(locked_seat.id, user, expected_version=0)
        assert not Booking.objects.filter(seat=locked_seat).exists()


# ── Idempotency ───────────────────────────────────────────────────────────────

class TestIdempotency:

    def test_duplicate_confirm_raises(self, db, locked_seat, user):
        confirm_booking(locked_seat.id, user)
        with pytest.raises((SeatAlreadyBooked, LockNotFound)):
            confirm_booking(locked_seat.id, user)

    def test_only_one_booking_exists(self, db, locked_seat, user):
        confirm_booking(locked_seat.id, user)
        with pytest.raises(Exception):
            confirm_booking(locked_seat.id, user)
        assert Booking.objects.filter(seat=locked_seat).count() == 1


# ── Full E2E Flow ─────────────────────────────────────────────────────────────

class TestFullFlow:

    def test_lock_then_confirm_final_state(self, db, seat, user):
        lock_seat(seat.id, user)
        booking = confirm_booking(seat.id, user)

        seat.refresh_from_db()
        assert seat.is_reserved
        assert not SeatLock.objects.filter(seat=seat).exists()
        assert booking.status == Booking.Status.CONFIRMED
        assert Booking.objects.filter(seat=seat).count() == 1