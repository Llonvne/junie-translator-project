"""
AI层 (AI Layer)
负责组装SRT与提示词并实际请求AI服务并回答
"""

from .translator import AITranslator
from .client import AIClient
from .service import TranslationService

__all__ = [
    'AITranslator',
    'AIClient', 
    'TranslationService'
]