"""
SRT Parser module for handling .srt subtitle files.
"""

import os
from pathlib import Path
from typing import List, Tuple, Iterator

import pysrt


class SRTParser:
    """
    Parser for .srt subtitle files.
    """

    def __init__(self, file_path: str):
        """
        Initialize the SRT parser with a file path.

        Args:
            file_path: Path to the .srt file
        """
        self.file_path = file_path
        self.subs = pysrt.open(file_path)

    def get_translatable_lines(self) -> List[Tuple[int, str]]:
        """
        Extract all translatable lines from the .srt file.

        Returns:
            List of tuples containing (index, text) for each subtitle
        """
        return [(i, sub.text) for i, sub in enumerate(self.subs)]

    def update_line(self, index: int, translated_text: str) -> None:
        """
        Update a specific line with translated text.

        Args:
            index: Index of the subtitle to update
            translated_text: Translated text to replace the original
        """
        self.subs[index].text = translated_text

    def save_translated_file(self, target_language: str) -> str:
        """
        Save the translated subtitles to a new file.

        Args:
            target_language: Target language code (e.g., 'es', 'fr', 'de')

        Returns:
            Path to the saved file
        """
        # Create output filename with language code
        file_path = Path(self.file_path)
        output_filename = f"{file_path.stem}_{target_language}{file_path.suffix}"
        output_path = file_path.parent / output_filename

        # Save the translated subtitles
        self.subs.save(str(output_path), encoding='utf-8')
        return str(output_path)

    @staticmethod
    def get_srt_files(directory: str) -> Iterator[str]:
        """
        Get all .srt files in a directory.

        Args:
            directory: Directory to search for .srt files

        Returns:
            Iterator of .srt file paths
        """
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.srt'):
                    yield os.path.join(root, file)