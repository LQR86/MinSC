"""
建筑管理服务实现

解决 WorkerStateMachine 需要访问建筑列表的问题
"""
from typing import List, Optional, Tuple, TYPE_CHECKING
import math

from ioc.services import IBuildingManagerService, BuildingType

if TYPE_CHECKING:
    from buildings.building import Building
    from ioc.services import IGameStateService, IEventBusService, ILoggingService


class BuildingManagerService:
    """建筑管理服务实现"""
    
    def __init__(self, 
                 game_state: 'IGameStateService',
                 event_bus: 'IEventBusService',
                 logging: 'ILoggingService'):
        self.game_state = game_state
        self.event_bus = event_bus
        self.logging = logging
        
        # 缓存建筑列表，提高性能
        self._buildings_cache: List['Building'] = []
        self._cache_dirty = True
        
        # 订阅建筑变更事件
        self.event_bus.subscribe('building_created', self._on_building_created)
        self.event_bus.subscribe('building_destroyed', self._on_building_destroyed)
    
    def get_buildings_by_player(self, player_id: int) -> List['Building']:
        """获取指定玩家的所有建筑"""
        self._refresh_cache_if_needed()
        return [b for b in self._buildings_cache if b.player_id == player_id]
    
    def find_nearest_building(self, 
                            position: Tuple[float, float], 
                            building_type: BuildingType,
                            player_id: int) -> Optional['Building']:
        """找到最近的指定类型建筑 - 解决 WorkerStateMachine 基地查找问题"""
        self.logging.debug(f"寻找最近建筑: 位置{position}, 类型{building_type.value}, 玩家{player_id}")
        
        candidate_buildings = []
        player_buildings = self.get_buildings_by_player(player_id)
        
        for building in player_buildings:
            # 检查建筑类型
            if self._matches_building_type(building, building_type):
                # 检查建筑是否可用
                if self._is_building_available(building):
                    candidate_buildings.append(building)
        
        if not candidate_buildings:
            self.logging.debug(f"未找到可用的{building_type.value}建筑")
            return None
        
        # 找到最近的建筑
        x, y = position
        nearest_building = None
        min_distance = float('inf')
        
        for building in candidate_buildings:
            # 计算到建筑中心的距离
            building_center_x = building.x + building.size // 2
            building_center_y = building.y + building.size // 2
            
            distance = math.sqrt((x - building_center_x) ** 2 + (y - building_center_y) ** 2)
            
            if distance < min_distance:
                min_distance = distance
                nearest_building = building
        
        if nearest_building:
            self.logging.debug(f"找到最近建筑: ID{nearest_building.id}, 距离{min_distance:.1f}")
        
        return nearest_building
    
    def get_buildings_in_range(self, 
                             center: Tuple[float, float], 
                             radius: float,
                             player_id: Optional[int] = None) -> List['Building']:
        """获取范围内的建筑"""
        self._refresh_cache_if_needed()
        
        x, y = center
        buildings_in_range = []
        
        for building in self._buildings_cache:
            # 如果指定了玩家ID，过滤掉其他玩家的建筑
            if player_id is not None and building.player_id != player_id:
                continue
            
            # 计算距离
            building_center_x = building.x + building.size // 2
            building_center_y = building.y + building.size // 2
            distance = math.sqrt((x - building_center_x) ** 2 + (y - building_center_y) ** 2)
            
            if distance <= radius:
                buildings_in_range.append(building)
        
        return buildings_in_range
    
    def can_building_accept_resources(self, building: 'Building') -> bool:
        """检查建筑是否可以接受资源"""
        # 检查建筑是否活着
        if not building.alive:
            return False
        
        # 检查建筑是否有接受资源的方法
        if hasattr(building, 'can_accept_resources'):
            return building.can_accept_resources()
        
        # 对于指挥中心，默认可以接受资源
        if hasattr(building, 'building_type'):
            return building.building_type.value == 'command_center'
        
        return False
    
    def _refresh_cache_if_needed(self):
        """如果需要，刷新建筑缓存"""
        if self._cache_dirty:
            self._refresh_cache()
    
    def _refresh_cache(self):
        """刷新建筑缓存"""
        try:
            # 从游戏状态获取建筑列表
            game_state = self.game_state.get_game_state()
            if hasattr(game_state, 'buildings'):
                self._buildings_cache = game_state.buildings[:]
                self._cache_dirty = False
                self.logging.debug(f"建筑缓存已刷新: {len(self._buildings_cache)}个建筑")
        except Exception as e:
            self.logging.error(f"刷新建筑缓存失败: {e}")
    
    def _matches_building_type(self, building: 'Building', building_type: BuildingType) -> bool:
        """检查建筑是否匹配指定类型"""
        if not hasattr(building, 'building_type'):
            return False
        
        if hasattr(building.building_type, 'value'):
            return building.building_type.value == building_type.value
        else:
            return str(building.building_type) == building_type.value
    
    def _is_building_available(self, building: 'Building') -> bool:
        """检查建筑是否可用"""
        return building.alive and getattr(building, 'operational', True)
    
    def _on_building_created(self, **kwargs):
        """建筑创建事件处理"""
        self._cache_dirty = True
        self.logging.debug("建筑已创建，标记缓存为脏")
    
    def _on_building_destroyed(self, **kwargs):
        """建筑销毁事件处理"""
        self._cache_dirty = True
        self.logging.debug("建筑已销毁，标记缓存为脏")


# 为了兼容现有代码，直接从GameManager获取建筑数据的适配器版本
class GameManagerAdapter:
    """GameManager 适配器 - 临时解决方案"""
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
    
    def get_game_state(self):
        """返回包含建筑信息的游戏状态"""
        class GameStateView:
            def __init__(self, buildings):
                self.buildings = buildings
        
        return GameStateView(self.game_manager.buildings)


def create_building_manager_with_game_manager(game_manager) -> BuildingManagerService:
    """使用 GameManager 创建 BuildingManagerService 的便捷函数"""
    from .logging_service import SimpleLoggingService
    from .event_bus_service import EventBusService
    
    # 创建简单的服务实现
    logging_service = SimpleLoggingService()
    event_bus_service = EventBusService()
    game_state_adapter = GameManagerAdapter(game_manager)
    
    return BuildingManagerService(
        game_state=game_state_adapter,
        event_bus=event_bus_service,
        logging=logging_service
    )