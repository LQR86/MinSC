"""
ECS 系统定义

定义所有游戏逻辑系统。
系统包含逻辑，处理具有特定组件的实体。
"""

import esper
import pygame
from typing import List, Tuple, Optional
import math
import logging

# 导入组件
from .components import (
    Position, Velocity, Movement, Health, Sprite, Selectable,
    Resource, ResourcePoint, Storage, ProductionQueue, Building,
    StateMachine, UnitInfo, Target, Collider
)

# ============================================================================
# 移动系统
# ============================================================================

class MovementSystem(esper.Processor):
    """
    移动系统 - 处理实体的移动逻辑
    """
    
    def process(self, dt: float):
        """处理所有具有位置和移动组件的实体"""
        for entity, (pos, movement) in esper.get_components(Position, Movement):
            if not movement.is_moving or movement.target is None:
                continue
            
            # 计算到目标的距离
            target_x, target_y = movement.target
            dx = target_x - pos.x
            dy = target_y - pos.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # 检查是否到达目标
            if distance < 5.0:  # 5像素的容差
                pos.x = target_x
                pos.y = target_y
                movement.is_moving = False
                movement.target = None
                
                # 触发移动完成事件
                self._on_movement_complete(entity)
                continue
            
            # 移动向目标
            if distance > 0:
                move_distance = movement.speed * dt
                move_ratio = min(move_distance / distance, 1.0)
                
                pos.x += dx * move_ratio
                pos.y += dy * move_ratio
    
    def _on_movement_complete(self, entity: int):
        """移动完成时的回调"""
        # 如果实体有状态机，触发到达事件
        try:
            state_machine_comp = esper.component_for_entity(entity, StateMachine)
            if state_machine_comp:
                state_machine_comp.trigger('arrive')
        except KeyError:
            pass
        
        logging.debug(f"🚶 实体 {entity} 移动完成")

# ============================================================================
# 渲染系统
# ============================================================================

