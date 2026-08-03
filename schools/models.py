from django.db import models
from django.utils.translation import gettext_lazy as _

class Building(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('教学楼名称'))
    description = models.TextField(blank=True, default='', verbose_name=_('描述'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))

    class Meta:
        verbose_name=_('教学楼')
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class School(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('教室名称'))
    building = models.ForeignKey(
        Building,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rooms',
        verbose_name=_('所属教学楼'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))

    class Meta:
        verbose_name=_('教室')
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name