from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import ClassAnalysisTask, AIAnalysisResult, AIModelConfig, TeachingEvaluation


@admin.register(ClassAnalysisTask)
class ClassAnalysisTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'video', 'task_type', 'status', 'progress', 'current_step', 'created_time', 'finished_time']
    list_filter = ['status', 'task_type', 'created_time']
    search_fields = ['video__title', 'current_step']
    readonly_fields = ['created_time', 'started_time', 'finished_time']
    ordering = ['-created_time']
    
    fieldsets = [
        (_('基本信息'), {'fields': ['video', 'teacher', 'school', 'task_type']}),
        (_('状态'), {'fields': ['status', 'progress', 'current_step', 'error_message']}),
        (_('时间'), {'fields': ['created_time', 'started_time', 'finished_time']}),
    ]


@admin.register(AIAnalysisResult)
class AIAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'teaching_score_display', 'grade_display', 'created_time']
    list_filter = ['created_time']
    search_fields = ['task__video__title', 'transcript']
    readonly_fields = ['created_time', 'updated_time']
    ordering = ['-created_time']
    
    def teaching_score_display(self, obj):
        score = obj.teaching_score or obj.overall_score
        color = '#67c23a' if score >= 80 else '#e6a23c' if score >= 60 else '#f56c6c'
        return format_html('<span style="color: {}; font-weight: bold; font-size: 16px;">{}</span>', color, score)
    teaching_score_display.short_description = _('教学评分')
    
    def grade_display(self, obj):
        report = obj.evaluation_report
        grade = report.get('grade', '') if isinstance(report, dict) else ''
        if not grade:
            return '-'
        color_map = {
            '优秀': '#67c23a',
            '良好': '#409eff',
            '中等': '#e6a23c',
            '及格': '#909399',
            '待提高': '#f56c6c',
        }
        color = color_map.get(grade, '#606266')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, grade)
    grade_display.short_description = _('等级')
    
    fieldsets = [
        (_('任务关联'), {'fields': ['task']}),
        (_('教学评价'), {'fields': ['teaching_score', 'evaluation_report', 'improvement_suggestions']}),
        (_('视频分析'), {'fields': ['video_info', 'key_frames', 'scene_analysis', 'teacher_actions', 'ppt_content', 'blackboard_content', 'student_interaction', 'classroom_environment']}),
        (_('语音分析'), {'fields': ['transcript', 'speech_segments', 'speaking_rate', 'keywords', 'knowledge_points']}),
        (_('总结'), {'fields': ['overall_score', 'student_engagement_score', 'teacher_score', 'summary', 'suggestions', 'report_url']}),
        (_('时间'), {'fields': ['created_time', 'updated_time']}),
    ]


@admin.register(TeachingEvaluation)
class TeachingEvaluationAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'overall_score_display', 'grade_display', 'evaluation_method', 'created_time']
    list_filter = ['grade', 'evaluation_method', 'created_time']
    search_fields = ['task__video__title']
    readonly_fields = ['created_time', 'updated_time']
    ordering = ['-created_time']
    
    def overall_score_display(self, obj):
        score = obj.overall_score
        color = '#67c23a' if score >= 80 else '#e6a23c' if score >= 60 else '#f56c6c'
        return format_html('<span style="color: {}; font-weight: bold; font-size: 18px;">{}</span>', color, score)
    overall_score_display.short_description = _('总分')
    
    def grade_display(self, obj):
        grade = obj.grade
        if not grade:
            return '-'
        color_map = {
            '优秀': '#67c23a',
            '良好': '#409eff',
            '中等': '#e6a23c',
            '及格': '#909399',
            '待提高': '#f56c6c',
        }
        color = color_map.get(grade, '#606266')
        return format_html('<span style="color: {}; font-weight: bold; font-size: 16px;">{}</span>', color, grade)
    grade_display.short_description = _('等级')
    
    fieldsets = [
        (_('任务关联'), {'fields': ['task']}),
        (_('评分概览'), {'fields': ['overall_score', 'grade', 'evaluation_method']}),
        (_('各维度评分'), {'fields': ['knowledge_score', 'interaction_score', 'expression_score', 'classroom_management_score', 'teaching_structure_score']}),
        (_('评价内容'), {'fields': ['strengths', 'weaknesses', 'suggestions']}),
        (_('时间'), {'fields': ['created_time', 'updated_time']}),
    ]
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj:
            extra_context['evaluation_data'] = {
                'overall_score': obj.overall_score,
                'knowledge_score': obj.knowledge_score,
                'interaction_score': obj.interaction_score,
                'expression_score': obj.expression_score,
                'classroom_management_score': obj.classroom_management_score,
                'teaching_structure_score': obj.teaching_structure_score,
                'grade': obj.grade,
                'strengths': obj.strengths,
                'weaknesses': obj.weaknesses,
                'suggestions': obj.suggestions,
                'evaluation_method': obj.evaluation_method,
            }
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(AIModelConfig)
class AIModelConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'provider', 'model_name', 'is_active', 'priority', 'created_time']
    list_filter = ['provider', 'is_active', 'created_time']
    search_fields = ['model_name', 'api_base']
    readonly_fields = ['created_time', 'updated_time']
    ordering = ['priority', '-created_time']
    
    fieldsets = [
        (_('基本信息'), {'fields': ['provider', 'model_name', 'is_active', 'priority']}),
        (_('API配置'), {'fields': ['api_key', 'api_base']}),
        (_('参数配置'), {'fields': ['max_tokens', 'temperature']}),
        (_('时间'), {'fields': ['created_time', 'updated_time']}),
    ]
    
    def save_model(self, request, obj, form, change):
        # 如果设置为启用，禁用其他启用的配置
        if obj.is_active:
            AIModelConfig.objects.filter(is_active=True).exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)