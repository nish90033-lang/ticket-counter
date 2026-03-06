from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Shorter lock timeout in dev so you don't wait 5 min during testing
SEAT_LOCK_TIMEOUT_SECONDS = 300