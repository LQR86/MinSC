"""
MinSC Map System - 地图系统
处理地图生成、资源点分布和地形管理
"""

import pygame
import random
import math
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class TerrainType(Enum):
    """地形类型"""
    EMPTY = "empty"
    RESOURCE = "resource"
    OBSTACLE = "obstacle"

@dataclass
class ResourcePoint:
    """资源点数据类"""
    x: int
    y: int
    resource_type: str = "mineral"
    amount: int = 1000
    max_amount: int = 1000
    size: int = 15  # 资源点大小/半径
    id: int = 0  # 资源点ID
    
    def __post_init__(self):
        """初始化后设置ID"""
        if self.id == 0:
            self.id = ResourcePoint._get_next_id()
    
    _next_id = 1
    
    @classmethod
    def _get_next_id(cls):
        current_id = cls._next_id
        cls._next_id += 1
        return current_id
    
    @property
    def is_depleted(self) -> bool:
        """资源是否枯竭"""
        return self.amount <= 0
    
    @property
    def depletion_ratio(self) -> float:
        """枯竭比例 (0.0 = 空, 1.0 = 满)"""
        return self.amount / self.max_amount if self.max_amount > 0 else 0.0

class Map:
    """MinSC地图类"""
    
    def __init__(self, 
                 width: int = 1024, 
                 height: int = 768,
                 resource_count: int = 8):
        """
        初始化地图
        
        Args:
            width: 地图宽度(像素)
            height: 地图高度(像素)
            resource_count: 资源点数量
        """
        self.width = width
        self.height = height
        self.resource_count = resource_count
        
        # 地图数据
        self.resource_points: List[ResourcePoint] = []
        
        # 渲染相关
        self.background_color = (20, 40, 20)  # 深绿色背景
        self.resource_color = (255, 255, 0)   # 黄色资源点
        self.grid_color = (40, 60, 40)        # 网格线颜色
        
        # 生成地图内容
        self.generate_resources()
        
        print(f"✅ 地图初始化完成: {width}x{height}, {len(self.resource_points)}个资源点")
    
    def generate_resources(self) -> None:
        """生成资源点分布"""
        self.resource_points.clear()
        
        # 资源点最小间距
        min_distance = 100
        
        attempts = 0
        max_attempts = 1000
        
        while len(self.resource_points) < self.resource_count and attempts < max_attempts:
            attempts += 1
            
            # 随机生成位置
            x = random.randint(50, self.width - 50)
            y = random.randint(50, self.height - 50)
            
            # 检查与现有资源点的距离
            too_close = False
            for existing in self.resource_points:
                distance = ((x - existing.x) ** 2 + (y - existing.y) ** 2) ** 0.5
                if distance < min_distance:
                    too_close = True
                    break
            
            if not too_close:
                # 创建资源点
                amount = random.randint(800, 1200)
                resource_point = ResourcePoint(x=x, y=y, amount=amount, max_amount=amount)
                self.resource_points.append(resource_point)
                print(f"  生成资源点: ({x}, {y}) - {amount}单位")
    
    def get_resource_at(self, x: int, y: int, radius: int = 20) -> Optional[ResourcePoint]:
        """
        获取指定位置的资源点
        
        Args:
            x: X坐标
            y: Y坐标
            radius: 检测半径
            
        Returns:
            ResourcePoint或None
        """
        for resource in self.resource_points:
            distance = ((x - resource.x) ** 2 + (y - resource.y) ** 2) ** 0.5
            if distance <= radius:
                return resource
        return None
    
    def get_resource_at_position(self, x: int, y: int) -> Optional[ResourcePoint]:
        """获取指定位置的资源点"""
        for resource in self.resource_points:
            distance = math.sqrt((x - resource.x) ** 2 + (y - resource.y) ** 2)
            if distance <= resource.size:
                return resource
        return None
    
    def harvest_resource(self, x: int, y: int, amount: int = 1) -> int:
        """
        采集资源
        
        Args:
            x: X坐标
            y: Y坐标
            amount: 尝试采集的数量
            
        Returns:
            实际采集到的数量
        """
        resource = self.get_resource_at(x, y)
        if not resource or resource.is_depleted:
            return 0
        
        # 计算实际采集量
        harvested = min(amount, resource.amount)
        resource.amount -= harvested
        
        return harvested
    
    def render(self, screen: pygame.Surface) -> None:
        """
        渲染地图
        
        Args:
            screen: Pygame屏幕表面
        """
        # 绘制背景
        screen.fill(self.background_color)
        
        # 绘制网格线（可选）
        self._draw_grid(screen)
        
        # 绘制资源点
        self._draw_resources(screen)
    
    def _draw_grid(self, screen: pygame.Surface, grid_size: int = 50) -> None:
        """绘制网格线"""
        for x in range(0, self.width, grid_size):
            pygame.draw.line(screen, self.grid_color, (x, 0), (x, self.height), 1)
        
        for y in range(0, self.height, grid_size):
            pygame.draw.line(screen, self.grid_color, (0, y), (self.width, y), 1)
    
    def _draw_resources(self, screen: pygame.Surface) -> None:
        """绘制资源点"""
        for resource in self.resource_points:
            if resource.is_depleted:
                continue
            
            # 根据资源剩余量调整颜色强度
            intensity = resource.depletion_ratio
            color = (
                int(255 * intensity),
                int(255 * intensity),
                0
            )
            
            # 绘制资源点
            radius = 15
            pygame.draw.circle(screen, color, (resource.x, resource.y), radius)
            pygame.draw.circle(screen, (255, 255, 255), (resource.x, resource.y), radius, 2)
            
            # 绘制资源数量文本
            font = pygame.font.Font(None, 24)
            text = font.render(str(resource.amount), True, (255, 255, 255))
            text_rect = text.get_rect(center=(resource.x, resource.y - 25))
            screen.blit(text, text_rect)

if __name__ == "__main__":
    # 测试地图系统
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("MinSC Map Test")
    clock = pygame.time.Clock()
    
    # 创建地图
    game_map = Map()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 点击鼠标测试资源采集
                mx, my = pygame.mouse.get_pos()
                harvested = game_map.harvest_resource(mx, my, 50)
                if harvested > 0:
                    print(f"采集到 {harvested} 单位资源")
        
        # 渲染地图
        game_map.render(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()