import redis
from django.conf import settings
from django.db import connection
from django.http import JsonResponse


def health(request):
    checks = {'django': True, 'database': True, 'redis': True}
    status = 200
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
    except Exception:
        checks['database'] = False
        status = 503
    try:
        client = redis.Redis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        checks['redis'] = bool(client.ping())
        if not checks['redis']:
            status = 503
    except Exception:
        checks['redis'] = False
        status = 503
    return JsonResponse(
        {'status': 'ok' if status == 200 else 'error', 'checks': checks},
        status=status,
    )
