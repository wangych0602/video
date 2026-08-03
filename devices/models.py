import secrets

from django.db import models
from django.utils.translation import gettext_lazy as _


def generate_device_token():
    return secrets.token_urlsafe(32)


class Device(models.Model):
    class DeviceType(models.TextChoices):
        RECORDING_HOST = 'recording_host', _('录播主机')
        CAMERA = 'camera', _('摄像头')
        MICROPHONE = 'microphone', _('麦克风')
        SPEAKER = 'speaker', _('音箱')
        TERMINAL = 'terminal', _('终端')
    class Status(models.TextChoices):
        OFFLINE = 'offline', _('离线')
        ONLINE = 'online', _('在线')
        RECORDING = 'recording', _('录制中')
        STREAMING = 'streaming', _('直播中')
        UPLOADING = 'uploading', _('上传中')
        ERROR = 'error', _('异常')
    device_name = models.CharField(max_length=100, default='', verbose_name=_('设备名称'))
    device_sn = models.CharField(max_length=100, unique=True, default='', verbose_name=_('设备SN'))
    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.RECORDING_HOST,
        verbose_name=_('设备类型'),
    )
    manufacturer = models.CharField(max_length=100, blank=True, default='', verbose_name=_('厂商'))
    model = models.CharField(max_length=100, blank=True, default='', verbose_name=_('型号'))
    firmware_version = models.CharField(max_length=50, blank=True, default='', verbose_name=_('固件版本'))
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='devices',
        verbose_name=_('学校'),
    )
    location = models.CharField(max_length=200, blank=True, default='', verbose_name=_('安装位置'))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('IP地址'))
    mac_address = models.CharField(max_length=17, blank=True, default='', verbose_name=_('MAC地址'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OFFLINE, verbose_name=_('状态'))
    last_online_time = models.DateTimeField(null=True, blank=True, verbose_name=_('最后在线时间'))
    device_token = models.CharField(max_length=64, unique=True, blank=True, default='', verbose_name=_('设备令牌'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))

    class Meta:
        verbose_name=_('设备')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.device_name

    def save(self, *args, **kwargs):
        if not self.device_token:
            self.device_token = generate_device_token()
        super().save(*args, **kwargs)


class LiveSession(models.Model):
    class Status(models.TextChoices):
        CREATED = 'created', _('已创建')
        STARTING = 'starting', _('启动中')
        LIVE = 'live', _('直播中')
        STOPPED = 'stopped', _('已停止')
        ERROR = 'error', _('异常')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='live_sessions', null=True, blank=True, verbose_name=_('设备'))
    title = models.CharField(max_length=255, blank=True, default='', verbose_name=_('直播标题'))
    teacher = models.ForeignKey(
        'users.TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='live_sessions',
        verbose_name=_('教师'),
    )
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='live_sessions',
        verbose_name=_('学校'),
    )
    stream_key = models.CharField(max_length=128, unique=True, verbose_name=_('推流密钥'))
    rtmp_push_url = models.CharField(max_length=255, verbose_name=_('RTMP推流地址'))
    hls_url = models.CharField(max_length=255, blank=True, default='', verbose_name=_('HLS观看地址'))
    stream_token = models.CharField(max_length=64, blank=True, default='', verbose_name=_('一次性推流令牌'))
    token_used = models.BooleanField(default=False, verbose_name=_('令牌已使用'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED, verbose_name=_('状态'))
    created_time = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    start_time = models.DateTimeField(null=True, blank=True, verbose_name=_('开始时间'))
    end_time = models.DateTimeField(null=True, blank=True, verbose_name=_('结束时间'))

    class Meta:
        verbose_name=_('直播会话')
        verbose_name_plural = verbose_name

    def __str__(self):
        if self.device_id:
            return f'{self.device.device_name} - {self.stream_key}'
        return f'{self.title or self.stream_key}'