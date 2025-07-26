"""
Base parser interface for implementing different subtitle file format parsers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Iterator, Optional


@dataclass
class SubtitleEntry:
    """
    Represents a single subtitle entry.
    
    Attributes:
        index: The index/number of the subtitle.
        start_time: The start time of the subtitle.
        end_time: The end time of the subtitle.
        text: The text content of the subtitle.
    """
    index: int
    start_time: str
    end_time: str
    text: str


class BaseParser(ABC):
    """
    Abstract base class for all subtitle file parsers.
    
    This class defines the interface that all parser implementations must follow.
    It provides a common API for parsing and writing subtitle files in different formats.
    """
    
    @abstractmethod
    def parse(self, file_path: str) -> List[SubtitleEntry]:
        """
        Parse a subtitle file and return a list of subtitle entries.
        
        Args:
            file_path: The path to the subtitle file.
            
        Returns:
            A list of SubtitleEntry objects.
        """
        pass
    
    @abstractmethod
    def write(self, entries: List[SubtitleEntry], output_path: str) -> None:
        """
        Write subtitle entries to a file.
        
        Args:
            entries: The subtitle entries to write.
            output_path: The path to write the subtitle file to.
        """
        pass
    
    @abstractmethod
    def get_extension(self) -> str:
        """
        Get the file extension for this parser.
        
        Returns:
            The file extension (e.g., ".srt").
        """
        pass