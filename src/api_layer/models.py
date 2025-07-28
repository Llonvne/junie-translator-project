"""
API 数据模型 (Pydantic Models)
"""
from typing import Optional
from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    """翻译请求模型"""
    text: str = Field(..., description="要翻译的文本", min_length=1)
    target_language: Optional[str] = Field(None, description="目标语言，如果不提供则使用配置中的默认值")


class TranslationResponse(BaseModel):
    """翻译响应模型"""
    success: bool = Field(..., description="翻译是否成功")
    translated_text: Optional[str] = Field(None, description="翻译后的文本")
    message: str = Field(..., description="响应消息")


class FileTranslationResponse(BaseModel):
    """文件翻译响应模型"""
    success: bool = Field(..., description="翻译是否成功")
    output_filename: Optional[str] = Field(None, description="输出文件名")
    download_url: Optional[str] = Field(None, description="下载链接")
    message: str = Field(..., description="响应消息")


class ConfigResponse(BaseModel):
    """配置响应模型"""
    from_language: str = Field(..., description="源语言")
    to_language: str = Field(..., description="目标语言")
    model: str = Field(..., description="AI模型")
    prompt_style: str = Field(..., description="提示词风格")
    provider: str = Field(..., description="AI服务提供商")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    ready: bool = Field(..., description="是否就绪")
    message: str = Field(..., description="状态消息")