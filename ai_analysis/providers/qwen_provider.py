import logging
from typing import List
from .base import BaseProvider, ProviderConfig, ChatMessage, ProviderResponse

logger = logging.getLogger("ai_analysis.providers.qwen")


class QwenProvider(BaseProvider):
    """阿里通义千问 Provider
    
    支持:
    - 文本对话
    - 视觉分析 (Qwen-VL)
    """
    
    provider_type = "qwen"
    
    capabilities = {
        "chat": True,
        "vision": True,
        "speech_to_text": False,
        "text_to_speech": False,
        "embedding": True,
    }
    
    DEFAULT_MODEL = "qwen-plus"
    DEFAULT_VISION_MODEL = "qwen-vl-plus"
    DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    def _get_base_url(self) -> str:
        return self.config.api_base or self.DEFAULT_BASE_URL
    
    def _get_model(self, vision: bool = False) -> str:
        if self.config.model_name:
            return self.config.model_name
        return self.DEFAULT_VISION_MODEL if vision else self.DEFAULT_MODEL
    
    def chat(self, messages: List[ChatMessage]) -> ProviderResponse:
        if not self.config.api_key:
            logger.warning("Qwen API key not configured, using mock")
            return self._get_mock_response("Qwen chat")
        
        try:
            import requests
            
            has_images = any(msg.images for msg in messages)
            model = self._get_model(vision=has_images)
            
            # 构建消息 (OpenAI 兼容格式)
            qwen_messages = []
            for msg in messages:
                content = []
                if msg.content:
                    content.append({"type": "text", "text": msg.content})
                
                # 添加图片
                for img_path in msg.images:
                    base64_img = self._encode_image_base64(img_path)
                    if base64_img:
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_img}"
                            }
                        })
                
                qwen_messages.append({
                    "role": msg.role,
                    "content": content if len(content) > 1 else msg.content
                })
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}"
            }
            
            payload = {
                "model": model,
                "messages": qwen_messages,
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
                logger.error(f"Qwen API error: {response.status_code} - {response.text}")
                return ProviderResponse(
                    success=False,
                    error=f"API error: {response.status_code}",
                    raw_response=response.text
                )
                
        except ImportError:
            logger.warning("requests not available, using mock")
            return self._get_mock_response("Qwen chat")
        except Exception as e:
            logger.error(f"Error in Qwen chat: {e}")
            return ProviderResponse(success=False, error=str(e))
