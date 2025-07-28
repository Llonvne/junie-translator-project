#!/usr/bin/env python3
"""
SRT翻译器演示脚本
展示如何使用新的分层架构
"""
import sys
import asyncio
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def demo_entities():
    """演示实体层使用"""
    print("🏗️ 演示实体层 (Entity Layer)")
    print("=" * 50)
    
    from entities import SrtFile, AIModel, PromptTemplate, AppConfig, PromptStyle
    from entities.ai_model import ModelConfig
    from entities.config import AIServiceConfig
    
    # 创建AI服务配置
    ai_service = AIServiceConfig(
        api_service_provider="openai",
        api_key="demo-key"
    )
    
    # 创建应用配置
    config = AppConfig(
        from_language="auto",
        to_language="中文",
        ai_api_service=ai_service,
        output_directory="./output",
        model="gpt-3.5-turbo",
        prompt_style=PromptStyle.SUBTITLE
    )
    
    print(f"📊 配置创建成功:")
    print(f"   源语言: {config.from_language}")
    print(f"   目标语言: {config.to_language}")
    print(f"   AI服务: {config.ai_api_service.api_service_provider}")
    print(f"   提示词风格: {config.prompt_style.value}")
    
    # 创建AI模型
    model_config = ModelConfig(max_tokens=1024, temperature=0.3)
    ai_model = AIModel(
        provider="openai",
        model_name="gpt-3.5-turbo",
        api_endpoint="https://api.openai.com/v1",
        config=model_config
    )
    
    print(f"🤖 AI模型创建成功: {ai_model.full_name}")
    
    # 创建提示词模板
    prompt_template = PromptTemplate(
        style=PromptStyle.SUBTITLE,
        system_prompt="You are a professional subtitle translator.",
        user_prompt_template="Translate to {target_language}: {text}"
    )
    
    print(f"📝 提示词模板创建成功: {prompt_template.style.value}")
    print()

async def demo_infra():
    """演示基础设施层使用"""
    print("🏢 演示基础设施层 (Infrastructure Layer)")
    print("=" * 50)
    
    try:
        from infra import InfrastructureManager
        
        # 创建基础设施管理器（使用mock配置避免依赖真实配置文件）
        infra = InfrastructureManager()
        
        # 获取系统信息
        info = infra.get_system_info()
        
        if 'error' not in info:
            print("📋 系统信息:")
            print(f"   可用AI提供商: {info['available_providers']}")
            print(f"   可用提示词风格: {info['available_prompt_styles']}")
        else:
            print(f"⚠️  获取系统信息时出现错误: {info['error']}")
            
    except Exception as e:
        print(f"⚠️  基础设施层演示需要配置文件: {e}")
    
    print()

async def demo_ai_layer():
    """演示AI层使用（模拟）"""
    print("🧠 演示AI层 (AI Layer)")
    print("=" * 50)
    
    from ai_layer.client import MockClient
    from ai_layer.translator import AITranslator
    from entities import AIModel, PromptTemplate, PromptStyle, SubtitleEntry
    from entities.ai_model import ModelConfig
    
    # 创建模拟AI客户端
    mock_client = MockClient(delay=0.1)
    
    # 创建AI模型
    model_config = ModelConfig(max_tokens=1024, temperature=0.3)
    ai_model = AIModel(
        provider="mock",
        model_name="mock",
        api_endpoint=None,
        config=model_config
    )
    
    # 创建提示词模板
    prompt_template = PromptTemplate(
        style=PromptStyle.SUBTITLE,
        system_prompt="You are a professional subtitle translator.",
        user_prompt_template="Translate to {target_language}: {text}"
    )
    
    # 创建翻译器
    translator = AITranslator(mock_client, ai_model, prompt_template)
    
    # 创建示例字幕条目
    subtitle_entry = SubtitleEntry(
        index=1,
        start_time="00:00:01,000",
        end_time="00:00:03,000",
        content=["Hello, world!", "This is a test."]
    )
    
    print(f"📽️ 原始字幕: {subtitle_entry.text}")
    
    # 翻译字幕条目
    translated_entry = await translator.translate_subtitle_entry(
        subtitle_entry, 
        "中文"
    )
    
    print(f"🌍 翻译后字幕: {translated_entry.text}")
    print()

def demo_webui_structure():
    """演示WebUI结构"""
    print("🌐 演示WebUI层 (WebUI Layer)")
    print("=" * 50)
    
    webui_path = Path(__file__).parent.parent / "webui"
    
    if webui_path.exists():
        print("📁 WebUI目录结构:")
        
        # 检查主要文件
        main_files = [
            "package.json",
            "vite.config.js",
            "index.html",
            "src/main.js",
            "src/App.vue",
            "src/router/index.js",
            "src/stores/app.js",
            "src/services/api.js"
        ]
        
        for file_path in main_files:
            full_path = webui_path / file_path
            if full_path.exists():
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path}")
        
        # 检查页面组件
        views_path = webui_path / "src" / "views"
        if views_path.exists():
            print(f"   📄 页面组件:")
            for vue_file in views_path.glob("*.vue"):
                print(f"      - {vue_file.name}")
    else:
        print("⚠️  WebUI目录不存在")
    
    print()

async def main():
    """主演示函数"""
    print("🎉 SRT翻译器新架构演示")
    print("=" * 80)
    print()
    
    # 演示各层
    await demo_entities()
    await demo_infra()
    await demo_ai_layer()
    demo_webui_structure()
    
    print("✨ 演示完成！新的分层架构包含:")
    print("   🏗️ 实体层 - 核心业务实体和数据模型")
    print("   🧠 AI层 - AI服务集成和翻译逻辑")
    print("   🌐 API层 - RESTful API接口")
    print("   🏢 基础设施层 - 配置管理和服务组装")
    print("   🎨 WebUI层 - Vue3前端界面")
    print()
    print("📖 查看 README_NEW.md 了解详细使用说明")

if __name__ == "__main__":
    asyncio.run(main())