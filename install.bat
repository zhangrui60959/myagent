@echo off
chcp 65001 >nul
REM
REM MyAgent Windows 源码安装脚本
REM 使用方法: 从 GitHub 下载 install.bat 并运行，或直接克隆仓库后运行
REM

echo ========================================
echo        MyAgent Windows 安装脚本
echo ========================================
echo.

REM 检查 Git
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未检测到 Git，请先安装 Git: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM 检查 Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    where python3 >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] 未检测到 Python，请先安装 Python 3.10+: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    set PYTHON=python3
) else (
    set PYTHON=python
)

REM 检查 Node
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未检测到 Node.js，请先安装 Node.js 18+: https://nodejs.org/
    pause
    exit /b 1
)

echo [INFO] 环境检查通过
echo.

REM 克隆仓库
set REPO_URL=https://github.com/zhangrui60959/myagent.git
set INSTALL_DIR=%USERPROFILE%\MyAgent

if exist "%INSTALL_DIR%\." (
    echo [INFO] 检测到已安装，更新中...
    cd /d "%INSTALL_DIR%"
    git pull
) else (
    echo [INFO] 克隆仓库到 %INSTALL_DIR%
    git clone %REPO_URL% "%INSTALL_DIR%"
    cd /d "%INSTALL_DIR%"
)

echo.
echo [INFO] 安装 Python 依赖...
cd /d "%INSTALL_DIR%\hub"
%PYTHON% -m venv venv
call venv\Scripts\activate.bat
pip install --upgrade pip -q

echo [INFO] 尝试安装 (优先使用预编译包)...
pip install -r requirements.txt --only-binary :all: -q
if %errorlevel% neq 0 (
    echo [INFO] 预编译包不足，尝试完整安装 (可能需要编译)...
    pip install -r requirements.txt -q
)
deactivate

echo.
echo [INFO] 安装 Node.js 依赖...
cd /d "%INSTALL_DIR%\client"
call npm install

echo.
echo [INFO] 创建配置文件...
if not exist "%INSTALL_DIR%\.env" (
    copy "%INSTALL_DIR%\.env.example" "%INSTALL_DIR%\.env"
    echo [INFO] 请编辑 %INSTALL_DIR%\.env 填入 API Key
)

echo.
echo ========================================
echo        安装完成！
echo ========================================
echo.
echo 安装目录: %INSTALL_DIR%
echo.
echo 启动方式:
echo   cd %INSTALL_DIR%
echo   start-hub.bat      - 启动 Hub 服务
echo   start-client.bat   - 启动客户端
echo   start-all.bat      - 全部启动
echo.
pause
