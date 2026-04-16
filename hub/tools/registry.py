"""
工具注册表 - 管理和执行各种工具
"""

import os
import asyncio
import subprocess
from typing import Dict, List, Callable, Any
from pathlib import Path


class BaseTool:
    """工具基类"""
    
    name: str = ""
    description: str = ""
    
    async def execute(self, **kwargs) -> Any:
        """执行工具"""
        raise NotImplementedError


class WebSearchTool(BaseTool):
    """网页搜索工具 (使用 DuckDuckGo)"""
    
    name = "web_search"
    description = "搜索互联网信息"
    
    async def execute(self, query: str, num_results: int = 5) -> str:
        try:
            # 使用 httpx 简单请求搜索 API
            import httpx
            response = httpx.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_redirect": 1}
            )
            data = response.json()
            
            results = []
            if data.get("RelatedTopics"):
                for item in data["RelatedTopics"][:num_results]:
                    if "Text" in item:
                        results.append(f"- {item['Text']}")
            
            if results:
                return "\n".join(results)
            return "未找到相关结果"
        except Exception as e:
            return f"搜索失败: {str(e)}"


class FileReadTool(BaseTool):
    """文件读取工具"""
    
    name = "file_read"
    description = "读取本地文件内容"
    
    async def execute(self, path: str, lines: int = 100) -> str:
        try:
            file_path = Path(path).expanduser()
            if not file_path.exists():
                return f"文件不存在: {path}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.readlines()[:lines]
            
            return "".join(content) + ("\n...(截断)" if len(content) >= lines else "")
        except Exception as e:
            return f"读取失败: {str(e)}"


class FileWriteTool(BaseTool):
    """文件写入工具"""
    
    name = "file_write"
    description = "写入内容到本地文件"
    
    async def execute(self, path: str, content: str, append: bool = False) -> str:
        try:
            file_path = Path(path).expanduser()
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            return f"文件已保存: {path}"
        except Exception as e:
            return f"写入失败: {str(e)}"


class ShellTool(BaseTool):
    """Shell 命令执行工具"""
    
    name = "shell"
    description = "执行 Shell 命令"
    
    async def execute(self, command: str, timeout: int = 30) -> str:
        try:
            result = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    result.communicate(), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                result.kill()
                return "命令执行超时"
            
            output = []
            if stdout:
                output.append(stdout.decode('utf-8', errors='ignore'))
            if stderr:
                output.append(f"STDERR:\n{stderr.decode('utf-8', errors='ignore')}")
            
            output.append(f"\n[Exit Code: {result.returncode}]")
            return "\n".join(output)
        except Exception as e:
            return f"执行失败: {str(e)}"


class ImageGenTool(BaseTool):
    """图像生成工具 (使用本地服务)"""
    
    name = "image_gen"
    description = "生成图片"
    
    async def execute(self, prompt: str, size: str = "1024x1024") -> str:
        # TODO: 接入实际图像生成服务
        return f"[模拟] 图像生成: {prompt}\n尺寸: {size}\n(请接入实际图像生成服务)"


class CalculatorTool(BaseTool):
    """计算器工具"""
    
    name = "calculator"
    description = "执行数学计算"
    
    async def execute(self, expression: str) -> str:
        try:
            # 安全计算
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expression):
                return "错误: 表达式包含非法字符"
            
            result = eval(expression)
            return f"{expression} = {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """注册工具"""
        self._tools[tool.name] = tool
    
    def register_default_tools(self):
        """注册默认工具"""
        default_tools = [
            WebSearchTool(),
            FileReadTool(),
            FileWriteTool(),
            ShellTool(),
            ImageGenTool(),
            CalculatorTool(),
        ]
        
        for tool in default_tools:
            self.register(tool)
    
    def get_tool(self, name: str) -> BaseTool:
        """获取工具"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[Dict]:
        """列出所有工具"""
        return [
            {"name": t.name, "description": t.description}
            for t in self._tools.values()
        ]
