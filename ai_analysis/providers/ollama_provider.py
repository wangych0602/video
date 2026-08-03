import logging
from typing import List
from .base import BaseProvider, ProviderConfig, ChatMessage, ProviderResponse

logger = logging.getLogger("ai_analysis.providers.ollama")


class OllamaProvider(BaseProvider):
    """Ollama 本地模型 Provider
    
    支持:
    - 文本对话
    - 视觉分析 (支持视觉的模型)
    """
    
    provider_type = "ollama"
    
    capabilities = {
        "chat": True,
        "vision": True,  # 取决于模型
        "speech_to_text": False,
        "text_to_speech": False,
        "embedding": True,
    }
    
    DEFAULT_MODEL = "llama3"
    DEFAULT_BASE_URL = "http://localhost:11434/api"
    
    def _get_base_url(self) -> str:
        return self.config.api_base or self.DEFAULT_BASE_URL
    
    def _get_model(self) -> str:
        return self.config.model_name or self.DEFAULT_MODEL
    
    def _validate_config(self):
        # Ollama 不需要 API key
        pass
    
    def chat(self, messages: List[ChatMessage]) -> ProviderResponse:
        try:
            import requests
            
            # 构建消息
            ollama_messages = []
            for msg in messages:
                msg_dict = {
                    "role": msg.role,
                    "content": msg.content,
                }
                
                # 添加图片
                if msg.images:
                    images = []
                    for img_path in msg.images:
                        base64_img = self._encode_image_base64(img_path)
                        if base64_img:
                            images.append(base64_img)
                    if images:
                        msg_dict["images"] = images
                
                ollama_messages.append(msg_dict)
            
            payload = {
                "model": self._get_model(),
                "messages": ollama_messages,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                }
            }
            
            response = requests.post(
                f"{self._get_base_url()}/chat",
                json=payload,
                timeout=self.config.timeout * 2  # 本地模型可能更慢
            )
            
            if response.status_code == 200:
                result = response.json()
                return ProviderResponse(
                    success=True,
                    content=result["message"]["content"],
                    raw_response=result
                )
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return ProviderResponse(
                    success=False,
                    error=f"API error: {response.status_code}",
                    raw_response=response.text
                )
                
        except ImportError:
            logger.warning("requests not available, using mock")
            return self._get_mock_response("Ollama chat")
        except Exception as e:
            logger.error(f"Error in Ollama chat: {e}")
            return self._get_mock_response(f"Ollama fallback: {e}")
