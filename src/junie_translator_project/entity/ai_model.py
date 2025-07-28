"""
AI Model Entity Module - Core data structures for AI models and providers.

This module defines the core data structures for representing AI models and providers,
based on the configuration in aiprovider.json.

AI模型实体模块 - AI模型和提供商的核心数据结构。

该模块定义了表示AI模型和提供商的核心数据结构，基于aiprovider.json中的配置。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set


@dataclass
class AIModel:
    """
    Represents an AI model configuration.
    
    表示AI模型配置。
    """
    name: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    aliases: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the AI model to a dictionary for serialization."""
        return {
            "name": self.name,
            "max-tokens": self.max_tokens,
            "temperature": self.temperature,
            "aliases": self.aliases
        }
    
    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'AIModel':
        """Create an AI model from a dictionary."""
        return cls(
            name=name,
            max_tokens=data.get("max-tokens"),
            temperature=data.get("temperature"),
            aliases=data.get("aliases", [])
        )


@dataclass
class AIProvider:
    """
    Represents an AI provider configuration.
    
    表示AI提供商配置。
    """
    name: str
    api_endpoint: Optional[str] = None
    models: Dict[str, AIModel] = field(default_factory=dict)
    
    def add_model(self, model: AIModel) -> None:
        """Add a model to the provider."""
        self.models[model.name] = model
    
    def get_model(self, model_name: str) -> Optional[AIModel]:
        """
        Get a model by name or alias.
        
        Args:
            model_name: The name or alias of the model
            
        Returns:
            The model if found, None otherwise
        """
        # Check if the model exists directly
        if model_name in self.models:
            return self.models[model_name]
        
        # Check if the model is an alias for another model
        for model in self.models.values():
            if model_name in model.aliases:
                return model
        
        return None
    
    def get_model_names(self) -> List[str]:
        """Get a list of all model names."""
        return list(self.models.keys())
    
    def get_all_model_names_and_aliases(self) -> Set[str]:
        """Get a set of all model names and aliases."""
        names = set(self.models.keys())
        for model in self.models.values():
            names.update(model.aliases)
        return names
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the AI provider to a dictionary for serialization."""
        return {
            "api-endpoint": self.api_endpoint,
            "models": {
                model.name: model.to_dict() for model in self.models.values()
            }
        }
    
    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'AIProvider':
        """Create an AI provider from a dictionary."""
        provider = cls(
            name=name,
            api_endpoint=data.get("api-endpoint")
        )
        
        # Add models
        models_data = data.get("models", {})
        for model_name, model_data in models_data.items():
            model = AIModel.from_dict(model_name, model_data)
            provider.add_model(model)
        
        return provider


@dataclass
class AIProviderRegistry:
    """
    Registry of AI providers.
    
    AI提供商注册表。
    """
    providers: Dict[str, AIProvider] = field(default_factory=dict)
    
    def add_provider(self, provider: AIProvider) -> None:
        """Add a provider to the registry."""
        self.providers[provider.name] = provider
    
    def get_provider(self, provider_name: str) -> Optional[AIProvider]:
        """
        Get a provider by name.
        
        Args:
            provider_name: The name of the provider
            
        Returns:
            The provider if found, None otherwise
        """
        return self.providers.get(provider_name.lower())
    
    def get_provider_names(self) -> List[str]:
        """Get a list of all provider names."""
        return list(self.providers.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the AI provider registry to a dictionary for serialization."""
        return {
            "providers": {
                provider.name: provider.to_dict() for provider in self.providers.values()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIProviderRegistry':
        """Create an AI provider registry from a dictionary."""
        registry = cls()
        
        providers_data = data.get("providers", {})
        for provider_name, provider_data in providers_data.items():
            provider = AIProvider.from_dict(provider_name, provider_data)
            registry.add_provider(provider)
        
        return registry
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'AIProviderRegistry':
        """
        Load an AI provider registry from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            An AIProviderRegistry instance
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file is not valid JSON
        """
        import json
        from pathlib import Path
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"AI provider configuration file not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save the AI provider registry to a JSON file.
        
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