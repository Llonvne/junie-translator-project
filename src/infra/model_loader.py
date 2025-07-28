"""
模型加载器 - 负责加载和管理AI模型配置
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from entities import AIModel, ModelConfig

logger = logging.getLogger(__name__)


class ModelLoader:
    """AI模型配置加载器"""
    
    DEFAULT_AIPROVIDER_PATH = "aiprovider.json"
    
    # 内置默认提供商配置
    DEFAULT_PROVIDERS = {
        "openai": {
            "api-endpoint": "https://api.openai.com/v1",
            "models": {
                "gpt-3.5-turbo": {
                    "max-tokens": 1024,
                    "temperature": 0.3
                },
                "gpt-4": {
                    "max-tokens": 2048,
                    "temperature": 0.3
                }
            }
        },
        "deepseek": {
            "api-endpoint": "https://api.deepseek.com/v1",
            "models": {
                "deepseek-chat": {
                    "max-tokens": 1024,
                    "temperature": 0.3,
                    "aliases": ["deepseek-v3", "v3"]
                },
                "deepseek-reasoner": {
                    "max-tokens": 1024,
                    "temperature": 0.3,
                    "aliases": ["deepseek-r1", "r1"]
                }
            }
        },
        "mock": {
            "api-endpoint": None,
            "models": {
                "mock": {
                    "max-tokens": None,
                    "temperature": None
                }
            }
        }
    }
    
    def __init__(self, aiprovider_path: str = None):
        self.aiprovider_path = aiprovider_path or self.DEFAULT_AIPROVIDER_PATH
        self._providers_cache: Dict[str, Any] = None
    
    def load_model(self, provider: str, model_name: str) -> AIModel:
        """加载指定的AI模型"""
        providers_data = self._load_providers()
        
        # 查找提供商
        if provider not in providers_data:
            raise ValueError(f"AI提供商 '{provider}' 未找到")
        
        provider_config = providers_data[provider]
        api_endpoint = provider_config.get("api-endpoint")
        models = provider_config.get("models", {})
        
        # 先尝试直接匹配模型名
        if model_name in models:
            model_config_data = models[model_name]
        else:
            # 尝试通过别名匹配
            model_config_data = None
            for model_key, model_data in models.items():
                aliases = model_data.get("aliases", [])
                if model_name in aliases:
                    model_config_data = model_data
                    model_name = model_key  # 使用实际的模型名
                    break
            
            if model_config_data is None:
                raise ValueError(f"模型 '{model_name}' 在提供商 '{provider}' 中未找到")
        
        # 创建模型配置
        config = ModelConfig(
            max_tokens=model_config_data.get("max-tokens"),
            temperature=model_config_data.get("temperature"),
            aliases=model_config_data.get("aliases")
        )
        
        return AIModel(
            provider=provider,
            model_name=model_name,
            api_endpoint=api_endpoint,
            config=config
        )
    
    def find_model_by_name(self, model_name: str) -> Optional[AIModel]:
        """通过模型名称查找模型（在所有提供商中搜索）"""
        providers_data = self._load_providers()
        
        for provider, provider_config in providers_data.items():
            try:
                return self.load_model(provider, model_name)
            except ValueError:
                continue
        
        return None
    
    def _load_providers(self) -> Dict[str, Any]:
        """加载AI提供商配置"""
        if self._providers_cache is not None:
            return self._providers_cache
        
        aiprovider_path = Path(self.aiprovider_path)
        
        if not aiprovider_path.exists():
            logger.warning(f"AI提供商配置文件不存在: {self.aiprovider_path}，使用内置默认配置")
            self._providers_cache = self.DEFAULT_PROVIDERS
            return self._providers_cache
        
        try:
            with open(aiprovider_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 提取providers部分，如果没有则使用整个配置
            if "providers" in config_data:
                providers_data = config_data["providers"]
            else:
                providers_data = config_data
            
            # 合并内置默认配置和文件中的配置
            merged_providers = self.DEFAULT_PROVIDERS.copy()
            merged_providers.update(providers_data)
            
            self._providers_cache = merged_providers
            logger.info(f"成功加载AI提供商配置: {self.aiprovider_path}")
            return self._providers_cache
            
        except json.JSONDecodeError as e:
            logger.error(f"AI提供商配置文件JSON格式错误: {e}，使用内置默认配置")
            self._providers_cache = self.DEFAULT_PROVIDERS
            return self._providers_cache
        except Exception as e:
            logger.error(f"加载AI提供商配置失败: {e}，使用内置默认配置")
            self._providers_cache = self.DEFAULT_PROVIDERS
            return self._providers_cache
    
    def list_providers(self) -> list:
        """列出可用的AI提供商"""
        providers_data = self._load_providers()
        return list(providers_data.keys())
    
    def list_models(self, provider: str) -> list:
        """列出指定提供商的可用模型"""
        providers_data = self._load_providers()
        
        if provider not in providers_data:
            return []
        
        return list(providers_data[provider].get("models", {}).keys())
    
    def reload_providers(self) -> None:
        """重新加载提供商配置"""
        self._providers_cache = None
        logger.info("AI提供商配置缓存已清除，下次加载时将重新读取文件")