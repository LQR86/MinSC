"""
ECS 组件定义

定义所有游戏实体使用的组件。
组件只包含数据，不包含逻辑。
"""

import pygame
from typing import Optional, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# 基础组件
# ============================================================================

@dataclass
class Position:
    """位置组件 - 实体在世界中的位置"""
    x: float
    y: float
    
    def to_tuple(self) -> Tuple[float, float]:
        """返回位置元组"""
        return (self.x, self.y)
    
    def distance_to(self, other: 'Position') -> float:
        """计算到另一个位置的距离"""
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx * dx + dy * dy) ** 0.5

@dataclass
class Velocity:
    """速度组件 - 实体的移动速度"""
    dx: float = 0.0
    dy: float = 0.0
    max_speed: float = 100.0  # 最大速度（像素/秒）
    
    def magnitude(self) -> float:
        """返回速度大小"""
        return (self.dx * self.dx + self.dy * self.dy) ** 0.5
    
    def normalize(self) -> None:
        """标准化速度到最大速度"""
        mag = self.magnitude()
        if mag > self.max_speed:
            self.dx = (self.dx / mag) * self.max_speed
            self.dy = (self.dy / mag) * self.max_speed

@dataclass
class Health:
    """生命值组件 - 实体的血量"""
    current: int
    maximum: int
    
    def is_alive(self) -> bool:
        """检查是否存活"""
        return self.current > 0
    
    def damage(self, amount: int) -> None:
        """受到伤害"""
        self.current = max(0, self.current - amount)
    
    def heal(self, amount: int) -> None:
        """治疗"""
        self.current = min(self.maximum, self.current + amount)
    
    def health_percentage(self) -> float:
        """返回血量百分比"""
        return self.current / self.maximum if self.maximum > 0 else 0.0

# ============================================================================
# 渲染组件
# ============================================================================

@dataclass
class Sprite:
    """精灵组件 - 实体的视觉表示"""
    color: Tuple[int, int, int]
    size: Tuple[int, int]
    layer: int = 0  # 渲染层级，数字越大越靠前
    visible: bool = True

@dataclass
class Animation:
    """动画组件 - 实体的动画状态"""
    current_frame: int = 0
    frame_count: int = 1
    frame_duration: float = 0.1  # 每帧持续时间（秒）
    elapsed_time: float = 0.0
    looping: bool = True

# ============================================================================
# 移动和AI组件
# ============================================================================

@dataclass
class Movement:
    """移动组件 - 实体的移动状态"""
    target: Optional[Tuple[float, float]] = None
    speed: float = 50.0  # 移动速度（像素/秒）
    is_moving: bool = False
    path: List[Tuple[float, float]] = None  # 移动路径
    
    def __post_init__(self):
        if self.path is None:
            self.path = []

class UnitType(Enum):
    """单位类型枚举"""
    WORKER = "worker"
    MARINE = "marine"
    COMMAND_CENTER = "command_center"
    BARRACKS = "barracks"

@dataclass
class UnitInfo:
    """单位信息组件 - 单位的基本信息"""
    unit_type: UnitType
    player_id: int
    name: str = ""
    description: str = ""

# ============================================================================
# 游戏逻辑组件
# ============================================================================

@dataclass
class Selectable:
    """可选择组件 - 标记实体可被玩家选择"""
    selected: bool = False
    selection_radius: float = 20.0  # 选择半径

@dataclass
class Resource:
    """资源组件 - 实体携带的资源"""
    amount: int = 0
    capacity: int = 10
    resource_type: str = "mineral"
    
    def is_full(self) -> bool:
        """检查是否满载"""
        return self.amount >= self.capacity
    
    def is_empty(self) -> bool:
        """检查是否为空"""
        return self.amount <= 0
    
    def add(self, amount: int) -> int:
        """添加资源，返回实际添加的数量"""
        can_add = min(amount, self.capacity - self.amount)
        self.amount += can_add
        return can_add
    
    def remove(self, amount: int) -> int:
        """移除资源，返回实际移除的数量"""
        can_remove = min(amount, self.amount)
        self.amount -= can_remove
        return can_remove

