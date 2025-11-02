"""
简化的建筑管理器 - 直接解决WorkerStateMachine基地查找问题
"""
from typing import List, Optional, Tuple
import math


class SimpleBuildingManager:
    """简化的建筑管理器"""
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
    
    def find_nearest_command_center(self, worker_pos: Tuple[float, float], player_id: int):
        """找到最近的己方指挥中心"""
        x, y = worker_pos
        nearest_building = None
        min_distance = float('inf')
        
        for building in self.game_manager.buildings:
            # 检查是否是己方指挥中心
            if (hasattr(building, 'building_type') and 
                hasattr(building, 'player_id') and
                building.player_id == player_id and
                building.alive):
                
                # 检查建筑类型
                building_type_value = getattr(building.building_type, 'value', str(building.building_type))
                if building_type_value == 'command_center':
                    # 计算距离
                    building_center_x = building.x + building.size // 2
                    building_center_y = building.y + building.size // 2
                    distance = math.sqrt((x - building_center_x) ** 2 + (y - building_center_y) ** 2)
                    
                    if distance < min_distance:
                        min_distance = distance
                        nearest_building = building
        
        return nearest_building