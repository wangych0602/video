from rest_framework import serializers
from .models import ClassAnalysisTask, AIAnalysisResult, AIModelConfig


class ClassAnalysisTaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    video_title = serializers.CharField(source='video.title', read_only=True)
    teacher_name = serializers.CharField(source='teacher.username', read_only=True, allow_null=True)
    school_name = serializers.CharField(source='school.name', read_only=True, allow_null=True)
    
    class Meta:
        model = ClassAnalysisTask
        fields = [
            'id',
            'video',
            'video_title',
            'teacher',
            'teacher_name',
            'school',
            'school_name',
            'task_type',
            'task_type_display',
            'status',
            'status_display',
            'progress',
            'error_message',
            'created_time',
            'finished_time',
        ]
        read_only_fields = [
            'id',
            'status',
            'progress',
            'error_message',
            'created_time',
            'finished_time',
        ]


class CreateAnalysisTaskSerializer(serializers.Serializer):
    video_id = serializers.IntegerField()
    task_type = serializers.ChoiceField(
        choices=ClassAnalysisTask.TYPE_CHOICES,
        default=ClassAnalysisTask.TYPE_FULL_ANALYSIS
    )
    
    def validate_video_id(self, value):
        from videos.models import Video
        if not Video.objects.filter(id=value).exists():
            raise serializers.ValidationError('Video not found')
        return value


class AIAnalysisResultSerializer(serializers.ModelSerializer):
    task_info = ClassAnalysisTaskSerializer(source='task', read_only=True)
    
    class Meta:
        model = AIAnalysisResult
        fields = [
            'id',
            'task',
            'task_info',
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
        read_only_fields = ['id', 'created_time']


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
        # 隐藏 api_key 的部分内容
        data = super().to_representation(instance)
        if data.get('api_key'):
            key = data['api_key']
            if len(key) > 8:
                data['api_key'] = key[:4] + '****' + key[-4:]
            else:
                data['api_key'] = '****'
        return data