import logging
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Seat, SeatLock, Booking
from .services import lock_seat, confirm_booking, release_lock
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
# POST /api/seats/<seat_id>/lock/
# Step 1 — temporarily hold the seat for the requesting user
# ─────────────────────────────────────────────────────────────────
class LockSeatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, seat_id):
        try:
            seat_lock = lock_seat(seat_id=seat_id, user=request.user)

            return Response({
                'status'           : 'locked',
                'seat_id'          : seat_id,
                'locked_by'        : request.user.username,
                'expires_at'       : seat_lock.expires_at,
                'seconds_remaining': int(
                    (seat_lock.expires_at - timezone.now()).total_seconds()
                ),
            }, status=status.HTTP_200_OK)

        except SeatAlreadyReserved:
            return Response(
                {'error': 'This seat is already booked.'},
                status=status.HTTP_409_CONFLICT
            )

        except SeatAlreadyLocked as e:
            return Response({
                'error'              : 'Seat is currently held by another user.',
                'expires_at'         : e.expires_at,
                'retry_after_seconds': int(
                    (e.expires_at - timezone.now()).total_seconds()
                ),
            }, status=status.HTTP_423_LOCKED)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.exception(f"Unexpected error in LockSeatView: {e}")
            return Response(
                {'error': 'Something went wrong. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ─────────────────────────────────────────────────────────────────
# POST /api/seats/<seat_id>/confirm/
# Step 3 — called after payment succeeds
# ─────────────────────────────────────────────────────────────────
class ConfirmBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, seat_id):
        payment_ref = request.data.get('payment_ref')

        try:
            booking = confirm_booking(
                seat_id=seat_id,
                user=request.user,
                payment_ref=payment_ref
            )

            return Response({
                'status'      : 'confirmed',
                'booking_ref' : booking.booking_ref,
                'seat_id'     : seat_id,
                'user'        : request.user.username,
                'confirmed_at': booking.created_at,
            }, status=status.HTTP_201_CREATED)

        except SeatAlreadyReserved:
            return Response(
                {'error': 'Seat was booked by someone else during payment.'},
                status=status.HTTP_409_CONFLICT
            )

        except LockNotFound:
            return Response(
                {'error': 'No active lock found. Please select the seat again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except LockExpired:
            return Response(
                {'error': 'Your seat hold expired. Please select the seat again.'},
                status=status.HTTP_410_GONE
            )

        except LockOwnedByAnotherUser:
            return Response(
                {'error': 'This lock does not belong to you.'},
                status=status.HTTP_403_FORBIDDEN
            )

        except StaleVersionError:
            return Response(
                {'error': 'Conflict detected. Please retry.'},
                status=status.HTTP_409_CONFLICT
            )

        except BookingAlreadyExists:
            # Idempotent — booking already confirmed, return success
            booking = Booking.objects.get(seat_id=seat_id, user=request.user)
            return Response({
                'status'     : 'confirmed',
                'booking_ref': booking.booking_ref,
                'seat_id'    : seat_id,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Unexpected error in ConfirmBookingView: {e}")
            return Response(
                {'error': 'Something went wrong. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ─────────────────────────────────────────────────────────────────
# DELETE /api/seats/<seat_id>/lock/release/
# User explicitly cancels their hold
# ─────────────────────────────────────────────────────────────────
class ReleaseLockView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, seat_id):
        try:
            release_lock(seat_id=seat_id, user=request.user)
            return Response(
                {'status': 'released', 'seat_id': seat_id},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(f"Unexpected error in ReleaseLockView: {e}")
            return Response(
                {'error': 'Something went wrong.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ─────────────────────────────────────────────────────────────────
# GET /api/events/<event_id>/seats/
# Returns live seat map — frontend polls this every 10s
# ─────────────────────────────────────────────────────────────────
class SeatMapView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        seats = Seat.objects.filter(
            event_id=event_id
        ).select_related('lock', 'booking')   # avoid N+1

        now    = timezone.now()
        result = []

        for seat in seats:
            seat_data = {
                'seat_id'    : seat.id,
                'seat_number': seat.seat_number,
                'row'        : seat.seat_number[0],
            }

            if seat.is_reserved:
                seat_data['status'] = 'reserved'

            elif hasattr(seat, 'lock') and not seat.lock.is_expired():
                lock = seat.lock
                seat_data['status']            = 'locked'
                seat_data['seconds_remaining'] = int(
                    (lock.expires_at - now).total_seconds()
                )
                seat_data['locked_by_you'] = (lock.user_id == request.user.id)

            else:
                seat_data['status'] = 'available'

            result.append(seat_data)

        return Response({'seats': result}, status=status.HTTP_200_OK)