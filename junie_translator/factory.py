"""
Factory for creating translator and parser instances.
"""
import os
from typing import Dict, Type, Optional

from junie_translator.parsers.base import BaseParser
from junie_translator.parsers.srt import SrtParser
from junie_translator.translators.base import BaseTranslator
from junie_translator.translators.openai_translator import OpenAITranslator


class TranslatorFactory:
    """
    Factory for creating translator instances.
    
    This factory provides a way to create translator instances based on the translator type.
    """
    
    _translators: Dict[str, Type[BaseTranslator]] = {
        'openai': OpenAITranslator,
        # Add more translators here
    }
    
    @classmethod
    def create(cls, translator_type: str, api_key: Optional[str] = None, **kwargs) -> BaseTranslator:
        """
        Create a translator instance.
        
        Args:
            translator_type: The type of translator to create.
            api_key: The API key for the translator. If not provided, it will be read from the environment.
            **kwargs: Additional configuration options for the translator.
            
        Returns:
            A translator instance.
            
        Raises:
            ValueError: If the translator type is not supported.
        """
        if translator_type not in cls._translators:
            raise ValueError(f"Unsupported translator type: {translator_type}. "
                            f"Supported types: {', '.join(cls._translators.keys())}")
        
        # Get the API key from the environment if not provided
        if api_key is None:
            env_var = f"{translator_type.upper()}_API_KEY"
            api_key = os.environ.get(env_var)
            if api_key is None:
                raise ValueError(f"API key not provided and {env_var} environment variable not set.")
        
        # Create the translator instance
        translator_class = cls._translators[translator_type]
        return translator_class(api_key, **kwargs)
    
    @classmethod
    def register(cls, name: str, translator_class: Type[BaseTranslator]) -> None:
        """
        Register a new translator class.
        
        Args:
            name: The name to register the translator under.
            translator_class: The translator class to register.
        """
        cls._translators[name] = translator_class


class ParserFactory:
    """
    Factory for creating parser instances.
    
    This factory provides a way to create parser instances based on the file extension.
    """
    
    _parsers: Dict[str, Type[BaseParser]] = {
        '.srt': SrtParser,
        # Add more parsers here
    }
    
    @classmethod
    def create(cls, file_extension: str, **kwargs) -> BaseParser:
        """
        Create a parser instance.
        
        Args:
            file_extension: The file extension to create a parser for.
            **kwargs: Additional configuration options for the parser.
            
        Returns:
            A parser instance.
            
        Raises:
            ValueError: If the file extension is not supported.
        """
        if file_extension not in cls._parsers:
            raise ValueError(f"Unsupported file extension: {file_extension}. "
                            f"Supported extensions: {', '.join(cls._parsers.keys())}")
        
        # Create the parser instance
        parser_class = cls._parsers[file_extension]
        return parser_class(**kwargs)
    
    @classmethod
    def create_from_file(cls, file_path: str, **kwargs) -> BaseParser:
        """
        Create a parser instance based on the file path.
        
        Args:
            file_path: The path to the file to create a parser for.
            **kwargs: Additional configuration options for the parser.
            
        Returns:
            A parser instance.
            
        Raises:
            ValueError: If the file extension is not supported.
        """
        _, file_extension = os.path.splitext(file_path)
        return cls.create(file_extension, **kwargs)
    
    @classmethod
    def register(cls, extension: str, parser_class: Type[BaseParser]) -> None:
        """
        Register a new parser class.
        
        Args:
            extension: The file extension to register the parser for.
            parser_class: The parser class to register.
        """
        cls._parsers[extension] = parser_class