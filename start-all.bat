@echo off
chcp 65001 >nul
REM 一键启动 MyAgent 全部服务 (Windows)

echo [INFO] 启动 Agent Hub...
start cmd /k "cd /d %~dp0hub && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat && python main.py) else (python main.py))"

timeout /t 3 >nul

echo [INFO] 启动 Electron 客户端...
cd /d "%~dp0client"
call npm start

echo [INFO] 启动完成！
