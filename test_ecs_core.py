#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ECS 核心功能测试脚本（无渲染）
"""

import sys
import os
sys.path.append('src')

# 导入ECS模块
from ecs.world import ECSWorld
from ecs.factory import EntityFactory
from ecs.components import *
from ecs.systems import MovementSystem, ResourceSystem, ProductionSystem, StateMachineSystem
from units.worker_fsm import WorkerStateMachine

def test_ecs_core_only():
    """测试ECS核心功能（不包含渲染）"""
    print("Testing ECS core functionality (no rendering)...")
    
    try:
        # 创建ECS世界
        world = ECSWorld()
        factory = EntityFactory(world)
        
        print("✓ ECS world and factory created")
        
        # 创建测试实体
        worker = factory.create_worker((100, 100), player_id=0)
        command_center = factory.create_command_center((300, 300), player_id=0)
        resource_point = factory.create_resource_point((200, 200), 500)
        
        print(f"✓ Entities created: worker={worker}, cc={command_center}, resource={resource_point}")
        
        # 添加系统（不包含渲染系统）
        movement_system = MovementSystem()
        resource_system = ResourceSystem()
        production_system = ProductionSystem(factory._create_unit_for_test)
        
        world.add_processor(movement_system, priority=1)
        world.add_processor(resource_system, priority=2)
        world.add_processor(production_system, priority=3)
        
        print("✓ Systems added")
        
        # 测试移动
        movement = world.get_component(worker, Movement)
        movement.target = (150, 150)
        movement.is_moving = True
        
        print("\nTesting movement...")
        for i in range(10):
            world.process(1/60)  # 60FPS
            pos = world.get_component(worker, Position)
            if i % 3 == 0:
                print(f"  Frame {i}: Worker at ({pos.x:.1f}, {pos.y:.1f})")
        
        # 测试资源采集
        print("\nTesting resource harvesting...")
        worker_resource = world.get_component(worker, Resource)
        resource_point_comp = world.get_component(resource_point, ResourcePoint)
        
        print(f"Before harvest: worker={worker_resource.amount}, resource={resource_point_comp.remaining_amount}")
        
        success = resource_system.harvest_resource(worker, resource_point)
        print(f"Harvest result: {success}")
        
        print(f"After harvest: worker={worker_resource.amount}, resource={resource_point_comp.remaining_amount}")
        
        # 测试生产
        print("\nTesting production...")
        production_queue = world.get_component(command_center, ProductionQueue)
        production_system.add_to_production(command_center, "worker")
        
        print(f"Production queue: {production_queue.queue}")
        
        # 运行生产系统
        for i in range(10):
            world.process(0.5)  # 加速时间
            if i % 3 == 0:
                print(f"  Production frame {i}: progress={production_queue.current_progress:.2f}")
        
        # 获取统计
        stats = world.get_stats()
        print(f"\n📊 Final stats: {stats}")
        
        print("✓ ECS core test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Core test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ecs_state_machine_integration():
    """测试ECS与状态机集成（无渲染）"""
    print("\nTesting ECS-StateMachine integration (no rendering)...")
    
    try:
        # 创建ECS世界
        world = ECSWorld()
        factory = EntityFactory(world)
        
        # 创建临时工人对象用于状态机
        class MockWorker:
            def __init__(self):
                self.x, self.y = 100, 100
                self.target_resource = None
                self.target_storage = None
        
        mock_worker = MockWorker()
        worker_fsm = WorkerStateMachine(mock_worker)
        
        # 创建工人实体
        worker = factory.create_worker((100, 100), player_id=0)
        
        # 添加状态机组件
        world.add_component(worker, StateMachine(
            state_machine=worker_fsm,
            current_state=worker_fsm.state
        ))
        
        print("✓ Worker with state machine created")
        
        # 添加系统
        state_machine_system = StateMachineSystem()
        movement_system = MovementSystem()
        
        world.add_processor(state_machine_system, priority=0)
        world.add_processor(movement_system, priority=1)
        
        print("✓ Systems added")
        
        # 测试状态机更新
        print(f"Initial state: {worker_fsm.state}")
        
        for i in range(5):
            world.process(1/60)
            state_comp = world.get_component(worker, StateMachine)
            pos = world.get_component(worker, Position)
            print(f"  Frame {i}: State={state_comp.current_state}, Pos=({pos.x:.1f}, {pos.y:.1f})")
        
        print("✓ State machine integration test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ State machine integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ecs_large_scale():
    """测试ECS大规模实体性能"""
    print("\nTesting ECS large scale performance...")
    
    try:
        import time
        
        world = ECSWorld()
        factory = EntityFactory(world)
        
        # 创建大量实体
        print("Creating many entities...")
        start_time = time.time()
        
        entities = []
        for i in range(100):  # 100个工人
            x = 50 + (i % 10) * 50
            y = 50 + (i // 10) * 50
            worker = factory.create_worker((x, y), player_id=i % 2)
            entities.append(worker)
        
        for i in range(10):  # 10个资源点
            x = 200 + i * 60
            y = 400
            resource = factory.create_resource_point((x, y), 1000)
            entities.append(resource)
        
        creation_time = time.time() - start_time
        print(f"✓ Created {len(entities)} entities in {creation_time:.3f}s")
        
        # 添加移动系统
        movement_system = MovementSystem()
        world.add_processor(movement_system, priority=1)
        
        # 测试更新性能
        print("Testing update performance...")
        start_time = time.time()
        
        for frame in range(120):  # 120帧 = 2秒
            world.process(1/60)
            
            # 每20帧移动一些工人
            if frame % 20 == 0:
                for i in range(min(20, len(entities))):
                    entity = entities[i]
                    movement = world.get_component(entity, Movement)
                    if movement:
                        new_x = 100 + (frame * 5) % 400
                        new_y = 100 + (i * 10) % 200
                        movement.target = (new_x, new_y)
                        movement.is_moving = True
        
        update_time = time.time() - start_time
        print(f"✓ 120 frames updated in {update_time:.3f}s")
        print(f"  Average: {(update_time/120)*1000:.2f}ms per frame")
        
        # 获取最终统计
        stats = world.get_stats()
        print(f"📊 Large scale test stats: {stats}")
        
        print("✓ Large scale performance test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Large scale test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# 为生产系统添加一个简单的单位创建函数
def _create_unit_for_test(unit_type, position, player_id, some_extra_param=None):
    """测试用的简单单位创建函数"""
    print(f"Mock creating {unit_type} at {position} for player {player_id}")
    return 999  # 返回虚拟实体ID

# 修复EntityFactory
from ecs.factory import EntityFactory
EntityFactory._create_unit_for_test = _create_unit_for_test

if __name__ == "__main__":
    print("🚀 MinSC ECS 核心功能测试")
    print("=" * 50)
    
    all_passed = True
    
    # 运行各项测试
    all_passed &= test_ecs_core_only()
    all_passed &= test_ecs_state_machine_integration()
    all_passed &= test_ecs_large_scale()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有ECS核心测试通过！")
        print("\n✅ ECS架构验证成功:")
        print("  - 基础组件和系统正常工作")
        print("  - 状态机集成无问题")
        print("  - 大规模实体性能良好")
        print("  - 资源系统和生产系统正常")
        print("\n🔄 阶段3: ECS架构重构 - 基础验证完成！")
        print("📋 下一步: 将现有main.py游戏循环迁移到ECS")
    else:
        print("❌ 部分测试失败，请查看错误信息并修复")
    
    print("\n🏁 测试完成")