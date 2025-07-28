#!/usr/bin/env python3
"""
SRT 翻译器命令行接口
"""
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import click

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from infra import InfrastructureManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@click.group()
@click.option('--config', '-c', help='配置文件路径', default='config.json')
@click.pass_context
def cli(ctx, config):
    """SRT字幕翻译器命令行工具"""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='输出文件路径')
@click.option('--concurrent', '-j', default=5, help='并发数量')
@click.pass_context
def translate_file(ctx, input_file, output, concurrent):
    """翻译SRT文件"""
    async def _translate():
        try:
            # 初始化基础设施
            infra = InfrastructureManager(config_path=ctx.obj['config_path'])
            
            # 验证配置
            if not infra.validate_configuration():
                click.echo("❌ 配置验证失败", err=True)
                sys.exit(1)
            
            # 创建翻译服务
            service = infra.create_translation_service()
            
            click.echo(f"🚀 开始翻译文件: {input_file}")
            click.echo(f"📊 并发数量: {concurrent}")
            
            # 执行翻译
            output_path = await service.translate_file(
                input_file, 
                output_path=output,
                max_concurrent=concurrent
            )
            
            click.echo(f"✅ 翻译完成: {output_path}")
            
        except Exception as e:
            click.echo(f"❌ 翻译失败: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_translate())


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--pattern', '-p', default='*.srt', help='文件匹配模式')
@click.option('--concurrent', '-j', default=5, help='并发数量')
@click.pass_context
def translate_dir(ctx, input_dir, pattern, concurrent):
    """翻译目录中的所有SRT文件"""
    async def _translate():
        try:
            # 初始化基础设施
            infra = InfrastructureManager(config_path=ctx.obj['config_path'])
            
            # 验证配置
            if not infra.validate_configuration():
                click.echo("❌ 配置验证失败", err=True)
                sys.exit(1)
            
            # 创建翻译服务
            service = infra.create_translation_service()
            
            click.echo(f"🚀 开始翻译目录: {input_dir}")
            click.echo(f"📁 文件模式: {pattern}")
            click.echo(f"📊 并发数量: {concurrent}")
            
            # 执行翻译
            output_paths = await service.translate_directory(
                input_dir,
                pattern=pattern,
                max_concurrent=concurrent
            )
            
            click.echo(f"✅ 翻译完成，共处理 {len(output_paths)} 个文件")
            for path in output_paths:
                click.echo(f"   📄 {path}")
            
        except Exception as e:
            click.echo(f"❌ 翻译失败: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_translate())


@cli.command()
@click.argument('text')
@click.pass_context
def translate_text(ctx, text):
    """翻译文本"""
    async def _translate():
        try:
            # 初始化基础设施
            infra = InfrastructureManager(config_path=ctx.obj['config_path'])
            
            # 验证配置
            if not infra.validate_configuration():
                click.echo("❌ 配置验证失败", err=True)
                sys.exit(1)
            
            # 创建翻译服务
            service = infra.create_translation_service()
            
            click.echo(f"🚀 翻译文本: {text}")
            
            # 执行翻译
            result = await service.test_translation(text)
            
            click.echo(f"✅ 翻译结果: {result}")
            
        except Exception as e:
            click.echo(f"❌ 翻译失败: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_translate())


@cli.command()
@click.pass_context
def check_config(ctx):
    """检查配置"""
    try:
        # 初始化基础设施
        infra = InfrastructureManager(config_path=ctx.obj['config_path'])
        
        # 获取系统信息
        info = infra.get_system_info()
        
        if 'error' in info:
            click.echo(f"❌ 配置错误: {info['error']}", err=True)
            sys.exit(1)
        
        click.echo("📋 系统配置信息:")
        click.echo("=" * 50)
        
        config = info['config']
        click.echo(f"源语言: {config['from_language']}")
        click.echo(f"目标语言: {config['to_language']}")
        click.echo(f"输出目录: {config['output_directory']}")
        click.echo(f"提示词风格: {config['prompt_style']}")
        
        model = info['model']
        click.echo(f"AI模型: {model['full_name']}")
        click.echo(f"API端点: {model['api_endpoint']}")
        
        click.echo(f"可用提供商: {', '.join(info['available_providers'])}")
        click.echo(f"可用提示词风格: {', '.join(info['available_prompt_styles'])}")
        
        # 验证配置
        if infra.validate_configuration():
            click.echo("✅ 配置验证通过")
        else:
            click.echo("❌ 配置验证失败")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ 检查配置失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--host', default='0.0.0.0', help='绑定地址')
@click.option('--port', default=8000, help='端口号')
@click.option('--reload', is_flag=True, help='启用热重载')
def serve(host, port, reload):
    """启动Web服务"""
    import uvicorn
    from main import create_app
    
    click.echo(f"🚀 启动Web服务 http://{host}:{port}")
    click.echo("📖 API文档: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
        reload_dirs=["src"] if reload else None
    )


if __name__ == '__main__':
    cli()