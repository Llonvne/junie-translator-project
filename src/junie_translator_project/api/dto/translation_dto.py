"""
Translation DTOs - Data Transfer Objects for translation endpoints.

This module defines the request and response models for translation endpoints.

翻译DTO - 翻译端点的数据传输对象。

该模块定义了翻译端点的请求和响应模型。
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    """
    Request model for translating text.
    
    翻译文本的请求模型。
    """
    text: str = Field(..., description="The text to translate")
    target_language: str = Field(..., description="The target language for translation")
    source_language: str = Field("auto", description="The source language (default: auto-detect)")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Hello, world!",
                "target_language": "Spanish",
                "source_language": "auto"
            }
        }


class TranslationResponse(BaseModel):
    """
    Response model for translated text.
    
    翻译文本的响应模型。
    """
    translated_text: str = Field(..., description="The translated text")
    source_text: str = Field(..., description="The original text")
    target_language: str = Field(..., description="The target language")
    source_language: str = Field(..., description="The source language (may be auto-detected)")
    request_id: str = Field(..., description="Unique identifier for the translation request")
    success: bool = Field(True, description="Whether the translation was successful")
    error_message: Optional[str] = Field(None, description="Error message if translation failed")
    
    class Config:
        schema_extra = {
            "example": {
                "translated_text": "¡Hola, mundo!",
                "source_text": "Hello, world!",
                "target_language": "Spanish",
                "source_language": "English",
                "request_id": "abcdef1234567890",
                "success": True,
                "error_message": None
            }
        }


class BatchTranslationRequest(BaseModel):
    """
    Request model for batch translating multiple texts.
    
    批量翻译多个文本的请求模型。
    """
    texts: List[str] = Field(..., description="List of texts to translate")
    target_language: str = Field(..., description="The target language for translation")
    source_language: str = Field("auto", description="The source language (default: auto-detect)")
    
    class Config:
        schema_extra = {
            "example": {
                "texts": ["Hello, world!", "How are you?"],
                "target_language": "Spanish",
                "source_language": "auto"
            }
        }


class BatchTranslationResponse(BaseModel):
    """
    Response model for batch translated texts.
    
    批量翻译文本的响应模型。
    """
    translations: List[TranslationResponse] = Field(..., description="List of translation responses")
    
    class Config:
        schema_extra = {
            "example": {
                "translations": [
                    {
                        "translated_text": "¡Hola, mundo!",
                        "source_text": "Hello, world!",
                        "target_language": "Spanish",
                        "source_language": "English",
                        "request_id": "abcdef1234567890",
                        "success": True,
                        "error_message": None
                    },
                    {
                        "translated_text": "¿Cómo estás?",
                        "source_text": "How are you?",
                        "target_language": "Spanish",
                        "source_language": "English",
                        "request_id": "abcdef1234567891",
                        "success": True,
                        "error_message": None
                    }
                ]
            }
        }


class TranslationStatus(BaseModel):
    """
    Response model for translation status.
    
    翻译状态的响应模型。
    """
    cache_size: int = Field(..., description="Current size of the translation cache")
    
    class Config:
        schema_extra = {
            "example": {
                "cache_size": 42
            }
        }