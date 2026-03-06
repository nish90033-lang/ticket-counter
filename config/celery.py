import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('ticket_counter')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# ── Beat schedule ─────────────────────────────────────────────────
app.conf.beat_schedule = {
    'expire-stale-locks-every-60-seconds': {
        'task'    : 'apps.bookings.tasks.expire_stale_locks',
        'schedule': 60.0,
    },
}