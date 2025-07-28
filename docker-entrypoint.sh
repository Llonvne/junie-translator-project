#!/bin/bash
set -e

# 等待配置文件
if [ ! -f "config.json" ]; then
    echo "⚠️  配置文件不存在，使用默认配置"
    cp config.json.example config.json
fi

# 根据命令启动不同服务
case "$1" in
    serve)
        echo "🚀 启动SRT翻译API服务..."
        cd /app && python -m src.main
        ;;
    webui)
        echo "🌐 启动WebUI开发服务器..."
        cd /app/webui && npm run dev -- --host 0.0.0.0
        ;;
    cli)
        shift
        echo "💻 运行CLI命令..."
        cd /app && python -m src.cli "$@"
        ;;
    check)
        echo "🔍 检查配置..."
        cd /app && python -m src.cli check-config
        ;;
    *)
        echo "使用方法: $0 {serve|webui|cli|check}"
        echo "  serve  - 启动API服务器"
        echo "  webui  - 启动WebUI开发服务器"
        echo "  cli    - 运行CLI命令"
        echo "  check  - 检查配置"
        exit 1
        ;;
esac