@dataclass
class ResourcePoint:
    """资源点组件 - 标记实体为资源点"""
    total_amount: int
    remaining_amount: int
    resource_type: str = "mineral"
    depletion_rate: int = 1  # 每次采集消耗的资源
    
    def is_depleted(self) -> bool:
        """检查是否枯竭"""
        return self.remaining_amount <= 0
    
    def harvest(self, amount: int) -> int:
        """采集资源，返回实际采集的数量"""
        can_harvest = min(amount, self.remaining_amount)
        self.remaining_amount -= can_harvest
        return can_harvest

@dataclass
class Storage:
    """存储组件 - 实体可以存储资源"""
    capacity: int
    stored: int = 0
    resource_type: str = "mineral"
    
    def is_full(self) -> bool:
        """检查是否满仓"""
        return self.stored >= self.capacity
    
    def can_store(self, amount: int) -> bool:
        """检查是否可以存储指定数量"""
        return self.stored + amount <= self.capacity
    
    def store(self, amount: int) -> int:
        """存储资源，返回实际存储的数量"""
        can_store = min(amount, self.capacity - self.stored)
        self.stored += can_store
        return can_store

# ============================================================================
# 生产和建筑组件
# ============================================================================

@dataclass
class ProductionQueue:
    """生产队列组件 - 实体可以生产其他单位"""
    queue: List[str]  # 生产队列，存储单位类型
    current_progress: float = 0.0  # 当前生产进度（0.0-1.0）
    production_speed: float = 1.0  # 生产速度倍率
    max_queue_size: int = 5
    
    def __post_init__(self):
        if self.queue is None:
            self.queue = []
    
    def add_to_queue(self, unit_type: str) -> bool:
        """添加单位到生产队列"""
        if len(self.queue) < self.max_queue_size:
            self.queue.append(unit_type)
            return True
        return False
    
    def is_empty(self) -> bool:
        """检查队列是否为空"""
        return len(self.queue) == 0
    
    def current_item(self) -> Optional[str]:
        """获取当前生产的项目"""
        return self.queue[0] if self.queue else None

@dataclass
class Building:
    """建筑组件 - 标记实体为建筑"""
    construction_progress: float = 1.0  # 建造进度（0.0-1.0）
    is_constructed: bool = True
    can_produce: bool = True  # 是否可以生产单位
    
    def is_under_construction(self) -> bool:
        """检查是否在建造中"""
        return self.construction_progress < 1.0

# ============================================================================
# 状态机组件
# ============================================================================

@dataclass
class StateMachine:
    """状态机组件 - 实体的状态机引用"""
    state_machine: Any  # 实际的状态机实例
    current_state: str = "idle"
    
    def trigger(self, event: str) -> bool:
        """触发状态机事件"""
        if hasattr(self.state_machine, 'trigger'):
            try:
                self.state_machine.trigger(event)
                self.current_state = self.state_machine.state
                return True
            except:
                return False
        return False

# ============================================================================
# 物理和碰撞组件
# ============================================================================

@dataclass
class Collider:
    """碰撞体组件 - 实体的碰撞检测"""
    radius: float = 10.0
    collision_layer: int = 0  # 碰撞层
    solid: bool = True  # 是否阻挡移动

@dataclass
class Target:
    """目标组件 - 实体的当前目标"""
    entity: Optional[int] = None  # 目标实体ID
    position: Optional[Tuple[float, float]] = None  # 目标位置
    target_type: str = "move"  # 目标类型：move, attack, gather, build

# ============================================================================
# 导出所有组件
# ============================================================================

__all__ = [
    # 基础组件
    'Position', 'Velocity', 'Health',
    # 渲染组件
    'Sprite', 'Animation',
    # 移动和AI组件
    'Movement', 'UnitType', 'UnitInfo',
    # 游戏逻辑组件
    'Selectable', 'Resource', 'ResourcePoint', 'Storage',
    # 生产和建筑组件
    'ProductionQueue', 'Building',
    # 状态机组件
    'StateMachine',
    # 物理和碰撞组件
    'Collider', 'Target'
]