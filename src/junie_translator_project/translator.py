"""
Translator Module - Handles translation of text using AI services.

This module provides an extensible framework for translating text using
various AI services like OpenAI, DeepSeek, or other compatible services.

Supported translator services:
- OpenAI: Uses OpenAI's GPT models for translation
- DeepSeek: Uses DeepSeek's R1 and V3 models for translation
- Mock: A simple mock translator for testing purposes
"""

import abc
import os
from typing import List, Optional, Dict, Any

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


class OpenAITranslator(TranslatorService):
    """Translator service using OpenAI API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the OpenAI translator.
        
        Args:
            api_key: OpenAI API key (if None, will try to get from environment)
            model: OpenAI model to use for translation
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
        self.client = openai.OpenAI(api_key=self.api_key)

    def translate(self, text: str, target_language: str) -> str:
        """
        Translate the given text to the target language using OpenAI.
        
        Args:
            text: The text to translate
            target_language: The target language code or name
            
        Returns:
            The translated text
        """
        prompt = f"Translate the following text to {target_language}. Preserve any formatting and special characters:\n\n{text}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        
        return response.choices[0].message.content.strip()

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
        return [self.translate(text, target_language) for text in texts]


class DeepSeekTranslator(TranslatorService):
    """Translator service using DeepSeek API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-v3"):
        """
        Initialize the DeepSeek translator.
        
        Args:
            api_key: DeepSeek API key (if None, will try to get from environment)
            model: DeepSeek model to use for translation (deepseek-r1 or deepseek-v3)
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
        if model.lower() in ["deepseek-r1", "r1", "deepseek-chat-r1"]:
            self.model = "deepseek-chat-r1"
        elif model.lower() in ["deepseek-v3", "v3", "deepseek-chat-v3"]:
            self.model = "deepseek-chat-v3"
        else:
            raise ValueError(
                f"Unsupported DeepSeek model: {model}. "
                "Supported models are: deepseek-r1, deepseek-v3"
            )
        
        # DeepSeek uses OpenAI-compatible API with a different base URL
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com/v1"  # DeepSeek API endpoint
        )

    def translate(self, text: str, target_language: str) -> str:
        """
        Translate the given text to the target language using DeepSeek.
        
        Args:
            text: The text to translate
            target_language: The target language code or name
            
        Returns:
            The translated text
        """
        prompt = f"Translate the following text to {target_language}. Preserve any formatting and special characters:\n\n{text}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        
        return response.choices[0].message.content.strip()

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
        return [self.translate(text, target_language) for text in texts]


class MockTranslator(TranslatorService):
    """Mock translator service for testing purposes."""

    def translate(self, text: str, target_language: str) -> str:
        """
        Mock translation that just adds a prefix to the text.
        
        Args:
            text: The text to translate
            target_language: The target language code or name
            
        Returns:
            The "translated" text
        """
        return f"[{target_language}] {text}"

    def batch_translate(self, texts: List[str], target_language: str) -> List[str]:
        """
        Mock batch translation.
        
        Args:
            texts: List of texts to translate
            target_language: The target language code or name
            
        Returns:
            List of "translated" texts
        """
        return [self.translate(text, target_language) for text in texts]


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
            return "deepseek-v3"
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
            return MockTranslator()
        else:
            raise ValueError(f"Unsupported translator service type: {service_type}")