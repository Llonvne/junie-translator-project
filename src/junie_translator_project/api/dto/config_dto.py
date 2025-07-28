"""
Config DTOs - Data Transfer Objects for configuration endpoints.

This module defines the request and response models for configuration endpoints.

配置DTO - 配置端点的数据传输对象。

该模块定义了配置端点的请求和响应模型。
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AIServiceConfigDTO(BaseModel):
    """
    DTO for AI service configuration.
    
    AI服务配置的DTO。
    """
    api_service_provider: str = Field("auto", description="AI service provider (auto, openai, deepseek, mock)")
    api_key: Optional[str] = Field(None, description="API key for the service provider")
    
    class Config:
        schema_extra = {
            "example": {
                "api_service_provider": "openai",
                "api_key": "sk-..."
            }
        }


class AppConfigDTO(BaseModel):
    """
    DTO for application configuration.
    
    应用程序配置的DTO。
    """
    from_language: str = Field("auto", description="Source language (default: auto-detect)")
    to_language: str = Field("English", description="Target language")
    ai_api_service: AIServiceConfigDTO = Field(default_factory=AIServiceConfigDTO, description="AI service configuration")
    output_directory: Optional[str] = Field(None, description="Directory for output files")
    model: Optional[str] = Field(None, description="Model to use for translation")
    prompt_style: str = Field("default", description="Style of prompts to use (default, chinese, formal, etc.)")
    enable_post_check: bool = Field(False, description="Whether to check translations for explanations and remove them")
    
    class Config:
        schema_extra = {
            "example": {
                "from_language": "auto",
                "to_language": "Spanish",
                "ai_api_service": {
                    "api_service_provider": "openai",
                    "api_key": "sk-..."
                },
                "output_directory": "./output",
                "model": "gpt-3.5-turbo",
                "prompt_style": "default",
                "enable_post_check": False
            }
        }


class WebAppConfigDTO(AppConfigDTO):
    """
    DTO for web application configuration.
    
    Web应用程序配置的DTO。
    """
    server_host: str = Field("0.0.0.0", description="Host to bind to")
    server_port: int = Field(8000, description="Port to bind to")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"], description="CORS origins")
    upload_directory: str = Field("./uploads", description="Directory for uploaded files")
    max_file_size_mb: int = Field(10, description="Maximum file size in MB")
    
    class Config:
        schema_extra = {
            "example": {
                "from_language": "auto",
                "to_language": "Spanish",
                "ai_api_service": {
                    "api_service_provider": "openai",
                    "api_key": "sk-..."
                },
                "output_directory": "./output",
                "model": "gpt-3.5-turbo",
                "prompt_style": "default",
                "enable_post_check": False,
                "server_host": "0.0.0.0",
                "server_port": 8000,
                "cors_origins": ["*"],
                "upload_directory": "./uploads",
                "max_file_size_mb": 10
            }
        }


class AIModelDTO(BaseModel):
    """
    DTO for an AI model.
    
    AI模型的DTO。
    """
    name: str = Field(..., description="Name of the model")
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens")
    temperature: Optional[float] = Field(None, description="Temperature for generation")
    aliases: List[str] = Field(default_factory=list, description="Aliases for the model")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "gpt-3.5-turbo",
                "max_tokens": 1024,
                "temperature": 0.3,
                "aliases": ["gpt-3.5", "3.5"]
            }
        }


class AIProviderDTO(BaseModel):
    """
    DTO for an AI provider.
    
    AI提供商的DTO。
    """
    name: str = Field(..., description="Name of the provider")
    api_endpoint: Optional[str] = Field(None, description="API endpoint for the provider")
    models: Dict[str, AIModelDTO] = Field(default_factory=dict, description="Models available for the provider")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "openai",
                "api_endpoint": "https://api.openai.com/v1",
                "models": {
                    "gpt-3.5-turbo": {
                        "name": "gpt-3.5-turbo",
                        "max_tokens": 1024,
                        "temperature": 0.3,
                        "aliases": ["gpt-3.5", "3.5"]
                    },
                    "gpt-4": {
                        "name": "gpt-4",
                        "max_tokens": 2048,
                        "temperature": 0.3,
                        "aliases": []
                    }
                }
            }
        }


class AIProvidersDTO(BaseModel):
    """
    DTO for AI providers.
    
    AI提供商的DTO。
    """
    providers: Dict[str, AIProviderDTO] = Field(..., description="Available AI providers")
    
    class Config:
        schema_extra = {
            "example": {
                "providers": {
                    "openai": {
                        "name": "openai",
                        "api_endpoint": "https://api.openai.com/v1",
                        "models": {
                            "gpt-3.5-turbo": {
                                "name": "gpt-3.5-turbo",
                                "max_tokens": 1024,
                                "temperature": 0.3,
                                "aliases": ["gpt-3.5", "3.5"]
                            }
                        }
                    },
                    "mock": {
                        "name": "mock",
                        "api_endpoint": null,
                        "models": {
                            "mock": {
                                "name": "mock",
                                "max_tokens": null,
                                "temperature": null,
                                "aliases": []
                            }
                        }
                    }
                }
            }
        }


class PromptTemplateDTO(BaseModel):
    """
    DTO for a prompt template.
    
    提示词模板的DTO。
    """
    system: str = Field(..., description="System prompt")
    user: str = Field(..., description="User prompt template")
    
    class Config:
        schema_extra = {
            "example": {
                "system": "You are a professional translator. Translate the text accurately while preserving the original meaning, tone, and formatting.",
                "user": "Translate the following text to {target_language}. Preserve any formatting and special characters:\n\n{text}"
            }
        }


class PromptStylesDTO(BaseModel):
    """
    DTO for prompt styles.
    
    提示词样式的DTO。
    """
    styles: Dict[str, PromptTemplateDTO] = Field(..., description="Available prompt styles")
    
    class Config:
        schema_extra = {
            "example": {
                "styles": {
                    "default": {
                        "system": "You are a professional translator. Translate the text accurately while preserving the original meaning, tone, and formatting.",
                        "user": "Translate the following text to {target_language}. Preserve any formatting and special characters:\n\n{text}"
                    },
                    "formal": {
                        "system": "You are a professional translator specializing in formal and official documents. Translate the text with a formal tone while preserving the original meaning and formatting.",
                        "user": "Translate the following formal document to {target_language}. Maintain a formal tone and preserve all formatting and special characters:\n\n{text}"
                    }
                }
            }
        }