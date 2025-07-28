"""
Main Module - Core functionality for translating SRT files.

This module ties together the SRT parser and translator modules to provide
the core functionality for translating SRT files with progress tracking.
"""

import os
import json
import hashlib
import glob
from pathlib import Path
from typing import Optional, List, Dict, Any, Set, Tuple

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

from junie_translator_project.srt_parser import SRTParser, SubtitleEntry
from junie_translator_project.translator import TranslatorService, TranslatorFactory


class Config:
    """Configuration loader and validator for the translator."""
    
    DEFAULT_CONFIG_PATH = "config.json"
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Path to the configuration file (if None, will use default)
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration from the config file.
        
        Returns:
            Configuration dictionary
        
        Raises:
            FileNotFoundError: If the config file doesn't exist
            json.JSONDecodeError: If the config file is not valid JSON
            ValueError: If the config file is missing required fields
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Validate required fields
            if 'to-language' not in config:
                raise ValueError("Config file must contain 'to-language' field")
                
            # Set default values for optional fields
            if 'from-language' not in config:
                config['from-language'] = 'auto'
                
            if 'ai-api-service' not in config:
                config['ai-api-service'] = {
                    'api-service-provider': 'auto',
                    'api-key': None
                }
            elif 'api-service-provider' not in config['ai-api-service']:
                config['ai-api-service']['api-service-provider'] = 'auto'
                
            return config
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Config file is not valid JSON: {self.config_path}")
            
    def get_from_language(self) -> str:
        """Get the source language from the config."""
        return self.config.get('from-language', 'auto')
        
    def get_to_language(self) -> str:
        """Get the target language from the config."""
        return self.config['to-language']
        
    def get_api_service_provider(self) -> str:
        """Get the API service provider from the config."""
        return self.config.get('ai-api-service', {}).get('api-service-provider', 'auto')
        
    def get_api_key(self) -> Optional[str]:
        """Get the API key from the config."""
        return self.config.get('ai-api-service', {}).get('api-key')
        
    def get_model(self) -> Optional[str]:
        """Get the model from the config."""
        return self.config.get('model')
        
    def get_output_directory(self) -> Optional[str]:
        """Get the output directory from the config."""
        return self.config.get('output-directory')


