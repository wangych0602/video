from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class ClassAnalysisTask(models.Model):
    # 课堂分析任务
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
    
    TYPE_FULL_ANALYSIS = 'full'
    TYPE_VIDEO_ONLY = 'video'
    TYPE_SPEECH_ONLY = 'speech'
    TYPE_TEACHING_ONLY = 'teaching'
    
    TYPE_CHOICES = [
        (TYPE_FULL_ANALYSIS, _('完整分析')),
        (TYPE_VIDEO_ONLY, _('仅视频分析')),
        (TYPE_SPEECH_ONLY, _('仅语音分析')),
        (TYPE_TEACHING_ONLY, _('仅教学评估')),
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
        verbose_name=_('学校')
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
    current_step = models.CharField(
        max_length=100,
        default='',
        blank=True,
        verbose_name=_('当前步骤')
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
    # AI分析结果
    task = models.OneToOneField(
        ClassAnalysisTask,
        on_delete=models.CASCADE,
        related_name='result',
        verbose_name=_('分析任务')
    )
    
    # 基础信息
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
    
    # 评分
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
    
    # 建议
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
    
    # 视频分析结果
    scene_analysis = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('场景分析')
    )
    teacher_actions = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('教师动作')
    )
    ppt_content = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('PPT内容')
    )
    blackboard_content = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('黑板内容')
    )
    student_interaction = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('学生互动')
    )
    classroom_environment = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('教室环境')
    )
    
    # 视频信息
    video_info = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('视频信息')
    )
    key_frames = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('关键帧列表')
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
        return f'Analysis Result for Task {self.task_id}'


class AIModelConfig(models.Model):
    # AI模型配置
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