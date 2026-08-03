from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from .models import SiteConfig


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'default_language', 'contact_email', 'footer_text', 'updated_at']
    fields = (
        'site_name',
        'site_description',
        'default_language',
        'contact_email',
        'registration_enabled',
        'footer_text',
        'footer_copyright',
        'footer_icp',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # 如果只有一条记录，直接跳转到编辑页面
        if SiteConfig.objects.count() == 1:
            obj = SiteConfig.objects.first()
            return redirect(f'../{obj.id}/change/')
        return super().changelist_view(request, extra_context)