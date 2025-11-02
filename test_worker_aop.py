"""
测试Worker类的AOP功能集成
"""
import sys
import os
import time

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ioc.container import get_container
from aop import apply_aspects_to_class, logging_aspect, performance_aspect, transactional


# 模拟ResourcePoint类
class MockResourcePoint:
    def __init__(self, x, y, amount=100):
        self.id = 1
        self.x = x
        self.y = y
        self.amount = amount


# 简化的Worker测试类
class TestWorker:
    def __init__(self, x, y, worker_id=1):
        self.id = worker_id
        self.x = x
        self.y = y
        self.carrying_resources = 0
        self.max_carry_capacity = 8
        self.gather_rate = 2
        self.gathering_target = None

    def distance_to(self, x, y):
        """计算到目标点的距离"""
        return ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5

    def _start_gather(self, resource_point):
        """开始采集资源 - 应用AOP装饰器"""
        if not resource_point or resource_point.amount <= 0:
            return
            
        print(f"🔨 工人{self.id} 前往采集资源点{resource_point.id} ({resource_point.x}, {resource_point.y})")
        self.gathering_target = resource_point
        return True

    def _gather_resources(self):
        """执行采集动作 - 应用AOP装饰器"""
        if not self.gathering_target:
            return
        
        # 模拟一点延迟
        time.sleep(0.05)
        
        # 计算本次采集量
        gather_amount = min(
            self.gather_rate,
            self.gathering_target.amount,
            self.max_carry_capacity - self.carrying_resources
        )
        
        if gather_amount > 0:
            # 从资源点扣除
            self.gathering_target.amount -= gather_amount
            # 工人携带
            self.carrying_resources += gather_amount
            
            print(f"🔨 工人{self.id} 采集了 {gather_amount} 资源 (携带: {self.carrying_resources}/{self.max_carry_capacity})")
            return gather_amount
        
        return 0

    def update(self, dt):
        """更新工人状态 - 应用性能监控"""
        # 模拟更新逻辑
        if self.gathering_target:
            distance = self.distance_to(self.gathering_target.x, self.gathering_target.y)
            if distance <= 2.0:  # 在采集范围内
                return self._gather_resources()
        return 0


def test_worker_aop():
    """测试Worker的AOP功能"""
    print("🚀 开始Worker AOP集成测试...")
    
    # 初始化容器
    container = get_container()
    print("✅ IoC容器初始化完成")
    
    # 创建测试Worker
    worker = TestWorker(10, 10, worker_id=1)
    
    # 手动应用AOP装饰器到关键方法
    worker._start_gather = logging_aspect(transactional(worker._start_gather))
    worker._gather_resources = performance_aspect(transactional(worker._gather_resources))
    worker.update = performance_aspect(worker.update)
    
    print("✅ AOP装饰器应用完成")
    
    # 创建资源点
    resource_point = MockResourcePoint(12, 12, amount=20)
    
    # 测试采集流程
    print("\n📦 测试采集流程...")
    
    # 1. 开始采集
    print("1. 开始采集任务...")
    worker._start_gather(resource_point)
    
    # 2. 执行多次更新（模拟游戏循环）
    print("2. 执行采集循环...")
    for i in range(5):
        print(f"   第{i+1}次更新:")
        worker.update(0.1)
        
        if resource_point.amount <= 0:
            print("   资源点已耗尽!")
            break
        
        time.sleep(0.02)  # 模拟游戏帧间隔
    
    # 3. 测试事务回滚
    print("\n🔄 测试事务回滚...")
    original_resources = worker.carrying_resources
    print(f"   回滚前携带资源: {original_resources}")
    
    # 创建会导致异常的资源点
    bad_resource = None
    try:
        worker._start_gather(bad_resource)  # 应该触发异常和回滚
    except Exception as e:
        print(f"   预期异常: {e}")
        print(f"   回滚后携带资源: {worker.carrying_resources}")
    
    # 4. 性能统计
    print("\n📊 性能测试...")
    start_time = time.time()
    
    # 执行大量更新
    for i in range(100):
        worker.update(0.016)  # 60 FPS
    
    total_time = time.time() - start_time
    print(f"   执行100次更新耗时: {total_time:.3f}s")
    print(f"   平均每次更新: {total_time/100*1000:.1f}ms")
    
    print("\n✅ Worker AOP集成测试完成!")
    print(f"最终状态 - 工人携带资源: {worker.carrying_resources}, 资源点剩余: {resource_point.amount}")


if __name__ == "__main__":
    test_worker_aop()