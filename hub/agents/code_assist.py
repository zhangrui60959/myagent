"""
代码助手 Agent
"""

import subprocess
from typing import Dict

from hub.agents.base import BaseAgent
from hub.tools.llm import BaseLLM
from hub.tools.memory import Memory
from hub.tools.registry import ToolRegistry


class CodeAssistAgent(BaseAgent):
    """代码助手 Agent"""
    
    name = "code_assist"
    description = "帮助编写、调试和优化代码"
    
    SYSTEM_PROMPT = """你是一个专业的编程助手。
你可以帮助用户：
- 编写和修改代码
- 调试和修复bug
- 代码优化和重构
- 解释代码逻辑
- 编写测试用例

请提供清晰、可执行的代码解决方案。"""
    
    async def execute(
        self, 
        content: str, 
        context: Dict,
        llm: BaseLLM,
        memory: Memory,
        tools: ToolRegistry
    ) -> str:
        """执行代码任务"""
        # 检测是否需要执行代码
        need_execute = any(kw in content.lower() for kw in ["运行", "执行", "run", "execute"])
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": content}
        ]
        
        if need_execute:
            # 添加执行上下文
            messages[0]["content"] += "\n\n如果需要执行代码，请在回复末尾添加执行结果。"
        
        response = await llm.chat(messages)
        
        # 检查是否需要执行
        if "```" in response or need_execute:
            shell_tool = tools.get_tool("shell")
            if shell_tool:
                # 尝试提取并执行代码块
                import re
                code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response, re.DOTALL)
                
                for code in code_blocks:
                    if any(lang in code for lang in ["python", "javascript", "bash", "sh"]):
                        lang = "python" if "python" in code else "bash"
                        cmd = f"python3 -c \"{code}\"" if lang == "python" else code
                        
                        result = await shell_tool.execute(command=cmd, timeout=10)
                        response += f"\n\n--- 执行结果 ---\n{result}"
                        break
        
        return response
