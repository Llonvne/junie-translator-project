"""
SRT 字幕文件实体
"""
import re
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class SubtitleEntry:
    """字幕条目实体"""
    index: int
    start_time: str
    end_time: str
    content: List[str]

    def __str__(self) -> str:
        """转换为SRT格式字符串"""
        return (
            f"{self.index}\n"
            f"{self.start_time} --> {self.end_time}\n"
            f"{'\n'.join(self.content)}\n"
        )

    @property
    def text(self) -> str:
        """获取字幕文本内容"""
        return '\n'.join(self.content)

    def set_text(self, text: str) -> None:
        """设置字幕文本内容"""
        self.content = text.split('\n')


@dataclass 
class SrtFile:
    """SRT文件实体"""
    file_path: Path
    entries: List[SubtitleEntry]
    encoding: str = 'utf-8'

    @classmethod
    def from_file(cls, file_path: str) -> 'SrtFile':
        """从文件加载SRT"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"SRT文件不存在: {file_path}")
        
        entries = cls._parse_srt_content(path)
        return cls(file_path=path, entries=entries)

    @staticmethod
    def _parse_srt_content(file_path: Path) -> List[SubtitleEntry]:
        """解析SRT文件内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        entries = []
        # 正则匹配SRT格式
        pattern = r'(\d+)\n([\d:,]+)\s*-->\s*([\d:,]+)\n(.*?)(?=\n\d+\n|\n*$)'
        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            index = int(match[0])
            start_time = match[1].strip()
            end_time = match[2].strip()
            content_lines = [line.strip() for line in match[3].strip().split('\n') if line.strip()]
            
            entries.append(SubtitleEntry(
                index=index,
                start_time=start_time,
                end_time=end_time,
                content=content_lines
            ))

        return entries

    def save_to_file(self, output_path: str) -> None:
        """保存到文件"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding=self.encoding) as f:
            for entry in self.entries:
                f.write(str(entry) + '\n')

    def get_file_hash(self) -> str:
        """获取文件内容哈希"""
        content = ''.join(str(entry) for entry in self.entries)
        return hashlib.md5(content.encode()).hexdigest()[:8]

    @property
    def total_entries(self) -> int:
        """获取字幕条目总数"""
        return len(self.entries)

    def get_all_text(self) -> List[str]:
        """获取所有字幕文本"""
        return [entry.text for entry in self.entries]