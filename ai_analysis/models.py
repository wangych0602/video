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
        (TYPE_TEACHING_ONLY, _('仅教学评价')),
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
    progress = models.PositiveIntegerField(
        default=0,
        verbose_name=_('进度')
    )
    current_step = models.CharField(
        max_length=100,
        blank=True,
        default='',
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
    started_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('开始时间')
    )
    finished_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('完成时间')
    )

    class Meta:
        verbose_name = _('课堂分析任务')
        verbose_name_plural = _('课堂分析任务')
        ordering = ['-created_time']

    def __str__(self):
        return f'{self.video.title} - {self.get_task_type_display()}'


class AIAnalysisResult(models.Model):
    # AI分析结果
    task = models.OneToOneField(
        ClassAnalysisTask,
        on_delete=models.CASCADE,
        related_name='result',
        verbose_name=_('分析任务')
    )
    
    # 视频信息
    video_info = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('视频信息')
    )
    
    # 关键帧
    key_frames = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('关键帧')
    )
    
    # 场景分析
    scene_analysis = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('场景分析')
    )
    
    # 教师动作分析
    teacher_actions = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('教师动作')
    )
    
    # PPT内容
    ppt_content = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('PPT内容')
    )
    
    # 黑板内容
    blackboard_content = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('黑板内容')
    )
    
    # 学生互动
    student_interaction = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('学生互动')
    )
    
    # 教室环境
    classroom_environment = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('教室环境')
    )
    
    # 语音分析 - 文字稿
    transcript = models.TextField(
        blank=True,
        default='',
        verbose_name=_('课堂文字稿')
    )
    
    # 语音分析 - 语音片段
    speech_segments = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('语音片段')
    )
    
    # 语音分析 - 语速
    speaking_rate = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('语速分析')
    )
    
    # 语音分析 - 关键词
    keywords = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('关键词')
    )
    
    # 语音分析 - 知识点
    knowledge_points = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('知识点')
    )
    
    # 教学评价 - 总分
    teaching_score = models.FloatField(
        default=0,
        verbose_name=_('教学评分')
    )
    
    # 教学评价 - 评价报告
    evaluation_report = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('评价报告')
    )
    
    # 教学评价 - 改进建议
    improvement_suggestions = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('改进建议')
    )
    
    # 教学评分（兼容旧字段）
    overall_score = models.FloatField(
        default=0,
        verbose_name=_('总分')
    )
    student_engagement_score = models.FloatField(
        default=0,
        verbose_name=_('学生参与度')
    )
    teacher_score = models.FloatField(
        default=0,
        verbose_name=_('教师评分')
    )
    
    # 总结
    summary = models.TextField(
        blank=True,
        default='',
        verbose_name=_('分析总结')
    )
    
    # 建议
    suggestions = models.TextField(
        blank=True,
        default='',
        verbose_name=_('改进建议')
    )
    
    # 报告URL
    report_url = models.URLField(
        max_length=500,
        blank=True,
        default='',
        verbose_name=_('报告链接')
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
        verbose_name = _('AI分析结果')
        verbose_name_plural = _('AI分析结果')
        ordering = ['-created_time']

    def __str__(self):
        return f'分析结果 - {self.task.id}'


class TeachingEvaluation(models.Model):
    # 教学评价
    task = models.OneToOneField(
        ClassAnalysisTask,
        on_delete=models.CASCADE,
        related_name='evaluation',
        verbose_name=_('分析任务')
    )
    
    # 总体评分
    overall_score = models.FloatField(
        default=0,
        verbose_name=_('总分')
    )
    
    # 知识掌握度
    knowledge_score = models.FloatField(
        default=0,
        verbose_name=_('知识掌握度')
    )
    
    # 互动参与度
    interaction_score = models.FloatField(
        default=0,
        verbose_name=_('互动参与度')
    )
    
    # 表达清晰度
    expression_score = models.FloatField(
        default=0,
        verbose_name=_('表达清晰度')
    )
    
    # 课堂管理
    classroom_management_score = models.FloatField(
        default=0,
        verbose_name=_('课堂管理')
    )
    
    # 教学结构
    teaching_structure_score = models.FloatField(
        default=0,
        verbose_name=_('教学结构')
    )
    
    # 等级
    grade = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name=_('等级')
    )
    
    # 优势
    strengths = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('优势')
    )
    
    # 不足
    weaknesses = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('不足')
    )
    
    # 建议
    suggestions = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('建议')
    )
    
    # 评价方式
    evaluation_method = models.CharField(
        max_length=20,
        default='rule_based',
        verbose_name=_('评价方式')
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
        verbose_name = _('教学评价')
        verbose_name_plural = _('教学评价')
        ordering = ['-created_time']

    def __str__(self):
        return f'教学评价 - {self.task.id} - {self.grade}'


class AIReport(models.Model):
    # AI分析报告
    task = models.OneToOneField(
        ClassAnalysisTask,
        on_delete=models.CASCADE,
        related_name='report',
        verbose_name=_('分析任务')
    )
    
    # 报告标题
    title = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name=_('报告标题')
    )
    
    # 课堂总结
    summary = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('课堂总结')
    )
    
    # 教师报告
    teacher_report = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('教师报告')
    )
    
    # 学校报告
    school_report = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('学校报告')
    )
    
    # PDF文件
    pdf_file = models.FileField(
        upload_to='reports/',
        null=True,
        blank=True,
        verbose_name=_('PDF文件')
    )
    
    # HTML内容
    html_content = models.TextField(
        blank=True,
        default='',
        verbose_name=_('HTML内容')
    )
    
    # 下载次数
    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('下载次数')
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
        verbose_name = _('分析报告')
        verbose_name_plural = _('分析报告')
        ordering = ['-created_time']

    def __str__(self):
        return f'分析报告 - {self.task.id} - {self.title}'


