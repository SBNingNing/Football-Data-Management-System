#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time
from pathlib import Path

def print_section(title):
    """打印分节标题"""
    print(f"\n===== {title} =====")
    print()

def check_directory_exists(path, name):
    """检查目录是否存在"""
    if Path(path).exists():
        print(f"{name}目录存在")
        return True
    else:
        print(f"错误：{name}目录不存在！")
        return False

def run_command(cmd, cwd=None, shell=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, cwd=cwd, shell=shell, check=True, 
                              capture_output=False, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败：{e}")
        return False

def start_service(name, cmd, cwd=None):
    """启动服务"""
    try:
        if os.name == 'nt':  # Windows
            # 修复Windows命令语法
            subprocess.Popen(f'start "足球管理系统-{name}" cmd /k "{cmd}"', 
                           cwd=cwd, shell=True)
        else:  # Unix/Linux
            subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', cmd], 
                           cwd=cwd)
        print(f"{name}服务已启动")
        return True
    except Exception as e:
        print(f"启动{name}服务失败：{e}")
        return False

def main():
    """主函数"""
    print("足球管理系统安装和启动脚本")
    
    # 获取脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print(f"\n当前目录: {os.getcwd()}")
    
    # 检查前端目录
    print_section("检查前端目录")
    if not check_directory_exists("frontend", "前端"):
        input("按任意键退出...")
        sys.exit(1)
    
    # 安装前端依赖
    print_section("安装前端依赖")
    
    frontend_dir = Path("frontend")
    package_json = frontend_dir / "package.json"
    
    if package_json.exists():
        print("找到package.json，开始安装依赖...")
        if not run_command("npm install", cwd=frontend_dir):
            print("npm install 失败！")
            input("按任意键退出...")
            sys.exit(1)
    else:
        print("错误：frontend目录中找不到package.json！")
        input("按任意键退出...")
        sys.exit(1)
    
    # 启动前端服务
    print_section("启动前端服务")
    frontend_cmd = f"cd /d \"{script_dir}\\frontend\" && npm run dev"
    if os.name != 'nt':
        frontend_cmd = f"cd \"{script_dir}/frontend\" && npm run dev"
    
    start_service("前端", frontend_cmd)
    
    # 启动后端服务
    print_section("启动后端服务（调试模式）")
    
    backend_run = Path("backend") / "run.py"
    if backend_run.exists():
        # 设置环境变量并启动后端服务 - 使用新的Flask 2.3+标准
        backend_cmd = f"cd /d \"{script_dir}\" && set FLASK_DEBUG=1 && python backend\\run.py"
        if os.name != 'nt':
            backend_cmd = f"cd \"{script_dir}\" && export FLASK_DEBUG=1 && python backend/run.py"
        
        start_service("后端", backend_cmd)
    else:
        print("错误：找不到backend\\run.py文件！")
        input("按任意键退出...")
        sys.exit(1)
    
    # 等待服务启动
    print("\n等待服务启动...")
    time.sleep(2)
    
    # 显示服务信息
    print("\n前后端服务已启动（调试模式）：")
    print("前端: http://localhost:3000")
    print("后端: http://localhost:5000 （调试模式，日志会显示在后端窗口中）")
    print("\n注意：后端窗口将显示所有调试日志信息")
    print("按任意键退出...")
    
    input()

if __name__ == "__main__":
    main()
