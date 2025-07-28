#!/usr/bin/env python3
"""
SRT 翻译器主入口
"""
import logging
import sys
import asyncio
from pathlib import Path

import uvicorn
from fastapi import FastAPI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('srt_translator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def create_app() -> FastAPI:
    """创建FastAPI应用"""
    from api_layer import create_app
    return create_app()

def main():
    """主函数"""
    logger.info("启动SRT翻译器服务")
    
    app = create_app()
    
    # 开发环境配置
    uvicorn.run(
        "main:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        log_level="info"
    )

if __name__ == "__main__":
    main()