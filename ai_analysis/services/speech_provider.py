import os
import json
import base64
import logging
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger('ai_analysis.speech_provider')


class BaseSpeechProvider(ABC):
    # 语音识别提供商基类
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.api_key = self.config.get('api_key', '')
        self.endpoint = self.config.get('endpoint', '')
        self.model_name = self.config.get('model_name', '')
    
    @abstractmethod
    def transcribe(self, audio_path: str, language: str = None) -> Dict:
        # 语音转文字
        pass
    
    def _get_mock_transcription(self, audio_path: str, language: str = None) -> Dict:
        # 返回模拟转写结果（用于测试）
        filename = os.path.basename(audio_path) if audio_path else 'audio.wav'
        
        segments = [
            {
                'id': 0,
                'start': 0.0,
                'end': 30.0,
                'text': '同学们好，今天我们来学习新的一课。首先，请大家回顾一下上节课的内容。',
                'speaker': 'teacher',
            },
            {
                'id': 1,
                'start': 30.0,
                'end': 90.0,
                'text': '好的，我们开始今天的新课。今天主要讲三个知识点：第一是基本概念，第二是应用方法，第三是典型例题。',
                'speaker': 'teacher',
            },
            {
                'id': 2,
                'start': 90.0,
                'end': 180.0,
                'text': '我们先来看第一个知识点，基本概念。什么是这个概念呢？简单来说，它是指...',
                'speaker': 'teacher',
            },
            {
                'id': 3,
                'start': 180.0,
                'end': 240.0,
                'text': '老师，我有一个问题。这个概念和我们之前学的有什么区别呢？',
                'speaker': 'student',
            },
            {
                'id': 4,
                'start': 240.0,
                'end': 360.0,
                'text': '这个问题问得很好。它们的区别主要在于...大家要注意这一点，这是考试的重点。',
                'speaker': 'teacher',
            },
            {
                'id': 5,
                'start': 360.0,
                'end': 600.0,
                'text': '好，接下来我们看第二个知识点，应用方法。这个方法有五个步骤，大家记一下：第一步...第二步...第三步...',
                'speaker': 'teacher',
            },
            {
                'id': 6,
                'start': 600.0,
                'end': 900.0,
                'text': '现在我们来看一道典型例题。这道题是去年的考题，大家先自己思考一下，然后我们一起来解答。',
                'speaker': 'teacher',
            },
            {
                'id': 7,
                'start': 900.0,
                'end': 1200.0,
                'text': '好，时间到了。我们一起来看这道题。首先，题目要求我们...第一步应该...第二步...第三步...最后得出结论。',
                'speaker': 'teacher',
            },
            {
                'id': 8,
                'start': 1200.0,
                'end': 1500.0,
                'text': '大家都听懂了吗？有问题的话可以举手提问。好，这位同学你说。',
                'speaker': 'teacher',
            },
            {
                'id': 9,
                'start': 1500.0,
                'end': 1620.0,
                'text': '老师，第三步我还是不太明白，能再讲一下吗？',
                'speaker': 'student',
            },
            {
                'id': 10,
                'start': 1620.0,
                'end': 1740.0,
                'text': '好的，我再讲一遍。第三步是关键，大家要注意...这样理解了吗？好的。',
                'speaker': 'teacher',
            },
            {
                'id': 11,
                'start': 1740.0,
                'end': 1800.0,
                'text': '好，今天的课就到这里。课后大家完成作业，预习下一节课的内容。下课。',
                'speaker': 'teacher',
            },
        ]
        
        full_text = ' '.join([seg['text'] for seg in segments])
        
        return {
            'success': True,
            'mock': True,
            'text': full_text,
            'segments': segments,
            'language': language or 'zh',
            'duration': 1800.0,
            'word_count': len(full_text),
            'filename': filename,
        }


