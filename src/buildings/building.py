"""
MinSC - 基础建筑系统
实现基础Building类，支持建筑生产、选择、状态管理
"""

import pygame
import math
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

# 建筑类型枚举
class BuildingType(Enum):
    COMMAND_CENTER = "command_center"
    BARRACKS = "barracks"
    SUPPLY_DEPOT = "supply_depot"

# 建筑状态枚举
class BuildingState(Enum):
    IDLE = "idle"
    PRODUCING = "producing"
    UNDER_CONSTRUCTION = "under_construction"
    DESTROYED = "destroyed"

@dataclass
class ProductionOrder:
    """生产订单"""
    unit_type: str
    production_time: float
    cost: int
    remaining_time: float

class Building:
    """基础建筑类"""
    
    _next_id = 1  # 类变量，用于生成唯一ID
    
    def __init__(self, 
                 x: int, 
                 y: int, 
                 building_type: BuildingType,
                 player_id: int = 0):
        # 基本属性
        self.id = Building._next_id
        Building._next_id += 1
        self.x = x
        self.y = y
        self.building_type = building_type
        self.player_id = player_id
        
        # 状态管理
        self.state = BuildingState.IDLE
        self.selected = False
        self.alive = True
        
        # 基础属性（可被子类重写）
        self.max_hp = 500
        self.current_hp = self.max_hp
        self.size = 60  # 建筑通常比单位大
        self.armor = 1
        
        # 建造相关
        self.construction_time = 0.0
        self.build_progress = 1.0  # 1.0表示建造完成
        
        # 生产相关
        self.production_queue: List[ProductionOrder] = []
        self.current_production: Optional[ProductionOrder] = None
        self.max_queue_size = 5
        
        # 资源存储
        self.stored_resources = 0
        self.max_storage = 0  # 0表示不存储资源
        
        # 渲染属性
        self.color = self._get_building_color()
        self.selected_color = (255, 255, 0)  # 黄色选择框
        
    def _get_building_color(self) -> tuple[int, int, int]:
        """根据玩家ID和建筑类型获取颜色"""
        base_colors = {
            0: (0, 150, 200),    # 深蓝色 - 玩家1
            1: (200, 100, 0),    # 深红色 - 玩家2
        }
        return base_colors.get(self.player_id, (100, 100, 100))
    
    def get_position(self) -> tuple[int, int]:
        """获取建筑位置"""
        return (int(self.x), int(self.y))
    
    def get_center(self) -> tuple[int, int]:
        """获取建筑中心点"""
        return (int(self.x + self.size // 2), int(self.y + self.size // 2))
    
    def distance_to(self, target_x: int, target_y: int) -> float:
        """计算到目标位置的距离"""
        center_x, center_y = self.get_center()
        dx = target_x - center_x
        dy = target_y - center_y
        return math.sqrt(dx * dx + dy * dy)
    
    def can_produce(self, unit_type: str) -> bool:
        """检查是否可以生产指定单位类型"""
        # 基类返回False，由子类重写
        return False
    
    def add_production_order(self, unit_type: str, cost: int = 0) -> bool:
        """添加生产订单"""
        if not self.can_produce(unit_type):
            return False
            
        if len(self.production_queue) >= self.max_queue_size:
            return False
        
        # 获取生产时间（由子类定义）
        production_time = self._get_production_time(unit_type)
        if production_time <= 0:
            return False
        
        order = ProductionOrder(
            unit_type=unit_type,
            production_time=production_time,
            cost=cost,
            remaining_time=production_time
        )
        
        self.production_queue.append(order)
        
        # 如果当前没有生产，立即开始
        if self.current_production is None and self.state == BuildingState.IDLE:
            self._start_next_production()
        
        return True
    
    def _get_production_time(self, unit_type: str) -> float:
        """获取单位生产时间（由子类重写）"""
        production_times = {
            "worker": 5.0,
            "warrior": 8.0,
        }
        return production_times.get(unit_type, 0.0)
    
    def _start_next_production(self):
        """开始下一个生产"""
        if self.production_queue and self.current_production is None:
            self.current_production = self.production_queue.pop(0)
            self.state = BuildingState.PRODUCING
            print(f"🏭 {self.building_type.value} 开始生产 {self.current_production.unit_type}")
    
    def update(self, dt: float):
        """更新建筑状态"""
        if not self.alive:
            return
        
        # 更新建造进度
        if self.state == BuildingState.UNDER_CONSTRUCTION:
            self._update_construction(dt)
        
        # 更新生产进度
        elif self.state == BuildingState.PRODUCING:
            self._update_production(dt)
    
    def _update_construction(self, dt: float):
        """更新建造进度"""
        if self.build_progress < 1.0:
            # 建造速度：每秒10%
            self.build_progress += dt * 0.1
            if self.build_progress >= 1.0:
                self.build_progress = 1.0
                self.state = BuildingState.IDLE
                print(f"🏗️ {self.building_type.value} 建造完成")
    
    def _update_production(self, dt: float):
        """更新生产进度"""
        if not self.current_production:
            return
        
        self.current_production.remaining_time -= dt
        
        if self.current_production.remaining_time <= 0:
            # 生产完成
            self._complete_production()
    
    def _complete_production(self):
        """完成生产"""
        if not self.current_production:
            return None
        
        # 在建筑附近生成单位
        spawn_x, spawn_y = self._get_spawn_position()
        unit_info = self._create_unit(self.current_production.unit_type, spawn_x, spawn_y)
        
        print(f"✅ {self.building_type.value} 完成生产 {self.current_production.unit_type}")
        
        self.current_production = None
        self.state = BuildingState.IDLE
        
        # 开始下一个生产
        self._start_next_production()
        
        return unit_info
    
    def _get_spawn_position(self) -> tuple[int, int]:
        """获取单位生成位置（建筑下方）"""
        spawn_x = self.x + self.size // 2 - 10  # 单位大小的一半
        spawn_y = self.y + self.size + 10
        return (spawn_x, spawn_y)
    
    def _create_unit(self, unit_type: str, x: int, y: int):
        """创建单位（由子类重写或游戏管理器处理）"""
        # 这里返回单位信息，由游戏管理器实际创建单位
        return {
            "type": unit_type,
            "position": (x, y),
            "player_id": self.player_id
        }
    
    def store_resources(self, amount: int) -> int:
        """存储资源，返回实际存储的数量"""
        if self.max_storage <= 0:
            return 0
        
        available_space = self.max_storage - self.stored_resources
        stored = min(amount, available_space)
        self.stored_resources += stored
        return stored
    
    def select(self):
        """选择建筑"""
        self.selected = True
    
    def deselect(self):
        """取消选择建筑"""
        self.selected = False
    
    def contains_point(self, x: int, y: int) -> bool:
        """检查点是否在建筑内"""
        return (self.x <= x <= self.x + self.size and
                self.y <= y <= self.y + self.size)
    
    def take_damage(self, damage: int):
        """受到伤害"""
        actual_damage = max(1, damage - self.armor)
        self.current_hp -= actual_damage
        
        if self.current_hp <= 0:
            self.current_hp = 0
            self.alive = False
            self.state = BuildingState.DESTROYED
    
    def repair(self, amount: int):
        """修理"""
        if self.state != BuildingState.DESTROYED:
            self.current_hp = min(self.current_hp + amount, self.max_hp)
    
    def render(self, screen: pygame.Surface):
        """渲染建筑"""
        if not self.alive:
            return
        
        # 渲染建筑主体
        color = self.color
        if self.state == BuildingState.UNDER_CONSTRUCTION:
            # 建造中使用更暗的颜色
            color = tuple(int(c * 0.6) for c in self.color)
        
        pygame.draw.rect(screen, color, 
                        (self.x, self.y, self.size, self.size))
        
        # 渲染边框
        border_color = (255, 255, 255) if not self.selected else self.selected_color
        pygame.draw.rect(screen, border_color,
                        (self.x, self.y, self.size, self.size), 2)
        
        # 渲染选择框
        if self.selected:
            pygame.draw.rect(screen, self.selected_color,
                           (self.x - 3, self.y - 3, self.size + 6, self.size + 6), 3)
        
        # 渲染血条
        if self.current_hp < self.max_hp:
            self._render_health_bar(screen)
        
        # 渲染建造进度
        if self.state == BuildingState.UNDER_CONSTRUCTION:
            self._render_construction_progress(screen)
        
        # 渲染生产进度
        if self.state == BuildingState.PRODUCING:
            self._render_production_progress(screen)
    
    def _render_health_bar(self, screen: pygame.Surface):
        """渲染血条"""
        bar_width = self.size
        bar_height = 6
        bar_y = self.y - 12
        
        # 背景
        pygame.draw.rect(screen, (255, 0, 0),
                        (self.x, bar_y, bar_width, bar_height))
        
        # 血量
        health_ratio = self.current_hp / self.max_hp
        health_width = int(bar_width * health_ratio)
        pygame.draw.rect(screen, (0, 255, 0),
                        (self.x, bar_y, health_width, bar_height))
    
    def _render_construction_progress(self, screen: pygame.Surface):
        """渲染建造进度"""
        bar_width = self.size
        bar_height = 4
        bar_y = self.y + self.size + 5
        
        # 背景
        pygame.draw.rect(screen, (100, 100, 100),
                        (self.x, bar_y, bar_width, bar_height))
        
        # 进度
        progress_width = int(bar_width * self.build_progress)
        pygame.draw.rect(screen, (0, 255, 255),
                        (self.x, bar_y, progress_width, bar_height))
    
    def _render_production_progress(self, screen: pygame.Surface):
        """渲染生产进度"""
        if not self.current_production:
            return
        
        bar_width = self.size
        bar_height = 4
        bar_y = self.y + self.size + 5
        
        # 背景
        pygame.draw.rect(screen, (100, 100, 100),
                        (self.x, bar_y, bar_width, bar_height))
        
        # 进度
        progress_ratio = 1.0 - (self.current_production.remaining_time / self.current_production.production_time)
        progress_width = int(bar_width * progress_ratio)
        pygame.draw.rect(screen, (255, 255, 0),
                        (self.x, bar_y, progress_width, bar_height))
    
    def get_info(self) -> dict:
        """获取建筑信息"""
        info = {
            "id": id(self),
            "type": self.building_type.value,
            "player": self.player_id,
            "position": self.get_position(),
            "hp": f"{self.current_hp}/{self.max_hp}",
            "state": self.state.value,
            "selected": self.selected
        }
        
        if self.current_production:
            info["producing"] = self.current_production.unit_type
            info["production_progress"] = f"{self.current_production.production_time - self.current_production.remaining_time:.1f}s/{self.current_production.production_time}s"
        
        if self.production_queue:
            info["queue_size"] = len(self.production_queue)
        
        if self.max_storage > 0:
            info["resources"] = f"{self.stored_resources}/{self.max_storage}"
        
        return info
    
    def __str__(self):
        return f"{self.building_type.value}({self.player_id}) at ({self.x}, {self.y})"