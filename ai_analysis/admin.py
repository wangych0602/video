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
        'current_step',
        'created_time',
        'finished_time',
    ]
    list_filter = [
        'status',
        'task_type',
        'created_time',
        'teacher',
    ]
    search_fields = [
        'video__title',
        'teacher__username',
        'error_message',
        'current_step',
    ]
    date_hierarchy = 'created_time'
    
    readonly_fields = [
        'status',
        'progress',
        'current_step',
        'error_message',
        'created_time',
        'finished_time',
        'video_title',
        'status_colored',
        'progress_bar',
        'task_type_display',
        'result_link',
    ]
    
    fieldsets = [
        (_('基本信息'), {
            'fields': ['video', 'video_title', 'teacher', 'school', 'task_type']
        }),
        (_('任务状态'), {
            'fields': ['status', 'status_colored', 'progress', 'progress_bar', 'current_step']
        }),
        (_('时间信息'), {
            'fields': ['created_time', 'finished_time']
        }),
        (_('错误信息'), {
            'fields': ['error_message']
        }),
        (_('分析结果'), {
            'fields': ['result_link']
        }),
    ]
    
    def video_title(self, obj):
        return obj.video.title if obj.video else '-'
    video_title.short_description = _('视频标题')
    
    def task_type_display(self, obj):
        return obj.get_task_type_display()
    task_type_display.short_description = _('任务类型')
    
    def status_colored(self, obj):
        status_colors = {
            'pending': '#9ca3af',
            'processing': '#3b82f6',
            'completed': '#10b981',
            'failed': '#ef4444',
        }
        color = status_colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = _('状态')
    
    def progress_bar(self, obj):
        progress = obj.progress or 0
        color = '#10b981' if progress >= 80 else '#3b82f6' if progress >= 30 else '#f59e0b'
        return format_html(
            '<div style="width: 120px; height: 20px; background: #e5e7eb; border-radius: 10px; overflow: hidden;">'
            '<div style="width: {}%; height: 100%; background: {}; transition: width 0.3s;"></div>'
            '</div>'
            '<span style="margin-left: 8px; font-size: 12px; color: #6b7280;">{}%</span>',
            progress,
            color,
            progress
        )
    progress_bar.short_description = _('进度')
    
    def result_link(self, obj):
        if hasattr(obj, 'result') and obj.result:
            return format_html(
                '<a href="/admin/ai_analysis/aianalysisresult/{}/change/" class="button">查看分析结果</a>',
                obj.result.id
            )
        return _('暂无结果')
    result_link.short_description = _('分析结果')
    
    def has_add_permission(self, request):
        return False


