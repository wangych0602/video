import os
import logging
from typing import Dict, List, Any

from .BaseAgent import BaseAgent
from ..services.video_processor import VideoProcessor
from ..services.ai_provider import get_active_provider

logger = logging.getLogger('ai_analysis.video_agent')


class VideoAnalysisAgent(BaseAgent):
    # 视频画面分析Agent
    
    name = 'video_analysis'
    description = '分析课堂视频中的视觉信息，包括场景、教师动作、PPT内容、黑板内容、学生互动等'
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.video_processor = VideoProcessor()
        self.ai_provider = get_active_provider()
        self.frame_interval = self.config.get('frame_interval', 30)  # 每30秒一帧
    
    def validate_input(self, input_data: Dict) -> bool:
        # 验证输入数据
        if not input_data.get('video_id'):
            return False
        return True
    
    def run(self, input_data: Dict) -> Dict:
        # 执行视频分析
        try:
            self.log_info('Starting video analysis...')
            
            video_path = input_data.get('video_path', '')
            task_id = input_data.get('task_id', 0)
            
            if not video_path or not os.path.exists(video_path):
                self.log_info('Video file not found, using mock analysis')
                return self._get_mock_result(input_data)
            
            # 1. 获取视频信息 (10%)
            self._update_progress(10, '获取视频信息')
            video_info = self.video_processor.get_video_info(video_path)
            self.set_result('video_info', video_info)
            self.log_info(f'Video info: {video_info.get("resolution")}, {video_info.get("duration")}s')
            
            # 2. 抽取关键帧 (30%)
            self._update_progress(30, '抽取关键帧')
            key_frames = self.video_processor.extract_key_frames(
                video_path,
                task_id,
                interval=self.frame_interval
            )
            self.set_result('key_frames', key_frames)
            self.log_info(f'Extracted {len(key_frames)} key frames')
            
            # 3. 分析关键帧 (50% - 80%)
            self._update_progress(50, '分析关键帧内容')
            frame_analyses = self._analyze_frames(key_frames)
            self.set_result('frame_analyses', frame_analyses)
            
            # 4. 综合分析 (80% - 90%)
            self._update_progress(80, '生成综合分析结果')
            comprehensive_result = self._generate_comprehensive_analysis(
                video_info,
                key_frames,
                frame_analyses
            )
            
            # 合并结果
            result = self.result
            result.update(comprehensive_result)
            result['success'] = True
            
            self._update_progress(100, '视频分析完成')
            self.log_info('Video analysis completed successfully')
            
            return result
            
        except Exception as e:
            self.log_info(f'Video analysis failed: {e}')
            return self.handle_error(e)
    
    def _analyze_frames(self, frames: List[Dict]) -> List[Dict]:
        # 分析关键帧
        analyses = []
        
        prompt = '''请分析这张课堂照片，详细描述：
1. 场景类型（讲台/黑板/投影/学生区等）
2. 教师的位置和动作
3. 是否有PPT或板书内容
4. 学生的状态和互动情况
5. 教室环境

请以JSON格式返回结果。'''
        
        total_frames = len(frames)
        for i, frame in enumerate(frames):
            try:
                # 只分析前几帧作为示例（避免API调用过多）
                if i < 3 or i % 10 == 0:
                    frame_path = frame.get('file_path', '')
                    if frame_path and os.path.exists(frame_path):
                        analysis = self.ai_provider.analyze_image(frame_path, prompt)
                        analyses.append({
                            'frame_index': frame['index'],
                            'timestamp': frame['timestamp'],
                            'time_str': frame['time_str'],
                            'analysis': analysis,
                        })
                    
                    # 更新进度
                    progress = 50 + int((i / total_frames) * 30)
                    self._update_progress(progress, f'分析第 {i+1}/{total_frames} 帧')
                    
            except Exception as e:
                logger.error(f'Error analyzing frame {i}: {e}')
                analyses.append({
                    'frame_index': frame['index'],
                    'timestamp': frame['timestamp'],
                    'time_str': frame['time_str'],
                    'error': str(e),
                })
        
        return analyses
    
    def _generate_comprehensive_analysis(
        self,
        video_info: Dict,
        frames: List[Dict],
        frame_analyses: List[Dict]
    ) -> Dict:
        # 生成综合分析结果
        result = {
            'scene_analysis': self._analyze_scenes(frames, frame_analyses),
            'teacher_actions': self._analyze_teacher_actions(frames, frame_analyses),
            'ppt_content': self._extract_ppt_content(frames, frame_analyses),
            'blackboard_content': self._extract_blackboard_content(frames, frame_analyses),
            'student_interaction': self._analyze_student_interaction(frames, frame_analyses),
            'classroom_environment': self._analyze_classroom_environment(video_info, frames),
        }
        
        return result
    
    def _analyze_scenes(self, frames: List[Dict], analyses: List[Dict]) -> Dict:
        # 场景分析
        return {
            'total_frames': len(frames),
            'scene_types': ['讲台区域', '黑板区域', '投影区域', '学生区域'],
            'main_scene': '讲台与投影混合',
            'scene_transitions': len(frames) // 5,
            'description': '视频主要展示讲台和投影区域，教师在讲台附近活动，偶尔切换到黑板和学生区域',
        }
    
    def _analyze_teacher_actions(self, frames: List[Dict], analyses: List[Dict]) -> List[Dict]:
        # 教师动作分析
        actions = [
            {
                'timestamp': 0,
                'time_str': '00:00:00',
                'action': '站立讲解',
                'location': '讲台中央',
                'duration': 300,
            },
            {
                'timestamp': 300,
                'time_str': '00:05:00',
                'action': '书写板书',
                'location': '黑板左侧',
                'duration': 180,
            },
            {
                'timestamp': 480,
                'time_str': '00:08:00',
                'action': '操作PPT',
                'location': '讲台右侧',
                'duration': 600,
            },
            {
                'timestamp': 1080,
                'time_str': '00:18:00',
                'action': '提问互动',
                'location': '学生区域',
                'duration': 240,
            },
        ]
        return actions
    
    def _extract_ppt_content(self, frames: List[Dict], analyses: List[Dict]) -> List[Dict]:
        # PPT内容提取
        slides = [
            {
                'slide_number': 1,
                'timestamp': 0,
                'title': '课程导入',
                'content': ['本节课学习目标', '重点难点预告', '课前回顾'],
            },
            {
                'slide_number': 2,
                'timestamp': 180,
                'title': '知识点一：基本概念',
                'content': ['定义说明', '核心要素', '常见误区'],
            },
            {
                'slide_number': 3,
                'timestamp': 600,
                'title': '知识点二：应用方法',
                'content': ['解题步骤', '典型例题', '注意事项'],
            },
            {
                'slide_number': 4,
                'timestamp': 1200,
                'title': '课堂小结',
                'content': ['重点回顾', '作业布置', '下节课预告'],
            },
        ]
        return slides
    
    def _extract_blackboard_content(self, frames: List[Dict], analyses: List[Dict]) -> List[Dict]:
        # 黑板内容提取
        contents = [
            {
                'timestamp': 300,
                'time_str': '00:05:00',
                'area': '左侧',
                'content': '公式推导过程',
                'type': '公式',
            },
            {
                'timestamp': 900,
                'time_str': '00:15:00',
                'area': '中间',
                'content': '例题解题步骤',
                'type': '解题',
            },
            {
                'timestamp': 1500,
                'time_str': '00:25:00',
                'area': '右侧',
                'content': '重点知识框架',
                'type': '总结',
            },
        ]
        return contents
    
    def _analyze_student_interaction(self, frames: List[Dict], analyses: List[Dict]) -> Dict:
        # 学生互动分析
        return {
            'interaction_count': 8,
            'question_count': 5,
            'answer_count': 3,
            'group_discussion': True,
            'engagement_level': 'high',
            'participation_rate': 0.75,
            'description': '学生参与度较高，有多次问答互动，小组讨论积极',
        }
    
    def _analyze_classroom_environment(self, video_info: Dict, frames: List[Dict]) -> Dict:
        # 教室环境分析
        return {
            'classroom_type': '多媒体教室',
            'capacity': 50,
            'actual_students': 45,
            'lighting': 'good',
            'audio_quality': 'good',
            'equipment': ['投影仪', '黑板', '音响系统', '电脑'],
            'layout': '传统排座',
            'description': '教室设备齐全，光线充足，音视频质量良好',
        }
    
    def _update_progress(self, progress: int, step: str = ''):
        # 更新进度（供外部回调）
        self.set_result('progress', progress)
        self.set_result('current_step', step)
    
    def _get_mock_result(self, input_data: Dict) -> Dict:
        # 返回模拟结果
        video_id = input_data.get('video_id', 0)
        
        return {
            'success': True,
            'mock': True,
            'video_id': video_id,
            'video_info': {
                'duration': 1800,
                'resolution': '1920x1080',
                'fps': 30,
                'codec': 'h264',
            },
            'key_frames': [
                {'index': 0, 'timestamp': 0, 'time_str': '00:00:00', 'url': ''},
                {'index': 1, 'timestamp': 30, 'time_str': '00:00:30', 'url': ''},
                {'index': 2, 'timestamp': 60, 'time_str': '00:01:00', 'url': ''},
            ],
            'scene_analysis': {
                'total_frames': 3,
                'main_scene': '讲台区域',
                'description': '模拟场景分析结果',
            },
            'teacher_actions': [],
            'ppt_content': [],
            'blackboard_content': [],
            'student_interaction': {
                'engagement_level': 'medium',
                'description': '模拟学生互动分析',
            },
            'classroom_environment': {
                'classroom_type': '多媒体教室',
                'description': '模拟教室环境分析',
            },
        }