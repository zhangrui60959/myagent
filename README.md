# MyAgent - 本地 AI Agent 一键部署应用

一个类似 WorkBuddy 的本地 AI Agent 办公助手，支持一键部署、多 Agent 协作、WebSocket 实时通信。

---

## 📁 项目结构

```
myagent/
├── README.md                 # 项目说明
├── LICENSE                   # MIT 许可证
├── .env.example              # 环境变量示例
├── docker-compose.yml        # Docker 部署配置
├── install.sh                # 一键安装脚本 (Linux/macOS)
├── install.bat               # 一键安装脚本 (Windows)
├── bin/
│   └── myagent               # CLI 启动脚本
├── hub/                      # Agent Hub (调度中心)
│   ├── main.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── web_search.py
│   │   ├── file_manager.py
│   │   ├── code_assist.py
│   │   └── general.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── llm.py
│   │   ├── memory.py
│   │   └── registry.py
│   └── requirements.txt
├── client/                   # Electron 客户端
│   ├── package.json
│   ├── main.js
│   ├── preload.js
│   ├── index.html
│   └── renderer.js
└── config/                   # 配置文件
    └── default.json
```

---

## 🚀 快速开始

### 一键安装 (Linux/macOS)

```bash
curl -fsSL https://raw.githubusercontent.com/your-repo/myagent/main/install.sh | bash
```

### 一键安装 (Windows)

```powershell
irm https://raw.githubusercontent.com/your-repo/myagent/main/install.bat | iex
```

### Docker 部署

```bash
git clone https://github.com/your-repo/myagent.git
cd myagent
cp .env.example .env
# 编辑 .env 填入 API Key
docker-compose up -d
```

---

## ⚙️ 环境配置

复制 `.env.example` 为 `.env` 并配置：

```env
# LLM 配置
LLM_PROVIDER=openai                    # openai / anthropic / ollama
OPENAI_API_KEY=sk-xxx                   # OpenAI API Key
OPENAI_MODEL=gpt-4o                     # 模型名称
ANTHROPIC_API_KEY=sk-ant-xxx           # Anthropic API Key (可选)

# 本地模型 (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# 服务配置
HUB_HOST=0.0.0.0
HUB_PORT=8080
WS_PORT=8765

# Redis (可选，用于分布式部署)
REDIS_URL=redis://localhost:6379

# 日志
LOG_LEVEL=INFO
```

---

## 📖 使用文档

详细文档请查看 [docs/](docs/)

- [安装指南](docs/installation.md)
- [架构设计](docs/architecture.md)
- [API 参考](docs/api.md)
- [工具开发指南](docs/tools.md)
- [Electron 客户端开发](docs/client.md)

---

## 🎯 核心功能

- ✅ **多 Agent 协作** - 支持多种专业 Agent 并行工作
- ✅ **WebSocket 实时通信** - 双向实时消息推送
- ✅ **记忆系统** - 跨会话持久化记忆
- ✅ **工具扩展** - 支持自定义工具插件
- ✅ **多平台集成** - 微信、飞书、钉钉 (开发中)
- ✅ **一键部署** - 脚本自动安装所有依赖

---

## 📜 License

MIT License
