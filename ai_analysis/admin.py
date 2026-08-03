from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import ClassAnalysisTask, AIAnalysisResult, AIModelConfig


@admin.register(ClassAnalysisTask)
class ClassAnalysisTaskAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'video_title',
        'teacher',
        'task_type_display',
        'status_colored',
        'progress_bar',
        'created_time',
        'finished_time',
    ]
    list_filter = ['status', 'task_type', 'created_time', 'teacher']
    search_fields = ['video__title', 'teacher__username', 'error_message']
    date_hierarchy = 'created_time'
    readonly_fields = [
        'status',
        'progress',
        'error_message',
        'created_time',
        'finished_time',
    ]
    ordering = ['-created_time']
    
    def video_title(self, obj):
        return obj.video.title
    video_title.short_description = _('视频')
    
    def task_type_display(self, obj):
        return obj.get_task_type_display()
    task_type_display.short_description = _('任务类型')
    
    def status_colored(self, obj):
        colors = {
            ClassAnalysisTask.STATUS_PENDING: '#909399',
            ClassAnalysisTask.STATUS_PROCESSING: '#409eff',
            ClassAnalysisTask.STATUS_COMPLETED: '#67c23a',
            ClassAnalysisTask.STATUS_FAILED: '#f56c6c',
        }
        color = colors.get(obj.status, '#909399')
        return format_html(
            '<span style=\"color: {}\">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = _('状态')
    
    def progress_bar(self, obj):
        progress = obj.progress or 0
        color = '#67c23a' if progress >= 100 else '#409eff'
        return format_html(
            '<div style=\"width: 100px; background: #ebeef5; border-radius: 10px; height: 20px; position: relative;\">'
            '<div style=\"width: {}%; background: {}; height: 100%; border-radius: 10px;\"></div>'
            '<span style=\"position: absolute; left: 0; right: 0; top: 0; bottom: 0; '
            'text-align: center; line-height: 20px; font-size: 12px; color: #303133;\">{}%</span>'
            '</div>',
            progress, color, progress
        )
    progress_bar.short_description = _('进度')


@admin.register(AIAnalysisResult)
class AIAnalysisResultAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'task_video',
        'teaching_score',
        'student_engagement_score',
        'teacher_score',
        'created_time',
    ]
    list_filter = ['created_time']
    search_fields = ['task__video__title', 'summary', 'suggestions']
    date_hierarchy = 'created_time'
    readonly_fields = [
        'task',
        'summary',
        'keywords',
        'knowledge_points',
        'teaching_score',
        'student_engagement_score',
        'teacher_score',
        'suggestions',
        'report_url',
        'created_time',
    ]
    ordering = ['-created_time']
    
    def task_video(self, obj):
        return obj.task.video.title
    task_video.short_description = _('视频')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AIModelConfig)
class AIModelConfigAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'provider_display',
        'model_name',
        'status_colored',
        'priority',
        'created_time',
    ]
    list_filter = ['provider', 'status', 'created_time']
    search_fields = ['model_name', 'endpoint']
    ordering = ['-priority', '-created_time']
    
    def provider_display(self, obj):
        return obj.get_provider_display()
    provider_display.short_description = _('提供商')
    
    def status_colored(self, obj):
        if obj.status:
            return format_html(
                '<span style=\"color: #67c23a\">{}</span>',
                _('启用')
            )
        return format_html(
            '<span style=\"color: #909399\">{}</span>',
            _('禁用')
        )
    status_colored.short_description = _('状态')
    
    fieldsets = (
        (_('基本信息'), {
            'fields': ('provider', 'model_name', 'status', 'priority'),
        }),
        (_('API配置'), {
            'fields': ('api_key', 'endpoint'),
            'classes': ('collapse',),
        }),
        (_('时间信息'), {
            'fields': ('created_time', 'updated_time'),
            'classes': ('collapse',),
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['created_time', 'updated_time']
        return ['created_time', 'updated_time']