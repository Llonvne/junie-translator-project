"""
翻译服务 - 高级翻译服务接口
"""
import logging
from pathlib import Path
from typing import Optional, List

from entities import SrtFile, AppConfig, AIModel, PromptTemplate
from .translator import AITranslator
from .client import AIClient, ClientFactory

logger = logging.getLogger(__name__)


class TranslationService:
    """翻译服务"""
    
    def __init__(self, config: AppConfig, model: AIModel, prompt_template: PromptTemplate,
                 client: Optional[AIClient] = None):
        self.config = config
        self.model = model
        self.prompt_template = prompt_template
        
        # 如果没有提供客户端，则创建一个
        if client is None:
            client = ClientFactory.create_client(
                provider=config.ai_api_service.api_service_provider,
                api_key=config.ai_api_service.api_key,
                api_endpoint=model.api_endpoint
            )
        
        self.client = client
        self.translator = AITranslator(client, model, prompt_template)
    
    async def translate_file(self, input_path: str, output_path: Optional[str] = None,
                           max_concurrent: int = 5) -> str:
        """翻译单个SRT文件"""
        logger.info(f"开始翻译文件: {input_path}")
        
        # 加载SRT文件
        srt_file = SrtFile.from_file(input_path)
        
        # 翻译文件
        translated_srt = await self.translator.translate_srt_file(
            srt_file, 
            self.config.to_language,
            max_concurrent
        )
        
        # 生成输出文件名
        if output_path is None:
            output_path = self._generate_output_filename(srt_file)
        
        # 保存翻译结果
        translated_srt.save_to_file(output_path)
        logger.info(f"翻译完成，文件保存至: {output_path}")
        
        return output_path
    
    async def translate_directory(self, input_dir: str, pattern: str = "*.srt",
                                max_concurrent: int = 5) -> List[str]:
        """翻译目录中的所有SRT文件"""
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"目录不存在: {input_dir}")
        
        srt_files = list(input_path.glob(pattern))
        if not srt_files:
            logger.warning(f"在 {input_dir} 中没有找到匹配 {pattern} 的文件")
            return []
        
        logger.info(f"找到 {len(srt_files)} 个SRT文件")
        
        results = []
        for srt_file in srt_files:
            try:
                output_path = await self.translate_file(str(srt_file), max_concurrent=max_concurrent)
                results.append(output_path)
            except Exception as e:
                logger.error(f"翻译文件 {srt_file} 失败: {e}")
        
        return results
    
    def _generate_output_filename(self, srt_file: SrtFile) -> str:
        """生成输出文件名"""
        input_path = srt_file.file_path
        file_hash = srt_file.get_file_hash()
        
        # 构建文件名: 原名_源语言_目标语言_哈希.srt
        from_lang = self.config.from_language
        to_lang = self.config.to_language
        
        stem = input_path.stem
        new_filename = f"{stem}_{from_lang}_{to_lang}_{file_hash}.srt"
        
        output_dir = self.config.get_output_path()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        return str(output_dir / new_filename)
    
    def is_ready(self) -> bool:
        """检查服务是否准备就绪"""
        return self.client.is_available()
    
    async def test_translation(self, text: str = "Hello, world!") -> str:
        """测试翻译功能"""
        messages = self.prompt_template.to_messages(text, self.config.to_language)
        return await self.client.translate_text(messages, self.model)