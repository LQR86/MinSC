"""
ECS (Entity Component System) 架构模块

使用esper库实现轻量级ECS架构，用于高效管理游戏实体和系统。
这个模块保持与现有代码的API兼容性，同时提供ECS性能优势。
"""

from .world import ECSWorld
from .factory import EntityFactory, create_default_game_entities
from .adapter import ECSAdapter, WorkerAdapter, BuildingAdapter, UnitAdapter, ResourcePointAdapter

# 导入主要组件
from .components import (
    Position, Velocity, Health, Sprite, Movement, UnitInfo, UnitType,
    Selectable, Resource, ResourcePoint, Storage, ProductionQueue, 
    Building, StateMachine, Collider, Target
)

# 导入主要系统
from .systems import (
    MovementSystem, RenderSystem, SelectionSystem, ResourceSystem,
    ProductionSystem, StateMachineSystem
)

__all__ = [
    # 核心类
    'ECSWorld',
    'EntityFactory', 
    'create_default_game_entities',
    'ECSAdapter',
    # 适配器类
    'WorkerAdapter', 'BuildingAdapter', 'UnitAdapter', 'ResourcePointAdapter',
    # Components
    'Position', 'Velocity', 'Health', 'Sprite', 'Movement', 'UnitInfo', 'UnitType',
    'Selectable', 'Resource', 'ResourcePoint', 'Storage', 'ProductionQueue', 
    'Building', 'StateMachine', 'Collider', 'Target',
    # Systems
    'MovementSystem', 'RenderSystem', 'SelectionSystem', 'ResourceSystem',
    'ProductionSystem', 'StateMachineSystem'
]