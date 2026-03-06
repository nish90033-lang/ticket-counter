class SeatAlreadyReserved(Exception):
    """Seat has a confirmed booking — permanently taken."""
    pass


class SeatAlreadyLocked(Exception):
    """
    Seat has an active lock by another user.
    Carries expires_at so the frontend can show a countdown.
    """
    def __init__(self, expires_at):
        self.expires_at = expires_at
        super().__init__(f"Seat is locked until {expires_at}")


class LockNotFound(Exception):
    """
    User tried to confirm a booking but no valid lock exists.
    Either it expired or they never locked it.
    """
    pass


class LockExpired(Exception):
    """
    Lock existed but has passed its expires_at.
    User must restart the flow and lock the seat again.
    """
    pass


class LockOwnedByAnotherUser(Exception):
    """
    The requesting user doesn't own this lock.
    Could be a session hijack attempt or a bug — treat it seriously.
    """
    pass


class StaleVersionError(Exception):
    """
    Optimistic locking conflict.
    Two users read the same seat version — the second commit lost the race.
    Caller must retry the operation.
    """
    pass


class BookingAlreadyExists(Exception):
    """Booking record already exists for this seat — idempotency guard."""
    pass