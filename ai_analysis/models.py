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
    model_config = models.ForeignKey(
        'AIModelConfig',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analysis_tasks',
        help_text=_('指定使用的模型配置，为空则自动选择'),
        verbose_name=_('模型配置')
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
    
    # Provider 类型
    PROVIDER_OPENAI = 'openai'
    PROVIDER_GEMINI = 'gemini'
    PROVIDER_CLAUDE = 'claude'
    PROVIDER_QWEN = 'qwen'
    PROVIDER_DEEPSEEK = 'deepseek'
    PROVIDER_GLM = 'glm'
    PROVIDER_OLLAMA = 'ollama'
    
    PROVIDER_CHOICES = [
        (PROVIDER_OPENAI, 'OpenAI'),
        (PROVIDER_GEMINI, 'Google Gemini'),
        (PROVIDER_CLAUDE, 'Anthropic Claude'),
        (PROVIDER_QWEN, '阿里通义千问'),
        (PROVIDER_DEEPSEEK, 'DeepSeek'),
        (PROVIDER_GLM, '智谱 GLM'),
        (PROVIDER_OLLAMA, 'Ollama 本地模型'),
    ]
    
    # 模型类型（用途）
    MODEL_TYPE_CHAT = 'chat'
    MODEL_TYPE_VISION = 'vision'
    MODEL_TYPE_SPEECH = 'speech_to_text'
    MODEL_TYPE_EMBEDDING = 'embedding'
    MODEL_TYPE_MULTIMODAL = 'multimodal'
    
    MODEL_TYPE_CHOICES = [
        (MODEL_TYPE_CHAT, '文本对话'),
        (MODEL_TYPE_VISION, '视觉分析'),
        (MODEL_TYPE_SPEECH, '语音识别'),
        (MODEL_TYPE_EMBEDDING, '向量嵌入'),
        (MODEL_TYPE_MULTIMODAL, '多模态'),
    ]
    # 部署类型
    DEPLOYMENT_CLOUD = 'cloud'
    DEPLOYMENT_PRIVATE = 'private'
    DEPLOYMENT_LOCAL = 'local'
    DEPLOYMENT_HYBRID = 'hybrid'

    DEPLOYMENT_CHOICES = [
        (DEPLOYMENT_CLOUD, '云服务'),
        (DEPLOYMENT_PRIVATE, '私有部署'),
        (DEPLOYMENT_LOCAL, '本地模型'),
        (DEPLOYMENT_HYBRID, '混合部署'),
    ]

    provider = models.CharField(
        max_length=30,
        choices=PROVIDER_CHOICES,
        default=PROVIDER_OPENAI,
        verbose_name=_('AI服务商')
    )
    
    model_type = models.CharField(
        max_length=30,
        choices=MODEL_TYPE_CHOICES,
        default=MODEL_TYPE_CHAT,
        verbose_name=_('模型类型')
    )
    
    model_name = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name=_('模型名称')
    )
    deployment_type = models.CharField(
        max_length=20,
        choices=DEPLOYMENT_CHOICES,
        default=DEPLOYMENT_CLOUD,
        verbose_name=_('部署类型')
    )
    
    api_key = models.CharField(
        max_length=500,
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
    api_endpoint = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name=_('私有部署端点')
    )
    
    status = models.BooleanField(
        default=False,
        verbose_name=_('状态')
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
    
    timeout = models.PositiveIntegerField(
        default=60,
        verbose_name=_('超时时间(秒)')
    )
    
    capabilities = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('能力配置')
    )
    # 健康状态
    HEALTH_STATUS_ACTIVE = 'active'
    HEALTH_STATUS_DEGRADED = 'degraded'
    HEALTH_STATUS_OFFLINE = 'offline'
    
    HEALTH_STATUS_CHOICES = [
        (HEALTH_STATUS_ACTIVE, '正常'),
        (HEALTH_STATUS_DEGRADED, '降级'),
        (HEALTH_STATUS_OFFLINE, '离线'),
    ]
    
    health_status = models.CharField(
        max_length=20,
        choices=HEALTH_STATUS_CHOICES,
        default=HEALTH_STATUS_ACTIVE,
        verbose_name=_('健康状态')
    )
    
    last_health_check_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('最后检查时间')
    )
    
    last_error_message = models.TextField(
        blank=True,
        default='',
        verbose_name=_('最后错误信息')
    )

    description = models.TextField(
        blank=True,
        default='',
        verbose_name=_('描述')
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
        return f'{self.get_provider_display()} - {self.model_name} ({self.get_model_type_display()})'
    
    def get_capabilities(self):
        """获取模型能力配置
        优先使用数据库中配置的 capabilities，否则使用 Provider 默认能力
        """
        from ai_analysis.providers import ProviderFactory
        
        # 获取 Provider 默认能力
        default_caps = ProviderFactory.get_provider_capabilities(self.provider)
        
        # 如果数据库中有配置，合并覆盖默认值
        if self.capabilities and isinstance(self.capabilities, dict):
            default_caps.update(self.capabilities)
        
        return default_caps

    def get_effective_api_base(self):
        """获取有效的 API 地址
        私有部署优先使用 api_endpoint，否则使用 api_base
        """
        if self.deployment_type == self.DEPLOYMENT_PRIVATE and self.api_endpoint:
            return self.api_endpoint
        return self.api_base
    
    def test_connection(self):
        """测试连接"""
        from ai_analysis.providers import ProviderFactory
        try:
            provider = ProviderFactory.get_provider_from_config(self)
            return provider.health_check()
        except Exception as e:
            return False



class AIUsageLog(models.Model):
    """AI 使用日志"""
    
    # 任务类型
    TASK_VIDEO_ANALYSIS = 'video_analysis'
    TASK_SPEECH_ANALYSIS = 'speech_analysis'
    TASK_TEACHING_EVALUATION = 'teaching_evaluation'
    TASK_REPORT_GENERATION = 'report_generation'
    TASK_CHAT = 'chat'
    TASK_EMBEDDING = 'embedding'
    
    TASK_TYPE_CHOICES = [
        (TASK_VIDEO_ANALYSIS, '视频分析'),
        (TASK_SPEECH_ANALYSIS, '语音分析'),
        (TASK_TEACHING_EVALUATION, '教学评价'),
        (TASK_REPORT_GENERATION, '报告生成'),
        (TASK_CHAT, '对话'),
        (TASK_EMBEDDING, '向量嵌入'),
    ]
    
    # 状态
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_DEGRADED = 'degraded'
    
    STATUS_CHOICES = [
        (STATUS_SUCCESS, '成功'),
        (STATUS_FAILED, '失败'),
        (STATUS_DEGRADED, '降级'),
    ]
    
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_usage_logs',
        verbose_name=_('用户')
    )
    
    organization = models.ForeignKey(
        'schools.School',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_usage_logs',
        verbose_name=_('组织/学校')
    )
    
    task_id = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name=_('任务ID')
    )
    
    provider = models.CharField(
        max_length=30,
        blank=True,
        default='',
        verbose_name=_('AI服务商')
    )
    
    model_name = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name=_('模型名称')
    )
    
    task_type = models.CharField(
        max_length=30,
        choices=TASK_TYPE_CHOICES,
        default=TASK_CHAT,
        verbose_name=_('任务类型')
    )
    
    input_tokens = models.PositiveIntegerField(
        default=0,
        verbose_name=_('输入Token数')
    )
    
    output_tokens = models.PositiveIntegerField(
        default=0,
        verbose_name=_('输出Token数')
    )
    
    total_tokens = models.PositiveIntegerField(
        default=0,
        verbose_name=_('总Token数')
    )
    
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=0,
        verbose_name=_('预估成本')
    )
    
    currency = models.CharField(
        max_length=10,
        default='USD',
        verbose_name=_('货币单位')
    )
    
    request_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('请求时间')
    )
    
    response_time = models.FloatField(
        default=0,
        verbose_name=_('响应时间(秒)')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SUCCESS,
        verbose_name=_('状态')
    )
    
    error_message = models.TextField(
        blank=True,
        default='',
        verbose_name=_('错误信息')
    )
    
    model_config = models.ForeignKey(
        'AIModelConfig',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usage_logs',
        verbose_name=_('模型配置')
    )
    
    class Meta:
        verbose_name = _('AI使用日志')
        verbose_name_plural = _('AI使用日志')
        ordering = ['-request_time']
        indexes = [
            models.Index(fields=['provider', 'model_name']),
            models.Index(fields=['task_type']),
            models.Index(fields=['status']),
            models.Index(fields=['request_time']),
        ]
    
    def __str__(self):
        return f"{self.provider}/{self.model_name} - {self.task_type} - {self.total_tokens} tokens"
    
    def save(self, *args, **kwargs):
        # 自动计算总 token 数
        if not self.total_tokens:
            self.total_tokens = self.input_tokens + self.output_tokens
        super().save(*args, **kwargs)


