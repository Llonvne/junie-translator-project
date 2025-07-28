"""
Translator Module - Handles translation of text using AI services.

This module provides an extensible framework for translating text using
various AI services like OpenAI, DeepSeek, or other compatible services.
It supports both synchronous and asynchronous translation methods.

Supported translator services:
- OpenAI: Uses OpenAI's GPT models for translation
- DeepSeek: Uses DeepSeek's R1 and V3 models for translation
- Mock: A simple mock translator for testing purposes

翻译模块 - 使用AI服务处理文本翻译。

本模块提供了一个可扩展的框架，使用各种AI服务（如OpenAI、DeepSeek或其他兼容服务）
来翻译文本。它支持同步和异步翻译方法。

支持的翻译服务：
- OpenAI：使用OpenAI的GPT模型进行翻译
- DeepSeek：使用DeepSeek的R1和V3模型进行翻译
- Mock：一个简单的模拟翻译器，用于测试目的
"""

import abc
import os
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Try to import OpenAI, but don't fail if it's not installed
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Default prompts if prompts.json is not available
DEFAULT_PROMPTS = {
    "default": {
        "system": "You are a professional translator. Translate the text accurately while preserving the original meaning, tone, and formatting.",
        "user": "Translate the following text to {target_language}. Preserve any formatting and special characters:\n\n{text}"
    }
}

def load_prompts(prompt_style: str = "default") -> Tuple[str, str]:
    """
    Load translation prompts from prompts.json file.
    
    Args:
        prompt_style: The style of prompts to use (default, chinese, formal, etc.)
        
    Returns:
        A tuple of (system_prompt, user_prompt_template)
    """
    prompts_file = Path("prompts.json")
    
    try:
        if prompts_file.exists():
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts = json.load(f)
                
            # If the requested style doesn't exist, fall back to default
            if prompt_style not in prompts:
                logger.warning(f"Prompt style '{prompt_style}' not found in prompts.json, using default")
                prompt_style = "default"
                
            # If default doesn't exist either, use hardcoded defaults
            if prompt_style not in prompts:
                logger.warning("Default prompts not found in prompts.json, using built-in defaults")
                return DEFAULT_PROMPTS["default"]["system"], DEFAULT_PROMPTS["default"]["user"]
                
            return prompts[prompt_style]["system"], prompts[prompt_style]["user"]
        else:
            logger.warning("prompts.json not found, using built-in default prompts")
            return DEFAULT_PROMPTS["default"]["system"], DEFAULT_PROMPTS["default"]["user"]
    except Exception as e:
        logger.error(f"Error loading prompts: {e}", exc_info=True)
        return DEFAULT_PROMPTS["default"]["system"], DEFAULT_PROMPTS["default"]["user"]


class TranslatorService(abc.ABC):
    """Abstract base class for translator services."""

    @abc.abstractmethod
    def translate(self, text: str, target_language: str) -> str:
        """
        Translate the given text to the target language.
        
        Args:
            text: The text to translate
            target_language: The target language code or name
            
        Returns:
            The translated text
        """
        pass

    @abc.abstractmethod
    def batch_translate(self, texts: List[str], target_language: str) -> List[str]:
        """
        Translate a batch of texts to the target language.
        
        Args:
            texts: List of texts to translate
            target_language: The target language code or name
            
        Returns:
            List of translated texts
        """
        pass
        
    @abc.abstractmethod
    async def translate_async(self, text: str, target_language: str) -> str:
        """
        Asynchronously translate the given text to the target language.
        
        Args:
            text: The text to translate
            target_language: The target language code or name
            
        Returns:
            The translated text
        """
        pass
        
    @abc.abstractmethod
    async def batch_translate_async(self, texts: List[str], target_language: str) -> List[str]:
        """
        Asynchronously translate a batch of texts to the target language.
        
        Args:
            texts: List of texts to translate
            target_language: The target language code or name
            
        Returns:
            List of translated texts
        """
        pass


