"""
AI翻译器 - 负责协调SRT、提示词和AI服务
"""
import asyncio
import logging
from typing import List, Optional

try:
    from tqdm.asyncio import tqdm as async_tqdm
    TQDM_AVAILABLE = True
except ImportError:
    try:
        from tqdm import tqdm
        TQDM_AVAILABLE = True
        async_tqdm = None
    except ImportError:
        TQDM_AVAILABLE = False
        async_tqdm = None

from entities import SrtFile, SubtitleEntry, AIModel, PromptTemplate
from .client import AIClient

logger = logging.getLogger(__name__)


class AITranslator:
    """AI翻译器"""
    
    def __init__(self, client: AIClient, model: AIModel, prompt_template: PromptTemplate):
        self.client = client
        self.model = model
        self.prompt_template = prompt_template
        
    async def translate_subtitle_entry(self, entry: SubtitleEntry, target_language: str) -> SubtitleEntry:
        """翻译单个字幕条目"""
        try:
            # 构建消息
            messages = self.prompt_template.to_messages(entry.text, target_language)
            
            # 调用AI服务
            translated_text = await self.client.translate_text(messages, self.model)
            
            # 创建新的字幕条目
            translated_entry = SubtitleEntry(
                index=entry.index,
                start_time=entry.start_time,
                end_time=entry.end_time,
                content=translated_text.split('\n')
            )
            
            return translated_entry
            
        except Exception as e:
            logger.error(f"翻译字幕条目 {entry.index} 失败: {e}")
            # 返回原始条目
            return entry
    
    async def translate_srt_file(self, srt_file: SrtFile, target_language: str, 
                               max_concurrent: int = 5) -> SrtFile:
        """翻译整个SRT文件"""
        logger.info(f"开始翻译SRT文件: {srt_file.file_path}")
        logger.info(f"总共 {srt_file.total_entries} 个字幕条目")
        
        # 创建信号量控制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def translate_with_semaphore(entry: SubtitleEntry) -> SubtitleEntry:
            async with semaphore:
                return await self.translate_subtitle_entry(entry, target_language)
        
        # 创建翻译任务
        tasks = [translate_with_semaphore(entry) for entry in srt_file.entries]
        
        # 执行翻译并显示进度
        if TQDM_AVAILABLE and async_tqdm:
            translated_entries = await async_tqdm.gather(
                *tasks, 
                desc="翻译进度",
                total=len(tasks)
            )
        else:
            translated_entries = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理异常
            for i, result in enumerate(translated_entries):
                if isinstance(result, Exception):
                    logger.error(f"翻译条目 {i+1} 时出错: {result}")
                    translated_entries[i] = srt_file.entries[i]  # 使用原始条目
        
        # 创建翻译后的SRT文件
        translated_srt = SrtFile(
            file_path=srt_file.file_path,
            entries=translated_entries,
            encoding=srt_file.encoding
        )
        
        logger.info("SRT文件翻译完成")
        return translated_srt
    
    async def translate_batch(self, entries: List[SubtitleEntry], target_language: str,
                            max_concurrent: int = 5) -> List[SubtitleEntry]:
        """批量翻译字幕条目"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def translate_with_semaphore(entry: SubtitleEntry) -> SubtitleEntry:
            async with semaphore:
                return await self.translate_subtitle_entry(entry, target_language)
        
        tasks = [translate_with_semaphore(entry) for entry in entries]
        
        if TQDM_AVAILABLE and async_tqdm:
            results = await async_tqdm.gather(*tasks, desc="批量翻译")
        else:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理异常
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"翻译条目 {i+1} 时出错: {result}")
                    results[i] = entries[i]  # 使用原始条目
        
        return results