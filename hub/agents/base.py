"""
Agent 基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from hub.tools.llm import BaseLLM
from hub.tools.memory import Memory
from hub.tools.registry import ToolRegistry


class BaseAgent(ABC):
    """Agent 基类"""
    
    name: str = "base"
    description: str = "基础 Agent"
    
    @abstractmethod
    async def execute(
        self, 
        content: str, 
        context: Dict,
        llm: BaseLLM,
        memory: Memory,
        tools: ToolRegistry
    ) -> str:
        """
        执行任务
        
        Args:
            content: 任务内容
            context: 上下文信息
            llm: LLM 实例
            memory: 记忆系统
            tools: 工具注册表
        
        Returns:
            str: 执行结果
        """
        pass
    
    async def think(self, prompt: str, llm: BaseLLM) -> str:
        """调用 LLM 进行思考"""
        messages = [
            {"role": "system", "content": "你是一个有帮助的AI助手。"},
            {"role": "user", "content": prompt}
        ]
        return await llm.chat(messages)
