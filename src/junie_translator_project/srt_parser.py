"""
SRT Parser Module - Handles parsing and writing of SRT subtitle files.

This module provides functionality to read SRT files, parse their content,
and write translated content back to new SRT files.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Iterator, Optional


@dataclass
class SubtitleEntry:
    """Represents a single subtitle entry in an SRT file."""
    index: int
    start_time: str
    end_time: str
    content: List[str]

    def __str__(self) -> str:
        """Convert the subtitle entry back to SRT format."""
        return (
            f"{self.index}\n"
            f"{self.start_time} --> {self.end_time}\n"
            f"{'\n'.join(self.content)}\n"
        )


class SRTParser:
    """Parser for SRT subtitle files."""

    def __init__(self, file_path: str):
        """
        Initialize the SRT parser with a file path.

        Args:
            file_path: Path to the SRT file to parse
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"SRT file not found: {file_path}")
        
        self.entries: List[SubtitleEntry] = []
        self._parse_file()

    def _parse_file(self) -> None:
        """Parse the SRT file and store subtitle entries."""
        with open(self.file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Split the file by double newline (entry separator)
        entry_blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in entry_blocks:
            if not block.strip():
                continue
                
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue  # Skip invalid entries
                
            try:
                index = int(lines[0])
                time_line = lines[1]
                content_lines = lines[2:]
                
                # Parse time line (format: 00:00:00,000 --> 00:00:00,000)
                time_match = re.match(r'([\d:,]+)\s*-->\s*([\d:,]+)', time_line)
                if not time_match:
                    continue
                    
                start_time, end_time = time_match.groups()
                
                self.entries.append(SubtitleEntry(
                    index=index,
                    start_time=start_time,
                    end_time=end_time,
                    content=content_lines
                ))
            except Exception as e:
                print(f"Error parsing entry: {block}\nError: {e}")
                continue

    def get_entries(self) -> List[SubtitleEntry]:
        """
        Get all subtitle entries from the parsed file.
        
        Returns:
            List of SubtitleEntry objects
        """
        return self.entries

    def get_content_lines(self) -> List[str]:
        """
        Get all content lines from all subtitle entries.
        
        Returns:
            List of content lines
        """
        lines = []
        for entry in self.entries:
            lines.extend(entry.content)
        return lines

    @staticmethod
    def write_srt(entries: List[SubtitleEntry], output_path: str) -> None:
        """
        Write subtitle entries to a new SRT file.
        
        Args:
            entries: List of SubtitleEntry objects
            output_path: Path to the output SRT file
        """
        with open(output_path, 'w', encoding='utf-8') as file:
            for i, entry in enumerate(entries):
                # Update index to ensure sequential numbering
                entry.index = i + 1
                file.write(str(entry))
                file.write('\n')  # Add empty line between entries

    @staticmethod
    def generate_output_filename(input_path: str, target_language: str) -> str:
        """
        Generate an output filename based on the input path and target language.
        
        Args:
            input_path: Path to the input SRT file
            target_language: Target language code or name
            
        Returns:
            Generated output filename
        """
        input_path = Path(input_path)
        stem = input_path.stem
        return str(input_path.with_name(f"{stem}_{target_language}{input_path.suffix}"))