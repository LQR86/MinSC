"""
资源管理服务实现
"""
from typing import List, Optional, Tuple, TYPE_CHECKING
import math
from ioc.services import IResourceManagerService

if TYPE_CHECKING:
    from engine.map import ResourcePoint
    from ioc.services import IGameStateService, IEventBusService


class ResourceManagerService:
    """资源管理服务实现"""
    
    def __init__(self, 
                 game_state: 'IGameStateService',
                 event_bus: 'IEventBusService'):
        self.game_state = game_state
        self.event_bus = event_bus
    
    def get_resource_points(self) -> List['ResourcePoint']:
        """获取所有资源点"""
        game_state = self.game_state.get_game_state()
        if hasattr(game_state, 'game_manager') and hasattr(game_state.game_manager, 'game_map'):
            return game_state.game_manager.game_map.resource_points
        return []
    
    def find_nearest_resource(self, 
                            position: Tuple[float, float],
                            resource_type: Optional[str] = None) -> Optional['ResourcePoint']:
        """找到最近的资源点"""
        x, y = position
        resource_points = self.get_resource_points()
        
        nearest_resource = None
        min_distance = float('inf')
        
        for resource in resource_points:
            if self.is_resource_available(resource):
                distance = math.sqrt((x - resource.x) ** 2 + (y - resource.y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_resource = resource
        
        return nearest_resource
    
    def is_resource_available(self, resource_point: 'ResourcePoint') -> bool:
        """检查资源点是否可用"""
        return resource_point.resource_amount > 0