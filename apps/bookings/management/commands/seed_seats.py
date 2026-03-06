from django.core.management.base import BaseCommand
from apps.events.models import Event
from apps.bookings.models import Seat


class Command(BaseCommand):
    help = 'Seed seats for an event'

    def handle(self, *args, **kwargs):
        try:
            event = Event.objects.first()
        except Event.DoesNotExist:
            self.stdout.write(self.style.ERROR('No events found. Create one in admin first.'))
            return

        rows  = ['A', 'B', 'C', 'D', 'E']
        seats_per_row = 10

        created = 0
        for row in rows:
            for num in range(1, seats_per_row + 1):
                seat_number = f"{row}{num}"
                _, was_created = Seat.objects.get_or_create(
                    event=event,
                    seat_number=seat_number
                )
                if was_created:
                    created += 1

        self.stdout.write(
            self.style.SUCCESS(f'Created {created} seats for "{event.name}"')
        )