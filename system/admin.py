from django.contrib import admin

from .models import SiteConfig

@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'default_language', 'contact_email', 'registration_enabled', 'updated_at']
    fieldsets = (
        (None, {'fields': ('site_name', 'site_description', 'default_language', 'contact_email', 'registration_enabled')}),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
