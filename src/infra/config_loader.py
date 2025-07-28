"""
配置加载器 - 负责加载和解析应用配置
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any

from entities import AppConfig

logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置加载器"""
    
    DEFAULT_CONFIG_PATH = "config.json"
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
    
    def load_config(self) -> AppConfig:
        """加载应用配置"""
        try:
            config_data = self._load_config_file()
            self._validate_config(config_data)
            return AppConfig.from_dict(config_data)
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            raise
    
    def _load_config_file(self) -> Dict[str, Any]:
        """从文件加载配置"""
        config_path = Path(self.config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"成功加载配置文件: {self.config_path}")
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件JSON格式错误: {e}")
        except Exception as e:
            raise ValueError(f"读取配置文件失败: {e}")
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """验证配置完整性"""
        required_fields = ['to-language']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"配置文件缺少必需字段: {field}")
        
        # 验证AI服务配置
        if 'ai-api-service' in config:
            ai_config = config['ai-api-service']
            if 'api-service-provider' not in ai_config:
                config['ai-api-service']['api-service-provider'] = 'auto'
        else:
            config['ai-api-service'] = {'api-service-provider': 'auto'}
        
        # 设置默认值
        config.setdefault('from-language', 'auto')
        config.setdefault('output-directory', './output')
        config.setdefault('model', 'gpt-3.5-turbo')
        config.setdefault('prompt-style', 'default')
        config.setdefault('enable-post-check', False)
        
        logger.debug("配置验证通过")
    
    def save_config(self, config: AppConfig, output_path: str = None) -> None:
        """保存配置到文件"""
        output_path = output_path or self.config_path
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"配置已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            raise