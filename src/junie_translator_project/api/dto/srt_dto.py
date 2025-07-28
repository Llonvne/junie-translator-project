"""
SRT DTOs - Data Transfer Objects for SRT file operation endpoints.

This module defines the request and response models for SRT file operation endpoints.

SRT DTO - SRT文件操作端点的数据传输对象。

该模块定义了SRT文件操作端点的请求和响应模型。
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SubtitleEntryDTO(BaseModel):
    """
    DTO for a subtitle entry.
    
    字幕条目的DTO。
    """
    index: int = Field(..., description="Index of the subtitle entry")
    start_time: str = Field(..., description="Start time of the subtitle (format: 00:00:00,000)")
    end_time: str = Field(..., description="End time of the subtitle (format: 00:00:00,000)")
    content: List[str] = Field(..., description="Content lines of the subtitle")
    
    class Config:
        schema_extra = {
            "example": {
                "index": 1,
                "start_time": "00:00:01,000",
                "end_time": "00:00:04,000",
                "content": ["Hello, world!", "This is a subtitle."]
            }
        }


class SrtFileDTO(BaseModel):
    """
    DTO for an SRT file.
    
    SRT文件的DTO。
    """
    filename: str = Field(..., description="Name of the SRT file")
    entries: List[SubtitleEntryDTO] = Field(..., description="Subtitle entries in the file")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata for the SRT file")
    
    class Config:
        schema_extra = {
            "example": {
                "filename": "example.srt",
                "entries": [
                    {
                        "index": 1,
                        "start_time": "00:00:01,000",
                        "end_time": "00:00:04,000",
                        "content": ["Hello, world!", "This is a subtitle."]
                    },
                    {
                        "index": 2,
                        "start_time": "00:00:05,000",
                        "end_time": "00:00:08,000",
                        "content": ["This is another subtitle."]
                    }
                ],
                "metadata": {
                    "file_hash": "abcdef12"
                }
            }
        }


class SrtTranslationRequest(BaseModel):
    """
    Request model for translating an SRT file.
    
    翻译SRT文件的请求模型。
    """
    target_language: str = Field(..., description="The target language for translation")
    source_language: str = Field("auto", description="The source language (default: auto-detect)")
    
    class Config:
        schema_extra = {
            "example": {
                "target_language": "Spanish",
                "source_language": "auto"
            }
        }


class SrtTranslationResponse(BaseModel):
    """
    Response model for a translated SRT file.
    
    翻译后的SRT文件的响应模型。
    """
    original_filename: str = Field(..., description="Original filename")
    translated_filename: str = Field(..., description="Translated filename")
    target_language: str = Field(..., description="Target language")
    source_language: str = Field(..., description="Source language (may be auto-detected)")
    entry_count: int = Field(..., description="Number of subtitle entries")
    download_url: str = Field(..., description="URL to download the translated file")
    
    class Config:
        schema_extra = {
            "example": {
                "original_filename": "example.srt",
                "translated_filename": "example_enEs_abcdef12.srt",
                "target_language": "Spanish",
                "source_language": "English",
                "entry_count": 42,
                "download_url": "/api/srt/download/example_enEs_abcdef12.srt"
            }
        }


class SrtUploadResponse(BaseModel):
    """
    Response model for an uploaded SRT file.
    
    上传的SRT文件的响应模型。
    """
    filename: str = Field(..., description="Uploaded filename")
    entry_count: int = Field(..., description="Number of subtitle entries")
    file_id: str = Field(..., description="Unique identifier for the file")
    
    class Config:
        schema_extra = {
            "example": {
                "filename": "example.srt",
                "entry_count": 42,
                "file_id": "abcdef1234567890"
            }
        }


class SrtListResponse(BaseModel):
    """
    Response model for listing uploaded SRT files.
    
    列出上传的SRT文件的响应模型。
    """
    files: List[Dict[str, Any]] = Field(..., description="List of uploaded SRT files")
    
    class Config:
        schema_extra = {
            "example": {
                "files": [
                    {
                        "filename": "example1.srt",
                        "entry_count": 42,
                        "file_id": "abcdef1234567890",
                        "upload_time": "2023-01-01T12:00:00Z"
                    },
                    {
                        "filename": "example2.srt",
                        "entry_count": 24,
                        "file_id": "abcdef1234567891",
                        "upload_time": "2023-01-02T12:00:00Z"
                    }
                ]
            }
        }