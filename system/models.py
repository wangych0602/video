from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteConfig(models.Model):
    site_name = models.CharField(max_length=100, blank=True, default='', verbose_name=_('站点名称'))
    site_description = models.TextField(blank=True, verbose_name=_('站点描述'))
    default_language = models.CharField(max_length=10, default='zh-hans', verbose_name=_('默认语言'))
    contact_email = models.EmailField(blank=True, verbose_name=_('联系邮箱'))
    registration_enabled = models.BooleanField(default=True, verbose_name=_('允许注册'))
    # Footer 设置
    footer_text = models.CharField(max_length=200, blank=True, default='', verbose_name=_('Footer 文字'))
    footer_copyright = models.CharField(max_length=200, blank=True, default='', verbose_name=_('版权信息'))
    footer_icp = models.CharField(max_length=100, blank=True, default='', verbose_name=_('ICP备案号'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))

    class Meta:
        verbose_name = _('系统设置')
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        self.id = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.site_name or _('系统设置')