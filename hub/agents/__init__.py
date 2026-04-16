"""
Agent 模块
"""

from hub.agents.base import BaseAgent
from hub.agents.general import GeneralAgent
from hub.agents.web_search import WebSearchAgent
from hub.agents.file_manager import FileManagerAgent
from hub.agents.code_assist import CodeAssistAgent


# Agent 注册表
_agents = {
    "general": GeneralAgent,
    "web_search": WebSearchAgent,
    "file_manager": FileManagerAgent,
    "code_assist": CodeAssistAgent,
}


def get_agent(name: str) -> BaseAgent:
    """获取 Agent 实例"""
    if name not in _agents:
        return GeneralAgent()  # 默认返回通用 Agent
    return _agents[name]()


def register_agent(name: str, agent_class):
    """注册新的 Agent"""
    _agents[name] = agent_class


__all__ = [
    "BaseAgent",
    "GeneralAgent",
    "WebSearchAgent",
    "FileManagerAgent",
    "CodeAssistAgent",
    "get_agent",
    "register_agent",
]
