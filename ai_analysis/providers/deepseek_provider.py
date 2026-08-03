import logging
from typing import List
from .base import BaseProvider, ProviderConfig, ChatMessage, ProviderResponse

logger = logging.getLogger("ai_analysis.providers.deepseek")


class DeepSeekProvider(BaseProvider):
    """DeepSeek Provider
    
    支持:
    - 文本对话
    """
    
    provider_type = "deepseek"
    
    capabilities = {
        "chat": True,
        "vision": False,
        "speech_to_text": False,
        "text_to_speech": False,
        "embedding": True,
    }
    
    DEFAULT_MODEL = "deepseek-chat"
    DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
    
    def _get_base_url(self) -> str:
        return self.config.api_base or self.DEFAULT_BASE_URL
    
    def _get_model(self) -> str:
        return self.config.model_name or self.DEFAULT_MODEL
    
    def chat(self, messages: List[ChatMessage]) -> ProviderResponse:
        if not self.config.api_key:
            logger.warning("DeepSeek API key not configured, using mock")
            return self._get_mock_response("DeepSeek chat")
        
        try:
            import requests
            
            # 构建消息 (OpenAI 兼容格式)
            deepseek_messages = []
            for msg in messages:
                deepseek_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}"
            }
            
            payload = {
                "model": self._get_model(),
                "messages": deepseek_messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            }
            
            response = requests.post(
                f"{self._get_base_url()}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return ProviderResponse(
                    success=True,
                    content=result["choices"][0]["message"]["content"],
                    usage=result.get("usage", {}),
                    raw_response=result
                )
            else:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return ProviderResponse(
                    success=False,
                    error=f"API error: {response.status_code}",
                    raw_response=response.text
                )
                
        except ImportError:
            logger.warning("requests not available, using mock")
            return self._get_mock_response("DeepSeek chat")
        except Exception as e:
            logger.error(f"Error in DeepSeek chat: {e}")
            return ProviderResponse(success=False, error=str(e))
