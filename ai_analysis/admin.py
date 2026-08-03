from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.utils.translation import gettext_lazy as _
from .models import ClassAnalysisTask, AIAnalysisResult, AIModelConfig, TeachingEvaluation, AIReport, AIUsageLog, OrganizationAIConfig


@admin.register(ClassAnalysisTask)
class ClassAnalysisTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'video', 'task_type', 'status', 'progress', 'current_step', 'teacher', 'created_time']
    list_filter = ['status', 'task_type', 'created_time']
    search_fields = ['video__title', 'teacher__username']
    readonly_fields = ['created_time', 'started_time', 'finished_time']
    list_per_page = 20
    
    fieldsets = (
        (_('基本信息'), {
            'fields': ('video', 'teacher', 'school', 'task_type')
        }),
        (_('状态信息'), {
            'fields': ('status', 'progress', 'current_step', 'error_message')
        }),
        (_('时间信息'), {
            'fields': ('created_time', 'started_time', 'finished_time')
        }),
    )


@admin.register(AIAnalysisResult)
class AIAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'teaching_score_display', 'overall_score', 'created_time']
    list_filter = ['created_time']
    search_fields = ['task__id', 'task__video__title']
    readonly_fields = ['created_time', 'updated_time']
    list_per_page = 20
    
    def teaching_score_display(self, obj):
        score = obj.teaching_score
        color = '#67c23a' if score >= 80 else '#e6a23c' if score >= 60 else '#f56c6c'
        return mark_safe(f'<span style="color: {color}; font-weight: bold;">{score}</span>')
    teaching_score_display.short_description = _('教学评分')


@admin.register(TeachingEvaluation)
class TeachingEvaluationAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'overall_score_display', 'grade_display', 'evaluation_method', 'created_time']
    list_filter = ['grade', 'evaluation_method', 'created_time']
    search_fields = ['task__id', 'task__video__title']
    readonly_fields = ['created_time', 'updated_time']
    list_per_page = 20
    
    def overall_score_display(self, obj):
        score = obj.overall_score
        color = '#67c23a' if score >= 80 else '#e6a23c' if score >= 60 else '#f56c6c'
        return mark_safe(f'<span style="color: {color}; font-weight: bold; font-size: 16px;">{score}</span>')
    overall_score_display.short_description = _('总分')
    
    def grade_display(self, obj):
        grade = obj.grade
        colors = {
            '优秀': '#67c23a',
            '良好': '#409eff',
            '中等': '#e6a23c',
            '及格': '#909399',
            '待提高': '#f56c6c',
        }
        color = colors.get(grade, '#909399')
        return mark_safe(f'<span style="color: {color}; font-weight: bold;">{grade}</span>')
    grade_display.short_description = _('等级')
    
    fieldsets = (
        (_('基本信息'), {
            'fields': ('task', 'evaluation_method')
        }),
        (_('总体评分'), {
            'fields': ('overall_score', 'grade')
        }),
        (_('各维度评分'), {
            'fields': ('knowledge_score', 'interaction_score', 'expression_score', 
                       'classroom_management_score', 'teaching_structure_score')
        }),
        (_('评价详情'), {
            'fields': ('strengths', 'weaknesses', 'suggestions')
        }),
        (_('时间信息'), {
            'fields': ('created_time', 'updated_time')
        }),
    )


@admin.register(AIReport)
class AIReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'title', 'has_pdf', 'download_count', 'created_time']
    list_filter = ['created_time']
    search_fields = ['task__id', 'title']
    readonly_fields = ['created_time', 'updated_time', 'download_count']
    list_per_page = 20
    
    def has_pdf(self, obj):
        if obj.pdf_file:
            return mark_safe(
                f'<a href="{obj.pdf_file.url}" target="_blank" style="color: #409eff;">📄 查看PDF</a>'
            )
        return mark_safe('<span style="color: #909399;">无PDF</span>')
    has_pdf.short_description = _('PDF文件')
    
    fieldsets = (
        (_('基本信息'), {
            'fields': ('task', 'title')
        }),
        (_('报告内容'), {
            'fields': ('summary', 'teacher_report', 'school_report', 'html_content')
        }),
        (_('文件信息'), {
            'fields': ('pdf_file', 'download_count')
        }),
        (_('时间信息'), {
            'fields': ('created_time', 'updated_time')
        }),
    )


@admin.register(AIModelConfig)
class AIModelConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'provider', 'model_name', 'is_active', 'priority', 'created_time']
    list_filter = ['provider', 'is_active', 'created_time']
    search_fields = ['model_name', 'api_key']
    readonly_fields = ['created_time', 'updated_time']
    list_per_page = 20
    
    fieldsets = (
        (_('基本配置'), {
            'fields': ('provider', 'model_name', 'is_active', 'priority')
        }),
        (_('API配置'), {
            'fields': ('api_key', 'api_base')
        }),
        (_('模型参数'), {
            'fields': ('max_tokens', 'temperature')
        }),
        (_('时间信息'), {
            'fields': ('created_time', 'updated_time')
        }),
    )


@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'provider', 'model_name', 'task_type', 'total_tokens', 
                    'estimated_cost', 'status', 'response_time', 'request_time']
    list_filter = ['provider', 'task_type', 'status', 'request_time']
    search_fields = ['provider', 'model_name', 'task_id', 'error_message']
    readonly_fields = ['request_time']
    date_hierarchy = 'request_time'


@admin.register(OrganizationAIConfig)
class OrganizationAIConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'organization', 'default_model', 'monthly_token_limit', 
                    'monthly_cost_limit', 'is_enabled', 'updated_time']
    list_filter = ['is_enabled']
    search_fields = ['organization__name']
    filter_horizontal = ['allowed_models']
    readonly_fields = ['created_time', 'updated_time']
