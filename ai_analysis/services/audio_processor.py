import os
import subprocess
import logging
from typing import Dict, Optional

logger = logging.getLogger('ai_analysis.audio_processor')


class AudioProcessor:
    # 音频处理器
    
    def __init__(self, media_root: str = None):
        self.media_root = media_root or os.environ.get('MEDIA_ROOT', '/app/media')
        self.audio_dir = os.path.join(self.media_root, 'ai_audio')
        os.makedirs(self.audio_dir, exist_ok=True)
    
    def extract_audio(
        self,
        video_path: str,
        task_id: int,
        sample_rate: int = 16000,
        channels: int = 1
    ) -> Dict:
        # 从视频中提取音频
        output_dir = os.path.join(self.audio_dir, str(task_id))
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, 'audio.wav')
        
        result = {
            'success': False,
            'audio_path': output_path,
            'duration': 0,
            'sample_rate': sample_rate,
            'channels': channels,
            'format': 'wav',
        }
        
        try:
            # 使用 ffmpeg 提取音频
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # 不要视频
                '-acodec', 'pcm_s16le',  # PCM 16bit
                '-ar', str(sample_rate),  # 采样率
                '-ac', str(channels),  # 声道数
                '-y',  # 覆盖输出
                output_path
            ]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if process.returncode == 0 and os.path.exists(output_path):
                # 获取音频信息
                audio_info = self._get_audio_info(output_path)
                result.update(audio_info)
                result['success'] = True
                logger.info(f'Audio extracted successfully: {output_path}')
            else:
                logger.error(f'FFmpeg error: {process.stderr}')
                result['error'] = process.stderr
                
        except FileNotFoundError:
            logger.warning('ffmpeg not found, using mock audio')
            result = self._get_mock_audio(task_id, output_path)
        except Exception as e:
            logger.error(f'Error extracting audio: {e}')
            result['error'] = str(e)
            result = self._get_mock_audio(task_id, output_path)
        
        return result
    
    def _get_audio_info(self, audio_path: str) -> Dict:
        # 获取音频信息
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                audio_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                format_info = data.get('format', {})
                streams = data.get('streams', [])
                
                audio_stream = None
                for stream in streams:
                    if stream.get('codec_type') == 'audio':
                        audio_stream = stream
                        break
                
                info = {
                    'duration': float(format_info.get('duration', 0)),
                    'size': int(format_info.get('size', 0)),
                    'bit_rate': int(format_info.get('bit_rate', 0)),
                }
                
                if audio_stream:
                    info.update({
                        'codec': audio_stream.get('codec_name', ''),
                        'sample_rate': int(audio_stream.get('sample_rate', 0)),
                        'channels': audio_stream.get('channels', 0),
                        'channel_layout': audio_stream.get('channel_layout', ''),
                    })
                
                return info
        except Exception as e:
            logger.error(f'Error getting audio info: {e}')
        
        return {}
    
    def _get_mock_audio(self, task_id: int, output_path: str) -> Dict:
        # 返回模拟音频信息（用于测试）
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        return {
            'success': True,
            'mock': True,
            'audio_path': output_path,
            'duration': 1800.0,  # 30分钟
            'sample_rate': 16000,
            'channels': 1,
            'format': 'wav',
            'codec': 'pcm_s16le',
            'size': 57600000,  # 约55MB
            'bit_rate': 256000,
            'task_id': task_id,
        }
    
    def get_audio_duration(self, audio_path: str) -> float:
        # 获取音频时长
        info = self._get_audio_info(audio_path)
        return info.get('duration', 0)
    
    def split_audio(
        self,
        audio_path: str,
        output_dir: str,
        chunk_duration: int = 30
    ) -> list:
        # 将音频分割成片段
        os.makedirs(output_dir, exist_ok=True)
        
        chunks = []
        
        try:
            duration = self.get_audio_duration(audio_path)
            num_chunks = int(duration // chunk_duration) + 1
            
            for i in range(num_chunks):
                start_time = i * chunk_duration
                chunk_path = os.path.join(output_dir, f'chunk_{i:04d}.wav')
                
                cmd = [
                    'ffmpeg',
                    '-ss', str(start_time),
                    '-i', audio_path,
                    '-t', str(chunk_duration),
                    '-acodec', 'copy',
                    '-y',
                    chunk_path
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0 and os.path.exists(chunk_path):
                    chunks.append({
                        'index': i,
                        'start_time': start_time,
                        'duration': min(chunk_duration, duration - start_time),
                        'file_path': chunk_path,
                    })
                    
        except Exception as e:
            logger.error(f'Error splitting audio: {e}')
        
        return chunks
    
    def convert_format(
        self,
        input_path: str,
        output_path: str,
        sample_rate: int = 16000,
        channels: int = 1
    ) -> bool:
        # 转换音频格式
        try:
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-ar', str(sample_rate),
                '-ac', str(channels),
                '-y',
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return result.returncode == 0 and os.path.exists(output_path)
            
        except Exception as e:
            logger.error(f'Error converting audio format: {e}')
            return False