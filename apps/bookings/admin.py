from django.contrib import admin
from django.utils import timezone
from .models import Seat, SeatLock, Booking


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display  = ['seat_number', 'event', 'is_reserved', 'version', 'updated_at']
    list_filter   = ['is_reserved', 'event']
    search_fields = ['seat_number']
    ordering      = ['event', 'seat_number']


@admin.register(SeatLock)
class SeatLockAdmin(admin.ModelAdmin):
    list_display  = ['seat', 'user', 'locked_at', 'expires_at', 'is_expired_display']
    list_filter   = ['user']
    search_fields = ['seat__seat_number', 'user__username']
    ordering      = ['expires_at']

    # Show a clear expired/active indicator in admin list
    @admin.display(boolean=True, description='Expired?')
    def is_expired_display(self, obj):
        return obj.is_expired()


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display  = ['booking_ref', 'seat', 'user', 'status', 'created_at']
    list_filter   = ['status']
    search_fields = ['booking_ref', 'user__username', 'seat__seat_number']
    ordering      = ['-created_at']
    readonly_fields = ['booking_ref', 'created_at', 'updated_at']