class OpenAITranslator(TranslatorService):
    """Translator service using OpenAI API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", prompt_style: str = "default"):
        """
        Initialize the OpenAI translator.
        
        Args:
            api_key: OpenAI API key (if None, will try to get from environment)
            model: OpenAI model to use for translation
            prompt_style: Style of prompts to use from prompts.json (default, chinese, formal, etc.)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package is not installed. "
                "Please install it with 'uv pip install openai'"
            )
        
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. "
                "Either pass it as an argument or set the OPENAI_API_KEY environment variable."
            )
        
        self.model = model
        self.prompt_style = prompt_style
        self.system_prompt, self.user_prompt_template = load_prompts(prompt_style)
        self.client = openai.OpenAI(api_key=self.api_key)
        logger.info(f"Initialized OpenAI translator with model: {model}, prompt style: {prompt_style}")

    def translate(self, text: str, target_language: str) -> str:
        """
        Translate the given text to the target language using OpenAI.
        
        Args:
            text: The text to translate
            target_language: The target language code or name
            
        Returns:
            The translated text
        """
        logger.debug(f"Translating text to {target_language} using OpenAI with {self.prompt_style} prompt style")
        
        # Format the user prompt template with the target language and text
        user_prompt = self.user_prompt_template.format(target_language=target_language, text=text)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        
        translated_text = response.choices[0].message.content.strip()
        logger.debug(f"Translation completed: {len(translated_text)} characters")
        return translated_text

    def batch_translate(self, texts: List[str], target_language: str) -> List[str]:
        """
        Translate a batch of texts to the target language.
        
        Note: This implementation translates one text at a time to ensure
        accurate translations and to avoid exceeding token limits.
        
        Args:
            texts: List of texts to translate
            target_language: The target language code or name
            
        Returns:
            List of translated texts
        """
        logger.info(f"Batch translating {len(texts)} texts to {target_language}")
        return [self.translate(text, target_language) for text in texts]
        
    async def translate_async(self, text: str, target_language: str) -> str:
        """
        Asynchronously translate the given text to the target language using OpenAI.
        
        Args:
            text: The text to translate
            target_language: The target language code or name
            
        Returns:
            The translated text
        """
        logger.debug(f"Async translating text to {target_language} using OpenAI")
        
        # Use a thread pool to run the synchronous API call asynchronously
        loop = asyncio.get_event_loop()
        translated_text = await loop.run_in_executor(
            None, lambda: self.translate(text, target_language)
        )
        
        logger.debug(f"Async translation completed: {len(translated_text)} characters")
        return translated_text
        
    async def batch_translate_async(self, texts: List[str], target_language: str) -> List[str]:
        """
        Asynchronously translate a batch of texts to the target language.
        
        This implementation creates tasks for each text and runs them concurrently
        for improved performance.
        
        Args:
            texts: List of texts to translate
            target_language: The target language code or name
            
        Returns:
            List of translated texts
        """
        logger.info(f"Async batch translating {len(texts)} texts to {target_language}")
        
        # Create tasks for each text
        tasks = [self.translate_async(text, target_language) for text in texts]
        
        # Run tasks concurrently and gather results
        translated_texts = await asyncio.gather(*tasks)
        
        logger.info(f"Async batch translation completed for {len(texts)} texts")
        return translated_texts


