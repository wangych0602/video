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
        
        # Inject custom JS and CSS into admin pages
        if request.path.startswith('/admin/') and response.get('Content-Type', '').startswith('text/html'):
            custom_html = '''
<style>
.logo img, .brand img, .el-aside img[src*="media/site"] {
    max-height: 50px !important;
    height: 50px !important;
    width: auto !important;
}
.logo, .brand {
    height: 60px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
.icon-home .icon-item {
    width: 120px !important;
    height: 100px !important;
}
.icon-home .icon-item i {
    font-size: 36px !important;
}
</style>
<script>
document.addEventListener('DOMContentLoaded', function() {
    var logos = document.querySelectorAll('.logo img, .brand img, .el-aside img');
    logos.forEach(function(img) {
        var src = img.src || '';
        var alt = (img.alt || '').toLowerCase();
        if (src.indexOf('logo') > -1 || src.indexOf('site') > -1 || alt.indexOf('logo') > -1) {
            img.style.maxHeight = '50px';
            img.style.height = '50px';
            img.style.width = 'auto';
        }
    });
});
</script>
'''
            custom_code = custom_html.encode('utf-8')
            if hasattr(response, 'content'):
                try:
                    content = response.content
                    if b'</head>' in content:
                        response.content = content.replace(b'</head>', custom_code + b'</head>', 1)
                        if 'Content-Length' in response:
                            response['Content-Length'] = str(len(response.content))
                except Exception:
                    pass
        
        return response