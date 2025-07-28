"""
实体层 (Entity Layer)
包含核心业务实体：SRT 字幕文件、AI 模型配置、提示词、配置文件等
"""

from .srt import SrtFile, SubtitleEntry
from .ai_model import AIModel, ModelConfig
from .prompt import PromptTemplate, PromptStyle
from .config import AppConfig, AIServiceConfig

__all__ = [
    'SrtFile',
    'SubtitleEntry', 
    'AIModel',
    'ModelConfig',
    'PromptTemplate',
    'PromptStyle',
    'AppConfig',
    'AIServiceConfig'
]