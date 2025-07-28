"""
SRT Entity Module - Core data structures for SRT subtitle files.

This module defines the core data structures for representing SRT subtitle files
and entries, adapted from the original srt_parser.py module.

SRT实体模块 - SRT字幕文件的核心数据结构。

该模块定义了表示SRT字幕文件和条目的核心数据结构，改编自原始的srt_parser.py模块。
"""

import re
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any


@dataclass
class SubtitleEntry:
    """
    Represents a single subtitle entry in an SRT file.
    
    表示SRT文件中的单个字幕条目。
    """
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the subtitle entry to a dictionary for serialization."""
        return {
            "index": self.index,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "content": self.content
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SubtitleEntry':
        """Create a subtitle entry from a dictionary."""
        return cls(
            index=data["index"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            content=data["content"]
        )


@dataclass
class SrtFile:
    """
    Represents a complete SRT subtitle file with multiple entries.
    
    表示包含多个条目的完整SRT字幕文件。
    """
    path: str
    entries: List[SubtitleEntry] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize the path as a Path object if it's a string."""
        if isinstance(self.path, str):
            self.path = Path(self.path)

    @property
    def filename(self) -> str:
        """Get the filename without the directory."""
        return self.path.name
    
    @property
    def stem(self) -> str:
        """Get the filename without the extension."""
        return self.path.stem
    
    @property
    def entry_count(self) -> int:
        """Get the number of subtitle entries."""
        return len(self.entries)
    
    def add_entry(self, entry: SubtitleEntry) -> None:
        """Add a subtitle entry to the file."""
        self.entries.append(entry)
    
    def get_content_lines(self) -> List[str]:
        """Get all content lines from all subtitle entries."""
        lines = []
        for entry in self.entries:
            lines.extend(entry.content)
        return lines
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the SRT file to a dictionary for serialization."""
        return {
            "path": str(self.path),
            "entries": [entry.to_dict() for entry in self.entries],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SrtFile':
        """Create an SRT file from a dictionary."""
        return cls(
            path=data["path"],
            entries=[SubtitleEntry.from_dict(entry) for entry in data["entries"]],
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_file(cls, file_path: str) -> 'SrtFile':
        """
        Create an SRT file by parsing an existing file.
        
        Args:
            file_path: Path to the SRT file to parse
            
        Returns:
            An SrtFile instance with parsed entries
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"SRT file not found: {file_path}")
        
        srt_file = cls(path=file_path)
        
        # Parse the file content
        with open(path, 'r', encoding='utf-8') as file:
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
                
                srt_file.add_entry(SubtitleEntry(
                    index=index,
                    start_time=start_time,
                    end_time=end_time,
                    content=content_lines
                ))
            except Exception as e:
                print(f"Error parsing entry: {block}\nError: {e}")
                continue
        
        # Add file hash to metadata
        with open(path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()[:8]
            srt_file.metadata["file_hash"] = file_hash
        
        return srt_file
    
    def to_file(self, output_path: Optional[str] = None) -> str:
        """
        Write the SRT file to disk.
        
        Args:
            output_path: Path to the output file (if None, will use self.path)
            
        Returns:
            The path to the written file
        """
        path = Path(output_path) if output_path else self.path
        
        with open(path, 'w', encoding='utf-8') as file:
            for i, entry in enumerate(self.entries):
                # Update index to ensure sequential numbering
                entry.index = i + 1
                file.write(str(entry))
                file.write('\n')  # Add empty line between entries
        
        return str(path)
    
    @staticmethod
    def generate_output_filename(
        input_path: str, 
        from_language: str, 
        target_language: str, 
        output_dir: Optional[str] = None
    ) -> str:
        """
        Generate an output filename based on the input path, source language, target language, and file hash.
        
        Args:
            input_path: Path to the input SRT file
            from_language: Source language code or name
            target_language: Target language code or name
            output_dir: Optional output directory
            
        Returns:
            Generated output filename
        """
        input_path = Path(input_path)
        stem = input_path.stem
        
        # Calculate hash of the file content
        with open(input_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()[:8]
        
        # Create the new filename with source language, target language, and hash
        new_filename = f"{stem}_{from_language}{target_language}_{file_hash}{input_path.suffix}"
        
        # If output directory is specified, use it
        if output_dir:
            output_dir_path = Path(output_dir)
            # Create the directory if it doesn't exist
            output_dir_path.mkdir(parents=True, exist_ok=True)
            return str(output_dir_path / new_filename)
        else:
            return str(input_path.with_name(new_filename))