class AIModelConfig(models.Model):
    # AI模型配置
    PROVIDER_OPENAI = 'openai'
    PROVIDER_GEMINI = 'gemini'
    PROVIDER_CLAUDE = 'claude'
    PROVIDER_DEEPSEEK = 'deepseek'
    PROVIDER_QIANFAN = 'qianfan'
    PROVIDER_DASHSCOPE = 'dashscope'
    PROVIDER_OPENAI_WHISPER = 'openai_whisper'
    PROVIDER_GEMINI_SPEECH = 'gemini_speech'
    PROVIDER_AZURE_SPEECH = 'azure_speech'
    PROVIDER_LOCAL_WHISPER = 'local_whisper'
    
    PROVIDER_CHOICES = [
        (PROVIDER_OPENAI, 'OpenAI'),
        (PROVIDER_GEMINI, 'Gemini'),
        (PROVIDER_CLAUDE, 'Claude'),
        (PROVIDER_DEEPSEEK, 'DeepSeek'),
        (PROVIDER_QIANFAN, '百度千帆'),
        (PROVIDER_DASHSCOPE, '阿里百炼'),
        (PROVIDER_OPENAI_WHISPER, 'OpenAI Whisper'),
        (PROVIDER_GEMINI_SPEECH, 'Gemini Speech'),
        (PROVIDER_AZURE_SPEECH, 'Azure Speech'),
        (PROVIDER_LOCAL_WHISPER, '本地Whisper'),
    ]
    
    provider = models.CharField(
        max_length=30,
        choices=PROVIDER_CHOICES,
        default=PROVIDER_OPENAI,
        verbose_name=_('AI服务商')
    )
    model_name = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name=_('模型名称')
    )
    api_key = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name=_('API密钥')
    )
    api_base = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name=_('API地址')
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_('是否启用')
    )
    priority = models.PositiveIntegerField(
        default=0,
        verbose_name=_('优先级')
    )
    max_tokens = models.PositiveIntegerField(
        default=4096,
        verbose_name=_('最大Token数')
    )
    temperature = models.FloatField(
        default=0.7,
        verbose_name=_('温度')
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
        ordering = ['priority', '-created_time']

    def __str__(self):
        return f'{self.get_provider_display()} - {self.model_name}'