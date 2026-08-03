import logging
import base64
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger("ai_analysis.providers.base")


@dataclass
class ProviderConfig:
    """Provider 配置"""
    api_key: str = ""
    api_base: str = ""
    model_name: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 60
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # user / assistant / system
    content: str
    images: List[str] = field(default_factory=list)  # 图片路径列表


@dataclass
class ProviderResponse:
    """Provider 统一响应"""
    success: bool
    content: str = ""
    usage: Dict[str, int] = field(default_factory=dict)
    error: str = ""
    raw_response: Any = None


class BaseProvider(ABC):
    """AI Provider 基类
    
    所有 Provider 必须继承此类，实现统一的接口。
    """
    
    # Provider 类型标识
    provider_type: str = "base"
    
    # 支持的能力
    capabilities = {
        "chat": False,        # 文本对话
        "vision": False,      # 视觉分析
        "speech_to_text": False,  # 语音转文字
        "text_to_speech": False,  # 文字转语音
        "embedding": False,   # 向量嵌入
    }
    
    def __init__(self, config: ProviderConfig = None):
        self.config = config or ProviderConfig()
        self._validate_config()
    
    def _validate_config(self):
        """验证配置"""
        if not self.config.api_key and self.provider_type != "ollama":
            logger.warning(f"{self.provider_type} API key not configured")
    
    def _encode_image_base64(self, image_path: str) -> str:
        """将图片编码为 base64"""
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            return ""
    
    def _get_mock_response(self, prompt: str = "") -> ProviderResponse:
        """返回模拟响应（用于测试）"""
        return ProviderResponse(
            success=True,
            content=f"[Mock Response] This is a mock response for: {prompt[:50]}...",
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            raw_response={"mock": True}
        )
    
    @abstractmethod
    def chat(self, messages: List[ChatMessage]) -> ProviderResponse:
        """文本对话
        
        Args:
            messages: 消息列表
            
        Returns:
            ProviderResponse: 统一响应
        """
        pass
    
    def chat_completion(self, prompt: str, system_prompt: str = "") -> ProviderResponse:
        """简单的单轮对话（便捷方法）
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            
        Returns:
            ProviderResponse: 统一响应
        """
        messages = []
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))
        messages.append(ChatMessage(role="user", content=prompt))
        return self.chat(messages)
    
    def analyze_image(self, image_path: str, prompt: str) -> ProviderResponse:
        """图片分析
        
        Args:
            image_path: 图片路径
            prompt: 分析提示
            
        Returns:
            ProviderResponse: 统一响应
        """
        if not self.capabilities.get("vision", False):
            return ProviderResponse(
                success=False,
                error=f"{self.provider_type} does not support vision"
            )
        
        message = ChatMessage(role="user", content=prompt, images=[image_path])
        return self.chat([message])
    
    def transcribe(self, audio_path: str, language: str = "") -> ProviderResponse:
        """语音转文字
        
        Args:
            audio_path: 音频路径
            language: 语言代码
            
        Returns:
            ProviderResponse: 统一响应
        """
        return ProviderResponse(
            success=False,
            error=f"{self.provider_type} does not support speech_to_text"
        )
    
    def get_capabilities(self) -> Dict[str, bool]:
        """获取支持的能力"""
        return self.capabilities.copy()
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            response = self.chat_completion("Hello")
            return response.success
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
