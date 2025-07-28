"""
Translation Router - Handles translation API endpoints.

This module defines the API endpoints for text translation.

翻译路由器 - 处理翻译API端点。

该模块定义了文本翻译的API端点。
"""

import logging
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status

from junie_translator_project.entity.config import AppConfig, WebAppConfig
from junie_translator_project.ai.translation_manager import TranslationManager
from junie_translator_project.api.dto.translation_dto import (
    TranslationRequest,
    TranslationResponse,
    BatchTranslationRequest,
    BatchTranslationResponse,
    TranslationStatus
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


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


@router.post(
    "/translate",
    response_model=TranslationResponse,
    summary="Translate text",
    description="Translate a single text to the target language"
)
async def translate_text(
    request: TranslationRequest,
    translation_manager: TranslationManager = Depends(get_translation_manager)
) -> TranslationResponse:
    """
    Translate a single text to the target language.
    
    Args:
        request: Translation request
        translation_manager: Translation manager
        
    Returns:
        Translation response
    """
    try:
        logger.info(f"Translating text to {request.target_language}")
        
        # Translate the text
        response = await translation_manager.translate(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language
        )
        
        # Convert to API response model
        return TranslationResponse(
            translated_text=response.translated_text,
            source_text=response.source_text,
            target_language=response.target_language,
            source_language=response.source_language,
            request_id=response.request_id,
            success=response.success,
            error_message=response.error_message
        )
    except Exception as e:
        logger.error(f"Error translating text: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error translating text: {str(e)}"
        )


@router.post(
    "/translate/batch",
    response_model=BatchTranslationResponse,
    summary="Translate multiple texts",
    description="Translate multiple texts to the target language"
)
async def translate_batch(
    request: BatchTranslationRequest,
    translation_manager: TranslationManager = Depends(get_translation_manager)
) -> BatchTranslationResponse:
    """
    Translate multiple texts to the target language.
    
    Args:
        request: Batch translation request
        translation_manager: Translation manager
        
    Returns:
        Batch translation response
    """
    try:
        logger.info(f"Batch translating {len(request.texts)} texts to {request.target_language}")
        
        # Translate the texts
        responses = await translation_manager.translate_batch(
            texts=request.texts,
            target_language=request.target_language,
            source_language=request.source_language
        )
        
        # Convert to API response models
        translation_responses = [
            TranslationResponse(
                translated_text=response.translated_text,
                source_text=response.source_text,
                target_language=response.target_language,
                source_language=response.source_language,
                request_id=response.request_id,
                success=response.success,
                error_message=response.error_message
            )
            for response in responses
        ]
        
        return BatchTranslationResponse(translations=translation_responses)
    except Exception as e:
        logger.error(f"Error batch translating texts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error batch translating texts: {str(e)}"
        )


@router.post(
    "/translate/queued",
    response_model=TranslationResponse,
    summary="Queue text for translation",
    description="Queue a text for translation in a batch"
)
async def translate_queued(
    request: TranslationRequest,
    translation_manager: TranslationManager = Depends(get_translation_manager)
) -> TranslationResponse:
    """
    Queue a text for translation in a batch.
    
    Args:
        request: Translation request
        translation_manager: Translation manager
        
    Returns:
        Translation response
    """
    try:
        logger.info(f"Queueing text for translation to {request.target_language}")
        
        # Queue the text for translation
        response = await translation_manager.translate_queued(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language
        )
        
        # Convert to API response model
        return TranslationResponse(
            translated_text=response.translated_text,
            source_text=response.source_text,
            target_language=response.target_language,
            source_language=response.source_language,
            request_id=response.request_id,
            success=response.success,
            error_message=response.error_message
        )
    except Exception as e:
        logger.error(f"Error queueing text for translation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error queueing text for translation: {str(e)}"
        )


@router.get(
    "/status",
    response_model=TranslationStatus,
    summary="Get translation status",
    description="Get the current status of the translation service"
)
async def get_translation_status(
    translation_manager: TranslationManager = Depends(get_translation_manager)
) -> TranslationStatus:
    """
    Get the current status of the translation service.
    
    Args:
        translation_manager: Translation manager
        
    Returns:
        Translation status
    """
    try:
        logger.info("Getting translation status")
        
        # Get the cache size
        cache_size = translation_manager.get_cache_size()
        
        return TranslationStatus(cache_size=cache_size)
    except Exception as e:
        logger.error(f"Error getting translation status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting translation status: {str(e)}"
        )


@router.post(
    "/cache/clear",
    response_model=TranslationStatus,
    summary="Clear translation cache",
    description="Clear the translation cache"
)
async def clear_translation_cache(
    translation_manager: TranslationManager = Depends(get_translation_manager)
) -> TranslationStatus:
    """
    Clear the translation cache.
    
    Args:
        translation_manager: Translation manager
        
    Returns:
        Translation status
    """
    try:
        logger.info("Clearing translation cache")
        
        # Clear the cache
        translation_manager.clear_cache()
        
        # Get the cache size
        cache_size = translation_manager.get_cache_size()
        
        return TranslationStatus(cache_size=cache_size)
    except Exception as e:
        logger.error(f"Error clearing translation cache: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing translation cache: {str(e)}"
        )