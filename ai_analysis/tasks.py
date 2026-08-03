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


def update_task_progress(task_id: int, progress: int, step: str = '', status: str = None):
    # 更新任务进度
    try:
        task = ClassAnalysisTask.objects.get(id=task_id)
        task.progress = progress
        if step:
            task.current_step = step
        if status:
            task.status = status
        task.save(update_fields=['progress', 'current_step', 'status'])
    except Exception as e:
        logger.error(f'Error updating task progress: {e}')


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
    task.current_step = '任务开始'
    task.save()
    
    try:
        logger.info(f'Starting analysis task {task_id}')
        
        # 准备输入数据
        video_path = ''
        if hasattr(task.video, 'file') and task.video.file:
            video_path = task.video.file.path
        
        input_data = {
            'video_id': task.video.id,
            'video_path': video_path,
            'task_id': task.id,
            'task_type': task.task_type,
        }
        
        # 1. 视频分析 (0% - 30%)
        update_task_progress(task_id, 5, '开始视频分析')
        
        video_agent = VideoAnalysisAgent()
        video_result = video_agent.run(input_data)
        
        update_task_progress(task_id, 30, '视频分析完成')
        logger.info(f'Video analysis completed for task {task_id}')
        
        # 2. 语音分析 (30% - 50%)
        update_task_progress(task_id, 35, '开始语音分析')
        
        speech_agent = SpeechAgent()
        speech_result = speech_agent.run(input_data)
        
        update_task_progress(task_id, 50, '语音分析完成')
        logger.info(f'Speech analysis completed for task {task_id}')
        
        # 3. 教学评估 (50% - 80%)
        update_task_progress(task_id, 55, '开始教学评估')
        
        eval_input = {
            'video_id': task.video.id,
            'video_result': video_result,
            'speech_result': speech_result,
        }
        eval_agent = TeachingEvaluationAgent()
        eval_result = eval_agent.run(eval_input)
        
        update_task_progress(task_id, 80, '教学评估完成')
        logger.info(f'Teaching evaluation completed for task {task_id}')
        
        # 4. 生成报告 (80% - 100%)
        update_task_progress(task_id, 85, '生成分析报告')
        
        report_input = {
            'video_id': task.video.id,
            'video_result': video_result,
            'speech_result': speech_result,
            'evaluation_result': eval_result,
        }
        report_agent = ReportAgent()
        report_result = report_agent.run(report_input)
        
        update_task_progress(task_id, 95, '保存分析结果')
        
        # 保存分析结果
        result_data = {
            'summary': report_result.get('summary', ''),
            'keywords': report_result.get('keywords', []),
            'knowledge_points': report_result.get('knowledge_points', []),
            'teaching_score': report_result.get('teaching_score', 0),
            'student_engagement_score': report_result.get('student_engagement_score', 0),
            'teacher_score': report_result.get('teacher_score', 0),
            'suggestions': report_result.get('suggestions', ''),
            'report_url': report_result.get('report_url', ''),
            # 视频分析结果
            'video_info': video_result.get('video_info', {}),
            'key_frames': video_result.get('key_frames', []),
            'scene_analysis': video_result.get('scene_analysis', {}),
            'teacher_actions': video_result.get('teacher_actions', []),
            'ppt_content': video_result.get('ppt_content', []),
            'blackboard_content': video_result.get('blackboard_content', []),
            'student_interaction': video_result.get('student_interaction', {}),
            'classroom_environment': video_result.get('classroom_environment', {}),
        }
        
        AIAnalysisResult.objects.update_or_create(
            task=task,
            defaults=result_data
        )
        
        # 更新任务状态为完成
        task.status = ClassAnalysisTask.STATUS_COMPLETED
        task.progress = 100
        task.current_step = '分析完成'
        task.finished_time = timezone.now()
        task.save()
        
        logger.info(f'Analysis task {task_id} completed successfully')
        
        return task
        
    except Exception as e:
        logger.error(f'Analysis task {task_id} failed: {str(e)}')
        
        # 更新任务状态为失败
        task.status = ClassAnalysisTask.STATUS_FAILED
        task.error_message = str(e)
        task.current_step = '分析失败'
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
        task.current_step = '任务开始'
        task.save()
        
        try:
            logger.info(f'Starting async analysis task {task_id}')
            
            # 准备输入数据
            video_path = ''
            if hasattr(task.video, 'file') and task.video.file:
                video_path = task.video.file.path
            
            input_data = {
                'video_id': task.video.id,
                'video_path': video_path,
                'task_id': task.id,
                'task_type': task.task_type,
            }
            
            # 1. 视频分析 (0% - 30%)
            self.update_state(state='PROGRESS', meta={'progress': 5, 'step': '开始视频分析'})
            update_task_progress(task_id, 5, '开始视频分析')
            
            video_agent = VideoAnalysisAgent()
            video_result = video_agent.run(input_data)
            
            self.update_state(state='PROGRESS', meta={'progress': 30, 'step': '视频分析完成'})
            update_task_progress(task_id, 30, '视频分析完成')
            
            # 2. 语音分析 (30% - 50%)
            self.update_state(state='PROGRESS', meta={'progress': 35, 'step': '开始语音分析'})
            update_task_progress(task_id, 35, '开始语音分析')
            
            speech_agent = SpeechAgent()
            speech_result = speech_agent.run(input_data)
            
            self.update_state(state='PROGRESS', meta={'progress': 50, 'step': '语音分析完成'})
            update_task_progress(task_id, 50, '语音分析完成')
            
            # 3. 教学评估 (50% - 80%)
            self.update_state(state='PROGRESS', meta={'progress': 55, 'step': '开始教学评估'})
            update_task_progress(task_id, 55, '开始教学评估')
            
            eval_input = {
                'video_id': task.video.id,
                'video_result': video_result,
                'speech_result': speech_result,
            }
            eval_agent = TeachingEvaluationAgent()
            eval_result = eval_agent.run(eval_input)
            
            self.update_state(state='PROGRESS', meta={'progress': 80, 'step': '教学评估完成'})
            update_task_progress(task_id, 80, '教学评估完成')
            
            # 4. 生成报告 (80% - 100%)
            self.update_state(state='PROGRESS', meta={'progress': 85, 'step': '生成分析报告'})
            update_task_progress(task_id, 85, '生成分析报告')
            
            report_input = {
                'video_id': task.video.id,
                'video_result': video_result,
                'speech_result': speech_result,
                'evaluation_result': eval_result,
            }
            report_agent = ReportAgent()
            report_result = report_agent.run(report_input)
            
            self.update_state(state='PROGRESS', meta={'progress': 95, 'step': '保存分析结果'})
            update_task_progress(task_id, 95, '保存分析结果')
            
            # 保存分析结果
            result_data = {
                'summary': report_result.get('summary', ''),
                'keywords': report_result.get('keywords', []),
                'knowledge_points': report_result.get('knowledge_points', []),
                'teaching_score': report_result.get('teaching_score', 0),
                'student_engagement_score': report_result.get('student_engagement_score', 0),
                'teacher_score': report_result.get('teacher_score', 0),
                'suggestions': report_result.get('suggestions', ''),
                'report_url': report_result.get('report_url', ''),
                # 视频分析结果
                'video_info': video_result.get('video_info', {}),
                'key_frames': video_result.get('key_frames', []),
                'scene_analysis': video_result.get('scene_analysis', {}),
                'teacher_actions': video_result.get('teacher_actions', []),
                'ppt_content': video_result.get('ppt_content', []),
                'blackboard_content': video_result.get('blackboard_content', []),
                'student_interaction': video_result.get('student_interaction', {}),
                'classroom_environment': video_result.get('classroom_environment', {}),
            }
            
            AIAnalysisResult.objects.update_or_create(
                task=task,
                defaults=result_data
            )
            
            # 更新任务状态为完成
            task.status = ClassAnalysisTask.STATUS_COMPLETED
            task.progress = 100
            task.current_step = '分析完成'
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
            task.current_step = '分析失败'
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