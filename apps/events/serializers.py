from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model  = Event
        fields = [
            'id', 'name', 'description', 'venue',
            'date', 'total_seats', 'available_seats', 'created_at'
        ]

    def get_available_seats(self, obj):
        from django.utils import timezone
        from apps.bookings.models import SeatLock

        booked = obj.seats.filter(is_reserved=True).count()
        locked = SeatLock.objects.filter(
            seat__event=obj,
            expires_at__gt=timezone.now()
        ).count()
        return obj.total_seats - booked - locked