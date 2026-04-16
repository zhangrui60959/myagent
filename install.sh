#!/bin/bash
#
# MyAgent 一键安装脚本 (Linux/macOS)
# 使用方法: curl -fsSL https://raw.githubusercontent.com/xxx/myagent/main/install.sh | bash
#

set -e

# ============== 配置 ==============
REPO_URL="https://github.com/your-repo/myagent.git"
INSTALL_DIR="${HOME}/MyAgent"
VERSION="1.0.0"

# ============== 颜色 ==============
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============== 函数 ==============
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============== 检测系统 ==============
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# ============== 检测依赖 ==============
check_command() {
    command -v "$1" &> /dev/null
}

# ============== 安装系统依赖 ==============
install_system_deps() {
    local os=$(detect_os)
    
    log_info "检测操作系统: $os"
    
    if [ "$os" == "macos" ]; then
        install_macos_deps
    elif [ "$os" == "linux" ]; then
        install_linux_deps
    else
        log_warn "不支持的操作系统，部分功能可能无法使用"
    fi
}

install_macos_deps() {
    log_info "安装 macOS 依赖..."
    
    # 检查 Homebrew
    if ! check_command brew; then
        log_info "安装 Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # 安装依赖
    if ! check_command python3; then
        log_info "安装 Python..."
        brew install python@3.12
    fi
    
    if ! check_command node; then
        log_info "安装 Node.js..."
        brew install node
    fi
    
    log_success "macOS 依赖安装完成"
}

install_linux_deps() {
    log_info "安装 Linux 依赖..."
    
    if check_command apt-get; then
        sudo apt-get update
        sudo apt-get install -y python3.12 python3-pip nodejs npm
    elif check_command yum; then
        sudo yum install -y python3 python3-pip nodejs npm
    elif check_command pacman; then
        sudo pacman -S python python-pip nodejs npm --noconfirm
    fi
    
    log_success "Linux 依赖安装完成"
}

# ============== 创建目录结构 ==============
create_dirs() {
    log_info "创建目录结构..."
    
    mkdir -p "${INSTALL_DIR}"
    mkdir -p "${INSTALL_DIR}/hub"
    mkdir -p "${INSTALL_DIR}/client"
    mkdir -p "${INSTALL_DIR}/data"
    mkdir -p "${INSTALL_DIR}/logs"
    mkdir -p "${INSTALL_DIR}/workspace"
    mkdir -p "${INSTALL_DIR}/config"
    
    log_success "目录创建完成"
}

# ============== 安装 Python 依赖 ==============
install_python_deps() {
    log_info "安装 Python 依赖..."
    
    cd "${INSTALL_DIR}/hub"
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # 激活虚拟环境并安装
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    deactivate
    
    log_success "Python 依赖安装完成"
}

# ============== 安装 Node 依赖 ==============
install_node_deps() {
    log_info "安装 Node.js 依赖..."
    
    cd "${INSTALL_DIR}/client"
    npm install
    
    log_success "Node.js 依赖安装完成"
}

# ============== 配置环境变量 ==============
setup_env() {
    log_info "配置环境变量..."
    
    cat > "${INSTALL_DIR}/.env" << 'EOF'
# MyAgent 环境配置
# 请填入您的 API Key

# LLM 配置
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o

# 服务端口
HUB_HOST=0.0.0.0
HUB_PORT=8080
WS_PORT=8765

# 工作目录
WORK_DIR=./workspace

# 日志
LOG_LEVEL=INFO
EOF
    
    log_success "环境配置文件已创建: ${INSTALL_DIR}/.env"
    log_warn "请编辑 .env 文件填入您的 API Key"
}

# ============== 创建启动脚本 ==============
create_scripts() {
    log_info "创建启动脚本..."
    
    # Hub 启动脚本
    cat > "${INSTALL_DIR}/start-hub.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/hub"
source venv/bin/activate
python main.py
EOF
    chmod +x "${INSTALL_DIR}/start-hub.sh"
    
    # 客户端启动脚本
    cat > "${INSTALL_DIR}/start-client.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/client"
npm start
EOF
    chmod +x "${INSTALL_DIR}/start-client.sh"
    
    # 全部启动脚本
    cat > "${INSTALL_DIR}/start-all.sh" << 'EOF'
#!/bin/bash
echo "启动 MyAgent Hub..."
osascript -e 'tell app "Terminal" to do script "cd \"'"$(pwd)"'/hub\" && source venv/bin/activate && python main.py"' 2>/dev/null || bash start-hub.sh &

sleep 2

echo "启动 MyAgent 客户端..."
bash start-client.sh
EOF
    chmod +x "${INSTALL_DIR}/start-all.sh"
    
    log_success "启动脚本创建完成"
}

# ============== 创建桌面快捷方式 ==============
create_desktop() {
    log_info "创建桌面快捷方式..."
    
    # macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        cat > "${HOME}/Desktop/MyAgent.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/../MyAgent"
./start-all.sh
EOF
        chmod +x "${HOME}/Desktop/MyAgent.command"
    fi
    
    log_success "桌面快捷方式创建完成"
}

# ============== 主流程 ==============
main() {
    echo "========================================"
    echo "       MyAgent 一键安装脚本"
    echo "========================================"
    echo ""
    
    log_info "开始安装 MyAgent v${VERSION}..."
    echo ""
    
    # 1. 检测系统
    local os=$(detect_os)
    if [ "$os" == "unknown" ]; then
        log_warn "无法检测操作系统，将尝试继续安装..."
    fi
    
    # 2. 安装系统依赖
    install_system_deps
    
    # 3. 创建目录
    create_dirs
    
    # 4. 安装 Python 依赖
    install_python_deps
    
    # 5. 安装 Node 依赖
    install_node_deps
    
    # 6. 配置环境
    setup_env
    
    # 7. 创建脚本
    create_scripts
    
    # 8. 创建桌面快捷方式
    create_desktop
    
    echo ""
    echo "========================================"
    log_success "安装完成！"
    echo "========================================"
    echo ""
    echo "📁 安装目录: ${INSTALL_DIR}"
    echo ""
    echo "启动方式:"
    echo "  1. 全部启动: cd ${INSTALL_DIR} && ./start-all.sh"
    echo "  2. 分别启动:"
    echo "     - Hub:   cd ${INSTALL_DIR} && ./start-hub.sh"
    echo "     - 客户端: cd ${INSTALL_DIR} && ./start-client.sh"
    echo ""
    echo "⚠️  首次使用请编辑 ${INSTALL_DIR}/.env 填入 API Key"
    echo ""
}

# 执行
main "$@"
