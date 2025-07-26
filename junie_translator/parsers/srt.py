"""
SRT subtitle file parser implementation.
"""
import re
import os
from typing import List, Optional, Match

from junie_translator.parsers.base import BaseParser, SubtitleEntry


class SrtParser(BaseParser):
    """
    Parser for SubRip (.srt) subtitle files.
    
    This parser handles reading and writing SubRip (.srt) subtitle files.
    """
    
    # Regular expression for parsing SRT entries
    PATTERN = re.compile(
        r'(\d+)\s*\n'                                # Index
        r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*'        # Start time
        r'(\d{2}:\d{2}:\d{2},\d{3})\s*\n'            # End time
        r'((?:.*\n)+?)'                              # Text (one or more lines)
        r'(?:\n|$)',                                 # End of entry (blank line or end of file)
        re.MULTILINE
    )
    
    def parse(self, file_path: str) -> List[SubtitleEntry]:
        """
        Parse an SRT subtitle file and return a list of subtitle entries.
        
        Args:
            file_path: The path to the SRT file.
            
        Returns:
            A list of SubtitleEntry objects.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        entries = []
        for match in self.PATTERN.finditer(content):
            entry = self._parse_match(match)
            entries.append(entry)
        
        return entries
    
    def write(self, entries: List[SubtitleEntry], output_path: str) -> None:
        """
        Write subtitle entries to an SRT file.
        
        Args:
            entries: The subtitle entries to write.
            output_path: The path to write the SRT file to.
        """
        with open(output_path, 'w', encoding='utf-8') as file:
            for entry in entries:
                file.write(f"{entry.index}\n")
                file.write(f"{entry.start_time} --> {entry.end_time}\n")
                file.write(f"{entry.text}\n\n")
    
    def get_extension(self) -> str:
        """
        Get the file extension for SRT files.
        
        Returns:
            The file extension ".srt".
        """
        return ".srt"
    
    def _parse_match(self, match: Match) -> SubtitleEntry:
        """
        Parse a regex match into a SubtitleEntry.
        
        Args:
            match: The regex match object.
            
        Returns:
            A SubtitleEntry object.
        """
        index = int(match.group(1))
        start_time = match.group(2)
        end_time = match.group(3)
        text = match.group(4).strip()
        
        return SubtitleEntry(index, start_time, end_time, text)