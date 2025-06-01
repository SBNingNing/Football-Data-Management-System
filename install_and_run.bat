@echo off
echo 足球管理系统安装和启动脚本

echo.
echo ===== 安装前端依赖 =====
echo.

cd frontend
call npm install
cd ..

echo.
echo ===== 启动前端服务 =====
echo.

start cmd /k "cd frontend && npm run dev"

echo.
echo ===== 启动后端服务 =====
echo.

start cmd /k "python backend/run.py"

echo.
echo 前后端服务已启动：
echo 前端: http://localhost:3000
echo 后端: http://localhost:5000
echo.

pause
