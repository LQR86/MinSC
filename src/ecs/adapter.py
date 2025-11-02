"""
ECS 适配器

这个模块提供了在现有面向对象代码和新的ECS架构之间的适配层。
允许逐步迁移，保持API兼容性。
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import pygame

from .world import ECSWorld
from .factory import EntityFactory
from .components import *
from .systems import *

class ECSAdapter:
    """
    ECS适配器类
    
    提供传统面向对象API，内部使用ECS实现。
    这允许现有代码无缝迁移到ECS架构。
    """
    
    def __init__(self, screen: pygame.Surface):
        """
        初始化ECS适配器
        
        Args:
            screen: Pygame屏幕表面
        """
        self.ecs_world = ECSWorld()
        self.factory = EntityFactory(self.ecs_world)
        
        # 初始化系统
        self.movement_system = MovementSystem()
        self.render_system = RenderSystem(screen)
        self.selection_system = SelectionSystem()
        self.resource_system = ResourceSystem()
        self.production_system = ProductionSystem(self._create_unit)
        self.state_machine_system = StateMachineSystem()
        
        # 添加系统到ECS世界
        self.ecs_world.add_processor(self.state_machine_system, priority=0)  # 状态机优先级最高
        self.ecs_world.add_processor(self.movement_system, priority=1)
        self.ecs_world.add_processor(self.resource_system, priority=2)
        self.ecs_world.add_processor(self.production_system, priority=3)
        self.ecs_world.add_processor(self.render_system, priority=10)  # 渲染优先级最低
        
        # 实体映射 - 为了兼容性保留对象引用
        self.entities: Dict[int, Any] = {}
        self.worker_state_machines: Dict[int, Any] = {}
        
        logging.info("🔗 ECS适配器初始化完成")
    
    def create_worker(self, x: float, y: float, player_id: int = 0, state_machine=None) -> 'WorkerAdapter':
        """
        创建工人（适配器版本）
        
        Args:
            x, y: 位置坐标
            player_id: 玩家ID
            state_machine: 可选的状态机
            
        Returns:
            WorkerAdapter: 工人适配器对象
        """
        entity_id = self.factory.create_worker((x, y), player_id)
        
        # 如果提供了状态机，添加状态机组件
        if state_machine:
            self.ecs_world.add_component(entity_id, StateMachine(
                state_machine=state_machine,
                current_state=state_machine.state if hasattr(state_machine, 'state') else 'idle'
            ))
            self.worker_state_machines[entity_id] = state_machine
        
        # 创建适配器对象
        worker_adapter = WorkerAdapter(self, entity_id)
        self.entities[entity_id] = worker_adapter
        
        return worker_adapter
    
    def create_command_center(self, x: float, y: float, player_id: int = 0) -> 'BuildingAdapter':
        """
        创建指挥中心（适配器版本）
        
        Args:
            x, y: 位置坐标
            player_id: 玩家ID
            
        Returns:
            BuildingAdapter: 建筑适配器对象
        """
        entity_id = self.factory.create_command_center((x, y), player_id)
        
        # 创建适配器对象
        building_adapter = BuildingAdapter(self, entity_id)
        self.entities[entity_id] = building_adapter
        
        return building_adapter
    
    def create_resource_point(self, x: float, y: float, amount: int = 1000) -> 'ResourcePointAdapter':
        """
        创建资源点（适配器版本）
        
        Args:
            x, y: 位置坐标
            amount: 资源数量
            
        Returns:
            ResourcePointAdapter: 资源点适配器对象
        """
        entity_id = self.factory.create_resource_point((x, y), amount)
        
        # 创建适配器对象
        resource_adapter = ResourcePointAdapter(self, entity_id)
        self.entities[entity_id] = resource_adapter
        
        return resource_adapter
    
    def _create_unit(self, unit_type: str, position: Tuple[float, float], player_id: int) -> int:
        """
        内部单位创建函数（供生产系统使用）
        
        Args:
            unit_type: 单位类型
            position: 生成位置
            player_id: 玩家ID
            
        Returns:
            int: 新创建的实体ID
        """
        if unit_type == "worker":
            entity_id = self.factory.create_worker(position, player_id)
            worker_adapter = WorkerAdapter(self, entity_id)
            self.entities[entity_id] = worker_adapter
            return entity_id
        elif unit_type == "marine":
            entity_id = self.factory.create_marine(position, player_id)
            marine_adapter = UnitAdapter(self, entity_id)
            self.entities[entity_id] = marine_adapter
            return entity_id
        
        return -1
    
    def update(self, dt: float):
        """
        更新ECS世界
        
        Args:
            dt: 时间增量
        """
        self.ecs_world.process(dt)
    
    def render(self):
        """渲染所有实体（通过渲染系统自动处理）"""
        pass  # 渲染通过RenderSystem自动处理
    
    def handle_click(self, pos: Tuple[int, int], shift_held: bool = False) -> Optional[Any]:
        """
        处理鼠标点击
        
        Args:
            pos: 点击位置
            shift_held: 是否按住Shift键
            
        Returns:
            Optional[Any]: 点击的对象适配器
        """
        # 查找点击位置的实体
        clicked_entity = self._find_entity_at_position(pos)
        
        if clicked_entity:
            if not shift_held:
                # 单选
                self.selection_system.select_entity(clicked_entity)
            else:
                # 多选（目前简化为单选）
                self.selection_system.select_entity(clicked_entity)
            
            return self.entities.get(clicked_entity)
        else:
            if not shift_held:
                self.selection_system.clear_selection()
        
        return None
    
    def handle_drag_selection(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]):
        """
        处理拖拽框选
        
        Args:
            start_pos: 开始位置
            end_pos: 结束位置
        """
        self.selection_system.select_entities_in_area(start_pos, end_pos)
    
    def handle_right_click(self, pos: Tuple[int, int]):
        """
        处理右键点击
        
        Args:
            pos: 点击位置
        """
        selected_entities = self.selection_system.get_selected_entities()
        
        for entity_id in selected_entities:
            # 检查点击的是否是资源点
            target_entity = self._find_entity_at_position(pos)
            
            if target_entity:
                target_resource = self.ecs_world.get_component(target_entity, ResourcePoint)
                target_storage = self.ecs_world.get_component(target_entity, Storage)
                
                if target_resource:
                    # 点击的是资源点，命令采集
                    self._command_harvest(entity_id, target_entity)
                elif target_storage:
                    # 点击的是存储建筑，命令存储
                    self._command_store(entity_id, target_entity)
                else:
                    # 普通移动
                    self._command_move(entity_id, pos)
            else:
                # 移动到位置
                self._command_move(entity_id, pos)
    
    def _find_entity_at_position(self, pos: Tuple[int, int]) -> Optional[int]:
        """查找指定位置的实体"""
        for entity, (entity_pos, sprite) in self.ecs_world.get_components(Position, Sprite):
            if sprite.visible:
                # 检查点击是否在实体范围内
                dx = abs(pos[0] - entity_pos.x)
                dy = abs(pos[1] - entity_pos.y)
                
                if dx <= sprite.size[0] // 2 and dy <= sprite.size[1] // 2:
                    return entity
        
        return None
    
    def _command_move(self, entity_id: int, target_pos: Tuple[int, int]):
        """命令实体移动"""
        movement = self.ecs_world.get_component(entity_id, Movement)
        if movement:
            movement.target = target_pos
            movement.is_moving = True
            
            # 如果有状态机，触发移动事件
            if entity_id in self.worker_state_machines:
                sm = self.worker_state_machines[entity_id]
                if hasattr(sm, 'trigger'):
                    try:
                        sm.trigger('start_move')
                    except:
                        pass
    
    def _command_harvest(self, entity_id: int, resource_entity_id: int):
        """命令工人采集资源"""
        # 先移动到资源点附近
        resource_pos = self.ecs_world.get_component(resource_entity_id, Position)
        if resource_pos:
            self._command_move(entity_id, (resource_pos.x, resource_pos.y))
            
            # 设置目标为采集
            target = self.ecs_world.get_component(entity_id, Target)
            if target:
                target.entity = resource_entity_id
                target.target_type = "gather"
                
            # 如果有状态机，触发采集事件
            if entity_id in self.worker_state_machines:
                sm = self.worker_state_machines[entity_id]
                if hasattr(sm, 'set_target_resource'):
                    sm.set_target_resource(resource_entity_id)
                if hasattr(sm, 'trigger'):
                    try:
                        sm.trigger('start_gather')
                    except:
                        pass
    
    def _command_store(self, entity_id: int, storage_entity_id: int):
        """命令工人存储资源"""
        # 先移动到存储建筑附近
        storage_pos = self.ecs_world.get_component(storage_entity_id, Position)
        if storage_pos:
            self._command_move(entity_id, (storage_pos.x, storage_pos.y))
            
            # 设置目标为存储
            target = self.ecs_world.get_component(entity_id, Target)
            if target:
                target.entity = storage_entity_id
                target.target_type = "store"
    
    def get_selected_units(self) -> List[Any]:
        """获取当前选中的单位适配器对象"""
        selected_entities = self.selection_system.get_selected_entities()
        return [self.entities[entity_id] for entity_id in selected_entities 
                if entity_id in self.entities]

class WorkerAdapter:
    """工人单位适配器"""
    
    def __init__(self, adapter: ECSAdapter, entity_id: int):
        self.adapter = adapter
        self.entity_id = entity_id
    
    @property
    def x(self) -> float:
        pos = self.adapter.ecs_world.get_component(self.entity_id, Position)
        return pos.x if pos else 0.0
    
    @property
    def y(self) -> float:
        pos = self.adapter.ecs_world.get_component(self.entity_id, Position)
        return pos.y if pos else 0.0
    
    @property
    def selected(self) -> bool:
        selectable = self.adapter.ecs_world.get_component(self.entity_id, Selectable)
        return selectable.selected if selectable else False
    
    @property
    def health(self) -> int:
        health_comp = self.adapter.ecs_world.get_component(self.entity_id, Health)
        return health_comp.current if health_comp else 0
    
    @property
    def max_health(self) -> int:
        health_comp = self.adapter.ecs_world.get_component(self.entity_id, Health)
        return health_comp.maximum if health_comp else 0
    
    @property
    def resource_amount(self) -> int:
        resource = self.adapter.ecs_world.get_component(self.entity_id, Resource)
        return resource.amount if resource else 0
    
    @property
    def resource_capacity(self) -> int:
        resource = self.adapter.ecs_world.get_component(self.entity_id, Resource)
        return resource.capacity if resource else 0
    
    def move_to(self, x: float, y: float):
        """移动到指定位置"""
        self.adapter._command_move(self.entity_id, (x, y))
    
    def start_gather(self, resource_entity_id: int):
        """开始采集资源"""
        self.adapter._command_harvest(self.entity_id, resource_entity_id)

class BuildingAdapter:
    """建筑适配器"""
    
    def __init__(self, adapter: ECSAdapter, entity_id: int):
        self.adapter = adapter
        self.entity_id = entity_id
    
    @property
    def x(self) -> float:
        pos = self.adapter.ecs_world.get_component(self.entity_id, Position)
        return pos.x if pos else 0.0
    
    @property
    def y(self) -> float:
        pos = self.adapter.ecs_world.get_component(self.entity_id, Position)
        return pos.y if pos else 0.0
    
    @property
    def selected(self) -> bool:
        selectable = self.adapter.ecs_world.get_component(self.entity_id, Selectable)
        return selectable.selected if selectable else False
    
    def produce_worker(self) -> bool:
        """生产工人"""
        return self.adapter.production_system.add_to_production(self.entity_id, "worker")

class UnitAdapter:
    """通用单位适配器"""
    
    def __init__(self, adapter: ECSAdapter, entity_id: int):
        self.adapter = adapter
        self.entity_id = entity_id
    
    @property
    def x(self) -> float:
        pos = self.adapter.ecs_world.get_component(self.entity_id, Position)
        return pos.x if pos else 0.0
    
    @property
    def y(self) -> float:
        pos = self.adapter.ecs_world.get_component(self.entity_id, Position)
        return pos.y if pos else 0.0

class ResourcePointAdapter:
    """资源点适配器"""
    
    def __init__(self, adapter: ECSAdapter, entity_id: int):
        self.adapter = adapter
        self.entity_id = entity_id
    
    @property
    def x(self) -> float:
        pos = self.adapter.ecs_world.get_component(self.entity_id, Position)
        return pos.x if pos else 0.0
    
    @property
    def y(self) -> float:
        pos = self.adapter.ecs_world.get_component(self.entity_id, Position)
        return pos.y if pos else 0.0
    
    @property
    def amount(self) -> int:
        resource = self.adapter.ecs_world.get_component(self.entity_id, ResourcePoint)
        return resource.remaining_amount if resource else 0

__all__ = [
    'ECSAdapter',
    'WorkerAdapter', 
    'BuildingAdapter',
    'UnitAdapter',
    'ResourcePointAdapter'
]