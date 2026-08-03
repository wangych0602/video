import os
import json
import base64
import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

logger = logging.getLogger('ai_analysis.ai_provider')


class BaseAIProvider(ABC):
    # AI 提供商基类
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.api_key = self.config.get('api_key', '')
        self.endpoint = self.config.get('endpoint', '')
        self.model_name = self.config.get('model_name', '')
    
    @abstractmethod
    def analyze_image(self, image_path: str, prompt: str) -> Dict:
        # 分析图片
        pass
    
    @abstractmethod
    def analyze_video(self, video_path: str, prompt: str) -> Dict:
        # 分析视频
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict]) -> str:
        # 对话
        pass
    
    def _encode_image(self, image_path: str) -> str:
        # 将图片编码为 base64
        try:
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            logger.error(f'Error encoding image: {e}')
            return ''
    
    def _get_mock_analysis(self, prompt: str) -> Dict:
        # 返回模拟分析结果（用于测试）
        return {
            'success': True,
            'mock': True,
            'description': '这是一个模拟的AI分析结果',
            'confidence': 0.85,
            'prompt': prompt,
        }


class OpenAIProvider(BaseAIProvider):
    # OpenAI Vision 提供商
    
    def analyze_image(self, image_path: str, prompt: str) -> Dict:
        if not self.api_key:
            logger.warning('OpenAI API key not configured, using mock')
            return self._get_mock_analysis(prompt)
        
        try:
            import requests
            
            base64_image = self._encode_image(image_path)
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            payload = {
                'model': self.model_name or 'gpt-4-vision-preview',
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {'type': 'text', 'text': prompt},
                            {
                                'type': 'image_url',
                                'image_url': {
                                    'url': f'data:image/jpeg;base64,{base64_image}'
                                }
                            }
                        ]
                    }
                ],
                'max_tokens': 1000
            }
            
            base_url = self.endpoint or 'https://api.openai.com/v1'
            response = requests.post(
                f'{base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return {
                    'success': True,
                    'content': content,
                    'usage': result.get('usage', {}),
                }
            else:
                logger.error(f'OpenAI API error: {response.status_code} - {response.text}')
                return {'success': False, 'error': response.text}
                
        except ImportError:
            logger.warning('requests not available, using mock')
            return self._get_mock_analysis(prompt)
        except Exception as e:
            logger.error(f'Error analyzing image with OpenAI: {e}')
            return {'success': False, 'error': str(e)}
    
    def analyze_video(self, video_path: str, prompt: str) -> Dict:
        # OpenAI 视频分析（使用关键帧）
        return self._get_mock_analysis(prompt)
    
    def chat(self, messages: List[Dict]) -> str:
        if not self.api_key:
            return '这是模拟的回复内容。'
        
        try:
            import requests
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            payload = {
                'model': self.model_name or 'gpt-4',
                'messages': messages,
            }
            
            base_url = self.endpoint or 'https://api.openai.com/v1'
            response = requests.post(
                f'{base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f'OpenAI chat error: {response.status_code}')
                return ''
                
        except Exception as e:
            logger.error(f'Error chatting with OpenAI: {e}')
            return ''


class GeminiProvider(BaseAIProvider):
    # Gemini Vision 提供商
    
    def analyze_image(self, image_path: str, prompt: str) -> Dict:
        if not self.api_key:
            logger.warning('Gemini API key not configured, using mock')
            return self._get_mock_analysis(prompt)
        
        try:
            import requests
            
            base64_image = self._encode_image(image_path)
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            payload = {
                'contents': [
                    {
                        'parts': [
                            {'text': prompt},
                            {
                                'inline_data': {
                                    'mime_type': 'image/jpeg',
                                    'data': base64_image
                                }
                            }
                        ]
                    }
                ]
            }
            
            model = self.model_name or 'gemini-pro-vision'
            base_url = self.endpoint or 'https://generativelanguage.googleapis.com/v1'
            url = f'{base_url}/models/{model}:generateContent?key={self.api_key}'
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                return {
                    'success': True,
                    'content': content,
                }
            else:
                logger.error(f'Gemini API error: {response.status_code} - {response.text}')
                return {'success': False, 'error': response.text}
                
        except ImportError:
            logger.warning('requests not available, using mock')
            return self._get_mock_analysis(prompt)
        except Exception as e:
            logger.error(f'Error analyzing image with Gemini: {e}')
            return {'success': False, 'error': str(e)}
    
    def analyze_video(self, video_path: str, prompt: str) -> Dict:
        return self._get_mock_analysis(prompt)
    
    def chat(self, messages: List[Dict]) -> str:
        if not self.api_key:
            return '这是模拟的回复内容。'
        
        try:
            import requests
            
            headers = {'Content-Type': 'application/json'}
            
            contents = []
            for msg in messages:
                contents.append({
                    'role': 'model' if msg['role'] == 'assistant' else 'user',
                    'parts': [{'text': msg['content']}]
                })
            
            payload = {'contents': contents}
            
            model = self.model_name or 'gemini-pro'
            base_url = self.endpoint or 'https://generativelanguage.googleapis.com/v1'
            url = f'{base_url}/models/{model}:generateContent?key={self.api_key}'
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                logger.error(f'Gemini chat error: {response.status_code}')
                return ''
                
        except Exception as e:
            logger.error(f'Error chatting with Gemini: {e}')
            return ''


class ClaudeProvider(BaseAIProvider):
    # Claude Vision 提供商
    
    def analyze_image(self, image_path: str, prompt: str) -> Dict:
        if not self.api_key:
            logger.warning('Claude API key not configured, using mock')
            return self._get_mock_analysis(prompt)
        
        try:
            import requests
            
            base64_image = self._encode_image(image_path)
            
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': self.api_key,
                'anthropic-version': '2023-06-01',
            }
            
            payload = {
                'model': self.model_name or 'claude-3-opus-20240229',
                'max_tokens': 1000,
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'image',
                                'source': {
                                    'type': 'base64',
                                    'media_type': 'image/jpeg',
                                    'data': base64_image
                                }
                            },
                            {
                                'type': 'text',
                                'text': prompt
                            }
                        ]
                    }
                ]
            }
            
            base_url = self.endpoint or 'https://api.anthropic.com/v1'
            response = requests.post(
                f'{base_url}/messages',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['content'][0]['text']
                return {
                    'success': True,
                    'content': content,
                    'usage': result.get('usage', {}),
                }
            else:
                logger.error(f'Claude API error: {response.status_code} - {response.text}')
                return {'success': False, 'error': response.text}
                
        except ImportError:
            logger.warning('requests not available, using mock')
            return self._get_mock_analysis(prompt)
        except Exception as e:
            logger.error(f'Error analyzing image with Claude: {e}')
            return {'success': False, 'error': str(e)}
    
    def analyze_video(self, video_path: str, prompt: str) -> Dict:
        return self._get_mock_analysis(prompt)
    
    def chat(self, messages: List[Dict]) -> str:
        if not self.api_key:
            return '这是模拟的回复内容。'
        
        try:
            import requests
            
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': self.api_key,
                'anthropic-version': '2023-06-01',
            }
            
            payload = {
                'model': self.model_name or 'claude-3-sonnet-20240229',
                'max_tokens': 1000,
                'messages': messages,
            }
            
            base_url = self.endpoint or 'https://api.anthropic.com/v1'
            response = requests.post(
                f'{base_url}/messages',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text']
            else:
                logger.error(f'Claude chat error: {response.status_code}')
                return ''
                
        except Exception as e:
            logger.error(f'Error chatting with Claude: {e}')
            return ''


class LocalProvider(BaseAIProvider):
    # 本地模型提供商
    
    def analyze_image(self, image_path: str, prompt: str) -> Dict:
        logger.info('Using local provider (mock)')
        return self._get_mock_analysis(prompt)
    
    def analyze_video(self, video_path: str, prompt: str) -> Dict:
        return self._get_mock_analysis(prompt)
    
    def chat(self, messages: List[Dict]) -> str:
        return '这是本地模型的模拟回复。'


# Provider 工厂
PROVIDER_MAP = {
    'openai': OpenAIProvider,
    'gemini': GeminiProvider,
    'claude': ClaudeProvider,
    'local': LocalProvider,
}


def get_provider(provider_type: str, config: Dict = None) -> BaseAIProvider:
    # 获取指定类型的 provider
    provider_class = PROVIDER_MAP.get(provider_type, LocalProvider)
    return provider_class(config or {})


def get_active_provider() -> BaseAIProvider:
    # 获取当前启用的 provider
    try:
        from ai_analysis.models import AIModelConfig
        
        active_config = AIModelConfig.objects.filter(status=True).first()
        
        if active_config:
            config = {
                'api_key': active_config.api_key,
                'endpoint': active_config.endpoint,
                'model_name': active_config.model_name,
            }
            return get_provider(active_config.provider, config)
    except Exception as e:
        logger.error(f'Error getting active provider: {e}')
    
    # 默认使用本地 mock provider
    return LocalProvider()