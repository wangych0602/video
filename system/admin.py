from django.contrib import admin
from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import SiteConfig, OperationLog


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'default_language', 'contact_email', 'footer_text', 'updated_at']
    fields = (
        'site_logo',
        'site_name',
        'site_description',
        'default_language',
        'contact_email',
        'registration_enabled',
        'footer_text',
        'footer_copyright',
        'footer_icp',
    )
    readonly_fields = ['updated_at']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        if SiteConfig.objects.count() == 1:
            obj = SiteConfig.objects.first()
            url = reverse('admin:system_siteconfig_change', args=[obj.id])
            return redirect(url)
        return super().changelist_view(request, extra_context)


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ['action_time', 'user', 'content_type', 'object_repr', 'action_flag_colored', 'change_message']
    list_filter = ['action_flag', 'content_type', 'action_time', 'user']
    search_fields = ['object_repr', 'change_message', 'user__username']
    date_hierarchy = 'action_time'
    readonly_fields = [
        'action_time', 'user', 'content_type', 'object_id',
        'object_repr', 'action_flag', 'change_message'
    ]
    ordering = ['-action_time']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def action_flag_colored(self, obj):
        flags = {
            ADDITION: _('添加'),
            CHANGE: _('修改'),
            DELETION: _('删除'),
        }
        flag = flags.get(obj.action_flag, obj.action_flag)
        colors = {
            ADDITION: '#67c23a',
            CHANGE: '#409eff',
            DELETION: '#f56c6c',
        }
        color = colors.get(obj.action_flag, '#909399')
        return format_html('<span style=\"color: {}\">{}</span>', color, flag)
    action_flag_colored.short_description = _('操作类型')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'content_type')