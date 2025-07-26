"""
OpenAI translator implementation.
"""
import time
from typing import Optional, Dict, Any

from junie_translator.translators.base import BaseTranslator


class OpenAITranslator(BaseTranslator):
    """
    Translator implementation using OpenAI's API.
    
    This translator uses OpenAI's API to translate text.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", **kwargs):
        """
        Initialize the OpenAI translator.
        
        Args:
            api_key: The OpenAI API key.
            model: The OpenAI model to use for translation.
            **kwargs: Additional configuration options for the OpenAI client.
        """
        self.api_key = api_key
        self.model = model
        self.client = None
        self.max_retries = kwargs.get('max_retries', 3)
        self.retry_delay = kwargs.get('retry_delay', 1)
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the OpenAI client."""
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "The 'openai' package is required for OpenAITranslator. "
                "Install it with 'uv pip install openai'."
            )
    
    def translate(self, text: str, target_language: str, **kwargs) -> str:
        """
        Translate the given text to the target language using OpenAI.
        
        Args:
            text: The text to translate.
            target_language: The language code to translate to.
            **kwargs: Additional options for the translation.
            
        Returns:
            The translated text.
        """
        if not self.client:
            self._initialize_client()
        
        system_prompt = kwargs.get('system_prompt', 
            f"You are a professional translator. Translate the following text to {target_language}. "
            f"Preserve the original formatting and meaning as much as possible. "
            f"Return only the translated text without explanations or notes."
        )
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    temperature=kwargs.get('temperature', 0.3),
                    max_tokens=kwargs.get('max_tokens', 1024),
                )
                
                # Extract the translated text from the response
                translated_text = response.choices[0].message.content.strip()
                return translated_text
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    # Wait before retrying
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise RuntimeError(f"Failed to translate text after {self.max_retries} attempts: {e}")
    
    def is_available(self) -> bool:
        """
        Check if the OpenAI service is available.
        
        Returns:
            True if the service is available, False otherwise.
        """
        if not self.client:
            try:
                self._initialize_client()
            except Exception:
                return False
        
        try:
            # Make a simple API call to check if the service is available
            self.client.models.list(limit=1)
            return True
        except Exception:
            return False