class OpenAIWhisperProvider(BaseSpeechProvider):
    # OpenAI Whisper 语音识别
    
    def transcribe(self, audio_path: str, language: str = None) -> Dict:
        if not self.api_key:
            logger.warning('OpenAI API key not configured, using mock')
            return self._get_mock_transcription(audio_path, language)
        
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
            }
            
            with open(audio_path, 'rb') as audio_file:
                files = {
                    'file': audio_file,
                    'model': (None, self.model_name or 'whisper-1'),
                    'response_format': (None, 'verbose_json'),
                }
                if language:
                    files['language'] = (None, language)
                
                base_url = self.endpoint or 'https://api.openai.com/v1'
                response = requests.post(
                    f'{base_url}/audio/transcriptions',
                    headers=headers,
                    files=files,
                    timeout=300
                )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'text': result.get('text', ''),
                    'segments': result.get('segments', []),
                    'language': result.get('language', language or 'zh'),
                    'duration': result.get('duration', 0),
                }
            else:
                logger.error(f'OpenAI Whisper error: {response.status_code} - {response.text}')
                return {'success': False, 'error': response.text}
                
        except ImportError:
            logger.warning('requests not available, using mock')
            return self._get_mock_transcription(audio_path, language)
        except Exception as e:
            logger.error(f'Error transcribing with OpenAI Whisper: {e}')
            return {'success': False, 'error': str(e)}


