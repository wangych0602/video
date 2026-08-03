import logging
from typing import List
from .base import BaseProvider, ProviderConfig, ChatMessage, ProviderResponse

logger = logging.getLogger("ai_analysis.providers.openai")


class OpenAIProvider(BaseProvider):
    """OpenAI Provider
    
    支持:
    - 文本对话 (GPT-3.5, GPT-4, etc.)
    - 视觉分析 (GPT-4V)
    - 语音转文字 (Whisper)
    """
    
    provider_type = "openai"
    
    capabilities = {
        "chat": True,
        "vision": True,
        "speech_to_text": True,
        "text_to_speech": True,
        "embedding": True,
    }
    
    DEFAULT_MODEL = "gpt-4o"
    DEFAULT_VISION_MODEL = "gpt-4o"
    DEFAULT_BASE_URL = "https://api.openai.com/v1"
    
    def _get_base_url(self) -> str:
        return self.config.api_base or self.DEFAULT_BASE_URL
    
    def _get_model(self, vision: bool = False) -> str:
        if self.config.model_name:
            return self.config.model_name
        return self.DEFAULT_VISION_MODEL if vision else self.DEFAULT_MODEL
    
    def chat(self, messages: List[ChatMessage]) -> ProviderResponse:
        if not self.config.api_key:
            logger.warning("OpenAI API key not configured, using mock")
            return self._get_mock_response("OpenAI chat")
        
        try:
            import requests
            
            has_images = any(msg.images for msg in messages)
            model = self._get_model(vision=has_images)
            
            # 构建消息
            openai_messages = []
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
                
                openai_messages.append({
                    "role": msg.role,
                    "content": content if len(content) > 1 else msg.content
                })
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}"
            }
            
            payload = {
                "model": model,
                "messages": openai_messages,
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
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return ProviderResponse(
                    success=False,
                    error=f"API error: {response.status_code}",
                    raw_response=response.text
                )
                
        except ImportError:
            logger.warning("requests not available, using mock")
            return self._get_mock_response("OpenAI chat")
        except Exception as e:
            logger.error(f"Error in OpenAI chat: {e}")
            return ProviderResponse(success=False, error=str(e))
    
    def transcribe(self, audio_path: str, language: str = "") -> ProviderResponse:
        if not self.config.api_key:
            return self._get_mock_response("OpenAI whisper")
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.config.api_key}"
            }
            
            with open(audio_path, "rb") as f:
                files = {"file": f}
                data = {
                    "model": "whisper-1",
                    "response_format": "verbose_json",
                }
                if language:
                    data["language"] = language
                
                response = requests.post(
                    f"{self._get_base_url()}/audio/transcriptions",
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=self.config.timeout * 2
                )
            
            if response.status_code == 200:
                result = response.json()
                return ProviderResponse(
                    success=True,
                    content=result.get("text", ""),
                    raw_response=result
                )
            else:
                logger.error(f"OpenAI Whisper error: {response.status_code}")
                return ProviderResponse(
                    success=False,
                    error=f"Whisper error: {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"Error in OpenAI transcribe: {e}")
            return ProviderResponse(success=False, error=str(e))
