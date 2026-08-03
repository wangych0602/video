"""
Provider 健康检查服务
"""
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

from django.utils import timezone as django_timezone

from ai_analysis.models import AIModelConfig
from ai_analysis.providers import ProviderFactory

logger = logging.getLogger(__name__)


class ProviderHealthChecker:
    """Provider 健康检查器"""
    
    def __init__(self):
        self.results = {}
    
    def check_all_providers(self) -> Dict:
        """检查所有激活的 Provider"""
        configs = AIModelConfig.objects.filter(is_active=True)
        results = {
            'total': configs.count(),
            'active': 0,
            'degraded': 0,
            'offline': 0,
            'details': []
        }
        
        for config in configs:
            result = self.check_provider(config)
            results['details'].append(result)
            
            if result['status'] == 'active':
                results['active'] += 1
            elif result['status'] == 'degraded':
                results['degraded'] += 1
            else:
                results['offline'] += 1
        
        self.results = results
        return results
    
    def check_provider(self, config: AIModelConfig) -> Dict:
        """检查单个 Provider 的健康状态
        
        Args:
            config: AIModelConfig 实例
            
        Returns:
            Dict: 健康检查结果
        """
        start_time = time.time()
        result = {
            'id': config.id,
            'provider': config.provider,
            'model_name': config.model_name,
            'deployment_type': config.deployment_type,
            'status': 'offline',
            'response_time': 0,
            'error': None,
            'checked_at': django_timezone.now().isoformat()
        }
        
        try:
            # 创建 Provider 实例
            provider = ProviderFactory.get_provider_from_config(config)
            
            # 执行健康检查
            health_result = provider.health_check()
            
            response_time = time.time() - start_time
            result['response_time'] = round(response_time, 3)
            
            if health_result.get('success', False):
                result['status'] = 'active'
                result['error'] = None
            else:
                result['status'] = 'degraded'
                result['error'] = health_result.get('error', 'Unknown error')
            
        except Exception as e:
            response_time = time.time() - start_time
            result['response_time'] = round(response_time, 3)
            result['status'] = 'offline'
            result['error'] = str(e)
            logger.error(f"Health check failed for {config.provider}/{config.model_name}: {e}")
        
        # 更新数据库中的健康状态
        self._update_config_health(config, result)
        
        return result
    
    def _update_config_health(self, config: AIModelConfig, result: Dict):
        """更新配置的健康状态
        
        Args:
            config: AIModelConfig 实例
            result: 健康检查结果
        """
        try:
            config.health_status = result['status']
            config.last_health_check_time = django_timezone.now()
            
            if result['error']:
                config.last_error_message = result['error'][:500]  # 限制长度
            
            config.save(update_fields=[
                'health_status', 
                'last_health_check_time', 
                'last_error_message'
            ])
        except Exception as e:
            logger.error(f"Failed to update health status for {config.provider}: {e}")
    
    def get_available_providers(self, capability: str = 'chat') -> List[AIModelConfig]:
        """获取可用的 Provider 列表
        
        Args:
            capability: 需要的能力（chat/vision/speech_to_text等）
            
        Returns:
            List[AIModelConfig]: 可用的配置列表，按优先级排序
        """
        # 查询所有激活且非离线的配置
        configs = AIModelConfig.objects.filter(
            is_active=True,
            status=True
        ).exclude(
            health_status='offline'
        ).order_by('priority')
        
        # 过滤能力匹配的配置
        available = []
        for config in configs:
            caps = config.get_capabilities()
            if caps.get(capability, False):
                available.append(config)
        
        return available
    
    def get_provider_status_summary(self) -> Dict:
        """获取 Provider 状态汇总
        
        Returns:
            Dict: 状态汇总
        """
        all_configs = AIModelConfig.objects.filter(is_active=True)
        
        summary = {
            'total': all_configs.count(),
            'by_status': {
                'active': all_configs.filter(health_status='active').count(),
                'degraded': all_configs.filter(health_status='degraded').count(),
                'offline': all_configs.filter(health_status='offline').count(),
            },
            'by_provider': {},
            'last_check_time': None
        }
        
        # 按 Provider 统计
        for config in all_configs:
            provider = config.provider
            if provider not in summary['by_provider']:
                summary['by_provider'][provider] = {
                    'total': 0,
                    'active': 0,
                    'degraded': 0,
                    'offline': 0,
                }
            summary['by_provider'][provider]['total'] += 1
            summary['by_provider'][provider][config.health_status] += 1
        
        # 最后检查时间
        last_check = all_configs.exclude(
            last_health_check_time__isnull=True
        ).order_by('-last_health_check_time').first()
        
        if last_check:
            summary['last_check_time'] = last_check.last_health_check_time.isoformat()
        
        return summary


# 全局健康检查器实例
health_checker = ProviderHealthChecker()


def check_all_providers_health():
    """检查所有 Provider 健康状态（Celery 任务调用）"""
    checker = ProviderHealthChecker()
    return checker.check_all_providers()


def get_available_providers(capability: str = 'chat') -> List[AIModelConfig]:
    """获取可用的 Provider 列表（便捷函数）"""
    checker = ProviderHealthChecker()
    return checker.get_available_providers(capability)


def get_provider_status_summary() -> Dict:
    """获取 Provider 状态汇总（便捷函数）"""
    checker = ProviderHealthChecker()
    return checker.get_provider_status_summary()
