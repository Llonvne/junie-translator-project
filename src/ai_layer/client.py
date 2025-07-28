"""
AI客户端 - 负责与AI服务提供商进行通信
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from entities import AIModel

logger = logging.getLogger(__name__)


class AIClient(ABC):
    """AI客户端抽象基类"""
    
    @abstractmethod
    async def translate_text(self, messages: List[Dict[str, str]], model: AIModel) -> str:
        """翻译文本"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查客户端是否可用"""
        pass


class OpenAIClient(AIClient):
    """OpenAI客户端"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"
        self._client = None
        
    def _get_client(self):
        """获取OpenAI客户端实例"""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI包未安装")
            
        if self._client is None:
            self._client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client
    
    async def translate_text(self, messages: List[Dict[str, str]], model: AIModel) -> str:
        """使用OpenAI API翻译文本"""
        try:
            client = self._get_client()
            
            response = await client.chat.completions.create(
                messages=messages,
                **model.get_request_params()
            )
            
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content.strip()
            else:
                raise ValueError("AI服务返回空响应")
                
        except Exception as e:
            logger.error(f"OpenAI翻译失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查OpenAI客户端是否可用"""
        return OPENAI_AVAILABLE and bool(self.api_key)


class MockClient(AIClient):
    """模拟客户端 - 用于测试"""
    
    def __init__(self, delay: float = 0.1):
        self.delay = delay
    
    async def translate_text(self, messages: List[Dict[str, str]], model: AIModel) -> str:
        """模拟翻译"""
        await asyncio.sleep(self.delay)
        
        # 提取要翻译的文本
        user_message = next((msg['content'] for msg in messages if msg['role'] == 'user'), '')
        
        # 简单的模拟翻译
        return f"[MOCK TRANSLATION] {user_message}"
    
    def is_available(self) -> bool:
        """模拟客户端总是可用"""
        return True


class ClientFactory:
    """AI客户端工厂"""
    
    @staticmethod
    def create_client(provider: str, api_key: Optional[str] = None, 
                     api_endpoint: Optional[str] = None) -> AIClient:
        """创建AI客户端"""
        if provider.lower() == 'openai':
            if not api_key:
                raise ValueError("OpenAI需要API密钥")
            return OpenAIClient(api_key, api_endpoint)
        
        elif provider.lower() == 'deepseek':
            if not api_key:
                raise ValueError("DeepSeek需要API密钥")
            return OpenAIClient(api_key, api_endpoint or "https://api.deepseek.com/v1")
        
        elif provider.lower() == 'mock':
            return MockClient()
        
        else:
            raise ValueError(f"不支持的AI服务提供商: {provider}")