class OrganizationAIConfig(models.Model):
    """组织级 AI 配置"""
    
    organization = models.OneToOneField(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='ai_config',
        verbose_name=_('组织/学校')
    )
    
    default_model = models.ForeignKey(
        'AIModelConfig',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_for_organizations',
        verbose_name=_('默认模型')
    )
    
    allowed_models = models.ManyToManyField(
        'AIModelConfig',
        blank=True,
        related_name='allowed_for_organizations',
        verbose_name=_('允许使用的模型')
    )
    
    monthly_token_limit = models.PositiveIntegerField(
        default=0,
        help_text=_('每月Token限制，0表示无限制'),
        verbose_name=_('每月Token限制')
    )
    
    monthly_cost_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('每月成本限制，0表示无限制'),
        verbose_name=_('每月成本限制')
    )
    
    is_enabled = models.BooleanField(
        default=True,
        verbose_name=_('是否启用')
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
        verbose_name = _('组织AI配置')
        verbose_name_plural = _('组织AI配置')
    
    def __str__(self):
        return f"{self.organization} - AI配置"
    
    def get_monthly_usage(self):
        """获取本月使用量"""
        from django.utils import timezone
        from django.db.models import Sum
        
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        usage = AIUsageLog.objects.filter(
            organization=self.organization,
            request_time__gte=month_start,
            status=AIUsageLog.STATUS_SUCCESS
        ).aggregate(
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('estimated_cost')
        )
        
        return {
            'total_tokens': usage['total_tokens'] or 0,
            'total_cost': usage['total_cost'] or 0,
        }
    
    def check_limit(self):
        """检查是否超出限制"""
        if self.monthly_token_limit == 0 and self.monthly_cost_limit == 0:
            return True, '无限制'
        
        usage = self.get_monthly_usage()
        
        if self.monthly_token_limit > 0 and usage['total_tokens'] >= self.monthly_token_limit:
            return False, '已超出本月Token限制'
        
        if self.monthly_cost_limit > 0 and usage['total_cost'] >= self.monthly_cost_limit:
            return False, '已超出本月成本限制'
        
        return True, '正常'
