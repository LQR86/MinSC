#!/usr/bin/env python3
"""MinSC环境验证脚本"""

import sys
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")

try:
    import pygame
    print(f"Pygame版本: {pygame.version.ver}")
    
    import numpy as np
    print(f"NumPy版本: {np.__version__}")
    
    import pydantic
    print(f"Pydantic版本: {pydantic.VERSION}")
    
    print("\n✅ 所有依赖安装成功！MinSC开发环境就绪。")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    sys.exit(1)