from django.urls import path
from .views import LockSeatView, ConfirmBookingView, ReleaseLockView, SeatMapView

urlpatterns = [
    path('events/<int:event_id>/seats/',      SeatMapView.as_view(),        name='seat-map'),
    path('seats/<int:seat_id>/lock/',         LockSeatView.as_view(),       name='lock-seat'),
    path('seats/<int:seat_id>/lock/release/', ReleaseLockView.as_view(),    name='release-lock'),
    path('seats/<int:seat_id>/confirm/',      ConfirmBookingView.as_view(), name='confirm-booking'),
]
