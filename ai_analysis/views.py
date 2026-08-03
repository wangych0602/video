from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404

from .models import ClassAnalysisTask, AIAnalysisResult, AIModelConfig
from .serializers import (
    ClassAnalysisTaskSerializer,
    CreateAnalysisTaskSerializer,
    AIAnalysisResultSerializer,
    AIModelConfigSerializer,
)
from .tasks import run_analysis_task, run_analysis_task_sync, HAS_CELERY


class ClassAnalysisTaskViewSet(viewsets.ModelViewSet):
    queryset = ClassAnalysisTask.objects.all()
    serializer_class = ClassAnalysisTaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # 普通用户只能看到自己的任务
        if not user.is_staff:
            queryset = queryset.filter(teacher=user)
        
        return queryset.order_by('-created_time')
    
    @action(detail=False, methods=['post'], url_path='create')
    def create_task(self, request):
        # 创建分析任务
        serializer = CreateAnalysisTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        video_id = serializer.validated_data['video_id']
        task_type = serializer.validated_data['task_type']
        
        from videos.models import Video
        video = Video.objects.get(id=video_id)
        
        # 创建任务
        task = ClassAnalysisTask.objects.create(
            video=video,
            teacher=request.user,
            school=video.school if hasattr(video, 'school') else None,
            task_type=task_type,
            status=ClassAnalysisTask.STATUS_PENDING,
        )
        
        # 执行任务
        if HAS_CELERY:
            try:
                run_analysis_task.delay(task.id)
            except Exception:
                # Celery 调用失败时同步执行
                run_analysis_task_sync(task.id)
        else:
            # 没有 Celery 时同步执行
            run_analysis_task_sync(task.id)
        
        return Response(
            ClassAnalysisTaskSerializer(task).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'], url_path='result')
    def get_result(self, request, pk=None):
        # 获取任务结果
        task = self.get_object()
        
        try:
            result = task.result
            serializer = AIAnalysisResultSerializer(result)
            return Response(serializer.data)
        except AIAnalysisResult.DoesNotExist:
            return Response(
                {'detail': 'Analysis result not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], url_path='retry')
    def retry_task(self, request, pk=None):
        # 重试任务
        task = self.get_object()
        
        # 重置任务状态
        task.status = ClassAnalysisTask.STATUS_PENDING
        task.progress = 0
        task.error_message = ''
        task.finished_time = None
        task.save()
        
        # 删除旧结果
        if hasattr(task, 'result'):
            task.result.delete()
        
        # 重新执行
        if HAS_CELERY:
            try:
                run_analysis_task.delay(task.id)
            except Exception:
                run_analysis_task_sync(task.id)
        else:
            run_analysis_task_sync(task.id)
        
        return Response(ClassAnalysisTaskSerializer(task).data)


class AIAnalysisResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AIAnalysisResult.objects.all()
    serializer_class = AIAnalysisResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_staff:
            queryset = queryset.filter(task__teacher=user)
        
        return queryset.order_by('-created_time')


class AIModelConfigViewSet(viewsets.ModelViewSet):
    queryset = AIModelConfig.objects.all()
    serializer_class = AIModelConfigSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return super().get_queryset().order_by('-priority', '-created_time')
    
    @action(detail=False, methods=['post'], url_path='set-active')
    def set_active(self, request):
        # 设置启用的模型
        config_id = request.data.get('id')
        if not config_id:
            return Response(
                {'detail': 'Config id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        config = get_object_or_404(AIModelConfig, id=config_id)
        
        # 禁用其他所有配置
        AIModelConfig.objects.update(status=False)
        
        # 启用当前配置
        config.status = True
        config.save()
        
        return Response(AIModelConfigSerializer(config).data)
    
    @action(detail=False, methods=['get'], url_path='active')
    def get_active(self, request):
        # 获取当前启用的模型配置
        active_config = AIModelConfig.objects.filter(status=True).first()
        if active_config:
            return Response(AIModelConfigSerializer(active_config).data)
        return Response(
            {'detail': 'No active model config found'},
            status=status.HTTP_404_NOT_FOUND
        )