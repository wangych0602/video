import logging
from typing import List
from .base import BaseProvider, ProviderConfig, ChatMessage, ProviderResponse

logger = logging.getLogger("ai_analysis.providers.claude")


class ClaudeProvider(BaseProvider):
    """Anthropic Claude Provider
    
    支持:
    - 文本对话
    - 视觉分析 (Claude 3)
    """
    
    provider_type = "claude"
    
    capabilities = {
        "chat": True,
        "vision": True,
        "speech_to_text": False,
        "text_to_speech": False,
        "embedding": False,
    }
    
    DEFAULT_MODEL = "claude-3-5-sonnet-20240620"
    DEFAULT_BASE_URL = "https://api.anthropic.com/v1"
    
    def _get_base_url(self) -> str:
        return self.config.api_base or self.DEFAULT_BASE_URL
    
    def _get_model(self) -> str:
        return self.config.model_name or self.DEFAULT_MODEL
    
    def chat(self, messages: List[ChatMessage]) -> ProviderResponse:
        if not self.config.api_key:
            logger.warning("Claude API key not configured, using mock")
            return self._get_mock_response("Claude chat")
        
        try:
            import requests
            
            # 分离 system prompt
            system_prompt = ""
            claude_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_prompt = msg.content
                else:
                    content = []
                    if msg.content:
                        content.append({"type": "text", "text": msg.content})
                    
                    # 添加图片
                    for img_path in msg.images:
                        base64_img = self._encode_image_base64(img_path)
                        if base64_img:
                            content.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_img
                                }
                            })
                    
                    claude_messages.append({
                        "role": msg.role,
                        "content": content if len(content) > 1 else msg.content
                    })
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.config.api_key,
                "anthropic-version": "2023-06-01",
            }
            
            payload = {
                "model": self._get_model(),
                "max_tokens": self.config.max_tokens,
                "messages": claude_messages,
                "temperature": self.config.temperature,
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self._get_base_url()}/messages",
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["content"][0]["text"]
                return ProviderResponse(
                    success=True,
                    content=content,
                    usage=result.get("usage", {}),
                    raw_response=result
                )
            else:
                logger.error(f"Claude API error: {response.status_code} - {response.text}")
                return ProviderResponse(
                    success=False,
                    error=f"API error: {response.status_code}",
                    raw_response=response.text
                )
                
        except ImportError:
            logger.warning("requests not available, using mock")
            return self._get_mock_response("Claude chat")
        except Exception as e:
            logger.error(f"Error in Claude chat: {e}")
            return ProviderResponse(success=False, error=str(e))
