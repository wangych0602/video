from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import LiveRoom, LiveSessionProxy

@admin.register(LiveRoom)
class LiveRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'teacher', 'status', 'scheduled_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'school__name')

@admin.register(LiveSessionProxy)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ('device_display', 'teacher', 'title', 'school', 'status', 'rtmp_push_url', 'hls_url', 'start_time', 'end_time')
    list_filter = ('status', 'school')
    search_fields = ('device__device_name', 'device__device_sn', 'teacher__user__username', 'stream_key', 'title')
    readonly_fields = ('stream_key', 'stream_token', 'token_used', 'rtmp_push_url', 'hls_url', 'created_time', 'start_time', 'end_time')

    class Media:
        css = {'all': ('admin/css/custom_admin.css',)}

    @admin.display(description=_('设备'), ordering='device')
    def device_display(self, obj):
        if obj.device_id:
            return obj.device
        return _('推流直播')
