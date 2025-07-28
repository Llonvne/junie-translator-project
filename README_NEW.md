# SRT 字幕翻译器 2.0

基于AI的智能SRT字幕翻译工具，采用现代分层架构设计，提供完整的Web界面和API服务。

## 🏗️ 项目架构

本项目采用分层架构设计，包含以下几个核心层次：

### 实体层 (Entity Layer) - `src/entities/`
包含核心业务实体，定义数据模型和业务规则：
- **SRT文件和字幕条目** (`srt.py`) - SRT文件解析和操作
- **AI模型配置** (`ai_model.py`) - AI服务和模型配置管理
- **提示词模板** (`prompt.py`) - 翻译提示词的管理
- **应用配置** (`config.py`) - 系统配置实体

### AI层 (AI Layer) - `src/ai_layer/`
负责组装SRT与提示词并实际请求AI服务：
- **AI客户端** (`client.py`) - 与各种AI服务提供商通信
- **翻译器** (`translator.py`) - 协调SRT、提示词和AI服务
- **翻译服务** (`service.py`) - 高级翻译服务接口

### API层 (API Layer) - `src/api_layer/`
通过网络开放RESTful API接口：
- **FastAPI应用** (`app.py`) - Web应用创建和配置
- **路由定义** (`routes.py`) - API端点实现
- **数据模型** (`models.py`) - API请求/响应模型
- **依赖注入** (`dependencies.py`) - 服务依赖管理

### 基础设施层 (Infrastructure Layer) - `src/infra/`
负责组装AI客户端、解析配置、建立各层服务：
- **配置加载器** (`config_loader.py`) - 加载和验证配置
- **提示词加载器** (`prompt_loader.py`) - 管理提示词模板
- **模型加载器** (`model_loader.py`) - 加载AI模型配置
- **基础设施管理器** (`manager.py`) - 统一管理所有基础设施组件

### WebUI层 - `webui/`
完全独立的前端界面，使用Vite+Vue3构建：
- **Vue3组件** - 现代化的用户界面
- **Element Plus** - 美观的UI组件库
- **Pinia状态管理** - 响应式状态管理
- **API服务集成** - 与后端API通信

## 🚀 快速开始

### 方式一：使用Docker Compose（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd srt-translator
```

2. **配置环境**
```bash
# 复制配置文件
cp config.json.example config.json

# 编辑配置，设置你的AI服务API密钥
nano config.json
```

3. **启动服务**
```bash
# 开发模式（包含WebUI开发服务器）
docker-compose --profile dev up -d

# 生产模式（使用Nginx代理）
docker-compose --profile prod up -d
```

4. **访问服务**
- API文档: http://localhost:8000/docs
- Web界面: http://localhost:3000 (开发模式) 或 http://localhost (生产模式)

### 方式二：本地开发

1. **安装Python依赖**
```bash
pip install -r requirements.txt
```

2. **启动API服务**
```bash
cd src
python main.py
```

3. **启动WebUI（另一个终端）**
```bash
cd webui
npm install
npm run dev
```

### 方式三：命令行工具

```bash
# 安装
pip install -e .

# 翻译单个文件
srt-translate translate-file sample.srt

# 翻译目录中所有SRT文件
srt-translate translate-dir ./videos/

# 翻译文本
srt-translate translate-text "Hello, world!"

# 检查配置
srt-translate check-config

# 启动Web服务
srt-translate serve
```

## 📋 功能特性

### 🎯 核心功能
- **SRT文件翻译** - 批量翻译字幕文件
- **实时文本翻译** - 快速翻译文本片段
- **多种AI服务支持** - OpenAI、DeepSeek等
- **提示词风格** - 字幕、正式、技术、日常等多种风格
- **并发翻译** - 可配置的并发数量提升效率

### 🌐 Web界面特性
- **现代化UI** - 基于Vue3和Element Plus
- **响应式设计** - 适配桌面和移动设备
- **拖拽上传** - 便捷的文件上传体验
- **进度显示** - 实时翻译进度反馈
- **历史记录** - 翻译历史和文件管理
- **主题切换** - 明暗主题支持

### 🔧 技术特性
- **分层架构** - 清晰的代码组织和职责分离
- **异步处理** - 高性能异步I/O
- **容器化部署** - Docker和Docker Compose支持
- **API优先** - RESTful API设计
- **配置驱动** - 灵活的配置管理
- **类型安全** - Python类型注解和Pydantic验证

## 🛠️ 配置说明

### config.json
```json
{
  "from-language": "auto",
  "to-language": "中文",
  "ai-api-service": {
    "api-service-provider": "openai",
    "api-key": "your-api-key-here"
  },
  "output-directory": "./output",
  "model": "gpt-3.5-turbo",
  "prompt-style": "subtitle"
}
```

### 支持的AI服务提供商
- **OpenAI**: GPT-3.5-turbo, GPT-4
- **DeepSeek**: deepseek-chat, deepseek-reasoner
- **Mock**: 测试用模拟服务

### 提示词风格
- **default**: 通用翻译
- **subtitle**: 字幕翻译专用（简洁）
- **formal**: 正式文档翻译
- **casual**: 日常对话翻译
- **technical**: 技术文档翻译
- **chinese**: 中文提示词

## 📁 项目结构

```
srt-translator/
├── src/                        # Python后端源码
│   ├── entities/               # 实体层
│   ├── ai_layer/              # AI层
│   ├── api_layer/             # API层
│   ├── infra/                 # 基础设施层
│   ├── main.py               # 应用入口
│   └── cli.py                # 命令行工具
├── webui/                     # Vue3前端源码
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   ├── stores/           # 状态管理
│   │   └── services/         # API服务
│   ├── package.json
│   └── vite.config.js
├── config.json.example       # 配置文件示例
├── aiprovider.json           # AI提供商配置
├── prompts.json             # 提示词配置
├── requirements.txt         # Python依赖
├── docker-compose.yml       # Docker Compose配置
├── Dockerfile              # Docker镜像构建
└── README.md              # 项目说明
```

## 🔀 API接口

### 核心端点
- `GET /` - 服务信息
- `GET /health` - 健康检查
- `GET /config` - 获取配置
- `POST /translate/text` - 翻译文本
- `POST /translate/file` - 翻译文件
- `GET /download/{filename}` - 下载文件
- `GET /files` - 列出输出文件

### API文档
启动服务后访问 http://localhost:8000/docs 查看完整的API文档。

## 🤝 贡献指南

1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [OpenAI](https://openai.com/) - AI服务支持
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - Vue 3组件库

---

如果这个项目对你有帮助，请给个⭐星标支持！