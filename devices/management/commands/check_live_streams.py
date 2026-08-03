import logging
import urllib.request
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from devices.models import Device, LiveSession

logger = logging.getLogger(__name__)

ACTIVE_STATUSES = (LiveSession.Status.STARTING, LiveSession.Status.LIVE)


def check_hls_url(url, timeout=5):
    if not url:
        return False
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status == 200
    except Exception:
        return False


class Command(BaseCommand):
    help = '检测活跃直播的 HLS 流，断流时自动将 LiveSession 标记为 error'

    def handle(self, *args, **options):
        sessions = list(LiveSession.objects.filter(status__in=ACTIVE_STATUSES).select_related('device'))
        now = timezone.now()
        changed = 0
        for session in sessions:
            if session.status == LiveSession.Status.STARTING and now - session.created_time < timedelta(seconds=60):
                continue
            if check_hls_url(session.hls_url):
                continue
            session.status = LiveSession.Status.ERROR
            session.end_time = now
            session.save(update_fields=['status', 'end_time'])
            device = session.device
            if device.status == Device.Status.STREAMING:
                device.status = Device.Status.ERROR
                device.save(update_fields=['status', 'updated_at'])
            changed += 1
            self.stdout.write(f'LiveSession {session.id} marked as error (stream lost)')
        self.stdout.write(f'Checked {len(sessions)} active sessions, {changed} marked as error')