class GeminiSpeechProvider(BaseSpeechProvider):
    # Gemini 语音识别
    
    def transcribe(self, audio_path: str, language: str = None) -> Dict:
        if not self.api_key:
            logger.warning('Gemini API key not configured, using mock')
            return self._get_mock_transcription(audio_path, language)
        
        try:
            import requests
            
            # 读取音频文件并编码
            with open(audio_path, 'rb') as f:
                audio_data = base64.b64encode(f.read()).decode('utf-8')
            
            headers = {'Content-Type': 'application/json'}
            
            prompt = f'''请将这段音频转写为文字。
请按时间分段，每段包含开始时间、结束时间和文字内容。
请识别说话人（教师/学生）。
请以JSON格式返回，包含以下字段：
- text: 完整文字稿
- segments: 分段列表，每个包含start, end, text, speaker
- language: 语言
- duration: 时长（秒）'''
            
            payload = {
                'contents': [
                    {
                        'parts': [
                            {'text': prompt},
                            {
                                'inline_data': {
                                    'mime_type': 'audio/wav',
                                    'data': audio_data
                                }
                            }
                        ]
                    }
                ]
            }
            
            model = self.model_name or 'gemini-1.5-pro'
            base_url = self.endpoint or 'https://generativelanguage.googleapis.com/v1'
            url = f'{base_url}/models/{model}:generateContent?key={self.api_key}'
            
            response = requests.post(url, headers=headers, json=payload, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                
                # 尝试解析 JSON
                try:
                    # 提取 JSON 部分
                    import re
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        parsed = json.loads(json_match.group())
                        return {
                            'success': True,
                            'text': parsed.get('text', content),
                            'segments': parsed.get('segments', []),
                            'language': parsed.get('language', language or 'zh'),
                            'duration': parsed.get('duration', 0),
                        }
                except:
                    pass
                
                return {
                    'success': True,
                    'text': content,
                    'segments': [],
                    'language': language or 'zh',
                    'duration': 0,
                }
            else:
                logger.error(f'Gemini Speech error: {response.status_code} - {response.text}')
                return {'success': False, 'error': response.text}
                
        except ImportError:
            logger.warning('requests not available, using mock')
            return self._get_mock_transcription(audio_path, language)
        except Exception as e:
            logger.error(f'Error transcribing with Gemini: {e}')
            return {'success': False, 'error': str(e)}


class AzureSpeechProvider(BaseSpeechProvider):
    # Azure 语音识别
    
    def transcribe(self, audio_path: str, language: str = None) -> Dict:
        if not self.api_key:
            logger.warning('Azure API key not configured, using mock')
            return self._get_mock_transcription(audio_path, language)
        
        try:
            import requests
            
            region = self.config.get('region', 'eastasia')
            lang = language or 'zh-CN'
            
            # 获取 token
            token_url = f'https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken'
            token_headers = {
                'Ocp-Apim-Subscription-Key': self.api_key,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            token_response = requests.post(token_url, headers=token_headers, timeout=30)
            
            if token_response.status_code != 200:
                logger.error(f'Azure token error: {token_response.status_code}')
                return self._get_mock_transcription(audio_path, language)
            
            token = token_response.text
            
            # 语音识别
            speech_url = f'https://{region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language={lang}&format=detailed'
            
            speech_headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'audio/wav; codecs=audio/pcm; samplerate=16000',
                'Accept': 'application/json',
            }
            
            with open(audio_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            response = requests.post(
                speech_url,
                headers=speech_headers,
                data=audio_data,
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'text': result.get('DisplayText', ''),
                    'segments': [],
                    'language': lang,
                    'duration': 0,
                }
            else:
                logger.error(f'Azure Speech error: {response.status_code} - {response.text}')
                return {'success': False, 'error': response.text}
                
        except ImportError:
            logger.warning('requests not available, using mock')
            return self._get_mock_transcription(audio_path, language)
        except Exception as e:
            logger.error(f'Error transcribing with Azure Speech: {e}')
            return {'success': False, 'error': str(e)}


class LocalWhisperProvider(BaseSpeechProvider):
    # 本地 Whisper 语音识别
    
    def transcribe(self, audio_path: str, language: str = None) -> Dict:
        try:
            # 尝试使用 whisper 库
            import whisper
            
            model_name = self.model_name or 'base'
            model = whisper.load_model(model_name)
            
            result = model.transcribe(
                audio_path,
                language=language,
                verbose=False
            )
            
            segments = []
            for i, seg in enumerate(result.get('segments', [])):
                segments.append({
                    'id': i,
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': seg['text'].strip(),
                    'speaker': 'unknown',
                })
            
            return {
                'success': True,
                'text': result.get('text', ''),
                'segments': segments,
                'language': result.get('language', language or 'zh'),
                'duration': result.get('duration', 0),
            }
            
        except ImportError:
            logger.warning('whisper not installed, using mock')
            return self._get_mock_transcription(audio_path, language)
        except Exception as e:
            logger.error(f'Error transcribing with local Whisper: {e}')
            return self._get_mock_transcription(audio_path, language)


# Provider 工厂
SPEECH_PROVIDER_MAP = {
    'openai_whisper': OpenAIWhisperProvider,
    'gemini_speech': GeminiSpeechProvider,
    'azure_speech': AzureSpeechProvider,
    'local_whisper': LocalWhisperProvider,
}


def get_speech_provider(provider_type: str, config: Dict = None) -> BaseSpeechProvider:
    # 获取指定类型的语音识别 provider
    provider_class = SPEECH_PROVIDER_MAP.get(provider_type, LocalWhisperProvider)
    return provider_class(config or {})


def get_active_speech_provider() -> BaseSpeechProvider:
    # 获取当前启用的语音识别 provider
    try:
        from ai_analysis.models import AIModelConfig
        
        # 查找语音识别相关的配置
        active_config = AIModelConfig.objects.filter(
            status=True,
            provider__in=['openai_whisper', 'gemini_speech', 'azure_speech', 'local_whisper']
        ).first()
        
        if active_config:
            config = {
                'api_key': active_config.api_key,
                'endpoint': active_config.endpoint,
                'model_name': active_config.model_name,
            }
            return get_speech_provider(active_config.provider, config)
    except Exception as e:
        logger.error(f'Error getting active speech provider: {e}')
    
    # 默认使用本地 mock provider
    return LocalWhisperProvider()