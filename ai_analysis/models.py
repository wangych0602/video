from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ClassAnalysisTask(models.Model):
    # 任务状态
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, _('等待中')),
        (STATUS_PROCESSING, _('处理中')),
        (STATUS_COMPLETED, _('已完成')),
        (STATUS_FAILED, _('失败')),
    ]
    
    # 任务类型
    TYPE_FULL_ANALYSIS = 'full'
    TYPE_VIDEO_ONLY = 'video'
    TYPE_SPEECH_ONLY = 'speech'
    TYPE_TEACHING_EVAL = 'teaching'
    
    TYPE_CHOICES = [
        (TYPE_FULL_ANALYSIS, _('完整分析')),
        (TYPE_VIDEO_ONLY, _('仅视频分析')),
        (TYPE_SPEECH_ONLY, _('仅语音分析')),
        (TYPE_TEACHING_EVAL, _('教学评估')),
    ]
    
    video = models.ForeignKey(
        'videos.Video',
        on_delete=models.CASCADE,
        related_name='analysis_tasks',
        verbose_name=_('视频')
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analysis_tasks',
        verbose_name=_('教师')
    )
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analysis_tasks',
        verbose_name=_('教室')
    )
    task_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_FULL_ANALYSIS,
        verbose_name=_('任务类型')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name=_('状态')
    )
    progress = models.IntegerField(
        default=0,
        verbose_name=_('进度')
    )
    error_message = models.TextField(
        blank=True,
        default='',
        verbose_name=_('错误信息')
    )
    created_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('创建时间')
    )
    finished_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('完成时间')
    )
    
    class Meta:
        verbose_name = _('AI分析任务')
        verbose_name_plural = _('AI分析任务')
        ordering = ['-created_time']
    
    def __str__(self):
        return f'{self.video.title} - {self.get_status_display()}'


class AIAnalysisResult(models.Model):
    task = models.OneToOneField(
        ClassAnalysisTask,
        on_delete=models.CASCADE,
        related_name='result',
        verbose_name=_('分析任务')
    )
    summary = models.TextField(
        blank=True,
        default='',
        verbose_name=_('课堂总结')
    )
    keywords = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('关键词')
    )
    knowledge_points = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('知识点')
    )
    teaching_score = models.FloatField(
        default=0,
        verbose_name=_('教学评分')
    )
    student_engagement_score = models.FloatField(
        default=0,
        verbose_name=_('学生参与度评分')
    )
    teacher_score = models.FloatField(
        default=0,
        verbose_name=_('教师综合评分')
    )
    suggestions = models.TextField(
        blank=True,
        default='',
        verbose_name=_('改进建议')
    )
    report_url = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name=_('报告URL')
    )
    created_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('创建时间')
    )
    
    class Meta:
        verbose_name = _('AI分析结果')
        verbose_name_plural = _('AI分析结果')
        ordering = ['-created_time']
    
    def __str__(self):
        return f'{self.task.video.title} - 分析结果'


class AIModelConfig(models.Model):
    # 模型提供商
    PROVIDER_OPENAI = 'openai'
    PROVIDER_GEMINI = 'gemini'
    PROVIDER_CLAUDE = 'claude'
    PROVIDER_LOCAL = 'local'
    
    PROVIDER_CHOICES = [
        (PROVIDER_OPENAI, 'OpenAI'),
        (PROVIDER_GEMINI, 'Gemini'),
        (PROVIDER_CLAUDE, 'Claude'),
        (PROVIDER_LOCAL, _('本地模型')),
    ]
    
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        default=PROVIDER_OPENAI,
        verbose_name=_('提供商')
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name=_('模型名称')
    )
    api_key = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name=_('API密钥')
    )
    endpoint = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name=_('API端点')
    )
    status = models.BooleanField(
        default=True,
        verbose_name=_('启用状态')
    )
    priority = models.IntegerField(
        default=0,
        verbose_name=_('优先级')
    )
    created_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('创建时间')
    )
    updated_time = models.DateTimeField(
        auto_now=True,
        verbose_name=_('更新时间')
    )
    
    class Meta:
        verbose_name = _('AI模型配置')
        verbose_name_plural = _('AI模型配置')
        ordering = ['-priority', '-created_time']
    
    def __str__(self):
        return f'{self.get_provider_display()} - {self.model_name}'