class DeepSeekTranslator(TranslatorService):
    """Translator service using DeepSeek API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-v3", prompt_style: str = "default"):
        """
        Initialize the DeepSeek translator.
        
        Args:
            api_key: DeepSeek API key (if None, will try to get from environment)
            model: DeepSeek model to use for translation (deepseek-r1 or deepseek-v3)
            prompt_style: Style of prompts to use from prompts.json (default, chinese, formal, etc.)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package is not installed. "
                "Please install it with 'uv pip install openai'"
            )
        
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key is required. "
                "Either pass it as an argument or set the DEEPSEEK_API_KEY environment variable."
            )
        
        # Validate and normalize model name
        if model.lower() in ["deepseek-r1", "r1", "deepseek-reasoner"]:
            self.model = "deepseek-reasoner"
        elif model.lower() in ["deepseek-v3", "v3", "deepseek-chat"]:
            self.model = "deepseek-chat"
        else:
            raise ValueError(
                f"Unsupported DeepSeek model: {model}. "
                "Supported models are: deepseek-r1 (maps to deepseek-reasoner), deepseek-v3 (maps to deepseek-chat)"
            )
        
        # Load prompts from prompts.json
        self.prompt_style = prompt_style
        self.system_prompt, self.user_prompt_template = load_prompts(prompt_style)
        
        # DeepSeek uses OpenAI-compatible API with a different base URL
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com/v1"  # DeepSeek API endpoint
        )
        
        logger.info(f"Initialized DeepSeek translator with model: {self.model}, prompt style: {prompt_style}")

    def translate(self, text: str, target_language: str) -> str:
        """
        Translate the given text to the target language using DeepSeek.
        
        Args:
            text: The text to translate
            target_language: The target language code or name
            
        Returns:
            The translated text
        """
        logger.debug(f"Translating text to {target_language} using DeepSeek with {self.prompt_style} prompt style")
        
        # Format the user prompt template with the target language and text
        user_prompt = self.user_prompt_template.format(target_language=target_language, text=text)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        
        translated_text = response.choices[0].message.content.strip()
        logger.debug(f"Translation completed: {len(translated_text)} characters")
        return translated_text

    def batch_translate(self, texts: List[str], target_language: str) -> List[str]:
        """
        Translate a batch of texts to the target language.
        
        Note: This implementation translates one text at a time to ensure
        accurate translations and to avoid exceeding token limits.
        
        Args:
            texts: List of texts to translate
            target_language: The target language code or name
            
        Returns:
            List of translated texts
        """
        logger.info(f"Batch translating {len(texts)} texts to {target_language}")
        return [self.translate(text, target_language) for text in texts]
        
    async def translate_async(self, text: str, target_language: str) -> str:
        """
        Asynchronously translate the given text to the target language using DeepSeek.
        
        Args:
            text: The text to translate
            target_language: The target language code or name
            
        Returns:
            The translated text
        """
        logger.debug(f"Async translating text to {target_language} using DeepSeek")
        
        # Use a thread pool to run the synchronous API call asynchronously
        loop = asyncio.get_event_loop()
        translated_text = await loop.run_in_executor(
            None, lambda: self.translate(text, target_language)
        )
        
        logger.debug(f"Async translation completed: {len(translated_text)} characters")
        return translated_text
        
    async def batch_translate_async(self, texts: List[str], target_language: str) -> List[str]:
        """
        Asynchronously translate a batch of texts to the target language.
        
        This implementation creates tasks for each text and runs them concurrently
        for improved performance.
        
        Args:
            texts: List of texts to translate
            target_language: The target language code or name
            
        Returns:
            List of translated texts
        """
        logger.info(f"Async batch translating {len(texts)} texts to {target_language}")
        
        # Create tasks for each text
        tasks = [self.translate_async(text, target_language) for text in texts]
        
        # Run tasks concurrently and gather results
        translated_texts = await asyncio.gather(*tasks)
        
        logger.info(f"Async batch translation completed for {len(texts)} texts")
        return translated_texts


