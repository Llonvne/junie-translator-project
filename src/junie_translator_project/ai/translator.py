"""
Translator Module - Handles translation of text using AI services.

This module provides an extensible framework for translating text using
various AI services. It adapts the original translator.py module to use
the new entity models.

翻译模块 - 使用AI服务处理文本翻译。

该模块提供了一个可扩展的框架，使用各种AI服务翻译文本。
它改编了原始的translator.py模块，以使用新的实体模型。
"""

import abc
import os
import asyncio
import logging
from typing import List, Optional, Dict, Any, Union

# Import entity models
from junie_translator_project.entity.ai_model import AIModel, AIProvider, AIProviderRegistry
from junie_translator_project.entity.prompt import PromptTemplate, PromptStyle, PromptRegistry, get_default_prompt_registry
from junie_translator_project.entity.config import AIServiceConfig

# Configure logging
logger = logging.getLogger(__name__)

# Try to import OpenAI, but don't fail if it's not installed
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


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
    """Translator service using AI providers."""

    def __init__(
        self, 
        provider: Union[str, AIProvider], 
        api_key: Optional[str] = None, 
        model: Optional[str] = None, 
        prompt_style: Union[str, PromptStyle] = "default", 
        enable_post_check: bool = False,
        provider_registry: Optional[AIProviderRegistry] = None,
        prompt_registry: Optional[PromptRegistry] = None
    ):
        """
        Initialize the AI provider translator.
        
        Args:
            provider: The AI provider to use (name or AIProvider instance)
            api_key: API key for the provider (if None, will try to get from environment)
            model: Model to use for translation (if None, will use provider's default)
            prompt_style: Style of prompts to use (name or PromptStyle instance)
            enable_post_check: If True, checks translated text for explanations and removes them
            provider_registry: Registry of AI providers (if None, will try to load from aiprovider.json)
            prompt_registry: Registry of prompt styles (if None, will try to load from prompts.json)
        """
        self.enable_post_check = enable_post_check
        
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package is not installed. "
                "Please install it with 'uv pip install openai'"
            )
        
        # Load provider registry if not provided
        if provider_registry is None:
            try:
                self.provider_registry = AIProviderRegistry.load_from_file("aiprovider.json")
            except Exception as e:
                logger.warning(f"Failed to load AI provider registry: {e}")
                raise ValueError("No AI provider registry available. Please provide a valid provider_registry.")
        else:
            self.provider_registry = provider_registry
        
        # Get provider
        if isinstance(provider, str):
            provider_name = provider.lower()
            provider_obj = self.provider_registry.get_provider(provider_name)
            if provider_obj is None:
                raise ValueError(
                    f"Unsupported AI provider: {provider}. "
                    f"Supported providers are: {', '.join(self.provider_registry.get_provider_names())}"
                )
            self.provider = provider_obj
        else:
            self.provider = provider
        
        # Get API key from argument, environment, or raise error
        env_var_name = f"{self.provider.name.upper()}_API_KEY"
        self.api_key = api_key or os.environ.get(env_var_name)
        if not self.api_key and self.provider.name != "mock":
            raise ValueError(
                f"{self.provider.name.capitalize()} API key is required. "
                f"Either pass it as an argument or set the {env_var_name} environment variable."
            )
        
        # Validate and normalize model name
        self.model_name = self._normalize_model_name(model)
        self.model = self.provider.get_model(self.model_name)
        
        # Load prompt registry if not provided
        if prompt_registry is None:
            try:
                self.prompt_registry = PromptRegistry.load_from_file("prompts.json")
            except Exception as e:
                logger.warning(f"Failed to load prompt registry: {e}")
                self.prompt_registry = get_default_prompt_registry()
        else:
            self.prompt_registry = prompt_registry
        
        # Get prompt style
        if isinstance(prompt_style, str):
            self.prompt_style = self.prompt_registry.get_style(prompt_style)
        else:
            self.prompt_style = prompt_style
        
        # Initialize OpenAI client with appropriate base URL
        if self.provider.name != "mock":
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.provider.api_endpoint
            )
        
        logger.info(f"Initialized {self.provider.name.capitalize()} translator with model: {self.model_name}, prompt style: {self.prompt_style.name}")

    def _normalize_model_name(self, model: Optional[str]) -> str:
        """
        Normalize the model name based on provider configuration.
        
        Args:
            model: The model name to normalize
            
        Returns:
            The normalized model name
        """
        if not model:
            # Use the first model in the provider as default
            model_names = self.provider.get_model_names()
            if not model_names:
                raise ValueError(f"No models available for provider: {self.provider.name}")
            return model_names[0]
        
        # Check if the model exists directly or as an alias
        if self.provider.get_model(model) is not None:
            return model
        
        # If model not found, raise error
        raise ValueError(
            f"Unsupported model for {self.provider.name}: {model}. "
            f"Supported models are: {', '.join(self.provider.get_model_names())}"
        )
        
    def _post_check_translation(self, translated_text: str) -> str:
        """
        Check translated text for explanations and remove them if found.
        
        This method sends the translated text to the AI to check if it contains
        explanations, notes, or additional content beyond the translation itself.
        If such content is found, it is removed to return only the pure translation.
        
        Args:
            translated_text: The translated text to check
            
        Returns:
            The cleaned translated text with explanations removed (if any)
        """
        if not self.enable_post_check or self.provider.name == "mock":
            return translated_text
            
        logger.debug("Performing post-check on translated text")
        
        # Create a prompt specifically for checking explanations
        system_prompt = "You are a translation validator. Your task is to identify and remove any explanations, notes, or additional content that is not part of the actual translation."
        user_prompt = "The following is a translated text that may contain explanations or notes that are not part of the actual translation. Please return ONLY the translated text without any explanations, notes, or additional content:\n\n" + translated_text
        
        # Get model-specific configuration
        model = self.provider.get_model(self.model_name)
        max_tokens = model.max_tokens if model and model.max_tokens else 1024
        temperature = 0.0  # Use 0 temperature for deterministic output
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            cleaned_text = response.choices[0].message.content.strip()
            
            # If the cleaned text is significantly shorter, log that explanations were removed
            if len(cleaned_text) < len(translated_text) * 0.8:
                logger.info("Post-check removed explanations from translated text")
            
            return cleaned_text
        except Exception as e:
            logger.error(f"Error during post-check: {e}", exc_info=True)
            # If post-check fails, return the original translation
            return translated_text

    def translate(self, text: str, target_language: str) -> str:
        """
        Translate the given text to the target language using the configured AI provider.
        
        Args:
            text: The text to translate
            target_language: The target language code or name
            
        Returns:
            The translated text
        """
        if self.provider.name == "mock":
            # Mock translation
            logger.debug(f"Mock translating text to {target_language}")
            translated_text = f"[{target_language}] {text}"
            logger.debug(f"Mock translation completed: {len(translated_text)} characters")
            return translated_text
        
        logger.debug(f"Translating text to {target_language} using {self.provider.name} with {self.prompt_style.name} prompt style")
        
        # Format the user prompt template with the target language and text
        user_prompt = self.prompt_style.template.format_user_prompt(target_language, text)
        
        # Get model-specific configuration
        model = self.provider.get_model(self.model_name)
        max_tokens = model.max_tokens if model and model.max_tokens else 1024
        temperature = model.temperature if model and model.temperature is not None else 0.3
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.prompt_style.template.system},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        translated_text = response.choices[0].message.content.strip()
        logger.debug(f"Translation completed: {len(translated_text)} characters")
        
        # Apply post-check if enabled
        if self.enable_post_check:
            translated_text = self._post_check_translation(translated_text)
            
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
        if self.provider.name == "mock":
            # Mock translation with a small delay
            logger.debug(f"Async mock translating text to {target_language}")
            await asyncio.sleep(0.01)
            translated_text = f"[{target_language}] {text}"
            logger.debug(f"Async mock translation completed: {len(translated_text)} characters")
            return translated_text
        
        logger.debug(f"Async translating text to {target_language} using {self.provider.name}")
        
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
    def detect_available_services(provider_registry: Optional[AIProviderRegistry] = None) -> List[str]:
        """
        Detect available translator services based on environment variables and provider registry.
        
        Args:
            provider_registry: Registry of AI providers (if None, will try to load from aiprovider.json)
            
        Returns:
            A list of available service types
        """
        available_services = ['mock']  # Mock is always available
        
        # Load provider registry if not provided
        if provider_registry is None:
            try:
                provider_registry = AIProviderRegistry.load_from_file("aiprovider.json")
            except Exception as e:
                logger.warning(f"Failed to load AI provider registry: {e}")
                return available_services
        
        # Check for API keys for each provider
        for provider_name in provider_registry.get_provider_names():
            if provider_name != 'mock':
                env_var_name = f"{provider_name.upper()}_API_KEY"
                if os.environ.get(env_var_name):
                    available_services.append(provider_name)
            
        return available_services
    
    @staticmethod
    def create_translator(
        service_type: str = "auto",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        prompt_style: str = "default",
        enable_post_check: bool = False,
        provider_registry: Optional[AIProviderRegistry] = None,
        prompt_registry: Optional[PromptRegistry] = None
    ) -> TranslatorService:
        """
        Create a translator service instance.
        
        Args:
            service_type: Type of translator service ('openai', 'deepseek', 'mock', 'auto')
                          If 'auto', will auto-detect based on available API keys
            api_key: API key for the service (if None, will try to get from environment)
            model: Model to use for translation (if None, will use service-specific defaults)
            prompt_style: Style of prompts to use (default, chinese, formal, etc.)
            enable_post_check: If True, checks translated text for explanations and removes them
            provider_registry: Registry of AI providers (if None, will try to load from aiprovider.json)
            prompt_registry: Registry of prompt styles (if None, will try to load from prompts.json)
            
        Returns:
            A TranslatorService instance
            
        Raises:
            ValueError: If the service type is not supported or no services are available
        """
        # Auto-detect service if requested
        if service_type.lower() == 'auto':
            available_services = TranslatorFactory.detect_available_services(provider_registry)
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
            return AIProviderTranslator(
                provider=service_type,
                api_key=api_key,
                model=model,
                prompt_style=prompt_style,
                enable_post_check=enable_post_check,
                provider_registry=provider_registry,
                prompt_registry=prompt_registry
            )
    
    @staticmethod
    def create_translator_from_config(
        config: AIServiceConfig,
        model: Optional[str] = None,
        prompt_style: str = "default",
        enable_post_check: bool = False,
        provider_registry: Optional[AIProviderRegistry] = None,
        prompt_registry: Optional[PromptRegistry] = None
    ) -> TranslatorService:
        """
        Create a translator service instance from a configuration.
        
        Args:
            config: AI service configuration
            model: Model to use for translation (if None, will use service-specific defaults)
            prompt_style: Style of prompts to use (default, chinese, formal, etc.)
            enable_post_check: If True, checks translated text for explanations and removes them
            provider_registry: Registry of AI providers (if None, will try to load from aiprovider.json)
            prompt_registry: Registry of prompt styles (if None, will try to load from prompts.json)
            
        Returns:
            A TranslatorService instance
        """
        return TranslatorFactory.create_translator(
            service_type=config.api_service_provider,
            api_key=config.api_key,
            model=model,
            prompt_style=prompt_style,
            enable_post_check=enable_post_check,
            provider_registry=provider_registry,
            prompt_registry=prompt_registry
        )