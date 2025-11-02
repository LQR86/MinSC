#!/usr/bin/env python3
"""
MinSC 游戏启动器
自动检测虚拟环境并启动游戏
"""

import os
import sys
import subprocess
import platform

def main():
    print("🚀 启动MinSC游戏...")
    print("=" * 50)
    
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 检测操作系统
    system = platform.system().lower()
    
    # 确定Python可执行文件路径
    if system == "windows":
        python_exe = os.path.join("venv", "Scripts", "python.exe")
    else:
        python_exe = os.path.join("venv", "bin", "python")
    
    # 检查虚拟环境是否存在
    if not os.path.exists(python_exe):
        print("❌ 虚拟环境未找到！")
        print("请先安装虚拟环境：")
        print("  python -m venv venv")
        print("  然后安装依赖：")
        if system == "windows":
            print("  venv\\Scripts\\pip install -r requirements.txt")
        else:
            print("  venv/bin/pip install -r requirements.txt")
        return 1
    
    # 游戏主文件路径
    main_py = os.path.join("src", "main.py")
    
    if not os.path.exists(main_py):
        print(f"❌ 游戏文件未找到: {main_py}")
        return 1
    
    # 启动游戏
    print("🎮 正在启动MinSC...")
    try:
        result = subprocess.run([python_exe, main_py], check=True)
        print("\n👋 游戏已结束")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 游戏启动失败: {e}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n⚠️ 游戏被用户中断")
        return 0

if __name__ == "__main__":
    sys.exit(main())