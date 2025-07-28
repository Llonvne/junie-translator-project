"""
Translator Module - Handles translation of text using AI services.

This module provides an extensible framework for translating text using
various AI services configured in aiprovider.json.
It supports both synchronous and asynchronous translation methods.

Supported translator services:
- AI Provider: Uses configuration from aiprovider.json for translation
- Mock: A simple mock translator for testing purposes

翻译模块 - 使用AI服务处理文本翻译。

本模块提供了一个可扩展的框架，使用在aiprovider.json中配置的各种AI服务
来翻译文本。它支持同步和异步翻译方法。

支持的翻译服务：
- AI Provider：使用aiprovider.json中的配置进行翻译
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

def load_aiprovider_config() -> Dict[str, Any]:
    """
    Load AI provider configuration from aiprovider.json file.
    
    Returns:
        A dictionary containing the AI provider configuration
    """
    config_file = Path("aiprovider.json")
    
    try:
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get("providers", {})
        else:
            logger.warning("aiprovider.json not found, using built-in defaults")
            return {}
    except Exception as e:
        logger.error(f"Error loading AI provider configuration: {e}", exc_info=True)
        return {}

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


class AIProviderTranslator(TranslatorService):
    """Translator service using AI providers configured in aiprovider.json."""

    def __init__(self, provider: str, api_key: Optional[str] = None, model: Optional[str] = None, prompt_style: str = "default"):
        """
        Initialize the AI provider translator.
        
        Args:
            provider: The AI provider to use (e.g., 'openai', 'deepseek')
            api_key: API key for the provider (if None, will try to get from environment)
            model: Model to use for translation (if None, will use provider's default)
            prompt_style: Style of prompts to use from prompts.json (default, chinese, formal, etc.)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package is not installed. "
                "Please install it with 'uv pip install openai'"
            )
        
        # Load AI provider configuration
        self.providers_config = load_aiprovider_config()
        if not self.providers_config:
            raise ValueError("No AI provider configuration found. Please create aiprovider.json file.")
        
        # Validate provider
        if provider.lower() not in self.providers_config:
            raise ValueError(
                f"Unsupported AI provider: {provider}. "
                f"Supported providers are: {', '.join(self.providers_config.keys())}"
            )
        
        self.provider = provider.lower()
        self.provider_config = self.providers_config[self.provider]
        
        # Get API key from argument, environment, or raise error
        env_var_name = f"{self.provider.upper()}_API_KEY"
        self.api_key = api_key or os.environ.get(env_var_name)
        if not self.api_key and self.provider != "mock":
            raise ValueError(
                f"{self.provider.capitalize()} API key is required. "
                f"Either pass it as an argument or set the {env_var_name} environment variable."
            )
        
        # Get API endpoint from configuration
        self.api_endpoint = self.provider_config.get("api-endpoint")
        
        # Get available models for this provider
        self.available_models = self.provider_config.get("models", {})
        if not self.available_models and self.provider != "mock":
            raise ValueError(f"No models configured for provider: {self.provider}")
        
        # Validate and normalize model name
        self.model = self._normalize_model_name(model)
        
        # Get model configuration
        self.model_config = self.available_models.get(self.model, {}) if self.model else {}
        
        # Load prompts from prompts.json
        self.prompt_style = prompt_style
        self.system_prompt, self.user_prompt_template = load_prompts(prompt_style)
        
        # Initialize OpenAI client with appropriate base URL
        if self.provider != "mock":
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.api_endpoint
            )
        
        logger.info(f"Initialized {self.provider.capitalize()} translator with model: {self.model}, prompt style: {prompt_style}")

    def _normalize_model_name(self, model: Optional[str]) -> str:
        """
        Normalize the model name based on provider configuration.
        
        Args:
            model: The model name to normalize
            
        Returns:
            The normalized model name
        """
        if not model:
            # Use the first model in the configuration as default
            return next(iter(self.available_models)) if self.available_models else "mock"
        
        # Check if the model exists directly
        if model in self.available_models:
            return model
        
        # Check if the model is an alias for another model
        for model_name, config in self.available_models.items():
            aliases = config.get("aliases", [])
            if model in aliases:
                return model_name
        
        # If model not found, raise error
        raise ValueError(
            f"Unsupported model for {self.provider}: {model}. "
            f"Supported models are: {', '.join(self.available_models.keys())}"
        )

    def translate(self, text: str, target_language: str) -> str:
        """
        Translate the given text to the target language using the configured AI provider.
        
        Args:
            text: The text to translate
            target_language: The target language code or name
            
        Returns:
            The translated text
        """
        if self.provider == "mock":
            # Mock translation
            logger.debug(f"Mock translating text to {target_language}")
            translated_text = f"[{target_language}] {text}"
            logger.debug(f"Mock translation completed: {len(translated_text)} characters")
            return translated_text
        
        logger.debug(f"Translating text to {target_language} using {self.provider} with {self.prompt_style} prompt style")
        
        # Format the user prompt template with the target language and text
        user_prompt = self.user_prompt_template.format(target_language=target_language, text=text)
        
        # Get model-specific configuration
        max_tokens = self.model_config.get("max-tokens", 1024)
        temperature = self.model_config.get("temperature", 0.3)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
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
        Asynchronously translate the given text to the target language.
        
        Args:
            text: The text to translate
            target_language: The target language code or name
            
        Returns:
            The translated text
        """
        if self.provider == "mock":
            # Mock translation with a small delay
            logger.debug(f"Async mock translating text to {target_language}")
            await asyncio.sleep(0.01)
            translated_text = f"[{target_language}] {text}"
            logger.debug(f"Async mock translation completed: {len(translated_text)} characters")
            return translated_text
        
        logger.debug(f"Async translating text to {target_language} using {self.provider}")
        
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
        Detect available translator services based on environment variables and aiprovider.json.
        
        Returns:
            A list of available service types from aiprovider.json
        """
        available_services = ['mock']  # Mock is always available
        
        # Load provider configuration
        providers_config = load_aiprovider_config()
        
        # Check for API keys for each provider
        for provider in providers_config:
            if provider != 'mock':
                env_var_name = f"{provider.upper()}_API_KEY"
                if os.environ.get(env_var_name):
                    available_services.append(provider)
            
        return available_services
    
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
                raise ValueError("No translator services available. Please set appropriate API_KEY environment variables.")
        
        # Create the appropriate translator
        if service_type.lower() == 'mock':
            # MockTranslator is simpler and doesn't need all the configuration
            return MockTranslator()
        else:
            # Use AIProviderTranslator for all other providers
            return AIProviderTranslator(provider=service_type, **kwargs)