"""
Translator Module - Handles translation of text using AI services.

This module provides an extensible framework for translating text using
various AI services like OpenAI or other compatible services.
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
    def create_translator(service_type: str, **kwargs) -> TranslatorService:
        """
        Create a translator service instance.
        
        Args:
            service_type: Type of translator service ('openai', 'mock', etc.)
            **kwargs: Additional arguments to pass to the translator constructor
            
        Returns:
            A TranslatorService instance
            
        Raises:
            ValueError: If the service type is not supported
        """
        if service_type.lower() == 'openai':
            return OpenAITranslator(**kwargs)
        elif service_type.lower() == 'mock':
            return MockTranslator()
        else:
            raise ValueError(f"Unsupported translator service type: {service_type}")