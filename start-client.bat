@echo off
chcp 65001 >nul
REM 启动 MyAgent 客户端 (Windows)

cd /d "%~dp0client"

echo [INFO] 启动 Electron 客户端...
npm start
