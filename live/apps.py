from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LiveConfig(AppConfig):
    name = 'live'
    verbose_name=_('直播')