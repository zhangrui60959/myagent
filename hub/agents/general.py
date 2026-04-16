"""
通用 Agent
"""

from typing import Dict

from hub.agents.base import BaseAgent
from hub.tools.llm import BaseLLM
from hub.tools.memory import Memory
from hub.tools.registry import ToolRegistry


class GeneralAgent(BaseAgent):
    """通用 Agent - 处理日常任务"""
    
    name = "general"
    description = "通用助手，处理日常问答和任务"
    
    SYSTEM_PROMPT = """你是一个智能助手，可以帮助用户完成各种任务。
你可以：
- 回答问题和提供信息
- 帮助分析和解决问题
- 生成文本内容
- 进行创意写作

请用简洁、专业的方式回复。"""
    
    async def execute(
        self, 
        content: str, 
        context: Dict,
        llm: BaseLLM,
        memory: Memory,
        tools: ToolRegistry
    ) -> str:
        """执行通用任务"""
        # 构建消息
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]
        
        # 添加上下文记忆
        session_id = context.get("session_id", "default")
        history = await memory.get_history(session_id, limit=10)
        
        for msg in reversed(history[-6:]):  # 最近3轮对话
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        messages.append({"role": "user", "content": content})
        
        # 调用 LLM
        response = await llm.chat(messages)
        
        return response
