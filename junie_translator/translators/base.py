"""
Base translator interface for implementing different translation services.
"""
from abc import ABC, abstractmethod
from typing import Optional


class BaseTranslator(ABC):
    """
    Abstract base class for all translator implementations.
    
    This class defines the interface that all translator implementations must follow.
    It provides a common API for translating text using different AI services.
    """
    
    @abstractmethod
    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the translator with the necessary credentials.
        
        Args:
            api_key: The API key for the translation service.
            **kwargs: Additional configuration options for the translator.
        """
        pass
    
    @abstractmethod
    def translate(self, text: str, target_language: str, **kwargs) -> str:
        """
        Translate the given text to the target language.
        
        Args:
            text: The text to translate.
            target_language: The language code to translate to.
            **kwargs: Additional options for the translation.
            
        Returns:
            The translated text.
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the translation service is available.
        
        Returns:
            True if the service is available, False otherwise.
        """
        pass