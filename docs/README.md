# MyAgent 技术文档

## 目录

- [快速开始](#快速开始)
- [架构设计](#架构设计)
- [API 参考](#api-参考)
- [工具开发](#工具开发)
- [Agent 开发](#agent-开发)
- [部署指南](#部署指南)

---

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- (可选) Redis 7+

### 安装

```bash
# 克隆项目
git clone https://github.com/your-repo/myagent.git
cd myagent

# 配置环境
cp .env.example .env
# 编辑 .env 填入 API Key

# 启动 Hub
cd hub
pip install -r requirements.txt
python main.py

# 启动客户端 (新终端)
cd client
npm install
npm start
```

### Docker 部署

```bash
docker-compose up -d
```

---

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端层                               │
│     Electron / Web / 移动端 / 微信 / 飞书 / 钉钉             │
└─────────────────────┬───────────────────────────────────────┘
                      │ WebSocket / HTTP
┌─────────────────────▼───────────────────────────────────────┐
│                      Agent Hub                              │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐   │
│  │   Router    │   Memory    │  Registry   │  Scheduler  │   │
│  └─────────────┴─────────────┴─────────────┴─────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼───────┬─────▼─────┬───────▼───────┐
│  GeneralAgent │ SearchAgent │ CodeAgent    │
│  FileAgent    │ ...        │ CustomAgents │
└───────┬───────┴─────┬─────┴───────┬───────┘
        │             │             │
┌───────▼─────────────▼─────────────▼───────┐
│                 工具层                      │
│  ┌─────────┬─────────┬─────────┬────────┐ │
│  │ LLM调用 │ 文件操作 │ 网络请求 │ Shell  │ │
│  └─────────┴─────────┴─────────┴────────┘ │
└────────────────────────────────────────────┘
```

### 核心组件

#### 1. Agent Hub (hub/main.py)

中央调度器，负责：
- HTTP API 服务
- WebSocket 实时通信
- 任务分发
- Agent 协调

#### 2. Agent (hub/agents/)

专业任务处理器：
- `GeneralAgent` - 通用对话
- `WebSearchAgent` - 网页搜索
- `FileManagerAgent` - 文件管理
- `CodeAssistAgent` - 代码助手

#### 3. Tools (hub/tools/)

可扩展工具集：
- `llm.py` - LLM 调用工厂
- `memory.py` - 记忆系统
- `registry.py` - 工具注册表

---

## API 参考

### HTTP API

#### POST /api/task
提交任务给 Agent

**请求体：**
```json
{
  "content": "帮我搜索最新的AI新闻",
  "agent_type": "web_search",
  "context": {}
}
```

**响应：**
```json
{
  "status": "success",
  "task_id": "uuid",
  "result": "搜索结果...",
  "agent": "web_search",
  "timestamp": "2024-01-01T00:00:00"
}
```

#### POST /api/chat
直接与 LLM 对话

**请求体：**
```json
{
  "messages": [
    {"role": "system", "content": "你是一个助手"},
    {"role": "user", "content": "你好"}
  ],
  "temperature": 0.7
}
```

#### GET /api/tools
列出所有可用工具

#### POST /api/tools/{tool_name}/execute
执行指定工具

#### GET /api/memory?session_id=xxx
获取会话记忆

### WebSocket API

**连接地址：** `ws://localhost:8765/ws/{client_id}`

**发送消息：**
```json
{
  "type": "task",
  "content": "帮我分析这个文件",
  "agent_type": "file_manager"
}
```

**接收消息：**
```json
{
  "type": "response",
  "status": "success",
  "result": "分析结果..."
}
```

---

## 工具开发

### 创建自定义工具

1. 继承 `BaseTool` 类
2. 实现 `execute` 方法
3. 注册到工具注册表

```python
from hub.tools.registry import BaseTool

class MyTool(BaseTool):
    name = "my_tool"
    description = "我的自定义工具"
    
    async def execute(self, param1: str, param2: int = 10) -> str:
        # 实现工具逻辑
        return f"结果: {param1}, {param2}"

# 注册
tool_registry.register(MyTool())
```

### 使用工具

```python
# 在 Agent 中调用
tool = tools.get_tool("my_tool")
result = await tool.execute(param1="hello", param2=20)
```

---

## Agent 开发

### 创建自定义 Agent

```python
from hub.agents.base import BaseAgent

class MyAgent(BaseAgent):
    name = "my_agent"
    description = "我的自定义Agent"
    
    async def execute(self, content, context, llm, memory, tools):
        # 1. 使用 LLM 思考
        thought = await self.think(f"分析: {content}", llm)
        
        # 2. 使用工具
        search_tool = tools.get_tool("web_search")
        results = await search_tool.execute(query=content)
        
        # 3. 整合结果
        return f"分析结果: {results}"
```

### 注册 Agent

```python
from hub.agents import register_agent

register_agent("my_agent", MyAgent)
```

---

## 部署指南

### 本地部署

```bash
# 开发模式
cd hub && python main.py

# 生产模式
uvicorn hub.main:app --host 0.0.0.0 --port 8080 --workers 4
```

### Docker 部署

```bash
# 构建镜像
docker build -t myagent-hub ./hub

# 运行容器
docker run -d \
  -p 8080:8080 \
  -p 8765:8765 \
  -e OPENAI_API_KEY=your-key \
  myagent-hub
```

### 一键部署

```bash
# Linux/macOS
curl -fsSL https://raw.githubusercontent.com/xxx/myagent/main/install.sh | bash

# Windows
irm https://raw.githubusercontent.com/xxx/myagent/main/install.bat | iex
```

---

## 配置说明

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LLM_PROVIDER` | openai | LLM 提供商 |
| `OPENAI_API_KEY` | - | OpenAI API Key |
| `OPENAI_MODEL` | gpt-4o | 模型名称 |
| `HUB_PORT` | 8080 | HTTP 端口 |
| `WS_PORT` | 8765 | WebSocket 端口 |

### 支持的 LLM

- `openai` - OpenAI GPT 系列
- `anthropic` - Anthropic Claude 系列
- `ollama` - Ollama 本地模型

---

## 常见问题

### Q: 连接失败？
检查 Hub 是否启动，确认端口未被占用。

### Q: LLM 调用失败？
确认 API Key 正确，网络可以访问对应服务。

### Q: 如何添加新工具？
参考 [工具开发](#工具开发) 部分。

### Q: 如何扩展 Agent？
参考 [Agent 开发](#agent-开发) 部分。
