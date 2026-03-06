import os
import dj_database_url

# Parse DATABASE_URL before base.py tries to read DB_NAME etc.
_db_url = os.environ.get('DATABASE_URL', '')
if _db_url:
    _db = dj_database_url.parse(_db_url)
    os.environ.setdefault('DB_NAME',     _db['NAME'])
    os.environ.setdefault('DB_USER',     _db['USER'])
    os.environ.setdefault('DB_PASSWORD', _db['PASSWORD'])
    os.environ.setdefault('DB_HOST',     _db['HOST'])
    os.environ.setdefault('DB_PORT',     str(_db['PORT']))

from .base import *

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '.railway.app').split(',')

# Override DB with full DATABASE_URL for connection pooling
DATABASES['default'] = dj_database_url.parse(_db_url, conn_max_age=600)

SECURE_HSTS_SECONDS         = 31536000
SECURE_SSL_REDIRECT         = True
SESSION_COOKIE_SECURE       = True
CSRF_COOKIE_SECURE          = True
SECURE_BROWSER_XSS_FILTER   = True
SECURE_CONTENT_TYPE_NOSNIFF = True

CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://*.onrender.com',
]