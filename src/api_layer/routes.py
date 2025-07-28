"""
API 路由定义
"""
import logging
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse

from .models import (
    TranslationRequest, TranslationResponse, 
    ConfigResponse, HealthResponse,
    FileTranslationResponse
)
from .dependencies import get_translation_service
from ai_layer import TranslationService

logger = logging.getLogger(__name__)


def register_routes(app: FastAPI) -> None:
    """注册所有路由"""
    
    @app.get("/", response_model=dict)
    async def root():
        """根路径"""
        return {"message": "SRT翻译API服务", "version": "1.0.0"}
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check(service: TranslationService = Depends(get_translation_service)):
        """健康检查"""
        is_ready = service.is_ready()
        return HealthResponse(
            status="healthy" if is_ready else "unhealthy",
            ready=is_ready,
            message="服务运行正常" if is_ready else "服务未就绪"
        )
    
    @app.get("/config", response_model=ConfigResponse)
    async def get_config(service: TranslationService = Depends(get_translation_service)):
        """获取配置信息"""
        return ConfigResponse(
            from_language=service.config.from_language,
            to_language=service.config.to_language,
            model=service.config.model,
            prompt_style=service.config.prompt_style.value,
            provider=service.config.ai_api_service.api_service_provider
        )
    
    @app.post("/translate/text", response_model=TranslationResponse)
    async def translate_text(
        request: TranslationRequest,
        service: TranslationService = Depends(get_translation_service)
    ):
        """翻译文本"""
        try:
            result = await service.test_translation(request.text)
            return TranslationResponse(
                success=True,
                translated_text=result,
                message="翻译成功"
            )
        except Exception as e:
            logger.error(f"文本翻译失败: {e}")
            raise HTTPException(status_code=500, detail=f"翻译失败: {str(e)}")
    
    @app.post("/translate/file", response_model=FileTranslationResponse)
    async def translate_file(
        file: UploadFile = File(...),
        max_concurrent: int = Form(5),
        service: TranslationService = Depends(get_translation_service)
    ):
        """翻译SRT文件"""
        if not file.filename.endswith('.srt'):
            raise HTTPException(status_code=400, detail="只支持SRT文件")
        
        try:
            # 保存上传的文件
            temp_dir = Path("/tmp/srt_uploads")
            temp_dir.mkdir(exist_ok=True)
            
            input_path = temp_dir / file.filename
            with open(input_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            # 翻译文件
            output_path = await service.translate_file(
                str(input_path), 
                max_concurrent=max_concurrent
            )
            
            return FileTranslationResponse(
                success=True,
                output_filename=Path(output_path).name,
                download_url=f"/download/{Path(output_path).name}",
                message="文件翻译成功"
            )
            
        except Exception as e:
            logger.error(f"文件翻译失败: {e}")
            raise HTTPException(status_code=500, detail=f"翻译失败: {str(e)}")
    
    @app.get("/download/{filename}")
    async def download_file(filename: str):
        """下载翻译后的文件"""
        # 这里应该有适当的安全检查
        file_path = Path("./output") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/octet-stream"
        )
    
    @app.get("/files", response_model=List[str])
    async def list_output_files():
        """列出输出目录中的文件"""
        output_dir = Path("./output")
        if not output_dir.exists():
            return []
        
        files = [f.name for f in output_dir.glob("*.srt")]
        return files