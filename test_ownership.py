#!/usr/bin/env python3
"""
测试玩家所有权功能
验证工人不能在敌方基地卸载资源
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from units.worker import Worker
from buildings.command_center import CommandCenter

def test_ownership():
    """测试所有权检查"""
    print("🧪 测试工人资源卸载所有权检查...")
    print("=" * 50)
    
    # 创建玩家1的工人和基地
    player1_worker = Worker(100, 100, player_id=0)
    player1_base = CommandCenter(50, 50, player_id=0)
    
    # 创建玩家2的基地
    player2_base = CommandCenter(500, 500, player_id=1)
    
    # 给工人一些资源
    player1_worker.carrying_resources = 10
    
    print(f"玩家1工人携带资源: {player1_worker.carrying_resources}")
    print(f"玩家1基地存储: {player1_base.stored_resources}/{player1_base.max_storage}")
    print(f"玩家2基地存储: {player2_base.stored_resources}/{player2_base.max_storage}")
    print()
    
    # 测试1: 在己方基地卸载 (应该成功)
    print("测试1: 在己方基地卸载资源")
    result1 = player1_base.accept_resources(player1_worker)
    print(f"卸载结果: {result1} 资源")
    print(f"工人剩余资源: {player1_worker.carrying_resources}")
    print(f"玩家1基地存储: {player1_base.stored_resources}/{player1_base.max_storage}")
    print()
    
    # 重新给工人资源
    player1_worker.carrying_resources = 10
    
    # 测试2: 在敌方基地卸载 (应该失败)
    print("测试2: 在敌方基地卸载资源")
    result2 = player2_base.accept_resources(player1_worker)
    print(f"卸载结果: {result2} 资源")
    print(f"工人剩余资源: {player1_worker.carrying_resources}")
    print(f"玩家2基地存储: {player2_base.stored_resources}/{player2_base.max_storage}")
    print()
    
    # 验证结果
    if result1 > 0 and result2 == 0:
        print("✅ 所有权检查测试通过!")
        print("   - 工人可以在己方基地卸载资源")
        print("   - 工人不能在敌方基地卸载资源")
    else:
        print("❌ 所有权检查测试失败!")
        print(f"   - 己方基地卸载结果: {result1} (期望 > 0)")
        print(f"   - 敌方基地卸载结果: {result2} (期望 = 0)")

if __name__ == "__main__":
    test_ownership()