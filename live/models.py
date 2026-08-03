from django.db import models
from django.utils.translation import gettext_lazy as _


class LiveRoom(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', _('待开播')
        LIVE = 'live', _('直播中')
        ENDED = 'ended', _('已结束')
    name = models.CharField(max_length=255, verbose_name=_('直播间名称'))
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='live_rooms',
        verbose_name=_('学校'),
    )
    teacher = models.ForeignKey(
        'users.TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='live_rooms',
        verbose_name=_('教师'),
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED, verbose_name=_('状态'))
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name=_('预约时间'))
    started_at = models.DateTimeField(null=True, blank=True, verbose_name=_('开始时间'))
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name=_('结束时间'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))

    class Meta:
        verbose_name=_('直播间')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

from devices.models import LiveSession

class LiveSessionProxy(LiveSession):
    class Meta:
        proxy = True
        verbose_name = _('直播会话')
        verbose_name_plural = verbose_name
