"""
Config Router - Handles configuration API endpoints.

This module defines the API endpoints for application configuration.

配置路由器 - 处理配置API端点。

该模块定义了应用程序配置的API端点。
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks

from junie_translator_project.entity.config import AppConfig, WebAppConfig, AIServiceConfig
from junie_translator_project.entity.ai_model import AIProviderRegistry, AIProvider, AIModel
from junie_translator_project.entity.prompt import PromptRegistry, PromptStyle, PromptTemplate
from junie_translator_project.api.dto.config_dto import (
    AIServiceConfigDTO,
    AppConfigDTO,
    WebAppConfigDTO,
    AIModelDTO,
    AIProviderDTO,
    AIProvidersDTO,
    PromptTemplateDTO,
    PromptStylesDTO
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# Dependencies
def get_config() -> WebAppConfig:
    """
    Dependency for getting the application configuration.
    
    Returns:
        Web application configuration
    """
    try:
        # Try to load from config.json
        config = WebAppConfig.load_from_file("config.json")
        return config
    except Exception as e:
        logger.warning(f"Failed to load config from file: {e}")
        # Return default config
        return WebAppConfig()


def get_ai_providers() -> AIProviderRegistry:
    """
    Dependency for getting the AI provider registry.
    
    Returns:
        AI provider registry
    """
    try:
        # Try to load from aiprovider.json
        registry = AIProviderRegistry.load_from_file("aiprovider.json")
        return registry
    except Exception as e:
        logger.warning(f"Failed to load AI providers from file: {e}")
        # Return empty registry
        return AIProviderRegistry()


def get_prompt_styles() -> PromptRegistry:
    """
    Dependency for getting the prompt registry.
    
    Returns:
        Prompt registry
    """
    try:
        # Try to load from prompts.json
        registry = PromptRegistry.load_from_file("prompts.json")
        return registry
    except Exception as e:
        logger.warning(f"Failed to load prompt styles from file: {e}")
        # Return empty registry
        return PromptRegistry()


@router.get(
    "/app",
    response_model=AppConfigDTO,
    summary="Get application configuration",
    description="Get the current application configuration"
)
async def get_app_config(
    config: WebAppConfig = Depends(get_config)
) -> AppConfigDTO:
    """
    Get the current application configuration.
    
    Args:
        config: Web application configuration
        
    Returns:
        Application configuration
    """
    try:
        logger.info("Getting application configuration")
        
        # Convert to DTO
        return AppConfigDTO(
            from_language=config.from_language,
            to_language=config.to_language,
            ai_api_service=AIServiceConfigDTO(
                api_service_provider=config.ai_api_service.api_service_provider,
                api_key=config.ai_api_service.api_key
            ),
            output_directory=str(config.output_directory) if config.output_directory else None,
            model=config.model,
            prompt_style=config.prompt_style,
            enable_post_check=config.enable_post_check
        )
    except Exception as e:
        logger.error(f"Error getting application configuration: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting application configuration: {str(e)}"
        )


@router.put(
    "/app",
    response_model=AppConfigDTO,
    summary="Update application configuration",
    description="Update the application configuration"
)
async def update_app_config(
    config_dto: AppConfigDTO,
    background_tasks: BackgroundTasks
) -> AppConfigDTO:
    """
    Update the application configuration.
    
    Args:
        config_dto: Application configuration DTO
        background_tasks: Background tasks
        
    Returns:
        Updated application configuration
    """
    try:
        logger.info("Updating application configuration")
        
        # Convert DTO to entity
        config = AppConfig(
            from_language=config_dto.from_language,
            to_language=config_dto.to_language,
            ai_api_service=AIServiceConfig(
                api_service_provider=config_dto.ai_api_service.api_service_provider,
                api_key=config_dto.ai_api_service.api_key
            ),
            output_directory=config_dto.output_directory,
            model=config_dto.model,
            prompt_style=config_dto.prompt_style,
            enable_post_check=config_dto.enable_post_check
        )
        
        # Save to file in the background
        background_tasks.add_task(config.save_to_file, "config.json")
        
        logger.info("Application configuration updated")
        
        return config_dto
    except Exception as e:
        logger.error(f"Error updating application configuration: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating application configuration: {str(e)}"
        )


@router.get(
    "/webapp",
    response_model=WebAppConfigDTO,
    summary="Get web application configuration",
    description="Get the current web application configuration"
)
async def get_webapp_config(
    config: WebAppConfig = Depends(get_config)
) -> WebAppConfigDTO:
    """
    Get the current web application configuration.
    
    Args:
        config: Web application configuration
        
    Returns:
        Web application configuration
    """
    try:
        logger.info("Getting web application configuration")
        
        # Convert to DTO
        return WebAppConfigDTO(
            from_language=config.from_language,
            to_language=config.to_language,
            ai_api_service=AIServiceConfigDTO(
                api_service_provider=config.ai_api_service.api_service_provider,
                api_key=config.ai_api_service.api_key
            ),
            output_directory=str(config.output_directory) if config.output_directory else None,
            model=config.model,
            prompt_style=config.prompt_style,
            enable_post_check=config.enable_post_check,
            server_host=config.server_host,
            server_port=config.server_port,
            cors_origins=config.cors_origins,
            upload_directory=config.upload_directory,
            max_file_size_mb=config.max_file_size_mb
        )
    except Exception as e:
        logger.error(f"Error getting web application configuration: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting web application configuration: {str(e)}"
        )


@router.put(
    "/webapp",
    response_model=WebAppConfigDTO,
    summary="Update web application configuration",
    description="Update the web application configuration"
)
async def update_webapp_config(
    config_dto: WebAppConfigDTO,
    background_tasks: BackgroundTasks
) -> WebAppConfigDTO:
    """
    Update the web application configuration.
    
    Args:
        config_dto: Web application configuration DTO
        background_tasks: Background tasks
        
    Returns:
        Updated web application configuration
    """
    try:
        logger.info("Updating web application configuration")
        
        # Convert DTO to entity
        config = WebAppConfig(
            from_language=config_dto.from_language,
            to_language=config_dto.to_language,
            ai_api_service=AIServiceConfig(
                api_service_provider=config_dto.ai_api_service.api_service_provider,
                api_key=config_dto.ai_api_service.api_key
            ),
            output_directory=config_dto.output_directory,
            model=config_dto.model,
            prompt_style=config_dto.prompt_style,
            enable_post_check=config_dto.enable_post_check,
            server_host=config_dto.server_host,
            server_port=config_dto.server_port,
            cors_origins=config_dto.cors_origins,
            upload_directory=config_dto.upload_directory,
            max_file_size_mb=config_dto.max_file_size_mb
        )
        
        # Save to file in the background
        background_tasks.add_task(config.save_to_file, "config.json")
        
        logger.info("Web application configuration updated")
        
        return config_dto
    except Exception as e:
        logger.error(f"Error updating web application configuration: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating web application configuration: {str(e)}"
        )


@router.get(
    "/providers",
    response_model=AIProvidersDTO,
    summary="Get AI providers",
    description="Get the available AI providers"
)
async def get_ai_provider_registry(
    registry: AIProviderRegistry = Depends(get_ai_providers)
) -> AIProvidersDTO:
    """
    Get the available AI providers.
    
    Args:
        registry: AI provider registry
        
    Returns:
        AI providers
    """
    try:
        logger.info("Getting AI providers")
        
        # Convert to DTO
        providers_dto = {}
        for provider_name, provider in registry.providers.items():
            models_dto = {}
            for model_name, model in provider.models.items():
                models_dto[model_name] = AIModelDTO(
                    name=model.name,
                    max_tokens=model.max_tokens,
                    temperature=model.temperature,
                    aliases=model.aliases
                )
            
            providers_dto[provider_name] = AIProviderDTO(
                name=provider.name,
                api_endpoint=provider.api_endpoint,
                models=models_dto
            )
        
        return AIProvidersDTO(providers=providers_dto)
    except Exception as e:
        logger.error(f"Error getting AI providers: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting AI providers: {str(e)}"
        )


@router.put(
    "/providers",
    response_model=AIProvidersDTO,
    summary="Update AI providers",
    description="Update the available AI providers"
)
async def update_ai_provider_registry(
    providers_dto: AIProvidersDTO,
    background_tasks: BackgroundTasks
) -> AIProvidersDTO:
    """
    Update the available AI providers.
    
    Args:
        providers_dto: AI providers DTO
        background_tasks: Background tasks
        
    Returns:
        Updated AI providers
    """
    try:
        logger.info("Updating AI providers")
        
        # Convert DTO to entity
        registry = AIProviderRegistry()
        for provider_name, provider_dto in providers_dto.providers.items():
            provider = AIProvider(
                name=provider_name,
                api_endpoint=provider_dto.api_endpoint
            )
            
            for model_name, model_dto in provider_dto.models.items():
                model = AIModel(
                    name=model_name,
                    max_tokens=model_dto.max_tokens,
                    temperature=model_dto.temperature,
                    aliases=model_dto.aliases
                )
                provider.add_model(model)
            
            registry.add_provider(provider)
        
        # Save to file in the background
        background_tasks.add_task(registry.save_to_file, "aiprovider.json")
        
        logger.info("AI providers updated")
        
        return providers_dto
    except Exception as e:
        logger.error(f"Error updating AI providers: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating AI providers: {str(e)}"
        )


@router.get(
    "/prompts",
    response_model=PromptStylesDTO,
    summary="Get prompt styles",
    description="Get the available prompt styles"
)
async def get_prompt_registry(
    registry: PromptRegistry = Depends(get_prompt_styles)
) -> PromptStylesDTO:
    """
    Get the available prompt styles.
    
    Args:
        registry: Prompt registry
        
    Returns:
        Prompt styles
    """
    try:
        logger.info("Getting prompt styles")
        
        # Convert to DTO
        styles_dto = {}
        for style_name, style in registry.styles.items():
            styles_dto[style_name] = PromptTemplateDTO(
                system=style.template.system,
                user=style.template.user
            )
        
        return PromptStylesDTO(styles=styles_dto)
    except Exception as e:
        logger.error(f"Error getting prompt styles: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting prompt styles: {str(e)}"
        )


@router.put(
    "/prompts",
    response_model=PromptStylesDTO,
    summary="Update prompt styles",
    description="Update the available prompt styles"
)
async def update_prompt_registry(
    styles_dto: PromptStylesDTO,
    background_tasks: BackgroundTasks
) -> PromptStylesDTO:
    """
    Update the available prompt styles.
    
    Args:
        styles_dto: Prompt styles DTO
        background_tasks: Background tasks
        
    Returns:
        Updated prompt styles
    """
    try:
        logger.info("Updating prompt styles")
        
        # Convert DTO to entity
        registry = PromptRegistry()
        for style_name, template_dto in styles_dto.styles.items():
            template = PromptTemplate(
                system=template_dto.system,
                user=template_dto.user
            )
            style = PromptStyle(
                name=style_name,
                template=template
            )
            registry.add_style(style)
        
        # Save to file in the background
        background_tasks.add_task(registry.save_to_file, "prompts.json")
        
        logger.info("Prompt styles updated")
        
        return styles_dto
    except Exception as e:
        logger.error(f"Error updating prompt styles: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating prompt styles: {str(e)}"
        )