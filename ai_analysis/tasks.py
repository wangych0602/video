import logging
from django.utils import timezone

from .models import ClassAnalysisTask, AIAnalysisResult
from .agents.VideoAnalysisAgent import VideoAnalysisAgent
from .agents.SpeechAgent import SpeechAgent
from .agents.TeachingEvaluationAgent import TeachingEvaluationAgent
from .agents.ReportAgent import ReportAgent

logger = logging.getLogger('ai_analysis.tasks')

# 可选导入 Celery
try:
    from celery import shared_task
    HAS_CELERY = True
except ImportError:
    HAS_CELERY = False
    logger.warning('Celery not available, tasks will run synchronously')


def run_analysis_task_sync(task_id: int):
    # 同步运行分析任务
    try:
        task = ClassAnalysisTask.objects.get(id=task_id)
    except ClassAnalysisTask.DoesNotExist:
        logger.error(f'Task {task_id} not found')
        return None
    
    # 更新任务状态为处理中
    task.status = ClassAnalysisTask.STATUS_PROCESSING
    task.progress = 0
    task.save()
    
    try:
        logger.info(f'Starting analysis task {task_id}')
        
        # 准备输入数据
        input_data = {
            'video_id': task.video.id,
            'video_path': task.video.file.path if hasattr(task.video, 'file') and task.video.file else '',
            'task_type': task.task_type,
        }
        
        # 1. 视频分析
        video_agent = VideoAnalysisAgent()
        video_result = video_agent.run(input_data)
        
        task.progress = 25
        task.save()
        
        # 2. 语音分析
        speech_agent = SpeechAgent()
        speech_result = speech_agent.run(input_data)
        
        task.progress = 50
        task.save()
        
        # 3. 教学评估
        eval_input = {
            'video_id': task.video.id,
            'video_result': video_result,
            'speech_result': speech_result,
        }
        eval_agent = TeachingEvaluationAgent()
        eval_result = eval_agent.run(eval_input)
        
        task.progress = 75
        task.save()
        
        # 4. 生成报告
        report_input = {
            'video_id': task.video.id,
            'video_result': video_result,
            'speech_result': speech_result,
            'evaluation_result': eval_result,
        }
        report_agent = ReportAgent()
        report_result = report_agent.run(report_input)
        
        # 保存分析结果
        AIAnalysisResult.objects.update_or_create(
            task=task,
            defaults={
                'summary': report_result.get('summary', ''),
                'keywords': report_result.get('keywords', []),
                'knowledge_points': report_result.get('knowledge_points', []),
                'teaching_score': report_result.get('teaching_score', 0),
                'student_engagement_score': report_result.get('student_engagement_score', 0),
                'teacher_score': report_result.get('teacher_score', 0),
                'suggestions': report_result.get('suggestions', ''),
                'report_url': report_result.get('report_url', ''),
            }
        )
        
        # 更新任务状态为完成
        task.status = ClassAnalysisTask.STATUS_COMPLETED
        task.progress = 100
        task.finished_time = timezone.now()
        task.save()
        
        logger.info(f'Analysis task {task_id} completed successfully')
        
        return task
        
    except Exception as e:
        logger.error(f'Analysis task {task_id} failed: {str(e)}')
        
        # 更新任务状态为失败
        task.status = ClassAnalysisTask.STATUS_FAILED
        task.error_message = str(e)
        task.finished_time = timezone.now()
        task.save()
        
        return task


if HAS_CELERY:
    @shared_task(bind=True, name='ai_analysis.run_analysis_task')
    def run_analysis_task(self, task_id: int):
        # 异步运行分析任务（Celery）
        try:
            task = ClassAnalysisTask.objects.get(id=task_id)
        except ClassAnalysisTask.DoesNotExist:
            logger.error(f'Task {task_id} not found')
            return
        
        # 更新任务状态为处理中
        task.status = ClassAnalysisTask.STATUS_PROCESSING
        task.progress = 0
        task.save()
        
        try:
            logger.info(f'Starting async analysis task {task_id}')
            
            # 准备输入数据
            input_data = {
                'video_id': task.video.id,
                'video_path': task.video.file.path if task.video.file else '',
                'task_type': task.task_type,
            }
            
            # 1. 视频分析 (25%)
            self.update_state(state='PROGRESS', meta={'progress': 10})
            task.progress = 10
            task.save()
            
            video_agent = VideoAnalysisAgent()
            video_result = video_agent.run(input_data)
            
            # 2. 语音分析 (50%)
            self.update_state(state='PROGRESS', meta={'progress': 35})
            task.progress = 35
            task.save()
            
            speech_agent = SpeechAgent()
            speech_result = speech_agent.run(input_data)
            
            # 3. 教学评估 (75%)
            self.update_state(state='PROGRESS', meta={'progress': 60})
            task.progress = 60
            task.save()
            
            eval_input = {
                'video_id': task.video.id,
                'video_result': video_result,
                'speech_result': speech_result,
            }
            eval_agent = TeachingEvaluationAgent()
            eval_result = eval_agent.run(eval_input)
            
            # 4. 生成报告 (100%)
            self.update_state(state='PROGRESS', meta={'progress': 85})
            task.progress = 85
            task.save()
            
            report_input = {
                'video_id': task.video.id,
                'video_result': video_result,
                'speech_result': speech_result,
                'evaluation_result': eval_result,
            }
            report_agent = ReportAgent()
            report_result = report_agent.run(report_input)
            
            # 保存分析结果
            AIAnalysisResult.objects.update_or_create(
                task=task,
                defaults={
                    'summary': report_result.get('summary', ''),
                    'keywords': report_result.get('keywords', []),
                    'knowledge_points': report_result.get('knowledge_points', []),
                    'teaching_score': report_result.get('teaching_score', 0),
                    'student_engagement_score': report_result.get('student_engagement_score', 0),
                    'teacher_score': report_result.get('teacher_score', 0),
                    'suggestions': report_result.get('suggestions', ''),
                    'report_url': report_result.get('report_url', ''),
                }
            )
            
            # 更新任务状态为完成
            task.status = ClassAnalysisTask.STATUS_COMPLETED
            task.progress = 100
            task.finished_time = timezone.now()
            task.save()
            
            logger.info(f'Async analysis task {task_id} completed successfully')
            
            return {
                'task_id': task_id,
                'status': 'completed',
                'progress': 100
            }
            
        except Exception as e:
            logger.error(f'Async analysis task {task_id} failed: {str(e)}')
            
            # 更新任务状态为失败
            task.status = ClassAnalysisTask.STATUS_FAILED
            task.error_message = str(e)
            task.finished_time = timezone.now()
            task.save()
            
            return {
                'task_id': task_id,
                'status': 'failed',
                'error': str(e)
            }
else:
    # 没有 Celery 时，run_analysis_task 指向同步版本
    def run_analysis_task(task_id: int):
        return run_analysis_task_sync(task_id)