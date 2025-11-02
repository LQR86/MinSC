"""
MinSC - 指挥中心
实现CommandCenter类，作为主基地，能生产工人并存储资源
"""

import pygame
from typing import Optional, TYPE_CHECKING
from .building import Building, BuildingType, BuildingState

if TYPE_CHECKING:
    from ..units.worker import Worker

class CommandCenter(Building):
    """指挥中心 - 主基地建筑"""
    
    def __init__(self, x: int, y: int, player_id: int = 0):
        super().__init__(x, y, BuildingType.COMMAND_CENTER, player_id)
        
        # 指挥中心特有属性
        self.max_hp = 800
        self.current_hp = self.max_hp
        self.size = 80
        self.armor = 2
        
        # 资源存储
        self.max_storage = 500
        self.stored_resources = 0
        
        # 生产能力
        self.max_queue_size = 5
        
        # 工人生成位置偏移
        self.spawn_offsets = [
            (0, 85),    # 正下方
            (-30, 85),  # 左下
            (30, 85),   # 右下
            (-60, 50),  # 左侧
            (60, 50)    # 右侧
        ]
        self.current_spawn_index = 0
        
    def can_produce(self, unit_type: str) -> bool:
        """检查是否可以生产指定单位类型"""
        # 指挥中心只能生产工人
        return unit_type == "worker"
    
    def _get_production_time(self, unit_type: str) -> float:
        """获取单位生产时间"""
        production_times = {
            "worker": 3.0,  # 工人生产较快
        }
        return production_times.get(unit_type, 0.0)
    
    def _get_spawn_position(self) -> tuple[int, int]:
        """获取单位生成位置（循环使用不同位置避免重叠）"""
        offset_x, offset_y = self.spawn_offsets[self.current_spawn_index]
        self.current_spawn_index = (self.current_spawn_index + 1) % len(self.spawn_offsets)
        
        spawn_x = self.x + self.size // 2 + offset_x
        spawn_y = self.y + offset_y
        
        # 确保在地图范围内
        spawn_x = max(20, min(spawn_x, 1000))  # 假设地图宽度1024
        spawn_y = max(20, min(spawn_y, 740))   # 假设地图高度768
        
        return (spawn_x, spawn_y)
    
    def accept_resources(self, worker: 'Worker') -> int:
        """接受工人卸载的资源"""
        if not worker or worker.carrying_resources <= 0:
            return 0
        
        # 检查玩家所有权 - 只有同一玩家的工人才能卸载资源
        if worker.player_id != self.player_id:
            print(f"⚠️ 工人{worker.id} 不能在敌方基地{self.id} 卸载资源")
            return 0
        
        # 计算可以存储的资源量
        available_space = self.max_storage - self.stored_resources
        resources_to_store = min(worker.carrying_resources, available_space)
        
        if resources_to_store > 0:
            # 存储资源
            self.stored_resources += resources_to_store
            
            # 工人卸载资源
            worker.carrying_resources -= resources_to_store
            
            print(f"📦 指挥中心{self.id} 接受了 {resources_to_store} 资源 (总计: {self.stored_resources}/{self.max_storage})")
            
            return resources_to_store
        
        return 0
    
    def can_accept_resources(self) -> bool:
        """检查是否可以接受资源"""
        return self.stored_resources < self.max_storage
    
    def produce_worker(self) -> bool:
        """生产工人的便捷方法"""
        return self.add_production_order("worker", cost=50)
    
    def render(self, screen: pygame.Surface):
        """渲染指挥中心"""
        super().render(screen)
        
        # 渲染指挥中心标识
        if self.alive and self.build_progress >= 1.0:
            # 在中心绘制指挥中心图标
            center_x, center_y = self.get_center()
            
            # 绘制十字标记
            cross_size = 15
            pygame.draw.line(screen, (255, 255, 255),
                           (center_x - cross_size, center_y),
                           (center_x + cross_size, center_y), 3)
            pygame.draw.line(screen, (255, 255, 255),
                           (center_x, center_y - cross_size),
                           (center_x, center_y + cross_size), 3)
            
            # 绘制外圈
            pygame.draw.circle(screen, (255, 255, 255), 
                             (center_x, center_y), cross_size + 5, 2)
    
    def get_info(self) -> dict:
        """获取指挥中心信息"""
        info = super().get_info()
        info.update({
            "resources_stored": f"{self.stored_resources}/{self.max_storage}",
            "can_produce": "Worker",
            "storage_full": self.stored_resources >= self.max_storage
        })
        return info