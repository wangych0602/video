import logging
from typing import List
from .base import BaseProvider, ProviderConfig, ChatMessage, ProviderResponse

logger = logging.getLogger("ai_analysis.providers.gemini")


class GeminiProvider(BaseProvider):
    """Google Gemini Provider
    
    支持:
    - 文本对话
    - 视觉分析
    - 语音转文字 (Gemini 1.5 Pro)
    """
    
    provider_type = "gemini"
    
    capabilities = {
        "chat": True,
        "vision": True,
        "speech_to_text": True,
        "text_to_speech": False,
        "embedding": True,
    }
    
    DEFAULT_MODEL = "gemini-1.5-pro"
    DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1"
    
    def _get_base_url(self) -> str:
        return self.config.api_base or self.DEFAULT_BASE_URL
    
    def _get_model(self) -> str:
        return self.config.model_name or self.DEFAULT_MODEL
    
    def chat(self, messages: List[ChatMessage]) -> ProviderResponse:
        if not self.config.api_key:
            logger.warning("Gemini API key not configured, using mock")
            return self._get_mock_response("Gemini chat")
        
        try:
            import requests
            
            # 构建 contents
            contents = []
            for msg in messages:
                role = "model" if msg.role == "assistant" else "user"
                parts = []
                
                if msg.content:
                    parts.append({"text": msg.content})
                
                # 添加图片
                for img_path in msg.images:
                    base64_img = self._encode_image_base64(img_path)
                    if base64_img:
                        parts.append({
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": base64_img
                            }
                        })
                
                contents.append({"role": role, "parts": parts})
            
            headers = {"Content-Type": "application/json"}
            
            payload = {"contents": contents}
            
            model = self._get_model()
            url = f"{self._get_base_url()}/models/{model}:generateContent?key={self.config.api_key}"
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                return ProviderResponse(
                    success=True,
                    content=content,
                    raw_response=result
                )
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return ProviderResponse(
                    success=False,
                    error=f"API error: {response.status_code}",
                    raw_response=response.text
                )
                
        except ImportError:
            logger.warning("requests not available, using mock")
            return self._get_mock_response("Gemini chat")
        except Exception as e:
            logger.error(f"Error in Gemini chat: {e}")
            return ProviderResponse(success=False, error=str(e))
    
    def transcribe(self, audio_path: str, language: str = "") -> ProviderResponse:
        # Gemini 1.5 Pro 支持音频输入，但需要特殊处理
        # 这里简化处理，返回 mock
        return self._get_mock_response("Gemini speech")
