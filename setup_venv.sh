#!/bin/bash
# MinSC虚拟环境管理脚本

set -e  # 遇到错误立即停止

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐍 MinSC虚拟环境管理${NC}"

# 确保在MinSC目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 当前目录: $(pwd)"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ venv目录不存在${NC}"
    exit 1
fi

# 激活虚拟环境的函数
activate_venv() {
    echo -e "${YELLOW}🔄 激活虚拟环境...${NC}"
    
    # Windows下的激活方式
    if [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    # Linux/Mac下的激活方式
    elif [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo -e "${RED}❌ 找不到虚拟环境激活脚本${NC}"
        exit 1
    fi
    
    # 验证虚拟环境是否激活
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo -e "${GREEN}✅ 虚拟环境已激活: $VIRTUAL_ENV${NC}"
        python -c "import sys; print('Python路径:', sys.executable)"
    else
        echo -e "${RED}❌ 虚拟环境激活失败${NC}"
        exit 1
    fi
}

# 安装依赖的函数
install_dependencies() {
    echo -e "${YELLOW}📦 安装MinSC架构组件...${NC}"
    
    # 升级pip
    python -m pip install --upgrade pip
    
    # 安装基础依赖
    echo "安装基础组件..."
    pip install pygame>=2.5.0 numpy>=1.26 pydantic>=1.10
    
    # 安装架构组件
    echo "安装架构组件..."
    pip install blinker>=1.6.0      # 事件系统
    pip install transitions>=0.9.0   # 状态机
    pip install esper>=2.1.0        # ECS系统
    
    # 安装开发工具
    echo "安装开发工具..."
    pip install pytest>=7.0.0
    
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
}

# 显示已安装包
show_packages() {
    echo -e "${YELLOW}📋 已安装的包:${NC}"
    pip list | grep -E "(pygame|blinker|transitions|esper|pytest|numpy|pydantic)"
}

# 测试安装
test_installation() {
    echo -e "${YELLOW}🧪 测试组件导入...${NC}"
    python -c "
import pygame
print('✅ pygame:', pygame.version.ver)

import blinker
print('✅ blinker: 导入成功')

import transitions
print('✅ transitions: 导入成功')

import esper
print('✅ esper: 导入成功')

print('🎉 所有组件导入成功!')
"
}

# 主逻辑
main() {
    activate_venv
    
    case "${1:-install}" in
        "install")
            install_dependencies
            show_packages
            test_installation
            ;;
        "test")
            test_installation
            ;;
        "list")
            show_packages
            ;;
        "shell")
            echo -e "${GREEN}🐚 进入虚拟环境shell...${NC}"
            echo "使用 'exit' 退出"
            exec bash
            ;;
        *)
            echo "用法: $0 [install|test|list|shell]"
            echo "  install - 安装所有依赖 (默认)"
            echo "  test    - 测试组件导入"
            echo "  list    - 显示已安装包"
            echo "  shell   - 进入虚拟环境shell"
            ;;
    esac
}

main "$@"