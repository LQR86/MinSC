"""
测试AOP功能集成
"""
import sys
import os
import time

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ioc.container import get_container, wire_container
from aop import logged, performance_monitored, transactional, monitored

# 测试类
class TestService:
    def __init__(self):
        self.data = {"count": 0}
    
    @logged
    def simple_method(self, value):
        """简单方法测试"""
        return f"Processed: {value}"
    
    @performance_monitored
    def slow_method(self):
        """性能监控测试"""
        time.sleep(0.1)  # 模拟慢操作
        return "Slow operation completed"
    
    @transactional
    def transactional_method(self, should_fail=False):
        """事务测试"""
        original_count = self.data["count"]
        self.data["count"] += 1
        
        if should_fail:
            raise ValueError("Simulated error")
        
        return self.data["count"]
    
    @monitored
    def monitored_method(self, value):
        """综合监控测试"""
        if value < 0:
            raise ValueError("Negative value not allowed")
        return value * 2

def test_aop_integration():
    """测试AOP集成"""
    print("🧪 开始AOP集成测试...")
    
    # 初始化容器
    container = get_container()
    print("✅ IoC容器初始化完成")
    
    # 创建测试服务
    test_service = TestService()
    
    # 测试日志切面
    print("\n🔍 测试日志切面...")
    result = test_service.simple_method("test_value")
    print(f"Result: {result}")
    
    # 测试性能监控切面
    print("\n⏱️ 测试性能监控切面...")
    result = test_service.slow_method()
    print(f"Result: {result}")
    
    # 测试事务切面 - 成功案例
    print("\n💾 测试事务切面 (成功)...")
    original_data = test_service.data.copy()
    result = test_service.transactional_method(should_fail=False)
    print(f"Result: {result}, Data: {test_service.data}")
    
    # 测试事务切面 - 失败回滚
    print("\n🔄 测试事务切面 (回滚)...")
    print(f"Data before transaction: {test_service.data}")
    try:
        test_service.transactional_method(should_fail=True)
    except ValueError as e:
        print(f"Expected error: {e}")
        print(f"Data after rollback: {test_service.data}")
    
    # 测试综合监控
    print("\n📊 测试综合监控...")
    
    # 正常情况
    result = test_service.monitored_method(5)
    print(f"Normal result: {result}")
    
    # 异常情况
    try:
        test_service.monitored_method(-1)
    except ValueError as e:
        print(f"Handled error: {e}")
    
    print("\n✅ AOP集成测试完成!")

if __name__ == "__main__":
    test_aop_integration()