class LockFile:
    """Lock file manager to avoid duplicate translations."""
    
    DEFAULT_LOCK_FILE = "junie-translator.lock"
    
    def __init__(self, lock_file_path: Optional[str] = None):
        """
        Initialize the lock file manager.
        
        Args:
            lock_file_path: Path to the lock file (if None, will use default)
        """
        self.lock_file_path = lock_file_path or self.DEFAULT_LOCK_FILE
        self.processed_files: Set[str] = set()
        self._load_lock_file()
        
    def _load_lock_file(self) -> None:
        """Load the lock file if it exists."""
        if os.path.exists(self.lock_file_path):
            try:
                with open(self.lock_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        self.processed_files.add(line.strip())
            except Exception as e:
                print(f"Warning: Failed to load lock file: {e}")
                
    def save_lock_file(self) -> None:
        """Save the lock file."""
        try:
            with open(self.lock_file_path, 'w', encoding='utf-8') as f:
                for file_id in sorted(self.processed_files):
                    f.write(f"{file_id}\n")
        except Exception as e:
            print(f"Warning: Failed to save lock file: {e}")
            
    def is_processed(self, file_id: str) -> bool:
        """
        Check if a file has already been processed.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            True if the file has been processed, False otherwise
        """
        return file_id in self.processed_files
        
    def mark_processed(self, file_id: str) -> None:
        """
        Mark a file as processed.
        
        Args:
            file_id: Unique identifier for the file
        """
        self.processed_files.add(file_id)
        self.save_lock_file()
        
    @staticmethod
    def generate_file_id(input_path: str, from_lang: str, to_lang: str) -> str:
        """
        Generate a unique identifier for a file based on its path and languages.
        
        Args:
            input_path: Path to the input file
            from_lang: Source language
            to_lang: Target language
            
        Returns:
            Unique identifier for the file
        """
        # Calculate hash of the file content
        with open(input_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()[:8]
            
        # Combine file path, languages, and hash
        return f"{input_path}|{from_lang}|{to_lang}|{file_hash}"


class SRTTranslator:
    """Main class for translating SRT files."""

    def __init__(
        self,
        translator_service: Optional[TranslatorService] = None,
        translator_type: str = "auto",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        show_progress: bool = True,
        lock_file: Optional[LockFile] = None,
        from_language: str = "auto",
        output_directory: Optional[str] = None
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
            lock_file: LockFile instance to track processed files
            from_language: Source language (if 'auto', will be inferred)
            output_directory: Directory for output files
        """
        self.translator = translator_service or TranslatorFactory.create_translator(
            translator_type, api_key=api_key, model=model
        )
        self.show_progress = show_progress and TQDM_AVAILABLE
        self.lock_file = lock_file or LockFile()
        self.from_language = from_language
        self.output_directory = output_directory
        
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
        # Generate file ID for lock file
        file_id = LockFile.generate_file_id(input_path, self.from_language, target_language)
        
        # Check if file has already been processed
        if self.lock_file.is_processed(file_id):
            print(f"Skipping already processed file: {input_path}")
            
            # Try to find the output file
            input_path_obj = Path(input_path)
            stem = input_path_obj.stem
            pattern = f"{stem}_{self.from_language}{target_language}_*{input_path_obj.suffix}"
            
            if self.output_directory:
                search_dir = Path(self.output_directory)
            else:
                search_dir = input_path_obj.parent
                
            matches = list(search_dir.glob(pattern))
            if matches:
                return str(matches[0])
            else:
                # If we can't find the output file, regenerate it
                print(f"Output file not found, regenerating: {input_path}")
            
        # Parse the input file
        parser = SRTParser(input_path)
        entries = parser.get_entries()
        
        # Generate output path if not provided
        if not output_path:
            output_path = SRTParser.generate_output_filename(
                input_path, 
                self.from_language, 
                target_language, 
                self.output_directory
            )
        
        # Translate each subtitle entry
        translated_entries = self._translate_entries(entries, target_language)
        
        # Write the translated entries to the output file
        SRTParser.write_srt(translated_entries, output_path)
        
        # Mark file as processed
        self.lock_file.mark_processed(file_id)
        
        return output_path

    def translate_directory(
        self,
        directory_path: str,
        target_language: str,
        file_pattern: str = "*.srt"
    ) -> List[str]:
        """
        Translate all SRT files in a directory.
        
        Args:
            directory_path: Path to the directory containing SRT files
            target_language: Target language code or name
            file_pattern: Pattern to match SRT files (default: "*.srt")
            
        Returns:
            List of paths to the output SRT files
        """
        # Find all SRT files in the directory
        directory_path = Path(directory_path)
        srt_files = list(directory_path.glob(file_pattern))
        
        if not srt_files:
            print(f"No SRT files found in directory: {directory_path}")
            return []
        
        output_files = []
        
        # Set up progress bar if enabled
        iterator = tqdm(srt_files, desc=f"Translating files to {target_language}") if self.show_progress else srt_files
        
        for srt_file in iterator:
            try:
                output_path = self.translate_file(str(srt_file), target_language)
                output_files.append(output_path)
            except Exception as e:
                print(f"Error translating file {srt_file}: {e}")
        
        return output_files

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
    show_progress: bool = True,
    from_language: str = "auto",
    output_directory: Optional[str] = None,
    lock_file_path: Optional[str] = None
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
        from_language: Source language (if 'auto', will be inferred)
        output_directory: Directory for output files
        lock_file_path: Path to the lock file
        
    Returns:
        Path to the output SRT file
    """
    lock_file = LockFile(lock_file_path)
    
    translator = SRTTranslator(
        translator_type=translator_type,
        api_key=api_key,
        model=model,
        show_progress=show_progress,
        lock_file=lock_file,
        from_language=from_language,
        output_directory=output_directory
    )
    
    return translator.translate_file(input_path, target_language, output_path)


def translate_directory(
    directory_path: str,
    target_language: str,
    translator_type: str = "auto",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    show_progress: bool = True,
    from_language: str = "auto",
    output_directory: Optional[str] = None,
    lock_file_path: Optional[str] = None,
    file_pattern: str = "*.srt"
) -> List[str]:
    """
    Convenience function to translate all SRT files in a directory.
    
    Args:
        directory_path: Path to the directory containing SRT files
        target_language: Target language code or name
        translator_type: Type of translator service to use ('auto', 'openai', 'deepseek', 'mock')
        api_key: API key for the translator service (if None, will try to get from environment)
        model: Model to use for translation (if None, will use service-specific defaults)
        show_progress: Whether to show a progress bar during translation
        from_language: Source language (if 'auto', will be inferred)
        output_directory: Directory for output files
        lock_file_path: Path to the lock file
        file_pattern: Pattern to match SRT files (default: "*.srt")
        
    Returns:
        List of paths to the output SRT files
    """
    lock_file = LockFile(lock_file_path)
    
    translator = SRTTranslator(
        translator_type=translator_type,
        api_key=api_key,
        model=model,
        show_progress=show_progress,
        lock_file=lock_file,
        from_language=from_language,
        output_directory=output_directory
    )
    
    return translator.translate_directory(directory_path, target_language, file_pattern)


def main(config_path: Optional[str] = None) -> int:
    """
    Main function to load config and execute translation.
    
    Args:
        config_path: Path to the configuration file (if None, will use default)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Load configuration
        config = Config(config_path)
        
        # Create lock file
        lock_file = LockFile()
        
        # Create translator
        translator = SRTTranslator(
            translator_type=config.get_api_service_provider(),
            api_key=config.get_api_key(),
            model=config.get_model(),
            show_progress=True,
            lock_file=lock_file,
            from_language=config.get_from_language(),
            output_directory=config.get_output_directory()
        )
        
        # Translate all SRT files in the current directory
        output_files = translator.translate_directory(
            ".", 
            config.get_to_language()
        )
        
        if output_files:
            print(f"Translation completed successfully. {len(output_files)} files translated.")
            return 0
        else:
            print("No files were translated.")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        return 1