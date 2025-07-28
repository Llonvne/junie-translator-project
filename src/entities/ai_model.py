"""
AI 模型实体
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass
class ModelConfig:
    """AI模型配置"""
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    aliases: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        if self.max_tokens is not None:
            result['max_tokens'] = self.max_tokens
        if self.temperature is not None:
            result['temperature'] = self.temperature
        if self.aliases:
            result['aliases'] = self.aliases
        return result


@dataclass
class AIModel:
    """AI模型实体"""
    provider: str
    model_name: str
    api_endpoint: str
    config: ModelConfig
    
    @property
    def full_name(self) -> str:
        """获取完整模型名称"""
        return f"{self.provider}/{self.model_name}"
    
    def get_request_params(self) -> Dict[str, Any]:
        """获取请求参数"""
        params = {
            'model': self.model_name
        }
        params.update(self.config.to_dict())
        return params
    
    def is_alias_match(self, alias: str) -> bool:
        """检查是否匹配别名"""
        if not self.config.aliases:
            return False
        return alias in self.config.aliases