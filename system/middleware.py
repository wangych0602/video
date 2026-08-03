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
        
        # Inject custom CSS into admin pages
        if request.path.startswith('/admin/') and response.get('Content-Type', '').startswith('text/html'):
            css_link = b'<link rel="stylesheet" type="text/css" href="/static/admin/css/custom.css">'
            if hasattr(response, 'content'):
                try:
                    content = response.content
                    if b'</head>' in content:
                        response.content = content.replace(b'</head>', css_link + b'</head>', 1)
                        if 'Content-Length' in response:
                            response['Content-Length'] = str(len(response.content))
                except Exception:
                    pass
        
        return response