"""
Prompt Entity Module - Core data structures for translation prompts.

This module defines the core data structures for representing translation prompts,
based on the configuration in prompts.json.

提示词实体模块 - 翻译提示词的核心数据结构。

该模块定义了表示翻译提示词的核心数据结构，基于prompts.json中的配置。
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List


@dataclass
class PromptTemplate:
    """
    Represents a prompt template for translation.
    
    表示翻译的提示词模板。
    """
    system: str
    user: str
    
    def format_user_prompt(self, target_language: str, text: str) -> str:
        """
        Format the user prompt with the target language and text.
        
        Args:
            target_language: The target language for translation
            text: The text to translate
            
        Returns:
            The formatted user prompt
        """
        return self.user.format(target_language=target_language, text=text)
    
    def to_dict(self) -> Dict[str, str]:
        """Convert the prompt template to a dictionary for serialization."""
        return {
            "system": self.system,
            "user": self.user
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'PromptTemplate':
        """Create a prompt template from a dictionary."""
        return cls(
            system=data["system"],
            user=data["user"]
        )


@dataclass
class PromptStyle:
    """
    Represents a style of prompts with a name and template.
    
    表示具有名称和模板的提示词样式。
    """
    name: str
    template: PromptTemplate
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the prompt style to a dictionary for serialization."""
        return self.template.to_dict()
    
    @classmethod
    def from_dict(cls, name: str, data: Dict[str, str]) -> 'PromptStyle':
        """Create a prompt style from a dictionary."""
        return cls(
            name=name,
            template=PromptTemplate.from_dict(data)
        )


@dataclass
class PromptRegistry:
    """
    Registry of prompt styles.
    
    提示词样式注册表。
    """
    styles: Dict[str, PromptStyle] = field(default_factory=dict)
    
    def add_style(self, style: PromptStyle) -> None:
        """Add a style to the registry."""
        self.styles[style.name] = style
    
    def get_style(self, style_name: str, default_style: str = "default") -> PromptStyle:
        """
        Get a style by name, falling back to the default style if not found.
        
        Args:
            style_name: The name of the style
            default_style: The name of the default style to use if the requested style is not found
            
        Returns:
            The requested style if found, otherwise the default style
            
        Raises:
            ValueError: If neither the requested style nor the default style is found
        """
        if style_name in self.styles:
            return self.styles[style_name]
        
        if default_style in self.styles:
            return self.styles[default_style]
        
        raise ValueError(f"Neither the requested style '{style_name}' nor the default style '{default_style}' was found")
    
    def get_style_names(self) -> List[str]:
        """Get a list of all style names."""
        return list(self.styles.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the prompt registry to a dictionary for serialization."""
        return {
            style.name: style.to_dict() for style in self.styles.values()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptRegistry':
        """Create a prompt registry from a dictionary."""
        registry = cls()
        
        for style_name, style_data in data.items():
            style = PromptStyle.from_dict(style_name, style_data)
            registry.add_style(style)
        
        return registry
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'PromptRegistry':
        """
        Load a prompt registry from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            A PromptRegistry instance
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file is not valid JSON
        """
        import json
        from pathlib import Path
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Prompt configuration file not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save the prompt registry to a JSON file.
        
        Args:
            file_path: Path to the JSON file
        """
        import json
        from pathlib import Path
        
        path = Path(file_path)
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)


# Default prompts if prompts.json is not available
DEFAULT_PROMPTS = {
    "default": {
        "system": "You are a professional translator. Translate the text accurately while preserving the original meaning, tone, and formatting. IMPORTANT: Only output the translated text without any explanations, notes, or additional content.",
        "user": "Translate the following text to {target_language}. Preserve any formatting and special characters. IMPORTANT: Only output the translated text without any explanations, notes, or additional content:\n\n{text}"
    }
}


def get_default_prompt_registry() -> PromptRegistry:
    """
    Get a default prompt registry with built-in prompts.
    
    Returns:
        A PromptRegistry instance with default prompts
    """
    registry = PromptRegistry()
    
    for style_name, style_data in DEFAULT_PROMPTS.items():
        style = PromptStyle.from_dict(style_name, style_data)
        registry.add_style(style)
    
    return registry