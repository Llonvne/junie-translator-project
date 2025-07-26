"""
Translator module for handling AI translation services.
"""

import abc
import os
import time
from typing import Optional, Dict, Any, List

import openai


class TranslationError(Exception):
    """Exception raised for errors in the translation process."""
    pass


class BaseTranslator(abc.ABC):
    """
    Abstract base class for translators.
    This allows for easy extension with different translation services.
    """

    @abc.abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text from source language to target language.

        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Translated text

        Raises:
            TranslationError: If translation fails
        """
        pass


class OpenAITranslator(BaseTranslator):
    """
    Translator using OpenAI API.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the OpenAI translator.

        Args:
            api_key: OpenAI API key (if None, will try to get from OPENAI_API_KEY environment variable)
            model: OpenAI model to use for translation
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set it as an argument or as OPENAI_API_KEY environment variable.")
        
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)
        
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text using OpenAI API.

        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Translated text

        Raises:
            TranslationError: If translation fails
        """
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": f"You are a translator. Translate the following text from {source_lang} to {target_lang}. Preserve any formatting, but only return the translated text without explanations or notes."},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3,
                )
                
                translated_text = response.choices[0].message.content.strip()
                return translated_text
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise TranslationError(f"Failed to translate text after {max_retries} attempts: {str(e)}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff


class TranslatorFactory:
    """
    Factory for creating translator instances.
    This allows for easy extension with new translator types.
    """
    
    @staticmethod
    def create_translator(translator_type: str, **kwargs) -> BaseTranslator:
        """
        Create a translator instance.

        Args:
            translator_type: Type of translator to create
            **kwargs: Additional arguments to pass to the translator constructor

        Returns:
            Translator instance

        Raises:
            ValueError: If translator_type is not supported
        """
        if translator_type.lower() == "openai":
            return OpenAITranslator(**kwargs)
        else:
            raise ValueError(f"Unsupported translator type: {translator_type}")