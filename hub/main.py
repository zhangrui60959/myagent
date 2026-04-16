"""
MyAgent Hub - 主入口

FastAPI 应用，提供 HTTP API 和 WebSocket 服务。
"""

import os
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from hub.tools.llm import LLMFactory
from hub.tools.memory import Memory
from hub.tools.registry import ToolRegistry
from hub.agents import get_agent

# 加载环境变量
load_dotenv()

# ============== 配置 ==============
HOST = os.getenv("HUB_HOST", "0.0.0.0")
PORT = int(os.getenv("HUB_PORT", "8080"))
WS_PORT = int(os.getenv("WS_PORT", "8765"))

# ============== 全局状态 ==============
# WebSocket 连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"[Hub] 客户端 {client_id} 已连接 (总计: {len(self.active_connections)})")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"[Hub] 客户端 {client_id} 已断开 (剩余: {len(self.active_connections)})")

    async def send(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()

# 初始化组件
llm = None
memory = None
tool_registry = None

# ============== 生命周期 ==============
@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm, memory, tool_registry
    
    print("=" * 60)
    print("  MyAgent Hub 启动中...")
    print("=" * 60)
    
    # 初始化 LLM
    provider = os.getenv("LLM_PROVIDER", "openai")
    llm = LLMFactory.create(provider)
    print(f"[Hub] LLM 提供商: {provider}")
    
    # 初始化记忆系统
    memory = Memory()
    await memory.init()
    print("[Hub] 记忆系统已初始化")
    
    # 初始化工具注册表
    tool_registry = ToolRegistry()
    tool_registry.register_default_tools()
    print(f"[Hub] 已注册 {len(tool_registry.list_tools())} 个工具")
    
    print(f"[Hub] HTTP 服务: http://{HOST}:{PORT}")
    print(f"[Hub] WebSocket: ws://{HOST}:{WS_PORT}")
    print("=" * 60)
    
    yield
    
    # 清理
    print("[Hub] 正在关闭...")
    await memory.close()

# ============== FastAPI 应用 ==============
app = FastAPI(
    title="MyAgent Hub",
    description="本地 AI Agent 调度中心",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== 请求模型 ==============
class TaskRequest(BaseModel):
    content: str
    agent_type: str = "general"
    context: Optional[dict] = None
    stream: bool = False

class ChatRequest(BaseModel):
    messages: list
    model: Optional[str] = None
    temperature: float = 0.7

# ============== HTTP API ==============

@app.get("/")
async def root():
    return {
        "name": "MyAgent Hub",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "api": "/api/task",
            "chat": "/api/chat",
            "tools": "/api/tools",
            "memory": "/api/memory",
            "websocket": f"ws://localhost:{WS_PORT}/ws"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/task")
async def submit_task(req: TaskRequest):
    """提交任务给 Agent 处理"""
    try:
        agent = get_agent(req.agent_type)
        result = await agent.execute(
            content=req.content,
            context=req.context or {},
            llm=llm,
            memory=memory,
            tools=tool_registry
        )
        
        return {
            "status": "success",
            "task_id": str(uuid.uuid4()),
            "result": result,
            "agent": req.agent_type,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """直接与 LLM 对话"""
    try:
        response = await llm.chat(
            messages=req.messages,
            model=req.model,
            temperature=req.temperature
        )
        return {"status": "success", "response": response}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )

@app.get("/api/tools")
async def list_tools():
    """列出所有可用工具"""
    return {
        "status": "success",
        "tools": tool_registry.list_tools()
    }

@app.post("/api/tools/{tool_name}/execute")
async def execute_tool(tool_name: str, params: dict):
    """执行指定工具"""
    try:
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        result = await tool.execute(**params)
        return {"status": "success", "result": result}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )

@app.get("/api/memory")
async def get_memory(session_id: str = "default"):
    """获取会话记忆"""
    try:
        history = await memory.get_history(session_id, limit=50)
        return {"status": "success", "history": history}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )

@app.delete("/api/memory/{session_id}")
async def clear_memory(session_id: str):
    """清除会话记忆"""
    try:
        await memory.clear(session_id)
        return {"status": "success", "message": f"Session {session_id} cleared"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )

# ============== WebSocket API ==============

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket 实时通信"""
    await manager.connect(client_id, websocket)
    
    # 发送欢迎消息
    await manager.send(client_id, {
        "type": "connected",
        "client_id": client_id,
        "message": "已连接到 MyAgent Hub",
        "timestamp": datetime.now().isoformat()
    })
    
    session_id = client_id  # 使用 client_id 作为 session_id
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await manager.send(client_id, {
                    "type": "error",
                    "error": "Invalid JSON format"
                })
                continue
            
            # 处理消息
            await handle_ws_message(client_id, session_id, message)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"[Hub] WebSocket 错误: {e}")
        manager.disconnect(client_id)

async def handle_ws_message(client_id: str, session_id: str, message: dict):
    """处理 WebSocket 消息"""
    msg_type = message.get("type")
    content = message.get("content", "")
    msg_id = message.get("id", str(uuid.uuid4()))
    
    # 保存用户消息到记忆
    await memory.add(session_id, "user", content)
    
    if msg_type == "task":
        # 任务模式
        agent_type = message.get("agent_type", "general")
        
        # 发送处理中状态
        await manager.send(client_id, {
            "type": "status",
            "status": "processing",
            "message": f"正在调用 {agent_type} Agent..."
        })
        
        try:
            agent = get_agent(agent_type)
            result = await agent.execute(
                content=content,
                context={"session_id": session_id},
                llm=llm,
                memory=memory,
                tools=tool_registry
            )
            
            # 保存助手回复到记忆
            await memory.add(session_id, "assistant", result)
            
            await manager.send(client_id, {
                "type": "response",
                "id": msg_id,
                "status": "success",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            await manager.send(client_id, {
                "type": "error",
                "id": msg_id,
                "error": str(e)
            })
    
    elif msg_type == "chat":
        # 对话模式
        try:
            # 获取历史消息
            history = await memory.get_history(session_id, limit=20)
            
            # 构建消息列表
            messages = [
                {"role": "system", "content": "你是一个有帮助的AI助手。"}
            ]
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": content})
            
            # 调用 LLM
            response = await llm.chat(messages)
            
            # 保存对话
            await memory.add(session_id, "user", content)
            await memory.add(session_id, "assistant", response)
            
            await manager.send(client_id, {
                "type": "response",
                "id": msg_id,
                "status": "success",
                "result": response,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            await manager.send(client_id, {
                "type": "error",
                "id": msg_id,
                "error": str(e)
            })
    
    elif msg_type == "ping":
        await manager.send(client_id, {
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        })
    
    else:
        await manager.send(client_id, {
            "type": "error",
            "error": f"Unknown message type: {msg_type}"
        })

# ============== 启动 ==============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, ws="wsproto")
