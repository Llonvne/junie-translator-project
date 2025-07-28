"""
Main Module - Core functionality for translating SRT files.

This module ties together the SRT parser and translator modules to provide
the core functionality for translating SRT files with progress tracking.
It supports async operations for improved performance with multiple files and entries.

主模块 - 翻译SRT文件的核心功能。

本模块将SRT解析器和翻译器模块结合在一起，提供翻译SRT文件的核心功能，并支持进度跟踪。
它支持异步操作，以提高处理多个文件和条目时的性能。
"""

import os
import json
import hashlib
import glob
import asyncio
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Set, Tuple, Union

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

from junie_translator_project.srt_parser import SRTParser, SubtitleEntry
from junie_translator_project.translator import TranslatorService, TranslatorFactory

# Configure logging
logger = logging.getLogger(__name__)


class Config:
    """
    Configuration loader and validator for the translator.
    
    配置加载器和验证器，用于翻译器的配置。
    """
    
    DEFAULT_CONFIG_PATH = "config.json"
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Path to the configuration file (if None, will use default)
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration from the config file.
        
        Returns:
            Configuration dictionary
        
        Raises:
            FileNotFoundError: If the config file doesn't exist
            json.JSONDecodeError: If the config file is not valid JSON
            ValueError: If the config file is missing required fields
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Validate required fields
            if 'to-language' not in config:
                raise ValueError("Config file must contain 'to-language' field")
                
            # Set default values for optional fields
            if 'from-language' not in config:
                config['from-language'] = 'auto'
                
            if 'ai-api-service' not in config:
                config['ai-api-service'] = {
                    'api-service-provider': 'auto',
                    'api-key': None
                }
            elif 'api-service-provider' not in config['ai-api-service']:
                config['ai-api-service']['api-service-provider'] = 'auto'
                
            # Set default prompt style if not provided
            if 'prompt-style' not in config:
                config['prompt-style'] = 'default'
                
            # Set default enable-post-check if not provided
            if 'enable-post-check' not in config:
                config['enable-post-check'] = False
                
            return config
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Config file is not valid JSON: {self.config_path}")
            
    def get_from_language(self) -> str:
        """Get the source language from the config."""
        return self.config.get('from-language', 'auto')
        
    def get_to_language(self) -> str:
        """Get the target language from the config."""
        return self.config['to-language']
        
    def get_api_service_provider(self) -> str:
        """Get the API service provider from the config."""
        return self.config.get('ai-api-service', {}).get('api-service-provider', 'auto')
        
    def get_api_key(self) -> Optional[str]:
        """Get the API key from the config."""
        return self.config.get('ai-api-service', {}).get('api-key')
        
    def get_model(self) -> Optional[str]:
        """Get the model from the config."""
        return self.config.get('model')
        
    def get_output_directory(self) -> Optional[str]:
        """Get the output directory from the config."""
        return self.config.get('output-directory')
        
    def get_prompt_style(self) -> str:
        """Get the prompt style from the config."""
        return self.config.get('prompt-style', 'default')
        
    def get_enable_post_check(self) -> bool:
        """Get the enable-post-check flag from the config."""
        return self.config.get('enable-post-check', False)


