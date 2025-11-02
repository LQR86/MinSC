"""
事件总线服务实现
"""
from typing import Dict, List, Callable
from ioc.services import IEventBusService


class EventBusService:
    """简单的事件总线服务实现"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def emit(self, event_name: str, **kwargs):
        """发送事件"""
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                try:
                    callback(**kwargs)
                except Exception as e:
                    print(f"事件处理器错误 {event_name}: {e}")
    
    def subscribe(self, event_name: str, callback: Callable):
        """订阅事件"""
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)
    
    def unsubscribe(self, event_name: str, callback: Callable):
        """取消订阅"""
        if event_name in self._subscribers:
            try:
                self._subscribers[event_name].remove(callback)
            except ValueError:
                pass