from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import shortuuid

from apps.events.models import Event          # ← import from events app


# ─────────────────────────────────────────────
# MODEL 1 — Seat
# ─────────────────────────────────────────────
class Seat(models.Model):
    event       = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_reserved = models.BooleanField(default=False)

    # Optimistic locking
    # version bumps on every confirmed booking write
    # if two transactions read version=3, first to commit wins
    # second sees rows_updated=0 and must retry
    version    = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event', 'seat_number')
        ordering        = ['seat_number']

    def __str__(self):
        return f"{self.event.name} — Seat {self.seat_number}"


# ─────────────────────────────────────────────
# MODEL 2 — SeatLock (temporary reservation)
# ─────────────────────────────────────────────
class SeatLock(models.Model):
    seat = models.OneToOneField(
        Seat,
        on_delete=models.CASCADE,
        related_name='lock'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='seat_locks'
    )
    locked_at  = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Lock: Seat {self.seat.seat_number} by {self.user.username} until {self.expires_at}"

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def is_owned_by(self, user):
        return self.user_id == user.id and not self.is_expired()

    @classmethod
    def active_lock_exists(cls, seat_id):
        return cls.objects.filter(
            seat_id=seat_id,
            expires_at__gt=timezone.now()
        ).exists()


# ─────────────────────────────────────────────
# MODEL 3 — Booking (permanent record)
# ─────────────────────────────────────────────
class Booking(models.Model):

    class Status(models.TextChoices):
        PENDING   = 'PENDING',   'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        FAILED    = 'FAILED',    'Failed'

    seat = models.OneToOneField(
        Seat,
        on_delete=models.PROTECT,
        related_name='booking'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='bookings'
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    booking_ref = models.CharField(
        max_length=22,
        unique=True,
        default=shortuuid.uuid
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['booking_ref']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Booking {self.booking_ref} — {self.status}"