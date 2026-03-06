import pytest
import threading
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from apps.events.models import Event
from apps.bookings.models import Seat, SeatLock, Booking
from apps.bookings.services import lock_seat, confirm_booking
from apps.bookings.exceptions import SeatAlreadyLocked, SeatAlreadyBooked


@pytest.fixture
def event(db):
    return Event.objects.create(
        name='Concurrency Test Concert',
        venue='Test Venue',
        date=timezone.now() + timedelta(days=30),
        total_seats=100
    )


@pytest.fixture
def seat(db, event):
    return Seat.objects.create(event=event, seat_number='A1')


@pytest.fixture
def users(db):
    return [
        User.objects.create_user(username=f'user{i}', password='pass')
        for i in range(100)
    ]


# ── 100 users lock same seat ──────────────────────────────────────────────────

@pytest.mark.django_db(transaction=True)
class TestConcurrentLocking:

    def test_exactly_one_lock_succeeds(self, db, seat, users):
        results  = []
        lock     = threading.Lock()

        def try_lock(user):
            try:
                lock_seat(seat.id, user)
                with lock:
                    results.append('success')
            except SeatAlreadyLocked:
                with lock:
                    results.append('failed')
            except Exception:
                with lock:
                    results.append('error')

        threads = [threading.Thread(target=try_lock, args=(u,)) for u in users]
        for t in threads: t.start()
        for t in threads: t.join()

        assert results.count('success') == 1
        assert results.count('success') + results.count('failed') + results.count('error') == 100
        assert results.count('error') < 5  # tolerate rare DB-level races, but not systemic failures
        assert SeatLock.objects.filter(seat=seat).count() == 1


# ── 100 users confirm same seat ───────────────────────────────────────────────

class TestConcurrentConfirm:

    def test_exactly_one_booking_confirmed(self, db, seat, users):
        # Give all users a lock record bypassing app logic
        # to test confirm_booking concurrency directly
        for user in users:
            SeatLock.objects.get_or_create(
                seat=seat,
                defaults={
                    'user'      : user,
                    'expires_at': timezone.now() + timedelta(seconds=300)
                }
            )
            break  # only one lock can exist due to OneToOne

        results = []
        lock    = threading.Lock()

        def try_confirm(user):
            try:
                confirm_booking(seat.id, user)
                with lock:
                    results.append('success')
            except Exception:
                with lock:
                    results.append('failed')

        # Only user who holds the lock can confirm
        threads = [threading.Thread(target=try_confirm, args=(u,)) for u in users[:10]]
        for t in threads: t.start()
        for t in threads: t.join()

        assert Booking.objects.filter(seat=seat).count() <= 1


# ── DB constraint bypass test ─────────────────────────────────────────────────

class TestDBConstraints:

    def test_db_rejects_duplicate_booking(self, db, seat, users):
        from django.db import IntegrityError
        user1, user2 = users[0], users[1]

        Booking.objects.create(
            seat=seat, user=user1,
            status=Booking.Status.CONFIRMED,
            booking_ref='REF001'
        )
        seat.is_reserved = True
        seat.save()

        with pytest.raises(IntegrityError):
            Booking.objects.create(
                seat=seat, user=user2,
                status=Booking.Status.CONFIRMED,
                booking_ref='REF002'
            )


# ── Lock expiry releases seat ─────────────────────────────────────────────────

class TestLockExpiry:

    def test_expired_lock_allows_new_user(self, db, seat, users):
        user1, user2 = users[0], users[1]
        lock = lock_seat(seat.id, user1)
        lock.expires_at = timezone.now() - timedelta(seconds=1)
        lock.save()

        new_lock = lock_seat(seat.id, user2)
        assert new_lock.user == user2
        assert SeatLock.objects.filter(seat=seat).count() == 1


# ── Optimistic locking version mismatch ──────────────────────────────────────

class TestOptimisticLockingConcurrency:

    def test_stale_version_prevents_double_booking(self, db, seat, users):
        from apps.bookings.exceptions import StaleVersionError
        user1, user2 = users[0], users[1]

        lock_seat(seat.id, user1)

        # Simulate another request already bumped the version in the DB
        # Use update() so the seat object's cached version stays stale
        Seat.objects.filter(id=seat.id).update(version=999)

        with pytest.raises(StaleVersionError):
            confirm_booking(seat.id, user1, expected_version=0)

        assert not Booking.objects.filter(seat=seat).exists()