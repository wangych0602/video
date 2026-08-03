"""Production settings for video_platform."""
import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from .settings import *  # noqa: F401,F403

DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY', '')
if not SECRET_KEY:
    raise ImproperlyConfigured('SECRET_KEY must be set in production.')

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

DATABASE_URL = os.environ.get('DATABASE_URL', '')
if not DATABASE_URL:
    raise ImproperlyConfigured('DATABASE_URL must be set in production.')
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600),
}

REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')

STATIC_URL = os.environ.get('STATIC_URL', '/static/')
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')

STORAGES = {
    'default': {
        'BACKEND': os.environ.get(
            'STORAGE_BACKEND',
            'django.core.files.storage.FileSystemStorage',
        ),
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}
# ponytail: set STORAGE_BACKEND to a django-storages backend (S3/OSS/MinIO)
# when object storage is needed; no business code changes required.

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'CSRF_TRUSTED_ORIGINS', 'http://localhost,http://127.0.0.1'
    ).split(',')
    if origin.strip()
]

RTMP_SERVER_URL = os.environ.get('RTMP_SERVER_URL', 'rtmp://localhost:1935').rstrip('/')
HLS_SERVER_URL = os.environ.get('HLS_SERVER_URL', 'http://localhost').rstrip('/')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'false').lower() == 'true'
