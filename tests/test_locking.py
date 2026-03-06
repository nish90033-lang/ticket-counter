import pytest
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from apps.events.models import Event
from apps.bookings.models import Seat, SeatLock
from apps.bookings.services import lock_seat, release_lock
from apps.bookings.exceptions import (
    SeatAlreadyLocked, SeatAlreadyBooked
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


# ── Acquiring Locks ───────────────────────────────────────────────────────────

class TestAcquiringLocks:

    def test_user_can_lock_available_seat(self, db, seat, user):
        lock = lock_seat(seat.id, user)
        assert lock.seat == seat
        assert lock.user == user

    def test_lock_has_correct_expiry(self, db, seat, user):
        lock = lock_seat(seat.id, user)
        expected = timezone.now() + timedelta(seconds=300)
        diff = abs((lock.expires_at - expected).total_seconds())
        assert diff < 5  # within 5 seconds

    def test_lock_nonexistent_seat_raises(self, db, user):
        from apps.bookings.exceptions import SeatNotFound
        with pytest.raises(SeatNotFound):
            lock_seat(99999, user)


# ── Lock Contention ───────────────────────────────────────────────────────────

class TestLockContention:

    def test_second_user_cannot_lock_locked_seat(self, db, seat, user, user2):
        lock_seat(seat.id, user)
        with pytest.raises(SeatAlreadyLocked):
            lock_seat(seat.id, user2)

    def test_exception_carries_expiry_time(self, db, seat, user, user2):
        lock_seat(seat.id, user)
        with pytest.raises(SeatAlreadyLocked) as exc_info:
            lock_seat(seat.id, user2)
        assert exc_info.value.expires_at is not None


# ── Lock Refresh ──────────────────────────────────────────────────────────────

class TestLockRefresh:

    def test_same_user_can_relock_extending_expiry(self, db, seat, user):
        first_lock  = lock_seat(seat.id, user)
        first_expiry = first_lock.expires_at
        second_lock = lock_seat(seat.id, user)
        assert second_lock.expires_at >= first_expiry
        assert SeatLock.objects.filter(seat=seat).count() == 1


# ── Lock Expiry ───────────────────────────────────────────────────────────────

class TestLockExpiry:

    def test_expired_lock_detected(self, db, seat, user):
        lock = lock_seat(seat.id, user)
        lock.expires_at = timezone.now() - timedelta(seconds=1)
        lock.save()
        assert not SeatLock.active_lock_exists(seat.id)

    def test_new_user_can_lock_after_expiry(self, db, seat, user, user2):
        lock = lock_seat(seat.id, user)
        lock.expires_at = timezone.now() - timedelta(seconds=1)
        lock.save()
        new_lock = lock_seat(seat.id, user2)
        assert new_lock.user == user2


# ── Release Lock ──────────────────────────────────────────────────────────────

class TestReleaseLock:

    def test_owner_can_release_lock(self, db, seat, user):
        lock_seat(seat.id, user)
        release_lock(seat.id, user)
        assert not SeatLock.active_lock_exists(seat.id)

    def test_non_owner_cannot_release_lock(self, db, seat, user, user2):
        from apps.bookings.exceptions import NotLockOwner
        lock_seat(seat.id, user)
        with pytest.raises(NotLockOwner):
            release_lock(seat.id, user2)


# ── active_lock_exists ────────────────────────────────────────────────────────

class TestActiveLockExists:

    def test_returns_true_when_active_lock(self, db, seat, user):
        lock_seat(seat.id, user)
        assert SeatLock.active_lock_exists(seat.id)

    def test_returns_false_when_no_lock(self, db, seat):
        assert not SeatLock.active_lock_exists(seat.id)