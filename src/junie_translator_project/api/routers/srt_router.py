"""
SRT Router - Handles SRT file operation API endpoints.

This module defines the API endpoints for SRT file operations.

SRT路由器 - 处理SRT文件操作API端点。

该模块定义了SRT文件操作的API端点。
"""

import os
import logging
import tempfile
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse

from junie_translator_project.entity.config import WebAppConfig
from junie_translator_project.entity.srt import SrtFile, SubtitleEntry
from junie_translator_project.ai.translation_manager import TranslationManager
from junie_translator_project.api.dto.srt_dto import (
    SubtitleEntryDTO,
    SrtFileDTO,
    SrtTranslationRequest,
    SrtTranslationResponse,
    SrtUploadResponse,
    SrtListResponse
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# In-memory storage for uploaded files (in a real application, this would be a database)
UPLOADED_FILES: Dict[str, Dict[str, Any]] = {}


# Dependencies
async def get_translation_manager(
    config: WebAppConfig = Depends()
) -> TranslationManager:
    """
    Dependency for getting the translation manager.
    
    Args:
        config: Web application configuration
        
    Returns:
        Translation manager instance
    """
    # In a real application, this would be a singleton managed by the dependency injection system
    # For simplicity, we're creating a new instance here
    translation_manager = TranslationManager(config=config)
    
    # Start the translation manager
    await translation_manager.start()
    
    try:
        yield translation_manager
    finally:
        # Stop the translation manager when the request is done
        await translation_manager.stop()


def get_upload_directory(config: WebAppConfig = Depends()) -> Path:
    """
    Dependency for getting the upload directory.
    
    Args:
        config: Web application configuration
        
    Returns:
        Path to the upload directory
    """
    upload_dir = Path(config.upload_directory)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


@router.post(
    "/upload",
    response_model=SrtUploadResponse,
    summary="Upload SRT file",
    description="Upload an SRT file for translation"
)
async def upload_srt_file(
    file: UploadFile = File(...),
    upload_dir: Path = Depends(get_upload_directory),
    config: WebAppConfig = Depends()
) -> SrtUploadResponse:
    """
    Upload an SRT file for translation.
    
    Args:
        file: The SRT file to upload
        upload_dir: Upload directory
        config: Web application configuration
        
    Returns:
        Upload response
    """
    try:
        logger.info(f"Uploading SRT file: {file.filename}")
        
        # Check file size
        file_size = 0
        chunk_size = 1024 * 1024  # 1MB
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as temp_file:
            # Read and write the file in chunks
            while chunk := await file.read(chunk_size):
                file_size += len(chunk)
                
                # Check if file size exceeds the limit
                if file_size > config.max_file_size_mb * 1024 * 1024:
                    # Remove the temporary file
                    os.unlink(temp_file.name)
                    
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File size exceeds the limit of {config.max_file_size_mb}MB"
                    )
                
                temp_file.write(chunk)
            
            temp_file_path = temp_file.name
        
        # Parse the SRT file
        try:
            srt_file = SrtFile.from_file(temp_file_path)
        except Exception as e:
            # Remove the temporary file
            os.unlink(temp_file_path)
            
            logger.error(f"Error parsing SRT file: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid SRT file: {str(e)}"
            )
        
        # Generate a unique file ID
        file_id = str(uuid.uuid4())
        
        # Save the file to the upload directory
        upload_path = upload_dir / f"{file_id}_{file.filename}"
        os.rename(temp_file_path, upload_path)
        
        # Store file information
        UPLOADED_FILES[file_id] = {
            "filename": file.filename,
            "path": str(upload_path),
            "entry_count": srt_file.entry_count,
            "upload_time": datetime.now().isoformat(),
            "file_id": file_id
        }
        
        logger.info(f"SRT file uploaded: {file.filename} (ID: {file_id})")
        
        return SrtUploadResponse(
            filename=file.filename,
            entry_count=srt_file.entry_count,
            file_id=file_id
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error uploading SRT file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading SRT file: {str(e)}"
        )


@router.get(
    "/list",
    response_model=SrtListResponse,
    summary="List uploaded SRT files",
    description="List all uploaded SRT files"
)
async def list_srt_files() -> SrtListResponse:
    """
    List all uploaded SRT files.
    
    Returns:
        List of uploaded SRT files
    """
    try:
        logger.info("Listing uploaded SRT files")
        
        # Get all uploaded files
        files = list(UPLOADED_FILES.values())
        
        return SrtListResponse(files=files)
    except Exception as e:
        logger.error(f"Error listing SRT files: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing SRT files: {str(e)}"
        )


