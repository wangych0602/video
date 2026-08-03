from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class SystemConfig(AppConfig):
    name = 'system'
    verbose_name=_('系统设置')