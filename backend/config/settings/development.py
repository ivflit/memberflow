import os
from decouple import config
from .base import *

DEBUG = True

SECRET_KEY = config('SECRET_KEY', default='dev-insecure-key-change-in-prod')

ALLOWED_HOSTS = ['*']

# Support SQLite for CI (DATABASE_URL=sqlite:///test.db) and
# PostgreSQL for local Docker development.
_database_url = os.environ.get('DATABASE_URL', '')

if _database_url.startswith('sqlite'):
    _db_path = _database_url.replace('sqlite:///', '')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': _db_path or 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('POSTGRES_DB', default='memberflow'),
            'USER': config('POSTGRES_USER', default='memberflow'),
            'PASSWORD': config('POSTGRES_PASSWORD', default='memberflow'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }

# Allow Vite dev server origin (fallback for direct API calls outside Vite proxy)
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
]

# Celery — uses the Redis service defined in docker-compose.yml
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'false').lower() == 'true'
