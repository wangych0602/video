from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VideosConfig(AppConfig):
    name = 'videos'
    verbose_name=_('视频')