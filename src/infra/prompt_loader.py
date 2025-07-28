"""
提示词加载器 - 负责加载和管理提示词模板
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any

from entities import PromptTemplate, PromptStyle

logger = logging.getLogger(__name__)


class PromptLoader:
    """提示词加载器"""
    
    DEFAULT_PROMPTS_PATH = "prompts.json"
    
    # 内置默认提示词
    DEFAULT_PROMPTS = {
        "default": {
            "system": "You are a professional translator. Translate the text accurately while preserving the original meaning, tone, and formatting. IMPORTANT: Only output the translated text without any explanations, notes, or additional content.",
            "user": "Translate the following text to {target_language}. Preserve any formatting and special characters. IMPORTANT: Only output the translated text without any explanations, notes, or additional content:\n\n{text}"
        },
        "chinese": {
            "system": "你是一位专业翻译。请准确翻译文本，同时保留原始含义、语气和格式。重要提示：只输出翻译后的文本，不要包含任何解释、注释或额外内容。",
            "user": "请将以下文本翻译成{target_language}。保留任何格式和特殊字符。重要提示：只输出翻译后的文本，不要包含任何解释、注释或额外内容：\n\n{text}"
        },
        "formal": {
            "system": "You are a professional translator specializing in formal and official documents. Translate the text with a formal tone while preserving the original meaning and formatting. IMPORTANT: Only output the translated text without any explanations, notes, or additional content.",
            "user": "Translate the following formal document to {target_language}. Maintain a formal tone and preserve all formatting and special characters. IMPORTANT: Only output the translated text without any explanations, notes, or additional content:\n\n{text}"
        },
        "casual": {
            "system": "You are a professional translator specializing in casual and conversational content. Translate the text with a natural, conversational tone while preserving the original meaning. IMPORTANT: Only output the translated text without any explanations, notes, or additional content.",
            "user": "Translate the following casual text to {target_language} using a natural, conversational style. Preserve the original meaning and any formatting. IMPORTANT: Only output the translated text without any explanations, notes, or additional content:\n\n{text}"
        },
        "technical": {
            "system": "You are a professional technical translator with expertise in specialized terminology. Translate the text accurately while preserving technical terms and formatting. IMPORTANT: Only output the translated text without any explanations, notes, or additional content.",
            "user": "Translate the following technical content to {target_language}. Ensure technical terms are accurately translated and preserve all formatting. IMPORTANT: Only output the translated text without any explanations, notes, or additional content:\n\n{text}"
        },
        "subtitle": {
            "system": "You are a professional subtitle translator. Translate concisely while preserving the original meaning. Keep translations brief enough to be read quickly as subtitles. IMPORTANT: Only output the translated text without any explanations, notes, or additional content.",
            "user": "Translate the following subtitle text to {target_language}. Keep the translation concise and easy to read quickly. Preserve the original meaning and any formatting. IMPORTANT: Only output the translated text without any explanations, notes, or additional content:\n\n{text}"
        }
    }
    
    def __init__(self, prompts_path: str = None):
        self.prompts_path = prompts_path or self.DEFAULT_PROMPTS_PATH
        self._prompts_cache: Dict[str, Dict[str, Any]] = None
    
    def load_prompt_template(self, style: PromptStyle) -> PromptTemplate:
        """加载指定风格的提示词模板"""
        prompts_data = self._load_prompts()
        
        style_key = style.value
        if style_key not in prompts_data:
            logger.warning(f"提示词风格 '{style_key}' 未找到，使用默认风格")
            style_key = PromptStyle.DEFAULT.value
            style = PromptStyle.DEFAULT
        
        if style_key not in prompts_data:
            logger.warning("默认提示词未找到，使用内置默认提示词")
            prompt_data = self.DEFAULT_PROMPTS[PromptStyle.DEFAULT.value]
        else:
            prompt_data = prompts_data[style_key]
        
        return PromptTemplate.from_dict(style, prompt_data)
    
    def _load_prompts(self) -> Dict[str, Any]:
        """加载提示词数据"""
        if self._prompts_cache is not None:
            return self._prompts_cache
        
        prompts_path = Path(self.prompts_path)
        
        if not prompts_path.exists():
            logger.warning(f"提示词文件不存在: {self.prompts_path}，使用内置默认提示词")
            self._prompts_cache = self.DEFAULT_PROMPTS
            return self._prompts_cache
        
        try:
            with open(prompts_path, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
            
            # 合并内置默认提示词和文件中的提示词
            merged_prompts = self.DEFAULT_PROMPTS.copy()
            merged_prompts.update(prompts_data)
            
            self._prompts_cache = merged_prompts
            logger.info(f"成功加载提示词文件: {self.prompts_path}")
            return self._prompts_cache
            
        except json.JSONDecodeError as e:
            logger.error(f"提示词文件JSON格式错误: {e}，使用内置默认提示词")
            self._prompts_cache = self.DEFAULT_PROMPTS
            return self._prompts_cache
        except Exception as e:
            logger.error(f"加载提示词文件失败: {e}，使用内置默认提示词")
            self._prompts_cache = self.DEFAULT_PROMPTS
            return self._prompts_cache
    
    def list_available_styles(self) -> list:
        """列出可用的提示词风格"""
        prompts_data = self._load_prompts()
        return list(prompts_data.keys())
    
    def reload_prompts(self) -> None:
        """重新加载提示词"""
        self._prompts_cache = None
        logger.info("提示词缓存已清除，下次加载时将重新读取文件")