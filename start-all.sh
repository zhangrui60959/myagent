#!/bin/bash
# 一键启动 MyAgent 全部服务

SCRIPT_DIR="$(dirname "$0")"

echo "[INFO] 启动 Agent Hub..."
"$SCRIPT_DIR/start-hub.sh" &
HUB_PID=$!

sleep 2

echo "[INFO] 启动 Electron 客户端..."
cd "$SCRIPT_DIR/client" && npm start

# 清理
trap "kill $HUB_PID 2>/dev/null" EXIT
