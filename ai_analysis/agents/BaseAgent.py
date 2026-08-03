import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAgent(ABC):
    # Agent 名称
    name: str = 'base_agent'
    # Agent 描述
    description: str = 'Base Agent'
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f'ai_analysis.agents.{self.name}')
        self._result: Dict[str, Any] = {}
    
    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # 执行 Agent 的核心逻辑
        pass
    
    def log_info(self, message: str):
        self.logger.info(f'[{self.name}] {message}')
    
    def log_error(self, message: str):
        self.logger.error(f'[{self.name}] {message}')
    
    def log_warning(self, message: str):
        self.logger.warning(f'[{self.name}] {message}')
    
    def set_result(self, key: str, value: Any):
        self._result[key] = value
    
    def get_result(self, key: str, default: Any = None) -> Any:
        return self._result.get(key, default)
    
    @property
    def result(self) -> Dict[str, Any]:
        return self._result.copy()
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        # 验证输入数据，默认返回 True
        return True
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        # 处理错误
        self.log_error(f'Error: {str(error)}')
        return {
            'success': False,
            'error': str(error),
            'agent': self.name
        }