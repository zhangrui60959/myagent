@echo off
chcp 65001 >nul
REM 启动 MyAgent Hub 服务 (Windows)

cd /d "%~dp0hub"

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] 未检测到虚拟环境，请先运行 install.bat
    pause
    exit /b 1
)

echo [INFO] 启动 Agent Hub 服务...
call venv\Scripts\activate.bat
python main.py
