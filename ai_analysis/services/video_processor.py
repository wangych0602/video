import os
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger('ai_analysis.video_processor')


class VideoProcessor:
    # 视频处理器
    
    def __init__(self, media_root: str = None):
        self.media_root = media_root or os.environ.get('MEDIA_ROOT', '/app/media')
        self.ai_frames_dir = os.path.join(self.media_root, 'ai_frames')
        os.makedirs(self.ai_frames_dir, exist_ok=True)
    
    def get_video_info(self, video_path: str) -> Dict:
        # 使用 ffprobe 获取视频信息
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return self._parse_video_info(data)
        except FileNotFoundError:
            logger.warning('ffprobe not found, using mock video info')
        except Exception as e:
            logger.error(f'Error getting video info: {e}')
        
        # 返回模拟数据
        return self._get_mock_video_info(video_path)
    
    def _parse_video_info(self, data: Dict) -> Dict:
        # 解析 ffprobe 输出
        format_info = data.get('format', {})
        streams = data.get('streams', [])
        
        video_stream = None
        audio_stream = None
        
        for stream in streams:
            if stream.get('codec_type') == 'video':
                video_stream = stream
            elif stream.get('codec_type') == 'audio':
                audio_stream = stream
        
        info = {
            'duration': float(format_info.get('duration', 0)),
            'size': int(format_info.get('size', 0)),
            'bit_rate': int(format_info.get('bit_rate', 0)),
            'format': format_info.get('format_name', ''),
        }
        
        if video_stream:
            info.update({
                'video_codec': video_stream.get('codec_name', ''),
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0)),
                'resolution': f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}",
                'fps': self._parse_fps(video_stream.get('r_frame_rate', '0/0')),
                'bit_depth': video_stream.get('bits_per_raw_sample', 0),
                'pix_fmt': video_stream.get('pix_fmt', ''),
            })
        
        if audio_stream:
            info.update({
                'audio_codec': audio_stream.get('codec_name', ''),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': audio_stream.get('channels', 0),
                'audio_bit_rate': int(audio_stream.get('bit_rate', 0)),
            })
        
        return info
    
    def _parse_fps(self, fps_str: str) -> float:
        # 解析帧率字符串，如 "30/1" 或 "2997/100"
        try:
            if '/' in fps_str:
                num, den = fps_str.split('/')
                return round(float(num) / float(den), 2)
            return float(fps_str)
        except (ValueError, ZeroDivisionError):
            return 0.0
    
    def _get_mock_video_info(self, video_path: str) -> Dict:
        # 返回模拟视频信息（用于测试）
        filename = os.path.basename(video_path)
        return {
            'duration': 1800.0,  # 30分钟
            'size': 524288000,  # 500MB
            'bit_rate': 2330000,
            'format': 'mov,mp4,m4a,3gp,3g2,mj2',
            'video_codec': 'h264',
            'width': 1920,
            'height': 1080,
            'resolution': '1920x1080',
            'fps': 30.0,
            'bit_depth': 8,
            'pix_fmt': 'yuv420p',
            'audio_codec': 'aac',
            'sample_rate': 44100,
            'channels': 2,
            'audio_bit_rate': 128000,
            'mock': True,
            'filename': filename,
        }
    
    def extract_key_frames(
        self,
        video_path: str,
        task_id: int,
        interval: int = 30
    ) -> List[Dict]:
        # 抽取关键帧
        output_dir = os.path.join(self.ai_frames_dir, str(task_id))
        os.makedirs(output_dir, exist_ok=True)
        
        frames = []
        
        try:
            # 先获取视频时长
            video_info = self.get_video_info(video_path)
            duration = video_info.get('duration', 0)
            
            if duration <= 0:
                duration = 1800  # 默认30分钟
            
            # 计算需要抽取的帧数
            num_frames = int(duration // interval) + 1
            
            # 使用 ffmpeg 抽帧
            output_pattern = os.path.join(output_dir, 'frame_%04d.jpg')
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', f'fps=1/{interval}',
                '-q:v', '2',
                '-y',
                output_pattern
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                # 收集生成的帧
                for i in range(num_frames):
                    frame_file = os.path.join(output_dir, f'frame_{i+1:04d}.jpg')
                    if os.path.exists(frame_file):
                        timestamp = i * interval
                        frames.append({
                            'index': i,
                            'timestamp': timestamp,
                            'time_str': self._format_time(timestamp),
                            'file_path': frame_file,
                            'url': f'/media/ai_frames/{task_id}/frame_{i+1:04d}.jpg',
                        })
        except FileNotFoundError:
            logger.warning('ffmpeg not found, using mock frames')
            frames = self._get_mock_frames(task_id, output_dir)
        except Exception as e:
            logger.error(f'Error extracting key frames: {e}')
            frames = self._get_mock_frames(task_id, output_dir)
        
        if not frames:
            frames = self._get_mock_frames(task_id, output_dir)
        
        logger.info(f'Extracted {len(frames)} key frames for task {task_id}')
        return frames
    
    def _get_mock_frames(self, task_id: int, output_dir: str) -> List[Dict]:
        # 返回模拟帧数据（用于测试）
        os.makedirs(output_dir, exist_ok=True)
        
        frames = []
        # 生成5个模拟帧
        for i in range(5):
            timestamp = i * 30
            frames.append({
                'index': i,
                'timestamp': timestamp,
                'time_str': self._format_time(timestamp),
                'file_path': os.path.join(output_dir, f'frame_{i+1:04d}.jpg'),
                'url': f'/media/ai_frames/{task_id}/frame_{i+1:04d}.jpg',
                'mock': True,
            })
        
        return frames
    
    def _format_time(self, seconds: int) -> str:
        # 格式化时间为 HH:MM:SS
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f'{hours:02d}:{minutes:02d}:{secs:02d}'
    
    def get_frame_at_time(self, video_path: str, timestamp: int, output_path: str) -> bool:
        # 获取指定时间点的帧
        try:
            cmd = [
                'ffmpeg',
                '-ss', str(timestamp),
                '-i', video_path,
                '-vframes', '1',
                '-q:v', '2',
                '-y',
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0 and os.path.exists(output_path)
        except Exception as e:
            logger.error(f'Error getting frame at time {timestamp}: {e}')
            return False
    
    def generate_thumbnail(self, video_path: str, output_path: str, timestamp: int = 1) -> bool:
        # 生成视频缩略图
        return self.get_frame_at_time(video_path, timestamp, output_path)
    
    def get_video_duration(self, video_path: str) -> float:
        # 获取视频时长
        info = self.get_video_info(video_path)
        return info.get('duration', 0)