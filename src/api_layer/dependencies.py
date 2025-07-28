"""
API 依赖注入
"""
import logging
from typing import Optional
from functools import lru_cache

from ai_layer import TranslationService
from infra import InfrastructureManager

logger = logging.getLogger(__name__)

# 全局基础设施管理器
_infra_manager: Optional[InfrastructureManager] = None


def get_infra_manager() -> InfrastructureManager:
    """获取基础设施管理器单例"""
    global _infra_manager
    if _infra_manager is None:
        _infra_manager = InfrastructureManager()
    return _infra_manager


@lru_cache()
def get_translation_service() -> TranslationService:
    """获取翻译服务实例"""
    try:
        infra = get_infra_manager()
        return infra.create_translation_service()
    except Exception as e:
        logger.error(f"创建翻译服务失败: {e}")
        raise