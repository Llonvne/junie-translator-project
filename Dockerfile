# 多阶段构建Docker镜像

# 第一阶段：构建WebUI
FROM node:18-alpine AS webui-builder

WORKDIR /app/webui

# 复制package.json和安装依赖
COPY webui/package*.json ./
RUN npm ci --only=production

# 复制源代码并构建
COPY webui/ ./
RUN npm run build

# 第二阶段：Python应用
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制Python依赖文件
COPY requirements.txt pyproject.toml ./

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY src/ ./src/
COPY config.json.example ./config.json
COPY aiprovider.json ./
COPY prompts.json ./

# 复制构建好的WebUI
COPY --from=webui-builder /app/webui/dist ./webui/dist

# 创建输出目录
RUN mkdir -p ./output

# 暴露端口
EXPOSE 8000 3000

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动脚本
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["serve"]