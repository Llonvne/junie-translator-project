"""
Config Entity Module - Core data structures for application configuration.

This module defines the core data structures for representing application configuration,
based on the structure in config.json.

配置实体模块 - 应用程序配置的核心数据结构。

该模块定义了表示应用程序配置的核心数据结构，基于config.json中的结构。
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List
from pathlib import Path


@dataclass
class AIServiceConfig:
    """
    Represents AI service configuration.
    
    表示AI服务配置。
    """
    api_service_provider: str = "auto"
    api_key: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the AI service configuration to a dictionary for serialization."""
        return {
            "api-service-provider": self.api_service_provider,
            "api-key": self.api_key
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIServiceConfig':
        """Create an AI service configuration from a dictionary."""
        return cls(
            api_service_provider=data.get("api-service-provider", "auto"),
            api_key=data.get("api-key")
        )


@dataclass
class AppConfig:
    """
    Represents application configuration.
    
    表示应用程序配置。
    """
    from_language: str = "auto"
    to_language: str = "English"
    ai_api_service: AIServiceConfig = field(default_factory=AIServiceConfig)
    output_directory: Optional[str] = None
    model: Optional[str] = None
    prompt_style: str = "default"
    enable_post_check: bool = False
    
    def __post_init__(self):
        """Initialize the output directory as a Path object if it's a string."""
        if isinstance(self.output_directory, str):
            self.output_directory = Path(self.output_directory)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the application configuration to a dictionary for serialization."""
        return {
            "from-language": self.from_language,
            "to-language": self.to_language,
            "ai-api-service": self.ai_api_service.to_dict(),
            "output-directory": str(self.output_directory) if self.output_directory else None,
            "model": self.model,
            "prompt-style": self.prompt_style,
            "enable-post-check": self.enable_post_check
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """Create an application configuration from a dictionary."""
        ai_api_service_data = data.get("ai-api-service", {})
        if not isinstance(ai_api_service_data, dict):
            ai_api_service_data = {}
        
        return cls(
            from_language=data.get("from-language", "auto"),
            to_language=data.get("to-language", "English"),
            ai_api_service=AIServiceConfig.from_dict(ai_api_service_data),
            output_directory=data.get("output-directory"),
            model=data.get("model"),
            prompt_style=data.get("prompt-style", "default"),
            enable_post_check=data.get("enable-post-check", False)
        )
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'AppConfig':
        """
        Load application configuration from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            An AppConfig instance
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file is not valid JSON
        """
        import json
        from pathlib import Path
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save the application configuration to a JSON file.
        
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


@dataclass
class WebAppConfig(AppConfig):
    """
    Extended application configuration for the web application.
    
    为Web应用程序扩展的应用程序配置。
    """
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    upload_directory: str = "./uploads"
    max_file_size_mb: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the web application configuration to a dictionary for serialization."""
        config_dict = super().to_dict()
        config_dict.update({
            "server-host": self.server_host,
            "server-port": self.server_port,
            "cors-origins": self.cors_origins,
            "upload-directory": self.upload_directory,
            "max-file-size-mb": self.max_file_size_mb
        })
        return config_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebAppConfig':
        """Create a web application configuration from a dictionary."""
        config = super().from_dict(data)
        
        return cls(
            from_language=config.from_language,
            to_language=config.to_language,
            ai_api_service=config.ai_api_service,
            output_directory=config.output_directory,
            model=config.model,
            prompt_style=config.prompt_style,
            enable_post_check=config.enable_post_check,
            server_host=data.get("server-host", "0.0.0.0"),
            server_port=data.get("server-port", 8000),
            cors_origins=data.get("cors-origins", ["*"]),
            upload_directory=data.get("upload-directory", "./uploads"),
            max_file_size_mb=data.get("max-file-size-mb", 10)
        )


def get_default_config() -> AppConfig:
    """
    Get a default application configuration.
    
    Returns:
        An AppConfig instance with default values
    """
    return AppConfig()


def get_default_webapp_config() -> WebAppConfig:
    """
    Get a default web application configuration.
    
    Returns:
        A WebAppConfig instance with default values
    """
    return WebAppConfig()