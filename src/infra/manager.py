"""
基础设施管理器 - 负责组装和管理整个应用的基础设施
"""
import logging
from typing import Optional

from entities import AppConfig, AIModel, PromptTemplate
from ai_layer import TranslationService
from .config_loader import ConfigLoader
from .prompt_loader import PromptLoader
from .model_loader import ModelLoader

logger = logging.getLogger(__name__)


class InfrastructureManager:
    """基础设施管理器"""
    
    def __init__(self, config_path: str = None, prompts_path: str = None, 
                 aiprovider_path: str = None):
        self.config_loader = ConfigLoader(config_path)
        self.prompt_loader = PromptLoader(prompts_path)
        self.model_loader = ModelLoader(aiprovider_path)
        
        # 缓存
        self._config: Optional[AppConfig] = None
        self._model: Optional[AIModel] = None
        self._prompt_template: Optional[PromptTemplate] = None
    
    def get_config(self) -> AppConfig:
        """获取应用配置"""
        if self._config is None:
            self._config = self.config_loader.load_config()
            logger.info("应用配置已加载")
        return self._config
    
    def get_model(self) -> AIModel:
        """获取AI模型"""
        if self._model is None:
            config = self.get_config()
            
            # 首先尝试使用配置中的提供商和模型
            provider = config.ai_api_service.api_service_provider
            model_name = config.model
            
            if provider == 'auto':
                # 自动选择提供商
                self._model = self.model_loader.find_model_by_name(model_name)
                if self._model is None:
                    # 如果找不到，使用默认的mock提供商进行测试
                    logger.warning(f"未找到模型 '{model_name}'，使用mock提供商")
                    self._model = self.model_loader.load_model('mock', 'mock')
            else:
                try:
                    self._model = self.model_loader.load_model(provider, model_name)
                except Exception as e:
                    logger.error(f"加载模型失败: {e}")
                    # 降级到mock模型
                    logger.warning("降级使用mock模型")
                    self._model = self.model_loader.load_model('mock', 'mock')
            
            logger.info(f"AI模型已加载: {self._model.full_name}")
        
        return self._model
    
    def get_prompt_template(self) -> PromptTemplate:
        """获取提示词模板"""
        if self._prompt_template is None:
            config = self.get_config()
            self._prompt_template = self.prompt_loader.load_prompt_template(config.prompt_style)
            logger.info(f"提示词模板已加载: {config.prompt_style.value}")
        
        return self._prompt_template
    
    def create_translation_service(self) -> TranslationService:
        """创建翻译服务"""
        config = self.get_config()
        model = self.get_model()
        prompt_template = self.get_prompt_template()
        
        service = TranslationService(config, model, prompt_template)
        logger.info("翻译服务已创建")
        
        return service
    
    def reload_all(self) -> None:
        """重新加载所有配置"""
        self._config = None
        self._model = None
        self._prompt_template = None
        
        self.prompt_loader.reload_prompts()
        self.model_loader.reload_providers()
        
        logger.info("所有配置已重新加载")
    
    def validate_configuration(self) -> bool:
        """验证配置的完整性"""
        try:
            config = self.get_config()
            model = self.get_model()
            prompt_template = self.get_prompt_template()
            
            # 检查必要的配置项
            if not config.to_language:
                logger.error("目标语言未配置")
                return False
            
            if not model:
                logger.error("AI模型未配置")
                return False
            
            if not prompt_template:
                logger.error("提示词模板未配置")
                return False
            
            logger.info("配置验证通过")
            return True
            
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            return False
    
    def get_system_info(self) -> dict:
        """获取系统信息"""
        try:
            config = self.get_config()
            model = self.get_model()
            prompt_template = self.get_prompt_template()
            
            return {
                "config": {
                    "from_language": config.from_language,
                    "to_language": config.to_language,
                    "output_directory": config.output_directory,
                    "prompt_style": config.prompt_style.value,
                    "enable_post_check": config.enable_post_check
                },
                "model": {
                    "provider": model.provider,
                    "model_name": model.model_name,
                    "api_endpoint": model.api_endpoint,
                    "full_name": model.full_name
                },
                "prompt": {
                    "style": prompt_template.style.value,
                    "system_prompt_length": len(prompt_template.system_prompt),
                    "user_template_length": len(prompt_template.user_prompt_template)
                },
                "available_providers": self.model_loader.list_providers(),
                "available_prompt_styles": self.prompt_loader.list_available_styles()
            }
        except Exception as e:
            logger.error(f"获取系统信息失败: {e}")
            return {"error": str(e)}