@admin.register(AIAnalysisResult)
class AIAnalysisResultAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'task_video',
        'teaching_score',
        'student_engagement_score',
        'teacher_score',
        'key_frames_count',
        'created_time',
    ]
    list_filter = [
        'created_time',
    ]
    search_fields = [
        'task__video__title',
        'summary',
        'suggestions',
    ]
    date_hierarchy = 'created_time'
    
    readonly_fields = [
        'task',
        'summary',
        'keywords_display',
        'knowledge_points_display',
        'teaching_score',
        'student_engagement_score',
        'teacher_score',
        'suggestions',
        'report_url',
        'video_info_display',
        'key_frames_display',
        'scene_analysis_display',
        'teacher_actions_display',
        'ppt_content_display',
        'blackboard_content_display',
        'student_interaction_display',
        'classroom_environment_display',
        'created_time',
    ]
    
    fieldsets = [
        (_('基本信息'), {
            'fields': ['task', 'created_time']
        }),
        (_('评分信息'), {
            'fields': [
                'teaching_score',
                'student_engagement_score',
                'teacher_score',
            ]
        }),
        (_('总结与建议'), {
            'fields': ['summary', 'keywords_display', 'knowledge_points_display', 'suggestions']
        }),
        (_('视频信息'), {
            'fields': ['video_info_display', 'key_frames_display']
        }),
        (_('场景分析'), {
            'fields': ['scene_analysis_display']
        }),
        (_('教师动作'), {
            'fields': ['teacher_actions_display']
        }),
        (_('PPT内容'), {
            'fields': ['ppt_content_display']
        }),
        (_('黑板内容'), {
            'fields': ['blackboard_content_display']
        }),
        (_('学生互动'), {
            'fields': ['student_interaction_display']
        }),
        (_('教室环境'), {
            'fields': ['classroom_environment_display']
        }),
    ]
    
    def task_video(self, obj):
        return obj.task.video.title if obj.task and obj.task.video else '-'
    task_video.short_description = _('视频标题')
    
    def key_frames_count(self, obj):
        frames = obj.key_frames or []
        return len(frames)
    key_frames_count.short_description = _('关键帧数')
    
    def keywords_display(self, obj):
        keywords = obj.keywords or []
        if not keywords:
            return '-'
        html = '<div style="display: flex; flex-wrap: wrap; gap: 6px;">'
        for kw in keywords[:20]:
            html += f'<span style="background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 12px; font-size: 12px;">{kw}</span>'
        html += '</div>'
        return format_html(html)
    keywords_display.short_description = _('关键词')
    
    def knowledge_points_display(self, obj):
        points = obj.knowledge_points or []
        if not points:
            return '-'
        html = '<ul style="margin: 0; padding-left: 20px;">'
        for point in points[:10]:
            html += f'<li style="margin-bottom: 4px;">{point}</li>'
        html += '</ul>'
        return format_html(html)
    knowledge_points_display.short_description = _('知识点')
    
    def video_info_display(self, obj):
        info = obj.video_info or {}
        if not info:
            return '-'
        html = '<div style="background: #f9fafb; padding: 12px; border-radius: 8px; font-family: monospace; font-size: 13px;">'
        for key, value in info.items():
            html += f'<div><strong>{key}:</strong> {value}</div>'
        html += '</div>'
        return format_html(html)
    video_info_display.short_description = _('视频信息')
    
    def key_frames_display(self, obj):
        frames = obj.key_frames or []
        if not frames:
            return _('暂无关键帧')
        
        html = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
        for frame in frames[:6]:
            url = frame.get('url', '')
            time_str = frame.get('time_str', '')
            if url:
                html += f'''
                <div style="text-align: center;">
                    <img src="{url}" style="width: 160px; height: 90px; object-fit: cover; border-radius: 6px; border: 1px solid #e5e7eb;">
                    <div style="font-size: 12px; color: #6b7280; margin-top: 4px;">{time_str}</div>
                </div>
                '''
            else:
                html += f'''
                <div style="text-align: center;">
                    <div style="width: 160px; height: 90px; background: #f3f4f6; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #9ca3af; font-size: 12px;">
                        无预览
                    </div>
                    <div style="font-size: 12px; color: #6b7280; margin-top: 4px;">{time_str}</div>
                </div>
                '''
        html += '</div>'
        if len(frames) > 6:
            html += f'<div style="margin-top: 8px; color: #6b7280; font-size: 12px;">共 {len(frames)} 帧，仅显示前 6 帧</div>'
        return format_html(html)
    key_frames_display.short_description = _('关键帧')
    
    def scene_analysis_display(self, obj):
        data = obj.scene_analysis or {}
        if not data:
            return '-'
        return self._format_json_display(data)
    scene_analysis_display.short_description = _('场景分析')
    
    def teacher_actions_display(self, obj):
        actions = obj.teacher_actions or []
        if not actions:
            return '-'
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background: #f3f4f6;"><th style="padding: 8px; text-align: left; border: 1px solid #e5e7eb;">时间</th><th style="padding: 8px; text-align: left; border: 1px solid #e5e7eb;">动作</th><th style="padding: 8px; text-align: left; border: 1px solid #e5e7eb;">位置</th><th style="padding: 8px; text-align: left; border: 1px solid #e5e7eb;">时长</th></tr>'
        for action in actions[:10]:
            html += f'''
            <tr>
                <td style="padding: 8px; border: 1px solid #e5e7eb;">{action.get('time_str', '')}</td>
                <td style="padding: 8px; border: 1px solid #e5e7eb;">{action.get('action', '')}</td>
                <td style="padding: 8px; border: 1px solid #e5e7eb;">{action.get('location', '')}</td>
                <td style="padding: 8px; border: 1px solid #e5e7eb;">{action.get('duration', '')}s</td>
            </tr>
            '''
        html += '</table>'
        return format_html(html)
    teacher_actions_display.short_description = _('教师动作')
    
    def ppt_content_display(self, obj):
        slides = obj.ppt_content or []
        if not slides:
            return '-'
        html = '<div style="display: flex; flex-direction: column; gap: 8px;">'
        for slide in slides[:5]:
            title = slide.get('title', '')
            content = slide.get('content', [])
            time_str = slide.get('timestamp', '')
            html += f'''
            <div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 10px; border-radius: 4px;">
                <div style="font-weight: bold; color: #166534;">第{slide.get('slide_number', '')}页: {title}</div>
                <div style="font-size: 12px; color: #6b7280; margin-bottom: 6px;">时间: {time_str}s</div>
                <ul style="margin: 0; padding-left: 20px; font-size: 13px;">
                    {''.join(f'<li>{c}</li>' for c in content)}
                </ul>
            </div>
            '''
        html += '</div>'
        return format_html(html)
    ppt_content_display.short_description = _('PPT内容')
    
    def blackboard_content_display(self, obj):
        contents = obj.blackboard_content or []
        if not contents:
            return '-'
        html = '<div style="display: flex; flex-direction: column; gap: 8px;">'
        for item in contents[:5]:
            html += f'''
            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 10px; border-radius: 4px;">
                <div style="font-weight: bold; color: #92400e;">{item.get('area', '')} - {item.get('type', '')}</div>
                <div style="font-size: 12px; color: #6b7280; margin-bottom: 6px;">时间: {item.get('time_str', '')}</div>
                <div style="font-size: 13px;">{item.get('content', '')}</div>
            </div>
            '''
        html += '</div>'
        return format_html(html)
    blackboard_content_display.short_description = _('黑板内容')
    
    def student_interaction_display(self, obj):
        data = obj.student_interaction or {}
        if not data:
            return '-'
        return self._format_json_display(data)
    student_interaction_display.short_description = _('学生互动')
    
    def classroom_environment_display(self, obj):
        data = obj.classroom_environment or {}
        if not data:
            return '-'
        return self._format_json_display(data)
    classroom_environment_display.short_description = _('教室环境')
    
    def _format_json_display(self, data):
        if isinstance(data, dict):
            html = '<div style="background: #f9fafb; padding: 12px; border-radius: 8px; font-family: monospace; font-size: 13px;">'
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    import json
                    value_str = json.dumps(value, ensure_ascii=False, indent=2)
                    html += f'<div><strong>{key}:</strong><pre style="margin: 4px 0; padding: 8px; background: #fff; border-radius: 4px; overflow-x: auto;">{value_str}</pre></div>'
                else:
                    html += f'<div><strong>{key}:</strong> {value}</div>'
            html += '</div>'
            return format_html(html)
        return str(data)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
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
    list_filter = [
        'provider',
        'status',
        'created_time',
    ]
    search_fields = [
        'model_name',
        'endpoint',
    ]
    ordering = ['-priority', '-created_time']
    
    fieldsets = [
        (_('基本配置'), {
            'fields': ['provider', 'model_name', 'api_key', 'endpoint']
        }),
        (_('状态设置'), {
            'fields': ['status', 'priority']
        }),
        (_('时间信息'), {
            'fields': ['created_time', 'updated_time']
        }),
    ]
    
    readonly_fields = ['created_time', 'updated_time']
    
    def provider_display(self, obj):
        provider_icons = {
            'openai': '🟢',
            'gemini': '🔵',
            'claude': '🟠',
            'local': '⚪',
        }
        icon = provider_icons.get(obj.provider, '⚪')
        return format_html('{} {}', icon, obj.get_provider_display())
    provider_display.short_description = _('提供商')
    
    def status_colored(self, obj):
        if obj.status:
            return format_html(
                '<span style="color: #10b981; font-weight: bold;">✓ {}</span>',
                _('启用')
            )
        return format_html(
            '<span style="color: #9ca3af;">○ {}</span>',
            _('禁用')
        )
    status_colored.short_description = _('状态')