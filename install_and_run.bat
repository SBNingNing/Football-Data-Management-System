@echo off
echo 足球管理系统安装和启动脚本

REM 获取脚本所在目录
cd /d "%~dp0"

echo.
echo 当前目录: %cd%
echo.

echo.
echo ===== 检查前端目录 =====
if exist "frontend" (
    echo 前端目录存在
) else (
    echo 错误：frontend目录不存在！
    pause
    exit /b 1
)

echo.
echo ===== 安装前端依赖 =====
echo.

cd frontend
if exist "package.json" (
    echo 找到package.json，开始安装依赖...
    call npm install
    if errorlevel 1 (
        echo npm install 失败！
        pause
        exit /b 1
    )
) else (
    echo 错误：frontend目录中找不到package.json！
    pause
    exit /b 1
)
cd ..

echo.
echo ===== 启动前端服务 =====
echo.

start "前端服务" cmd /k "cd /d "%cd%\frontend" && npm run dev"

echo.
echo ===== 启动后端服务（调试模式） =====
echo.

if exist "backend\run.py" (
    REM 设置调试环境变量并启动后端服务，保持窗口打开显示日志
    start "后端服务-调试模式" cmd /k "cd /d "%cd%" && set FLASK_ENV=development && set FLASK_DEBUG=1 && python backend\run.py"
) else (
    echo 错误：找不到backend\run.py文件！
    pause
    exit /b 1
)

echo.
echo 前后端服务已启动（调试模式）：
echo 前端: http://localhost:3000
echo 后端: http://localhost:5000 （调试模式，日志会显示在后端窗口中）
echo.
echo 注意：后端窗口将显示所有调试日志信息
echo 按任意键退出...

pause
