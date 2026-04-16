#!/bin/bash
# 启动 MyAgent 客户端

cd "$(dirname "$0")/client"

echo "[INFO] 启动 Electron 客户端..."
npm start
