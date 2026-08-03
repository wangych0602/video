from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class VideoCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('分类名称'))
    description = models.TextField(blank=True, verbose_name=_('描述'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))

    class Meta:
        verbose_name=_('视频分类')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Video(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('草稿')
        PENDING = 'pending', _('待审核')
        APPROVED = 'approved', _('已审核')
        PUBLISHED = 'published', _('已发布')
        REJECTED = 'rejected', _('已拒绝')
    title = models.CharField(max_length=255, verbose_name=_('标题'))
    description = models.TextField(blank=True, verbose_name=_('描述'))
    teacher = models.ForeignKey(
        'users.TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos',
        verbose_name=_('教师'),
    )
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos',
        verbose_name=_('学校'),
    )
    category = models.ForeignKey(
        VideoCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos',
        verbose_name=_('分类'),
    )
    file = models.FileField(
        upload_to='videos/',
        validators=[FileExtensionValidator(['mp4', 'mkv', 'mov'])],
        null=True,
        blank=True,
        verbose_name=_('视频文件'),
    )
    cover_image = models.ImageField(upload_to='covers/', blank=True, verbose_name=_('封面图'))
    duration = models.DurationField(null=True, blank=True, verbose_name=_('视频时长'))
    file_size = models.PositiveBigIntegerField(default=0, verbose_name=_('文件大小'))
    resolution = models.CharField(max_length=20, blank=True, default='', verbose_name=_('分辨率'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name=_('状态'))
    view_count = models.PositiveIntegerField(default=0, verbose_name=_('点击次数'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))

    class Meta:
        verbose_name=_('视频')
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class VideoAlbum(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('专辑名称'))
    teacher = models.ForeignKey(
        'users.TeacherProfile',
        on_delete=models.CASCADE,
        related_name='albums',
        verbose_name=_('教师'),
    )
    description = models.TextField(blank=True, verbose_name=_('专辑简介'))
    cover_image = models.ImageField(upload_to='album_covers/', blank=True, verbose_name=_('专辑封面'))
    view_count = models.PositiveIntegerField(default=0, verbose_name=_('点击次数'))
    videos = models.ManyToManyField('videos.Video', related_name='albums', blank=True, verbose_name=_('视频'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))

    class Meta:
        verbose_name=_('视频专辑')
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ReviewLog(models.Model):
    class Action(models.TextChoices):
        APPROVED = 'approved', _('通过')
        REJECTED = 'rejected', _('拒绝')
        PUBLISHED = 'published', _('已发布')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='review_logs', verbose_name=_('视频'))
    reviewer = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review_logs',
        verbose_name=_('审核人'),
    )
    action = models.CharField(max_length=20, choices=Action.choices, verbose_name=_('操作'))
    comment = models.TextField(blank=True, verbose_name=_('审核意见'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))

    class Meta:
        verbose_name=_('审核记录')
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.video.title} - {self.action}'
class VideoSetting(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False, verbose_name=_('设置ID'))
    banner_image = models.ImageField(upload_to='settings/', blank=True, null=True, verbose_name=_('首页横幅背景图'))
    default_cover = models.ImageField(upload_to='settings/', blank=True, null=True, verbose_name=_('全局默认视频封面'))
    site_name = models.CharField(max_length=100, blank=True, default='', verbose_name=_('平台名称'))
    footer_description = models.TextField(blank=True, default='', verbose_name=_('页脚简介'))
    footer_copyright = models.CharField(max_length=200, blank=True, default='', verbose_name=_('版权信息'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))

    class Meta:
        verbose_name=_('视频设置')
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        self.id = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return _('视频设置')