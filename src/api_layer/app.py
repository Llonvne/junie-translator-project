"""
FastAPI 应用创建
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .routes import register_routes

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="SRT翻译API",
        description="AI驱动的SRT字幕文件翻译服务",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 在生产环境中应该设置具体的域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 添加GZip压缩中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 注册路由
    register_routes(app)

    @app.on_event("startup")
    async def startup_event():
        logger.info("SRT翻译API服务启动")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("SRT翻译API服务关闭")

    return app