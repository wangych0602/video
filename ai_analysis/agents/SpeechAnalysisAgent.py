import os
import re
import logging
from typing import Dict, List, Any
from collections import Counter

from .BaseAgent import BaseAgent
from ..services.audio_processor import AudioProcessor
from ..services.speech_provider import get_active_speech_provider

logger = logging.getLogger('ai_analysis.speech_agent')


class SpeechAnalysisAgent(BaseAgent):
    # 语音分析Agent
    
    name = 'speech_analysis'
    description = '分析课堂音频，包括语音转文字、关键词提取、知识点提取、语速分析等'
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.audio_processor = AudioProcessor()
        self.speech_provider = get_active_speech_provider()
        self.language = self.config.get('language', 'zh')
    
    def validate_input(self, input_data: Dict) -> bool:
        # 验证输入数据
        if not input_data.get('video_id'):
            return False
        return True
    
    def run(self, input_data: Dict) -> Dict:
        # 执行语音分析
        try:
            self.log_info('Starting speech analysis...')
            
            video_path = input_data.get('video_path', '')
            task_id = input_data.get('task_id', 0)
            
            if not video_path or not os.path.exists(video_path):
                self.log_info('Video file not found, using mock analysis')
                return self._get_mock_result(input_data)
            
            # 1. 提取音频 (35% - 40%)
            self._update_progress(35, '提取音频')
            audio_result = self.audio_processor.extract_audio(
                video_path,
                task_id,
                sample_rate=16000,
                channels=1
            )
            
            if not audio_result.get('success'):
                self.log_info(f'Audio extraction failed: {audio_result.get("error")}')
                return self._get_mock_result(input_data)
            
            audio_path = audio_result.get('audio_path', '')
            audio_duration = audio_result.get('duration', 0)
            self.set_result('audio_info', audio_result)
            self.log_info(f'Audio extracted: {audio_duration}s')
            
            # 2. 语音识别 (40% - 45%)
            self._update_progress(40, '语音识别中')
            transcription = self.speech_provider.transcribe(
                audio_path,
                language=self.language
            )
            
            if not transcription.get('success'):
                self.log_info(f'Speech recognition failed: {transcription.get("error")}')
                return self._get_mock_result(input_data)
            
            self.set_result('transcription', transcription)
            self.log_info(f'Transcription completed: {len(transcription.get("text", ""))} chars')
            
            # 3. 关键词提取 (45% - 47%)
            self._update_progress(45, '提取关键词')
            keywords = self._extract_keywords(transcription.get('text', ''))
            self.set_result('keywords', keywords)
            self.log_info(f'Extracted {len(keywords)} keywords')
            
            # 4. 知识点提取 (47% - 49%)
            self._update_progress(47, '提取知识点')
            knowledge_points = self._extract_knowledge_points(transcription.get('text', ''))
            self.set_result('knowledge_points', knowledge_points)
            self.log_info(f'Extracted {len(knowledge_points)} knowledge points')
            
            # 5. 语速分析 (49% - 50%)
            self._update_progress(49, '分析语速')
            speaking_rate = self._analyze_speaking_rate(
                transcription.get('text', ''),
                audio_duration
            )
            self.set_result('speaking_rate', speaking_rate)
            
            # 6. 语音片段分析
            speech_segments = self._analyze_segments(transcription.get('segments', []))
            self.set_result('speech_segments', speech_segments)
            
            # 合并结果
            result = self.result
            result['success'] = True
            result['transcript'] = transcription.get('text', '')
            result['speech_segments'] = speech_segments
            result['audio_duration'] = audio_duration
            result['word_count'] = len(transcription.get('text', ''))
            
            self._update_progress(50, '语音分析完成')
            self.log_info('Speech analysis completed successfully')
            
            return result
            
        except Exception as e:
            self.log_info(f'Speech analysis failed: {e}')
            return self.handle_error(e)
    
    def _extract_keywords(self, text: str, top_n: int = 20) -> List[Dict]:
        # 提取关键词
        if not text:
            return []
        
        # 简单的关键词提取（基于词频和停用词过滤）
        # 中文分词简化版：按常见模式提取
        keywords = []
        
        # 提取课程相关词汇
        course_patterns = [
            r'第[一二三四五六七八九十\d]+[章节知识点]',
            r'[一二三四五六七八九十\d]+、',
            r'首先|其次|然后|接着|最后|第一|第二|第三',
            r'重点|难点|关键|核心|基础|概念|定义',
            r'公式|定理|定律|原理|方法|步骤',
            r'例题|练习|作业|考试|考题',
        ]
        
        found_keywords = set()
        
        for pattern in course_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) >= 2 and len(match) <= 20:
                    found_keywords.add(match)
        
        # 提取数字+单位的组合
        number_patterns = re.findall(r'\d+[%％个条项点步]', text)
        found_keywords.update(number_patterns[:10])
        
        # 按出现频率排序
        word_freq = Counter()
        for word in found_keywords:
            word_freq[word] = text.count(word)
        
        # 生成关键词列表
        for word, freq in word_freq.most_common(top_n):
            keywords.append({
                'word': word,
                'count': freq,
                'weight': min(freq / 5, 1.0),
            })
        
        # 如果关键词太少，添加一些默认的
        if len(keywords) < 5:
            default_keywords = [
                {'word': '课堂教学', 'count': 1, 'weight': 0.5},
                {'word': '知识点讲解', 'count': 1, 'weight': 0.5},
                {'word': '例题分析', 'count': 1, 'weight': 0.5},
                {'word': '师生互动', 'count': 1, 'weight': 0.5},
                {'word': '课程总结', 'count': 1, 'weight': 0.5},
            ]
            keywords.extend(default_keywords[:5 - len(keywords)])
        
        return keywords
    
    def _extract_knowledge_points(self, text: str) -> List[Dict]:
        # 提取知识点
        if not text:
            return []
        
        knowledge_points = []
        
        # 识别知识点的模式
        patterns = [
            (r'第[一二三四五六七八九十\d]+[章节][：:](.*?)[。，,；;]', 'chapter'),
            (r'知识点[一二三四五六七八九十\d]*[：:](.*?)[。，,；;]', 'knowledge'),
            (r'[我们大家][来]?[看学习讲](.*?)[。，,；;]', 'topic'),
            (r'首先(.*?)[。，,；;]', 'first'),
            (r'其次(.*?)[。，,；;]', 'second'),
            (r'然后(.*?)[。，,；;]', 'then'),
            (r'最后(.*?)[。，,；;]', 'last'),
        ]
        
        found_points = set()
        
        for pattern, ptype in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ''
                match = match.strip()
                if 2 <= len(match) <= 50 and match not in found_points:
                    found_points.add(match)
                    knowledge_points.append({
                        'point': match,
                        'type': ptype,
                        'importance': 'high' if ptype in ['chapter', 'knowledge'] else 'medium',
                    })
        
        # 如果知识点太少，添加一些模拟的
        if len(knowledge_points) < 3:
            mock_points = [
                {'point': '基本概念与定义', 'type': 'concept', 'importance': 'high'},
                {'point': '核心原理与公式', 'type': 'principle', 'importance': 'high'},
                {'point': '典型例题解析', 'type': 'example', 'importance': 'medium'},
                {'point': '解题方法与步骤', 'type': 'method', 'importance': 'high'},
                {'point': '常见误区与注意事项', 'type': 'warning', 'importance': 'medium'},
            ]
            knowledge_points.extend(mock_points[:5 - len(knowledge_points)])
        
        return knowledge_points[:10]
    
    def _analyze_speaking_rate(self, text: str, duration: float) -> Dict:
        # 分析语速
        if not text or duration <= 0:
            return {
                'words_per_minute': 0,
                'chars_per_minute': 0,
                'pace': 'unknown',
                'description': '无法分析语速',
            }
        
        # 中文字符数
        char_count = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        # 词数（中文按字符估算）
        word_count = char_count
        
        # 每分钟字数
        chars_per_minute = int(char_count / (duration / 60)) if duration > 0 else 0
        words_per_minute = int(word_count / (duration / 60)) if duration > 0 else 0
        
        # 判断语速
        if chars_per_minute < 150:
            pace = 'slow'
            description = '语速较慢，适合学生理解'
        elif chars_per_minute < 250:
            pace = 'normal'
            description = '语速适中，表达清晰'
        elif chars_per_minute < 350:
            pace = 'fast'
            description = '语速较快，需要注意学生接受度'
        else:
            pace = 'very_fast'
            description = '语速过快，建议适当放慢'
        
        return {
            'words_per_minute': words_per_minute,
            'chars_per_minute': chars_per_minute,
            'total_chars': char_count,
            'total_words': word_count,
            'duration_seconds': duration,
            'pace': pace,
            'description': description,
        }
    
    def _analyze_segments(self, segments: List[Dict]) -> List[Dict]:
        # 分析语音片段
        result = []
        
        for seg in segments:
            segment = {
                'id': seg.get('id', 0),
                'start': seg.get('start', 0),
                'end': seg.get('end', 0),
                'duration': round(seg.get('end', 0) - seg.get('start', 0), 2),
                'text': seg.get('text', ''),
                'speaker': seg.get('speaker', 'unknown'),
            }
            
            # 计算该片段的语速
            text = seg.get('text', '')
            duration = seg.get('end', 0) - seg.get('start', 0)
            if duration > 0 and text:
                char_count = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
                segment['chars_per_minute'] = int(char_count / (duration / 60))
            
            result.append(segment)
        
        return result
    
    def _update_progress(self, progress: int, step: str = ''):
        # 更新进度
        self.set_result('progress', progress)
        self.set_result('current_step', step)
    
    def _get_mock_result(self, input_data: Dict) -> Dict:
        # 返回模拟结果
        video_id = input_data.get('video_id', 0)
        
        mock_transcription = self.speech_provider._get_mock_transcription('', self.language)
        
        return {
            'success': True,
            'mock': True,
            'video_id': video_id,
            'transcript': mock_transcription['text'],
            'speech_segments': mock_transcription['segments'],
            'keywords': self._extract_keywords(mock_transcription['text']),
            'knowledge_points': self._extract_knowledge_points(mock_transcription['text']),
            'speaking_rate': self._analyze_speaking_rate(
                mock_transcription['text'],
                mock_transcription['duration']
            ),
            'audio_info': {
                'duration': 1800,
                'sample_rate': 16000,
                'channels': 1,
                'format': 'wav',
                'mock': True,
            },
            'word_count': len(mock_transcription['text']),
            'audio_duration': 1800,
        }