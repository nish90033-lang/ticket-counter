from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display  = ['name', 'venue', 'date', 'total_seats', 'created_at']
    search_fields = ['name', 'venue']
    ordering      = ['date']