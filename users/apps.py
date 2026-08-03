from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name=_('用户')

    def ready(self):
        from django.apps import apps
        from django.contrib.admin import AdminSite

        apps.get_app_config('auth').verbose_name = _('权限控制')

        _get_app_list = AdminSite.get_app_list
        def _app_list(site, request, app_label=None):
            result = _get_app_list(site, request, app_label)
            if app_label is None:
                result.sort(key=lambda x: (x.get('app_label') == 'system', x['name'].lower()))
            return result
        AdminSite.get_app_list = _app_list
