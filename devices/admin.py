from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        'device_name',
        'device_sn',
        'school',
        'status',
        'last_online_time',
        'current_live_status',
    )
    list_filter = ('status', 'device_type', 'school')
    search_fields = ('device_sn', 'device_name', 'ip_address', 'mac_address')
    readonly_fields = ('device_token', 'last_online_time', 'created_at', 'updated_at')

    def current_live_status(self, obj):
        session = obj.live_sessions.filter(status__in=['created', 'starting', 'live']).first()
        return session.status if session else _('无')

    current_live_status.short_description=_('直播状态')

