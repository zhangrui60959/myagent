@echo off
chcp 65001 >nul
color 0A

echo ========================================
echo        MyAgent 一键安装脚本 (Windows)
echo ========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 建议以管理员身份运行此脚本
    echo.
)

:: 检测 Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] 正在安装 Python...
    winget install Python.Python.3.12 -e --silent --accept-package-agreements --accept-source-agreements
)

:: 检测 Node
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] 正在安装 Node.js...
    winget install OpenJS.NodeJS.LTS -e --silent --accept-package-agreements --accept-source-agreements
)

:: 创建安装目录
set INSTALL_DIR=%USERPROFILE%\MyAgent
echo [INFO] 安装目录: %INSTALL_DIR%
echo.

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\hub" mkdir "%INSTALL_DIR%\hub"
if not exist "%INSTALL_DIR%\client" mkdir "%INSTALL_DIR%\client"
if not exist "%INSTALL_DIR%\data" mkdir "%INSTALL_DIR%\data"
if not exist "%INSTALL_DIR%\logs" mkdir "%INSTALL_DIR%\logs"
if not exist "%INSTALL_DIR%\workspace" mkdir "%INSTALL_DIR%\workspace"

:: 复制文件
echo [INFO] 复制项目文件...
xcopy /E /Y "%~dp0hub\*" "%INSTALL_DIR%\hub\" >nul
xcopy /E /Y /exclude:"%~dp0install.bat" "%~dp0client\*" "%INSTALL_DIR%\client\" >nul

:: 安装 Python 依赖
echo [INFO] 安装 Python 依赖...
cd /d "%INSTALL_DIR%\hub"
python -m venv venv
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
deactivate

:: 安装 Node 依赖
echo [INFO] 安装 Node.js 依赖...
cd /d "%INSTALL_DIR%\client"
call npm install

:: 创建 .env 文件
echo [INFO] 创建配置文件...
(
echo # MyAgent 环境配置
echo LLM_PROVIDER=openai
echo OPENAI_API_KEY=your-api-key-here
echo OPENAI_MODEL=gpt-4o
echo HUB_HOST=localhost
echo HUB_PORT=8080
echo WS_PORT=8765
echo WORK_DIR=.\workspace
) > "%INSTALL_DIR%\.env"

:: 创建启动脚本
echo [INFO] 创建启动脚本...

:: Hub 启动
(
echo @echo off
echo cd /d "%%~dp0hub"
echo call venv\Scripts\activate.bat
echo python main.py
) > "%INSTALL_DIR%\start-hub.bat"

:: 客户端启动
(
echo @echo off
echo cd /d "%%~dp0client"
echo npm start
) > "%INSTALL_DIR%\start-client.bat"

:: 全部启动
(
echo @echo off
echo title MyAgent Hub
echo start cmd /k "%%~dp0start-hub.bat"
echo timeout /t 2 /nobreak >nul
echo title MyAgent Client
echo start cmd /k "%%~dp0start-client.bat"
) > "%INSTALL_DIR%\start-all.bat"

:: 创建桌面快捷方式
echo [INFO] 创建桌面快捷方式...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%USERPROFILE%\Desktop\MyAgent.lnk'); $s.TargetPath = '%INSTALL_DIR%\start-all.bat'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Description = 'MyAgent'; $s.Save()"

echo.
echo ========================================
echo [SUCCESS] 安装完成！
echo ========================================
echo.
echo 安装目录: %INSTALL_DIR%
echo.
echo 启动方式:
echo   1. 全部启动: 双击桌面 MyAgent 快捷方式
echo   2. 手动启动:
echo      - Hub:   运行 start-hub.bat
echo      - 客户端: 运行 start-client.bat
echo.
echo [提示] 请先编辑 .env 文件填入您的 API Key
echo.
pause
