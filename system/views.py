from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import SiteConfig


class SiteConfigView(APIView):
    """获取站点配置"""
    permission_classes = [AllowAny]

    def get(self, request):
        config, created = SiteConfig.objects.get_or_create(id=1)
        return Response({
            'site_name': config.site_name,
            'site_description': config.site_description,
            'default_language': config.default_language,
            'contact_email': config.contact_email,
            'registration_enabled': config.registration_enabled,
            'footer_text': config.footer_text,
            'footer_copyright': config.footer_copyright,
            'footer_icp': config.footer_icp,
        })