class LockFile:
    """Lock file manager to avoid duplicate translations."""
    
    DEFAULT_LOCK_FILE = "junie-translator.lock"
    
    def __init__(self, lock_file_path: Optional[str] = None):
        """
        Initialize the lock file manager.
        
        Args:
            lock_file_path: Path to the lock file (if None, will use default)
        """
        self.lock_file_path = lock_file_path or self.DEFAULT_LOCK_FILE
        self.processed_files: Set[str] = set()
        self._load_lock_file()
        
    def _load_lock_file(self) -> None:
        """Load the lock file if it exists."""
        if os.path.exists(self.lock_file_path):
            try:
                with open(self.lock_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        self.processed_files.add(line.strip())
            except Exception as e:
                print(f"Warning: Failed to load lock file: {e}")
                
    def save_lock_file(self) -> None:
        """Save the lock file."""
        try:
            with open(self.lock_file_path, 'w', encoding='utf-8') as f:
                for file_id in sorted(self.processed_files):
                    f.write(f"{file_id}\n")
        except Exception as e:
            print(f"Warning: Failed to save lock file: {e}")
            
    def is_processed(self, file_id: str) -> bool:
        """
        Check if a file has already been processed.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            True if the file has been processed, False otherwise
        """
        return file_id in self.processed_files
        
    def mark_processed(self, file_id: str) -> None:
        """
        Mark a file as processed.
        
        Args:
            file_id: Unique identifier for the file
        """
        self.processed_files.add(file_id)
        self.save_lock_file()
        
    @staticmethod
    def generate_file_id(input_path: str, from_lang: str, to_lang: str) -> str:
        """
        Generate a unique identifier for a file based on its path and languages.
        
        Args:
            input_path: Path to the input file
            from_lang: Source language
            to_lang: Target language
            
        Returns:
            Unique identifier for the file
        """
        # Calculate hash of the file content
        with open(input_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()[:8]
            
        # Combine file path, languages, and hash
        return f"{input_path}|{from_lang}|{to_lang}|{file_hash}"


class SRTTranslator:
    """
    Main class for translating SRT files.
    
    用于翻译SRT文件的主类。
    """

    def __init__(
        self,
        translator_service: Optional[TranslatorService] = None,
        translator_type: str = "auto",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        show_progress: bool = True,
        lock_file: Optional[LockFile] = None,
        from_language: str = "auto",
        output_directory: Optional[str] = None,
        prompt_style: str = "default",
        enable_post_check: bool = False
    ):
        """
        Initialize the SRT translator.
        
        Args:
            translator_service: A TranslatorService instance (if None, one will be created)
            translator_type: Type of translator service to create if translator_service is None
                            ('auto', 'openai', 'deepseek', 'mock'). If 'auto', will auto-detect
                            based on available API keys in environment variables.
            api_key: API key for the translator service (if None, will try to get from environment)
            model: Model to use for translation (if None, will use service-specific defaults)
            show_progress: Whether to show a progress bar during translation
            lock_file: LockFile instance to track processed files
            from_language: Source language (if 'auto', will be inferred)
            output_directory: Directory for output files
            prompt_style: Style of prompts to use from prompts.json (default, chinese, formal, etc.)
            enable_post_check: If True, checks translated text for explanations and removes them
        """
        self.translator = translator_service or TranslatorFactory.create_translator(
            translator_type, api_key=api_key, model=model, prompt_style=prompt_style,
            enable_post_check=enable_post_check
        )
        self.show_progress = show_progress and TQDM_AVAILABLE
        self.lock_file = lock_file or LockFile()
        self.from_language = from_language
        self.output_directory = output_directory
        
        if self.show_progress and not TQDM_AVAILABLE:
            logger.warning("tqdm is not installed. Progress bar will not be shown.")
            logger.warning("Install tqdm with 'uv pip install tqdm' to enable progress bars.")
            self.show_progress = False
            
        logger.info(f"Initialized SRTTranslator with {type(self.translator).__name__}")
        logger.info(f"Source language: {from_language}, Output directory: {output_directory}")

    def translate_file(
        self,
        input_path: str,
        target_language: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Translate an SRT file to the target language.
        
        Args:
            input_path: Path to the input SRT file
            target_language: Target language code or name
            output_path: Path to the output SRT file (if None, will be generated)
            
        Returns:
            Path to the output SRT file
        """
        logger.info(f"Translating file: {input_path} to {target_language}")
        
        # Generate file ID for lock file
        file_id = LockFile.generate_file_id(input_path, self.from_language, target_language)
        
        # Check if file has already been processed
        if self.lock_file.is_processed(file_id):
            logger.info(f"Skipping already processed file: {input_path}")
            
            # Try to find the output file
            input_path_obj = Path(input_path)
            stem = input_path_obj.stem
            pattern = f"{stem}_{self.from_language}{target_language}_*{input_path_obj.suffix}"
            
            if self.output_directory:
                search_dir = Path(self.output_directory)
            else:
                search_dir = input_path_obj.parent
                
            matches = list(search_dir.glob(pattern))
            if matches:
                logger.info(f"Found existing output file: {matches[0]}")
                return str(matches[0])
            else:
                # If we can't find the output file, regenerate it
                logger.warning(f"Output file not found, regenerating: {input_path}")
            
        # Parse the input file
        logger.debug(f"Parsing input file: {input_path}")
        parser = SRTParser(input_path)
        entries = parser.get_entries()
        logger.info(f"Found {len(entries)} subtitle entries in {input_path}")
        
        # Generate output path if not provided
        if not output_path:
            output_path = SRTParser.generate_output_filename(
                input_path, 
                self.from_language, 
                target_language, 
                self.output_directory
            )
            logger.debug(f"Generated output path: {output_path}")
        
        # Translate each subtitle entry
        logger.info(f"Translating {len(entries)} subtitle entries")
        translated_entries = self._translate_entries(entries, target_language)
        
        # Write the translated entries to the output file
        logger.debug(f"Writing translated entries to: {output_path}")
        SRTParser.write_srt(translated_entries, output_path)
        
        # Mark file as processed
        self.lock_file.mark_processed(file_id)
        logger.info(f"Translation completed: {input_path} -> {output_path}")
        
        return output_path
        
    async def translate_file_async(
        self,
        input_path: str,
        target_language: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Asynchronously translate an SRT file to the target language.
        
        Args:
            input_path: Path to the input SRT file
            target_language: Target language code or name
            output_path: Path to the output SRT file (if None, will be generated)
            
        Returns:
            Path to the output SRT file
        """
        logger.info(f"Async translating file: {input_path} to {target_language}")
        
        # Generate file ID for lock file
        file_id = LockFile.generate_file_id(input_path, self.from_language, target_language)
        
        # Check if file has already been processed
        if self.lock_file.is_processed(file_id):
            logger.info(f"Skipping already processed file: {input_path}")
            
            # Try to find the output file
            input_path_obj = Path(input_path)
            stem = input_path_obj.stem
            pattern = f"{stem}_{self.from_language}{target_language}_*{input_path_obj.suffix}"
            
            if self.output_directory:
                search_dir = Path(self.output_directory)
            else:
                search_dir = input_path_obj.parent
                
            matches = list(search_dir.glob(pattern))
            if matches:
                logger.info(f"Found existing output file: {matches[0]}")
                return str(matches[0])
            else:
                # If we can't find the output file, regenerate it
                logger.warning(f"Output file not found, regenerating: {input_path}")
            
        # Parse the input file
        logger.debug(f"Parsing input file: {input_path}")
        parser = SRTParser(input_path)
        entries = parser.get_entries()
        logger.info(f"Found {len(entries)} subtitle entries in {input_path}")
        
        # Generate output path if not provided
        if not output_path:
            output_path = SRTParser.generate_output_filename(
                input_path, 
                self.from_language, 
                target_language, 
                self.output_directory
            )
            logger.debug(f"Generated output path: {output_path}")
        
        # Translate each subtitle entry asynchronously
        logger.info(f"Async translating {len(entries)} subtitle entries")
        translated_entries = await self._translate_entries_async(entries, target_language)
        
        # Write the translated entries to the output file
        logger.debug(f"Writing translated entries to: {output_path}")
        SRTParser.write_srt(translated_entries, output_path)
        
        # Mark file as processed
        self.lock_file.mark_processed(file_id)
        logger.info(f"Async translation completed: {input_path} -> {output_path}")
        
        return output_path

    def translate_directory(
        self,
        directory_path: str,
        target_language: str,
        file_pattern: str = "*.srt"
    ) -> List[str]:
        """
        Translate all SRT files in a directory.
        
        Args:
            directory_path: Path to the directory containing SRT files
            target_language: Target language code or name
            file_pattern: Pattern to match SRT files (default: "*.srt")
            
        Returns:
            List of paths to the output SRT files
        """
        logger.info(f"Translating all SRT files in directory: {directory_path}")
        
        # Find all SRT files in the directory
        directory_path = Path(directory_path)
        srt_files = list(directory_path.glob(file_pattern))
        
        if not srt_files:
            logger.warning(f"No SRT files found in directory: {directory_path}")
            return []
        
        logger.info(f"Found {len(srt_files)} SRT files matching pattern: {file_pattern}")
        output_files = []
        
        # Set up progress bar if enabled
        iterator = tqdm(srt_files, desc=f"Translating files to {target_language}") if self.show_progress else srt_files
        
        for srt_file in iterator:
            try:
                output_path = self.translate_file(str(srt_file), target_language)
                output_files.append(output_path)
            except Exception as e:
                logger.error(f"Error translating file {srt_file}: {e}", exc_info=True)
        
        logger.info(f"Translated {len(output_files)} files in directory: {directory_path}")
        return output_files
        
    async def translate_directory_async(
        self,
        directory_path: str,
        target_language: str,
        file_pattern: str = "*.srt"
    ) -> List[str]:
        """
        Asynchronously translate all SRT files in a directory.
        
        Args:
            directory_path: Path to the directory containing SRT files
            target_language: Target language code or name
            file_pattern: Pattern to match SRT files (default: "*.srt")
            
        Returns:
            List of paths to the output SRT files
        """
        logger.info(f"Async translating all SRT files in directory: {directory_path}")
        
        # Find all SRT files in the directory
        directory_path = Path(directory_path)
        srt_files = list(directory_path.glob(file_pattern))
        
        if not srt_files:
            logger.warning(f"No SRT files found in directory: {directory_path}")
            return []
        
        logger.info(f"Found {len(srt_files)} SRT files matching pattern: {file_pattern}")
        
        # Create tasks for each file
        tasks = []
        for srt_file in srt_files:
            tasks.append(self.translate_file_async(str(srt_file), target_language))
        
        # Run tasks concurrently with progress bar if enabled
        if self.show_progress:
            output_files = []
            for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"Translating files to {target_language}"):
                try:
                    output_path = await f
                    output_files.append(output_path)
                except Exception as e:
                    logger.error(f"Error translating file: {e}", exc_info=True)
        else:
            # Run all tasks concurrently without progress bar
            results = await asyncio.gather(*tasks, return_exceptions=True)
            output_files = [r for r in results if not isinstance(r, Exception)]
            
            # Log any errors
            for r in results:
                if isinstance(r, Exception):
                    logger.error(f"Error translating file: {r}", exc_info=True)
        
        logger.info(f"Async translated {len(output_files)} files in directory: {directory_path}")
        return output_files

    def _translate_entries(
        self,
        entries: List[SubtitleEntry],
        target_language: str
    ) -> List[SubtitleEntry]:
        """
        Translate subtitle entries to the target language.
        
        Args:
            entries: List of SubtitleEntry objects
            target_language: Target language code or name
            
        Returns:
            List of translated SubtitleEntry objects
        """
        logger.debug(f"Translating {len(entries)} subtitle entries to {target_language}")
        translated_entries = []
        
        # Set up progress bar if enabled
        iterator = tqdm(entries, desc=f"Translating to {target_language}") if self.show_progress else entries
        
        for entry in iterator:
            # Translate each line in the entry's content
            translated_content = []
            for line in entry.content:
                translated_line = self.translator.translate(line, target_language)
                translated_content.append(translated_line)
            
            # Create a new entry with the translated content
            translated_entry = SubtitleEntry(
                index=entry.index,
                start_time=entry.start_time,
                end_time=entry.end_time,
                content=translated_content
            )
            
            translated_entries.append(translated_entry)
        
        logger.debug(f"Completed translating {len(entries)} subtitle entries")
        return translated_entries
        
    async def _translate_entries_async(
        self,
        entries: List[SubtitleEntry],
        target_language: str
    ) -> List[SubtitleEntry]:
        """
        Asynchronously translate subtitle entries to the target language.
        
        Args:
            entries: List of SubtitleEntry objects
            target_language: Target language code or name
            
        Returns:
            List of translated SubtitleEntry objects
        """
        logger.debug(f"Async translating {len(entries)} subtitle entries to {target_language}")
        
        async def translate_entry(entry: SubtitleEntry) -> SubtitleEntry:
            """Translate a single subtitle entry asynchronously."""
            # Translate each line in the entry's content
            tasks = [self.translator.translate_async(line, target_language) for line in entry.content]
            translated_content = await asyncio.gather(*tasks)
            
            # Create a new entry with the translated content
            return SubtitleEntry(
                index=entry.index,
                start_time=entry.start_time,
                end_time=entry.end_time,
                content=translated_content
            )
        
        # Create tasks for each entry
        tasks = [translate_entry(entry) for entry in entries]
        
        # Run tasks with progress bar if enabled
        if self.show_progress:
            translated_entries = []
            for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"Translating to {target_language}"):
                translated_entry = await f
                translated_entries.append(translated_entry)
                
            # Sort entries by index to maintain order
            translated_entries.sort(key=lambda e: e.index)
        else:
            # Run all tasks concurrently
            translated_entries = await asyncio.gather(*tasks)
        
        logger.debug(f"Completed async translating {len(entries)} subtitle entries")
        return translated_entries


def translate_srt(
    input_path: str,
    target_language: str,
    output_path: Optional[str] = None,
    translator_type: str = "auto",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    show_progress: bool = True,
    from_language: str = "auto",
    output_directory: Optional[str] = None,
    lock_file_path: Optional[str] = None,
    enable_post_check: bool = False
) -> str:
    """
    Convenience function to translate an SRT file.
    
    Args:
        input_path: Path to the input SRT file
        target_language: Target language code or name
        output_path: Path to the output SRT file (if None, will be generated)
        translator_type: Type of translator service to use ('auto', 'openai', 'deepseek', 'mock')
        api_key: API key for the translator service (if None, will try to get from environment)
        model: Model to use for translation (if None, will use service-specific defaults:
              gpt-3.5-turbo for OpenAI, deepseek-v3 for DeepSeek)
        show_progress: Whether to show a progress bar during translation
        from_language: Source language (if 'auto', will be inferred)
        output_directory: Directory for output files
        lock_file_path: Path to the lock file
        enable_post_check: If True, checks translated text for explanations and removes them
        
    Returns:
        Path to the output SRT file
    """
    lock_file = LockFile(lock_file_path)
    
    translator = SRTTranslator(
        translator_type=translator_type,
        api_key=api_key,
        model=model,
        show_progress=show_progress,
        lock_file=lock_file,
        from_language=from_language,
        output_directory=output_directory,
        enable_post_check=enable_post_check
    )
    
    return translator.translate_file(input_path, target_language, output_path)


def translate_directory(
    directory_path: str,
    target_language: str,
    translator_type: str = "auto",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    show_progress: bool = True,
    from_language: str = "auto",
    output_directory: Optional[str] = None,
    lock_file_path: Optional[str] = None,
    file_pattern: str = "*.srt",
    enable_post_check: bool = False
) -> List[str]:
    """
    Convenience function to translate all SRT files in a directory.
    
    Args:
        directory_path: Path to the directory containing SRT files
        target_language: Target language code or name
        translator_type: Type of translator service to use ('auto', 'openai', 'deepseek', 'mock')
        api_key: API key for the translator service (if None, will try to get from environment)
        model: Model to use for translation (if None, will use service-specific defaults)
        show_progress: Whether to show a progress bar during translation
        from_language: Source language (if 'auto', will be inferred)
        output_directory: Directory for output files
        lock_file_path: Path to the lock file
        file_pattern: Pattern to match SRT files (default: "*.srt")
        enable_post_check: If True, checks translated text for explanations and removes them
        
    Returns:
        List of paths to the output SRT files
    """
    lock_file = LockFile(lock_file_path)
    
    translator = SRTTranslator(
        translator_type=translator_type,
        api_key=api_key,
        model=model,
        show_progress=show_progress,
        lock_file=lock_file,
        from_language=from_language,
        output_directory=output_directory,
        enable_post_check=enable_post_check
    )
    
    return translator.translate_directory(directory_path, target_language, file_pattern)


def get_api_key_from_github_secrets(service_provider: str) -> Optional[str]:
    """
    Try to get API key from GitHub Secrets environment variables.
    
    Args:
        service_provider: The service provider ('openai', 'deepseek', etc.)
        
    Returns:
        API key if found, None otherwise
    """
    # GitHub Actions sets secrets as environment variables
    if service_provider.lower() == 'openai':
        # Try different possible environment variable names
        for env_var in ['OPENAI_API_KEY', 'OPENAI_KEY', 'GITHUB_OPENAI_API_KEY']:
            api_key = os.environ.get(env_var)
            if api_key:
                logger.info(f"Found OpenAI API key in GitHub Secrets: {env_var}")
                return api_key
    elif service_provider.lower() == 'deepseek':
        # Try different possible environment variable names
        for env_var in ['DEEPSEEK_API_KEY', 'DEEPSEEK_KEY', 'GITHUB_DEEPSEEK_API_KEY']:
            api_key = os.environ.get(env_var)
            if api_key:
                logger.info(f"Found DeepSeek API key in GitHub Secrets: {env_var}")
                return api_key
    
    # Check for generic API keys
    for env_var in ['API_KEY', 'GITHUB_API_KEY', 'AI_API_KEY']:
        api_key = os.environ.get(env_var)
        if api_key:
            logger.info(f"Found generic API key in GitHub Secrets: {env_var}")
            return api_key
            
    return None

async def main_async(config_path: Optional[str] = None) -> int:
    """
    Asynchronous main function to load config and execute translation.
    
    Args:
        config_path: Path to the configuration file (if None, will use default)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Load configuration
        logger.info(f"Loading configuration from: {config_path or Config.DEFAULT_CONFIG_PATH}")
        config = Config(config_path)
        
        # Create lock file
        lock_file = LockFile()
        
        # Get API key from config or GitHub Secrets
        api_key = config.get_api_key()
        if not api_key:
            logger.info("No API key found in config, trying to get from GitHub Secrets")
            api_key = get_api_key_from_github_secrets(config.get_api_service_provider())
            if api_key:
                logger.info("Successfully retrieved API key from GitHub Secrets")
            else:
                logger.warning("No API key found in GitHub Secrets")
        
        # Create translator
        logger.info(f"Creating translator with service provider: {config.get_api_service_provider()}, prompt style: {config.get_prompt_style()}")
        logger.info(f"正在创建翻译器，服务提供商: {config.get_api_service_provider()}，提示风格: {config.get_prompt_style()}")
        translator = SRTTranslator(
            translator_type=config.get_api_service_provider(),
            api_key=api_key,
            model=config.get_model(),
            show_progress=True,
            lock_file=lock_file,
            from_language=config.get_from_language(),
            output_directory=config.get_output_directory(),
            prompt_style=config.get_prompt_style(),
            enable_post_check=config.get_enable_post_check()
        )
        
        # Translate all SRT files in the current directory asynchronously
        logger.info(f"Starting async translation to {config.get_to_language()}")
        output_files = await translator.translate_directory_async(
            ".", 
            config.get_to_language()
        )
        
        if output_files:
            logger.info(f"Translation completed successfully. {len(output_files)} files translated.")
            logger.info(f"翻译成功完成。已翻译 {len(output_files)} 个文件。")
            return 0
        else:
            logger.warning("No files were translated.")
            logger.warning("没有文件被翻译。")
            return 1
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

def main(config_path: Optional[str] = None) -> int:
    """
    Main function to load config and execute translation.
    
    Args:
        config_path: Path to the configuration file (if None, will use default)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Run the async main function
        return asyncio.run(main_async(config_path))
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1