"""
网页搜索 Agent
"""

from typing import Dict

from hub.agents.base import BaseAgent
from hub.tools.llm import BaseLLM
from hub.tools.memory import Memory
from hub.tools.registry import ToolRegistry


class WebSearchAgent(BaseAgent):
    """网页搜索 Agent"""
    
    name = "web_search"
    description = "搜索互联网信息并整理结果"
    
    SYSTEM_PROMPT = """你是一个专业的网络搜索助手。
你的职责是：
1. 理解用户的搜索需求
2. 使用搜索工具获取信息
3. 整理和总结搜索结果

请提供准确、简洁的回答。"""
    
    async def execute(
        self, 
        content: str, 
        context: Dict,
        llm: BaseLLM,
        memory: Memory,
        tools: ToolRegistry
    ) -> str:
        """执行搜索任务"""
        # 获取搜索工具
        search_tool = tools.get_tool("web_search")
        if not search_tool:
            return "错误: 搜索工具不可用"
        
        # 提取搜索关键词
        messages = [
            {"role": "system", "content": "你是一个搜索助手。请从用户问题中提取搜索关键词，只返回关键词，不要其他内容。"},
            {"role": "user", "content": content}
        ]
        
        query = await llm.chat(messages)
        
        # 执行搜索
        search_results = await search_tool.execute(query=query, num_results=5)
        
        # 整理结果
        summary_messages = [
            {"role": "system", "content": """你是一个信息整理助手。
请根据搜索结果，为用户整理出有用的信息。
格式要求：
1. 简要总结主要发现
2. 列出关键信息点
3. 如果有链接，提供参考来源"""},
            {"role": "user", "content": f"搜索关键词: {query}\n\n搜索结果:\n{search_results}\n\n请整理这些结果。"}
        ]
        
        summary = await llm.chat(summary_messages)
        
        return summary
