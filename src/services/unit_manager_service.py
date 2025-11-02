"""
单位管理服务实现
"""
from typing import List, Optional, Tuple, TYPE_CHECKING
import math
from ioc.services import IUnitManagerService

if TYPE_CHECKING:
    from units.unit import Unit
    from ioc.services import IGameStateService, IEventBusService, ILoggingService


class UnitManagerService:
    """单位管理服务实现"""
    
    def __init__(self, 
                 game_state: 'IGameStateService',
                 event_bus: 'IEventBusService',
                 logging: 'ILoggingService'):
        self.game_state = game_state
        self.event_bus = event_bus
        self.logging = logging
    
    def get_units_by_player(self, player_id: int) -> List['Unit']:
        """获取指定玩家的所有单位"""
        game_state = self.game_state.get_game_state()
        return [u for u in game_state.units if u.player_id == player_id]
    
    def find_units_in_range(self, 
                          center: Tuple[float, float],
                          radius: float,
                          player_id: Optional[int] = None) -> List['Unit']:
        """获取范围内的单位"""
        x, y = center
        game_state = self.game_state.get_game_state()
        units_in_range = []
        
        for unit in game_state.units:
            if player_id is not None and unit.player_id != player_id:
                continue
            
            distance = math.sqrt((x - unit.x) ** 2 + (y - unit.y) ** 2)
            if distance <= radius:
                units_in_range.append(unit)
        
        return units_in_range
    
    def get_unit_by_id(self, unit_id: int) -> Optional['Unit']:
        """根据ID获取单位"""
        game_state = self.game_state.get_game_state()
        for unit in game_state.units:
            if unit.id == unit_id:
                return unit
        return None