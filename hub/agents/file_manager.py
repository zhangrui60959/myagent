"""
文件管理 Agent
"""

import os
from typing import Dict
from pathlib import Path

from hub.agents.base import BaseAgent
from hub.tools.llm import BaseLLM
from hub.tools.memory import Memory
from hub.tools.registry import ToolRegistry


class FileManagerAgent(BaseAgent):
    """文件管理 Agent"""
    
    name = "file_manager"
    description = "管理本地文件和目录"
    
    SYSTEM_PROMPT = """你是一个文件管理助手。
你可以帮助用户：
- 读取文件内容
- 创建和编辑文件
- 浏览目录结构
- 执行文件搜索

请注意：
1. 路径使用标准路径格式
2. 确认操作后再执行
3. 报告操作结果"""
    
    async def execute(
        self, 
        content: str, 
        context: Dict,
        llm: BaseLLM,
        memory: Memory,
        tools: ToolRegistry
    ) -> str:
        """执行文件管理任务"""
        # 分析用户意图
        messages = [
            {"role": "system", "content": """分析用户的文件操作请求，返回JSON格式的指令：
{
    "action": "read|write|list|search|delete",
    "path": "文件或目录路径",
    "content": "如果需要写入，提供内容"
}

只返回JSON，不要其他内容。"""},
            {"role": "user", "content": content}
        ]
        
        # 解析意图
        response = await llm.chat(messages)
        
        try:
            import json
            # 提取JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                intent = json.loads(response[start:end])
            else:
                return "无法理解您的请求"
        except:
            return f"无法解析指令: {response}"
        
        # 获取对应工具
        action = intent.get("action")
        path = intent.get("path", "./")
        
        # 默认工作目录
        work_dir = context.get("work_dir", os.getenv("WORK_DIR", "./workspace"))
        full_path = os.path.join(work_dir, path)
        
        if action == "read":
            tool = tools.get_tool("file_read")
            if tool:
                return await tool.execute(path=full_path, lines=200)
            return "读取工具不可用"
        
        elif action == "write":
            tool = tools.get_tool("file_write")
            content = intent.get("content", "")
            if tool:
                return await tool.execute(path=full_path, content=content)
            return "写入工具不可用"
        
        elif action == "list":
            try:
                items = list(Path(full_path).iterdir())
                result = [f"{'📁 ' if i.is_dir() else '📄 '}{i.name}" for i in items]
                return "\n".join(result) if result else "目录为空"
            except Exception as e:
                return f"无法列出目录: {e}"
        
        elif action == "search":
            try:
                import glob
                pattern = os.path.join(full_path, "**/*")
                files = glob.glob(pattern, recursive=True)
                return f"找到 {len(files)} 个文件:\n" + "\n".join(files[:50])
            except Exception as e:
                return f"搜索失败: {e}"
        
        return f"未知操作: {action}"
