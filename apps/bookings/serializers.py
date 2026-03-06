from rest_framework import serializers
from .models import Seat, SeatLock, Booking


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Seat
        fields = ['id', 'seat_number', 'is_reserved', 'version', 'updated_at']


class SeatLockSerializer(serializers.ModelSerializer):
    seat_number = serializers.CharField(source='seat.seat_number', read_only=True)
    locked_by   = serializers.CharField(source='user.username',    read_only=True)
    seconds_remaining = serializers.SerializerMethodField()

    class Meta:
        model  = SeatLock
        fields = [
            'id', 'seat_number', 'locked_by',
            'locked_at', 'expires_at', 'seconds_remaining'
        ]

    def get_seconds_remaining(self, obj):
        from django.utils import timezone
        if obj.expires_at and obj.expires_at > timezone.now():
            return int((obj.expires_at - timezone.now()).total_seconds())
        return 0


class BookingSerializer(serializers.ModelSerializer):
    seat_number = serializers.CharField(source='seat.seat_number', read_only=True)
    username    = serializers.CharField(source='user.username',    read_only=True)

    class Meta:
        model  = Booking
        fields = [
            'id', 'booking_ref', 'seat_number',
            'username', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = fields