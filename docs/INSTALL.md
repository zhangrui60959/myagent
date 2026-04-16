# MyAgent 源码安装指南

## 支持平台

| 平台 | 支持状态 | 安装脚本 |
|------|---------|---------|
| macOS | ✅ 完全支持 | `install.sh` |
| Linux | ✅ 完全支持 | `install.sh` |
| Windows | ✅ 完全支持 | `install.bat` |

---

## 快速安装

### macOS / Linux

```bash
# 方式一：直接运行脚本
git clone https://github.com/zhangrui60959/myagent.git
cd myagent
chmod +x install.sh
./install.sh

# 方式二：一行命令安装
curl -fsSL https://raw.githubusercontent.com/zhangrui60959/myagent/main/install.sh | bash
```

### Windows

**方式一：PowerShell**
```powershell
# 克隆仓库
git clone https://github.com/zhangrui60959/myagent.git
cd myagent

# 运行安装脚本
.\install.bat
```

**方式二：手动安装**
```powershell
# 1. 安装依赖
# - Git: https://git-scm.com/download/win
# - Python 3.10+: https://www.python.org/downloads/
# - Node.js 18+: https://nodejs.org/

# 2. 克隆仓库
git clone https://github.com/zhangrui60959/myagent.git
cd myagent

# 3. 安装 Python 依赖
cd hub
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
deactivate

# 4. 安装 Node 依赖
cd ..\client
npm install

# 5. 配置
copy .env.example .env
# 编辑 .env 填入 API Key
```

---

## 系统要求

| 组件 | 最低版本 | 说明 |
|------|---------|------|
| Git | 2.0+ | 代码版本管理 |
| Python | 3.10+ | Hub 服务运行 |
| Node.js | 18+ | Electron 客户端 |
| 内存 | 4GB+ | 推荐 8GB+ |

---

## 安装后配置

1. 编辑 `.env` 文件配置 API Key：

```bash
# Agent Hub 配置
HUB_HOST=localhost
HUB_PORT=8765

# LLM API 配置 (至少选择一个)
OPENAI_API_KEY=sk-xxx          # OpenAI
CLAUDE_API_KEY=sk-xxx          # Anthropic Claude
OLLAMA_BASE_URL=http://localhost:11434  # 本地 Ollama
```

2. 启动服务：

```bash
# macOS / Linux
./start-all.sh     # 全部启动
./start-hub.sh     # 仅 Hub
./start-client.sh  # 仅客户端

# Windows
start-all.bat      # 全部启动
start-hub.bat      # 仅 Hub
start-client.bat   # 仅客户端
```

---

## 故障排除

### Git 克隆失败
```bash
# 检查网络连接
ping github.com

# 使用代理 (如有)
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

### Python 虚拟环境问题
```powershell
# Windows PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Node 模块安装失败
```bash
# 清除缓存重试
npm cache clean --force
npm install
```

---

## Docker 安装 (可选)

```bash
# 使用 Docker Compose 一键启动
docker-compose up -d
```
