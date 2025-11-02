"""
MinSC 状态机框架
用于管理游戏对象的复杂状态转换和行为逻辑
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Optional, Callable, Any
import time

class StateTransition:
    """状态转换定义"""
    def __init__(self, from_state: str, to_state: str, condition: Callable[[], bool], action: Optional[Callable] = None):
        self.from_state = from_state
        self.to_state = to_state
        self.condition = condition
        self.action = action  # 转换时执行的动作

class State(ABC):
    """抽象状态基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.entry_time = 0.0
    
    def enter(self, context: Any) -> None:
        """进入状态时调用"""
        self.entry_time = time.time()
        self.on_enter(context)
    
    def exit(self, context: Any) -> None:
        """离开状态时调用"""
        self.on_exit(context)
    
    def update(self, context: Any, dt: float) -> None:
        """状态更新逻辑"""
        self.on_update(context, dt)
    
    @abstractmethod
    def on_enter(self, context: Any) -> None:
        """子类实现：进入状态逻辑"""
        pass
    
    @abstractmethod
    def on_exit(self, context: Any) -> None:
        """子类实现：离开状态逻辑"""
        pass
    
    @abstractmethod
    def on_update(self, context: Any, dt: float) -> None:
        """子类实现：状态更新逻辑"""
        pass
    
    def get_duration(self) -> float:
        """获取在此状态的持续时间"""
        return time.time() - self.entry_time

class StateMachine:
    """状态机管理器"""
    
    def __init__(self, initial_state: str):
        self.states: Dict[str, State] = {}
        self.transitions: list[StateTransition] = []
        self.current_state: Optional[State] = None
        self.initial_state = initial_state
        self.context = None
        
        # 调试信息
        self.debug_enabled = True
        self.transition_history: list[tuple[str, str, float]] = []  # (from, to, timestamp)
    
    def add_state(self, state: State) -> None:
        """添加状态"""
        self.states[state.name] = state
    
    def add_transition(self, transition: StateTransition) -> None:
        """添加状态转换规则"""
        self.transitions.append(transition)
    
    def start(self, context: Any) -> None:
        """启动状态机"""
        self.context = context
        if self.initial_state in self.states:
            self._change_state(self.initial_state)
        else:
            raise ValueError(f"初始状态 '{self.initial_state}' 不存在")
    
    def update(self, dt: float) -> None:
        """更新状态机"""
        if not self.current_state:
            return
        
        # 更新当前状态
        self.current_state.update(self.context, dt)
        
        # 检查状态转换条件
        for transition in self.transitions:
            if (transition.from_state == self.current_state.name and 
                transition.condition()):
                
                # 执行转换动作
                if transition.action:
                    transition.action()
                
                # 切换状态
                self._change_state(transition.to_state)
                break
    
    def force_transition(self, target_state: str) -> bool:
        """强制切换到指定状态"""
        if target_state in self.states:
            self._change_state(target_state)
            return True
        return False
    
    def _change_state(self, state_name: str) -> None:
        """内部状态切换方法"""
        if state_name not in self.states:
            raise ValueError(f"状态 '{state_name}' 不存在")
        
        old_state_name = self.current_state.name if self.current_state else "None"
        
        # 离开当前状态
        if self.current_state:
            self.current_state.exit(self.context)
        
        # 进入新状态
        self.current_state = self.states[state_name]
        self.current_state.enter(self.context)
        
        # 记录转换历史
        self.transition_history.append((old_state_name, state_name, time.time()))
        
        # 调试输出
        if self.debug_enabled and hasattr(self.context, 'id'):
            print(f"🔄 {self.context.__class__.__name__}{self.context.id} 状态: {old_state_name} → {state_name}")
    
    def get_current_state_name(self) -> Optional[str]:
        """获取当前状态名称"""
        return self.current_state.name if self.current_state else None
    
    def get_transition_history(self) -> list[tuple[str, str, float]]:
        """获取状态转换历史"""
        return self.transition_history.copy()
    
    def is_in_state(self, state_name: str) -> bool:
        """检查是否在指定状态"""
        return (self.current_state and 
                self.current_state.name == state_name)
    
    def reset(self) -> None:
        """重置状态机到初始状态"""
        if self.current_state:
            self.current_state.exit(self.context)
        self.current_state = None
        self.transition_history.clear()
        if self.context:
            self.start(self.context)

# 便捷的状态创建函数
def create_simple_state(name: str, 
                       enter_func: Optional[Callable] = None,
                       exit_func: Optional[Callable] = None,
                       update_func: Optional[Callable] = None) -> State:
    """创建简单状态的便捷函数"""
    
    class SimpleState(State):
        def on_enter(self, context):
            if enter_func:
                enter_func(context)
        
        def on_exit(self, context):
            if exit_func:
                exit_func(context)
        
        def on_update(self, context, dt):
            if update_func:
                update_func(context, dt)
    
    return SimpleState(name)