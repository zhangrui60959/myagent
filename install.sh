#!/bin/bash
#
# MyAgent 一键安装脚本 (从 GitHub 源码安装)
# 使用方法: curl -fsSL https://raw.githubusercontent.com/[用户名]/myagent/main/install.sh | bash
#

set -e

# ============== 配置 ==============
REPO_URL="${REPO_URL:-}"
INSTALL_DIR="${HOME}/MyAgent"

# ============== 颜色 ==============
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============== 主流程 ==============
main() {
    echo "========================================"
    echo "       MyAgent 源码安装脚本"
    echo "========================================"
    echo ""

    # 1. 获取仓库地址
    if [ -z "$REPO_URL" ]; then
        read -p "请输入 GitHub 仓库地址: " REPO_URL
    fi

    if [ -z "$REPO_URL" ]; then
        log_error "未提供仓库地址"
        echo "使用方式: REPO_URL=https://github.com/用户名/myagent.git $0"
        exit 1
    fi

    log_info "克隆仓库: $REPO_URL"

    # 2. 克隆或更新
    if [ -d "$INSTALL_DIR/.git" ]; then
        log_info "更新现有安装..."
        cd "$INSTALL_DIR"
        git pull
    else
        log_info "克隆仓库..."
        rm -rf "$INSTALL_DIR"
        git clone "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi

    # 3. 检查环境
    if ! command -v python3 &> /dev/null; then
        log_error "需要 Python 3.10+，请先安装"
        exit 1
    fi

    if ! command -v node &> /dev/null; then
        log_error "需要 Node.js 18+，请先安装"
        exit 1
    fi

    # 4. 安装 Python 依赖
    log_info "安装 Python 依赖..."
    cd "$INSTALL_DIR/hub"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    deactivate

    # 5. 安装 Node 依赖
    log_info "安装 Node.js 依赖..."
    cd "$INSTALL_DIR/client"
    npm install -q

    # 6. 配置
    if [ ! -f "$INSTALL_DIR/.env" ]; then
        log_info "创建配置文件..."
        cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
        log_success "请编辑 $INSTALL_DIR/.env 填入 API Key"
    fi

    echo ""
    echo "========================================"
    log_success "安装完成！"
    echo "========================================"
    echo ""
    echo "📁 安装目录: $INSTALL_DIR"
    echo ""
    echo "启动方式:"
    echo "  cd $INSTALL_DIR"
    echo "  ./start-all.sh     # 全部启动"
    echo "  ./start-hub.sh     # 仅 Hub"
    echo "  ./start-client.sh  # 仅客户端"
    echo ""
}

main "$@"
