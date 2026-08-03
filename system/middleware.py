from django.contrib import admin
from django.conf import settings
from .models import SiteConfig


class SiteConfigMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            try:
                config = SiteConfig.objects.get(id=1)
                if config.site_name:
                    admin.site.site_header = config.site_name
                    admin.site.site_title = config.site_name
                    admin.site.index_title = config.site_name
                if config.site_logo:
                    settings.SIMPLEUI_LOGO = config.site_logo.url
            except SiteConfig.DoesNotExist:
                pass
        response = self.get_response(request)
        return response