"""
LLM 工厂 - 支持多种模型提供商
"""

import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

import openai
import anthropic
import httpx


class BaseLLM(ABC):
    """LLM 基类"""
    
    @abstractmethod
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """发送对话请求"""
        pass


class OpenAILLM(BaseLLM):
    """OpenAI GPT 系列"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    async def chat(self, messages: List[Dict], model: str = None, 
                   temperature: float = 0.7, **kwargs) -> str:
        model = model or self.default_model
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            **kwargs
        )
        
        return response.choices[0].message.content


class AnthropicLLM(BaseLLM):
    """Anthropic Claude 系列"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.default_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    
    async def chat(self, messages: List[Dict], model: str = None,
                   temperature: float = 0.7, **kwargs) -> str:
        model = model or self.default_model
        
        # 转换消息格式
        system_msg = ""
        filtered_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                filtered_messages.append(msg)
        
        response = self.client.messages.create(
            model=model,
            system=system_msg,
            messages=filtered_messages,
            temperature=temperature,
            **kwargs
        )
        
        return response.content[0].text


class OllamaLLM(BaseLLM):
    """Ollama 本地模型"""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def chat(self, messages: List[Dict], model: str = None,
                   temperature: float = 0.7, **kwargs) -> str:
        model = model or self.default_model
        
        # 转换消息格式
        ollama_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages if msg["role"] != "system"
        ]
        
        response = await self.client.post(
            f"{self.base_url}/api/chat",
            json={
                "model": model,
                "messages": ollama_messages,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
        )
        
        result = response.json()
        return result["message"]["content"]


class LLMFactory:
    """LLM 工厂类"""
    
    _providers = {
        "openai": OpenAILLM,
        "anthropic": AnthropicLLM,
        "ollama": OllamaLLM,
    }
    
    @classmethod
    def create(cls, provider: str = "openai") -> BaseLLM:
        """创建 LLM 实例"""
        provider = provider.lower()
        
        if provider not in cls._providers:
            raise ValueError(f"Unknown LLM provider: {provider}. "
                           f"Available: {list(cls._providers.keys())}")
        
        return cls._providers[provider]()
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """列出所有可用的提供商"""
        return list(cls._providers.keys())