class MockTranslator(TranslatorService):
    """Mock translator service for testing purposes."""
    
    def __init__(self):
        """Initialize the mock translator."""
        logger.info("Initialized Mock translator")

    def translate(self, text: str, target_language: str) -> str:
        """
        Mock translation that just adds a prefix to the text.
        
        Args:
            text: The text to translate
            target_language: The target language code or name
            
        Returns:
            The "translated" text
        """
        logger.debug(f"Mock translating text to {target_language}")
        translated_text = f"[{target_language}] {text}"
        logger.debug(f"Mock translation completed: {len(translated_text)} characters")
        return translated_text

    def batch_translate(self, texts: List[str], target_language: str) -> List[str]:
        """
        Mock batch translation.
        
        Args:
            texts: List of texts to translate
            target_language: The target language code or name
            
        Returns:
            List of "translated" texts
        """
        logger.info(f"Mock batch translating {len(texts)} texts to {target_language}")
        return [self.translate(text, target_language) for text in texts]
        
    async def translate_async(self, text: str, target_language: str) -> str:
        """
        Asynchronously mock translate the given text.
        
        Args:
            text: The text to translate
            target_language: The target language code or name
            
        Returns:
            The "translated" text
        """
        logger.debug(f"Async mock translating text to {target_language}")
        
        # Simulate a small delay to mimic async processing
        await asyncio.sleep(0.01)
        
        translated_text = f"[{target_language}] {text}"
        logger.debug(f"Async mock translation completed: {len(translated_text)} characters")
        return translated_text
        
    async def batch_translate_async(self, texts: List[str], target_language: str) -> List[str]:
        """
        Asynchronously mock translate a batch of texts.
        
        Args:
            texts: List of texts to translate
            target_language: The target language code or name
            
        Returns:
            List of "translated" texts
        """
        logger.info(f"Async mock batch translating {len(texts)} texts to {target_language}")
        
        # Create tasks for each text
        tasks = [self.translate_async(text, target_language) for text in texts]
        
        # Run tasks concurrently and gather results
        translated_texts = await asyncio.gather(*tasks)
        
        logger.info(f"Async mock batch translation completed for {len(texts)} texts")
        return translated_texts


class TranslatorFactory:
    """Factory for creating translator service instances."""
    
    @staticmethod
    def detect_available_services():
        """
        Detect available translator services based on environment variables.
        
        Returns:
            A list of available service types ('openai', 'deepseek', 'mock')
        """
        available_services = ['mock']  # Mock is always available
        
        # Check for OpenAI API key
        if os.environ.get("OPENAI_API_KEY"):
            available_services.append('openai')
            
        # Check for DeepSeek API key
        if os.environ.get("DEEPSEEK_API_KEY"):
            available_services.append('deepseek')
            
        return available_services
    
    @staticmethod
    def get_default_model(service_type: str) -> str:
        """
        Get the default model for a given service type.
        
        Args:
            service_type: Type of translator service ('openai', 'deepseek')
            
        Returns:
            The default model name for the service
        """
        if service_type.lower() == 'openai':
            return "gpt-3.5-turbo"
        elif service_type.lower() == 'deepseek':
            return "deepseek-v3"  # This will be mapped to "deepseek-chat" in DeepSeekTranslator
        else:
            return ""
    
    @staticmethod
    def create_translator(service_type: str = "auto", **kwargs) -> TranslatorService:
        """
        Create a translator service instance.
        
        Args:
            service_type: Type of translator service ('openai', 'deepseek', 'mock', 'auto')
                          If 'auto', will auto-detect based on available API keys
            **kwargs: Additional arguments to pass to the translator constructor
                      - api_key: API key for the service
                      - model: Model to use for translation
                      - prompt_style: Style of prompts to use (default, chinese, formal, etc.)
            
        Returns:
            A TranslatorService instance
            
        Raises:
            ValueError: If the service type is not supported or no services are available
        """
        # Auto-detect service if requested
        if service_type.lower() == 'auto':
            available_services = TranslatorFactory.detect_available_services()
            # Prefer OpenAI, then DeepSeek, then Mock
            if 'openai' in available_services:
                service_type = 'openai'
            elif 'deepseek' in available_services:
                service_type = 'deepseek'
            elif 'mock' in available_services:
                service_type = 'mock'
            else:
                raise ValueError("No translator services available. Please set OPENAI_API_KEY or DEEPSEEK_API_KEY environment variables.")
        
        # Set default model if not provided
        if 'model' not in kwargs:
            default_model = TranslatorFactory.get_default_model(service_type)
            if default_model:
                kwargs['model'] = default_model
        
        # Create the appropriate translator
        if service_type.lower() == 'openai':
            return OpenAITranslator(**kwargs)
        elif service_type.lower() == 'deepseek':
            return DeepSeekTranslator(**kwargs)
        elif service_type.lower() == 'mock':
            # MockTranslator doesn't use prompt_style, so we don't pass it
            return MockTranslator()
        else:
            raise ValueError(f"Unsupported translator service type: {service_type}")