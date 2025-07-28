"""
配置实体
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any
from .prompt import PromptStyle


@dataclass
class AIServiceConfig:
    """AI服务配置"""
    api_service_provider: str
    api_key: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {'api-service-provider': self.api_service_provider}
        if self.api_key:
            result['api-key'] = self.api_key
        return result


@dataclass
class AppConfig:
    """应用配置实体"""
    from_language: str
    to_language: str
    ai_api_service: AIServiceConfig
    output_directory: str
    model: str
    prompt_style: PromptStyle
    enable_post_check: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """从字典创建配置"""
        ai_service_data = data.get('ai-api-service', {})
        ai_service = AIServiceConfig(
            api_service_provider=ai_service_data.get('api-service-provider', 'auto'),
            api_key=ai_service_data.get('api-key')
        )
        
        prompt_style_str = data.get('prompt-style', 'default')
        try:
            prompt_style = PromptStyle(prompt_style_str)
        except ValueError:
            prompt_style = PromptStyle.DEFAULT
        
        return cls(
            from_language=data.get('from-language', 'auto'),
            to_language=data['to-language'],
            ai_api_service=ai_service,
            output_directory=data.get('output-directory', './output'),
            model=data.get('model', 'gpt-3.5-turbo'),
            prompt_style=prompt_style,
            enable_post_check=data.get('enable-post-check', False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'from-language': self.from_language,
            'to-language': self.to_language,
            'ai-api-service': self.ai_api_service.to_dict(),
            'output-directory': self.output_directory,
            'model': self.model,
            'prompt-style': self.prompt_style.value,
            'enable-post-check': self.enable_post_check
        }
    
    def get_output_path(self) -> Path:
        """获取输出路径"""
        return Path(self.output_directory)