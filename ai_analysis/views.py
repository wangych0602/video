from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, FileResponse
from django.conf import settings
import os

from .models import ClassAnalysisTask, AIAnalysisResult, AIModelConfig, TeachingEvaluation, AIReport, AIUsageLog
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
            current_step='等待中',
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

    @action(detail=True, methods=['get'], url_path='progress')
    def get_progress(self, request, pk=None):
        # 获取任务进度
        task = self.get_object()

        return Response({
            'id': task.id,
            'status': task.status,
            'status_display': task.get_status_display(),
            'progress': task.progress,
            'current_step': task.current_step,
            'created_time': task.created_time,
            'finished_time': task.finished_time,
            'error_message': task.error_message,
        })

    @action(detail=True, methods=['get'], url_path='result')
    def get_result(self, request, pk=None):
        # 获取分析结果
        task = self.get_object()
        
        try:
            result = task.result
            return Response(AIAnalysisResultSerializer(result).data)
        except AIAnalysisResult.DoesNotExist:
            return Response(
                {'error': '结果不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'], url_path='transcript')
    def get_transcript(self, request, pk=None):
        # 获取课堂文字稿
        task = self.get_object()

        try:
            result = task.result
            return Response({
                'task_id': task.id,
                'transcript': result.transcript,
                'speech_segments': result.speech_segments,
                'speaking_rate': result.speaking_rate,
            })
        except AIAnalysisResult.DoesNotExist:
            return Response(
                {'error': '结果不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'], url_path='keywords')
    def get_keywords(self, request, pk=None):
        # 获取关键词和知识点
        task = self.get_object()

        try:
            result = task.result
            return Response({
                'task_id': task.id,
                'keywords': result.keywords,
                'knowledge_points': result.knowledge_points,
            })
        except AIAnalysisResult.DoesNotExist:
            return Response(
                {'error': '结果不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'], url_path='evaluation')
    def get_evaluation(self, request, pk=None):
        # 获取教学评价结果
        task = self.get_object()

        try:
            evaluation = task.evaluation
            return Response({
                'task_id': task.id,
                'overall_score': evaluation.overall_score,
                'knowledge_score': evaluation.knowledge_score,
                'interaction_score': evaluation.interaction_score,
                'expression_score': evaluation.expression_score,
                'classroom_management_score': evaluation.classroom_management_score,
                'teaching_structure_score': evaluation.teaching_structure_score,
                'grade': evaluation.grade,
                'strengths': evaluation.strengths,
                'weaknesses': evaluation.weaknesses,
                'suggestions': evaluation.suggestions,
                'evaluation_method': evaluation.evaluation_method,
            })
        except TeachingEvaluation.DoesNotExist:
            # 尝试从 AIAnalysisResult 中获取
            try:
                result = task.result
                return Response({
                    'task_id': task.id,
                    'overall_score': result.teaching_score,
                    'evaluation_report': result.evaluation_report,
                    'improvement_suggestions': result.improvement_suggestions,
                })
            except AIAnalysisResult.DoesNotExist:
                return Response(
                    {'error': '评价结果不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )

    @action(detail=True, methods=['get'], url_path='score')
    def get_score(self, request, pk=None):
        # 获取评分数据
        task = self.get_object()

        try:
            evaluation = task.evaluation
            return Response({
                'task_id': task.id,
                'scores': {
                    'overall': evaluation.overall_score,
                    'knowledge': evaluation.knowledge_score,
                    'interaction': evaluation.interaction_score,
                    'expression': evaluation.expression_score,
                    'classroom_management': evaluation.classroom_management_score,
                    'teaching_structure': evaluation.teaching_structure_score,
                },
                'grade': evaluation.grade,
                'weights': {
                    'knowledge': 0.25,
                    'interaction': 0.20,
                    'expression': 0.20,
                    'classroom_management': 0.15,
                    'teaching_structure': 0.20,
                },
            })
        except TeachingEvaluation.DoesNotExist:
            # 尝试从 AIAnalysisResult 中获取
            try:
                result = task.result
                return Response({
                    'task_id': task.id,
                    'scores': {
                        'overall': result.teaching_score,
                        'teaching': result.teacher_score,
                        'engagement': result.student_engagement_score,
                    },
                    'grade': '',
                })
            except AIAnalysisResult.DoesNotExist:
                return Response(
                    {'error': '评分数据不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )

    @action(detail=True, methods=['get'], url_path='report')
    def get_report(self, request, pk=None):
        # 获取分析报告
        task = self.get_object()

        try:
            report = task.report
            return Response({
                'task_id': task.id,
                'report_id': report.id,
                'title': report.title,
                'summary': report.summary,
                'teacher_report': report.teacher_report,
                'school_report': report.school_report,
                'html_content': report.html_content,
                'has_pdf': bool(report.pdf_file),
                'pdf_url': report.pdf_file.url if report.pdf_file else '',
                'download_count': report.download_count,
                'created_time': report.created_time,
            })
        except AIReport.DoesNotExist:
            # 尝试从 AIAnalysisResult 中获取基本信息
            try:
                result = task.result
                return Response({
                    'task_id': task.id,
                    'title': '课堂分析报告',
                    'summary': {
                        'overall_score': result.teaching_score,
                        'strengths': result.improvement_suggestions[:3] if result.improvement_suggestions else [],
                    },
                    'has_pdf': False,
                    'pdf_url': '',
                    'note': '完整报告正在生成中',
                })
            except AIAnalysisResult.DoesNotExist:
                return Response(
                    {'error': '报告不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )

    @action(detail=True, methods=['get'], url_path='report/pdf')
    def get_report_pdf(self, request, pk=None):
        # 下载PDF报告
        task = self.get_object()

        try:
            report = task.report
            
            if not report.pdf_file:
                return Response(
                    {'error': 'PDF文件不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 增加下载次数
            report.download_count += 1
            report.save(update_fields=['download_count'])
            
            # 返回文件
            response = FileResponse(report.pdf_file.open('rb'))
            response['Content-Type'] = 'application/pdf'
            response['Content-Disposition'] = f'attachment; filename="report_{task.id}.pdf"'
            return response
            
        except AIReport.DoesNotExist:
            return Response(
                {'error': '报告不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='retry')
    def retry_task(self, request, pk=None):
        # 重试任务
        task = self.get_object()

        # 重置状态
        task.status = ClassAnalysisTask.STATUS_PENDING
        task.progress = 0
        task.current_step = '等待中'
        task.error_message = ''
        task.save()

        # 重新执行任务
        if HAS_CELERY:
            try:
                run_analysis_task.delay(task.id)
            except Exception:
                run_analysis_task_sync(task.id)
        else:
            run_analysis_task_sync(task.id)

        return Response({
            'id': task.id,
            'status': task.status,
            'message': '任务已重新开始',
        })


class AIAnalysisResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AIAnalysisResult.objects.all()
    serializer_class = AIAnalysisResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 普通用户只能看到自己的结果
        if not user.is_staff:
            queryset = queryset.filter(task__teacher=user)

        return queryset.order_by('-created_time')


class AIModelConfigViewSet(viewsets.ModelViewSet):
    queryset = AIModelConfig.objects.all()
    serializer_class = AIModelConfigSerializer
    permission_classes = [IsAdminUser]


class ProviderStatusView(APIView):
    """Provider 状态列表"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        from ai_analysis.services.provider_health import get_provider_status_summary
        
        summary = get_provider_status_summary()
        
        # 获取详细列表
        from ai_analysis.models import AIModelConfig
        configs = AIModelConfig.objects.filter(is_active=True).order_by('priority')
        
        details = []
        for config in configs:
            details.append({
                'id': config.id,
                'provider': config.provider,
                'deployment_type': config.deployment_type,
                'model_name': config.model_name,
                'model_type': config.model_type,
                'health_status': config.health_status,
                'is_active': config.is_active,
                'priority': config.priority,
                'last_health_check_time': config.last_health_check_time.isoformat() if config.last_health_check_time else None,
                'last_error_message': config.last_error_message,
                'capabilities': config.get_capabilities(),
            })
        
        return Response({
            'summary': summary,
            'details': details,
        })


class UsageStatisticsView(APIView):
    """AI 使用统计"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        from django.db.models import Sum, Count
        from django.utils import timezone
        from datetime import timedelta
        
        # 时间范围参数
        days = request.query_params.get('days', 30)
        try:
            days = int(days)
        except (ValueError, TypeError):
            days = 30
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # 总体统计
        total_stats = AIUsageLog.objects.filter(
            request_time__gte=start_date,
            request_time__lte=end_date
        ).aggregate(
            total_requests=Count('id'),
            total_tokens=Sum('total_tokens'),
            total_input_tokens=Sum('input_tokens'),
            total_output_tokens=Sum('output_tokens'),
            total_cost=Sum('estimated_cost'),
            success_count=Count('id', filter=models.Q(status='success')),
            failed_count=Count('id', filter=models.Q(status='failed')),
        )
        
        # 按 Provider 统计
        by_provider = AIUsageLog.objects.filter(
            request_time__gte=start_date,
            request_time__lte=end_date
        ).values('provider', 'model_name').annotate(
            requests=Count('id'),
            tokens=Sum('total_tokens'),
            cost=Sum('estimated_cost'),
        ).order_by('-tokens')
        
        # 按任务类型统计
        by_task_type = AIUsageLog.objects.filter(
            request_time__gte=start_date,
            request_time__lte=end_date
        ).values('task_type').annotate(
            requests=Count('id'),
            tokens=Sum('total_tokens'),
            cost=Sum('estimated_cost'),
        ).order_by('-tokens')
        
        return Response({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days,
            },
            'total': {
                'total_requests': total_stats['total_requests'] or 0,
                'total_tokens': total_stats['total_tokens'] or 0,
                'total_input_tokens': total_stats['total_input_tokens'] or 0,
                'total_output_tokens': total_stats['total_output_tokens'] or 0,
                'total_cost': float(total_stats['total_cost'] or 0),
                'success_count': total_stats['success_count'] or 0,
                'failed_count': total_stats['failed_count'] or 0,
                'success_rate': round(
                    (total_stats['success_count'] or 0) / (total_stats['total_requests'] or 1) * 100, 2
                ),
            },
            'by_provider': list(by_provider),
            'by_task_type': list(by_task_type),
        })


class AvailableModelsView(APIView):
    """可用模型列表"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        from ai_analysis.services.provider_health import get_available_providers
        
        # 能力参数
        capability = request.query_params.get('capability', 'chat')
        
        configs = get_available_providers(capability)
        
        models = []
        for config in configs:
            models.append({
                'id': config.id,
                'provider': config.provider,
                'deployment_type': config.deployment_type,
                'model_name': config.model_name,
                'model_type': config.model_type,
                'priority': config.priority,
                'capabilities': config.get_capabilities(),
                'health_status': config.health_status,
            })
        
        return Response({
            'capability': capability,
            'count': len(models),
            'models': models,
        })
