"""
提示词实体
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any


class PromptStyle(Enum):
    """提示词风格枚举"""
    DEFAULT = "default"
    CHINESE = "chinese" 
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    SUBTITLE = "subtitle"


@dataclass
class PromptTemplate:
    """提示词模板实体"""
    style: PromptStyle
    system_prompt: str
    user_prompt_template: str
    
    def format_user_prompt(self, text: str, target_language: str) -> str:
        """格式化用户提示词"""
        return self.user_prompt_template.format(
            text=text,
            target_language=target_language
        )
    
    def to_messages(self, text: str, target_language: str) -> list:
        """转换为消息格式"""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.format_user_prompt(text, target_language)}
        ]
    
    @classmethod
    def from_dict(cls, style: PromptStyle, data: Dict[str, Any]) -> 'PromptTemplate':
        """从字典创建提示词模板"""
        return cls(
            style=style,
            system_prompt=data.get('system', ''),
            user_prompt_template=data.get('user', '')
        )