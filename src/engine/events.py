"""
MinSC事件系统
基于blinker实现的游戏事件总线，用于系统间解耦通信
"""

from blinker import signal
from typing import Dict, Any, Optional
import time


class GameEventBus:
    """游戏事件总线"""
    
    def __init__(self):
        # 定义游戏核心事件
        self.events = {
            # 单位事件
            'unit_created': signal('unit-created'),
            'unit_died': signal('unit-died'),
            'unit_moved': signal('unit-moved'),
            'unit_selected': signal('unit-selected'),
            'unit_deselected': signal('unit-deselected'),
            
            # 资源事件
            'resource_gathered': signal('resource-gathered'),
            'resource_depleted': signal('resource-depleted'),
            'resource_delivered': signal('resource-delivered'),
            
            # 建筑事件
            'building_created': signal('building-created'),
            'building_destroyed': signal('building-destroyed'),
            'building_selected': signal('building-selected'),
            'production_started': signal('production-started'),
            'production_completed': signal('production-completed'),
            
            # 游戏状态事件
            'game_started': signal('game-started'),
            'game_paused': signal('game-paused'),
            'game_resumed': signal('game-resumed'),
            'game_ended': signal('game-ended'),
            
            # 玩家事件
            'player_command': signal('player-command'),
            'player_resources_changed': signal('player-resources-changed'),
            
            # 战斗事件
            'combat_started': signal('combat-started'),
            'combat_ended': signal('combat-ended'),
            'unit_attacked': signal('unit-attacked'),
            'unit_damaged': signal('unit-damaged'),
        }
        
        # 事件历史记录（用于调试）
        self.event_history = []
        self.max_history_size = 1000
        
        # 统计信息
        self.event_stats = {}
    
    def emit(self, event_name: str, sender: Any = None, **kwargs) -> None:
        """发送事件"""
        if event_name not in self.events:
            print(f"⚠️ 未知事件: {event_name}")
            return
        
        # 添加时间戳
        kwargs['timestamp'] = time.time()
        
        # 记录事件历史
        self._record_event(event_name, sender, kwargs)
        
        # 发送事件
        self.events[event_name].send(sender, **kwargs)
    
    def connect(self, event_name: str, callback, weak: bool = True) -> None:
        """连接事件监听器"""
        if event_name not in self.events:
            print(f"⚠️ 未知事件: {event_name}")
            return
        
        self.events[event_name].connect(callback, weak=weak)
    
    def disconnect(self, event_name: str, callback) -> None:
        """断开事件监听器"""
        if event_name not in self.events:
            return
        
        self.events[event_name].disconnect(callback)
    
    def _record_event(self, event_name: str, sender: Any, kwargs: Dict[str, Any]) -> None:
        """记录事件历史"""
        event_record = {
            'event': event_name,
            'sender': str(sender),
            'data': kwargs.copy(),
            'timestamp': time.time()
        }
        
        self.event_history.append(event_record)
        
        # 限制历史记录大小
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)
        
        # 更新统计
        self.event_stats[event_name] = self.event_stats.get(event_name, 0) + 1
    
    def get_event_history(self, event_name: Optional[str] = None, limit: int = 100) -> list:
        """获取事件历史"""
        if event_name:
            filtered = [e for e in self.event_history if e['event'] == event_name]
            return filtered[-limit:]
        return self.event_history[-limit:]
    
    def get_event_stats(self) -> Dict[str, int]:
        """获取事件统计"""
        return self.event_stats.copy()
    
    def clear_history(self) -> None:
        """清空事件历史"""
        self.event_history.clear()
        self.event_stats.clear()


# 全局事件总线实例
game_events = GameEventBus()


# 便捷装饰器
def on_event(event_name: str):
    """事件监听装饰器"""
    def decorator(func):
        game_events.connect(event_name, func)
        return func
    return decorator


# 事件监听器示例和调试工具
class EventLogger:
    """事件日志记录器"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        if enabled:
            self._setup_logging()
    
    def _setup_logging(self):
        """设置日志记录"""
        # 记录所有重要事件
        important_events = [
            'unit_created', 'unit_died', 'resource_gathered', 
            'production_completed', 'game_started', 'game_ended'
        ]
        
        for event_name in important_events:
            game_events.connect(event_name, self._log_event)
    
    def _log_event(self, sender, **kwargs):
        """记录事件日志"""
        if not self.enabled:
            return
        
        event_name = kwargs.get('event', 'unknown')
        timestamp = kwargs.get('timestamp', time.time())
        
        # 格式化日志信息
        sender_info = ""
        if hasattr(sender, 'id'):
            sender_info = f"{sender.__class__.__name__}{sender.id}"
        elif hasattr(sender, '__class__'):
            sender_info = sender.__class__.__name__
        else:
            sender_info = str(sender)
        
        print(f"📡 [{timestamp:.2f}] {event_name}: {sender_info}")


# 默认启用事件日志
event_logger = EventLogger(enabled=True)


# 单元测试辅助
def test_event_system():
    """测试事件系统"""
    print("🧪 测试事件系统...")
    
    # 测试事件发送和接收
    received_events = []
    
    @on_event('unit_created')
    def test_handler(sender, **kwargs):
        received_events.append((sender, kwargs))
    
    # 发送测试事件
    class TestUnit:
        def __init__(self, unit_id):
            self.id = unit_id
    
    test_unit = TestUnit(999)
    game_events.emit('unit_created', test_unit, position=(100, 200), unit_type='worker')
    
    # 验证事件接收
    assert len(received_events) == 1
    assert received_events[0][0] == test_unit
    assert received_events[0][1]['position'] == (100, 200)
    
    # 测试事件统计
    stats = game_events.get_event_stats()
    assert 'unit_created' in stats
    assert stats['unit_created'] >= 1
    
    print("✅ 事件系统测试通过!")


if __name__ == "__main__":
    test_event_system()