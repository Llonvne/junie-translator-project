"""
FastAPI Application - Main entry point for the API Layer.

This module sets up the FastAPI application with middleware, routers, and dependencies.

FastAPI应用程序 - API层的主入口点。

该模块设置FastAPI应用程序，包括中间件、路由器和依赖项。
"""

import logging
from typing import Dict, Any, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from junie_translator_project.entity.config import WebAppConfig, AppConfig
from junie_translator_project.ai.translation_manager import TranslationManager

# Configure logging
logger = logging.getLogger(__name__)


def create_app(
    config: Optional[WebAppConfig] = None,
    translation_manager: Optional[TranslationManager] = None
) -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Args:
        config: Web application configuration (if None, default config will be used)
        translation_manager: Translation manager (if None, one will be created from config)
        
    Returns:
        Configured FastAPI application
    """
    # Create default config if not provided
    if config is None:
        config = WebAppConfig()
    
    # Create translation manager if not provided
    if translation_manager is None:
        translation_manager = TranslationManager(config=config)
    
    # Create FastAPI app
    app = FastAPI(
        title="Junie Translator API",
        description="API for translating text and SRT files using AI services",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add exception handlers
    @app.exception_handler(Exception)
    async def generic_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "message": str(exc)}
        )
    
    # Add dependencies
    @app.dependency
    def get_config() -> WebAppConfig:
        """Dependency for getting the application configuration."""
        return config
    
    @app.dependency
    def get_translation_manager() -> TranslationManager:
        """Dependency for getting the translation manager."""
        return translation_manager
    
    # Add startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        """Start the translation manager's background tasks."""
        await translation_manager.start()
        logger.info("API application started")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Stop the translation manager's background tasks."""
        await translation_manager.stop()
        logger.info("API application stopped")
    
    # Add health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check() -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            "status": "ok",
            "version": app.version,
            "cache_size": translation_manager.get_cache_size()
        }
    
    # Import and include routers
    # Note: We import here to avoid circular imports
    try:
        from junie_translator_project.api.routers import config_router, translation_router, srt_router
        
        # Include routers
        app.include_router(config_router.router, prefix="/api/config", tags=["Config"])
        app.include_router(translation_router.router, prefix="/api/translation", tags=["Translation"])
        app.include_router(srt_router.router, prefix="/api/srt", tags=["SRT"])
    except ImportError as e:
        logger.warning(f"Failed to import routers: {e}")
        logger.warning("API will be started without routers")
    
    return app


# Create a default app instance for direct import
app = create_app()


def run_app(host: str = "0.0.0.0", port: int = 8000, config: Optional[WebAppConfig] = None):
    """
    Run the FastAPI application with uvicorn.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        config: Web application configuration (if None, default config will be used)
    """
    import uvicorn
    
    # Create config if not provided
    if config is None:
        config = WebAppConfig(server_host=host, server_port=port)
    else:
        # Override config with provided host and port
        config.server_host = host
        config.server_port = port
    
    # Create app with config
    app = create_app(config=config)
    
    # Run app with uvicorn
    uvicorn.run(
        app,
        host=config.server_host,
        port=config.server_port,
        log_level="info"
    )


if __name__ == "__main__":
    # Run app directly if this module is executed
    run_app()