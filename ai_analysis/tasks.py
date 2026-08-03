import os
import logging
from datetime import datetime

from django.conf import settings

logger = logging.getLogger('ai_analysis.tasks')

# 检测 Celery 是否可用
HAS_CELERY = False
try:
    from celery import shared_task
    HAS_CELERY = True
except ImportError:
    logger.warning('Celery not available, tasks will run synchronously')
    
    # 定义一个假的 shared_task 装饰器，让代码能正常运行
    def shared_task(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.delay = lambda *a, **kw: func(*a, **kw)
        return wrapper


def update_task_progress(task_id: int, progress: int, step: str = '', status: str = None):
    # 更新任务进度
    try:
        from .models import ClassAnalysisTask
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
    # 同步执行分析任务
    try:
        from .models import ClassAnalysisTask, AIAnalysisResult, TeachingEvaluation
        from .agents.VideoAnalysisAgent import VideoAnalysisAgent
        from .agents.SpeechAnalysisAgent import SpeechAnalysisAgent
        from .agents.TeachingEvaluationAgent import TeachingEvaluationAgent
        from .agents.ReportAgent import ReportAgent
        
        task = ClassAnalysisTask.objects.get(id=task_id)
        
        # 更新状态为处理中
        task.status = ClassAnalysisTask.STATUS_PROCESSING
        task.progress = 0
        task.current_step = '任务开始'
        task.started_time = datetime.now()
        task.save()
        
        logger.info(f'Starting analysis task {task_id}')
        
        # 获取视频路径
        video_path = ''
        if task.video and task.video.file:
            video_path = task.video.file.path
        
        # 初始化结果
        result_data = {}
        
        # 1. 视频分析
        if task.task_type in ['full', 'video']:
            try:
                update_task_progress(task_id, 5, '开始视频分析')
                
                video_agent = VideoAnalysisAgent()
                video_input = {
                    'video_path': video_path,
                    'video_id': task.video_id,
                    'task_id': task_id,
                }
                video_result = video_agent.run(video_input)
                
                if video_result.get('success'):
                    result_data['video'] = video_result
                    update_task_progress(task_id, 30, '视频分析完成')
                    logger.info(f'Video analysis completed for task {task_id}')
                else:
                    logger.warning(f'Video analysis failed for task {task_id}: {video_result.get("error")}')
                    
            except Exception as e:
                logger.error(f'Video analysis error for task {task_id}: {e}')
        
        # 2. 语音分析
        if task.task_type in ['full', 'speech']:
            try:
                update_task_progress(task_id, 35, '开始语音分析')
                
                speech_agent = SpeechAnalysisAgent()
                speech_input = {
                    'video_path': video_path,
                    'video_id': task.video_id,
                    'task_id': task_id,
                }
                speech_result = speech_agent.run(speech_input)
                
                if speech_result.get('success'):
                    result_data['speech'] = speech_result
                    update_task_progress(task_id, 50, '语音分析完成')
                    logger.info(f'Speech analysis completed for task {task_id}')
                else:
                    logger.warning(f'Speech analysis failed for task {task_id}: {speech_result.get("error")}')
                    
            except Exception as e:
                logger.error(f'Speech analysis error for task {task_id}: {e}')
        
        # 3. 教学评价
        if task.task_type in ['full', 'teaching']:
            try:
                update_task_progress(task_id, 55, '开始教学评价')
                
                eval_agent = TeachingEvaluationAgent()
                eval_input = {
                    'video_result': result_data.get('video', {}),
                    'speech_result': result_data.get('speech', {}),
                    'video_id': task.video_id,
                    'task_id': task_id,
                }
                eval_result = eval_agent.run(eval_input)
                
                if eval_result.get('success'):
                    result_data['evaluation'] = eval_result
                    update_task_progress(task_id, 80, '教学评价完成')
                    logger.info(f'Teaching evaluation completed for task {task_id}')
                else:
                    logger.warning(f'Teaching evaluation failed for task {task_id}: {eval_result.get("error")}')
                    
            except Exception as e:
                logger.error(f'Teaching evaluation error for task {task_id}: {e}')
        
        # 4. 生成报告
        try:
            update_task_progress(task_id, 85, '生成分析报告')
            
            report_agent = ReportAgent()
            report_input = {
                'video_result': result_data.get('video', {}),
                'speech_result': result_data.get('speech', {}),
                'evaluation_result': result_data.get('evaluation', {}),
                'video_id': task.video_id,
            }
            report_result = report_agent.run(report_input)
            
            if report_result.get('success'):
                result_data['report'] = report_result
                update_task_progress(task_id, 95, '保存分析结果')
                logger.info(f'Report generation completed for task {task_id}')
                
        except Exception as e:
            logger.error(f'Report generation error for task {task_id}: {e}')
        
        # 5. 保存结果
        try:
            # 删除旧结果
            if hasattr(task, 'result'):
                task.result.delete()
            if hasattr(task, 'evaluation'):
                task.evaluation.delete()
            
            # 创建新结果
            result = AIAnalysisResult(task=task)
            
            # 视频分析结果
            video_result = result_data.get('video', {})
            if video_result:
                result.video_info = video_result.get('video_info', {})
                result.key_frames = video_result.get('key_frames', [])
                result.scene_analysis = video_result.get('scene_analysis', {})
                result.teacher_actions = video_result.get('teacher_actions', [])
                result.ppt_content = video_result.get('ppt_content', [])
                result.blackboard_content = video_result.get('blackboard_content', [])
                result.student_interaction = video_result.get('student_interaction', {})
                result.classroom_environment = video_result.get('classroom_environment', {})
            
            # 语音分析结果
            speech_result = result_data.get('speech', {})
            if speech_result:
                result.transcript = speech_result.get('transcript', '')
                result.speech_segments = speech_result.get('speech_segments', [])
                result.speaking_rate = speech_result.get('speaking_rate', {})
                result.keywords = speech_result.get('keywords', [])
                result.knowledge_points = speech_result.get('knowledge_points', [])
            
            # 教学评价结果
            eval_result = result_data.get('evaluation', {})
            if eval_result:
                result.teaching_score = eval_result.get('overall_score', 0)
                result.evaluation_report = {
                    'knowledge_score': eval_result.get('knowledge_score', 0),
                    'interaction_score': eval_result.get('interaction_score', 0),
                    'expression_score': eval_result.get('expression_score', 0),
                    'classroom_management_score': eval_result.get('classroom_management_score', 0),
                    'teaching_structure_score': eval_result.get('teaching_structure_score', 0),
                    'grade': eval_result.get('grade', ''),
                    'strengths': eval_result.get('strengths', []),
                    'weaknesses': eval_result.get('weaknesses', []),
                    'evaluation_method': eval_result.get('evaluation_method', 'rule_based'),
                }
                result.improvement_suggestions = eval_result.get('suggestions', [])
                result.overall_score = eval_result.get('overall_score', 0)
                result.student_engagement_score = eval_result.get('interaction_score', 0)
                result.teacher_score = eval_result.get('knowledge_score', 0)
                result.summary = '; '.join(eval_result.get('strengths', []))
                result.suggestions = '\n'.join(eval_result.get('suggestions', []))
                
                # 保存到 TeachingEvaluation 模型
                teaching_eval = TeachingEvaluation(
                    task=task,
                    overall_score=eval_result.get('overall_score', 0),
                    knowledge_score=eval_result.get('knowledge_score', 0),
                    interaction_score=eval_result.get('interaction_score', 0),
                    expression_score=eval_result.get('expression_score', 0),
                    classroom_management_score=eval_result.get('classroom_management_score', 0),
                    teaching_structure_score=eval_result.get('teaching_structure_score', 0),
                    grade=eval_result.get('grade', ''),
                    strengths=eval_result.get('strengths', []),
                    weaknesses=eval_result.get('weaknesses', []),
                    suggestions=eval_result.get('suggestions', []),
                    evaluation_method=eval_result.get('evaluation_method', 'rule_based'),
                )
                teaching_eval.save()
            
            # 报告结果
            report_result = result_data.get('report', {})
            if report_result:
                result.report_url = report_result.get('report_url', '')
                if not result.summary:
                    result.summary = report_result.get('summary', '')
                if not result.suggestions:
                    result.suggestions = report_result.get('suggestions', '')
            
            result.save()
            
            # 更新任务状态
            task.status = ClassAnalysisTask.STATUS_COMPLETED
            task.progress = 100
            task.current_step = '分析完成'
            task.finished_time = datetime.now()
            task.save()
            
            logger.info(f'Analysis task {task_id} completed successfully')
            
        except Exception as e:
            logger.error(f'Error saving result for task {task_id}: {e}')
            task.status = ClassAnalysisTask.STATUS_FAILED
            task.error_message = str(e)
            task.save()
            
    except Exception as e:
        logger.error(f'Analysis task {task_id} failed: {e}')
        try:
            from .models import ClassAnalysisTask
            task = ClassAnalysisTask.objects.get(id=task_id)
            task.status = ClassAnalysisTask.STATUS_FAILED
            task.error_message = str(e)
            task.save()
        except:
            pass


if HAS_CELERY:
    @shared_task
    def run_analysis_task(task_id: int):
        # Celery 异步任务
        run_analysis_task_sync(task_id)
else:
    # 没有 Celery 时，定义一个同步版本
    def run_analysis_task(task_id: int):
        run_analysis_task_sync(task_id)
    # 添加 delay 方法，保持接口一致
    run_analysis_task.delay = lambda task_id: run_analysis_task_sync(task_id)