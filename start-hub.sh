#!/bin/bash
# 启动 MyAgent Hub 服务

cd "$(dirname "$0")/hub"

if [ ! -d "venv" ]; then
    echo "[ERROR] 未检测到虚拟环境，请先运行 install.sh"
    exit 1
fi

echo "[INFO] 启动 Agent Hub 服务..."
source venv/bin/activate
python main.py
