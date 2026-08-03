import logging
from typing import Dict, Type, Optional, List

from django.conf import settings

from .base import BaseProvider, ProviderConfig
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider
from .claude_provider import ClaudeProvider
from .qwen_provider import QwenProvider
from .deepseek_provider import DeepSeekProvider
from .glm_provider import GLMProvider
from .ollama_provider import OllamaProvider

logger = logging.getLogger("ai_analysis.providers.factory")


class ProviderFactory:
    """Provider 工厂类
    负责创建和管理 AI Provider 实例。
    """

    # Provider 注册表
    _providers: Dict[str, Type[BaseProvider]] = {
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "claude": ClaudeProvider,
        "qwen": QwenProvider,
        "deepseek": DeepSeekProvider,
        "glm": GLMProvider,
        "ollama": OllamaProvider,
    }

    # 实例缓存
    _instances: Dict[str, BaseProvider] = {}

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseProvider]):
        """注册新的 Provider 类型"""
        cls._providers[name] = provider_class
        logger.info(f"Registered provider: {name}")

    @classmethod
    def get_provider_class(cls, provider_type: str) -> Optional[Type[BaseProvider]]:
        """获取 Provider 类"""
        return cls._providers.get(provider_type)

    @classmethod
    def create_provider(cls, provider_type: str, config: ProviderConfig = None) -> Optional[BaseProvider]:
        """创建 Provider 实例"""
        provider_class = cls.get_provider_class(provider_type)
        if not provider_class:
            logger.error(f"Unknown provider type: {provider_type}")
            return None

        try:
            if config:
                return provider_class(config)
            return provider_class()
        except Exception as e:
            logger.error(f"Failed to create provider {provider_type}: {e}")
            return None

    @classmethod
    def get_provider(cls, provider_type: str, config: ProviderConfig = None) -> Optional[BaseProvider]:
        """获取 Provider 实例（带缓存）"""
        cache_key = f"{provider_type}_{id(config) if config else 'default'}"

        if cache_key not in cls._instances:
            provider = cls.create_provider(provider_type, config)
            if provider:
                cls._instances[cache_key] = provider
            else:
                return None

        return cls._instances[cache_key]

    @classmethod
    def get_provider_from_config(cls, config) -> Optional[BaseProvider]:
        """从数据库配置创建 Provider"""
        try:
            provider_config = ProviderConfig(
                api_key=config.api_key,
                api_base=config.get_effective_api_base(),
                model_name=config.model_name,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                timeout=config.timeout,
                extra_params={
                    "deployment_type": config.deployment_type,
                    "capabilities": config.get_capabilities(),
                }
            )
            return cls.create_provider(config.provider, provider_config)
        except Exception as e:
            logger.error(f"Failed to create provider from config: {e}")
            return None

    @classmethod
    def get_active_provider(cls, capability: str = "chat") -> Optional[BaseProvider]:
        """获取激活的 Provider（按优先级）"""
        from ai_analysis.models import AIModelConfig

        # 查询状态为激活且非离线的配置，按优先级排序
        configs = AIModelConfig.objects.filter(
            is_active=True,
            status=True
        ).exclude(
            health_status="offline"
        ).order_by("priority")

        for config in configs:
            provider = cls.get_provider_from_config(config)
            if provider:
                # 检查能力
                capabilities = provider.get_capabilities()
                if capabilities.get(capability, False):
                    return provider

        # 如果没有找到，返回 None
        logger.warning(f"No active provider found for capability: {capability}")
        return None

    @classmethod
    def get_vision_provider(cls) -> Optional[BaseProvider]:
        """获取视觉分析 Provider"""
        return cls.get_active_provider("vision")

    @classmethod
    def get_chat_provider(cls) -> Optional[BaseProvider]:
        """获取文本对话 Provider"""
        return cls.get_active_provider("chat")

    @classmethod
    def get_speech_provider(cls) -> Optional[BaseProvider]:
        """获取语音识别 Provider"""
        return cls.get_active_provider("speech_to_text")

    @classmethod
    def list_available_providers(cls) -> List[str]:
        """列出所有可用的 Provider 类型"""
        return list(cls._providers.keys())

    @classmethod
    def get_provider_capabilities(cls, provider_type: str) -> Dict[str, bool]:
        """获取指定 Provider 的能力"""
        provider_class = cls.get_provider_class(provider_type)
        if provider_class:
            return provider_class.capabilities.copy()
        return {}

    @classmethod
    def clear_cache(cls):
        """清除 Provider 缓存"""
        cls._instances.clear()
        logger.info("Provider cache cleared")

    @classmethod
    def chat_with_fallback(cls, messages, model_type: str = "chat", **kwargs):
        """带自动降级的对话调用
        
        按优先级依次尝试每个 Provider，失败则自动降级到下一个
        
        Args:
            messages: 消息列表
            model_type: 模型类型（chat/vision/speech_to_text等）
            **kwargs: 其他参数
            
        Returns:
            ProviderResponse: 响应结果
        """
        import time
        from ai_analysis.models import AIUsageLog, AIModelConfig
        
        active_configs = AIModelConfig.objects.filter(
            status=True,
            is_active=True
        ).exclude(
            health_status="offline"
        ).order_by("priority")
        
        last_error = None
        fallback_count = 0
        
        for config in active_configs:
            try:
                start_time = time.time()
                provider = cls.get_provider_from_config(config)
                
                # 检查能力
                capabilities = provider.get_capabilities()
                if not capabilities.get(model_type, False):
                    continue
                
                # 调用
                response = provider.chat(messages, **kwargs)
                
                response_time = time.time() - start_time
                
                # 记录使用日志
                try:
                    usage = response.usage if hasattr(response, "usage") else {}
                    AIUsageLog.objects.create(
                        provider=config.provider,
                        model_name=config.model_name,
                        task_type="chat",
                        input_tokens=usage.get("prompt_tokens", 0) if isinstance(usage, dict) else 0,
                        output_tokens=usage.get("completion_tokens", 0) if isinstance(usage, dict) else 0,
                        total_tokens=usage.get("total_tokens", 0) if isinstance(usage, dict) else 0,
                        response_time=round(response_time, 3),
                        status="success" if response.success else "failed",
                        error_message=response.error if not response.success else "",
                        model_config=config,
                    )
                except Exception as log_error:
                    logger.error(f"Failed to log usage: {log_error}")
                
                # 如果有降级，记录降级状态
                if fallback_count > 0:
                    logger.info(f"Fallback succeeded after {fallback_count} attempts, using {config.provider}")
                
                return response
                
            except Exception as e:
                fallback_count += 1
                last_error = e
                logger.warning(f"Provider {config.provider} failed, falling back: {e}")
                
                # 记录失败日志
                try:
                    AIUsageLog.objects.create(
                        provider=config.provider,
                        model_name=config.model_name,
                        task_type="chat",
                        status="failed",
                        error_message=str(e)[:500],
                        model_config=config,
                    )
                except Exception as log_error:
                    logger.error(f"Failed to log failure: {log_error}")
                
                continue
        
        # 所有 Provider 都失败了
        logger.error(f"All providers failed. Last error: {last_error}")
        
        # 返回失败响应
        from .base import ProviderResponse
        return ProviderResponse(
            success=False,
            content="",
            usage={},
            error=str(last_error) if last_error else "All providers failed"
        )

    @classmethod
    def analyze_image_with_fallback(cls, image_path: str, prompt: str, **kwargs):
        """带自动降级的图片分析调用
        
        Args:
            image_path: 图片路径
            prompt: 提示词
            **kwargs: 其他参数
            
        Returns:
            ProviderResponse: 响应结果
        """
        # 构造消息
        messages = [
            {"role": "user", "content": prompt, "images": [image_path]}
        ]
        
        return cls.chat_with_fallback(messages, model_type="vision", **kwargs)