@router.get(
    "/file/{file_id}",
    response_model=SrtFileDTO,
    summary="Get SRT file",
    description="Get an uploaded SRT file by ID"
)
async def get_srt_file(file_id: str) -> SrtFileDTO:
    """
    Get an uploaded SRT file by ID.
    
    Args:
        file_id: ID of the uploaded file
        
    Returns:
        SRT file
    """
    try:
        logger.info(f"Getting SRT file: {file_id}")
        
        # Check if file exists
        if file_id not in UPLOADED_FILES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SRT file not found: {file_id}"
            )
        
        # Get file information
        file_info = UPLOADED_FILES[file_id]
        
        # Parse the SRT file
        srt_file = SrtFile.from_file(file_info["path"])
        
        # Convert to DTO
        entries = [
            SubtitleEntryDTO(
                index=entry.index,
                start_time=entry.start_time,
                end_time=entry.end_time,
                content=entry.content
            )
            for entry in srt_file.entries
        ]
        
        return SrtFileDTO(
            filename=file_info["filename"],
            entries=entries,
            metadata=srt_file.metadata
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting SRT file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting SRT file: {str(e)}"
        )


@router.post(
    "/translate/{file_id}",
    response_model=SrtTranslationResponse,
    summary="Translate SRT file",
    description="Translate an uploaded SRT file"
)
async def translate_srt_file(
    file_id: str,
    request: SrtTranslationRequest,
    translation_manager: TranslationManager = Depends(get_translation_manager),
    upload_dir: Path = Depends(get_upload_directory),
    config: WebAppConfig = Depends()
) -> SrtTranslationResponse:
    """
    Translate an uploaded SRT file.
    
    Args:
        file_id: ID of the uploaded file
        request: Translation request
        translation_manager: Translation manager
        upload_dir: Upload directory
        config: Web application configuration
        
    Returns:
        Translation response
    """
    try:
        logger.info(f"Translating SRT file: {file_id} to {request.target_language}")
        
        # Check if file exists
        if file_id not in UPLOADED_FILES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SRT file not found: {file_id}"
            )
        
        # Get file information
        file_info = UPLOADED_FILES[file_id]
        
        # Parse the SRT file
        srt_file = SrtFile.from_file(file_info["path"])
        
        # Translate the SRT file
        translated_file = await translation_manager.translate_srt_file(
            srt_file=srt_file,
            target_language=request.target_language
        )
        
        # Save the translated file
        translated_path = upload_dir / translated_file.filename
        translated_file.to_file(str(translated_path))
        
        # Store the translated file information
        translated_file_id = str(uuid.uuid4())
        UPLOADED_FILES[translated_file_id] = {
            "filename": translated_file.filename,
            "path": str(translated_path),
            "entry_count": translated_file.entry_count,
            "upload_time": datetime.now().isoformat(),
            "file_id": translated_file_id,
            "original_file_id": file_id,
            "target_language": request.target_language,
            "source_language": request.source_language
        }
        
        logger.info(f"SRT file translated: {file_id} to {request.target_language} (ID: {translated_file_id})")
        
        return SrtTranslationResponse(
            original_filename=file_info["filename"],
            translated_filename=translated_file.filename,
            target_language=request.target_language,
            source_language=request.source_language,
            entry_count=translated_file.entry_count,
            download_url=f"/api/srt/download/{translated_file_id}"
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error translating SRT file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error translating SRT file: {str(e)}"
        )


@router.get(
    "/download/{file_id}",
    summary="Download SRT file",
    description="Download an uploaded or translated SRT file"
)
async def download_srt_file(file_id: str) -> FileResponse:
    """
    Download an uploaded or translated SRT file.
    
    Args:
        file_id: ID of the file to download
        
    Returns:
        File response
    """
    try:
        logger.info(f"Downloading SRT file: {file_id}")
        
        # Check if file exists
        if file_id not in UPLOADED_FILES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SRT file not found: {file_id}"
            )
        
        # Get file information
        file_info = UPLOADED_FILES[file_id]
        
        # Return the file
        return FileResponse(
            path=file_info["path"],
            filename=file_info["filename"],
            media_type="application/x-subrip"
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error downloading SRT file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading SRT file: {str(e)}"
        )


@router.delete(
    "/file/{file_id}",
    summary="Delete SRT file",
    description="Delete an uploaded SRT file"
)
async def delete_srt_file(file_id: str) -> Dict[str, Any]:
    """
    Delete an uploaded SRT file.
    
    Args:
        file_id: ID of the file to delete
        
    Returns:
        Deletion status
    """
    try:
        logger.info(f"Deleting SRT file: {file_id}")
        
        # Check if file exists
        if file_id not in UPLOADED_FILES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SRT file not found: {file_id}"
            )
        
        # Get file information
        file_info = UPLOADED_FILES[file_id]
        
        # Delete the file
        try:
            os.unlink(file_info["path"])
        except Exception as e:
            logger.warning(f"Error deleting file {file_info['path']}: {e}")
        
        # Remove from storage
        del UPLOADED_FILES[file_id]
        
        logger.info(f"SRT file deleted: {file_id}")
        
        return {"status": "success", "message": f"File {file_id} deleted"}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error deleting SRT file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting SRT file: {str(e)}"
        )