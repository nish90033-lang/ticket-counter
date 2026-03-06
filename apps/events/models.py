from django.db import models


class Event(models.Model):
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    venue       = models.CharField(max_length=255)
    date        = models.DateTimeField()
    total_seats = models.PositiveIntegerField()
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.name} @ {self.venue}"