"""
AI Provider 兼容层

旧的代码可以继续使用这个模块，内部调用新的 ProviderFactory。
"""
import logging
from typing import Dict, List, Optional

from .providers import ProviderFactory, BaseProvider
from .providers.base import ProviderConfig, ChatMessage, ProviderResponse

logger = logging.getLogger("ai_analysis.ai_provider")


# 兼容旧的接口
def get_provider(provider_type: str, config: Dict = None) -> "CompatProvider":
    """获取指定类型的 provider（兼容旧接口）"""
    provider_config = ProviderConfig(
        api_key=config.get("api_key", "") if config else "",
        api_base=config.get("endpoint", "") if config else "",
        model_name=config.get("model_name", "") if config else "",
    )
    actual_provider = ProviderFactory.get_provider(provider_type, provider_config)
    return CompatProvider(actual_provider)


def get_active_provider() -> "CompatProvider":
    """获取当前激活的 provider（兼容旧接口）"""
    actual_provider = ProviderFactory.get_chat_provider()
    if actual_provider is None:
        # 如果没有配置，返回 Ollama（会走 mock）
        from .providers.ollama_provider import OllamaProvider
        actual_provider = OllamaProvider()
    return CompatProvider(actual_provider)


class CompatProvider:
    """兼容旧接口的 Provider 包装器"""
    
    def __init__(self, actual_provider: BaseProvider):
        self._provider = actual_provider
    
    def analyze_image(self, image_path: str, prompt: str) -> Dict:
        """分析图片（兼容旧接口）"""
        response = self._provider.analyze_image(image_path, prompt)
        return self._convert_response(response)
    
    def analyze_video(self, video_path: str, prompt: str) -> Dict:
        """分析视频（兼容旧接口）"""
        response = self._provider._get_mock_response(prompt)
        return self._convert_response(response)
    
    def chat(self, messages: List[Dict]) -> str:
        """对话（兼容旧接口）"""
        # 转换消息格式
        chat_messages = []
        for msg in messages:
            chat_messages.append(ChatMessage(
                role=msg.get("role", "user"),
                content=msg.get("content", "")
            ))
        
        response = self._provider.chat(chat_messages)
        return response.content if response.success else ""
    
    def _convert_response(self, response: ProviderResponse) -> Dict:
        """将新的响应格式转换为旧格式"""
        result = {
            "success": response.success,
            "content": response.content,
            "usage": response.usage,
        }
        
        if response.error:
            result["error"] = response.error
        
        if response.raw_response and isinstance(response.raw_response, dict) and response.raw_response.get("mock"):
            result["mock"] = True
        
        return result
