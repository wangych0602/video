from django.apps import AppConfig


class SystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'system'
    verbose_name = '系统管理'

    def ready(self):
        # 应用启动时自动创建默认站点配置
        try:
            from .models import SiteConfig
            SiteConfig.objects.get_or_create(id=1)
        except Exception:
            pass