class RenderSystem(esper.Processor):
    """
    渲染系统 - 处理实体的渲染
    """
    
    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.screen = screen
    
    def process(self, dt: float):
        """渲染所有具有位置和精灵组件的实体"""
        # 按层级排序渲染
        entities_to_render = []
        
        for entity, (pos, sprite) in esper.get_components(Position, Sprite):
            if sprite.visible:
                entities_to_render.append((sprite.layer, entity, pos, sprite))
        
        # 按层级排序
        entities_to_render.sort(key=lambda x: x[0])
        
        # 渲染实体
        for layer, entity, pos, sprite in entities_to_render:
            self._render_entity(entity, pos, sprite)
    
    def _render_entity(self, entity: int, pos: Position, sprite: Sprite):
        """渲染单个实体"""
        rect = pygame.Rect(
            int(pos.x - sprite.size[0] // 2),
            int(pos.y - sprite.size[1] // 2),
            sprite.size[0],
            sprite.size[1]
        )
        pygame.draw.rect(self.screen, sprite.color, rect)
        
        # 渲染选择框
        try:
            selectable = esper.component_for_entity(entity, Selectable)
            if selectable and selectable.selected:
                pygame.draw.rect(self.screen, (255, 255, 0), rect, 2)
        except KeyError:
            pass
        
        # 渲染血条
        try:
            health = esper.component_for_entity(entity, Health)
            if health and health.current < health.maximum:
                self._render_health_bar(pos, health)
        except KeyError:
            pass
        
        # 渲染资源指示器
        try:
            resource = esper.component_for_entity(entity, Resource)
            if resource and resource.amount > 0:
                self._render_resource_indicator(pos, resource)
        except KeyError:
            pass
    
    def _render_health_bar(self, pos: Position, health: Health):
        """渲染血条"""
        bar_width = 30
        bar_height = 4
        bar_x = int(pos.x - bar_width // 2)
        bar_y = int(pos.y - 25)
        
        # 背景
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (60, 60, 60), bg_rect)
        
        # 血量
        health_ratio = health.health_percentage()
        health_width = int(bar_width * health_ratio)
        health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
        
        # 血量颜色
        if health_ratio > 0.6:
            color = (0, 200, 0)  # 绿色
        elif health_ratio > 0.3:
            color = (255, 255, 0)  # 黄色
        else:
            color = (255, 0, 0)  # 红色
        
        pygame.draw.rect(self.screen, color, health_rect)
    
    def _render_resource_indicator(self, pos: Position, resource: Resource):
        """渲染资源指示器"""
        indicator_size = 6
        indicator_x = int(pos.x + 15)
        indicator_y = int(pos.y - 15)
        
        # 根据资源量确定颜色
        fill_ratio = resource.amount / resource.capacity
        if fill_ratio < 0.3:
            color = (255, 255, 0)  # 黄色
        elif fill_ratio < 0.7:
            color = (255, 165, 0)  # 橙色
        else:
            color = (255, 0, 0)    # 红色
        
        pygame.draw.circle(self.screen, color, (indicator_x, indicator_y), indicator_size)

# ============================================================================
# 选择系统
# ============================================================================

class SelectionSystem(esper.Processor):
    """
    选择系统 - 处理实体的选择逻辑
    """
    
    def __init__(self):
        super().__init__()
        self.selected_entities: List[int] = []
    
    def select_entity(self, entity: int):
        """选择实体"""
        # 取消之前的选择
        self.clear_selection()
        
        try:
            selectable = esper.component_for_entity(entity, Selectable)
            if selectable:
                selectable.selected = True
                self.selected_entities.append(entity)
                logging.debug(f"🎯 选择实体 {entity}")
        except KeyError:
            pass
    
    def select_entities_in_area(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float]):
        """在区域内选择实体"""
        # 取消之前的选择
        self.clear_selection()
        
        # 计算选择矩形
        min_x = min(start_pos[0], end_pos[0])
        max_x = max(start_pos[0], end_pos[0])
        min_y = min(start_pos[1], end_pos[1])
        max_y = max(start_pos[1], end_pos[1])
        
        # 查找在区域内的可选择实体
        for entity, (pos, selectable) in esper.get_components(Position, Selectable):
            if min_x <= pos.x <= max_x and min_y <= pos.y <= max_y:
                selectable.selected = True
                self.selected_entities.append(entity)
        
        logging.debug(f"🎯 区域选择了 {len(self.selected_entities)} 个实体")
    
    def clear_selection(self):
        """清除所有选择"""
        for entity in self.selected_entities:
            try:
                selectable = esper.component_for_entity(entity, Selectable)
                if selectable:
                    selectable.selected = False
            except KeyError:
                pass
        
        self.selected_entities.clear()
    
    def get_selected_entities(self) -> List[int]:
        """获取当前选择的实体"""
        return self.selected_entities.copy()
    
    def process(self, dt: float):
        """选择系统不需要每帧处理"""
        pass

# ============================================================================
# 资源系统
# ============================================================================

class ResourceSystem(esper.Processor):
    """
    资源系统 - 处理资源采集和存储逻辑
    """
    
    def harvest_resource(self, harvester_entity: int, resource_entity: int) -> bool:
        """
        采集资源
        
        Args:
            harvester_entity: 采集者实体ID
            resource_entity: 资源点实体ID
            
        Returns:
            bool: 是否成功采集
        """
        # 获取组件
        try:
            harvester_resource = esper.component_for_entity(harvester_entity, Resource)
            resource_point = esper.component_for_entity(resource_entity, ResourcePoint)
        except KeyError:
            return False
        
        if not harvester_resource or not resource_point:
            return False
        
        if harvester_resource.is_full() or resource_point.is_depleted():
            return False
        
        # 计算可采集的数量
        can_harvest = min(
            harvester_resource.capacity - harvester_resource.amount,
            resource_point.remaining_amount,
            resource_point.depletion_rate
        )
        
        if can_harvest > 0:
            # 执行采集
            harvested = resource_point.harvest(can_harvest)
            harvester_resource.add(harvested)
            
            logging.debug(f"⛏️ 实体 {harvester_entity} 从资源点 {resource_entity} 采集了 {harvested} 资源")
            return True
        
        return False
    
    def store_resource(self, carrier_entity: int, storage_entity: int) -> bool:
        """
        存储资源
        
        Args:
            carrier_entity: 携带者实体ID
            storage_entity: 存储建筑实体ID
            
        Returns:
            bool: 是否成功存储
        """
        # 获取组件
        try:
            carrier_resource = esper.component_for_entity(carrier_entity, Resource)
            storage = esper.component_for_entity(storage_entity, Storage)
        except KeyError:
            return False
        
        if not carrier_resource or not storage:
            return False
        
        if carrier_resource.is_empty() or storage.is_full():
            return False
        
        # 执行存储
        amount_to_store = carrier_resource.amount
        stored = storage.store(amount_to_store)
        carrier_resource.remove(stored)
        
        logging.debug(f"📦 实体 {carrier_entity} 向建筑 {storage_entity} 存储了 {stored} 资源")
        return True
    
    def process(self, dt: float):
        """资源系统不需要每帧处理"""
        pass

# ============================================================================
# 生产系统
# ============================================================================

class ProductionSystem(esper.Processor):
    """
    生产系统 - 处理单位生产逻辑
    """
    
    def __init__(self, unit_factory=None):
        super().__init__()
        self.unit_factory = unit_factory  # 单位工厂函数
        self.production_times = {
            'worker': 3.0,  # 工人生产时间3秒
            'marine': 5.0,  # 士兵生产时间5秒
        }
    
    def process(self, dt: float):
        """处理所有生产队列"""
        for entity, (production, building) in esper.get_components(ProductionQueue, Building):
            if not building.is_constructed or production.is_empty():
                continue
            
            # 获取当前生产项目
            current_item = production.current_item()
            if not current_item:
                continue
            
            # 更新生产进度
            production_time = self.production_times.get(current_item, 1.0)
            progress_delta = (dt * production.production_speed) / production_time
            production.current_progress += progress_delta
            
            # 检查是否完成生产
            if production.current_progress >= 1.0:
                self._complete_production(entity, production, current_item)
    
    def _complete_production(self, producer_entity: int, production: ProductionQueue, unit_type: str):
        """完成生产"""
        # 移除队列中的第一个项目
        production.queue.pop(0)
        production.current_progress = 0.0
        
        # 创建新单位
        if self.unit_factory:
            # 获取生产者位置
            try:
                producer_pos = esper.component_for_entity(producer_entity, Position)
                if producer_pos:
                    spawn_pos = (producer_pos.x + 50, producer_pos.y + 50)  # 在建筑旁边生成
                    
                    # 获取生产者的玩家ID
                    producer_info = esper.component_for_entity(producer_entity, UnitInfo)
                    player_id = producer_info.player_id if producer_info else 0
                    
                    # 创建新单位
                    new_entity = self.unit_factory(unit_type, spawn_pos, player_id)
                    
                    logging.info(f"🏭 实体 {producer_entity} 生产完成 {unit_type}，新实体ID: {new_entity}")
            except KeyError:
                pass
    
    def add_to_production(self, producer_entity: int, unit_type: str) -> bool:
        """添加单位到生产队列"""
        try:
            production = esper.component_for_entity(producer_entity, ProductionQueue)
            if production:
                success = production.add_to_queue(unit_type)
                if success:
                    logging.debug(f"📋 实体 {producer_entity} 添加 {unit_type} 到生产队列")
                return success
        except KeyError:
            pass
        return False

# ============================================================================
# 状态机系统
# ============================================================================

class StateMachineSystem(esper.Processor):
    """
    状态机系统 - 更新所有实体的状态机
    """
    
    def process(self, dt: float):
        """更新所有状态机"""
        for entity, (state_machine,) in esper.get_components(StateMachine):
            if hasattr(state_machine.state_machine, 'update'):
                state_machine.state_machine.update(dt)
                # 更新当前状态
                if hasattr(state_machine.state_machine, 'state'):
                    state_machine.current_state = state_machine.state_machine.state

# ============================================================================
# 导出所有系统
# ============================================================================

__all__ = [
    'MovementSystem',
    'RenderSystem', 
    'SelectionSystem',
    'ResourceSystem',
    'ProductionSystem',
    'StateMachineSystem'
]