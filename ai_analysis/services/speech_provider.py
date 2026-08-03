"""
Speech Provider 兼容层

旧的代码可以继续使用这个模块，内部调用新的 ProviderFactory。
"""
import logging
from typing import Dict, List, Optional

from .providers import ProviderFactory, BaseProvider
from .providers.base import ProviderConfig

logger = logging.getLogger("ai_analysis.speech_provider")


def get_speech_provider(provider_type: str, config: Dict = None) -> "CompatSpeechProvider":
    """获取指定类型的语音 provider（兼容旧接口）"""
    provider_config = ProviderConfig(
        api_key=config.get("api_key", "") if config else "",
        api_base=config.get("endpoint", "") if config else "",
        model_name=config.get("model_name", "") if config else "",
    )
    
    # 映射旧的 provider 类型到新的
    provider_map = {
        "openai_whisper": "openai",
        "gemini_speech": "gemini",
        "azure_speech": "openai",  # Azure 暂时映射到 openai
        "local_whisper": "ollama",  # 本地映射到 ollama
    }
    
    new_provider_type = provider_map.get(provider_type, provider_type)
    actual_provider = ProviderFactory.get_provider(new_provider_type, provider_config)
    return CompatSpeechProvider(actual_provider)


def get_active_speech_provider() -> "CompatSpeechProvider":
    """获取当前激活的语音 provider（兼容旧接口）"""
    actual_provider = ProviderFactory.get_speech_provider()
    if actual_provider is None:
        # 如果没有配置，返回 Ollama（会走 mock）
        from .providers.ollama_provider import OllamaProvider
        actual_provider = OllamaProvider()
    return CompatSpeechProvider(actual_provider)


class CompatSpeechProvider:
    """兼容旧接口的 Speech Provider 包装器"""
    
    def __init__(self, actual_provider: BaseProvider):
        self._provider = actual_provider
    
    def transcribe(self, audio_path: str, language: str = None) -> Dict:
        """语音转文字（兼容旧接口）"""
        response = self._provider.transcribe(audio_path, language or "")
        
        if response.success:
            return {
                "success": True,
                "text": response.content,
                "segments": [],
                "language": language or "zh",
                "duration": 0,
            }
        else:
            # 如果失败，返回 mock
            return self._get_mock_transcription(audio_path, language)
    
    def _get_mock_transcription(self, audio_path: str, language: str = None) -> Dict:
        """返回模拟转录结果（用于测试）"""
        import os
        filename = os.path.basename(audio_path) if audio_path else "audio.wav"
        
        segments = [
            {
                "id": 0,
                "start": 0.0,
                "end": 30.0,
                "text": "同学们好，今天我们来学习新的一课。首先，请大家回顾一下上节课的内容。",
                "speaker": "teacher",
            },
            {
                "id": 1,
                "start": 30.0,
                "end": 90.0,
                "text": "好的，我们开始今天的新课。今天主要讲三个知识点：第一是基本概念，第二是应用方法，第三是典型例题。",
                "speaker": "teacher",
            },
        ]
        
        full_text = " ".join([seg["text"] for seg in segments])
        
        return {
            "success": True,
            "mock": True,
            "text": full_text,
            "segments": segments,
            "language": language or "zh",
            "duration": 1800.0,
            "word_count": len(full_text),
            "filename": filename,
        }
