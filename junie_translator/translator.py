"""
Main translator program that ties everything together.
"""
import os
import time
from typing import Optional, List, Type, Dict, Any

from junie_translator.parsers.base import BaseParser, SubtitleEntry
from junie_translator.translators.base import BaseTranslator
from junie_translator.utils.progress import ProgressTracker


class SubtitleTranslator:
    """
    Main translator program that handles the translation process from start to finish.
    
    This class ties together the parser, translator, and progress tracking components
    to provide a complete subtitle translation solution.
    """
    
    def __init__(self, parser: BaseParser, translator: BaseTranslator):
        """
        Initialize the subtitle translator.
        
        Args:
            parser: The parser to use for reading and writing subtitle files.
            translator: The translator to use for translating subtitle text.
        """
        self.parser = parser
        self.translator = translator
        self.progress_tracker = ProgressTracker()
    
    def translate_file(self, input_file: str, target_language: str, 
                       output_file: Optional[str] = None, **kwargs) -> str:
        """
        Translate a subtitle file to the target language.
        
        Args:
            input_file: The path to the input subtitle file.
            target_language: The language code to translate to.
            output_file: The path to write the translated subtitle file to.
                         If not provided, a default name will be generated.
            **kwargs: Additional options for the translation.
            
        Returns:
            The path to the translated subtitle file.
        """
        # Check if the translator is available
        if not self.translator.is_available():
            raise RuntimeError("Translator service is not available. Please check your API key and internet connection.")
        
        # Parse the input file
        entries = self.parser.parse(input_file)
        
        # Generate a default output file name if not provided
        if output_file is None:
            base_name, _ = os.path.splitext(input_file)
            output_file = f"{base_name}.{target_language}{self.parser.get_extension()}"
        
        # Translate each subtitle entry
        translated_entries = self._translate_entries(entries, target_language, **kwargs)
        
        # Write the translated entries to the output file
        self.parser.write(translated_entries, output_file)
        
        return output_file
    
    def _translate_entries(self, entries: List[SubtitleEntry], target_language: str, 
                          **kwargs) -> List[SubtitleEntry]:
        """
        Translate a list of subtitle entries.
        
        Args:
            entries: The subtitle entries to translate.
            target_language: The language code to translate to.
            **kwargs: Additional options for the translation.
            
        Returns:
            A list of translated subtitle entries.
        """
        translated_entries = []
        
        # Use progress tracker to show translation progress
        for entry in self.progress_tracker.track(entries, desc=f"Translating to {target_language}"):
            # Translate the text
            translated_text = self.translator.translate(entry.text, target_language, **kwargs)
            
            # Create a new entry with the translated text
            translated_entry = SubtitleEntry(
                index=entry.index,
                start_time=entry.start_time,
                end_time=entry.end_time,
                text=translated_text
            )
            
            translated_entries.append(translated_entry)
            
            # Add a small delay to avoid rate limiting
            time.sleep(kwargs.get('delay', 0.1))
        
        return translated_entries