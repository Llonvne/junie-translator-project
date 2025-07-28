"""
Main Module - Core functionality for translating SRT files.

This module ties together the SRT parser and translator modules to provide
the core functionality for translating SRT files with progress tracking.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

from junie_translator_project.srt_parser import SRTParser, SubtitleEntry
from junie_translator_project.translator import TranslatorService, TranslatorFactory


class SRTTranslator:
    """Main class for translating SRT files."""

    def __init__(
        self,
        translator_service: Optional[TranslatorService] = None,
        translator_type: str = "auto",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        show_progress: bool = True
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
        """
        self.translator = translator_service or TranslatorFactory.create_translator(
            translator_type, api_key=api_key, model=model
        )
        self.show_progress = show_progress and TQDM_AVAILABLE
        
        if self.show_progress and not TQDM_AVAILABLE:
            print("Warning: tqdm is not installed. Progress bar will not be shown.")
            print("Install tqdm with 'uv pip install tqdm' to enable progress bars.")
            self.show_progress = False

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
        # Parse the input file
        parser = SRTParser(input_path)
        entries = parser.get_entries()
        
        # Generate output path if not provided
        if not output_path:
            output_path = SRTParser.generate_output_filename(input_path, target_language)
        
        # Translate each subtitle entry
        translated_entries = self._translate_entries(entries, target_language)
        
        # Write the translated entries to the output file
        SRTParser.write_srt(translated_entries, output_path)
        
        return output_path

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
        
        return translated_entries


def translate_srt(
    input_path: str,
    target_language: str,
    output_path: Optional[str] = None,
    translator_type: str = "auto",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    show_progress: bool = True
) -> str:
    """
    Convenience function to translate an SRT file.
    
    Args:
        input_path: Path to the input SRT file
        target_language: Target language code or name
        output_path: Path to the output SRT file (if None, will be generated)
        translator_type: Type of translator service to use ('auto', 'openai', 'deepseek', 'mock')
                        If 'auto', will auto-detect based on available API keys in environment variables.
        api_key: API key for the translator service (if None, will try to get from environment)
        model: Model to use for translation (if None, will use service-specific defaults:
              gpt-3.5-turbo for OpenAI, deepseek-v3 for DeepSeek)
        show_progress: Whether to show a progress bar during translation
        
    Returns:
        Path to the output SRT file
    """
    translator = SRTTranslator(
        translator_type=translator_type,
        api_key=api_key,
        model=model,
        show_progress=show_progress
    )
    
    return translator.translate_file(input_path, target_language, output_path)