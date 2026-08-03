from rest_framework import serializers
from .models import ClassAnalysisTask, AIAnalysisResult, AIModelConfig


class ClassAnalysisTaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    video_title = serializers.CharField(source='video.title', read_only=True)
    
    class Meta:
        model = ClassAnalysisTask
        fields = [
            'id',
            'video',
            'video_title',
            'teacher',
            'school',
            'task_type',
            'task_type_display',
            'status',
            'status_display',
            'progress',
            'current_step',
            'error_message',
            'created_time',
            'finished_time',
        ]
        read_only_fields = [
            'id',
            'status',
            'progress',
            'current_step',
            'error_message',
            'created_time',
            'finished_time',
        ]


class CreateAnalysisTaskSerializer(serializers.Serializer):
    video_id = serializers.IntegerField()
    task_type = serializers.CharField(default='full')
    
    def validate_task_type(self, value):
        valid_types = ['full', 'video', 'speech', 'teaching']
        if value not in valid_types:
            raise serializers.ValidationError(f'Invalid task type. Must be one of {valid_types}')
        return value


class AIAnalysisResultSerializer(serializers.ModelSerializer):
    task_id = serializers.IntegerField(source='task.id', read_only=True)
    video_title = serializers.CharField(source='task.video.title', read_only=True)
    
    class Meta:
        model = AIAnalysisResult
        fields = [
            'id',
            'task',
            'task_id',
            'video_title',
            # 基础信息
            'summary',
            'keywords',
            'knowledge_points',
            # 评分
            'teaching_score',
            'student_engagement_score',
            'teacher_score',
            # 建议
            'suggestions',
            'report_url',
            # 视频分析结果
            'video_info',
            'key_frames',
            'scene_analysis',
            'teacher_actions',
            'ppt_content',
            'blackboard_content',
            'student_interaction',
            'classroom_environment',
            # 时间
            'created_time',
        ]
        read_only_fields = fields


class AIModelConfigSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    
    class Meta:
        model = AIModelConfig
        fields = [
            'id',
            'provider',
            'provider_display',
            'model_name',
            'api_key',
            'endpoint',
            'status',
            'priority',
            'created_time',
            'updated_time',
        ]
        read_only_fields = ['id', 'created_time', 'updated_time']
    
    def to_representation(self, instance):
        # API key 脱敏，只显示前后4位
        data = super().to_representation(instance)
        if data.get('api_key') and len(data['api_key']) > 8:
            data['api_key'] = data['api_key'][:4] + '****' + data['api_key'][-4:]
        return data